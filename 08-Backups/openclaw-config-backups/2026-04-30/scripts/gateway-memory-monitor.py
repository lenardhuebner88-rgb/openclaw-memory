#!/usr/bin/env python3
"""Gateway heap / RSS memory monitor. Run via cron every 5 min.

Patched 2026-04-29:
- Thresholds raised to match MemoryHigh=5G / MemoryMax=6G era
  (previous 1.4G/1.7G were stale from pre-MCP-Hardening-sprint)
- PID discovery now uses systemctl MainPID (avoids pgrep matching the
  monitor script itself, which caused rss_kb=3732 false-readings)
"""
from pathlib import Path
import os
import subprocess
import sys
import time
import urllib.request

THRESHOLD_WARNING_KB = 4_000_000   # ~3.8 GB (well below MemoryHigh=5G)
THRESHOLD_CRITICAL_KB = 5_500_000  # ~5.2 GB (urgent before MemoryMax=6G)
LOG_PATH = Path("/home/piet/.openclaw/workspace/logs/gateway-memory-monitor.log")
COOLDOWN_FILE = Path("/tmp/gateway-memory-alert.cooldown")
COOLDOWN_SEC = 30 * 60            # 30 minutes
USER_AGENT = "mc-gateway-monitor/1.0 (+openclaw; python-urllib)"
WEBHOOK_URL = os.environ.get("AUTO_PICKUP_WEBHOOK_URL", "")


def get_gateway_rss() -> int | None:
    """Return RSS in kB for the primary openclaw gateway process, or None.
    Respects MOCK_RSS_KB env for testing.

    Discovery order:
      1. systemctl --user MainPID for openclaw-gateway (most reliable)
      2. pgrep fallback with self-PID exclusion + max-RSS pick
    """
    mock = os.environ.get("MOCK_RSS_KB", "").strip()
    if mock:
        try:
            return int(mock)
        except ValueError:
            pass

    # Primary: systemctl MainPID
    try:
        result = subprocess.run(
            ["systemctl", "--user", "show", "openclaw-gateway",
             "-p", "MainPID", "--value"],
            capture_output=True, text=True, timeout=5,
        )
        pid_str = result.stdout.strip()
        if pid_str.isdigit() and int(pid_str) > 0:
            pid = int(pid_str)
            with open(f"/proc/{pid}/status") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        return int(line.split()[1])  # kB
    except Exception:
        pass

    # Fallback: pgrep with self-exclusion + max-RSS pick
    try:
        result = subprocess.run(
            ["pgrep", "-f", "openclaw-gateway"],
            capture_output=True, text=True, timeout=5,
        )
        own_pid = os.getpid()
        pids = []
        for p in result.stdout.strip().split():
            try:
                pid_int = int(p)
                if pid_int != own_pid:
                    pids.append(pid_int)
            except ValueError:
                continue
        if not pids:
            return None
        best_rss = 0
        for pid in pids:
            try:
                with open(f"/proc/{pid}/status") as f:
                    for line in f:
                        if line.startswith("VmRSS:"):
                            rss = int(line.split()[1])
                            if rss > best_rss:
                                best_rss = rss
                            break
            except Exception:
                continue
        return best_rss if best_rss > 0 else None
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
