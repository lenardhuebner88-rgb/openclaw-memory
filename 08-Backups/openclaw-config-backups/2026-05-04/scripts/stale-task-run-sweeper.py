#!/usr/bin/env python3
import argparse
import json
import sqlite3
import time
from pathlib import Path


DEFAULT_DB = Path("/home/piet/.openclaw/tasks/runs.sqlite")
DEFAULT_MAX_AGE_HOURS = 24
DEFAULT_CLEANUP_DAYS = 7


def parse_args():
    parser = argparse.ArgumentParser(description="Mark stale durable OpenClaw CLI task-runs as lost.")
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--max-age-hours", type=float, default=DEFAULT_MAX_AGE_HOURS)
    parser.add_argument("--apply", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    now_ms = int(time.time() * 1000)
    cutoff_ms = now_ms - int(args.max_age_hours * 60 * 60 * 1000)
    cleanup_after = now_ms + DEFAULT_CLEANUP_DAYS * 24 * 60 * 60 * 1000
    db_path = Path(args.db)
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        """
        select task_id, runtime, run_id, owner_key, child_session_key, last_event_at, started_at, created_at
        from task_runs
        where status = 'running'
          and runtime = 'cli'
          and coalesce(last_event_at, started_at, created_at) < ?
        order by coalesce(last_event_at, started_at, created_at) asc
        """,
        (cutoff_ms,),
    ).fetchall()
    ids = [row["task_id"] for row in rows]
    if args.apply and ids:
        error = (
            "Auto-normalized by stale-task-run-sweeper: durable CLI task-run was still "
            f"running after >{args.max_age_hours:g}h with no live worker process; marked lost "
            "to unblock gateway restart deferral."
        )
        con.executemany(
            """
            update task_runs
            set status = 'lost',
                ended_at = ?,
                last_event_at = ?,
                cleanup_after = coalesce(cleanup_after, ?),
                error = coalesce(error, ?)
            where task_id = ?
            """,
            [(now_ms, now_ms, cleanup_after, error, task_id) for task_id in ids],
        )
        con.commit()
    print(json.dumps({
        "db": str(db_path),
        "apply": args.apply,
        "maxAgeHours": args.max_age_hours,
        "matched": len(ids),
        "taskIds": ids,
    }, indent=2))


if __name__ == "__main__":
    main()
