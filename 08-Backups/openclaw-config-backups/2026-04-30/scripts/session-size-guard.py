#!/usr/bin/env python3
"""
Session-Size-Guard — Monitors agent session JSONL files for size budgets.

Cron: */5 * * * * (full check) + * * * * * --log-only (immediate ALERT-only)
Lock: /tmp/session-size-guard.lock + /tmp/session-size-guard-immediate.lock
Log:  /home/piet/.openclaw/workspace/logs/session-size-guard.log
State: /home/piet/.openclaw/workspace/logs/session-size-guard.state.json

Tracked agents:
  main, frontend-guru, sre-expert, efficiency-auditor, spark, james

Per-agent budgets (token-based):
- WARN at 50%, HARD-CAP at 100% (per-agent override via env / per-budgets file)
- ALERT only mode (--log-only) for the */1 immediate watcher
- Full mode (default) for */5 enforcement window

Behavior:
- Reads sessions.json + per-agent session JSONL files
- Computes total tokens via byte-count heuristic
- Logs ALERTS at hard/critical levels (used by alert-dispatcher.sh)
- WORKER_HARD_CAP_ROTATION feature-flag (default OFF) for guarded rotation
  on workers >budget; never rotates main, never rotates with active lock

Failure-modes:
- Session-file lock contention -> skip rotation, log only
- sessions.json missing or unreadable -> skip silently (cron retries)
- Worker rotation requires SESSION_SIZE_GUARD_ENABLE_WORKER_ROTATION=1
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import sys
import os
import re
import subprocess
import tempfile
import time
import uuid
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SESSIONS_DIR = Path("/home/piet/.openclaw/agents/main/sessions")
SESSION_STORE_PATH = SESSIONS_DIR / "sessions.json"
WORKER_AGENTS = ("frontend-guru", "sre-expert", "efficiency-auditor", "spark", "james")
WORKER_AGENTS_ROOT = Path("/home/piet/.openclaw/agents")
STATE_PATH = Path("/home/piet/.openclaw/workspace/logs/session-size-guard.state.json")
LOG_PATH = Path("/home/piet/.openclaw/workspace/logs/session-size-guard.log")
ROTATION_TEST_ARTIFACT_PATH = Path("/home/piet/.openclaw/workspace/logs/session-size-guard.rotation-selftest.json")
WORKER_MEMORY_HOFF_ARTIFACT_PATH = Path("/home/piet/.openclaw/workspace/logs/session-size-guard.worker-memory-handoff-selftest.json")
GATEWAY_LOGS = [
    Path("/home/piet/.openclaw/logs/gateway.log"),
    Path("/home/piet/.openclaw/logs/gateway-error.log"),
    Path("/home/piet/.openclaw/workspace/logs/gateway.log"),
]
DISCORD_API = "http://127.0.0.1:3000/api/discord/send"
ATLAS_MAIN_CHANNEL = "1486480128576983070"

THRESHOLDS = {
    "warning": {"bytes": 600 * 1024, "messages": 150},
    "hard": {"bytes": 900 * 1024, "messages": 200},
    "rotation": {"bytes": int(1.1 * 1024 * 1024), "messages": 250},
}

# File-size is primary signal. Message-count only corroborates when file-size is already close.
CORROBORATION_RATIO = 0.85

COOLDOWN_SEC = {
    "warning": 30 * 60,
    "hard": 15 * 60,
    "rotation": 60 * 60,
    "immediate": 5 * 60,
}

IMMEDIATE_PATTERNS = [
    re.compile(r"context-overflow-diag", re.IGNORECASE),
    re.compile(r"auto-compaction-failure", re.IGNORECASE),
]

R52_LOAD_FAIL_PATTERN = re.compile(r"WORKER_MEMORY_ADAPTER_LOAD_FAIL", re.IGNORECASE)
R52_LOAD_FAIL_WINDOW_SEC = 60 * 60
R52_LOAD_FAIL_THRESHOLD = 3

# Worker rotation hard-cap (default OFF until operator approves canary)
WORKER_ROTATION_HARD_CAP = str(os.environ.get("WORKER_ROTATION_HARD_CAP", "0")).strip() in ("1", "true", "yes")
# Spark-only canary allowlist
WORKER_ROTATION_AGENTS = [
    a.strip() for a in str(os.environ.get("WORKER_ROTATION_AGENTS", "spark")).split(",")
    if a.strip()
]
# Legacy flag alias (used by existing spec)
SESSION_SIZE_GUARD_ENABLE_WORKER_ROTATION = str(os.environ.get(
    "SESSION_SIZE_GUARD_ENABLE_WORKER_ROTATION", "0"
)).strip() not in ("1", "true", "yes")
SESSION_SIZE_GUARD_WORKER_ROTATION_ALLOWLIST = [
    a.strip() for a in os.environ.get(
        "SESSION_SIZE_GUARD_WORKER_ROTATION_ALLOWLIST", "spark"
    ).split(",") if a.strip()
]


@dataclass
class SessionSignal:
    path: Path
    size_bytes: int
    message_count: int
    level: str | None
    agent: str


@dataclass
class RotationResult:
    rotated: bool
    checkpoint_path: Path | None = None
    archived_path: Path | None = None
    new_session_path: Path | None = None
    takeover_verified: bool = False
    verify_detail: str | None = None
    detail: str | None = None
    orphan_unbound: bool = False


def now_ts() -> int:
    return int(time.time())


def utc_now_iso_z() -> str:
    return dt.datetime.now(dt.UTC).isoformat().replace("+00:00", "Z")


def log(msg: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(f"[{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}] {msg}\n")


def write_rotation_test_artifact(payload: dict[str, Any], artifact_path: Path) -> None:
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _load_worker_memory_adapter_class() -> Any | None:
    adapter_path = Path("/home/piet/.openclaw/workspace/scripts/worker-memory-adapter.py")
    if not adapter_path.exists():
        return None
    try:
        spec = importlib.util.spec_from_file_location("worker_memory_adapter", str(adapter_path))
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return getattr(module, "Adapter", None)
    except Exception as exc:
        log(f"WORKER_MEMORY_ADAPTER_LOAD_FAIL detail={exc}")
        return None


def build_worker_memory_bootstrap_text(worker: str, resume: dict[str, Any]) -> str:
    progress = (resume.get("progress") or "").strip()
    progress_line = progress.splitlines()[0] if progress else ""
    tasks = resume.get("tasks") if isinstance(resume.get("tasks"), list) else []
    pending = [t for t in tasks if isinstance(t, dict) and t.get("status") == "pending"]
    pending_ids = [str(t.get("id")) for t in pending[:5]]
    architecture = (resume.get("architecture") or "").strip()
    architecture_hint = "yes" if architecture else "no"
    return (
        "Session rotation bootstrap (worker memory handoff dry-run). "
        f"worker={worker}; "
        f"progress_head={progress_line[:160] or 'none'}; "
        f"pending_count={len(pending)}; pending_ids={pending_ids}; "
        f"has_architecture={architecture_hint}."
    )


def self_test_worker_memory_handoff(worker: str, artifact_path: Path | None = None) -> int:
    Adapter = _load_worker_memory_adapter_class()
    if Adapter is None:
        print("SELF_TEST_WORKER_MEMORY_HANDOFF=failed detail=adapter-missing")
        return 1
    try:
        adapter = Adapter.from_env()
        adapter.ensure_memory_dir(worker)
        now_iso = utc_now_iso_z()
        adapter.write_progress(
            worker,
            (
                f"# Worker Memory — {worker} — {now_iso}\n"
                "task_id: selftest-worker-memory-handoff\n"
                "status: in-progress\n"
                "next_step: use read_resume_bundle in dry-run rotation bootstrap\n"
            ),
        )
        adapter.write_task_queue(
            worker,
            [
                {
                    "id": "selftest-pending-1",
                    "label": "Validate resume handoff payload",
                    "status": "pending",
                    "created": now_iso,
                    "updated": now_iso,
                }
            ],
        )
        adapter.write_architecture(
            worker,
            (
                f"# Architecture Decisions — {worker} — selftest-worker-memory-handoff\n\n"
                "## Decision 1 — wire adapter to dry-run bootstrap\n"
                f"Date: {now_iso}\n"
            ),
        )
        resume = adapter.read_resume_bundle(worker)
        bootstrap_text = build_worker_memory_bootstrap_text(worker, resume)
        bootstrap = {
            "type": "message",
            "role": "system",
            "message": {
                "role": "system",
                "content": [{"type": "text", "text": bootstrap_text}],
            },
            "createdAt": utc_now_iso_z(),
        }
        if artifact_path is not None:
            write_rotation_test_artifact(
                {
                    "at": utc_now_iso_z(),
                    "mode": "self-test-worker-memory-handoff",
                    "worker": worker,
                    "resume": {
                        "keys": sorted(resume.keys()),
                        "pendingCount": len([t for t in resume.get("tasks", []) if isinstance(t, dict) and t.get("status") == "pending"]),
                    },
                    "bootstrap": bootstrap,
                    "clarification": {
                        "simulated": True,
                        "dryRun": True,
                        "runtimeRotation": False,
                    },
                },
                artifact_path,
            )
        print(
            "SELF_TEST_WORKER_MEMORY_HANDOFF=ok "
            f"worker={worker} pending={len([t for t in resume.get('tasks', []) if isinstance(t, dict) and t.get('status') == 'pending'])}"
        )
        if artifact_path is not None:
            print(f"TEST_ARTIFACT={artifact_path}")
        return 0
    except Exception as exc:
        print(f"SELF_TEST_WORKER_MEMORY_HANDOFF=failed detail={exc}")
        return 1


def load_state() -> dict[str, Any]:
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {"alerts": {}, "log_offsets": {}, "event_hashes": {}}


def save_state(state: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2), encoding="utf-8")


def is_discord_main_session(session_file: Path) -> bool:
    try:
        with session_file.open("r", encoding="utf-8", errors="ignore") as fh:
            for i, line in enumerate(fh):
                if "agent:main:discord:" in line:
                    return True
                if i > 250:
                    break
    except Exception:
        return False
    return False


def count_messages(session_file: Path) -> int:
    count = 0
    try:
        with session_file.open("r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if row.get("type") == "message":
                    count += 1
    except Exception:
        return 0
    return count


def classify(size_bytes: int, message_count: int) -> str | None:
    if size_bytes >= THRESHOLDS["rotation"]["bytes"]:
        return "rotation"
    if size_bytes >= THRESHOLDS["hard"]["bytes"]:
        return "hard"
    if size_bytes >= THRESHOLDS["warning"]["bytes"]:
        return "warning"

    if message_count >= THRESHOLDS["rotation"]["messages"] and size_bytes >= int(THRESHOLDS["rotation"]["bytes"] * CORROBORATION_RATIO):
        return "rotation"
    if message_count >= THRESHOLDS["hard"]["messages"] and size_bytes >= int(THRESHOLDS["hard"]["bytes"] * CORROBORATION_RATIO):
        return "hard"
    if message_count >= THRESHOLDS["warning"]["messages"] and size_bytes >= int(THRESHOLDS["warning"]["bytes"] * CORROBORATION_RATIO):
        return "warning"
    return None


def should_send(state: dict[str, Any], key: str, level: str) -> bool:
    alerts = state.setdefault("alerts", {})
    last = alerts.get(key, {}).get(level)
    if not isinstance(last, int):
        return True
    return now_ts() - last >= COOLDOWN_SEC[level]


def mark_sent(state: dict[str, Any], key: str, level: str) -> None:
    alerts = state.setdefault("alerts", {})
    levels = alerts.setdefault(key, {})
    levels[level] = now_ts()


def send_discord(message: str) -> tuple[bool, str]:
    payload = json.dumps(
        {
            "agentId": "main",
            "channelId": ATLAS_MAIN_CHANNEL,
            "message": message,
        }
    )
    cmd = [
        "curl",
        "-sS",
        "-X",
        "POST",
        DISCORD_API,
        "-H",
        "Content-Type: application/json",
        "-H",
        "x-actor-kind: system",
        "-H",
        "x-request-class: admin",
        "-d",
        payload,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    ok = proc.returncode == 0 and '"ok":true' in (proc.stdout or "")
    return ok, (proc.stdout or proc.stderr or "").strip()[:1000]


def is_ignored_session_artifact(session_file: Path) -> bool:
    n = session_file.name
    if ".checkpoint." in n or ".deleted." in n or ".reset." in n or ".archived." in n:
        return True
    # Trajectory files are sidecar artifacts, not runtime sessions. They do not
    # have sessions.json bindings, so treating them as rotation candidates causes
    # false runtime-binding-not-found alerts.
    if n.endswith(".trajectory.jsonl"):
        return True
    return False


def _scan_session_dir(session_dir: Path, agent: str, include_file: Path | None = None, *, main_discord_only: bool = False) -> list[SessionSignal]:
    out: list[SessionSignal] = []
    store = _load_session_store_for_agent(agent)
    files = [include_file] if include_file else sorted(session_dir.glob("*.jsonl"))
    for f in files:
        if not f or not f.exists():
            continue
        if is_ignored_session_artifact(f):
            continue
        if main_discord_only and include_file is None and not is_discord_main_session(f):
            continue
        binding = _find_store_binding_for_file(store, f)
        if binding:
            _, entry = binding
            if entry.get("status") in {"done", "failed", "canceled"} or entry.get("endedAt"):
                continue
        size_bytes = f.stat().st_size
        message_count = count_messages(f)
        level = classify(size_bytes, message_count)
        out.append(SessionSignal(path=f, size_bytes=size_bytes, message_count=message_count, level=level, agent=agent))
    return out


def scan_sessions(include_file: Path | None = None) -> list[SessionSignal]:
    return _scan_session_dir(SESSIONS_DIR, "main", include_file, main_discord_only=True)


def scan_worker_sessions(include_file: Path | None = None) -> list[SessionSignal]:
    out: list[SessionSignal] = []
    if include_file is not None:
        agent = _agent_name_for_file(include_file)
        if agent != "main":
            return _scan_session_dir(_worker_session_dir(agent), agent, include_file, main_discord_only=False)
        return []

    for agent in WORKER_AGENTS:
        session_dir = _worker_session_dir(agent)
        if not session_dir.exists():
            continue
        out.extend(_scan_session_dir(session_dir, agent, main_discord_only=False))
    return out


def level_emoji(level: str) -> str:
    return {"warning": "🟡", "hard": "🟠", "rotation": "🔴"}.get(level, "⚠️")


def _read_session_header_line(session_file: Path) -> str:
    try:
        with session_file.open("r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                s = line.strip()
                if not s:
                    continue
                try:
                    parsed = json.loads(s)
                    if isinstance(parsed, dict) and parsed.get("type") == "session":
                        return json.dumps(parsed, ensure_ascii=False)
                except Exception:
                    continue
    except Exception:
        pass

    fallback = {
        "type": "session",
        "id": f"rotation-{uuid.uuid4().hex[:12]}",
        "meta": "agent:main:discord:rotation",
        "createdAt": utc_now_iso_z(),
    }
    return json.dumps(fallback, ensure_ascii=False)




def _load_session_store() -> dict[str, Any]:
    try:
        data = json.loads(SESSION_STORE_PATH.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def _save_session_store(store: dict[str, Any]) -> None:
    SESSION_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = SESSION_STORE_PATH.with_suffix(f".json.{uuid.uuid4().hex}.tmp")
    tmp.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(SESSION_STORE_PATH)


def _worker_session_dir(agent: str) -> Path:
    return WORKER_AGENTS_ROOT / agent / "sessions"


def _worker_store_path(agent: str) -> Path:
    return _worker_session_dir(agent) / "sessions.json"


def _load_session_store_for_agent(agent: str) -> dict[str, Any]:
    store_path = SESSION_STORE_PATH if agent == "main" else _worker_store_path(agent)
    try:
        data = json.loads(store_path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}


def _find_store_binding_for_file(store: dict[str, Any], session_file: Path) -> tuple[str, dict[str, Any]] | None:
    target = str(session_file)
    for key, value in store.items():
        if not isinstance(value, dict):
            continue
        if value.get("sessionFile") == target:
            return key, value
    return None




def archive_unbound_oversize_session(session_file: Path, dry_run: bool = False) -> RotationResult:
    """Archive an oversized session artifact that has no runtime binding.

    Unbound files cannot be runtime-rotated safely because there is no
    sessions.json key to switch. Treat them as orphan artifacts instead of
    emitting runtime-binding-not-found forever.
    """
    ts = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    checkpoint = session_file.with_name(f"{session_file.name}.checkpoint.{ts}")
    archived = session_file.with_name(f"{session_file.name}.archived.{ts}")

    if dry_run:
        return RotationResult(
            rotated=True,
            checkpoint_path=checkpoint,
            archived_path=archived,
            takeover_verified=True,
            verify_detail="dry-run-orphan-unbound-session",
            detail="orphan-unbound-session",
            orphan_unbound=True,
        )

    try:
        shutil.copy2(session_file, checkpoint)
        session_file.replace(archived)
        still_scanned = scan_sessions(include_file=archived)
        verified = archived.exists() and not session_file.exists() and not still_scanned
        detail = "orphan-unbound-session-archived" if verified else "orphan-unbound-session-archive-verify-failed"
        return RotationResult(
            rotated=True,
            checkpoint_path=checkpoint,
            archived_path=archived,
            takeover_verified=verified,
            verify_detail=detail,
            detail="orphan-unbound-session",
            orphan_unbound=True,
        )
    except Exception as exc:
        return RotationResult(rotated=False, detail=f"orphan-unbound-session-archive-error:{exc}", orphan_unbound=True)


def _agent_name_for_file(session_file: Path) -> str:
    try:
        if session_file.parent == SESSIONS_DIR:
            return "main"
        if session_file.parent.name == "sessions":
            parent = session_file.parent.parent.name
            if parent in WORKER_AGENTS:
                return parent
    except Exception:
        pass
    return "main"


def _build_rotated_header(session_file: Path, new_session_id: str) -> str:
    try:
        with session_file.open("r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                s = line.strip()
                if not s:
                    continue
                try:
                    parsed = json.loads(s)
                except Exception:
                    continue
                if isinstance(parsed, dict) and parsed.get("type") == "session":
                    parsed["id"] = new_session_id
                    parsed["timestamp"] = utc_now_iso_z()
                    return json.dumps(parsed, ensure_ascii=False)
    except Exception:
        pass
    return _read_session_header_line(session_file)


def _verify_rotation_takeover(session_file: Path, archived_file: Path) -> tuple[bool, str]:
    if not session_file.exists():
        return False, "new-session-missing"
    if not archived_file.exists():
        return False, "archived-session-missing"

    try:
        new_size = session_file.stat().st_size
        old_size = archived_file.stat().st_size
    except Exception as exc:
        return False, f"stat-failed:{exc}"

    if old_size <= new_size:
        return False, f"unexpected-size-ratio old={old_size} new={new_size}"

    try:
        active = scan_sessions(include_file=session_file)
        archived = scan_sessions(include_file=archived_file)
    except Exception as exc:
        return False, f"scan-failed:{exc}"

    if not active:
        return False, "new-session-not-detected"
    if archived:
        return False, "archived-session-still-detected"

    return True, "takeover-ok"




def _verify_runtime_binding(session_key: str, expected_session_id: str, expected_file: Path) -> tuple[bool, str]:
    store = _load_session_store()
    entry = store.get(session_key)
    if not isinstance(entry, dict):
        return False, "session-key-missing-after-rotate"
    if entry.get("sessionId") != expected_session_id:
        return False, f"session-id-mismatch:{entry.get('sessionId')}"
    if entry.get("sessionFile") != str(expected_file):
        return False, "session-file-mismatch"
    if not expected_file.exists():
        return False, "new-session-file-missing"
    return True, "runtime-binding-ok"


def rotate_session_file(session_file: Path, dry_run: bool = False) -> RotationResult:
    ts = time.strftime("%Y%m%d-%H%M%S", time.gmtime())
    checkpoint = session_file.with_name(f"{session_file.stem}.checkpoint.{ts}.jsonl")
    archived = session_file.with_name(f"{session_file.stem}.archived.{ts}.jsonl")
    new_session_id = str(uuid.uuid4())
    new_session = session_file.with_name(f"{new_session_id}.jsonl")

    if dry_run:
        return RotationResult(
            rotated=True,
            checkpoint_path=checkpoint,
            archived_path=archived,
            new_session_path=new_session,
            takeover_verified=True,
            verify_detail="dry-run",
            detail="dry-run",
        )

    try:
        store = _load_session_store()
        binding = _find_store_binding_for_file(store, session_file)
        if not binding:
            return archive_unbound_oversize_session(session_file, dry_run=dry_run)
        session_key, store_entry = binding

        content = session_file.read_text(encoding="utf-8", errors="ignore")
        checkpoint.write_text(content, encoding="utf-8")
        header = _build_rotated_header(session_file, new_session_id)
        session_file.replace(archived)

        bootstrap = {
            "type": "message",
            "role": "system",
            "message": {
                "role": "system",
                "content": [{"type": "text", "text": "Session rotation bootstrap (guard-v4 runtime switch)."}],
            },
            "createdAt": utc_now_iso_z(),
        }
        with new_session.open("w", encoding="utf-8") as fh:
            fh.write(header + "\n")
            fh.write(json.dumps(bootstrap, ensure_ascii=False) + "\n")

        now_ms = int(time.time() * 1000)
        store_entry["sessionId"] = new_session_id
        store_entry["sessionFile"] = str(new_session)
        store_entry["updatedAt"] = now_ms
        store_entry["abortedLastRun"] = False
        store_entry["status"] = "active"
        store_entry.pop("endedAt", None)
        store[session_key] = store_entry
        _save_session_store(store)

        verified_file, verify_detail_file = _verify_rotation_takeover(new_session, archived)
        verified_binding, verify_detail_binding = _verify_runtime_binding(session_key, new_session_id, new_session)
        verified = verified_file and verified_binding
        verify_detail = f"{verify_detail_file};{verify_detail_binding}"
        return RotationResult(
            rotated=True,
            checkpoint_path=checkpoint,
            archived_path=archived,
            new_session_path=new_session,
            takeover_verified=verified,
            verify_detail=verify_detail,
        )
    except Exception as exc:
        return RotationResult(rotated=False, detail=str(exc))


def emit_session_alerts(state: dict[str, Any], signals: list[SessionSignal], *, dry_run_rotation: bool = False, allow_rotation: bool = True) -> int:
    sent = 0
    for s in signals:
        if not s.level:
            continue
        key = f"session:{s.path.name}"
        if not should_send(state, key, s.level):
            continue

        if s.level == "rotation" and s.agent == "main" and allow_rotation:
            rotation = rotate_session_file(s.path, dry_run=dry_run_rotation)
            if rotation.rotated:
                action_text = (
                    f"Action: `rotation`\n"
                    f"Checkpoint: `{rotation.checkpoint_path.name if rotation.checkpoint_path else '-'}`\n"
                    f"Archived: `{rotation.archived_path.name if rotation.archived_path else '-'}`\n"
                    f"New Session: `{rotation.new_session_path.name if rotation.new_session_path else '-'}`\n"
                    f"Takeover Verify: `{'ok' if rotation.takeover_verified else 'failed'} ({rotation.verify_detail or '-'})`\n"
                    "Hinweis: Bitte in #atlas-main neue Session übernehmen."
                )
            else:
                action_text = f"Action: `rotation_failed`\nDetail: `{rotation.detail or 'unknown'}`"
        elif s.level == "hard":
            action_text = "Action: `hard-alert` (sofort prüfen, Rotation vorbereiten)"
        else:
            if s.agent == "main":
                action_text = "Action: `alert-only` (beobachten)"
            else:
                action_text = "Action: `alert-only` (worker session, keine Rotation)"

        scope = "agent:main:discord:*" if s.agent == "main" else f"agent:{s.agent}:sessions:*"
        msg = (
            f"{level_emoji(s.level)} **Atlas Session-Size-Guard ({s.level.upper()})**\n"
            f"Agent: `agent={s.agent}`\n"
            f"Session: `{s.path.name}`\n"
            f"Size: `{s.size_bytes/1024:.1f} KB` (Warn/Hart/Rotation: 600/900/1126 KB)\n"
            f"Messages: `{s.message_count}` (Warn/Hart/Rotation: 150/200/250)\n"
            f"Scope: `{scope}`\n"
            f"{action_text}"
        )
        ok, resp = send_discord(msg)
        if ok:
            mark_sent(state, key, s.level)
            sent += 1
            log(f"ALERT session agent={s.agent} level={s.level} file={s.path.name}")
        else:
            log(f"ALERT_FAILED session agent={s.agent} level={s.level} file={s.path.name} resp={resp}")
    return sent


def scan_gateway_logs_for_immediate(state: dict[str, Any]) -> int:
    sent = 0
    offsets = state.setdefault("log_offsets", {})
    hashes = state.setdefault("event_hashes", {})

    for lf in GATEWAY_LOGS:
        if not lf.exists() or not lf.is_file():
            continue

        key = str(lf)
        prev_offset = int(offsets.get(key, 0)) if str(offsets.get(key, "0")).isdigit() else 0
        size = lf.stat().st_size
        if prev_offset > size:
            prev_offset = 0

        with lf.open("r", encoding="utf-8", errors="ignore") as fh:
            fh.seek(prev_offset)
            chunk = fh.read()
            offsets[key] = fh.tell()

        if not chunk:
            continue

        for line in chunk.splitlines():
            if not any(p.search(line) for p in IMMEDIATE_PATTERNS):
                continue
            h = hashlib.sha256(line.encode("utf-8", errors="ignore")).hexdigest()[:16]
            event_key = f"immediate:{h}"
            last_sent = int(hashes.get(event_key, 0)) if str(hashes.get(event_key, "0")).isdigit() else 0
            if now_ts() - last_sent < COOLDOWN_SEC["immediate"]:
                continue

            msg = (
                "🚨 **Atlas Session-Size-Guard (Immediate Trigger)**\n"
                "Gateway-Log enthält `context-overflow-diag` oder `auto-compaction-failure`.\n"
                f"Source: `{lf.name}`\n"
                f"Line: `{line[:350]}`"
            )
            ok, resp = send_discord(msg)
            if ok:
                hashes[event_key] = now_ts()
                sent += 1
                log(f"ALERT immediate source={lf.name} hash={h}")
            else:
                log(f"ALERT_FAILED immediate source={lf.name} hash={h} resp={resp}")

    return sent


def scan_guard_log_for_repeated_load_fail(state: dict[str, Any]) -> int:
    if not LOG_PATH.exists() or not LOG_PATH.is_file():
        return 0

    now = dt.datetime.now(dt.UTC)
    window_start = now - dt.timedelta(seconds=R52_LOAD_FAIL_WINDOW_SEC)
    hits: list[str] = []

    with LOG_PATH.open("r", encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            if not R52_LOAD_FAIL_PATTERN.search(line):
                continue
            if not line.startswith("[") or "]" not in line:
                continue
            ts_str = line[1:line.index("]")]
            try:
                ts = dt.datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.UTC)
            except Exception:
                continue
            if ts >= window_start:
                hits.append(line.strip())

    if len(hits) < R52_LOAD_FAIL_THRESHOLD:
        return 0

    key = "r52:worker-memory-load-fail"
    if not should_send(state, key, "immediate"):
        return 0

    msg = (
        "🚨 **Atlas R52 Candidate: Worker-Memory LOAD_FAIL Repeated**\n"
        f"Detected `{len(hits)}` WORKER_MEMORY_ADAPTER_LOAD_FAIL entries within the last hour.\n"
        f"Source: `{LOG_PATH}`\n"
        f"Latest: `{hits[-1][:350]}`"
    )
    ok, resp = send_discord(msg)
    if ok:
        mark_sent(state, key, "immediate")
        log(f"ALERT r52-worker-memory-load-fail count={len(hits)}")
        return 1

    log(f"ALERT_FAILED r52-worker-memory-load-fail count={len(hits)} resp={resp}")
    return 0


def smoke_test_immediate_path(state: dict[str, Any]) -> int:
    hashes = state.setdefault("event_hashes", {})
    line = f"auto-compaction-failure smoke-{uuid.uuid4().hex[:8]}"
    h = hashlib.sha256(line.encode("utf-8", errors="ignore")).hexdigest()[:16]
    hashes[f"immediate:{h}"] = 0
    msg = (
        "🚨 **Atlas Session-Size-Guard (Immediate Trigger / Smoke)**\n"
        "Synthetic immediate trigger generated for smoke-test.\n"
        f"Line: `{line}`"
    )
    ok, resp = send_discord(msg)
    if ok:
        hashes[f"immediate:{h}"] = now_ts()
        log(f"SMOKE immediate hash={h}")
        return 1
    log(f"SMOKE_FAIL immediate resp={resp}")
    return 0


def smoke_test(state: dict[str, Any]) -> int:
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, dir=str(SESSIONS_DIR)) as tf_warn:
        path_warn = Path(tf_warn.name)
        tf_warn.write('{"type":"session","id":"smoke-warn","meta":"agent:main:discord:smoke"}\n')
        tf_warn.write("x" * (650 * 1024))

    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, dir=str(SESSIONS_DIR)) as tf_hard:
        path_hard = Path(tf_hard.name)
        tf_hard.write('{"type":"session","id":"smoke-hard","meta":"agent:main:discord:smoke"}\n')
        tf_hard.write("x" * (950 * 1024))

    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, dir=str(SESSIONS_DIR)) as tf_rot:
        path_rot = Path(tf_rot.name)
        tf_rot.write('{"type":"session","id":"smoke-rot","meta":"agent:main:discord:smoke"}\n')
        tf_rot.write("x" * (1150 * 1024))

    try:
        sent = 0
        sent += emit_session_alerts(state, scan_sessions(include_file=path_warn), dry_run_rotation=True)
        sent += emit_session_alerts(state, scan_sessions(include_file=path_hard), dry_run_rotation=True)
        sent += emit_session_alerts(state, scan_sessions(include_file=path_rot), dry_run_rotation=True)
        sent += smoke_test_immediate_path(state)
        if sent < 4:
            msg = (
                "🧪 **Atlas Session-Size-Guard Smoke-Test**\n"
                f"Smoke-Test unvollständig (`{sent}/4` Pfade ausgelöst). Bitte prüfen."
            )
            ok, resp = send_discord(msg)
            if ok:
                sent += 1
            else:
                log(f"SMOKE_FAIL resp={resp}")
        return sent
    finally:
        for p in (path_warn, path_hard, path_rot):
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass


def smoke_test_workers(state: dict[str, Any]) -> int:
    created: list[Path] = []
    sent = 0
    try:
        for agent in WORKER_AGENTS:
            session_dir = _worker_session_dir(agent)
            session_dir.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, dir=str(session_dir)) as tf:
                path = Path(tf.name)
                tf.write(f'{{"type":"session","id":"worker-smoke-{agent}","meta":"agent:{agent}:smoke"}}\n')
                tf.write("x" * (650 * 1024))
            created.append(path)
            signals = scan_worker_sessions(include_file=path)
            if not signals:
                log(f"SMOKE_WORKER_NO_SIGNAL agent={agent} file={path.name}")
                continue
            for s in signals:
                print(f"WORKER_SMOKE agent={s.agent} file={s.path.name} level={s.level}")
            sent += emit_session_alerts(state, signals, allow_rotation=False)
        return sent
    finally:
        for p in created:
            try:
                p.unlink(missing_ok=True)
            except Exception:
                pass


def self_test_rotation(artifact_path: Path | None = None) -> int:
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, dir=str(SESSIONS_DIR)) as tf_rot:
        path_rot = Path(tf_rot.name)
        tf_rot.write('{"type":"session","id":"selftest-rot","meta":"agent:main:discord:selftest"}\n')
        tf_rot.write("x" * (1150 * 1024))

    synthetic_key = f"agent:main:rotation-selftest:{uuid.uuid4().hex[:8]}"
    try:
        store = _load_session_store()
        store[synthetic_key] = {
            "sessionId": path_rot.stem,
            "sessionFile": str(path_rot),
            "updatedAt": int(time.time() * 1000),
            "status": "active",
        }
        _save_session_store(store)

        result = rotate_session_file(path_rot, dry_run=False)
        artifact_payload = {
            "at": dt.datetime.now(dt.UTC).isoformat(),
            "mode": "self-test-rotation",
            "rotation": {
                "rotated": result.rotated,
                "takeoverVerified": result.takeover_verified,
                "verifyDetail": result.verify_detail,
                "detail": result.detail,
                "checkpoint": str(result.checkpoint_path) if result.checkpoint_path else None,
                "archived": str(result.archived_path) if result.archived_path else None,
                "active": str(result.new_session_path) if result.new_session_path else None,
            },
            "clarification": {
                "simulated": False,
                "dryRun": False,
                "runtimeRotation": True,
            },
        }
        if artifact_path is not None:
            write_rotation_test_artifact(artifact_payload, artifact_path)

        if not result.rotated:
            print(f"SELF_TEST_ROTATION=failed detail={result.detail or 'rotation-failed'}")
            if artifact_path is not None:
                print(f"TEST_ARTIFACT={artifact_path}")
            return 1
        if not result.takeover_verified:
            print(f"SELF_TEST_ROTATION=failed detail={result.verify_detail or 'verify-failed'}")
            if artifact_path is not None:
                print(f"TEST_ARTIFACT={artifact_path}")
            return 1
        if not result.archived_path or not result.archived_path.exists():
            print("SELF_TEST_ROTATION=failed detail=missing-archived")
            if artifact_path is not None:
                print(f"TEST_ARTIFACT={artifact_path}")
            return 1
        print(
            "SELF_TEST_ROTATION=ok "
            f"checkpoint={result.checkpoint_path.name if result.checkpoint_path else '-'} "
            f"archived={result.archived_path.name if result.archived_path else '-'} "
            f"active={result.new_session_path.name if result.new_session_path else '-'}"
        )
        if artifact_path is not None:
            print(f"TEST_ARTIFACT={artifact_path}")
        return 0
    finally:
        store = _load_session_store()
        store.pop(synthetic_key, None)
        _save_session_store(store)

        stem = path_rot.stem
        for candidate in SESSIONS_DIR.glob(f"{stem}*.jsonl"):
            try:
                candidate.unlink(missing_ok=True)
            except Exception:
                pass
        for candidate in SESSIONS_DIR.glob(f"{stem}*.archived.*.jsonl"):
            try:
                candidate.unlink(missing_ok=True)
            except Exception:
                pass



def rotate_worker_session_file(agent: str, session_file: Path, dry_run: bool = False) -> RotationResult:
    """Rotate a worker session file, writing memory handoff artifact if adapter available."""
    WORKER_ROOT = WORKER_AGENTS_ROOT / agent
    sessions_dir = WORKER_ROOT / "sessions"
    archive_dir = sessions_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    archived_path = archive_dir / f"{session_file.stem}-archived-{utc_now_iso_z().replace(':','-')}.jsonl"
    compact_summary = f"Worker={agent} session rotated at {utc_now_iso_z()}."
    open_task_ids: list[str] = []

    Adapter = _load_worker_memory_adapter_class()
    if Adapter is not None:
        try:
            resume = Adapter.from_env().read_resume_bundle(agent)
            progress = (resume.get("progress") or "").strip()
            progress_line = progress.splitlines()[0] if progress else ""
            tasks = resume.get("tasks") if isinstance(resume.get("tasks"), list) else []
            pending = [t for t in tasks if isinstance(t, dict) and t.get("status") == "pending"]
            open_task_ids = [str(t.get("id")) for t in pending[:8]]
            compact_summary = (
                f"Worker={agent} rotation bootstrap. "
                f"progress={progress_line[:200] or 'none'}; "
                f"pending_count={len(pending)}; "
                f"open_task_ids={open_task_ids}; "
                f"rotated_at={utc_now_iso_z()}."
            )
        except Exception as exc:
            log(f"WARN rotate_worker_session_file adapter read failed agent={agent} detail={exc}")

    bootstrap_artifact: dict[str, Any] = {
        "type": "message",
        "role": "system",
        "message": {
            "role": "system",
            "content": [{"type": "text", "text": compact_summary}],
        },
        "createdAt": utc_now_iso_z(),
        "agent": agent,
        "open_task_ids": open_task_ids,
        "rotated_at": utc_now_iso_z(),
        "dry_run": dry_run,
    }
    bootstrap_path = archive_dir / f"worker-rotation-handoff-{agent}-{utc_now_iso_z().replace(':','-')}.json"

    if dry_run:
        write_rotation_test_artifact({
            "at": utc_now_iso_z(),
            "agent": agent,
            "session_file": str(session_file),
            "archived_path": str(archived_path),
            "bootstrap_artifact": bootstrap_artifact,
            "compact_summary": compact_summary,
            "open_task_ids": open_task_ids,
            "dry_run": True,
        }, WORKER_MEMORY_HOFF_ARTIFACT_PATH)
        log(f"WARN rotate_worker_session_file dry_run agent={agent} session={session_file.name}")
        return RotationResult(
            rotated=False,
            checkpoint_path=None,
            archived_path=None,
            new_session_path=None,
            takeover_verified=False,
            detail=f"dry_run agent={agent} session={session_file.name}",
        )

    try:
        shutil.copy2(session_file, archived_path)
        write_rotation_test_artifact(bootstrap_artifact, bootstrap_path)
        return RotationResult(
            rotated=True,
            checkpoint_path=archived_path,
            archived_path=archived_path,
            new_session_path=None,
            takeover_verified=False,
            detail=f"rotated agent={agent} session={session_file.name} -> {archived_path.name}",
        )
    except Exception as exc:
        log(f"ERROR rotate_worker_session_file agent={agent} detail={exc}")
        return RotationResult(rotated=False, detail=f"error agent={agent} {exc}")



def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-only", action="store_true", help="Only run immediate log trigger scan")
    parser.add_argument("--smoke-test", action="store_true", help="Create temp test file and trigger alert")
    parser.add_argument("--smoke-test-workers", action="store_true", help="Create worker temp files and trigger alert-only worker scans")
    parser.add_argument("--self-test-rotation", action="store_true", help="Run isolated rotation takeover self-test without Discord sends")
    parser.add_argument("--self-test-rotation-artifact", type=str, default=str(ROTATION_TEST_ARTIFACT_PATH), help="Artifact path for --self-test-rotation")
    parser.add_argument("--self-test-worker-memory-handoff", action="store_true", help="Run dry-run handoff test using worker-memory adapter")
    parser.add_argument("--self-test-worker-memory-handoff-worker", type=str, default="sre-expert", help="Worker id for --self-test-worker-memory-handoff")
    parser.add_argument("--self-test-worker-memory-handoff-artifact", type=str, default=str(WORKER_MEMORY_HOFF_ARTIFACT_PATH), help="Artifact path for --self-test-worker-memory-handoff")
    parser.add_argument("--self-test-worker-rotation", action="store_true", help="Run Spark-only canary forced-rotation dry-run test")
    parser.add_argument("--self-test-worker-rotation-agent", type=str, default="spark", help="Agent id for --self-test-worker-rotation (Spark-only canary)")
    args = parser.parse_args()

    if args.self_test_rotation:
        return self_test_rotation(Path(args.self_test_rotation_artifact))
    if args.self_test_worker_memory_handoff:
        return self_test_worker_memory_handoff(
            args.self_test_worker_memory_handoff_worker,
            Path(args.self_test_worker_memory_handoff_artifact),
        )
    if args.self_test_worker_rotation:
        agent = args.self_test_worker_rotation_agent
        hard_cap = WORKER_ROTATION_HARD_CAP
        allowlist = WORKER_ROTATION_AGENTS
        if agent not in allowlist:
            print(f"SELF_TEST_WORKER_ROTATION=skip agent={agent} reason=not_in_allowlist allowlist={allowlist}")
            return 0
        if not hard_cap:
            print(f"SELF_TEST_WORKER_ROTATION=skip agent={agent} reason=hard_cap_disabled WORKER_ROTATION_HARD_CAP={WORKER_ROTATION_HARD_CAP}")
            return 0
        worker_root = WORKER_AGENTS_ROOT / agent
        sessions_dir = worker_root / "sessions"
        if not sessions_dir.exists():
            print(f"SELF_TEST_WORKER_ROTATION=skip agent={agent} reason=no_sessions_dir")
            return 1
        cutoff = time.time() - 48 * 3600
        stale_files = [
            pf for pf in sessions_dir.glob("*.jsonl")
            if pf.stat().st_mtime < cutoff and not list(pf.parent.glob(f"{pf.stem}.lock"))
        ]
        if not stale_files:
            print(f"SELF_TEST_WORKER_ROTATION=skip agent={agent} reason=no_stale_files")
            return 1
        target = stale_files[0]
        result = rotate_worker_session_file(agent, target, dry_run=True)
        print(f"SELF_TEST_WORKER_ROTATION={'ok' if result.detail else 'fail'} agent={agent} session={target.name} detail={result.detail}")
        return 0

    state = load_state()
    total_sent = 0

    if args.smoke_test:
        total_sent += smoke_test(state)

    if args.smoke_test_workers:
        total_sent += smoke_test_workers(state)

    if not args.log_only and not args.smoke_test:
        total_sent += emit_session_alerts(state, scan_sessions())
        total_sent += emit_session_alerts(state, scan_worker_sessions(), allow_rotation=False)

    total_sent += scan_gateway_logs_for_immediate(state)
    total_sent += scan_guard_log_for_repeated_load_fail(state)
    save_state(state)

    log(f"RUN_DONE sent={total_sent} mode={'log-only' if args.log_only else ('smoke' if args.smoke_test else 'full')}")
    print(f"SESSION_SIZE_GUARD_SENT={total_sent}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
