#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATA_DIR = Path(os.environ.get('MISSION_CONTROL_DATA_DIR', '/home/piet/.openclaw/state/mission-control/data'))
TASKS_PATH = DATA_DIR / 'tasks.json'
SCHEMA_PY = Path('/home/piet/.openclaw/workspace/mission-control/src/schemas/sprint_outcome.py')


@dataclass
class BackfillResult:
    selected: int
    updated: int
    schema_errors: int
    remaining_legacy: int
    backup_path: str | None


def parse_iso(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    except Exception:
        return None


def derive_duration_seconds(task: dict[str, Any]) -> float:
    start = parse_iso(task.get('startedAt')) or parse_iso(task.get('acceptedAt')) or parse_iso(task.get('createdAt'))
    end = parse_iso(task.get('completedAt')) or parse_iso(task.get('failedAt')) or parse_iso(task.get('updatedAt')) or datetime.now(timezone.utc)
    if start is None or end is None:
        return 0.0
    return max(0.0, (end - start).total_seconds())


def derive_status(task_status: str) -> str:
    if task_status == 'done':
        return 'done'
    if task_status == 'blocked':
        return 'blocked'
    if task_status in {'failed', 'canceled'}:
        return 'failed'
    return 'partial'


def derive_next_actions(task: dict[str, Any], status: str) -> list[dict[str, Any]]:
    if status != 'failed':
        return []
    priority = 'P1' if bool(task.get('maxRetriesReached')) else 'P2'
    return [{
        'id': f"{task.get('id', 'task')}-followup",
        'owner': 'atlas',
        'priority': priority,
        'due': None,
        'reason_code': 'legacy_backfill_followup',
    }]


def derive_blockers(task: dict[str, Any], status: str) -> list[dict[str, Any]]:
    reason = str(task.get('blockerReason') or task.get('failureReason') or '').strip()
    if status not in {'blocked', 'failed'} or not reason:
        return []
    severity = 'critical' if any(k in reason.lower() for k in ('critical', 'oom', 'security', 'panic')) else 'high'
    return [{
        'id': f"{task.get('id', 'task')}-blocker",
        'severity': severity,
        'evidence_ref': f"task:{task.get('id', 'unknown')}",
        'note': reason[:500],
    }]


def derive_sprint_outcome(task: dict[str, Any]) -> dict[str, Any]:
    status = derive_status(str(task.get('status') or 'partial'))
    tokens_out = 1 if str(task.get('resultSummary') or '').strip() else 0
    tokens_in = max(1, tokens_out)
    outcome = {
        'schema_version': 'v1',
        'status': status,
        'next_actions': derive_next_actions(task, status),
        'blockers': derive_blockers(task, status),
        'artifacts': [],
        'metrics': {
            'duration_s': round(derive_duration_seconds(task), 3),
            'tokens_in': tokens_in,
            'tokens_out': tokens_out,
            'cost_usd': 0.0,
        },
        'human_narrative': str(task.get('resultSummary') or '').strip() or None,
    }
    return outcome


def load_sprint_outcome_validator():
    spec = importlib.util.spec_from_file_location('sprint_outcome', SCHEMA_PY)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'Cannot load schema module: {SCHEMA_PY}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    validator = getattr(module, 'SprintOutcome', None)
    if validator is None:
        raise RuntimeError('SprintOutcome model not found in schema module')
    try:
        validator.model_rebuild(_types_namespace=module.__dict__)
    except Exception:
        pass
    return validator


def legacy_candidates(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates = [
        t for t in tasks
        if str(t.get('status') or '') in {'done', 'failed', 'blocked', 'canceled'}
        and not isinstance(t.get('sprintOutcome'), dict)
    ]
    candidates.sort(key=lambda t: (
        parse_iso(t.get('updatedAt')) or parse_iso(t.get('createdAt')) or datetime.min.replace(tzinfo=timezone.utc),
        str(t.get('id') or ''),
    ))
    return candidates


def run(tasks_path: Path, limit: int, execute: bool, backup_prefix: str) -> BackfillResult:
    original_payload = json.loads(tasks_path.read_text(encoding='utf-8'))
    payload = json.loads(json.dumps(original_payload))
    tasks = payload.get('tasks', [])
    if not isinstance(tasks, list):
        raise RuntimeError('tasks.json invalid: tasks must be array')

    validator = load_sprint_outcome_validator()
    candidates = legacy_candidates(tasks)
    selected = candidates[:limit]

    schema_errors = 0
    selected_ids = {str(t.get('id')) for t in selected}
    updated = 0
    for task in tasks:
        tid = str(task.get('id') or '')
        if tid not in selected_ids:
            continue
        outcome = derive_sprint_outcome(task)
        try:
            validator.model_validate(outcome)
        except Exception:
            schema_errors += 1
            continue
        if execute:
            task['sprintOutcome'] = outcome
            updated += 1

    backup_path = None
    if execute:
        ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
        backup_path = str(tasks_path.with_name(f"tasks.json.bak-{backup_prefix}-{ts}"))
        Path(backup_path).write_text(json.dumps(original_payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
        tasks_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')

    remaining = len(legacy_candidates(payload.get('tasks', [])))
    return BackfillResult(
        selected=len(selected),
        updated=updated if execute else 0,
        schema_errors=schema_errors,
        remaining_legacy=remaining,
        backup_path=backup_path,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description='Backfill legacy tasks with SprintOutcome v1 payloads')
    parser.add_argument('--tasks', default=str(TASKS_PATH), help='Path to tasks.json')
    parser.add_argument('--limit', type=int, default=149, help='Max legacy tasks to backfill (default 149)')
    parser.add_argument('--execute', action='store_true', help='Apply mutations (default dry-run)')
    parser.add_argument('--backup-prefix', default='pre-backfill', help='Backup file name prefix')
    args = parser.parse_args()

    result = run(Path(args.tasks), args.limit, args.execute, args.backup_prefix)
    print(json.dumps({
        'mode': 'execute' if args.execute else 'dry-run',
        'selected': result.selected,
        'updated': result.updated,
        'schema_errors': result.schema_errors,
        'remaining_legacy': result.remaining_legacy,
        'backup_path': result.backup_path,
        'rollback_command': f"cp {result.backup_path} {args.tasks}" if result.backup_path else None,
    }, indent=2, ensure_ascii=False))

    if args.execute:
        if result.schema_errors != 0:
            return 2
        if result.updated != result.selected:
            return 3
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
