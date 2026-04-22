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
  AUTO_PICKUP_CLAIM_GRACE  seconds an unclaimed spawn-lock may exist (default 90)
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
AGENT_SESSIONS_BASE = Path(os.environ.get("AUTO_PICKUP_AGENT_SESSIONS_BASE", "/home/piet/.openclaw/agents"))
MISSION_CONTROL_DATA_DIR = Path(
    os.environ.get("MISSION_CONTROL_DATA_DIR", "/home/piet/.openclaw/workspace/mission-control/data")
)
WORKER_RUNS_FILE = MISSION_CONTROL_DATA_DIR / "worker-runs.json"
MIN_AGE_SEC = int(os.environ.get("AUTO_PICKUP_MIN_AGE", "60"))
MAX_PER_AGENT = int(os.environ.get("AUTO_PICKUP_MAX_PER", "1"))
STALE_LOCK_SEC = int(os.environ.get("AUTO_PICKUP_STALE_LOCK", "600"))
SESSION_LOCK_THRESHOLD_SEC = int(os.environ.get("AUTO_PICKUP_SESSION_LOCK_THRESHOLD", "120"))
CLAIM_GRACE_SEC = int(os.environ.get("AUTO_PICKUP_CLAIM_GRACE", "90"))
UNCLAIMED_MAX_ATTEMPTS = int(os.environ.get("AUTO_PICKUP_UNCLAIMED_MAX_ATTEMPTS", "3"))
ENABLED = os.environ.get("AUTO_PICKUP_ENABLED", "1") == "1"
DRY_RUN = os.environ.get("AUTO_PICKUP_DRY_RUN", "0") == "1"
ALERT_CHANNEL = os.environ.get("AUTO_PICKUP_ALERT_CH", "1491148986109661334")
ALERT_WEBHOOK_URL = os.environ.get("AUTO_PICKUP_WEBHOOK_URL", "").strip()
ALERT_RATE_LIMIT_SEC = int(os.environ.get("AUTO_PICKUP_ALERT_RATE", "900"))
ALERT_STATE_FILE = Path("/tmp/mc-auto-pickup-alert-state.json")
SILENT_FAIL_CHECK_SEC = int(os.environ.get("AUTO_PICKUP_SILENT_FAIL_CHECK_SEC", "8"))
SESSION_RETRY_WINDOW_SEC = int(os.environ.get("AUTO_PICKUP_SESSION_RETRY_WINDOW_SEC", "600"))
SESSION_RETRY_CAP = int(os.environ.get("AUTO_PICKUP_SESSION_RETRY_CAP", "3"))


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
                "x-request-class": "admin",
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


def _process_starttime(pid: int) -> int | None:
    if pid <= 0:
        return None
    try:
        raw = Path(f"/proc/{pid}/stat").read_text().strip()
    except Exception:
        return None
    rparen = raw.rfind(")")
    if rparen < 0:
        return None
    fields = raw[rparen + 2 :].split()
    if len(fields) <= 19:
        return None
    try:
        return int(fields[19])
    except ValueError:
        return None


def _read_lock_meta(lock_path: Path) -> dict:
    meta: dict = {
        "path": str(lock_path),
        "pid": None,
        "starttime": None,
        "createdAt": None,
        "outPath": None,
        "taskId": None,
        "agent": None,
    }
    try:
        raw = json.loads(lock_path.read_text())
        if isinstance(raw, dict):
            meta["pid"] = raw.get("pid")
            meta["starttime"] = raw.get("starttime")
            meta["createdAt"] = raw.get("createdAt")
            meta["outPath"] = raw.get("outPath")
            meta["taskId"] = raw.get("taskId")
            meta["agent"] = raw.get("agent")
    except Exception:
        pass
    return meta


def _lock_has_spawn_meta(meta: dict) -> bool:
    return any(meta.get(key) not in (None, "") for key in ("pid", "starttime", "createdAt", "outPath"))


def _lock_process_alive(meta: dict) -> bool:
    pid_raw = meta.get("pid")
    pid = int(pid_raw) if isinstance(pid_raw, int) or (isinstance(pid_raw, str) and str(pid_raw).isdigit()) else 0
    if pid <= 0 or not _process_alive(pid):
        return False
    expected_start = meta.get("starttime")
    if expected_start in (None, ""):
        return True
    current_start = _process_starttime(pid)
    if current_start is None:
        # If /proc is not readable we at least know the pid is alive.
        return True
    try:
        return int(expected_start) == current_start
    except Exception:
        return False


def _write_lock_meta(lock_path: Path, *, task_id: str, agent: str, pid: int, starttime: int | None, out_path: Path) -> None:
    payload = {
        "taskId": task_id,
        "agent": agent,
        "pid": pid,
        "starttime": starttime,
        "createdAt": _ts(),
        "outPath": str(out_path),
    }
    lock_path.write_text(json.dumps(payload, sort_keys=True), encoding="utf-8")


def _agent_session_locks(agent: str) -> list[Path]:
    sessions_dir = AGENT_SESSIONS_BASE / agent / "sessions"
    if not sessions_dir.exists():
        return []
    return sorted(sessions_dir.glob("*.jsonl.lock"), key=lambda p: p.stat().st_mtime, reverse=True)


def _load_agent_session_store(agent: str) -> dict[str, dict]:
    store_path = AGENT_SESSIONS_BASE / agent / "sessions" / "sessions.json"
    if not store_path.exists():
        return {}
    try:
        raw = json.loads(store_path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return raw if isinstance(raw, dict) else {}


def _resolve_session_id_for_lock(lock_path: Path) -> str | None:
    name = lock_path.name
    if name.endswith(".jsonl.lock"):
        return name.removesuffix(".jsonl.lock")
    if name.endswith(".lock"):
        return name.removesuffix(".lock")
    return None


def _resolve_lock_session_key(agent: str, lock_path: Path, session_store: dict[str, dict] | None = None) -> str | None:
    session_id = _resolve_session_id_for_lock(lock_path)
    if not session_id:
        return None
    store = session_store if session_store is not None else _load_agent_session_store(agent)
    for session_key, entry in store.items():
        if not isinstance(entry, dict):
            continue
        if str(entry.get("sessionId") or "").strip() == session_id:
            return str(session_key).strip()
    return None


def _is_agent_main_session(agent: str, session_key: str | None) -> bool:
    if not session_key:
        return False
    return session_key.strip().lower() == f"agent:{agent.strip().lower()}:main"


def evaluate_session_strategy(agent: str, now: float, target_session: str = "main") -> tuple[str, str | None]:
    """Return strategy + session-id override.

    strategy:
      - skip-alive-lock: active/fresh lock detected, skip current auto-pickup cycle
      - spawn-new-for-orphan: stale/dead lock detected, force fresh session id
      - proceed-normal: no conflicting session lock
    """
    session_store = _load_agent_session_store(agent)
    for lock_path in _agent_session_locks(agent):
        try:
            lock_age = now - lock_path.stat().st_mtime
        except FileNotFoundError:
            continue

        session_key = _resolve_lock_session_key(agent, lock_path, session_store)
        if target_session == "main" and session_key and not _is_agent_main_session(agent, session_key):
            log(
                "SESSION_LOCK_IGNORE",
                (
                    f"agent={agent} lock={lock_path.name} session={session_key} "
                    f"reason=non-main-session"
                ),
            )
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


def fetch_task(task_id: str) -> dict | None:
    req = Request(
        f"{API_BASE}/api/tasks/{task_id}",
        headers={"x-actor-kind": "system", "x-request-class": "read"},
    )
    with urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    task = data.get("task")
    return task if isinstance(task, dict) else None


def refresh_trigger_candidate(task_id: str, expected_agent: str, now: float) -> tuple[dict | None, float | None, str | None]:
    try:
        live_task = fetch_task(task_id)
    except Exception as e:
        return None, None, f"fetch-error:{e}"
    if not isinstance(live_task, dict):
        return None, None, "missing-task"
    status = str(live_task.get("status") or "").strip()
    if status != "pending-pickup":
        return None, None, f"status={status or 'unknown'}"
    live_agent = str(live_task.get("dispatchTarget") or "").strip()
    if live_agent != expected_agent:
        return None, None, f"dispatchTarget={live_agent or 'missing'}"
    if _has_claim_binding(live_task):
        return None, None, "claim-binding-present"
    dispatched_at = str(live_task.get("dispatchedAt") or "").strip()
    if not dispatched_at:
        return None, None, "missing-dispatchedAt"
    try:
        age = now - parse_iso(dispatched_at)
    except Exception as e:
        return None, None, f"parse-error:{e}"
    return live_task, age, None


def _attempt_run_logs(task_id: str, agent: str) -> list[Path]:
    try:
        return sorted(OUT_DIR.glob(f"{task_id}__{agent}__*.log"))
    except Exception:
        return []


def _build_explicit_session_key(agent: str, session_id: str) -> str:
    return f"agent:{agent.strip().lower()}:explicit:{session_id.strip()}"


def _tail_run_log(path: Path | None, limit: int = 10) -> str:
    if path is None or not path.exists():
        return ""
    try:
        lines = path.read_text(errors="replace").splitlines()
    except Exception:
        return ""
    if not lines:
        return ""
    return " | ".join(lines[-limit:])


def fail_task(task_id: str, reason: str, failure_details: str) -> bool:
    payload = json.dumps({
        "reason": reason,
        "failureDetails": failure_details,
        "actorKind": "system",
    }).encode("utf-8")
    req = Request(
        f"{API_BASE}/api/tasks/{task_id}/fail",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-actor-kind": "system",
            "x-request-class": "write",
        },
        method="POST",
    )
    try:
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        task = data.get("task")
        return bool(data.get("ok")) or (isinstance(task, dict) and task.get("status") == "failed")
    except Exception as e:
        log("FAIL_ROUTE_ERR", f"task={task_id[:8]} err={e}")
        return False


def move_task_blocked(task_id: str, blocker_reason: str) -> bool:
    payload = json.dumps({
        "status": "blocked",
        "blockerReason": blocker_reason,
        "actorKind": "system",
        "requestClass": "review",
    }).encode("utf-8")
    req = Request(
        f"{API_BASE}/api/tasks/{task_id}/move",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-actor-kind": "system",
            "x-request-class": "review",
        },
        method="PUT",
    )
    try:
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        task = data.get("task")
        return isinstance(task, dict) and task.get("status") == "blocked"
    except Exception as e:
        log("BLOCK_ROUTE_ERR", f"task={task_id} err={e}")
        return False


def count_recent_session_retries(task_id: str, now: float, window_sec: int = SESSION_RETRY_WINDOW_SEC) -> int:
    if not LOG_FILE.exists() or window_sec <= 0:
        return 0
    try:
        lines = LOG_FILE.read_text(errors="replace").splitlines()
    except Exception:
        return 0

    cutoff = now - window_sec
    hits = 0
    marker = f"SESSION_RETRY task={task_id} "

    for line in reversed(lines[-5000:]):
        if marker not in line:
            continue
        parts = line.split(" ", 2)
        if len(parts) < 3:
            continue
        ts = parts[0]
        try:
            ts_epoch = parse_iso(ts)
        except Exception:
            continue
        if ts_epoch < cutoff:
            continue
        hits += 1
    return hits


def maybe_terminalize_unclaimed_task(
    task: dict | None,
    *,
    agent: str,
    attempts: int,
    reason: str,
    out_path: str | None = None,
) -> bool:
    if UNCLAIMED_MAX_ATTEMPTS <= 0 or attempts < UNCLAIMED_MAX_ATTEMPTS:
        return False
    if not isinstance(task, dict):
        return False

    task_id = str(task.get("id") or "").strip()
    if not task_id:
        return False

    live_task = task
    try:
        refreshed = fetch_task(task_id)
        if isinstance(refreshed, dict):
            live_task = refreshed
    except Exception as e:
        log("UNCLAIMED_REFRESH_ERR", f"task={task_id[:8]} err={e}")

    if live_task.get("status") != "pending-pickup" or _has_claim_binding(live_task):
        return False

    run_logs = _attempt_run_logs(task_id, agent)
    latest_path = Path(out_path) if isinstance(out_path, str) and out_path else (run_logs[-1] if run_logs else None)
    latest_name = latest_path.name if latest_path is not None else "n/a"
    tail = _tail_run_log(latest_path)
    fail_reason = f"Auto-pickup unclaimed after {attempts} attempts: {reason}"
    failure_details = (
        "Worker never reached its first claim receipt and the task remained pending-pickup. "
        "Smallest next fix: repair the dispatch-spawn to first-receipt handoff so dead-unclaimed runs terminate cleanly. "
        f"agent={agent}; attempts={attempts}; latestOut={latest_name}; tail={tail or 'n/a'}"
    )

    if not fail_task(task_id, fail_reason, failure_details):
        return False

    log(
        "AUTO_FAIL_UNCLAIMED",
        (
            f"task={task_id[:8]} agent={agent} attempts={attempts} "
            f"reason={reason} latestOut={latest_name}"
        ),
    )
    alert("unclaimed-terminalized", f"task={task_id[:8]} agent={agent} attempts={attempts} reason={reason}")
    return True


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


def _has_claim_binding(task: dict | None) -> bool:
    if not isinstance(task, dict):
        return False
    worker_session = str(task.get("workerSessionId") or "").strip()
    accepted_at = str(task.get("acceptedAt") or "").strip()
    receipt_stage = str(task.get("receiptStage") or "").strip()
    execution_state = str(task.get("executionState") or "").strip()
    if worker_session or accepted_at:
        return True
    return receipt_stage in {"accepted", "started", "progress"} or execution_state in {"active", "started", "stalled-warning"}


def load_claimed_open_run_task_ids(all_tasks: list[dict]) -> set[str]:
    """Return task ids whose open worker-runs are already claimed/bound.

    Dispatch now writes an open placeholder run before the first worker claim.
    Treating every open run as "already picked up" deadlocks pending-pickup
    tasks: auto-pickup skips the task before the first worker ever starts.

    We therefore only preserve/skip open runs that show real claim evidence:
    explicit run claim metadata, or a matching task-side binding/accepted state.
    Bare placeholders must remain eligible for the first trigger.
    """

    if not WORKER_RUNS_FILE.exists():
        return set()
    try:
        payload = json.loads(WORKER_RUNS_FILE.read_text())
    except Exception as e:
        log("ERR_WORKER_RUNS", f"path={WORKER_RUNS_FILE} err={e}")
        return set()

    runs = payload.get("runs", []) if isinstance(payload, dict) else []
    if not isinstance(runs, list):
        log("ERR_WORKER_RUNS", f"path={WORKER_RUNS_FILE} err=invalid-format")
        return set()

    tasks_by_id = {
        task.get("id"): task
        for task in all_tasks
        if isinstance(task, dict) and isinstance(task.get("id"), str)
    }
    open_task_ids: set[str] = set()
    for run in runs:
        if not isinstance(run, dict):
            continue
        task_id = run.get("taskId")
        if not isinstance(task_id, str) or not task_id or run.get("endedAt"):
            continue
        claim_state = str(run.get("claimState") or "").strip()
        claimed_at = str(run.get("claimedAt") or "").strip()
        task_claimed = _has_claim_binding(tasks_by_id.get(task_id))
        if claim_state == "placeholder" and not claimed_at and not task_claimed:
            continue
        if claim_state == "claimed" or claimed_at or task_claimed:
            open_task_ids.add(task_id)
    return open_task_ids


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


def cleanup_unclaimed_spawn_locks(now: float, all_tasks: list[dict], claimed_open_run_task_ids: set[str]) -> tuple[int, int, set[str]]:
    """Remove pending-pickup locks whose worker never reached a claim.

    A triggered subprocess is not equivalent to a claimed worker session. If the
    spawned `openclaw agent` dies before `accepted`, the empty lock would wedge
    auto-pickup until the stale-lock timeout. New metadata locks let us reap
    such dead spawns on the next cycle; older empty locks are reaped after a
    short claim grace window.
    """
    if not LOCK_DIR.exists():
        return 0, 0, set()

    tasks_by_id = {
        task.get("id"): task
        for task in all_tasks
        if isinstance(task, dict) and isinstance(task.get("id"), str)
    }

    removed = 0
    waiting = 0
    terminalized: set[str] = set()
    for lock in LOCK_DIR.glob("*.lock"):
        try:
            age = now - lock.stat().st_mtime
        except FileNotFoundError:
            continue

        task_id = lock.stem.rsplit("__", 1)[0]
        task = tasks_by_id.get(task_id)
        if not isinstance(task, dict) or task.get("status") != "pending-pickup":
            continue
        if task_id in claimed_open_run_task_ids or _has_claim_binding(task):
            continue

        meta = _read_lock_meta(lock)
        reason = None
        if _lock_has_spawn_meta(meta):
            if not _lock_process_alive(meta):
                reason = "dead-unclaimed-spawn"
            else:
                waiting += 1
                continue
        elif age >= CLAIM_GRACE_SEC:
            reason = "legacy-unclaimed-lock"
        else:
            waiting += 1
            continue

        try:
            lock.unlink()
            removed += 1
            pid = meta.get("pid")
            out_path = meta.get("outPath")
            out_name = Path(out_path).name if isinstance(out_path, str) and out_path else "n/a"
            task_agent = str(task.get("dispatchTarget") or meta.get("agent") or "?").strip()
            log(
                "LOCK_REAP",
                (
                    f"task={task_id[:8]} agent={task_agent} "
                    f"reason={reason} age={int(age)}s pid={pid or 0} out={out_name}"
                ),
            )
            attempts = len(_attempt_run_logs(task_id, task_agent)) if task_agent else 0
            if task_agent and maybe_terminalize_unclaimed_task(
                task,
                agent=task_agent,
                attempts=attempts,
                reason=reason,
                out_path=out_path if isinstance(out_path, str) else None,
            ):
                terminalized.add(task_id)
        except FileNotFoundError:
            continue

    return removed, waiting, terminalized


def cleanup_stale_locks(now: float, open_run_task_ids: set[str] | None = None) -> tuple[int, int]:
    if not LOCK_DIR.exists():
        return 0, 0
    open_run_task_ids = open_run_task_ids or set()
    removed = 0
    preserved = 0
    for lock in LOCK_DIR.glob("*.lock"):
        try:
            age = now - lock.stat().st_mtime
            if age > STALE_LOCK_SEC:
                task_id = lock.stem.rsplit("__", 1)[0]
                if task_id in open_run_task_ids:
                    preserved += 1
                    continue
                lock.unlink()
                removed += 1
        except FileNotFoundError:
            continue
    return removed, preserved


def running_for_agent(agent: str, all_tasks: list[dict]) -> int:
    """Count tasks actively held by this agent (in-progress). Uses live task
    state, not lock files — locks persist after worker completion and would
    wedge the concurrency gate otherwise."""
    return sum(
        1 for t in all_tasks
        if t.get("dispatchTarget") == agent
        and t.get("status") == "in-progress"
    )


def trigger_worker(task_id: str, agent: str, session_id: str | None = None) -> dict | None:
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
            cmd.extend(["--session-key", _build_explicit_session_key(agent, session_id)])

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
            return {
                "pid": proc.pid,
                "starttime": _process_starttime(proc.pid),
                "outPath": str(out_path),
            }

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
            return None

        log(
            "TRIGGER_SILENT_FAIL",
            f"task={task_id[:8]} agent={agent} rc={rc} out={out_path.name} tail={tail}",
        )
        alert("trigger-silent-fail", f"task={task_id[:8]} agent={agent} rc={rc} out={out_path.name}")
        return None
    except Exception as e:
        log("TRIGGER_FAIL", f"task={task_id[:8]} agent={agent} err={e}")
        return None


def choose_retry_session_override(task_id: str, agent: str, existing_session_id: str | None) -> tuple[str | None, int]:
    """Force a fresh session id after prior dead-unclaimed attempts for the same task.

    Repeated empty spawn logs plus `ws closed before connect` indicate a startup-path issue
    before the worker ever claims the task. In that state, reusing the default session routing
    has proven brittle. A fresh session id is the smallest safe retry hardening: it only applies
    after at least one prior run artifact exists for the same task+agent.
    """
    if existing_session_id:
        return existing_session_id, 0

    prior_runs = _attempt_run_logs(task_id, agent)

    if not prior_runs:
        return None, 0

    return f"{agent}-{uuid.uuid4()}", len(prior_runs)


def main() -> int:
    if not ENABLED:
        log("DISABLED", "AUTO_PICKUP_ENABLED=0")
        return 0

    LOCK_DIR.mkdir(exist_ok=True)
    now = time.time()

    try:
        all_tasks = fetch_tasks()
    except URLError as e:
        log("ERR_API", f"{e}")
        alert("api-unreachable", f"GET /api/tasks failed: {e}")
        return 1
    except Exception as e:
        log("ERR_API", f"{e}")
        alert("api-error", f"unexpected: {e}")
        return 1

    claimed_open_run_task_ids = load_claimed_open_run_task_ids(all_tasks)
    reaped_unclaimed, waiting_claim, terminalized_unclaimed = cleanup_unclaimed_spawn_locks(now, all_tasks, claimed_open_run_task_ids)
    if reaped_unclaimed or waiting_claim or terminalized_unclaimed:
        parts = []
        if reaped_unclaimed:
            parts.append(f"reaped_unclaimed_locks={reaped_unclaimed}")
        if waiting_claim:
            parts.append(f"waiting_claim_locks={waiting_claim}")
        if terminalized_unclaimed:
            parts.append(f"terminalized_unclaimed_tasks={len(terminalized_unclaimed)}")
        log("CLEANUP_UNCLAIMED", " ".join(parts))
    stale, preserved_stale = cleanup_stale_locks(now, claimed_open_run_task_ids)
    if stale or preserved_stale:
        parts = []
        if stale:
            parts.append(f"removed_stale_locks={stale}")
        if preserved_stale:
            parts.append(f"preserved_open_run_locks={preserved_stale}")
        log("CLEANUP", " ".join(parts))

    tasks = sort_pending_tasks(
        [
            t for t in all_tasks
            if t.get("status") == "pending-pickup"
            and t.get("id") not in terminalized_unclaimed
        ]
    )

    freed = cleanup_terminal_locks(all_tasks)
    if freed:
        log("CLEANUP_TERMINAL", f"removed_locks={freed}")

    mode = "DRY-RUN" if DRY_RUN else "LIVE"
    triggered = 0
    held = 0
    skipped_young = 0
    skipped_locked = 0
    skipped_open_run = 0
    missing_target = 0
    skipped_alive_lock = 0
    spawned_new_session = 0
    silent_fails = 0
    reaped_locks = reaped_unclaimed
    waiting_locks = waiting_claim

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
        if tid in claimed_open_run_task_ids:
            skipped_open_run += 1
            log("SKIP_OPEN_RUN", f"task={tid[:8]} agent={agent}")
            continue
        lock = LOCK_DIR / f"{tid}__{agent}.lock"
        if lock.exists():
            skipped_locked += 1
            continue

        live_task, live_age, refresh_reason = refresh_trigger_candidate(tid, agent, now)
        if live_task is None:
            log("SKIP_STALE_TASK", f"task={tid[:8]} agent={agent} reason={refresh_reason}")
            continue
        age = live_age if isinstance(live_age, (int, float)) else age
        if age < MIN_AGE_SEC:
            skipped_young += 1
            continue

        strategy, session_override = evaluate_session_strategy(agent, now, target_session="main")
        if strategy == "skip-alive-lock":
            skipped_alive_lock += 1
            continue
        if strategy == "spawn-new-for-orphan":
            spawned_new_session += 1

        session_override, retry_run_count = choose_retry_session_override(tid, agent, session_override)
        if retry_run_count > 0:
            recent_retries = count_recent_session_retries(tid, now)
            next_retry = recent_retries + 1
            if SESSION_RETRY_CAP > 0 and next_retry > SESSION_RETRY_CAP:
                blocker_reason = (
                    f"SESSION_RETRY cap reached: >{SESSION_RETRY_CAP} retries within "
                    f"{int(SESSION_RETRY_WINDOW_SEC / 60)}min; spawn suppressed"
                )
                if move_task_blocked(tid, blocker_reason):
                    log(
                        "SESSION_RETRY_CAP",
                        (
                            f"task={tid} agent={agent} retries_in_window={recent_retries} "
                            f"window_sec={SESSION_RETRY_WINDOW_SEC} cap={SESSION_RETRY_CAP} action=blocked"
                        ),
                    )
                    alert(
                        "session-retry-cap",
                        (
                            f"task={tid[:8]} agent={agent} retries={recent_retries} "
                            f"window={int(SESSION_RETRY_WINDOW_SEC / 60)}m cap={SESSION_RETRY_CAP} -> blocked"
                        ),
                    )
                else:
                    log(
                        "SESSION_RETRY_CAP_FAIL",
                        (
                            f"task={tid} agent={agent} retries_in_window={recent_retries} "
                            f"window_sec={SESSION_RETRY_WINDOW_SEC} cap={SESSION_RETRY_CAP}"
                        ),
                    )
                continue

            spawned_new_session += 1
            log(
                "SESSION_RETRY",
                (
                    f"task={tid} agent={agent} decision=fresh-session-after-prior-run "
                    f"prior_runs={retry_run_count} session={session_override} "
                    f"retry_window_count={next_retry}/{SESSION_RETRY_CAP} window_sec={SESSION_RETRY_WINDOW_SEC}"
                ),
            )

        if maybe_terminalize_unclaimed_task(
            live_task,
            agent=agent,
            attempts=retry_run_count,
            reason="unclaimed-retry-limit-before-trigger",
        ):
            continue

        if running_for_agent(agent, all_tasks) >= MAX_PER_AGENT:
            held += 1
            log("HOLD", f"task={tid[:8]} agent={agent} concurrency_cap={MAX_PER_AGENT}")
            continue
        if DRY_RUN:
            tail = f" session={session_override}" if session_override else ""
            log("DRY_TRIGGER", f"task={tid[:8]} agent={agent} age={int(age)}s{tail}")
            triggered += 1
            continue
        spawn_meta = trigger_worker(tid, agent, session_override)
        if spawn_meta is not None:
            try:
                _write_lock_meta(
                    lock,
                    task_id=tid,
                    agent=agent,
                    pid=int(spawn_meta.get("pid") or 0),
                    starttime=spawn_meta.get("starttime"),
                    out_path=Path(str(spawn_meta.get("outPath") or "")),
                )
            except Exception as e:
                log("LOCK_FAIL", f"task={tid[:8]} err={e}")
            tail = f" session={session_override}" if session_override else ""
            log(
                "TRIGGER",
                (
                    f"task={tid[:8]} agent={agent} age={int(age)}s pid={int(spawn_meta.get('pid') or 0)}"
                    f"{tail}"
                ),
            )
            triggered += 1
        else:
            silent_fails += 1
            alert("trigger-fail", f"task={tid[:8]} agent={agent}")

    log(
        "CYCLE",
        f"mode={mode} pending={len(tasks)} triggered={triggered} held={held} "
        f"young={skipped_young} locked={skipped_locked} open_run={skipped_open_run} "
        f"alive_lock={skipped_alive_lock} reaped={reaped_locks} waiting_claim={waiting_locks} "
        f"spawn_new={spawned_new_session} silent_fails={silent_fails} no_target={missing_target}"
    )

    if missing_target > 0:
        alert("missing-target", f"{missing_target} pending-pickup tasks without dispatchTarget")

    return 0


if __name__ == "__main__":
    sys.exit(main())
