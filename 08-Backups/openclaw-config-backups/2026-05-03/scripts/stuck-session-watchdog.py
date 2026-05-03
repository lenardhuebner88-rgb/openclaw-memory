#!/usr/bin/env python3
"""
stuck-session-watchdog.py
Detects stuck openclaw-gateway sessions via journald and auto-restarts the gateway.
Run via systemd timer (openclaw-stuck-watchdog.timer) every 5 minutes.

A session is "stuck" when the diagnostic module logs it with age >= STUCK_AGE_THRESHOLD_S
and queueDepth=0 (nothing queued, but Claude subprocess is not responding).
"""

import json
import re
import subprocess
import sys
from datetime import datetime, timezone

SERVICE = "openclaw-gateway"
AUDIT_LOG = "/home/piet/bots/commander/logs/audit.jsonl"
STUCK_AGE_THRESHOLD_S = 300  # only act if age >= 5 min (gateway logs at 30s intervals)
LOOKBACK = "10 minutes ago"


def get_stuck_sessions():
    """Parse journald for stuck-session log lines in the last LOOKBACK window."""
    result = subprocess.run(
        ["journalctl", "--user", "-u", SERVICE, "--since", LOOKBACK, "-o", "json", "--no-pager"],
        capture_output=True, text=True
    )
    stuck = []
    for line in result.stdout.splitlines():
        try:
            entry = json.loads(line)
            msg = entry.get("MESSAGE", "")
            if "stuck session:" not in msg:
                continue
            m = re.search(r"age=(\d+)s", msg)
            if not m:
                continue
            age_s = int(m.group(1))
            if age_s >= STUCK_AGE_THRESHOLD_S:
                sid = re.search(r"sessionId=(\S+)", msg)
                stuck.append({
                    "sessionId": sid.group(1) if sid else "unknown",
                    "age_s": age_s,
                    "msg": msg,
                })
        except (json.JSONDecodeError, KeyError):
            continue
    return stuck


def restart_gateway(reason):
    subprocess.run(["systemctl", "--user", "restart", SERVICE], check=True)


def audit(action, rationale, verified):
    entry = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "action": action,
        "path": f"{SERVICE}.service",
        "rationale": rationale,
        "rollback": f"systemctl --user restart {SERVICE}",
        "verified": verified,
    }
    with open(AUDIT_LOG, "a") as f:
        f.write(json.dumps(entry) + "\n")


def main():
    stuck = get_stuck_sessions()
    if not stuck:
        print(f"[watchdog] ok — no stuck sessions >= {STUCK_AGE_THRESHOLD_S}s in last {LOOKBACK}")
        return 0

    ages = [s["age_s"] for s in stuck]
    sessions = [s["sessionId"] for s in stuck]
    rationale = f"watchdog: {len(stuck)} stuck session(s) detected — sessions={sessions} ages={ages}s >= {STUCK_AGE_THRESHOLD_S}s threshold"
    print(f"[watchdog] {rationale} — restarting {SERVICE}")

    restart_gateway(rationale)

    # Verify
    check = subprocess.run(
        ["systemctl", "--user", "is-active", SERVICE],
        capture_output=True, text=True
    )
    state = check.stdout.strip()
    verified = f"post-restart is-active={state}"
    print(f"[watchdog] {verified}")
    audit("restart", rationale, verified)

    if state != "active":
        print(f"[watchdog] ERROR: {SERVICE} not active after restart — manual intervention required", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
