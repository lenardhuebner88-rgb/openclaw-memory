---
title: Hermes OpenClaw Collaboration Improvement Plan
created: 2026-05-03T18:10Z
agent: Hermes
for: Piet, Atlas, Forge
status: proposed_plan
scope: hermes-openclaw-collaboration
mutation_level: plan_only_no_runtime_changes
---

# Hermes OpenClaw Collaboration Improvement Plan

> **For Atlas/Forge:** This is a proposal/implementation plan only. It does not record any OpenClaw runtime/config change.

**Goal:** Make Hermes more useful as Piet's bounded OpenClaw shadow-debug assistant without increasing operational risk.

**Architecture:** Improve Hermes in three layers: (1) structured read-only evidence, (2) OpenClaw-specific skills/runbooks, (3) Atlas-readable vault handoffs. Break-glass mutations remain explicitly gated by Piet.

**Tech Stack:** Hermes Agent, OpenClaw read-only MCP, Mission Control read-only MCP, QMD Vault MCP, `/home/piet/vault`, optional future OpenClaw redacted API endpoints.

---

## Phase 0 — Governance Baseline

### Task 0.1: Keep the operating boundary explicit

**Objective:** Preserve Hermes as read-only first, break-glass only with explicit Piet approval.

**Files:**
- Review: `/home/piet/vault/03-Agents/Hermes/AGENTS.md`
- Review: Hermes skill `openclaw-operator`

**Acceptance Criteria:**
- Hermes does not get blanket YOLO permissions.
- Restarts/config edits still require live evidence, exact command/file/key, expected post-check, and explicit in-thread approval.
- Hermes does not receive or store raw Discord/OpenClaw tokens.

---

## Phase 1 — Better Read-only Evidence

### Task 1.1: Define redacted effective config endpoint

**Objective:** Give Hermes/Atlas a safe way to inspect actual OpenClaw config without secrets.

**Proposed Endpoint:**

```text
GET /api/config/effective-redacted
```

**Should Include:**

```text
openclaw version
agents.defaults.agentRuntime
agents list: id, name, model.primary, model.fallbacks, agentRuntime
models.providers: provider id, baseUrl host only, api type, auth type, configured models
plugins: id, status, providerIds
channels.discord: enabled channel ids/names, streaming mode, command flags
```

**Must Redact:**

```text
apiKey
tokens
OAuth refresh/access tokens
Discord bot token
email/password/secrets
```

**Acceptance Criteria:**
- Endpoint returns JSON.
- No secret-shaped values appear in response.
- Hermes can answer model-routing questions without shell-reading full `openclaw.json`.

### Task 1.2: Define structured model/runtime failure endpoint

**Objective:** Replace broad journal grep with direct error-class evidence.

**Proposed Endpoint:**

```text
GET /api/diagnostics/model-failures?window=30m
```

**Should Group By:**

```text
provider_not_found
auth_failed
fetch_timeout
codex_app_server_timeout
tool_call_format_error
discord_send_failed
lane_timeout
```

**Acceptance Criteria:**
- Each item includes timestamp, agent id, session id if known, model/provider, lane, error class, redacted message.
- Supports `window=10m|30m|2h`.
- No raw prompt/user content required.

### Task 1.3: Define session-health summary endpoint

**Objective:** Let Hermes quickly distinguish healthy sessions from stuck lanes.

**Proposed Endpoint:**

```text
GET /api/diagnostics/sessions/summary?active=180m
```

**Should Include:**

```text
agent id
session id
status
updatedAt
ageMs
model/provider/runtime
lastErrorClass
inputTokens/outputTokens if available
active_embedded_run / queued_work_without_active_run indicators
```

**Acceptance Criteria:**
- Identifies Atlas stuck/running sessions without parsing JSONL files.
- Separates gateway liveness from agent-turn health.

---

## Phase 2 — Hermes Skills / Runbooks

### Task 2.1: Create `openclaw-model-routing` skill

**Objective:** Encode known model/provider/runtime pitfalls.

**Content Must Cover:**

```text
openai/gpt-* + agentRuntime.id=codex for ChatGPT/Codex subscription path
openai-codex/* vs codex/openai provider confusion
Codex runtime vs PI/provider runtime
agentRuntime.fallback: pi for non-Codex fallback providers
MiniMax Token Plan vs portal/OAuth route
OpenRouter provider-not-found handling
verification: direct config parse beats cached model-status
```

**Acceptance Criteria:**
- Hermes loads this skill for `/model`, fallback, provider, MiniMax/OpenRouter/OpenAI routing questions.
- Includes safe read-only diagnostic checklist.

### Task 2.2: Create `minimax-openclaw-token-plan` skill

**Objective:** Preserve MiniMax M2.7-highspeed research as reusable procedure.

**Content Must Cover:**

```text
Piet uses MiniMax Token Plan API key
baseUrl=https://api.minimax.io/anthropic
api=anthropic-messages
model=minimax/MiniMax-M2.7-highspeed
recommended initial maxTokens=8192-16384
temperature=1 per MiniMax docs
streaming on
known risks: TODO continuation stops, duplicate tool_call id, HTTP 400 / 2013
isolation test matrix before production use
```

**Acceptance Criteria:**
- Hermes no longer assumes missing MiniMax account/plan.
- Atlas can use the skill output to select safe tests.

### Task 2.3: Create `openclaw-incident-rca` template/skill

**Objective:** Standardize incident reports.

**Template:**

```text
Summary
Timeline
Confirmed Facts
Rejected Hypotheses
Root Cause
Mitigation
Permanent Fix
Verification
Follow-ups
```

**Acceptance Criteria:**
- RCA files become consistent and Atlas-readable.
- Distinguishes operator-provided claims from live evidence.

### Task 2.4: Create `openclaw-config-change-safe` skill

**Objective:** Standardize approved config changes.

**Required Gate:**

```text
1. live evidence
2. exact file/key/path
3. timestamped backup
4. intended diff
5. Piet approval
6. apply targeted edit
7. focused post-check
8. receipt
```

**Acceptance Criteria:**
- No accidental broad JSON edits.
- Every config change has backup + verify trail.

### Task 2.5: Create `openclaw-discord-ops` skill

**Objective:** Improve Discord-specific diagnosis.

**Content Must Cover:**

```text
channel isolation: Hermes channel intentionally not OpenClaw-owned
native slash command registry vs Discord UI delay
Commander legacy collision patterns
Discord WS silent-death pattern
streaming/typing mode UX checks
Discord send failure classes
```

**Acceptance Criteria:**
- Hermes can verify Discord command/UX claims without treating UI picker as sole truth.

---

## Phase 3 — Atlas-readable Vault Integration

### Task 3.1: Create Hermes index file

**Objective:** Give Atlas one stable file to find Hermes outputs.

**File:**

```text
/home/piet/vault/03-Agents/Hermes/INDEX.md
```

**Initial Sections:**

```text
Current Role
Read-only MCP Surfaces
Latest Receipts
Latest Plans
Useful Runbooks
Atlas Handoff Format
```

**Acceptance Criteria:**
- Atlas can find latest Hermes plans/receipts without directory guessing.
- Index avoids `/home/piet/Vault` and `.openclaw/workspace/vault` traps.

### Task 3.2: Add standard `for_atlas` block to future receipts/plans

**Objective:** Make Hermes outputs machine-readable for Atlas.

**YAML Block:**

```yaml
for_atlas:
  status: info_only | actionable | needs_piet_approval
  affected_agents: []
  affected_files: []
  recommended_next_action: ""
  risk: ""
  evidence_files: []
```

**Acceptance Criteria:**
- New Hermes receipts include a clear Atlas handoff.
- Atlas can decide whether to act, ask Piet, or just ingest context.

### Task 3.3: Add receipt naming convention

**Objective:** Keep Hermes outputs predictable.

**Convention:**

```text
03-Agents/Hermes/receipts/YYYY-MM-DD_<topic>_receipt.md
03-Agents/Hermes/plans/YYYY-MM-DD_<topic>_plan.md
03-Agents/Hermes/lessons/YYYY-MM-DD_<topic>_lesson.md
```

**Acceptance Criteria:**
- Avoids duplicate topic filenames.
- Easier nightly KB pickup.

---

## Phase 4 — Optional Break-glass Guardrails

### Task 4.1: Document approved restart runbook shape

**Objective:** Keep restarts bounded and auditable.

**Allowed Only With Approval:**

```text
systemctl --user restart openclaw-gateway.service
systemctl --user restart mission-control.service
```

**Preconditions:**

```text
live evidence of stuck/degraded service
exact service named
expected post-check named
Piet approval in current thread
```

**Post-check:**

```text
MainPID changed if restart expected
health endpoint live
recent journal has no fresh matching error class
relevant E2E signal works
```

**Acceptance Criteria:**
- Hermes does not restart services from vague symptoms.

### Task 4.2: Document approved config patch runbook shape

**Objective:** Keep config edits reversible.

**Allowed Only With Approval:**

```text
Targeted edit to /home/piet/.openclaw/openclaw.json or named runbook file
```

**Preconditions:**

```text
timestamped backup path stated
exact key/path stated
intended diff stated
Piet approval in current thread
```

**Post-check:**

```text
JSON parse succeeds
specific key has expected value
gateway restart only if necessary and approved
focused health/session/log check
receipt written
```

**Acceptance Criteria:**
- No silent config drift.
- No token exposure.

---

## Phase 5 — Verification Matrix

### Task 5.1: Verify read-only endpoints

**Objective:** Prove new MCP/API surfaces are useful and safe.

**Tests:**

```text
Call effective-redacted config endpoint
Search response for token-like strings
Compare selected fields against direct redacted file parse
Call model-failures endpoint during known clean period
Call session summary endpoint during active Atlas session
```

**Expected:**

```text
No secrets returned
Fields match live config/session state
Failure grouping is accurate enough for PERN reporting
```

### Task 5.2: Verify new skills load in right cases

**Objective:** Ensure Hermes picks the correct skill automatically.

**Scenarios:**

```text
"Atlas fallback minimax not found"
"Discord slash commands hängen"
"Bitte RCA schreiben"
"Config Änderung vorbereiten"
"MiniMax M2.7 highspeed timeouted"
```

**Expected:**
- Correct skill is loaded before answering.
- Response remains PERN-style for incidents.

### Task 5.3: Verify Atlas handoff readability

**Objective:** Check Atlas can consume Hermes outputs.

**Test:**
- Give Atlas `03-Agents/Hermes/INDEX.md` and one receipt with `for_atlas` block.
- Ask Atlas to summarize recommended next action and required approval state.

**Expected:**
- Atlas distinguishes `info_only` vs `needs_piet_approval`.

---

## Proposed Implementation Order

1. Create/patch skills:
   - `openclaw-model-routing`
   - `minimax-openclaw-token-plan`
   - `openclaw-incident-rca`
   - `openclaw-config-change-safe`
   - `openclaw-discord-ops`
2. Create Hermes `INDEX.md` in vault.
3. Adopt `for_atlas` YAML block in all future Hermes plans/receipts.
4. Ask Forge/Atlas to implement read-only redacted endpoints if desired.
5. Validate with the verification matrix.
6. Only then consider optional break-glass runbook formalization.

## Non-goals

- No YOLO mode.
- No permanent command allowlist expansion.
- No raw token access.
- No automatic crons/tasks/agents created by Hermes.
- No writing to `/home/piet/.openclaw/workspace/vault` as SSoT.
- No replacing Atlas as lead orchestrator.

## for_atlas

```yaml
for_atlas:
  status: actionable
  affected_agents:
    - Hermes
    - Atlas
    - Forge
  affected_files:
    - /home/piet/vault/03-Agents/Hermes/plans/hermes-openclaw-collaboration-improvement-plan-2026-05-03.md
    - /home/piet/vault/03-Agents/Hermes/INDEX.md
    - /home/piet/.hermes/skills/devops/openclaw-operator/SKILL.md
  recommended_next_action: "Start with Phase 2 skills and Phase 3 Hermes INDEX.md; defer API endpoint implementation to Forge/Atlas as a normal task."
  risk: "Low for vault/skill docs; medium for new OpenClaw API endpoints; high for any ungated runtime mutation."
  evidence_files:
    - /home/piet/vault/03-Agents/Hermes/receipts/minimax-m27-highspeed-research-summary-2026-05-03.md
```
