#!/usr/bin/env python3
"""Gateway heap / RSS memory monitor. Run via cron every 5 min."""
from pathlib import Path
import os
import subprocess
import sys
import time
import urllib.request

THRESHOLD_WARNING_KB = 1_400_000   # ~1.34 GB
THRESHOLD_CRITICAL_KB = 1_700_000  # ~1.62 GB
LOG_PATH = Path("/home/piet/.openclaw/workspace/logs/gateway-memory-monitor.log")
COOLDOWN_FILE = Path("/tmp/gateway-memory-alert.cooldown")
COOLDOWN_SEC = 30 * 60            # 30 minutes
USER_AGENT = "mc-gateway-monitor/1.0 (+openclaw; python-urllib)"
WEBHOOK_URL = os.environ.get("AUTO_PICKUP_WEBHOOK_URL", "")


def get_gateway_rss() -> int | None:
    """Return RSS in kB for the primary openclaw gateway process, or None.
    Respects MOCK_RSS_KB env for testing."""
    mock = os.environ.get("MOCK_RSS_KB", "").strip()
    if mock:
        try:
            return int(mock)
        except ValueError:
            pass

    try:
        result = subprocess.run(
            ["pgrep", "-f", "openclaw.*gateway"],
            capture_output=True, text=True, timeout=5,
        )
        pids = result.stdout.strip().split()
        if not pids:
            return None
        pid = int(pids[0])
        with open(f"/proc/{pid}/status") as f:
            for line in f:
                if line.startswith("VmRSS:"):
                    return int(line.split()[1])  # kB
    except Exception:
        pass
    return None


def is_cooldown_active() -> bool:
    """Return True if cooldown file exists and is younger than COOLDOWN_SEC."""
    if not COOLDOWN_FILE.exists():
        return False
    try:
        age = time.time() - COOLDOWN_FILE.stat().st_mtime
        return age < COOLDOWN_SEC
    except OSError:
        return False


def touch_cooldown() -> None:
    """Create/update cooldown marker file."""
    try:
        COOLDOWN_FILE.parent.mkdir(parents=True, exist_ok=True)
        COOLDOWN_FILE.touch()
    except OSError:
        pass


def send_discord_alert(rss_kb: int, ts: str) -> bool:
    """Send critical alert to Discord webhook. Returns True on success."""
    if not WEBHOOK_URL:
        print(f"[{ts}] discord_alert=skip reason=no_webhook_url")
        return False

    if is_cooldown_active():
        print(f"[{ts}] discord_alert=skip reason=cooldown_active")
        return False

    rss_gb = rss_kb / 1024 / 1024
    payload = f'{{"content": "🚨 **Gateway OOM Critical** — RSS={rss_gb:.1f}GB (>{THRESHOLD_CRITICAL_KB/1024/1024:.1f}GB threshold). Restart window recommended before crash."}}'.encode("utf-8")

    try:
        req = urllib.request.Request(
            WEBHOOK_URL,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": USER_AGENT,
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status in (200, 204):
                touch_cooldown()
                print(f"[{ts}] discord_alert=sent rss_kb={rss_kb}")
                return True
            else:
                print(f"[{ts}] discord_alert=fail status={resp.status}")
                return False
    except Exception as e:
        print(f"[{ts}] discord_alert=error err={e}")
        return False


def main() -> int:
    rss = get_gateway_rss()
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if rss is None:
        msg = f"[{ts}] gateway_memory=unknown reason=no_pid_found"
        print(msg)
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        LOG_PATH.open("a").write(msg + "\n")
        return 1

    level = (
        "critical"
        if rss >= THRESHOLD_CRITICAL_KB
        else "warning"
        if rss >= THRESHOLD_WARNING_KB
        else "ok"
    )
    msg = (
        f"[{ts}] gateway_memory={level} "
        f"rss_kb={rss} "
        f"threshold_warning_kb={THRESHOLD_WARNING_KB} "
        f"threshold_critical_kb={THRESHOLD_CRITICAL_KB}"
    )
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.open("a").write(msg + "\n")
    print(msg)

    if level == "critical":
        send_discord_alert(rss, ts)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
