#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API_BASE = os.environ.get('COSTS_ALERTS_API', 'http://127.0.0.1:3000')
ANOMALIES_URL = f"{API_BASE}/api/costs/anomalies"
LOG_FILE = Path(os.environ.get('COSTS_ALERTS_LOG', '/home/piet/.openclaw/workspace/logs/cost-alert-dispatcher.log'))
STATE_FILE = Path(os.environ.get('COSTS_ALERTS_STATE', '/tmp/mc-costs-alert-state.json'))
RATE_LIMIT_SECONDS = int(os.environ.get('COSTS_ALERTS_RATE_LIMIT_SEC', '21600'))  # default 6h to avoid repeated false-alarm bursts
ENABLED = os.environ.get('COSTS_ALERTS_ENABLED', '1') == '1'
WEBHOOK_URL = os.environ.get('COSTS_ALERT_WEBHOOK_URL', os.environ.get('AUTO_PICKUP_WEBHOOK_URL', '')).strip()
DISCORD_CHANNEL_ID = os.environ.get('COSTS_ALERT_DISCORD_CHANNEL_ID', os.environ.get('AUTO_PICKUP_ALERT_CH', '1491148986109661334'))
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN', '').strip()
USER_AGENT = 'mc-cost-alert-dispatcher/1.0 (+openclaw; python-urllib)'


def _ts() -> str:
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def log(level: str, msg: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open('a', encoding='utf-8') as f:
        f.write(f"{_ts()} {level} {msg}\n")


def load_state() -> dict[str, float]:
    if not STATE_FILE.exists():
        return {}
    try:
        data = json.loads(STATE_FILE.read_text(encoding='utf-8'))
        if isinstance(data, dict):
            out: dict[str, float] = {}
            for k, v in data.items():
                try:
                    out[str(k)] = float(v)
                except Exception:
                    continue
            return out
    except Exception:
        pass
    return {}


def save_state(state: dict[str, float]) -> None:
    STATE_FILE.write_text(json.dumps(state), encoding='utf-8')


def fetch_anomalies() -> list[dict[str, Any]]:
    req = Request(
        ANOMALIES_URL,
        headers={
            'x-actor-kind': 'system',
            'x-request-class': 'read',
            'User-Agent': USER_AGENT,
        },
    )
    with urlopen(req, timeout=15) as resp:
        payload = json.loads(resp.read().decode('utf-8'))
    anomalies = payload.get('anomalies', []) if isinstance(payload, dict) else []
    return [a for a in anomalies if isinstance(a, dict)]


def format_alert(anomaly: dict[str, Any]) -> str:
    kind = str(anomaly.get('kind', 'unknown'))
    provider = str(anomaly.get('provider', 'unknown'))
    metric = str(anomaly.get('metric', 'metric'))
    actual = anomaly.get('actual', 0)
    threshold = anomaly.get('threshold', 0)
    recommended = str(anomaly.get('recommended', 'review required'))
    return f":rotating_light: **cost-alert {kind}** — {provider} {metric}: {actual} ({threshold}), action: {recommended}"


def post_discord(content: str) -> tuple[bool, str]:
    if WEBHOOK_URL:
        payload = json.dumps({'content': content, 'username': 'MC Cost Alerts'}).encode('utf-8')
        req = Request(
            WEBHOOK_URL,
            data=payload,
            method='POST',
            headers={
                'Content-Type': 'application/json',
                'User-Agent': USER_AGENT,
            },
        )
        try:
            with urlopen(req, timeout=15) as resp:
                status = getattr(resp, 'status', 200)
                resp.read()
            if status in (200, 204):
                return True, f'webhook:{status}'
            return False, f'webhook-unexpected:{status}'
        except HTTPError as e:
            return False, f'webhook-http:{e.code}'
        except URLError as e:
            return False, f'webhook-url:{e}'
        except Exception as e:
            return False, f'webhook-error:{e}'

    if DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID:
        payload = json.dumps({'content': content}).encode('utf-8')
        req = Request(
            f'https://discord.com/api/v10/channels/{DISCORD_CHANNEL_ID}/messages',
            data=payload,
            method='POST',
            headers={
                'Authorization': f'Bot {DISCORD_BOT_TOKEN}',
                'Content-Type': 'application/json',
                'User-Agent': USER_AGENT,
            },
        )
        try:
            with urlopen(req, timeout=15) as resp:
                status = getattr(resp, 'status', 200)
                body = resp.read().decode('utf-8', errors='ignore')
            if status in (200, 201):
                message_id = ''
                try:
                    parsed = json.loads(body)
                    message_id = str(parsed.get('id', ''))
                except Exception:
                    pass
                return True, f'bot:{status}:{message_id}'
            return False, f'bot-unexpected:{status}'
        except HTTPError as e:
            return False, f'bot-http:{e.code}'
        except URLError as e:
            return False, f'bot-url:{e}'
        except Exception as e:
            return False, f'bot-error:{e}'

    return False, 'no-discord-destination-configured'


def should_send(kind: str, state: dict[str, float], now: float, force: bool) -> bool:
    if force:
        return True
    last = state.get(kind, 0)
    return (now - last) >= RATE_LIMIT_SECONDS


def run_dispatch(force_smoke: bool = False) -> int:
    if not ENABLED and not force_smoke:
        log('DISABLED', 'COSTS_ALERTS_ENABLED=0')
        return 0

    if force_smoke:
        anomalies = [{
            'kind': 'smoke-test',
            'provider': 'minimax',
            'metric': 'pool_depletion_eur',
            'actual': 72.46,
            'threshold': 40,
            'recommended': 'verify dispatcher routing and operator ack',
        }]
    else:
        try:
            anomalies = fetch_anomalies()
        except Exception as e:
            log('FETCH_FAIL', str(e))
            return 1

    state = load_state()
    now = time.time()
    sent = 0
    suppressed = 0
    failures = 0

    for anomaly in anomalies:
        kind = str(anomaly.get('kind', 'unknown'))
        if not should_send(kind, state, now, force_smoke):
            suppressed += 1
            log('SUPPRESS', f'kind={kind} reason=rate_limit')
            continue

        content = format_alert(anomaly)
        ok, detail = post_discord(content)
        if ok:
            state[kind] = now
            sent += 1
            log('ALERT_SENT', f'kind={kind} detail={detail}')
        else:
            failures += 1
            log('ALERT_FAIL', f'kind={kind} detail={detail}')

    save_state(state)
    log('SUMMARY', f'anomalies={len(anomalies)} sent={sent} suppressed={suppressed} failures={failures} force_smoke={int(force_smoke)}')
    return 0 if failures == 0 else 2


def main() -> int:
    parser = argparse.ArgumentParser(description='Dispatch cost anomaly alerts to Discord')
    parser.add_argument('--smoke-test', action='store_true', help='Send one forced smoke alert')
    args = parser.parse_args()
    return run_dispatch(force_smoke=args.smoke_test)


if __name__ == '__main__':
    raise SystemExit(main())
