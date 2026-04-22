# Codex Global Rules — coexistence with Claude Code

**This file is loaded at the start of EVERY Codex CLI session.** It is symlinked from `~/.codex/AGENTS.md` on the homeserver and lives in the Syncthing-synced vault so desktop/phone copies stay in step.

Authoritative source: `<vault>/03-Agents/_shared/CODEX-GLOBAL-RULES.md`. If you disagree with a rule here, propose an edit in your session log — do not silently override.

## Who you are

You are **Codex CLI** running on a Linux homeserver at `/home/piet` (user `piet`, hostname `huebners`). You share this vault with:

- **Claude Code** — a separate agent also writing to the same vault (memory at `C:\Users\Lenar\.claude\projects\...\MEMORY.md` on a desktop that lives in the Syncthing ring).
- **openclaw multi-agent system** — a 15-agent runtime on this same host that auto-writes to `/home/piet/vault/03-Agents/{Atlas,Forge,Pixel,...}` continuously and commits every ~30 min.
- **Android Galaxy S24** — Obsidian Mobile in the Syncthing ring.

All four touch the same filesystem. You are not alone. Act like it.

## Where to work

- **Vault root:** `/home/piet/vault/` (identical to `C:\Users\Lenar\Obsidian\openclaw-memory\` on the desktop, live-synced via Syncthing v2 on port 22000).
- **Your home in the vault:** `03-Agents/codex/` (notes, scratch, daily logs). Claude's home is `03-Agents/claude-code/`. Stay out of each other's homes unless handing off.
- **openclaw runtime internals:** `/home/piet/.openclaw/` — read-only unless the operator explicitly asks. Touching it wrong has caused 25-minute production outages (2026-04-20 incident).
- **Shared coordination board:** `03-Agents/_coordination/` — session check-in/out, see below.

## Before every task: three-step bootstrap

1. **Read project rules:** `cat <repo-root>/AGENTS.md` for the project-specific ownership table and commit conventions. If the repo root is not detectable (no `.git/`), fall back to `/home/piet/vault/AGENTS.md`.
2. **Check the coordination board:** `ls /home/piet/vault/03-Agents/_coordination/ | head -30` then `grep -l "ended: null" /home/piet/vault/03-Agents/_coordination/*.md 2>/dev/null`. If any live session's `touching:` list overlaps with files you plan to edit → **stop** and tell the operator. Claude or another agent is mid-work.
3. **Create your session file** in `03-Agents/_coordination/` using this template:
   ```markdown
   ---
   agent: codex
   started: 2026-04-22T21:50Z
   ended: null
   task: "One-line goal"
   touching:
     - 03-Agents/codex/scratch/
     - 03-Projects/foo/bar.ts
   operator: lenard
   ---
   ## Plan
   ## Log
   ```
4. When finished: set `ended:` to UTC now, append a one-line entry to `03-Agents/codex/daily/$(date +%Y-%m-%d).md`.

## Authoritative rule indexes (read once per session if relevant)

- `/home/piet/vault/03-Agents/feedback_system_rules.md` — R1–R50 system rules. R50 (session-lock governance) in particular.
- `/home/piet/vault/03-Agents/_VAULT-INDEX.md` — live sprint + plan status.
- `/home/piet/vault/MEMORY.md` — deprecated (there is no repo-level MEMORY.md; Claude's memory is on the desktop and not in git).

## Filesystem ownership (do-not-touch unless invited)

| Path | Owner | Rule |
|---|---|---|
| `03-Agents/OpenClaw/`, `Atlas/`, `Forge/`, `Pixel/`, `Lens/`, `James/`, `Main/`, `Spark/`, `Sre Expert/`, … | openclaw runtime | **Read-only.** Agents hold open file handles; you will corrupt live state. |
| `10-KB/` | KB-Compiler cron `0 4 * * *` | **Read-only.** Regenerated nightly from facts. |
| `03-Agents/memory-dashboard.md` | Memory orchestrator | **Read-only.** Auto-regen at `30 4 * * *`. |
| `.openclaw/` | openclaw runtime | **Never touch** unless operator asked. 14 defense crons live here. |
| `.git/` | Each device-local repo | Per-device; excluded from Syncthing via `.stignore`. |
| `.obsidian/workspace*.json`, `.obsidian/community-plugins.json`, `.obsidian/plugins/*/data.json` | Per-device | Excluded from Syncthing + gitignored. Don't commit. |
| `01-Daily/`, `00-Inbox/` | Human (operator) | Append-only. Never rewrite historic days. |
| `03-Agents/codex/` | **You** | Your home. |

## Commits — prefix so we know who did what

- `codex:` — you (manual commit only when operator explicitly asks).
- `claude:` — Claude Code.
- `auto-sync:` — the server-side openclaw cron (every ~30 min via post-commit hook to GitHub).
- Do **not** use `vault backup:` — that was the old obsidian-git plugin, deprecated 2026-04-22.
- Do **not** `git push --force` on `master` without operator OK — the mobile device would see divergence.

## Things that will break the vault (hard gotchas)

- Creating a directory that differs from an existing one only in case (e.g., `Atlas/` vs `atlas/`). Linux allows it, the Windows desktop resolver merges them → Syncthing-conflict storm. **Canonical form is Title Case** (`Atlas`, `Forge`, `Pixel`).
- Long-running builds (`npm install`, `docker compose up`, `cargo build`) inside the vault: Syncthing's fsWatcher will thrash. Use `/tmp/` or `~/scratch/` for heavy I/O.
- Dropping an `AGENTS.override.md` at repo root without updating the shared board — it silently overrides this file and confuses the other agents.

## Memory hygiene (your `~/.codex/memories/`)

- The `memories/` directory is auto-populated after rollouts. Treat it as a read cache; **authoritative rules live in `AGENTS.md` (this file)**.
- If a memory entry conflicts with a rule here, trust **this file** and flag the stale memory to the operator.
- Do not write new files into `~/.codex/memories/` by hand — that's the rollout pipeline's job.

## End-of-session checklist

1. `ended:` timestamp in your `03-Agents/_coordination/` session file.
2. One-line summary appended to `03-Agents/codex/daily/YYYY-MM-DD.md`.
3. If you modified anything under `.openclaw/` (hopefully not), tell the operator explicitly so they can verify the next memory-orchestrator run.
4. Do **not** commit on the user's behalf unless asked — `auto-sync:` will pick up your changes within 30 minutes.

---

*Version 1 — 2026-04-22. Edits go through the operator via the session log.*
