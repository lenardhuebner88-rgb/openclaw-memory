#!/usr/bin/env python3
"""Auto-Pickup Executor for Mission Control (Feature #9).

Polls /api/tasks?status=pending-pickup, triggers the assigned worker agent via
`openclaw agent`. Human-in-the-loop pickup is replaced by this cron; operators
now only interact with Atlas, workers are spawned automatically.

Config via env:
  AUTO_PICKUP_ENABLED   '1' = active (default), '0' = disabled (no triggers)
  AUTO_PICKUP_DRY_RUN   '1' = log intent only, no subprocess, no locks written
  AUTO_PICKUP_MIN_AGE   seconds before a pending-pickup is eligible (default 60)
  AUTO_PICKUP_MAX_PER   max concurrent triggers per agent (default 1)
  AUTO_PICKUP_ALERT_CH  Discord channel id for error alerts
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

API_BASE = os.environ.get("AUTO_PICKUP_API", "http://127.0.0.1:3000")
OPENCLAW = os.environ.get("AUTO_PICKUP_OPENCLAW", "/home/piet/.openclaw/bin/openclaw")
LOCK_DIR = Path(os.environ.get("AUTO_PICKUP_LOCK_DIR", "/tmp/mc-auto-pickup-locks"))
LOG_FILE = Path(os.environ.get("AUTO_PICKUP_LOG", "/home/piet/.openclaw/workspace/logs/auto-pickup.log"))
OUT_DIR = Path(os.environ.get("AUTO_PICKUP_OUT_DIR", "/home/piet/.openclaw/workspace/logs/auto-pickup-runs"))
MIN_AGE_SEC = int(os.environ.get("AUTO_PICKUP_MIN_AGE", "60"))
MAX_PER_AGENT = int(os.environ.get("AUTO_PICKUP_MAX_PER", "1"))
STALE_LOCK_SEC = int(os.environ.get("AUTO_PICKUP_STALE_LOCK", "600"))
SESSION_LOCK_THRESHOLD_SEC = int(os.environ.get("AUTO_PICKUP_SESSION_LOCK_THRESHOLD", "120"))
ENABLED = os.environ.get("AUTO_PICKUP_ENABLED", "1") == "1"
DRY_RUN = os.environ.get("AUTO_PICKUP_DRY_RUN", "0") == "1"
ALERT_CHANNEL = os.environ.get("AUTO_PICKUP_ALERT_CH", "1491148986109661334")
ALERT_WEBHOOK_URL = os.environ.get("AUTO_PICKUP_WEBHOOK_URL", "").strip()
ALERT_RATE_LIMIT_SEC = int(os.environ.get("AUTO_PICKUP_ALERT_RATE", "900"))
ALERT_STATE_FILE = Path("/tmp/mc-auto-pickup-alert-state.json")
SILENT_FAIL_CHECK_SEC = int(os.environ.get("AUTO_PICKUP_SILENT_FAIL_CHECK_SEC", "8"))


def _is_operator_locked(task: dict) -> bool:
    """P0-2: returns True if operatorLock=True and lockedUntil is in the future."""
    if not task.get("operatorLock"):
        return False
    lu = task.get("lockedUntil")
    if not lu:
        return True  # explicit lock without expiry is a hold
    try:
        exp = __import__("datetime").datetime.fromisoformat(str(lu).replace("Z", "+00:00"))
        now = __import__("datetime").datetime.now(__import__("datetime").timezone.utc)
        return exp > now
    except Exception:
        return True  # malformed -> err on safe side, treat as locked



def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(level: str, msg: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a") as f:
        f.write(f"{_ts()} {level} {msg}\n")


def alert(kind: str, msg: str) -> None:
    """Post error alert to Discord channel, rate-limited per kind."""
    now = time.time()
    state: dict[str, float] = {}
    if ALERT_STATE_FILE.exists():
        try:
            state = json.loads(ALERT_STATE_FILE.read_text())
        except Exception:
            state = {}
    last = state.get(kind, 0)
    if now - last < ALERT_RATE_LIMIT_SEC:
        log("ALERT_SUPPRESSED", f"kind={kind} msg={msg}")
        return
    content = f":rotating_light: **auto-pickup {kind}** — {msg}"
    # Primary path: direct Discord webhook (MC-independent). Falls back to MC
    # /api/discord/send only if AUTO_PICKUP_WEBHOOK_URL is not configured. The
    # direct webhook ensures alerts survive MC downtime (rebuild / crash).
    if ALERT_WEBHOOK_URL:
        payload = json.dumps({
            "content": content,
            "username": "MC Auto-Pickup",
        }).encode("utf-8")
        req = Request(
            ALERT_WEBHOOK_URL,
            data=payload,
            headers={
                "Content-Type": "application/json",
                # Discord rejects default Python-urllib user-agent with 403.
                "User-Agent": "mc-auto-pickup/1.0 (+openclaw; python-urllib)",
            },
            method="POST",
        )
        transport = "webhook"
    else:
        payload = json.dumps({
            "channelId": ALERT_CHANNEL,
            "message": content,
        }).encode("utf-8")
        req = Request(
            f"{API_BASE}/api/discord/send",
            data=payload,
            headers={
                "Content-Type": "application/json",
                "x-actor-kind": "system",
                "x-request-class": "write",
            },
            method="POST",
        )
        transport = "mc-api"
    try:
        with urlopen(req, timeout=10) as resp:
            resp.read()
        state[kind] = now
        ALERT_STATE_FILE.write_text(json.dumps(state))
        log("ALERT_SENT", f"kind={kind} transport={transport}")
    except Exception as e:
        log("ALERT_FAIL", f"kind={kind} transport={transport} err={e}")


def parse_iso(ts: str) -> float:
    if ts.endswith("Z"):
        ts = ts[:-1] + "+00:00"
    return datetime.fromisoformat(ts).timestamp()


def _process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        # process exists but is not inspectable by this user
        return True


def _read_lock_meta(lock_path: Path) -> dict:
    meta: dict = {
        "path": str(lock_path),
        "pid": None,
        "starttime": None,
        "createdAt": None,
    }
    try:
        raw = json.loads(lock_path.read_text())
        if isinstance(raw, dict):
            meta["pid"] = raw.get("pid")
            meta["starttime"] = raw.get("starttime")
            meta["createdAt"] = raw.get("createdAt")
    except Exception:
        pass
    return meta


def _agent_session_locks(agent: str) -> list[Path]:
    sessions_dir = Path(f"/home/piet/.openclaw/agents/{agent}/sessions")
    if not sessions_dir.exists():
        return []
    return sorted(sessions_dir.glob("*.jsonl.lock"), key=lambda p: p.stat().st_mtime, reverse=True)


def evaluate_session_strategy(agent: str, now: float) -> tuple[str, str | None]:
    """Return strategy + session-id override.

    strategy:
      - skip-alive-lock: active/fresh lock detected, skip current auto-pickup cycle
      - spawn-new-for-orphan: stale/dead lock detected, force fresh session id
      - proceed-normal: no conflicting session lock
    """
    for lock_path in _agent_session_locks(agent):
        try:
            lock_age = now - lock_path.stat().st_mtime
        except FileNotFoundError:
            continue

        meta = _read_lock_meta(lock_path)
        pid_raw = meta.get("pid")
        pid = int(pid_raw) if isinstance(pid_raw, int) or (isinstance(pid_raw, str) and str(pid_raw).isdigit()) else 0
        alive = _process_alive(pid)

        if alive and lock_age < SESSION_LOCK_THRESHOLD_SEC:
            log(
                "SESSION_LOCK",
                (
                    f"agent={agent} decision=skip-alive-lock lock={lock_path.name} "
                    f"age={int(lock_age)}s pid={pid}"
                ),
            )
            return "skip-alive-lock", None

        if (not alive) or lock_age >= SESSION_LOCK_THRESHOLD_SEC:
            session_id = f"{agent}-{uuid.uuid4()}"
            log(
                "SESSION_LOCK",
                (
                    f"agent={agent} decision=spawn-new-for-orphan lock={lock_path.name} "
                    f"age={int(lock_age)}s pid={pid} alive={alive} session={session_id}"
                ),
            )
            return "spawn-new-for-orphan", session_id

    log("SESSION_LOCK", f"agent={agent} decision=proceed-normal")
    return "proceed-normal", None


def fetch_tasks(status: str | None = None) -> list[dict]:
    url = f"{API_BASE}/api/tasks"
    if status:
        url += f"?status={status}"
    req = Request(url, headers={"x-actor-kind": "system", "x-request-class": "read"})
    with urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    return data.get("tasks", [])


def fetch_pending() -> list[dict]:
    return sort_pending_tasks(fetch_tasks("pending-pickup"))


def sort_pending_tasks(tasks: list[dict]) -> list[dict]:
    """FIFO order by dispatchedAt ascending.

    Fallback for missing/invalid dispatchedAt keeps ordering stable by using
    createdAt (if present) and id as deterministic tie-breaker.
    """

    def _sort_key(task: dict) -> tuple:
        dispatched_at = task.get("dispatchedAt")
        if isinstance(dispatched_at, str) and dispatched_at.strip():
            try:
                return (0, parse_iso(dispatched_at), task.get("id") or "")
            except Exception:
                pass
        created_at = task.get("createdAt")
        if isinstance(created_at, str) and created_at.strip():
            try:
                return (1, parse_iso(created_at), task.get("id") or "")
            except Exception:
                pass
        return (2, float("inf"), task.get("id") or "")

    return sorted(tasks, key=_sort_key)


TERMINAL_STATUSES = {"done", "failed", "canceled", "blocked"}


def cleanup_terminal_locks(all_tasks: list[dict]) -> int:
    """Remove lock files whose task is no longer pending-pickup / in-progress.
    This is what actually frees the concurrency slot."""
    if not LOCK_DIR.exists():
        return 0
    by_id = {t.get("id"): t for t in all_tasks}
    removed = 0
    for lock in LOCK_DIR.glob("*.lock"):
        stem = lock.stem  # "<taskId>__<agent>"
        tid = stem.rsplit("__", 1)[0]
        task = by_id.get(tid)
        if task is None or task.get("status") in TERMINAL_STATUSES:
            try:
                lock.unlink()
                removed += 1
            except FileNotFoundError:
                pass
    return removed


def cleanup_stale_locks(now: float) -> int:
    if not LOCK_DIR.exists():
        return 0
    removed = 0
    for lock in LOCK_DIR.glob("*.lock"):
        try:
            age = now - lock.stat().st_mtime
            if age > STALE_LOCK_SEC:
                lock.unlink()
                removed += 1
        except FileNotFoundError:
            continue
    return removed


def running_for_agent(agent: str, all_tasks: list[dict]) -> int:
    """Count tasks actively held by this agent (in-progress). Uses live task
    state, not lock files — locks persist after worker completion and would
    wedge the concurrency gate otherwise."""
    return sum(
        1 for t in all_tasks
        if t.get("dispatchTarget") == agent
        and t.get("status") == "in-progress"
    )


def trigger_worker(task_id: str, agent: str, session_id: str | None = None) -> bool:
    # R37 fix 2026-04-19: Explicit REAL_TASK marker so agent cannot classify as heartbeat.
    # Orchestrator-tasks (agent=='main') get extra-explicit orchestrator-mode hint.
    role_hint = ""
    if agent == "main":
        role_hint = "ORCHESTRATOR_MODE=true. This is NOT a heartbeat. Read the task body, orchestrate sub-tasks to worker agents, wait for their receipts, consolidate, send final result-receipt. Do NOT return HEARTBEAT_OK unless the task body literally asks for a heartbeat check. "
    msg = (
        f"REAL_TASK=true TASK_ID={task_id}. {role_hint}"
        f"Auto-Pickup: Hol deine pending-pickup Task {task_id} und arbeite sie vollstaendig ab. "
        f"Sende accepted-Receipt sofort, dann progress/result. "
        f"Verify nach jedem Write via GET /api/tasks/{task_id}."
    )
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{task_id}__{agent}__{int(time.time())}.log"
    try:
        cmd = [
            OPENCLAW, "agent",
            "--agent", agent,
            "--message", msg,
            "--thinking", "medium",
            "--timeout", "1500",
            "--json",
        ]
        if session_id:
            cmd.extend(["--session-id", session_id])

        out_fh = out_path.open("w")
        proc = subprocess.Popen(
            cmd,
            stdout=out_fh,
            stderr=subprocess.STDOUT,
            start_new_session=True,
            env={**os.environ, "PATH": f"/home/piet/.openclaw/bin:{os.environ.get('PATH', '')}"},
        )

        # R52: detect silent immediate subprocess failure.
        time.sleep(max(1, SILENT_FAIL_CHECK_SEC))
        rc = proc.poll()
        try:
            out_fh.flush()
        except Exception:
            pass
        try:
            out_fh.close()
        except Exception:
            pass

        if rc is None:
            return True

        lock = LOCK_DIR / f"{task_id}__{agent}.lock"
        if lock.exists():
            try:
                lock.unlink()
            except Exception:
                pass

        tail = ""
        if out_path.exists():
            try:
                lines = out_path.read_text(errors="replace").splitlines()
                tail = " | ".join(lines[-5:])
            except Exception:
                tail = ""

        if rc == 0:
            log(
                "TRIGGER_WARN",
                f"task={task_id[:8]} agent={agent} rc=0 immediate-exit out={out_path.name} tail={tail}",
            )
            alert("trigger-immediate-exit", f"task={task_id[:8]} agent={agent} rc=0 out={out_path.name}")
            return False

        log(
            "TRIGGER_SILENT_FAIL",
            f"task={task_id[:8]} agent={agent} rc={rc} out={out_path.name} tail={tail}",
        )
        alert("trigger-silent-fail", f"task={task_id[:8]} agent={agent} rc={rc} out={out_path.name}")
        return False
    except Exception as e:
        log("TRIGGER_FAIL", f"task={task_id[:8]} agent={agent} err={e}")
        return False


def main() -> int:
    if not ENABLED:
        log("DISABLED", "AUTO_PICKUP_ENABLED=0")
        return 0

    LOCK_DIR.mkdir(exist_ok=True)
    now = time.time()
    stale = cleanup_stale_locks(now)
    if stale:
        log("CLEANUP", f"removed_stale_locks={stale}")

    try:
        all_tasks = fetch_tasks()
        tasks = sort_pending_tasks([t for t in all_tasks if t.get("status") == "pending-pickup"])
    except URLError as e:
        log("ERR_API", f"{e}")
        alert("api-unreachable", f"GET /api/tasks failed: {e}")
        return 1
    except Exception as e:
        log("ERR_API", f"{e}")
        alert("api-error", f"unexpected: {e}")
        return 1

    freed = cleanup_terminal_locks(all_tasks)
    if freed:
        log("CLEANUP_TERMINAL", f"removed_locks={freed}")

    mode = "DRY-RUN" if DRY_RUN else "LIVE"
    triggered = 0
    held = 0
    skipped_young = 0
    skipped_locked = 0
    missing_target = 0
    skipped_alive_lock = 0
    spawned_new_session = 0
    silent_fails = 0

    for t in tasks:
        tid = t.get("id")
        # P0-2 Operator-Lock (2026-04-19): skip if operator has locked the task
        if _is_operator_locked(t):
            log("SKIP_OPERATOR_LOCK", f"task={t.get('id','?')[:8]} locked_until={t.get('lockedUntil','?')}")
            continue

        agent = t.get("dispatchTarget")
        dispatched_at = t.get("dispatchedAt")
        if not tid:
            continue
        if not agent or not dispatched_at:
            missing_target += 1
            log("SKIP_NO_TARGET", f"task={tid[:8]} dispatchTarget={agent} dispatchedAt={dispatched_at}")
            continue
        try:
            age = now - parse_iso(dispatched_at)
        except Exception as e:
            log("ERR_PARSE", f"task={tid[:8]} dispatchedAt={dispatched_at} err={e}")
            continue
        if age < MIN_AGE_SEC:
            skipped_young += 1
            continue
        lock = LOCK_DIR / f"{tid}__{agent}.lock"
        if lock.exists():
            skipped_locked += 1
            continue

        strategy, session_override = evaluate_session_strategy(agent, now)
        if strategy == "skip-alive-lock":
            skipped_alive_lock += 1
            continue
        if strategy == "spawn-new-for-orphan":
            spawned_new_session += 1

        if running_for_agent(agent, all_tasks) >= MAX_PER_AGENT:
            held += 1
            log("HOLD", f"task={tid[:8]} agent={agent} concurrency_cap={MAX_PER_AGENT}")
            continue
        if DRY_RUN:
            tail = f" session={session_override}" if session_override else ""
            log("DRY_TRIGGER", f"task={tid[:8]} agent={agent} age={int(age)}s{tail}")
            triggered += 1
            continue
        if trigger_worker(tid, agent, session_override):
            try:
                lock.touch()
            except Exception as e:
                log("LOCK_FAIL", f"task={tid[:8]} err={e}")
            tail = f" session={session_override}" if session_override else ""
            log("TRIGGER", f"task={tid[:8]} agent={agent} age={int(age)}s{tail}")
            triggered += 1
        else:
            silent_fails += 1
            alert("trigger-fail", f"task={tid[:8]} agent={agent}")

    log(
        "CYCLE",
        f"mode={mode} pending={len(tasks)} triggered={triggered} held={held} "
        f"young={skipped_young} locked={skipped_locked} alive_lock={skipped_alive_lock} "
        f"spawn_new={spawned_new_session} silent_fails={silent_fails} no_target={missing_target}"
    )

    if missing_target > 0:
        alert("missing-target", f"{missing_target} pending-pickup tasks without dispatchTarget")

    return 0


if __name__ == "__main__":
    sys.exit(main())
