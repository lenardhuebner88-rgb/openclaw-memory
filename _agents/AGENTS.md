# 03-Agents — Agent Working Memory & Scratch

**Purpose:** Live per-agent state (working-context, handoffs, scratch). The openclaw runtime holds open file handles here — treat carefully.
**Writers:** openclaw agents (Atlas, Forge, Pixel, Lens, James, Main, Spark, Sre Expert, Researcher, OpenClaw, etc.), each in their own sub-dir.
**Readers:** Other agents + human.

## Structure
- `<AgentName>/working-context.md` — live state
- `<AgentName>/daily/YYYY-MM-DD.md` — agent daily logs
- `_handoffs/` — inter-agent session handovers
- `_coordination/` — shared session board (Claude Code, Codex, etc.)
- `_shared/` — cross-agent rules (e.g., `CODEX-GLOBAL-RULES.md`)

## Rules
- NEVER rename or delete a per-agent dir while its agent is running. Use R50 session-lock first.
- Case-sensitive: canonical is Title Case (`Atlas`, not `atlas`).
- Handovers write to `_handoffs/`, not to the target agent's own dir.

## Never touch
- `memory-dashboard.md` — auto-regenerated `30 4 * * *`.
- `_VAULT-INDEX.md` — authoritative plan/status; append-only via dedicated script.
