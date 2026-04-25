#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SESSIONS_DIR = Path("/home/piet/.openclaw/agents/main/sessions")
SESSION_STORE_PATH = SESSIONS_DIR / "sessions.json"
STATE_PATH = Path("/home/piet/.openclaw/workspace/logs/session-size-guard.state.json")
LOG_PATH = Path("/home/piet/.openclaw/workspace/logs/session-size-guard.log")
ROTATION_TEST_ARTIFACT_PATH = Path("/home/piet/.openclaw/workspace/logs/session-size-guard.rotation-selftest.json")
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
    "rotation": 5 * 60,
    "immediate": 5 * 60,
}

IMMEDIATE_PATTERNS = [
    re.compile(r"context-overflow-diag", re.IGNORECASE),
    re.compile(r"auto-compaction-failure", re.IGNORECASE),
]


@dataclass
class SessionSignal:
    path: Path
    size_bytes: int
    message_count: int
    level: str | None


@dataclass
class RotationResult:
    rotated: bool
    checkpoint_path: Path | None = None
    archived_path: Path | None = None
    new_session_path: Path | None = None
    takeover_verified: bool = False
    verify_detail: str | None = None
    detail: str | None = None


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


def scan_sessions(include_file: Path | None = None) -> list[SessionSignal]:
    out: list[SessionSignal] = []
    files = [include_file] if include_file else sorted(SESSIONS_DIR.glob("*.jsonl"))
    for f in files:
        if not f or not f.exists():
            continue
        n = f.name
        if is_ignored_session_artifact(f):
            continue
        if include_file is None and not is_discord_main_session(f):
            continue
        size_bytes = f.stat().st_size
        message_count = count_messages(f)
        level = classify(size_bytes, message_count)
        out.append(SessionSignal(path=f, size_bytes=size_bytes, message_count=message_count, level=level))
    return out


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


def _find_store_binding_for_file(store: dict[str, Any], session_file: Path) -> tuple[str, dict[str, Any]] | None:
    target = str(session_file)
    for key, value in store.items():
        if not isinstance(value, dict):
            continue
        if value.get("sessionFile") == target:
            return key, value
    return None


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
            return RotationResult(rotated=False, detail="runtime-binding-not-found")
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


def emit_session_alerts(state: dict[str, Any], signals: list[SessionSignal], *, dry_run_rotation: bool = False) -> int:
    sent = 0
    for s in signals:
        if not s.level:
            continue
        key = f"session:{s.path.name}"
        if not should_send(state, key, s.level):
            continue

        if s.level == "rotation":
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
            action_text = "Action: `alert-only` (beobachten)"

        msg = (
            f"{level_emoji(s.level)} **Atlas Session-Size-Guard ({s.level.upper()})**\n"
            f"Session: `{s.path.name}`\n"
            f"Size: `{s.size_bytes/1024:.1f} KB` (Warn/Hart/Rotation: 600/900/1126 KB)\n"
            f"Messages: `{s.message_count}` (Warn/Hart/Rotation: 150/200/250)\n"
            f"Scope: `agent:main:discord:*`\n"
            f"{action_text}"
        )
        ok, resp = send_discord(msg)
        if ok:
            mark_sent(state, key, s.level)
            sent += 1
            log(f"ALERT session level={s.level} file={s.path.name}")
        else:
            log(f"ALERT_FAILED session level={s.level} file={s.path.name} resp={resp}")
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


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-only", action="store_true", help="Only run immediate log trigger scan")
    parser.add_argument("--smoke-test", action="store_true", help="Create temp test file and trigger alert")
    parser.add_argument("--self-test-rotation", action="store_true", help="Run isolated rotation takeover self-test without Discord sends")
    parser.add_argument("--self-test-rotation-artifact", type=str, default=str(ROTATION_TEST_ARTIFACT_PATH), help="Artifact path for --self-test-rotation")
    args = parser.parse_args()

    if args.self_test_rotation:
        return self_test_rotation(Path(args.self_test_rotation_artifact))

    state = load_state()
    total_sent = 0

    if args.smoke_test:
        total_sent += smoke_test(state)

    if not args.log_only and not args.smoke_test:
        total_sent += emit_session_alerts(state, scan_sessions())

    total_sent += scan_gateway_logs_for_immediate(state)
    save_state(state)

    log(f"RUN_DONE sent={total_sent} mode={'log-only' if args.log_only else ('smoke' if args.smoke_test else 'full')}")
    print(f"SESSION_SIZE_GUARD_SENT={total_sent}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
