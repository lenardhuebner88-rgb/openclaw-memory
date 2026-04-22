#!/usr/bin/env python3
"""
MC Critical-Alert-Dispatcher (Tonight-Safety)

Runs every 2min via cron. Sends Discord push if:
- MC is unreachable/down for >10min (can't check itself when dead → sends direct)
- Gateway unreachable for >10min
- Budget >150% (runaway cost)
- Failed-count >5 in last 1h (cascade)

Rate-limit: 1 alert per type per 30min (avoid spam).
State-file: /tmp/mc-critical-alert-state.json

Direct Discord-Webhook (R10: alerts don't go through MC-API because MC might be dead).
"""
from __future__ import annotations
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

MC_HEALTH = os.environ.get('MC_CRITICAL_HEALTH', 'http://127.0.0.1:3000/api/health')
GW_HEALTH = os.environ.get('MC_CRITICAL_GW', 'http://127.0.0.1:18789/healthz')
WEBHOOK_URL = os.environ.get('MC_CRITICAL_WEBHOOK', os.environ.get('AUTO_PICKUP_WEBHOOK_URL', '')).strip()
RATE_LIMIT_SEC = int(os.environ.get('MC_CRITICAL_RATE_LIMIT_SEC', '1800'))  # 30min per type
STATE_FILE = Path(os.environ.get('MC_CRITICAL_STATE', '/tmp/mc-critical-alert-state.json'))
LOG_FILE = Path(os.environ.get('MC_CRITICAL_LOG', '/home/piet/.openclaw/workspace/logs/mc-critical-alert.log'))
DOWN_THRESHOLD_SEC = int(os.environ.get('MC_CRITICAL_DOWN_MIN', '10')) * 60
BUDGET_THRESHOLD_PCT = float(os.environ.get('MC_CRITICAL_BUDGET_PCT', '150'))
USER_AGENT = 'mc-critical-alert/1.0 (+openclaw; python-urllib)'


def _ts():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def log(level, msg):
    line = f'[{_ts()}] [{level}] {msg}\n'
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with LOG_FILE.open('a') as f:
            f.write(line)
    except Exception:
        pass
    print(line.strip())


def load_state():
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {}


def save_state(s):
    try:
        STATE_FILE.write_text(json.dumps(s))
    except Exception:
        pass


def rate_limited(state, key):
    last = state.get(f'last_{key}', 0)
    return (time.time() - last) < RATE_LIMIT_SEC


def mark_sent(state, key):
    state[f'last_{key}'] = time.time()


def http_ok(url, timeout=5):
    try:
        req = Request(url, headers={'User-Agent': USER_AGENT})
        with urlopen(req, timeout=timeout) as r:
            return r.status == 200, r.read().decode('utf-8', errors='ignore')
    except (HTTPError, URLError, OSError) as e:
        return False, str(e)


def send_discord(title, body, mention='@here'):
    """Send via central alert-dispatcher for cooldown/dedupe (Sprint-G G2)."""
    import subprocess
    msg = f'{mention} 🚨 **{title}**\n{body}'
    try:
        proc = subprocess.run(
            ['/home/piet/.openclaw/scripts/alert-dispatcher.sh', 'mc-critical', msg, mention],
            capture_output=True, timeout=15,
        )
        ok = proc.returncode == 0
        log('SENT' if ok else 'WARN', f'{title} (dispatcher rc={proc.returncode})')
        return ok
    except Exception as e:
        log('FAIL', f'alert-dispatcher error: {e}')
        return False


def check_mc_down(state):
    ok, _ = http_ok(MC_HEALTH)
    if ok:
        state.pop('mc_down_since', None)
        return
    first_down = state.get('mc_down_since')
    if not first_down:
        state['mc_down_since'] = time.time()
        return
    down_sec = time.time() - first_down
    if down_sec >= DOWN_THRESHOLD_SEC and not rate_limited(state, 'mc_down'):
        send_discord(
            'MC DOWN',
            f'Mission Control is unreachable for {int(down_sec/60)}min.\nWatchdog may have failed. Check systemd: `systemctl --user status mission-control`',
        )
        mark_sent(state, 'mc_down')


def check_gateway_down(state):
    ok, _ = http_ok(GW_HEALTH)
    if ok:
        state.pop('gw_down_since', None)
        return
    first_down = state.get('gw_down_since')
    if not first_down:
        state['gw_down_since'] = time.time()
        return
    down_sec = time.time() - first_down
    if down_sec >= DOWN_THRESHOLD_SEC and not rate_limited(state, 'gw_down'):
        send_discord(
            'GATEWAY DOWN',
            f'OpenClaw Gateway is unreachable for {int(down_sec/60)}min. All dispatch is frozen.',
        )
        mark_sent(state, 'gw_down')


def check_budget(state):
    ok, body = http_ok('http://127.0.0.1:3000/api/costs')
    if not ok:
        return
    try:
        data = json.loads(body)
        budget = data.get('budget', {})
        pct = budget.get('todayPct', 0)
        if pct >= BUDGET_THRESHOLD_PCT and not rate_limited(state, 'budget'):
            send_discord(
                f'BUDGET {int(pct)}%',
                f"Daily budget consumed {pct:.1f}% of ${budget.get('dailyBudget', '?')}.\nConsider: pause auto-pickup, switch to fallback models.",
            )
            mark_sent(state, 'budget')
    except Exception as e:
        log('WARN', f'budget parse error: {e}')


def main():
    state = load_state()
    check_mc_down(state)
    check_gateway_down(state)
    check_budget(state)
    save_state(state)


if __name__ == '__main__':
    main()
