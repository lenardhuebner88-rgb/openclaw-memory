#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path('/home/piet/.openclaw')
WORKSPACE = ROOT / 'workspace'
LOGS = WORKSPACE / 'logs'
STATE_PATH = LOGS / 'daily-ops-digest-state.json'
AGENTS = ['main', 'frontend-guru', 'sre-expert', 'efficiency-auditor', 'spark', 'james']

ALERT_THRESHOLDS = {
    'session_mb_warn': 10,
    'session_mb_crit': 15,
    'reaper_kills_warn': 5,
    'timeouts_warn': 3,
}

DISCORD_API = 'http://127.0.0.1:3000/api/discord/send'
ATLAS_MAIN_CHANNEL = '1486480128576983070'

TS_PATTERNS = [
    re.compile(r'^(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z)'),
    re.compile(r'^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d+)?)'),
    re.compile(r'^(?P<ts>\w{3} +\d{1,2} \d{2}:\d{2}:\d{2})'),
]


def parse_ts(text: str) -> datetime | None:
    for pat in TS_PATTERNS:
        m = pat.search(text)
        if not m:
            continue
        ts = m.group('ts')
        try:
            if ts.endswith('Z'):
                return datetime.fromisoformat(ts.replace('Z', '+00:00'))
            if 'T' in ts:
                return datetime.fromisoformat(ts).replace(tzinfo=timezone.utc)
            return datetime.strptime(ts, '%b %d %H:%M:%S').replace(year=datetime.now().year, tzinfo=timezone.utc)
        except Exception:
            continue
    return None


def bytes_to_mb(n: int) -> float:
    return round(n / (1024 * 1024), 1)


def classify_session(path: Path) -> str:
    n = path.name
    return 'sidecar' if '.checkpoint.' in n or '.trajectory.' in n else 'normal'


def scan_sessions() -> dict[str, Any]:
    out: dict[str, Any] = {}
    for agent in AGENTS:
        d = ROOT / 'agents' / agent / 'sessions'
        if not d.exists():
            continue
        normal_max = sidecar_max = 0
        normal_file = sidecar_file = None
        for p in d.glob('*.jsonl'):
            try:
                size = p.stat().st_size
            except FileNotFoundError:
                continue
            if classify_session(p) == 'normal':
                if size > normal_max:
                    normal_max, normal_file = size, p.name
            else:
                if size > sidecar_max:
                    sidecar_max, sidecar_file = size, p.name
        out[agent] = {
            'normal_max_bytes': normal_max,
            'normal_max_file': normal_file,
            'sidecar_max_bytes': sidecar_max,
            'sidecar_max_file': sidecar_file,
        }
    return out


def load_state() -> dict[str, Any]:
    if not STATE_PATH.exists():
        return {}
    try:
        return json.loads(STATE_PATH.read_text(encoding='utf-8'))
    except Exception:
        return {}


def save_state(data: dict[str, Any]) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def trend_line(current: float, previous: float | None) -> str:
    if previous is None:
        return 'baseline=n/a'
    delta = round(current - previous, 1)
    sign = '+' if delta >= 0 else ''
    return f'trend={sign}{delta}MB vs prev'


def collect_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return path.read_text(encoding='utf-8', errors='replace').splitlines()


def reaper_metrics() -> dict[str, Any]:
    lines = collect_lines(LOGS / 'mcp-reaper.log')
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=24)
    peak_alive: int | None = None
    kills = 0
    parsed_any = False
    for line in lines:
        ts = parse_ts(line)
        if ts:
            parsed_any = True
            if ts < cutoff:
                continue
        elif parsed_any:
            continue
        m = re.search(r'alive=(\d+)', line)
        if m:
            val = int(m.group(1))
            peak_alive = val if peak_alive is None else max(peak_alive, val)
        if 'killed ' in line:
            kills += 1
    return {
        'peak_alive': peak_alive,
        'kills': kills,
        'window': '24h' if parsed_any else 'unknown timestamp window',
        'fallback': 'none' if parsed_any else 'all-lines',
    }


def auto_pickup_metrics() -> dict[str, Any]:
    lines = collect_lines(LOGS / 'auto-pickup.log')
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=24)
    counts = Counter()
    parsed_any = False

    for line in lines:
        ts = parse_ts(line)
        if ts:
            parsed_any = True
            if ts < cutoff:
                continue
        elif parsed_any:
            continue

        matched = []
        for key in ('claim-timeout', 'systemd-stop:mc-worker-'):
            if key in line:
                counts[key] += 1
                matched.append(key)

        m = re.search(r'agent[=: ](?P<agent>[A-Za-z0-9_-]+)', line)
        if m and matched:
            counts[f'agent:{m.group("agent")}'] += 1

    agent = 'unknown'
    top_agent_count = 0
    for k, v in counts.items():
        if k.startswith('agent:') and v > top_agent_count:
            agent = k.split(':', 1)[1]
            top_agent_count = v

    non_agent_keys = [k for k in counts if not k.startswith('agent:')]
    top_class = max(non_agent_keys, key=lambda k: counts[k], default='n/a')

    return {
        'counts': dict(counts),
        'agent': agent,
        'top_class': top_class,
        'window': '24h' if parsed_any else 'unknown timestamp window',
        'fallback': 'none' if parsed_any else 'all-lines',
    }


def level_for_session(mb: float) -> str:
    if mb >= ALERT_THRESHOLDS['session_mb_crit']:
        return 'CRIT'
    if mb >= ALERT_THRESHOLDS['session_mb_warn']:
        return 'WARN'
    return 'OK'


def send_discord(message_text: str) -> tuple[bool, str]:
    payload = json.dumps({'agentId': 'main', 'channelId': ATLAS_MAIN_CHANNEL, 'message': message_text})
    proc = subprocess.run([
        'curl', '-sS', '-X', 'POST', DISCORD_API,
        '-H', 'Content-Type: application/json',
        '-H', 'x-actor-kind: system',
        '-H', 'x-request-class: admin',
        '-d', payload,
    ], capture_output=True, text=True)
    out = (proc.stdout or proc.stderr or '').strip()
    return proc.returncode == 0 and '"ok":true' in out, out[:800]


def build_digest(sessions: dict[str, Any], prev_sessions: dict[str, Any]) -> str:
    lines = ['# Daily Ops Digest']

    for agent in AGENTS:
        s = sessions.get(agent, {})
        mb = bytes_to_mb(s.get('normal_max_bytes', 0))
        prev_mb = prev_sessions.get(agent, {}).get('normal_max_mb') if isinstance(prev_sessions.get(agent), dict) else None
        lvl = level_for_session(mb)
        lines.append(f'- {lvl} {agent}: normal max {mb}MB ({trend_line(mb, prev_mb)})')
        sidecar_b = s.get('sidecar_max_bytes', 0)
        if sidecar_b >= ALERT_THRESHOLDS['session_mb_warn'] * 1024 * 1024:
            lines.append(f'  - note: sidecar max {bytes_to_mb(sidecar_b)}MB ({s.get("sidecar_max_file")})')

    rep = reaper_metrics()
    rep_alive = rep['peak_alive'] if rep['peak_alive'] is not None else 'unknown'
    rep_lvl = 'WARN' if rep['kills'] >= ALERT_THRESHOLDS['reaper_kills_warn'] or rep_alive == 'unknown' else 'OK'
    lines.append(
        f'- {rep_lvl} reaper: peak alive={rep_alive}, kills={rep["kills"]}, '
        f'window={rep["window"]}, fallback={rep["fallback"]}'
    )

    apm = auto_pickup_metrics()
    timeout_total = apm['counts'].get('claim-timeout', 0) + apm['counts'].get('systemd-stop:mc-worker-', 0)
    ap_lvl = 'CRIT' if timeout_total >= 5 else 'WARN' if timeout_total >= ALERT_THRESHOLDS['timeouts_warn'] else 'OK'
    lines.append(
        f'- {ap_lvl} auto-pickup: timeouts={timeout_total}, agent={apm["agent"]}, class={apm["top_class"]}, '
        f'window={apm["window"]}, fallback={apm["fallback"]}'
    )

    lines.append('- Thresholds: session>=10MB warn, >=15MB crit; reaper kills>=5 warn; timeouts>=3 warn')
    lines.append('- Schedule proposal: 05 21 * * * TZ=Europe/Berlin /usr/bin/python3 /home/piet/.openclaw/scripts/daily-ops-digest.py --post')
    lines.append('- APPROVAL_NEEDED: schedule activation')
    return '\n'.join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--dry-run', action='store_true', help='Print digest only, no Discord post')
    ap.add_argument('--post', action='store_true', help='Post digest to #atlas-main via local Mission Control API')
    args = ap.parse_args()

    sessions = scan_sessions()
    prev = load_state()
    prev_sessions = prev.get('agents', {}) if isinstance(prev.get('agents', {}), dict) else {}
    digest = build_digest(sessions, prev_sessions)

    new_state = {
        'generatedAt': datetime.now(timezone.utc).isoformat(),
        'agents': {a: {'normal_max_mb': bytes_to_mb(sessions.get(a, {}).get('normal_max_bytes', 0))} for a in AGENTS},
    }
    save_state(new_state)

    if args.post:
        ok, detail = send_discord(digest)
        if not ok:
            print(f'POST_FAILED: {detail}')
            return 1
        print('POST_OK')
        return 0

    print(digest)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
