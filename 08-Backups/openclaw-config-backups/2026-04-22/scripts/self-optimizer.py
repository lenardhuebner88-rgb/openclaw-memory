#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

UTC = timezone.utc
NOW = datetime.now(UTC)
WORKSPACE = Path('/home/piet/.openclaw/workspace')
LOG_PATH = WORKSPACE / 'logs' / 'self-optimizer.log'
MC_WATCHDOG_LOG = WORKSPACE / 'logs' / 'mc-watchdog.log'
AUTO_PICKUP_LOG = WORKSPACE / 'logs' / 'auto-pickup-cron.log'
COST_ALERT_LOG = WORKSPACE / 'logs' / 'cost-alert-dispatcher.log'

HEALTH_URL = 'http://127.0.0.1:3000/api/health'
ANOMALIES_URL = 'http://127.0.0.1:3000/api/costs/anomalies'
SCRIPT_HEALTH_URL = 'http://127.0.0.1:3000/api/ops/script-health'

SELF_OPT_ENABLED = os.getenv('SELF_OPT_ENABLED', '1').strip().lower() not in {'0', 'false', 'off', 'no'}
SELF_OPT_DRY_RUN = os.getenv('SELF_OPT_DRY_RUN', '1').strip().lower() not in {'0', 'false', 'off', 'no'}
SELF_OPT_SYNTHETIC = os.getenv('SELF_OPT_SYNTHETIC', '0').strip().lower() in {'1', 'true', 'on', 'yes'}

QUIET_WHEN_HEALTHY_SCRIPTS = {
    'gateway-port-guard.sh',
    'mission-control-port-guard.sh',
    'script-integrity-check.sh',
}


def iso_now() -> str:
    return datetime.now(UTC).isoformat().replace('+00:00', 'Z')


def parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(UTC)
    except ValueError:
        return None


def log(kind: str, payload: dict[str, Any]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    line = {'ts': iso_now(), 'kind': kind, **payload}
    with LOG_PATH.open('a', encoding='utf-8') as f:
        f.write(json.dumps(line, ensure_ascii=False) + '\n')


def tail_lines(path: Path, max_lines: int = 300, max_bytes: int = 128 * 1024) -> list[str]:
    if not path.exists():
        return []
    raw = path.read_text(encoding='utf-8', errors='replace')
    if len(raw) > max_bytes:
        raw = raw[-max_bytes:]
    lines = [line.strip() for line in raw.splitlines() if line.strip()]
    return lines[-max_lines:]


def fetch_json(url: str) -> tuple[Any | None, str | None]:
    req = Request(url, headers={'User-Agent': 'self-optimizer/1.0'})
    try:
        with urlopen(req, timeout=5) as resp:
            body = resp.read().decode('utf-8', errors='replace')
            return json.loads(body), None
    except HTTPError as exc:
        return None, f'HTTP {exc.code}'
    except URLError as exc:
        return None, f'URL error: {exc}'
    except json.JSONDecodeError as exc:
        return None, f'JSON decode error: {exc}'
    except Exception as exc:  # noqa: BLE001
        return None, f'Unexpected error: {exc}'


def gateway_rss_mb() -> float | None:
    try:
        out = subprocess.check_output(['ps', '-eo', 'comm,rss'], text=True, timeout=4)
    except Exception:  # noqa: BLE001
        return None
    best = 0
    for line in out.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 2:
            continue
        comm, rss = parts[0], parts[1]
        if 'openclaw-gatewa' in comm or comm == 'openclaw-gateway':
            try:
                best = max(best, int(rss))
            except ValueError:
                continue
    return (best / 1024.0) if best > 0 else None


@dataclass
class Suggestion:
    rule: str
    severity: str
    action: str
    evidence: str

    def as_dict(self) -> dict[str, str]:
        return {
            'rule': self.rule,
            'severity': self.severity,
            'action': self.action,
            'evidence': self.evidence,
        }


def health_degraded_over_30m(health: dict[str, Any] | None) -> Suggestion | None:
    if not isinstance(health, dict):
        return None
    if str(health.get('status')) == 'ok':
        return None

    lines = tail_lines(LOG_PATH)
    seen = None
    for line in reversed(lines):
        if 'rule-health-degraded-over-30m' not in line:
            continue
        try:
            seen_obj = json.loads(line)
            seen = parse_iso(str(seen_obj.get('ts')))
            break
        except Exception:
            continue

    if seen and (NOW - seen) < timedelta(minutes=30):
        return Suggestion(
            'rule-health-degraded-over-30m',
            'warn',
            'Keep observing degraded health; 30m threshold not crossed yet.',
            f'health.status={health.get("status")}, first_seen={seen.isoformat()}',
        )

    if seen is None:
        return Suggestion(
            'rule-health-degraded-over-30m',
            'warn',
            'Mark degraded health and re-check in 30 minutes before intervention.',
            f'health.status={health.get("status")}, first detection now',
        )

    return Suggestion(
        'rule-health-degraded-over-30m',
        'high',
        'Open reliability incident and schedule focused remediation run.',
        f'health.status={health.get("status")} persisted >30m',
    )


def gateway_ram_over_3gb() -> Suggestion | None:
    rss = gateway_rss_mb()
    if rss is None:
        return Suggestion(
            'rule-gateway-ram-over-3gb',
            'warn',
            'Gateway RAM signal unavailable; inspect process telemetry path.',
            'ps-based rss probe returned no gateway process',
        )
    if rss <= 3072:
        return None
    return Suggestion(
        'rule-gateway-ram-over-3gb',
        'high',
        'Suggest gateway memory containment: inspect leaks, restart window, reduce child pressure.',
        f'gateway_rss_mb={rss:.1f}',
    )


def critical_anomaly_unacked_over_1h(anomalies: Any) -> Suggestion | None:
    if not isinstance(anomalies, dict):
        return None
    items = anomalies.get('anomalies')
    if not isinstance(items, list):
        return None

    cost_lines = tail_lines(COST_ALERT_LOG)
    for item in items:
        if not isinstance(item, dict):
            continue
        severity = str(item.get('severity') or item.get('tone') or '').lower()
        if severity != 'critical':
            continue
        detected = parse_iso(str(item.get('detectedAt') or ''))
        if not detected:
            continue
        if (NOW - detected) <= timedelta(hours=1):
            continue
        kind = str(item.get('kind') or 'unknown')
        provider = str(item.get('provider') or 'unknown')
        acked = any(('ack' in line.lower() or 'resolved' in line.lower()) and kind in line and provider in line for line in cost_lines)
        if not acked:
            return Suggestion(
                'rule-critical-anomaly-unacked-over-1h',
                'high',
                'Escalate critical anomaly ownership and request explicit acknowledgement.',
                f'kind={kind}, provider={provider}, detectedAt={detected.isoformat()}',
            )
    return None


def dead_script_health(script_health: Any) -> Suggestion | None:
    if not isinstance(script_health, list):
        return Suggestion(
            'rule-dead-script-health',
            'warn',
            'Script-health endpoint unavailable; keep fallback log probes active.',
            'script-health payload unavailable',
        )

    dead: list[dict[str, Any]] = []
    for row in script_health:
        if not isinstance(row, dict):
            continue
        if str(row.get('status')) != 'dead':
            continue
        script = str(row.get('script') or '')
        error = str(row.get('error') or row.get('lastError') or '').lower()
        if script in QUIET_WHEN_HEALTHY_SCRIPTS and 'log missing' in error:
            continue
        dead.append(row)

    if not dead:
        return None
    scripts = ', '.join(str(row.get('script')) for row in dead)
    return Suggestion(
        'rule-dead-script-health',
        'high',
        'Open repair tasks for dead scripts and restore missing runtime paths.',
        f'dead_scripts={scripts}',
    )


def recoveryload_over_3(health: dict[str, Any] | None) -> Suggestion | None:
    if not isinstance(health, dict):
        return None
    metrics = health.get('metrics') if isinstance(health.get('metrics'), dict) else {}
    value = metrics.get('recoveryLoad')
    try:
        recovery = float(value)
    except Exception:
        return None
    if recovery <= 3:
        return None
    return Suggestion(
        'rule-recoveryload-over-3',
        'high',
        'Pause new work intake and clear recovery backlog first.',
        f'recoveryLoad={recovery}',
    )


def watchdog_or_pickup_failure(script_health: Any) -> Suggestion | None:
    watchdog = tail_lines(MC_WATCHDOG_LOG, max_lines=120)
    pickup = tail_lines(AUTO_PICKUP_LOG, max_lines=120)
    if any('failed' in line.lower() or 'error' in line.lower() for line in watchdog[-10:]):
        return Suggestion(
            'rule-watchdog-failure-tail',
            'medium',
            'Investigate watchdog errors and verify MC endpoint reachability.',
            f'last_watchdog_line={watchdog[-1] if watchdog else "none"}',
        )

    pickup_tail = pickup[-20:]
    failed_exec_lines = [line for line in pickup_tail if 'failed to execute' in line.lower()]
    if failed_exec_lines:
        auto_pickup_healthy = False
        if isinstance(script_health, list):
            for row in script_health:
                if not isinstance(row, dict):
                    continue
                if str(row.get('script') or '') == 'auto-pickup.py' and str(row.get('status') or '') == 'healthy':
                    auto_pickup_healthy = True
                    break

        benign_flock_noise = all(
            'flock: failed to execute /home/piet/.openclaw/scripts/auto-pickup.py' in line.lower()
            and 'no such file or directory' in line.lower()
            for line in failed_exec_lines
        )

        if auto_pickup_healthy and benign_flock_noise:
            return None

        return Suggestion(
            'rule-auto-pickup-failure-tail',
            'high',
            'Repair auto-pickup script path and rerun recovery smoke.',
            f'last_auto_pickup_line={pickup[-1] if pickup else "none"}',
        )
    return None


def _severity_rank(level: str) -> int:
    return {
        'info': 1,
        'warn': 2,
        'warning': 2,
        'medium': 3,
        'high': 4,
        'critical': 5,
    }.get(level.lower(), 0)


def _script_health_signal(script_health_err: str | None, suggestions: list[Suggestion]) -> str:
    if script_health_err:
        return f'error:{script_health_err}'
    related = [s for s in suggestions if s.rule == 'rule-dead-script-health']
    if not related:
        return 'ok'
    max_rank = max(_severity_rank(s.severity) for s in related)
    return 'high' if max_rank >= 4 else 'warn'


def main() -> int:
    if not SELF_OPT_ENABLED:
        log('self-opt-disabled', {'enabled': False, 'dryRun': SELF_OPT_DRY_RUN})
        return 0

    health, health_err = fetch_json(HEALTH_URL)
    anomalies, anomalies_err = fetch_json(ANOMALIES_URL)
    script_health, script_health_err = fetch_json(SCRIPT_HEALTH_URL)

    suggestions: list[Suggestion] = []

    if health_err:
        suggestions.append(Suggestion('signal-health-unavailable', 'warn', 'Check Mission Control availability for /api/health.', health_err))
    if anomalies_err:
        suggestions.append(Suggestion('signal-anomalies-unavailable', 'warn', 'Check /api/costs/anomalies endpoint and parser.', anomalies_err))
    if script_health_err:
        suggestions.append(Suggestion('signal-script-health-unavailable', 'warn', 'Continue with fallback heuristics until /api/ops/script-health is available.', script_health_err))

    for rule in (
        health_degraded_over_30m(health if isinstance(health, dict) else None),
        gateway_ram_over_3gb(),
        critical_anomaly_unacked_over_1h(anomalies),
        dead_script_health(script_health),
        recoveryload_over_3(health if isinstance(health, dict) else None),
        watchdog_or_pickup_failure(script_health),
    ):
        if rule is not None:
            suggestions.append(rule)

    if SELF_OPT_SYNTHETIC:
        suggestions.append(
            Suggestion(
                'synthetic-example',
                'info',
                'DRY-RUN synthetic suggestion for operator preview.',
                'forced by SELF_OPT_SYNTHETIC=1',
            )
        )

    payload = {
        'enabled': SELF_OPT_ENABLED,
        'dryRun': SELF_OPT_DRY_RUN,
        'signals': {
            'health': 'ok' if not health_err else f'error:{health_err}',
            'anomalies': 'ok' if not anomalies_err else f'error:{anomalies_err}',
            'scriptHealth': _script_health_signal(script_health_err, suggestions),
        },
        'suggestions': [s.as_dict() for s in suggestions],
    }
    log('self-opt-cycle', payload)

    # Never execute actions in v1, regardless of SELF_OPT_DRY_RUN.
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
