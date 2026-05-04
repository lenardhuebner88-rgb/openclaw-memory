#!/usr/bin/env python3
"""Gateway heap / RSS memory monitor. Run via cron every 5 min.

Patched 2026-04-29:
- Thresholds raised to match MemoryHigh=5G / MemoryMax=6G era
  (previous 1.4G/1.7G were stale from pre-MCP-Hardening-sprint)
- PID discovery now uses systemctl MainPID (avoids pgrep matching the
  monitor script itself, which caused rss_kb=3732 false-readings)

Patched 2026-05-03:
- Added Discord Gateway transport watchdog. Gateway HTTP health can remain
  green while Discord inbound WebSocket transport is stale; this checks
  `openclaw health --json` and performs a guarded stop/start when Discord
  transport activity is older than the configured threshold.
"""
import json
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
OPENCLAW_BIN = os.environ.get("OPENCLAW_BIN", "/home/piet/bin/openclaw")

DISCORD_WATCHDOG_ENABLED = os.environ.get("OPENCLAW_DISCORD_WATCHDOG_ENABLED", "1") == "1"
DISCORD_STALE_THRESHOLD_SEC = int(os.environ.get("OPENCLAW_DISCORD_STALE_THRESHOLD_SEC", "600"))
DISCORD_RESTART_COOLDOWN_SEC = int(os.environ.get("OPENCLAW_DISCORD_RESTART_COOLDOWN_SEC", "1800"))
DISCORD_COOLDOWN_FILE = Path("/tmp/openclaw-discord-ws-watchdog.cooldown")
DISCORD_TEST_MODE = os.environ.get("OPENCLAW_DISCORD_WATCHDOG_TEST_MODE", "0") == "1"


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


def is_path_cooldown_active(path: Path, cooldown_sec: int) -> bool:
    if not path.exists():
        return False
    try:
        return time.time() - path.stat().st_mtime < cooldown_sec
    except OSError:
        return False


def touch_path(path: Path) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
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


GATEWAY_HTTP_URL = os.environ.get("OPENCLAW_GATEWAY_HTTP_URL", "http://127.0.0.1:18789")


def load_openclaw_health(ts: str) -> dict | None:
    # Try openclaw CLI first (preferred, returns rich channel-level data)
    try:
        result = subprocess.run(
            [OPENCLAW_BIN, "health", "--json"],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        # CLI failed — check if it's a Node version issue
        stderr = result.stderr.strip().lower()
        if "node.js v22" in stderr or "v20" in stderr:
            print(f"[{ts}] discord_watchdog=skip reason=openclaw_node_version_too_old cli=openclaw_health")
            # Fall through to HTTP fallback
        else:
            print(f"[{ts}] discord_watchdog=skip reason=health_command_failed rc={result.returncode} stderr={result.stderr.strip()[:200]}")
            return None
    except FileNotFoundError:
        print(f"[{ts}] discord_watchdog=skip reason=openclaw_bin_not_found bin={OPENCLAW_BIN}")
        # Fall through to HTTP fallback
    except Exception as err:
        print(f"[{ts}] discord_watchdog=skip reason=health_command_error err={err}")
        # Fall through to HTTP fallback

    # HTTP fallback: direct gateway health endpoint (always uses bundled Node)
    try:
        req = urllib.request.Request(
            f"{GATEWAY_HTTP_URL}/health",
            headers={"User-Agent": USER_AGENT},
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                return json.loads(resp.read())
    except Exception as err:
        print(f"[{ts}] discord_watchdog=skip reason=health_http_fallback_failed err={err}")

    return None


def resolve_discord_account_health(health: dict) -> dict | None:
    discord = (health.get("channels") or {}).get("discord")
    if not isinstance(discord, dict):
        return None
    accounts = discord.get("accounts")
    if isinstance(accounts, dict):
        default = accounts.get("default")
        if isinstance(default, dict):
            return default
        for account in accounts.values():
            if isinstance(account, dict):
                return account
    return discord


def restart_gateway_for_discord_stale(ts: str, age_sec: int, last_transport_at: int | None) -> bool:
    if is_path_cooldown_active(DISCORD_COOLDOWN_FILE, DISCORD_RESTART_COOLDOWN_SEC):
        print(f"[{ts}] discord_watchdog=stale action=skip reason=cooldown_active age_sec={age_sec}")
        return False
    touch_path(DISCORD_COOLDOWN_FILE)
    if DISCORD_TEST_MODE:
        print(f"[{ts}] discord_watchdog=stale action=test-mode age_sec={age_sec} lastTransportActivityAt={last_transport_at}")
        return True

    print(f"[{ts}] discord_watchdog=stale action=restart-gateway age_sec={age_sec} lastTransportActivityAt={last_transport_at}")
    stop = subprocess.run(
        ["systemctl", "--user", "stop", "openclaw-gateway.service"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    time.sleep(2)
    start = subprocess.run(
        ["systemctl", "--user", "start", "openclaw-gateway.service"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    ok = stop.returncode == 0 and start.returncode == 0
    if ok:
        print(f"[{ts}] discord_watchdog=restart_complete result=ok")
    else:
        print(
            f"[{ts}] discord_watchdog=restart_complete result=failed "
            f"stop_rc={stop.returncode} start_rc={start.returncode} "
            f"stop_err={stop.stderr.strip()[:200]} start_err={start.stderr.strip()[:200]}"
        )
    return ok


def check_discord_gateway_transport(ts: str) -> int:
    if not DISCORD_WATCHDOG_ENABLED:
        print(f"[{ts}] discord_watchdog=skip reason=disabled")
        return 0

    health = load_openclaw_health(ts)
    if not health:
        return 0
    account = resolve_discord_account_health(health)
    if not account:
        print(f"[{ts}] discord_watchdog=skip reason=no_discord_health")
        return 0

    configured = account.get("configured") is True
    running = account.get("running") is True
    connected = account.get("connected") is True
    restart_pending = account.get("restartPending") is True
    last_transport_at = account.get("lastTransportActivityAt")
    now_ms = int(time.time() * 1000)

    if not configured or not running:
        print(f"[{ts}] discord_watchdog=ok configured={configured} running={running}")
        return 0
    if restart_pending:
        print(f"[{ts}] discord_watchdog=skip reason=restart_pending")
        return 0

    if not isinstance(last_transport_at, int) or last_transport_at <= 0:
        age_sec = DISCORD_STALE_THRESHOLD_SEC + 1 if connected else 0
        last_transport_ms = None
    else:
        age_sec = max(0, (now_ms - last_transport_at) // 1000)
        last_transport_ms = last_transport_at

    if connected and age_sec > DISCORD_STALE_THRESHOLD_SEC:
        restarted = restart_gateway_for_discord_stale(ts, age_sec, last_transport_ms)
        return 2 if restarted else 1

    print(
        f"[{ts}] discord_watchdog=ok connected={connected} "
        f"transport_age_sec={age_sec} threshold_sec={DISCORD_STALE_THRESHOLD_SEC}"
    )
    return 0


def main() -> int:
    rss = get_gateway_rss()
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if rss is None:
        msg = f"[{ts}] gateway_memory=unknown reason=no_pid_found"
        print(msg)
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        LOG_PATH.open("a").write(msg + "\n")
        # Discord watchdog must always run — even when PID is unknown
        check_discord_gateway_transport(ts)
        return 0

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

    check_discord_gateway_transport(ts)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
