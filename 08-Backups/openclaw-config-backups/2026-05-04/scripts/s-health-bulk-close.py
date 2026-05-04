#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
from pathlib import Path

DATA_DIR = Path(os.environ.get('MISSION_CONTROL_DATA_DIR', '/home/piet/.openclaw/state/mission-control/data'))
TASKS_PATH = DATA_DIR / 'tasks.json'


def parse_iso(value: str | None):
    if not value or not isinstance(value, str):
        return None
    try:
        return dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    except Exception:
        return None


def is_nonempty(value):
    return isinstance(value, str) and value.strip() != ''


def run(execute: bool):
    data = json.loads(TASKS_PATH.read_text(encoding='utf-8'))
    tasks = data.get('tasks', [])
    now = dt.datetime.now(dt.timezone.utc)
    cutoff = now - dt.timedelta(days=7)

    a1_ids = []
    b1_ids = []

    for task in tasks:
        if task.get('status') != 'done':
            continue

        updated_at = parse_iso(task.get('updatedAt'))
        has_final_report = is_nonempty(task.get('finalReportSentAt'))
        has_blocker = is_nonempty(task.get('blockerReason'))

        if (not has_final_report) and updated_at and updated_at < cutoff:
            a1_ids.append(task.get('id'))

        if has_blocker:
            b1_ids.append(task.get('id'))

    a1_set = set(a1_ids)
    b1_set = set(b1_ids)
    overlap = sorted(a1_set & b1_set)

    print(json.dumps({
        'mode': 'execute' if execute else 'dry-run',
        'a1_count': len(a1_ids),
        'b1_count': len(b1_ids),
        'overlap_count': len(overlap),
        'unique_tasks': len(a1_set | b1_set),
        'field_mutations_expected': len(a1_ids) + len(b1_ids),
        'tasks_path': str(TASKS_PATH),
    }, ensure_ascii=False))

    if not execute:
        return 0

    mutated = 0
    for task in tasks:
        tid = task.get('id')
        if tid in a1_set:
            updated_at = task.get('updatedAt')
            if is_nonempty(updated_at) and not is_nonempty(task.get('finalReportSentAt')):
                task['finalReportSentAt'] = updated_at
                mutated += 1
        if tid in b1_set:
            if is_nonempty(task.get('blockerReason')):
                task['blockerReason'] = ''
                mutated += 1

    data['tasks'] = tasks
    TASKS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    print(json.dumps({
        'mode': 'execute',
        'field_mutations_applied': mutated,
        'field_mutations_expected': len(a1_ids) + len(b1_ids),
        'ok': mutated == (len(a1_ids) + len(b1_ids)),
    }, ensure_ascii=False))

    return 0 if mutated == (len(a1_ids) + len(b1_ids)) else 2


def main():
    parser = argparse.ArgumentParser(description='S-HEALTH T3 bulk close for A1+B1 categories')
    parser.add_argument('--execute', action='store_true', help='apply mutations (default is dry-run)')
    args = parser.parse_args()
    raise SystemExit(run(args.execute))


if __name__ == '__main__':
    main()
