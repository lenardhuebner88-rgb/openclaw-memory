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
import re
import shlex
import signal
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
TASKS_FILE = MISSION_CONTROL_DATA_DIR / "tasks.json"
WORKER_RUNS_FILE = MISSION_CONTROL_DATA_DIR / "worker-runs.json"
MIN_AGE_SEC = int(os.environ.get("AUTO_PICKUP_MIN_AGE", "60"))
MAX_PER_AGENT = int(os.environ.get("AUTO_PICKUP_MAX_PER", "1"))
STALE_LOCK_SEC = int(os.environ.get("AUTO_PICKUP_STALE_LOCK", "600"))
SESSION_LOCK_THRESHOLD_SEC = int(os.environ.get("AUTO_PICKUP_SESSION_LOCK_THRESHOLD", "120"))
CLAIM_GRACE_SEC = int(os.environ.get("AUTO_PICKUP_CLAIM_GRACE", "90"))
UNCLAIMED_MAX_ATTEMPTS = int(os.environ.get("AUTO_PICKUP_UNCLAIMED_MAX_ATTEMPTS", "3"))
PENDING_CLAIM_STALE_SEC = int(os.environ.get("AUTO_PICKUP_PENDING_CLAIM_STALE_SEC", "600"))
ENABLED = os.environ.get("AUTO_PICKUP_ENABLED", "1") == "1"
DRY_RUN = os.environ.get("AUTO_PICKUP_DRY_RUN", "0") == "1"
ALERT_CHANNEL = os.environ.get("AUTO_PICKUP_ALERT_CH", "1491148986109661334")
ALERT_WEBHOOK_URL = os.environ.get("AUTO_PICKUP_WEBHOOK_URL", "").strip()
ALERT_RATE_LIMIT_SEC = int(os.environ.get("AUTO_PICKUP_ALERT_RATE", "900"))
ALERT_STATE_FILE = Path("/tmp/mc-auto-pickup-alert-state.json")
SILENT_FAIL_CHECK_SEC = int(os.environ.get("AUTO_PICKUP_SILENT_FAIL_CHECK_SEC", "8"))
SESSION_RETRY_WINDOW_SEC = int(os.environ.get("AUTO_PICKUP_SESSION_RETRY_WINDOW_SEC", "600"))
SESSION_RETRY_CAP = int(os.environ.get("AUTO_PICKUP_SESSION_RETRY_CAP", "3"))
SYNC_CLAIM_ENABLED = os.environ.get("AUTO_PICKUP_SYNC_CLAIM", "1") == "1"
SYNC_CLAIM_TIMEOUT_SEC = int(os.environ.get("AUTO_PICKUP_SYNC_CLAIM_TIMEOUT_SEC", "45"))
MAIN_SYNC_CLAIM_TIMEOUT_SEC = int(os.environ.get("AUTO_PICKUP_MAIN_SYNC_CLAIM_TIMEOUT_SEC", "90"))
LENS_SYNC_CLAIM_TIMEOUT_SEC = int(os.environ.get("AUTO_PICKUP_LENS_SYNC_CLAIM_TIMEOUT_SEC", "90"))
SYNC_CLAIM_POLL_SEC = float(os.environ.get("AUTO_PICKUP_SYNC_CLAIM_POLL_SEC", "0.5"))
LAUNCH_MODE = os.environ.get("AUTO_PICKUP_LAUNCH_MODE", "popen").strip() or "popen"
TREND_WINDOW_SEC = int(os.environ.get("AUTO_PICKUP_TREND_WINDOW_SEC", "600"))
CLAIM_TIMEOUT_TREND_ALERT_THRESHOLD = int(os.environ.get("AUTO_PICKUP_TREND_CLAIM_TIMEOUTS_ALERT", "3"))
FIRST_HEARTBEAT_ACCEPTED_FRESH_SEC = int(os.environ.get("AUTO_PICKUP_FIRST_HEARTBEAT_ACCEPTED_FRESH_SEC", "120"))

ROTATION_SIGNAL_FILE = Path(os.environ.get("AUTO_PICKUP_ROTATION_SIGNAL_FILE", "/tmp/atlas-rotation-signal.json"))
ROTATION_CONSUMER_STATE_FILE = Path(os.environ.get("AUTO_PICKUP_ROTATION_STATE_FILE", "/tmp/atlas-rotation-consumer-state.json"))
ROTATION_ACTION_LOG = Path(os.environ.get("AUTO_PICKUP_ROTATION_ACTION_LOG", "/home/piet/.openclaw/workspace/logs/atlas-rotate-actions.jsonl"))
ROTATION_CONSUMER_MODE = os.environ.get("AUTO_PICKUP_ROTATION_CONSUMER_MODE", "dry-run").strip().lower()
ROTATION_LIVE_APPROVED = os.environ.get("AUTO_PICKUP_ROTATION_LIVE_APPROVED", "0") == "1"
ROTATION_LIVE_COMMAND = os.environ.get("AUTO_PICKUP_ROTATION_LIVE_COMMAND", "").strip()

ROTATION_ALLOWED_ACTIONS = {"graceful-rotate-with-summary", "emergency-rotate-too-late"}


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


def _write_json_atomic(path: Path, payload: dict) -> None:
    tmp = path.with_name(f"{path.name}.{os.getpid()}.{uuid.uuid4()}.tmp")
    tmp.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


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


def _load_json_file(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return raw if isinstance(raw, dict) else {}
    except Exception:
        return {}


def _save_json_file(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.{os.getpid()}.{uuid.uuid4().hex}.tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def _append_rotation_action_log(payload: dict) -> None:
    ROTATION_ACTION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ROTATION_ACTION_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _rotation_signal_key(payload: dict) -> str:
    return f"{str(payload.get('session_id') or '').strip()}::{str(payload.get('recommended_action') or '').strip()}"


def _consume_rotation_signal() -> tuple[str, str]:
    """Consume watchdog rotation signal in a bounded, idempotent way.

    Returns tuple(status, detail):
      - none: no signal file
      - consumed: action accepted, signal file cleared
      - duplicate: same session+action already handled, signal file cleared
      - blocked: pre-flight prevented unsafe mutation, signal kept
      - invalid: malformed signal, signal kept
      - failed: action execution failed, signal kept
    """
    if ROTATION_CONSUMER_MODE in {"off", "disabled", "0", "false"}:
        return "none", "consumer-disabled"

    if not ROTATION_SIGNAL_FILE.exists():
        return "none", "signal-missing"

    signal_payload = _load_json_file(ROTATION_SIGNAL_FILE)
    session_id = str(signal_payload.get("session_id") or "").strip()
    action = str(signal_payload.get("recommended_action") or "").strip()
    pct_raw = signal_payload.get("pct")
    pct = int(pct_raw) if isinstance(pct_raw, (int, float, str)) and str(pct_raw).strip().lstrip('-').isdigit() else None

    if not session_id or action not in ROTATION_ALLOWED_ACTIONS:
        log("ROTATION_SIGNAL_INVALID", f"file={ROTATION_SIGNAL_FILE} session={session_id or '-'} action={action or '-'}")
        return "invalid", "invalid-signal-payload"

    state = _load_json_file(ROTATION_CONSUMER_STATE_FILE)
    handled = state.get("handled", {}) if isinstance(state.get("handled"), dict) else {}
    key = _rotation_signal_key(signal_payload)
    now_iso = _ts()
    triggered_at = str(signal_payload.get("triggered_at") or "").strip()
    trigger_age_s = None
    if triggered_at:
        try:
            trigger_age_s = round(max(0.0, time.time() - parse_iso(triggered_at)), 3)
        except Exception:
            trigger_age_s = None

    if key in handled:
        try:
            ROTATION_SIGNAL_FILE.unlink()
        except FileNotFoundError:
            pass
        _append_rotation_action_log({
            "ts": now_iso,
            "mode": ROTATION_CONSUMER_MODE,
            "status": "duplicate-skip",
            "session_id": session_id,
            "recommended_action": action,
            "pct": pct,
            "signal_file": str(ROTATION_SIGNAL_FILE),
            "detail": "idempotent-skip-session-action-already-handled",
        })
        log("ROTATION_SIGNAL_DUPLICATE", f"session={session_id} action={action} file-cleared=1")
        return "duplicate", "idempotent-skip-and-clear"

    if ROTATION_CONSUMER_MODE == "live" and (not ROTATION_LIVE_APPROVED or not ROTATION_LIVE_COMMAND):
        reason = "missing-live-approval" if not ROTATION_LIVE_APPROVED else "missing-live-command"
        log("ROTATION_SIGNAL_BLOCKED", f"session={session_id} action={action} reason={reason}")
        return "blocked", reason

    action_event = {
        "ts": now_iso,
        "mode": ROTATION_CONSUMER_MODE,
        "status": "started",
        "session_id": session_id,
        "recommended_action": action,
        "pct": pct,
        "triggered_at": triggered_at or None,
        "trigger_age_s": trigger_age_s,
        "signal_file": str(ROTATION_SIGNAL_FILE),
    }

    if ROTATION_CONSUMER_MODE == "live":
        try:
            rendered = ROTATION_LIVE_COMMAND.format(session_id=session_id, action=action, pct=(pct if pct is not None else ""))
            cmd = shlex.split(rendered)
            proc = subprocess.run(cmd, check=False, capture_output=True, text=True, timeout=90)
            action_event.update({
                "command": rendered,
                "returncode": proc.returncode,
                "stdout": (proc.stdout or "").strip()[:400],
                "stderr": (proc.stderr or "").strip()[:400],
            })
            if proc.returncode != 0:
                action_event["status"] = "failed"
                _append_rotation_action_log(action_event)
                log("ROTATION_SIGNAL_FAIL", f"session={session_id} action={action} rc={proc.returncode}")
                return "failed", f"live-command-rc-{proc.returncode}"
        except Exception as exc:
            action_event.update({"status": "failed", "error": str(exc)[:400]})
            _append_rotation_action_log(action_event)
            log("ROTATION_SIGNAL_FAIL", f"session={session_id} action={action} err={exc}")
            return "failed", "live-command-exception"
    else:
        action_event.update({
            "status": "simulated",
            "detail": "dry-run atlas-rotate trigger accepted",
        })

    handled[key] = {
        "at": now_iso,
        "session_id": session_id,
        "recommended_action": action,
        "pct": pct,
        "mode": ROTATION_CONSUMER_MODE,
    }
    state["handled"] = handled
    _save_json_file(ROTATION_CONSUMER_STATE_FILE, state)

    try:
        ROTATION_SIGNAL_FILE.unlink()
    except FileNotFoundError:
        pass

    action_event["status"] = action_event.get("status") or "consumed"
    action_event["signal_cleared"] = True
    _append_rotation_action_log(action_event)
    log(
        "ROTATION_SIGNAL_CONSUMED",
        (
            f"session={session_id} action={action} mode={ROTATION_CONSUMER_MODE} "
            f"trigger_age_s={trigger_age_s if trigger_age_s is not None else 'na'} file-cleared=1"
        ),
    )
    return "consumed", f"action={action} mode={ROTATION_CONSUMER_MODE}"


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


def _has_confirmed_claim_binding(task: dict | None) -> bool:
    """Strict claim proof for sync-wait after spawn.

    workerLabel/receiptStage alone can be noisy. We only trust hard binding
    artifacts that prove pickup ownership persisted.
    """
    if not isinstance(task, dict):
        return False
    worker_session = str(task.get("workerSessionId") or "").strip()
    accepted_at = str(task.get("acceptedAt") or "").strip()
    return bool(worker_session or accepted_at)


def _terminate_spawned_worker(pid: int, *, grace_sec: float = 5.0) -> str:
    if pid <= 0:
        return "invalid-pid"
    # Keep a fallback kill path even when the original group leader already
    # exited. start_new_session=True makes pid the original pgid, and child
    # members can survive briefly after leader death.
    try:
        pgid = os.getpgid(pid)
    except ProcessLookupError:
        pgid = pid
    except Exception:
        pgid = pid

    try:
        os.killpg(pgid, signal.SIGTERM)
    except ProcessLookupError:
        return "already-exited"
    except Exception as e:
        return f"term-failed:{e}"

    deadline = time.time() + max(0.5, grace_sec)
    while time.time() < deadline:
        if not _process_alive(pid):
            return "sigterm"
        time.sleep(0.2)

    try:
        os.killpg(pgid, signal.SIGKILL)
    except ProcessLookupError:
        return "sigterm"
    except Exception as e:
        return f"kill-failed:{e}"
    return "sigkill"


def _systemd_unit_name(task_id: str, agent: str) -> str:
    safe_agent = re.sub(r"[^A-Za-z0-9_.-]+", "-", agent).strip("-") or "agent"
    safe_task = re.sub(r"[^A-Za-z0-9_.-]+", "-", task_id).strip("-")[:12] or "task"
    return f"mc-worker-{safe_agent}-{safe_task}-{int(time.time())}"


def _systemd_show_unit(unit: str) -> dict[str, str]:
    try:
        proc = subprocess.run(
            [
                "systemctl", "--user", "show", unit,
                "--property=ActiveState,SubState,MainPID,ExecMainStatus,Result",
                "--no-pager",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return {}

    result: dict[str, str] = {}
    for line in proc.stdout.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key] = value
    return result


def _trigger_worker_systemd_service(cmd: list[str], out_path: Path, task_id: str, agent: str) -> dict | None:
    unit = _systemd_unit_name(task_id, agent)
    path_env = f"/home/piet/.openclaw/bin:{os.environ.get('PATH', '')}"
    launch_cmd = [
        "systemd-run",
        "--user",
        "--collect",
        "--no-block",
        "--unit", unit,
        "--description", f"Mission Control worker {agent} {task_id[:8]}",
        "--property", "KillMode=mixed",
        "--property", "TimeoutStopSec=20s",
        "--working-directory", "/home/piet",
        "--setenv", f"PATH={path_env}",
        "bash", "-lc", 'out="$1"; shift; exec "$@" >> "$out" 2>&1',
        "mc-worker-launch",
        str(out_path),
        *cmd,
    ]
    proc = subprocess.run(
        launch_cmd,
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
        env={**os.environ, "PATH": path_env},
    )
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip().replace("\n", " | ")
        log("TRIGGER_FAIL", f"task={task_id[:8]} agent={agent} mode=systemd-service rc={proc.returncode} unit={unit} err={tail[:500]}")
        return None

    time.sleep(max(1, SILENT_FAIL_CHECK_SEC))
    state = _systemd_show_unit(unit)
    active_state = state.get("ActiveState", "")
    main_pid = int(state.get("MainPID") or "0") if str(state.get("MainPID") or "").isdigit() else 0
    if active_state in {"active", "activating"} and main_pid > 0:
        return {
            "pid": main_pid,
            "starttime": _process_starttime(main_pid),
            "outPath": str(out_path),
            "unit": unit,
            "launchMode": "systemd-service",
        }

    tail = ""
    if out_path.exists():
        try:
            lines = out_path.read_text(errors="replace").splitlines()
            tail = " | ".join(lines[-5:])
        except Exception:
            tail = ""
    log(
        "TRIGGER_SILENT_FAIL",
        (
            f"task={task_id[:8]} agent={agent} mode=systemd-service "
            f"unit={unit} state={active_state or '?'} sub={state.get('SubState', '?')} "
            f"result={state.get('Result', '?')} status={state.get('ExecMainStatus', '?')} tail={tail}"
        ),
    )
    return None


def _terminate_spawned_worker_meta(spawn_meta: dict, *, grace_sec: float = 5.0) -> str:
    unit = str(spawn_meta.get("unit") or "").strip()
    pid = int(spawn_meta.get("pid") or 0)
    if unit:
        try:
            proc = subprocess.run(
                ["systemctl", "--user", "stop", unit],
                check=False,
                capture_output=True,
                text=True,
                timeout=max(5, int(grace_sec) + 5),
            )
            if proc.returncode == 0:
                return f"systemd-stop:{unit}"
        except subprocess.TimeoutExpired:
            fallback = _terminate_spawned_worker(pid, grace_sec=grace_sec)
            return f"systemd-stop-timeout:{unit}:{fallback}"
        fallback = _terminate_spawned_worker(pid, grace_sec=grace_sec)
        return f"systemd-stop-failed:{unit}:{fallback}"
    return _terminate_spawned_worker(pid, grace_sec=grace_sec)


def wait_for_claim_binding(task_id: str, pid: int, timeout_sec: float, poll_sec: float) -> tuple[bool, str, dict | None]:
    deadline = time.time() + max(1.0, timeout_sec)
    poll = max(0.2, poll_sec)
    last_status = "unknown"
    last_receipt = "unknown"
    last_worker = "none"
    last_err = ""

    while time.time() < deadline:
        task = None
        try:
            task = fetch_task(task_id)
        except Exception as e:
            last_err = str(e)

        if isinstance(task, dict):
            last_status = str(task.get("status") or "unknown")
            last_receipt = str(task.get("receiptStage") or "none")
            last_worker = str(task.get("workerSessionId") or "none")
            if _has_confirmed_claim_binding(task):
                return True, "claim-confirmed", task
            if last_status in TERMINAL_STATUSES:
                return False, f"task-terminal-before-claim:{last_status}", task

        if not _process_alive(pid):
            if isinstance(task, dict) and _has_confirmed_claim_binding(task):
                return True, "claim-confirmed-after-worker-exit", task
            return False, "worker-exited-before-claim", task

        time.sleep(poll)

    detail = (
        f"claim-timeout status={last_status} receipt={last_receipt} workerSessionId={last_worker}"
    )
    if last_err:
        detail += f" lastErr={last_err}"
    return False, detail, None


def claim_timeout_for_agent(agent: str) -> int:
    """Return the sync-claim wait budget after trigger_worker's startup probe."""
    base_timeout = max(SYNC_CLAIM_TIMEOUT_SEC, SILENT_FAIL_CHECK_SEC + 30)
    if agent == "main":
        return max(base_timeout, MAIN_SYNC_CLAIM_TIMEOUT_SEC)
    if agent == "efficiency-auditor":
        return max(base_timeout, LENS_SYNC_CLAIM_TIMEOUT_SEC)
    return base_timeout


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


def first_heartbeat_metrics(task: dict | None, now: float | None = None) -> tuple[str, str]:
    """Return first-heartbeat age (sec|none) and gate status (ok|missing|unknown)."""
    if not isinstance(task, dict):
        return "none", "unknown"

    now_epoch = time.time() if now is None else now
    accepted_at = str(task.get("acceptedAt") or "").strip()
    last_heartbeat_at = str(task.get("lastHeartbeatAt") or "").strip()
    receipt_stage = str(task.get("receiptStage") or "").strip()
    execution_event = str(task.get("lastExecutionEvent") or "").strip()

    accepted_heartbeat_fresh = False
    if accepted_at and last_heartbeat_at:
        try:
            heartbeat_age = max(0, int(now_epoch - parse_iso(last_heartbeat_at)))
            accepted_heartbeat_fresh = heartbeat_age <= FIRST_HEARTBEAT_ACCEPTED_FRESH_SEC
        except Exception:
            accepted_heartbeat_fresh = False

    first_heartbeat_seen = (
        receipt_stage in {"progress", "result", "failed", "blocked"}
        or execution_event in {"progress", "result", "failed", "blocked"}
        or accepted_heartbeat_fresh
    )
    gate = "ok" if first_heartbeat_seen else "missing"

    if not accepted_at:
        return "none", gate
    try:
        age = max(0, int(now_epoch - parse_iso(accepted_at)))
        return str(age), gate
    except Exception:
        return "none", gate


def count_no_first_heartbeat_tasks(all_tasks: list[dict]) -> int:
    count = 0
    for task in all_tasks:
        if not isinstance(task, dict):
            continue
        if str(task.get("status") or "") != "in-progress":
            continue
        if not _has_claim_binding(task):
            continue
        _, gate = first_heartbeat_metrics(task)
        if gate != "ok":
            count += 1
    return count


def read_recent_trend_counts(now: float, window_sec: int = TREND_WINDOW_SEC) -> dict[str, int]:
    counts = {
        "trend_claim_timeouts_10m": 0,
        "trend_reap_10m": 0,
        "trend_requeue_10m": 0,
    }
    if not LOG_FILE.exists() or window_sec <= 0:
        return counts
    try:
        lines = LOG_FILE.read_text(errors="replace").splitlines()
    except Exception:
        return counts

    cutoff = now - window_sec
    for line in reversed(lines[-5000:]):
        parts = line.split(" ", 2)
        if len(parts) < 3:
            continue
        ts, level = parts[0], parts[1]
        try:
            ts_epoch = parse_iso(ts)
        except Exception:
            continue
        if ts_epoch < cutoff:
            break
        if level == "CLAIM_TIMEOUT":
            counts["trend_claim_timeouts_10m"] += 1
        elif level == "LOCK_REAP":
            counts["trend_reap_10m"] += 1
        elif level == "PENDING_CLAIM_REQUEUE":
            counts["trend_requeue_10m"] += 1
    return counts


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
        if not isinstance(task, dict):
            continue
        if task.get("status") != "pending-pickup":
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


def cleanup_stale_pending_claim_runs(now: float, all_tasks: list[dict]) -> tuple[int, int]:
    """Requeue pending-pickup tasks whose claimed run never produced heartbeat.

    Atlas/main can occasionally create a claimed worker-run row and task-side
    claim binding, then exit before the first heartbeat. That state blocks
    pickup forever because the task is still pending-pickup but looks claimed.
    Close only old no-heartbeat pending-pickup runs; active/running tasks are
    handled by the worker reconciler instead.
    """
    if not TASKS_FILE.exists() or not WORKER_RUNS_FILE.exists():
        return 0, 0

    try:
        tasks_payload = json.loads(TASKS_FILE.read_text())
        runs_payload = json.loads(WORKER_RUNS_FILE.read_text())
    except Exception as e:
        log("ERR_PENDING_CLAIM_CLEANUP", f"err={e}")
        return 0, 0

    tasks = tasks_payload.get("tasks", []) if isinstance(tasks_payload, dict) else []
    runs = runs_payload.get("runs", []) if isinstance(runs_payload, dict) else []
    if not isinstance(tasks, list) or not isinstance(runs, list):
        log("ERR_PENDING_CLAIM_CLEANUP", "err=invalid-data-format")
        return 0, 0

    live_task_ids = {
        task.get("id")
        for task in all_tasks
        if isinstance(task, dict) and task.get("status") == "pending-pickup"
    }
    candidate_by_task: dict[str, dict] = {}
    for run in runs:
        if not isinstance(run, dict) or run.get("endedAt") or run.get("lastHeartbeatAt"):
            continue
        task_id = str(run.get("taskId") or "").strip()
        if not task_id or task_id not in live_task_ids:
            continue
        if str(run.get("claimState") or "").strip() != "claimed" and not str(run.get("claimedAt") or "").strip():
            continue
        ts_value = str(run.get("claimedAt") or run.get("createdAt") or "").strip()
        if not ts_value:
            continue
        try:
            age = now - parse_iso(ts_value)
        except Exception:
            continue
        if age < PENDING_CLAIM_STALE_SEC:
            continue
        candidate_by_task[task_id] = run

    if not candidate_by_task:
        return 0, 0

    now_iso = _ts()
    mutated_tasks = 0
    closed_runs = 0
    next_tasks = []
    for task in tasks:
        if not isinstance(task, dict):
            next_tasks.append(task)
            continue
        task_id = str(task.get("id") or "").strip()
        run = candidate_by_task.get(task_id)
        if (
            not run
            or task.get("status") != "pending-pickup"
            or task.get("lastHeartbeatAt")
            or task.get("receiptStage")
        ):
            next_tasks.append(task)
            continue
        mutated_tasks += 1
        next_task = {
            **task,
            "status": "assigned",
            "dispatched": False,
            "dispatchState": "queued",
            "executionState": "queued",
            "workerLabel": task.get("assigned_agent") or task.get("dispatchTarget") or task.get("workerLabel"),
            "lastExecutionEvent": "pending-claim-no-heartbeat-requeued",
            "lastActivityAt": now_iso,
            "updatedAt": now_iso,
        }
        for key in ("receiptStage", "workerSessionId", "acceptedAt", "startedAt", "blockerReason"):
            next_task.pop(key, None)
        next_tasks.append(next_task)

    next_runs = []
    for run in runs:
        if not isinstance(run, dict):
            next_runs.append(run)
            continue
        task_id = str(run.get("taskId") or "").strip()
        candidate = candidate_by_task.get(task_id)
        if candidate and run.get("runId") == candidate.get("runId") and not run.get("endedAt"):
            closed_runs += 1
            next_runs.append({
                **run,
                "endedAt": now_iso,
                "outcome": "requeued-claimed-no-heartbeat",
                "terminationHint": "closed-by-auto-pickup:pending-claim-no-heartbeat",
                "cleanupHandled": True,
            })
        else:
            next_runs.append(run)

    if mutated_tasks == 0 or closed_runs == 0:
        return 0, 0

    _write_json_atomic(TASKS_FILE, {**tasks_payload, "tasks": next_tasks})
    _write_json_atomic(WORKER_RUNS_FILE, {**runs_payload, "runs": next_runs})
    for task_id, run in candidate_by_task.items():
        log("PENDING_CLAIM_REQUEUE", f"task={task_id[:8]} run={str(run.get('runId') or '')[:8]} reason=no-heartbeat")
    return mutated_tasks, closed_runs


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


def trigger_worker(task_id: str, agent: str, session_id: str | None = None, dispatch_token: str | None = None) -> dict | None:
    # R37 fix 2026-04-19: Explicit REAL_TASK marker so agent cannot classify as heartbeat.
    # Orchestrator-tasks (agent=='main') get extra-explicit orchestrator-mode hint.
    role_hint = ""
    if agent == "main":
        role_hint = "ORCHESTRATOR_MODE=true. This is NOT a heartbeat. Read the task body, orchestrate sub-tasks to worker agents, wait for their receipts, consolidate, send final result-receipt. Do NOT return HEARTBEAT_OK unless the task body literally asks for a heartbeat check. "

    receipt_quality_hint = (
        "Terminal result quality contract: set resultSummary to a task-specific human-meaningful summary "
        "(never generic placeholders like 'Task accepted and completed.'). "
        "If task requires sections (e.g. EXECUTION_STATUS/RESULT_SUMMARY), include them exactly in final output and keep receipt/result aligned. "
    )
    if agent == "james":
        receipt_quality_hint += (
            "James-specific: final receipt must reflect actual analysis findings, key evidence and residual risk in compact form. "
            "Do not send bootstrap/profile questions in production task results unless explicitly requested by the task body. "
        )
    if agent == "efficiency-auditor":
        receipt_quality_hint += (
            "Lens-specific: sende den accepted-Receipt sofort vor Deep-Research, Log-Auswertung oder groesserem Kontextaufbau. "
            "Erst danach laengere Analyse starten, damit auto-pickup die Claim-Bindung nicht als Timeout wertet. "
        )

    dispatch_token_hint = ""
    if isinstance(dispatch_token, str) and dispatch_token.strip():
        token = dispatch_token.strip()
        dispatch_token_hint = (
            f" Für den ersten non-terminal Receipt (accepted/started/progress) MUSST du dispatchToken={token} mitsenden; "
            "ohne dieses Token wird pending-pickup claim-seitig mit 409 abgewiesen. "
            "Nutze dasselbe dispatchToken auch für result/failed/blocked-Receipts."
        )

    msg = (
        f"REAL_TASK=true TASK_ID={task_id}. {role_hint}{receipt_quality_hint}"
        f"Auto-Pickup: Hol deine pending-pickup Task {task_id} und arbeite sie vollstaendig ab. "
        f"Sende accepted-Receipt sofort, dann progress/result.{dispatch_token_hint} "
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
            cmd.extend(["--session-id", session_id.strip()])

        if LAUNCH_MODE == "systemd-service":
            return _trigger_worker_systemd_service(cmd, out_path, task_id, agent)

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

    rotation_signal_status, rotation_signal_detail = _consume_rotation_signal()

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
    requeued_pending_claims, closed_pending_claim_runs = cleanup_stale_pending_claim_runs(now, all_tasks)
    if requeued_pending_claims or closed_pending_claim_runs:
        log(
            "CLEANUP_PENDING_CLAIM",
            f"requeued_tasks={requeued_pending_claims} closed_runs={closed_pending_claim_runs}",
        )
        try:
            all_tasks = fetch_tasks()
        except Exception as e:
            log("PENDING_CLAIM_REFRESH_ERR", f"err={e}")
        claimed_open_run_task_ids = load_claimed_open_run_task_ids(all_tasks)
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
    no_first_heartbeat = 0
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
        dispatch_token = str(live_task.get("dispatchToken") or "").strip() if isinstance(live_task, dict) else ""
        spawn_meta = trigger_worker(tid, agent, session_override, dispatch_token or None)
        if spawn_meta is not None:
            pid = int(spawn_meta.get("pid") or 0)
            try:
                _write_lock_meta(
                    lock,
                    task_id=tid,
                    agent=agent,
                    pid=pid,
                    starttime=spawn_meta.get("starttime"),
                    out_path=Path(str(spawn_meta.get("outPath") or "")),
                )
            except Exception as e:
                log("LOCK_FAIL", f"task={tid[:8]} err={e}")

            if SYNC_CLAIM_ENABLED:
                # Claim-wait starts *after* the silent-fail probe delay in trigger_worker.
                # Keep a robust floor so normal agent bootstrap/startup latency does not
                # look like a dead-unclaimed run and trigger fresh-session retry loops.
                effective_claim_timeout_sec = claim_timeout_for_agent(agent)
                claim_ok, claim_reason, claim_task = wait_for_claim_binding(
                    tid,
                    pid=pid,
                    timeout_sec=effective_claim_timeout_sec,
                    poll_sec=SYNC_CLAIM_POLL_SEC,
                )
                if not claim_ok:
                    term_state = _terminate_spawned_worker_meta(spawn_meta)
                    try:
                        if lock.exists():
                            lock.unlink()
                    except Exception:
                        pass
                    claim_status = str(claim_task.get("status") if isinstance(claim_task, dict) else "unknown")
                    log(
                        "CLAIM_TIMEOUT",
                        (
                            f"task={tid[:8]} agent={agent} pid={pid} reason={claim_reason} "
                            f"claim_timeout_sec={effective_claim_timeout_sec} "
                            f"task_status={claim_status} terminate={term_state}"
                        ),
                    )
                    alert("claim-timeout", f"task={tid[:8]} agent={agent} reason={claim_reason} terminate={term_state}")
                    silent_fails += 1
                    continue

                first_heartbeat_age_sec, first_heartbeat_gate = first_heartbeat_metrics(claim_task, now=time.time())
                if first_heartbeat_gate != "ok":
                    no_first_heartbeat += 1
                log(
                    "CLAIM_CONFIRMED",
                    (
                        f"task={tid[:8]} agent={agent} pid={pid} "
                        f"first_heartbeat_age_sec={first_heartbeat_age_sec} "
                        f"first_heartbeat_gate={first_heartbeat_gate}"
                    ),
                )

            tail = f" session={session_override}" if session_override else ""
            log(
                "TRIGGER",
                (
                    f"task={tid[:8]} agent={agent} age={int(age)}s pid={pid}"
                    f"{tail}"
                ),
            )
            triggered += 1
        else:
            silent_fails += 1
            alert("trigger-fail", f"task={tid[:8]} agent={agent}")

    trend_counts = read_recent_trend_counts(now, TREND_WINDOW_SEC)
    if trend_counts["trend_claim_timeouts_10m"] >= CLAIM_TIMEOUT_TREND_ALERT_THRESHOLD:
        alert(
            "trend-claim-timeouts-10m",
            (
                f"claim_timeouts_10m={trend_counts['trend_claim_timeouts_10m']} "
                f"threshold={CLAIM_TIMEOUT_TREND_ALERT_THRESHOLD}"
            ),
        )

    cycle_tasks = all_tasks
    try:
        cycle_tasks = fetch_tasks()
    except Exception as e:
        log("CYCLE_REFRESH_ERR", f"err={e}")
    no_first_heartbeat = max(no_first_heartbeat, count_no_first_heartbeat_tasks(cycle_tasks))

    log(
        "CYCLE",
        f"mode={mode} pending={len(tasks)} triggered={triggered} held={held} "
        f"rotation_signal={rotation_signal_status} rotation_detail={rotation_signal_detail} "
        f"young={skipped_young} locked={skipped_locked} open_run={skipped_open_run} "
        f"alive_lock={skipped_alive_lock} reaped={reaped_locks} waiting_claim={waiting_locks} "
        f"spawn_new={spawned_new_session} silent_fails={silent_fails} no_target={missing_target} "
        f"no_first_heartbeat={no_first_heartbeat} "
        f"trend_claim_timeouts_10m={trend_counts['trend_claim_timeouts_10m']} "
        f"trend_reap_10m={trend_counts['trend_reap_10m']} "
        f"trend_requeue_10m={trend_counts['trend_requeue_10m']}"
    )

    if missing_target > 0:
        alert("missing-target", f"{missing_target} pending-pickup tasks without dispatchTarget")

    first_heartbeat_gate = "pass" if no_first_heartbeat == 0 else "warn"
    trend_gate = "fail" if trend_counts["trend_claim_timeouts_10m"] >= CLAIM_TIMEOUT_TREND_ALERT_THRESHOLD else (
        "warn" if (trend_counts["trend_reap_10m"] > 0 or trend_counts["trend_requeue_10m"] > 0) else "pass"
    )
    pending_pickup_gate = "pass" if len(tasks) == 0 else "warn"
    proof_green_gate = "pass" if (silent_fails == 0 and missing_target == 0) else "fail"
    log(
        "GATE_MATRIX",
        (
            f"first_heartbeat={first_heartbeat_gate} no_first_heartbeat={no_first_heartbeat} "
            f"pending_pickup={pending_pickup_gate} pending={len(tasks)} "
            f"trend={trend_gate} trend_claim_timeouts_10m={trend_counts['trend_claim_timeouts_10m']} "
            f"trend_reap_10m={trend_counts['trend_reap_10m']} trend_requeue_10m={trend_counts['trend_requeue_10m']} "
            f"proof_green={proof_green_gate} silent_fails={silent_fails} no_target={missing_target}"
        ),
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
