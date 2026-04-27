# Worker Memory Tool MVP — Safe Filesystem Contract
**Task:** `5b41d689-79e9-4597-ac61-e22c602f3f9a`  
**Agent:** James  
**Date:** 2026-04-27  
**Owner:** James (research + spec) → Forge (lifecycle integration)  
**Status:** MVP Spec — implementation-ready

---

## 1 — Problem Statement

Worker sessions die on rotation. A fresh session after rotation has zero context about what the previous worker was doing. This is unsafe for multi-step tasks. The fix is a per-worker memory filesystem that survives rotation.

**Context from `context-management-longterm-fix-2026-04-27.md`:**
- Worker rotation is currently **disabled** (alerts only)
- 7+ worker sessions exceed ROTATION-Threshold (>1126 KB)
- No worker memory persistence exists
- Anthropic's `memory_20250818` GA tool pattern is the reference

---

## 2 — Memory File Schema

### 2.1 — `progress.md` — Session State Summary

**Path:** `/home/piet/.openclaw/agents/<worker>/memory/progress.md`  
**Purpose:** One-paragraph state of current task, readable in <30s by fresh worker.  
**Size cap:** 8 KB  
**TTL:** 48h (rotated workers; actively running workers overwrite on each significant event)

```markdown
# Worker Memory — <worker> — <ISO timestamp>
task_id: <task-id>
task_title: <title>
status: in-progress | stalled | waiting
last_activity: <ISO timestamp>
open_tool_calls:
  - tool: <name>
    purpose: <one-line why>
    status: done | pending
next_step: <concrete next action, max 2 sentences>
blockers: <known blockers or empty>
resume_hint: <how to resume if killed — e.g. "check open-tasks.jsonl for remaining items">
```

### 2.2 — `open-tasks.jsonl` — Structured Task Queue

**Path:** `/home/piet/.openclaw/agents/<worker>/memory/open-tasks.jsonl`  
**Purpose:** Machine-readable queue of remaining subtasks. One JSON object per line.  
**Size cap:** 32 KB  
**TTL:** 72h

```jsonl
{"id":"<subtask-id>","label":"short label","status":"pending|done","created":"<ISO>","updated":"<ISO>"}
{"id":"<subtask-id>","label":"short label","status":"pending|done","created":"<ISO>","updated":"<ISO>"}
```

**Schema rules:**
- `id`: non-empty string, max 64 chars
- `label`: non-empty string, max 256 chars
- `status`: enum `pending` | `done`
- No nested objects
- No append during read — write is always full-file replace

### 2.3 — `architecture.md` — Decisions Log

**Path:** `/home/piet/.openclaw/agents/<worker>/memory/architecture.md`  
**Purpose:** Key decisions made during this task (what was tried, what worked, what was rejected)  
**Size cap:** 16 KB  
**TTL:** 168h (7 days)

```markdown
# Architecture Decisions — <worker> — <task-id>

## Decision 1 — <title>
Date: <ISO>
Context: <why this was needed>
Decision: <what was decided>
Alternatives considered: <brief note on what else was weighed>
```

---

## 3 — Safety Guardrails

### 3.1 — Path Traversal Prevention

```python
from pathlib import Path
import re

ALLOWED_PATH_PREFIX = Path("/home/piet/.openclaw/agents")
MEMORY_DIR_NAME = "memory"
FILENAME_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]+\.(md|jsonl)$")

def safe_memory_path(worker: str, filename: str) -> Path:
    # Reject any path that would escape the memory directory
    resolved = (ALLOWED_PATH_PREFIX / worker / MEMORY_DIR_NAME / filename).resolve()
    if not str(resolved).startswith(str(ALLOWED_PATH_PREFIX / worker / MEMORY_DIR_NAME)):
        raise ValueError(f"Path traversal attempt blocked: {filename}")
    if not FILENAME_PATTERN.match(filename):
        raise ValueError(f"Invalid filename: {filename}")
    return resolved
```

**Rule:** No `..` in any path component. No absolute paths. No paths outside `$OPENCLAW_AGENTS_ROOT/agents/<worker>/memory/`.

### 3.2 — Filesize Caps

| File | Cap | Action when exceeded |
|---|---|---|
| `progress.md` | 8 KB | Truncate oldest entries, keep last 3 |
| `open-tasks.jsonl` | 32 KB | Remove `done` tasks older than 24h, then oldest pending if still over cap |
| `architecture.md` | 16 KB | Truncate oldest decision blocks |

### 3.3 — TTL Cleanup

```bash
# Cron: every 6h
find /home/piet/.openclaw/agents/*/memory/ -type f \( -name "progress.md" -mmin +2880 \) -delete   # 48h
find /home/piet/.openclaw/agents/*/memory/ -type f \( -name "open-tasks.jsonl" -mmin +4320 \) -delete  # 72h
find /home/piet/.openclaw/agents/*/memory/ -type f \( -name "architecture.md" -mmin +10080 \) -delete  # 168h
```

### 3.4 — Write Permission Rules

- Workers write ONLY to their own memory directory: `/home/piet/.openclaw/agents/<worker>/memory/`
- No writes to other workers' memory dirs
- Memory directory created on first write if absent
- File perms: `0600` (owner read/write only)

---

## 4 — Read/Write/Resume Flow

### 4.1 — On Rotation or Fresh Start

```
1. Worker starts
2. Check: does /home/piet/.openclaw/agents/<worker>/memory/ exist?
3. If YES:
   a. Read progress.md → restore task context
   b. Read open-tasks.jsonl → restore task queue
   c. Read architecture.md → restore decisions
   d. Validate all files against size caps
   e. If any file exceeds cap → truncate to cap
4. If NO:
   a. Create directory with 0700 perms
   b. Write empty progress.md with current timestamp
   c. Create empty open-tasks.jsonl
```

### 4.2 — On Significant Event (tool call, blocker, decision)

```
1. Append to progress.md (one paragraph update) — full file rewrite to enforce size cap
2. If subtask completes → update open-tasks.jsonl (full file rewrite)
3. If architectural decision made → append to architecture.md
4. All writes are full-file replace, never append-only
```

### 4.3 — On Task Completion

```
1. Write final progress.md with status=done
2. Run TTL cleanup immediately
3. Do NOT delete memory dir — kept for 48h/72h/168h respectively for post-mortem
```

---

## 5 — Integration with Worker Rotation

### 5.1 — Rotation Trigger (R51 pattern from context-management doc)

When `session.tokens > 60% of worker_budget_cap`:
1. Current worker writes final `progress.md` with `status=stalled` or `status=done`
2. Parent spawns fresh sub-agent with:
   - `progress.md` as bootstrap context
   - `open-tasks.jsonl` as task queue
   - `architecture.md` for context
3. Fresh worker resumes from files

### 5.2 — Forge Integration Points

Forge owns the lifecycle integration. James specifies the contract; Forge implements:

| Integration Point | James Contract | Forge Action |
|---|---|---|
| `memory.write_progress(worker, content)` | Called on significant events | Full file replace, size cap enforced |
| `memory.read_progress(worker)` | Returns parsed progress.md | Returns null if file absent |
| `memory.write_task_queue(worker, tasks)` | Full file replace | JSONL schema validated before write |
| `memory.read_task_queue(worker)` | Returns list of task objects | Returns empty list if file absent |
| `memory.cleanup(worker)` | TTL enforcement | Deletes expired files per schedule |
| `memory.rotate(worker)` | Called on rotation trigger | Writes final progress, parent reads |

---

## 6 — What's NOT in Scope (Anti-Scope)

- No vector DB / RAG embeddings
- No LTM writes by workers (no agent generating permanent knowledge)
- No cross-worker memory access
- No SQLite/chroma (filesystem only for MVP)
- No private data — memory dirs are `0700` and excluded from any vault sync

---

## 7 — Open Issues

1. **Tool name conflict:** If OpenClaw already has a `memory_*` tool namespace, the filesystem adapter should be named `worker-memory` to avoid collision.
2. **Rotation trigger integration:** Who calls `memory.rotate()`? Worker itself or parent spawner? Needs Forge decision.
3. **Memory dir auto-creation:** Currently specified as first-write. May need explicit init on agent startup.

---

## 8 — Verification

```bash
# Path traversal test
python3 -c "
from pathlib import Path
# This must raise:
try:
    safe_memory_path('james', '../../etc/passwd')
    print('FAIL: path traversal not blocked')
except ValueError as e:
    print('PASS:', e)

# Valid path test
p = safe_memory_path('james', 'progress.md')
print('PASS: valid path =', p)
"

# Size cap test
dd if=/dev/zero of=/tmp/10k.txt bs=1024 count=10
# progress.md cap is 8K — file > 8K should be truncated
```

---

*Spec by James (agent), 2026-04-27. Implementation: Forge owns lifecycle integration.*
