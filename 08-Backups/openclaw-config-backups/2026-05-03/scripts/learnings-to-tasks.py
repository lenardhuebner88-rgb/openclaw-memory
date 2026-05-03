#!/usr/bin/env python3
"""
learnings-to-tasks.py
---------------------
Reads learnings.md + evening-debrief files, extracts Top-3 Actionables
via MiniMax, creates tasks on the board, and posts a link-summary to
#status-reports (Discord channel 1486480074491559966).

Run standalone:   python3 /home/piet/.openclaw/scripts/learnings-to-tasks.py
Or via cron:      daily at 06:55 (Europe/Berlin)
"""

import json
import os
import sys
import glob
import subprocess
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────────
WORKSPACE   = "/home/piet/.openclaw/workspace"
MEMORY_DIR  = os.path.join(WORKSPACE, "memory")
LEARNINGS   = os.path.join(MEMORY_DIR, "learnings.md")
TASK_API    = "http://127.0.0.1:3000/api/tasks"
CHANNEL_ID  = "1486480074491559966"          # #status-reports
DISCORD_TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")

# MiniMax (fallback — read key from workspace openclaw.json first)
def _load_openclaw_config():
    candidates = [
        "/home/piet/.openclaw/workspace/openclaw.json",
        "/home/piet/.openclaw/openclaw.json",
    ]
    best_cfg = {}
    best_has_minimax = False

    for candidate in candidates:
        try:
            with open(os.path.expanduser(candidate)) as f:
                cfg = json.load(f)
        except FileNotFoundError:
            continue
        except Exception as e:
            log(f"⚠️  Could not parse {candidate}: {e}")
            continue

        providers = cfg.get("models", {}).get("providers", {})
        has_minimax = any(
            "minimax" in pid.lower() and provider.get("apiKey")
            for pid, provider in providers.items()
        )

        if has_minimax:
            return cfg
        if not best_cfg:
            best_cfg = cfg
        best_has_minimax = best_has_minimax or has_minimax

    return best_cfg if not best_has_minimax else {}


def _load_minimax_key():
    """Load MiniMax API key from openclaw.json at models.providers.minimax.apiKey."""
    # Try workspace + main config first
    cfg = _load_openclaw_config()
    provs = cfg.get("models", {}).get("providers", {})
    for provider_id in ("minimax", "minimax-portal"):
        provider = provs.get(provider_id, {})
        key = provider.get("apiKey", "")
        if key and key != "__OPENCLAW_REDACTED__":
            return key
    for pid, prov in provs.items():
        if "minimax" in pid.lower() and prov.get("apiKey"):
            k = prov["apiKey"]
            if k and k != "__OPENCLAW_REDACTED__":
                return k
    # Fallback: read directly from main config (workspace config may be empty)
    try:
        import json as _json
        with open("/home/piet/.openclaw/openclaw.json") as _f:
            _main = _json.load(_f)
        for _pid in ("minimax", "minimax-portal"):
            _p = _main.get("models", {}).get("providers", {}).get(_pid, {})
            _k = _p.get("apiKey", "")
            if _k and _k != "__OPENCLAW_REDACTED__":
                return _k
    except Exception:
        pass
    return ""

MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY") or _load_minimax_key()
if not MINIMAX_API_KEY:
    key_file = os.path.expanduser("/home/piet/.minimax_key")
    if os.path.exists(key_file):
        with open(key_file) as f:
            MINIMAX_API_KEY = f.read().strip()
if MINIMAX_API_KEY and not os.environ.get("MINIMAX_API_KEY"):
    os.environ["MINIMAX_API_KEY"] = MINIMAX_API_KEY
MINIMAX_BASE    = "https://api.minimax.io/v1"
MODEL           = "MiniMax-M2.7-highspeed"

# Ollama (preferred — local, free, fast)
OLLAMA_BASE = os.environ.get("OLLAMA_BASE", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3.5:4b")
OLLAMA_TIMEOUT = int(os.environ.get("LEARNINGS_OLLAMA_TIMEOUT", "45"))
MINIMAX_TIMEOUT = int(os.environ.get("LEARNINGS_MINIMAX_TIMEOUT", "35"))
TASK_TIMEOUT    = int(os.environ.get("LEARNINGS_TASK_TIMEOUT", "10"))
DISCORD_TIMEOUT = int(os.environ.get("LEARNINGS_DISCORD_TIMEOUT", "10"))
MAX_INPUT_CHARS = int(os.environ.get("LEARNINGS_MAX_INPUT_CHARS", "5000"))
MAX_DEBRIEFS    = int(os.environ.get("LEARNINGS_MAX_DEBRIEFS", "4"))

# Files to scan (newest first)
DEBRIEF_PATTERN = os.path.join(MEMORY_DIR, "evening-debrief-*.md")

# ─── Helpers ───────────────────────────────────────────────────────────────────

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)


def read_file(path):
    try:
        with open(path) as f:
            return f.read()
    except Exception as e:
        log(f"⚠️  Could not read {path}: {e}")
        return ""


def glob_files(pattern):
    files = glob.glob(pattern)
    # Sort newest first
    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return files


def call_minimax(prompt: str) -> str:
    """Call MiniMax chat completion API and return the response text."""
    if not MINIMAX_API_KEY:
        raise RuntimeError("MINIMAX_API_KEY not set")

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 350,
        "temperature": 0.3,
    }

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{MINIMAX_BASE}/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {MINIMAX_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=MINIMAX_TIMEOUT) as resp:
            result = json.loads(resp.read())
            choices = result.get("choices", [])
            if choices:
                return choices[0].get("message", {}).get("content", "").strip()
            return ""
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"MiniMax HTTP {e.code}: {body}")
    except Exception as e:
        raise RuntimeError(f"MiniMax request failed: {e}")


def call_ollama(prompt: str) -> str:
    """Call Ollama local model — fast & free."""
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "num_predict": 350,
        }
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{OLLAMA_BASE}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
            result = json.loads(resp.read())
            return result.get("response", "").strip()
    except Exception as e:
        raise RuntimeError(f"Ollama request failed: {e}")


def extract_actionables(learnings_text: str, debriefs: list[str]) -> list[dict]:
    """
    Send combined learnings + debriefs to Ollama first, then MiniMax on failure.
    Returns list of dicts: {title, description, priority}
    """
    combined = "\n\n---\n\n".join(
        [f"=== LEARNINGS ===\n{learnings_text}"]
        + [f"=== EVENING DEBRIEF ===\n{d}" for d in debriefs]
    )

    prompt = f"""Analyze the following Learnings and Evening Debriefs. Extract the TOP 3 most impactful, actionable tasks for today.

Format — one task per line, use EXACTLY this format:
TASK: [HIGH/MEDIUM/LOW] | Title (max 60 chars) | Why it matters (max 100 chars)

Rules:
- Only 3 tasks maximum, only if genuinely important
- No duplicates of similar existing tasks
- Prioritize by Impact + Urgency
- If nothing substantial: write ONLY "NONE"

=== LEARNINGS + DEBRIEFS ===
{combined[:MAX_INPUT_CHARS]}

=== OUTPUT (exactly 1-3 lines, nothing else) ==="""

    response = ""
    ollama_error = None
    try:
        log(f"Calling Ollama ({OLLAMA_MODEL}) for actionable extraction...")
        response = call_ollama(prompt)
        if response and response.strip():
            log("✅ Ollama extraction successful")
    except Exception as e:
        ollama_error = e
        log(f"⚠️  Ollama failed ({e}) — falling back to MiniMax")

    if not response.strip():
        if not MINIMAX_API_KEY:
            raise RuntimeError(
                "Ollama returned no usable result and no MiniMax API key was available in "
                "MINIMAX_API_KEY or workspace/openclaw.json (models.providers.minimax.apiKey)."
            ) from ollama_error
        log("Calling MiniMax fallback for actionable extraction...")
        response = call_minimax(prompt)

    if "NONE" in response.upper() or not response.strip():
        log("No new actionables found.")
        return []

    # Parse TASK: [PRIORITY] | Title | Description
    import re
    actionables = []
    for line in response.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        match = re.match(r'TASK:\s*\[(\w+)\]\s*\|\s*(.+?)\s*\|\s*(.+)', line)
        if match:
            priority = match.group(1).lower()
            title = match.group(2).strip()[:80]
            desc = match.group(3).strip()[:200]
            actionables.append({"title": title, "description": desc, "priority": priority})
        if len(actionables) >= 3:
            break

    log(f"Parsed {len(actionables)} actionables from MiniMax response")
    return actionables[:3]


def create_task(title: str, description: str, priority: str = "medium") -> str | None:
    """POST a task to the board API. Returns task ID or None."""
    import re
    # Strip markdown and control characters that could cause API rejection
    clean_title = re.sub(r'[*_`#~>|+]', '', title).strip()[:200]
    clean_desc = re.sub(r'[*_`#~>|+]', '', (description or "")).strip()[:2000]
    payload = {
        "title": clean_title,
        "description": clean_desc,
        "status": "draft",
        "priority": priority,
        "tags": ["learnings", "lens", "automated"],
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            TASK_API,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=TASK_TIMEOUT) as resp:
            result = json.loads(resp.read())
            task_id = result.get("id") or result.get("task", {}).get("id", "")
            if not task_id:
                tasks = result.get("tasks") or []
                if tasks and isinstance(tasks, list):
                    task_id = tasks[0].get("id", "")
            log(f"✅ Task created: {task_id[:8]} — {title[:50]}")
            return task_id
    except Exception as e:
        log(f"❌ Failed to create task '{title[:40]}': {e}")
        return None


def discord_announce(text: str) -> bool:
    """Post a message to #status-reports via Discord API."""
    if not DISCORD_TOKEN:
        log("⚠️  DISCORD_BOT_TOKEN not set, skipping Discord notification.")
        return False

    payload = {"content": text}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages",
        data=data,
        headers={
            "Authorization": f"Bot {DISCORD_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        check_req = urllib.request.Request(
            f"https://discord.com/api/v10/channels/{CHANNEL_ID}",
            headers={"Authorization": f"Bot {DISCORD_TOKEN}"},
            method="GET",
        )
        with urllib.request.urlopen(check_req, timeout=DISCORD_TIMEOUT):
            pass

        with urllib.request.urlopen(req, timeout=DISCORD_TIMEOUT) as resp:
            log(f"📤 Posted to #status-reports")
            return True
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:500]
        if e.code == 403:
            log(
                "⚠️  Discord post skipped (HTTP 403 Forbidden). "
                f"Channel={CHANNEL_ID}, token_present={bool(DISCORD_TOKEN)}, response={body or 'empty'}. "
                "Check guild allowlist plus bot permissions for View Channel and Send Messages."
            )
            return True
        log(f"⚠️  Discord post skipped (HTTP {e.code}): {body or 'empty'}")
        return False
    except Exception as e:
        log(f"⚠️  Discord post skipped: {e} (channel={CHANNEL_ID}, token_present={bool(DISCORD_TOKEN)})")
        return False


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    log("🚀 Learnings → Tasks Pipeline started")

    # 1. Read learnings.md
    learnings_text = read_file(LEARNINGS)
    if not learnings_text:
        log("⚠️  No learnings.md found, exiting.")
        sys.exit(0)

    # 2. Read latest evening-debriefs
    debrief_files = glob_files(DEBRIEF_PATTERN)[:MAX_DEBRIEFS]
    debriefs = [read_file(p) for p in debrief_files]
    debriefs = [d for d in debriefs if d]
    log(f"📖 Read {len(debriefs)} evening-debrief(s), {len(learnings_text)} chars of learnings")

    # 3. Extract Top-3 Actionables
    actionables = extract_actionables(learnings_text, debriefs)

    if not actionables:
        discord_announce(
            "**📋 Learnings Review** — "
            f"`{datetime.now().strftime('%Y-%m-%d')}`\n"
            "Keine neuen actionables diese Woche. ✅"
        )
        log("🏁 Done (no actionables).")
        return

    # 4. Create tasks on board
    created = []
    for a in actionables:
        task_id = create_task(
            title=a.get("title", "Untitled"),
            description=a.get("description", ""),
            priority=a.get("priority", "medium"),
        )
        if task_id:
            created.append((task_id, a.get("title", "")))

    # 5. Post to #status-reports
    if created:
        lines = [
            f"**📋 Learnings → Tasks** — `{datetime.now().strftime('%Y-%m-%d')}`",
            f"Extracted **{len(created)}** actionable(s) from learnings + evening debriefs:",
            ""
        ]
        for tid, title in created:
            lines.append(f"• [{title[:70]}](http://127.0.0.1:3000/tasks/{tid})")

        discord_announce("\n".join(lines))

    log(f"🏁 Done. Created {len(created)} task(s).")


if __name__ == "__main__":
    main()
