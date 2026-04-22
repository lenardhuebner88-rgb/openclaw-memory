#!/usr/bin/env python3
"""Session health monitor for OpenClaw worker sessions.

Scans ~/.openclaw/agents/*/sessions and reports anomalies:
- orphaned lockfiles (lock present, pid dead)
- zombie sessions (dead lock + session file still hot)
- ghost sessions (jsonl < 1KB and older than 30 min)
- size exploded sessions (> 2MB)

Writes newline-delimited JSON to:
  /home/piet/.openclaw/workspace/memory/session-health.log

Alerts only on NEW anomalies (dedupe via state file).
"""

from __future__ import annotations

import glob
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

SESSIONS_GLOB = "/home/piet/.openclaw/agents/*/sessions"
LOG_FILE = Path("/home/piet/.openclaw/workspace/memory/session-health.log")
STATE_FILE = Path("/tmp/session-health-monitor-state.json")
API_BASE = os.environ.get("AUTO_PICKUP_API", "http://127.0.0.1:3000")
ALERT_CHANNEL = os.environ.get("AUTO_PICKUP_ALERT_CH", "1491148986109661334")
ALERT_WEBHOOK_URL = os.environ.get("AUTO_PICKUP_WEBHOOK_URL", "").strip()
GHOST_MIN_AGE_SEC = int(os.environ.get("SESSION_HEALTH_GHOST_MIN_AGE", "1800"))
GHOST_MAX_BYTES = int(os.environ.get("SESSION_HEALTH_GHOST_MAX_BYTES", "1024"))
EXPLODED_BYTES = int(os.environ.get("SESSION_HEALTH_EXPLODED_BYTES", str(2 * 1024 * 1024)))


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True


def load_state() -> set[str]:
    if not STATE_FILE.exists():
        return set()
    try:
        raw = json.loads(STATE_FILE.read_text())
        if isinstance(raw, list):
            return {str(x) for x in raw}
    except Exception:
        pass
    return set()


def save_state(keys: set[str]) -> None:
    STATE_FILE.write_text(json.dumps(sorted(keys)))


def alert(text: str) -> None:
    content = f"⚠️ **session-health-monitor** — {text}"
    if ALERT_WEBHOOK_URL:
        req = Request(
            ALERT_WEBHOOK_URL,
            data=json.dumps({"content": content, "username": "Session Health Monitor"}).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "session-health-monitor/1.0 (+openclaw)",
            },
            method="POST",
        )
    else:
        req = Request(
            f"{API_BASE}/api/discord/send",
            data=json.dumps({"channelId": ALERT_CHANNEL, "message": content}).encode("utf-8"),
            headers={"Content-Type": "application/json", "x-actor-kind": "system", "x-request-class": "write"},
            method="POST",
        )
    try:
        with urlopen(req, timeout=10) as resp:
            resp.read()
    except Exception:
        pass


def scan() -> tuple[list[dict], list[str]]:
    now = time.time()
    anomalies: list[dict] = []
    keys: list[str] = []

    for sessions_dir_str in glob.glob(SESSIONS_GLOB):
        sessions_dir = Path(sessions_dir_str)
        agent = sessions_dir.parts[-2] if len(sessions_dir.parts) >= 2 else "unknown"

        for lock_file in sessions_dir.glob("*.jsonl.lock"):
            session_file = lock_file.with_suffix("")
            pid = 0
            try:
                raw = json.loads(lock_file.read_text())
                pid_raw = raw.get("pid") if isinstance(raw, dict) else None
                pid = int(pid_raw) if isinstance(pid_raw, int) or (isinstance(pid_raw, str) and str(pid_raw).isdigit()) else 0
            except Exception:
                pass

            alive = process_alive(pid)
            lock_age = int(now - lock_file.stat().st_mtime)
            if not alive:
                key = f"orphan-lock:{agent}:{lock_file.name}"
                anomalies.append({
                    "ts": now_iso(),
                    "type": "orphan-lock",
                    "agent": agent,
                    "lock": str(lock_file),
                    "session": str(session_file),
                    "pid": pid,
                    "lockAgeSec": lock_age,
                })
                keys.append(key)

                if session_file.exists() and (now - session_file.stat().st_mtime) < GHOST_MIN_AGE_SEC:
                    zkey = f"zombie-session:{agent}:{session_file.name}"
                    anomalies.append({
                        "ts": now_iso(),
                        "type": "zombie-session",
                        "agent": agent,
                        "session": str(session_file),
                        "pid": pid,
                        "sessionBytes": session_file.stat().st_size,
                        "sessionMtimeAgeSec": int(now - session_file.stat().st_mtime),
                    })
                    keys.append(zkey)

        for session_file in sessions_dir.glob("*.jsonl"):
            size = session_file.stat().st_size
            age_sec = int(now - session_file.stat().st_mtime)
            if size < GHOST_MAX_BYTES and age_sec >= GHOST_MIN_AGE_SEC:
                key = f"ghost-session:{agent}:{session_file.name}"
                anomalies.append({
                    "ts": now_iso(),
                    "type": "ghost-session",
                    "agent": agent,
                    "session": str(session_file),
                    "sessionBytes": size,
                    "sessionMtimeAgeSec": age_sec,
                })
                keys.append(key)

            if size > EXPLODED_BYTES:
                key = f"size-exploded:{agent}:{session_file.name}"
                anomalies.append({
                    "ts": now_iso(),
                    "type": "size-exploded",
                    "agent": agent,
                    "session": str(session_file),
                    "sessionBytes": size,
                    "sessionMtimeAgeSec": age_sec,
                })
                keys.append(key)

    return anomalies, keys


def main() -> int:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    anomalies, keys = scan()
    for row in anomalies:
        LOG_FILE.open("a").write(json.dumps(row, ensure_ascii=False) + "\n")

    prev = load_state()
    current = set(keys)
    new = sorted(current - prev)

    if new:
        alert(f"{len(new)} neue Anomalie(n): " + ", ".join(new[:5]))

    save_state(current)
    summary = {
        "ts": now_iso(),
        "type": "summary",
        "anomalyCount": len(anomalies),
        "newCount": len(new),
    }
    LOG_FILE.open("a").write(json.dumps(summary, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
