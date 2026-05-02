#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import urlopen

ROOT = Path('/home/piet/.openclaw')
WORKSPACE = ROOT / 'workspace'
LOGS = WORKSPACE / 'logs'
AGENTS = ['main', 'frontend-guru', 'sre-expert', 'efficiency-auditor', 'spark', 'james']
WORKER_AGENTS = ['frontend-guru', 'sre-expert', 'efficiency-auditor', 'spark', 'james']
TRENDS_URL = 'http://127.0.0.1:3000/api/trends'
MODEL_HEALTH_URL = 'http://127.0.0.1:3000/api/models/health'

SESSION_WARN_MB = 10.0
SESSION_CRIT_MB = 15.0


@dataclass
class Metric:
    name: str
    source: str
    value: Any
    unit: str | None
    threshold: str
    fallback: str
    false_positive_risk: str
    status: str


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def fetch_json(url: str) -> dict[str, Any] | list[Any] | None:
    try:
        with urlopen(url, timeout=10) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception:
        return None


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return ''


def latest_session_sizes() -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for agent in AGENTS:
        d = ROOT / 'agents' / agent / 'sessions'
        normal_max = 0
        normal_file = None
        sidecar_max = 0
        sidecar_file = None
        if d.exists():
            for p in d.glob('*.jsonl'):
                try:
                    size = p.stat().st_size
                except FileNotFoundError:
                    continue
                if '.checkpoint.' in p.name or '.trajectory.' in p.name:
                    if size > sidecar_max:
                        sidecar_max = size
                        sidecar_file = p.name
                else:
                    if size > normal_max:
                        normal_max = size
                        normal_file = p.name
        out[agent] = {
            'normal_max_bytes': normal_max,
            'normal_max_file': normal_file,
            'sidecar_max_bytes': sidecar_max,
            'sidecar_max_file': sidecar_file,
        }
    return out


def parse_ops_digest_line(text: str, prefix: str) -> str | None:
    for line in text.splitlines():
        if line.startswith(prefix):
            return line
    return None


def build_metrics() -> tuple[list[Metric], dict[str, Any]]:
    trends = fetch_json(TRENDS_URL) or {}
    model_health = fetch_json(MODEL_HEALTH_URL) or {}
    digest = read_text(LOGS / 'daily-ops-digest.log')
    guard_log = read_text(LOGS / 'session-size-guard.log')
    auto_pickup_log = read_text(LOGS / 'auto-pickup.log')
    sessions = latest_session_sizes()

    velocity_timeline = trends.get('velocityTimeline') or []
    latest_velocity = velocity_timeline[-1]['velocity'] if velocity_timeline else None
    rolling_avg = velocity_timeline[-1]['avg'] if velocity_timeline else None
    velocity_ratio = round(latest_velocity / rolling_avg, 2) if latest_velocity and rolling_avg else None

    worker_sizes = [sessions[a]['normal_max_bytes'] for a in WORKER_AGENTS if sessions.get(a)]
    max_worker_mb = round(max(worker_sizes) / (1024 * 1024), 2) if worker_sizes else None
    worker_util_pct = round((max_worker_mb / SESSION_CRIT_MB) * 100, 1) if max_worker_mb is not None else None

    model_ok = [m for m in (model_health.get('models') or []) if isinstance(m, dict) and m.get('ok')]
    latencies = [m['latency'] for m in model_ok if isinstance(m.get('latency'), (int, float))]
    p95_latency = round(statistics.quantiles(latencies, n=20)[-1], 1) if len(latencies) >= 2 else (latencies[0] if latencies else None)

    metrics: list[Metric] = [
        Metric(
            name='token_velocity',
            source='GET /api/trends.velocityTimeline',
            value={'latest': latest_velocity, 'rolling_avg': rolling_avg, 'ratio': velocity_ratio},
            unit='tasks/day',
            threshold='alert if latest > 2x rolling_avg',
            fallback='proxy from /api/trends summary if timeline missing',
            false_positive_risk='single-day spikes from backlog catch-up',
            status='ok' if velocity_ratio is None or velocity_ratio <= 2 else 'warn',
        ),
        Metric(
            name='tool_call_density',
            source='logs/session-size-guard.log + session/receipt events proxy',
            value={'recent_alert_lines': len([l for l in guard_log.splitlines() if 'ALERT ' in l][-24:])},
            unit='alerts/day proxy',
            threshold='alert if >5 tool-like events / 1K emitted tokens',
            fallback='receipt-event count proxy',
            false_positive_risk='debug/smoke runs inflate counts',
            status='proxy',
        ),
        Metric(
            name='cache_hit_rate',
            source='proxy from model health + digest cache counters (not directly exposed)',
            value='unavailable',
            unit='%',
            threshold='alert if <40%',
            fallback='mark proxy/unavailable until direct cache header capture exists',
            false_positive_risk='provider headers unavailable or 401 health responses',
            status='unavailable',
        ),
        Metric(
            name='output_input_ratio',
            source='task receipt resultSummary/progressSummary text volume',
            value='proxy-unavailable',
            unit=None,
            threshold='alert if <0.05 or >0.5',
            fallback='ratio from receipt text length if structured counts missing',
            false_positive_risk='short tasks and terse receipts skew ratio',
            status='proxy',
        ),
        Metric(
            name='time_between_tool_errors',
            source='logs/gateway + session-size-guard recent error lines',
            value={'error_lines': len([l for l in (guard_log + '\n' + auto_pickup_log).splitlines() if 'ERROR' in l or 'FAILED' in l])},
            unit='errors',
            threshold='alert if <30s between repeated tool errors',
            fallback='consecutive-failure counter',
            false_positive_risk='rate-limited smoke runs and external API failures',
            status='proxy',
        ),
        Metric(
            name='context_utilization_per_worker',
            source='agents/<worker>/sessions normal file size',
            value={'max_worker_mb': max_worker_mb, 'utilization_pct_vs_15mb': worker_util_pct},
            unit='%',
            threshold='alert if >70%',
            fallback='message-count proxy per session file',
            false_positive_risk='large but inactive session archives',
            status='warn' if worker_util_pct is not None and worker_util_pct > 70 else 'ok',
        ),
        Metric(
            name='latency_p95_drift',
            source='GET /api/models/health latency sample',
            value={'healthy_models': len(latencies), 'p95_ms': p95_latency},
            unit='ms',
            threshold='alert if +50% vs 10m baseline',
            fallback='task/API RTT proxy',
            false_positive_risk='401 responses make health data incomplete',
            status='proxy' if p95_latency is None else 'ok',
        ),
    ]

    ctx = {
        'generated_at': now_iso(),
        'approval_needed': 'APPROVAL_NEEDED: cron activation + export target approval required before scheduling',
        'schedule_proposal': '*/2 * * * * /usr/bin/python3 /home/piet/.openclaw/scripts/session-vitals-collector.py --emit json,markdown --scope workers,main',
        'export_targets': ['local-json', 'local-markdown'],
        'sources': {
            'trends': TRENDS_URL,
            'model_health': MODEL_HEALTH_URL,
            'daily_ops_digest_log': str(LOGS / 'daily-ops-digest.log'),
            'session_size_guard_log': str(LOGS / 'session-size-guard.log'),
            'auto_pickup_log': str(LOGS / 'auto-pickup.log'),
            'worker_session_dirs': [str(ROOT / 'agents' / a / 'sessions') for a in WORKER_AGENTS],
        },
        'worker_session_files': {
            a: sessions.get(a) for a in AGENTS
        },
    }
    return metrics, ctx


def render_markdown(metrics: list[Metric], ctx: dict[str, Any]) -> str:
    lines = [
        '# Session Vitals Collector (Dry-Run)',
        f"- generated_at: {ctx['generated_at']}",
        f"- {ctx['approval_needed']}",
        f"- schedule: {ctx['schedule_proposal']}",
        '',
        '| Metric | Source | Value | Threshold | Fallback | Risk | Status |',
        '|---|---|---:|---|---|---|---|',
    ]
    for m in metrics:
        value = m.value if isinstance(m.value, str) else json.dumps(m.value, ensure_ascii=False)
        lines.append(f'| {m.name} | {m.source} | `{value}` | {m.threshold} | {m.fallback} | {m.false_positive_risk} | {m.status} |')
    lines.extend([
        '',
        '## Approval Needed',
        ctx['approval_needed'],
        '',
        '## Export Targets',
        '- local JSON',
        '- local Markdown',
    ])
    return '\n'.join(lines)


def build_output() -> dict[str, Any]:
    metrics, ctx = build_metrics()
    return {
        'schema_version': 'v1',
        'mode': 'dry-run',
        'collector': 'session-vitals-collector',
        'generated_at': ctx['generated_at'],
        'approval_needed': ctx['approval_needed'],
        'schedule_proposal': ctx['schedule_proposal'],
        'export_targets': ctx['export_targets'],
        'metrics': [asdict(m) for m in metrics],
        'sources': ctx['sources'],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--emit', default='json,markdown', help='Comma-separated outputs to print')
    ap.add_argument('--out-dir', default=str(LOGS / 'session-vitals-collector'), help='Directory for written artifacts')
    args = ap.parse_args()

    out = build_output()
    md = render_markdown([Metric(**m) for m in out['metrics']], {
        'generated_at': out['generated_at'],
        'approval_needed': out['approval_needed'],
        'schedule_proposal': out['schedule_proposal'],
    })

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / 'session-vitals-collector.dry-run.json'
    md_path = out_dir / 'session-vitals-collector.dry-run.md'
    json_path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    md_path.write_text(md + '\n', encoding='utf-8')

    emit = {x.strip().lower() for x in args.emit.split(',') if x.strip()}
    if 'json' in emit:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    if 'markdown' in emit:
        print(md)
    print(f'JSON_PATH={json_path}')
    print(f'MD_PATH={md_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
