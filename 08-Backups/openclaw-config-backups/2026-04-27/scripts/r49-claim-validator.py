#!/usr/bin/env python3
"""
R49 Claim-Validator — parses agent session-jsonl files, extracts claimed
commit-SHAs / session-IDs / task-IDs / done-claims from assistant-role text,
validates each against Disk (git log, filesystem, curl /api/tasks), and posts
Discord-Alert on mismatch.

Deployment:
  chmod +x /home/piet/.openclaw/scripts/r49-claim-validator.py
  Cron: */15 * * * * /home/piet/.openclaw/scripts/r49-claim-validator.py >> /tmp/r49-validator.log 2>&1

Motivation:
  Live-Case 2026-04-19 19:42-20:03 UTC — Atlas Session d27407ee halluzinierte
  2x Commit-SHAs + 4x Session-IDs. Entlarvung dauerte 2h manuell.
  Mit diesem Cron: automatic catch innerhalb 15 min, Discord-Alert + Log.

Alert-Thresholds:
  - commit-SHA claim ohne git-hit → CRITICAL
  - session-ID claim ohne filesystem-hit → CRITICAL
  - task-ID claim ohne curl-200 → WARNING (task may be canceled legit)
  - "done ✅" claim while Board-status != done → WARNING (R45-drift)
"""

import json
import re
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime, timezone, timedelta
import os
import sys

# Config
AGENTS_ROOT = Path("/home/piet/.openclaw/agents")
GIT_REPO = "/home/piet/.openclaw/workspace/mission-control"
MC_API = "http://localhost:3000/api/tasks"
LOG_FILE = Path("/home/piet/.openclaw/workspace/memory/r49-validator.log")
STATE_FILE = Path("/tmp/r49-validator.state.json")  # cache validated claims
DISCORD_WEBHOOK = None  # loaded from openclaw.json
LOOKBACK_MINUTES = 20  # parse only messages from last N minutes

# Patterns
RE_COMMIT_SHA = re.compile(r'\bcommit\s+([a-f0-9]{7,40})\b', re.IGNORECASE)
RE_COMMIT_SHA_BARE = re.compile(r'\b([a-f0-9]{7,12})\b')  # bare SHA (risky, more false positives)
RE_SESSION_ID = re.compile(r'\bsession[- ]?(?:id|key|:)\s*["\']?([a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12})', re.IGNORECASE)
RE_SESSION_ID_SHORT = re.compile(r'\bsubagent:\s*([a-f0-9]{8})\b', re.IGNORECASE)
RE_TASK_ID = re.compile(r'\b([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})\b')
RE_DONE_CLAIM = re.compile(r'(?:J|E|F|G|H|K|I)\d+\s+(?:ist\s+)?(?:fertig|done|abgeschlossen)\s*(?:✅|✓|OK)', re.IGNORECASE)

def load_discord_webhook():
    global DISCORD_WEBHOOK
    try:
        with open("/home/piet/.openclaw/openclaw.json") as f:
            cfg = json.load(f)
        DISCORD_WEBHOOK = cfg.get("discord", {}).get("webhookUrl") or cfg.get("discordWebhookUrl") or None
    except Exception:
        pass

def load_state():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"validated_shas": {}, "validated_sessions": {}, "validated_tasks": {}, "alerts_sent": []}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state))

def verify_commit_sha(sha, cache):
    if sha in cache:
        return cache[sha]
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H", sha],
            cwd=GIT_REPO,
            capture_output=True,
            timeout=5,
            text=True,
        )
        ok = result.returncode == 0 and len(result.stdout.strip()) > 0
        cache[sha] = ok
        return ok
    except Exception:
        return False

def verify_session_id(session_id, agent_name, cache):
    key = f"{agent_name}:{session_id}"
    if key in cache:
        return cache[key]
    # Try full UUID or short prefix
    search_patterns = [session_id, session_id[:8]]
    for agent_dir in AGENTS_ROOT.iterdir():
        if not agent_dir.is_dir():
            continue
        sessions_dir = agent_dir / "sessions"
        if not sessions_dir.is_dir():
            continue
        for f in sessions_dir.glob("*.jsonl"):
            for pat in search_patterns:
                if pat in f.name:
                    cache[key] = True
                    return True
    cache[key] = False
    return False

def verify_task_id(task_id, cache):
    if task_id in cache:
        return cache[task_id]
    try:
        req = urllib.request.Request(f"{MC_API}/{task_id}", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                body = json.loads(resp.read())
                status = body.get("task", {}).get("status") or body.get("status")
                cache[task_id] = {"exists": True, "status": status}
                return cache[task_id]
    except urllib.error.HTTPError as e:
        if e.code == 404:
            cache[task_id] = {"exists": False, "status": None}
            return cache[task_id]
    except Exception:
        pass
    cache[task_id] = {"exists": False, "status": None}
    return cache[task_id]

def parse_session_claims(session_file, lookback_mins):
    """Parse one session file and extract claims from assistant messages within lookback window."""
    claims = []
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=lookback_mins)
    try:
        with open(session_file, "rb") as f:
            f.seek(max(0, os.path.getsize(session_file) - 500_000))  # tail last ~500KB
            data = f.read().decode("utf-8", errors="replace")
        for line in data.splitlines():
            if not line.strip():
                continue
            try:
                d = json.loads(line)
            except Exception:
                continue
            msg = d.get("message", {})
            if msg.get("role") != "assistant":
                continue
            ts = d.get("timestamp", "")
            try:
                msg_time = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                if msg_time < cutoff:
                    continue
            except Exception:
                pass
            content = msg.get("content")
            texts = []
            if isinstance(content, str):
                texts.append(content)
            elif isinstance(content, list):
                for b in content:
                    if isinstance(b, dict) and b.get("type") == "text":
                        texts.append(b.get("text", ""))
            for t in texts:
                for m in RE_COMMIT_SHA.finditer(t):
                    claims.append(("commit", m.group(1), ts))
                for m in RE_SESSION_ID.finditer(t):
                    claims.append(("session", m.group(1), ts))
                for m in RE_SESSION_ID_SHORT.finditer(t):
                    claims.append(("session_short", m.group(1), ts))
                for m in RE_TASK_ID.finditer(t):
                    claims.append(("task", m.group(1), ts))
                for m in RE_DONE_CLAIM.finditer(t):
                    claims.append(("done", m.group(0), ts))
    except Exception as e:
        print(f"Error parsing {session_file}: {e}", file=sys.stderr)
    return claims

def post_discord(message):
    if not DISCORD_WEBHOOK:
        return
    try:
        payload = json.dumps({"content": message}).encode()
        req = urllib.request.Request(
            DISCORD_WEBHOOK,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        urllib.request.urlopen(req, timeout=5)
    except Exception as e:
        print(f"Discord post failed: {e}", file=sys.stderr)

def log(msg):
    ts = datetime.now(timezone.utc).isoformat()
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(f"[{ts}] {msg}")

def main():
    load_discord_webhook()
    state = load_state()
    sha_cache = state.setdefault("validated_shas", {})
    session_cache = state.setdefault("validated_sessions", {})
    task_cache = state.setdefault("validated_tasks", {})
    alerts_sent = state.setdefault("alerts_sent", [])

    violations = []
    total_claims = 0

    for agent_dir in AGENTS_ROOT.iterdir():
        if not agent_dir.is_dir():
            continue
        sessions_dir = agent_dir / "sessions"
        if not sessions_dir.is_dir():
            continue
        # Only check 2 most recent sessions per agent
        sessions = sorted(sessions_dir.glob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True)[:2]
        for sess in sessions:
            # Skip sessions not touched in lookback window
            mtime = datetime.fromtimestamp(sess.stat().st_mtime, tz=timezone.utc)
            if mtime < datetime.now(timezone.utc) - timedelta(minutes=LOOKBACK_MINUTES):
                continue
            claims = parse_session_claims(sess, LOOKBACK_MINUTES)
            total_claims += len(claims)
            for kind, value, ts in claims:
                fingerprint = f"{sess.name}:{kind}:{value}:{ts}"
                if fingerprint in alerts_sent:
                    continue
                if kind == "commit":
                    if not verify_commit_sha(value, sha_cache):
                        violations.append({
                            "kind": "commit_not_in_git",
                            "severity": "CRITICAL",
                            "agent": agent_dir.name,
                            "session": sess.name,
                            "value": value,
                            "ts": ts,
                        })
                        alerts_sent.append(fingerprint)
                elif kind in ("session", "session_short"):
                    if not verify_session_id(value, agent_dir.name, session_cache):
                        violations.append({
                            "kind": "session_not_in_fs",
                            "severity": "CRITICAL",
                            "agent": agent_dir.name,
                            "session": sess.name,
                            "value": value,
                            "ts": ts,
                        })
                        alerts_sent.append(fingerprint)
                elif kind == "task":
                    result = verify_task_id(value, task_cache)
                    if isinstance(result, dict) and not result.get("exists"):
                        violations.append({
                            "kind": "task_not_found",
                            "severity": "WARNING",
                            "agent": agent_dir.name,
                            "session": sess.name,
                            "value": value,
                            "ts": ts,
                        })
                        alerts_sent.append(fingerprint)
                # done-claims are logged but not alerted (too noisy without cross-ref)

    # Prune alerts_sent older than 24h (simple: keep last 500)
    if len(alerts_sent) > 500:
        state["alerts_sent"] = alerts_sent[-500:]

    save_state(state)

    # Report
    if violations:
        critical = [v for v in violations if v["severity"] == "CRITICAL"]
        warning = [v for v in violations if v["severity"] == "WARNING"]
        msg_lines = [f"🚨 **R49 Claim-Validator** — {len(critical)} CRITICAL, {len(warning)} WARNING (checked {total_claims} claims)"]
        for v in violations[:10]:  # cap output
            msg_lines.append(f"  [{v['severity']}] {v['kind']}: `{v['value']}` in {v['agent']}/{v['session'][:12]} @ {v['ts'][:19]}")
        if len(violations) > 10:
            msg_lines.append(f"  ... and {len(violations) - 10} more (see log)")
        message = "\n".join(msg_lines)
        log(message)
        post_discord(message)
    else:
        log(f"OK — checked {total_claims} claims, 0 violations")

if __name__ == "__main__":
    main()
