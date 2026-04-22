# AGENTS.md — Coexistence Rules for AI Coding Agents

**Audience:** Any AI coding agent (OpenAI Codex, Claude Code, Cursor, Aider, etc.) operating in this repository.
**Purpose:** Prevent parallel-universe drift when multiple agents touch the same vault.

> **For Codex CLI users on the homeserver:** global rules are also symlinked at `~/.codex/AGENTS.md` and auto-loaded each session. Shared master lives at `03-Agents/_shared/CODEX-GLOBAL-RULES.md`. If that global load fails (e.g., Codex issue #8759 regression), this file is the fallback.

---

## 1. Where you are

You are operating inside the **openclaw-memory** Obsidian vault — a live knowledge base shared by:

- A **Linux homeserver** (`homeserver` SSH alias, `192.168.178.61`, path `/home/piet/vault/`) running a 15-agent openclaw multi-agent system that writes ~100 markdown files per day and auto-commits to GitHub (`lenardhuebner88-rgb/openclaw-memory`) every ~30 min.
- A **Windows 11 desktop** at `C:\Users\Lenar\Obsidian\openclaw-memory\` — your likely working copy.
- An **Android Galaxy S24** with Obsidian Mobile.

All three are **live-synced via Syncthing v2** (LAN, port 22000). Changes you make on the desktop **propagate to server and phone within seconds**.

## 2. Where to work — single source of truth

- **Desktop filesystem** (`C:\Users\Lenar\Obsidian\openclaw-memory\`) and **server filesystem** (`/home/piet/vault/`) are **live mirrors**. Pick ONE and stay there for the session.
  - Prefer the **desktop** for anything under `03-Projects/`, `03-Agents/codex/`, `05-Research/`.
  - Prefer the **server** (via `ssh homeserver`) for any change touching `.openclaw/`, `03-Agents/OpenClaw/`, `10-KB/`, or crontab.
- Do **not** operate on a third checkout — there is no third checkout. If you create one, you have just invented a parallel universe.

## 3. Announce your presence — every session

Before your first write, create a session file in the shared coordination board:

```
03-Agents/_coordination/YYYY-MM-DD_HHMM_<agent>_<task-slug>.md
```

Template:

```markdown
---
agent: codex              # or claude-code, cursor, aider, ...
started: 2026-04-22T21:45Z
ended:   null             # fill in when done
task: "Short one-line goal"
touching:
  - 03-Projects/foo/
  - 03-Agents/codex/notes/
operator: lenard
---

## Plan
- step 1
- step 2

## Log
(append as you go)
```

- **Check this directory before you start.** If there is another `*_<agent>_*.md` file with `ended: null` that touches overlapping paths, **pause and ask the operator** — Claude Code or another agent is mid-work.
- **Update `ended:` when you finish.** Leave the log.

## 4. Claim the files you edit

Atomically, before you write a file:

1. `grep -rl "ended: null" 03-Agents/_coordination/` — list live sessions.
2. If another live session's `touching:` list overlaps with your file → abort that write, tell the operator, and wait.
3. If no overlap → proceed.

This is cheaper than any lock file and survives crashes (stale claims just get cleaned up by the nightly cron on the homeserver).

## 5. Filesystem conventions you must honor

| Path | Who owns it | Rule for you |
|---|---|---|
| `03-Agents/OpenClaw/`, `03-Agents/Atlas/`, `03-Agents/Forge/`, … agent name dirs | openclaw runtime (server-side) | **Read-only** from any coding agent. Those dirs are live state of openclaw workers; overwriting them breaks the system. |
| `10-KB/` | KB-Compiler cron (server, `0 4 * * *`) | **Read-only.** Regenerated nightly. |
| `03-Agents/codex/` | Codex | **Your home.** Put session notes, scratch, spikes here. |
| `03-Agents/claude-code/` | Claude Code | Claude's home. Don't write here. |
| `03-Agents/_coordination/` | All agents | Shared session-board (see §3). |
| `01-Daily/`, `00-Inbox/` | Human (lenard) | Treat as user space. Append only; never rewrite existing days. |
| `.openclaw/` (server only) | openclaw runtime | **Never touch** unless operator explicitly asked. This is the heartbeat of 14 defense crons. |
| `.git/`, `.obsidian/` | Per-device | Excluded from Syncthing via `.stignore`. Keep device-local. |

## 6. Commits — prefix so we know who did what

When you commit git (server does this automatically every ~30 min, but if you commit manually):

```
codex: <imperative summary>

<body>
```

Prefixes in active use:
- `codex:` — you
- `claude:` — Claude Code
- `auto-sync:` — server-side openclaw auto-commit cron
- `vault backup:` — deprecated (do not use; was from the old obsidian-git plugin, now disabled on desktop)

## 7. Memory system — read, don't overwrite

- The operator keeps memory at `C:\Users\Lenar\.claude\projects\C--Users-Lenar-Neuer-Ordner\memory\MEMORY.md` (desktop) — that is **Claude's** memory. You can read it for context but **do not write** there.
- Authoritative plan/status index: `/home/piet/vault/03-Agents/_VAULT-INDEX.md` on the server.
- System rules: `03-Agents/feedback_system_rules.md` (R1–R50). Honor them; if one trips you, stop and tell the operator.
- The memory-orchestrator cron writes to `.openclaw/workspace/memory/` on the server — do not touch.

## 8. Things that will break the vault (avoid)

- Renaming or deleting anything under `03-Agents/OpenClaw/*` while openclaw agents are running — they hold file descriptors.
- Creating two directories that differ only in case (e.g., `Atlas/` and `atlas/`) — the Linux server allows it, Windows does not. Canonical form is **Title Case** (`Atlas`, `Forge`, `Pixel`).
- Committing `.obsidian/workspace.json`, `.obsidian/community-plugins.json`, or `.obsidian/plugins/*/data.json` — these are per-device and are already excluded by `.stignore` + `.gitignore`.
- `git push --force` against `origin/master` on either desktop or server without operator approval — there is a 30-min commit cadence and a mobile device in the sync ring.
- Running `npm install`, `docker compose up`, or long builds inside the vault directory on the desktop — Syncthing watches it. Do heavy work in a scratch dir outside.

## 9. End-of-session checklist

1. `ended:` timestamp filled in your `_coordination/` session file.
2. Final log entries appended.
3. A one-line summary in `03-Agents/codex/daily/YYYY-MM-DD.md` so the operator and the nightly KB-Compiler can pick it up.
4. If you changed config that affects the server, mention it explicitly so the operator can verify the next memory-orchestrator run.
5. Don't commit on the user's behalf unless they asked — the server's auto-sync will capture your changes in the next 30-min window.

---

*This file is versioned. If you think a rule is wrong, propose an edit in your session log and ask the operator. Don't silently change it.*
