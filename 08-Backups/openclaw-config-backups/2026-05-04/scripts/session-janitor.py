#!/usr/bin/env python3
"""Atlas session janitor.

Archives:
- Any .checkpoint.*.jsonl file older than 1 hour (always archive — snapshots)
- Regular .jsonl files > 70% budget AND not modified in last 30 min

Leaves alone:
- Files < 70% budget
- Recently active files (< 30 min modified)
- Anything in sessions-archive/

Covers all agent session dirs: agents/*/sessions/ -> agents/*/sessions-archive/
"""
import json
import shutil
import time
from datetime import datetime
from pathlib import Path

AGENTS_ROOT = Path("/home/piet/.openclaw/agents")
AUDIT = Path("/home/piet/bots/commander/logs/audit.jsonl")
AUDIT.parent.mkdir(parents=True, exist_ok=True)

BUDGET_BYTES = 150000 * 4
THRESHOLD_PCT = 70
IDLE_SECONDS = 30 * 60
CHECKPOINT_AGE = 60 * 60
NOW = time.time()
TS_TAG = datetime.now().strftime("%Y%m%d-%H%M%S")

total_archived = 0
total_bytes = 0
agent_stats = []

for agent_dir in AGENTS_ROOT.iterdir():
    if not agent_dir.is_dir():
        continue
    session_dir = agent_dir / "sessions"
    if not session_dir.exists():
        continue
    archive_dir = agent_dir / "sessions-archive"
    archive_dir.mkdir(parents=True, exist_ok=True)

    archived = 0
    archived_bytes = 0
    for f in session_dir.glob("*.jsonl"):
        try:
            size = f.stat().st_size
            age = NOW - f.stat().st_mtime
            is_ckpt = ".checkpoint." in f.name
            pct = size * 100 // BUDGET_BYTES
            should_archive = False
            if is_ckpt and age >= CHECKPOINT_AGE:
                should_archive = True
            elif pct >= THRESHOLD_PCT and age >= IDLE_SECONDS:
                should_archive = True
            if should_archive:
                dst = archive_dir / f"{f.name}.archived-{TS_TAG}"
                shutil.move(str(f), str(dst))
                archived += 1
                archived_bytes += size
        except FileNotFoundError:
            continue
        except Exception:
            continue

    if archived:
        total_archived += archived
        total_bytes += archived_bytes
        agent_stats.append({"agent": agent_dir.name, "files": archived, "mb": round(archived_bytes / 1024 / 1024, 2)})

if total_archived:
    audit = {
        "ts": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "action": "session-janitor-cron",
        "archived": total_archived,
        "mb_freed": round(total_bytes / 1024 / 1024, 2),
        "agents": agent_stats,
    }
    try:
        with AUDIT.open("a") as fh:
            fh.write(json.dumps(audit) + "\n")
    except Exception:
        pass
    print(f"session-janitor: archived {total_archived} files, {total_bytes/1024/1024:.1f} MB freed across {len(agent_stats)} agent(s)")
else:
    print("session-janitor: nothing to archive")
