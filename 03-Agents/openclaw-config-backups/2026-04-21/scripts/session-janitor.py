#!/usr/bin/env python3
"""Atlas session janitor.

Archives:
- Any .checkpoint.*.jsonl file older than 1 hour (always archive — snapshots)
- Regular .jsonl files > 70% budget AND not modified in last 30 min

Leaves alone:
- Files < 70% budget
- Recently active files (< 30 min modified)
- Anything in sessions-archive/
"""
import json
import shutil
import time
from datetime import datetime
from pathlib import Path

SESSION_DIR = Path("/home/piet/.openclaw/agents/main/sessions")
ARCHIVE = Path("/home/piet/.openclaw/agents/main/sessions-archive")
ARCHIVE.mkdir(parents=True, exist_ok=True)
AUDIT = Path("/home/piet/bots/commander/logs/audit.jsonl")

BUDGET_BYTES = 150000 * 4
THRESHOLD_PCT = 70
IDLE_SECONDS = 30 * 60
CHECKPOINT_AGE = 60 * 60
NOW = time.time()
TS_TAG = datetime.now().strftime("%Y%m%d-%H%M%S")

archived = 0
archived_bytes = 0
for f in SESSION_DIR.glob("*.jsonl"):
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
            dst = ARCHIVE / f"{f.name}.archived-{TS_TAG}"
            shutil.move(str(f), str(dst))
            archived += 1
            archived_bytes += size
    except FileNotFoundError:
        continue
    except Exception:
        continue

if archived:
    audit = {
        "ts": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "action": "session-janitor-cron",
        "archived": archived,
        "mb_freed": round(archived_bytes / 1024 / 1024, 2),
    }
    try:
        with AUDIT.open("a") as fh:
            fh.write(json.dumps(audit) + "\n")
    except Exception:
        pass
    print(f"session-janitor: archived {archived} files, {archived_bytes/1024/1024:.1f} MB freed")
