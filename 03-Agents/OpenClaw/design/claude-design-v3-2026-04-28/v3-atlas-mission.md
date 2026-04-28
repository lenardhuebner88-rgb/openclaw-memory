---
title: V3 Atlas Mission — Autonomous Bootstrap & Execution
date: 2026-04-29
target: atlas (main agent profile)
trigger: bootstrap-task POST by operator morning of 2026-04-29
mode: full-atlas-autonomy (NO codex involvement)
---

# Atlas Mission: V3 Taskboard Implementation Sprint

## Du bist Atlas. Mission:

Bootstrap und orchestriere den V3 Taskboard Implementation Sprint end-to-end.
KEIN Codex. KEIN Operator-Eingriff während Ausführung.
Du handhabst Phasen 0–4 selbst über deinen Auto-Pickup-Decision-Loop.

## Pflichtlektüre (Cycle 1)

1. `/home/piet/vault/03-Agents/OpenClaw/design/claude-design-v3-2026-04-28/v3-status-derivation-spec.md`
   → V3 Architektur, 12 Status, 7 Lanes, Mapping-Tabelle
2. `/home/piet/vault/03-Agents/OpenClaw/design/claude-design-v3-2026-04-28/v3-codex-dispatch-prompt-2026-04-28.md`
   → SPRINT-MATRIX (17 Slices), SLICE DETAILS (per-slice tasks), HARTE REGELN
3. `/home/piet/vault/03-Agents/OpenClaw/design/claude-design-v3-2026-04-28/source-export-final-2026-04-28-2213/`
   → Polish-Pass-Source-Files (Atlas selbst nicht direkt nötig; Worker lesen das)

## State-Detection pro Cycle

Du machst pro Cycle genau **eine** Entscheidung (R5). Vor jeder Entscheidung:

```
1. GET deine eigene master-task: /api/tasks/<own-id>
2. GET board snapshot: /api/board/snapshot
3. test -f /home/piet/.openclaw/state/v3-atlas-handover.json
4. test -f /home/piet/.openclaw/HALT  → wenn ja: cleanly exit
5. Decide:

IF (handover-file fehlt)
  → Phase 0: Vault-Files lesen, /api/health + snapshot baseline,
    git -C ~/.openclaw/workspace/mission-control status --short,
    schreibe handover-skeleton.
  → Discord-Report "Phase 0 — Baseline complete"

ELSE IF (slice-tasks erstellt < 17)
  → Phase 1: Erstelle nächsten Slice-Task gemäß SPRINT-MATRIX-Reihenfolge:
    F1 → A0 → A1 → B → C → D → F2 → E → F3 → F → G → H → I → V0 → V1 → V2 → V3
  → Pro-Cycle 1 Task-Creation. Per-Slice-Prompt-Template aus SLICE DETAILS
    übernehmen (Block für jeweiligen Slice id-genau kopieren in description).
  → Beim 17. Task: Discord-Report "Phase 1 — All 17 slices created"

ELSE IF (Slices existieren UND eligible Slice nicht dispatched UND WIP <2)
  → Phase 2: Wähle Slice mit erfüllten Dependencies + freier Agent-Capacity.
    POST /api/tasks/<slice-id>/dispatch.
  → Discord-Report "Slice <id> dispatched to <agent>"

ELSE IF (Slices in-progress UND noch nicht alle done)
  → Phase 3 monitoring: Lese Receipts. PATCH Slice-Status auf done|failed
    nach Acceptance-Check. Bei FAIL: Discord-Escalation, weiter mit independent slices.
  → Discord-Report nur bei Slice-Transition (accepted, result, done, fail).

ELSE IF (alle Slices done OR sprint-fatal)
  → Phase 4: aggregate. Schreibe final summary. PATCH master done|partial.
    Verdict: GREEN | YELLOW | RED.
  → Final Discord-Report mit Sprint-Closure.

END
```

## Phase 0 — Baseline (1 Cycle)

```bash
# Read & verify (no mutation)
curl -sS http://127.0.0.1:3000/api/health | jq '{status, severity, openCount: .board.openCount}'
curl -sS http://127.0.0.1:3000/api/board/snapshot | jq '{laneCounts: .summary.laneCounts, statusCounts: .summary.statusCounts, taskCount: (.tasks | length)}'
git -C /home/piet/.openclaw/workspace/mission-control status --short

# Read 3 vault files (siehe Pflichtlektüre)

# Write handover skeleton
cat > /home/piet/.openclaw/state/v3-atlas-handover.json <<EOF
{
  "sprintId": "v3-taskboard-2026-04-29",
  "createdAt": "<iso>",
  "masterTaskId": "<own-task-id>",
  "phase": "0-baseline-complete",
  "slices": [],
  "specFile": "/home/piet/vault/03-Agents/OpenClaw/design/claude-design-v3-2026-04-28/v3-status-derivation-spec.md",
  "dispatchPrompt": "/home/piet/vault/03-Agents/OpenClaw/design/claude-design-v3-2026-04-28/v3-codex-dispatch-prompt-2026-04-28.md",
  "source": "/home/piet/vault/03-Agents/OpenClaw/design/claude-design-v3-2026-04-28/source-export-final-2026-04-28-2213/",
  "dirtyFilesAtStart": [...],
  "gitStatusOutput": "..."
}
EOF
```

Discord-Report:
```
[V3 SPRINT] Phase: 0 | Slice: -
Status: PASS
Owner: atlas

Was: Vault gelesen (spec, dispatch-prompt, source). Live-Baseline ok
(/api/health=ok, openCount=<n>, dirty-files=<n>). Handover-skeleton geschrieben.

Evidence: /home/piet/.openclaw/state/v3-atlas-handover.json

Next: Phase 1 — Erstelle Slice F1 als ersten der 17 Tasks.
```

## Phase 1 — Slice Task Creation (~17 Cycles, 1 Task pro Cycle)

Für jeden Slice in SPRINT-MATRIX-Reihenfolge:

```
POST http://127.0.0.1:3000/api/tasks
Content-Type: application/json

{
  "title": "[V3 Sprint] Slice <id> — <name>",
  "description": "<per-slice-block from SLICE DETAILS>",
  "assignee": "<profile>",
  "parentTaskId": "<your-master-id>",
  "priority": "<high if id in (F1,V1) else medium>",
  "approvalClass": "safe-read-only",
  "riskLevel": "<medium if id in (G,F2,F3) else low>",
  "decisionKey": "v3-sprint-2026-04-29-<id-lowercase>",
  "labels": ["v3-sprint", "slice-<id-lowercase>"],
  "status": "draft"
}
```

**Profile-Mapping:**
- forge → `sre-expert` (F1, F2, F3)
- pixel → `frontend-guru` (A0, A1, B, C, D, E, F, H, I)
- pixel + forge → both for G (assigne primary `frontend-guru`, secondary mention in description)
- lens → `efficiency-auditor` (V0, V1)
- spark → `spark` (V2)
- james → `james` (V3)

**Per-Slice-Prompt:** Kopiere den vollständigen Block aus `v3-codex-dispatch-prompt-2026-04-28.md` Section "SLICE DETAILS" für den jeweiligen Slice-ID. Inhalt = `description`-Feld des Tasks.

Idempotenz: wenn `decisionKey` schon existiert, skip create (POST wird vom System abgelehnt mit 409 Conflict — das ist OK).

Aktualisiere `slices[]` in `v3-atlas-handover.json` nach jeder Creation.

Erst beim 17. Slice (V3 Doc): Discord-Report "Phase 1 — All 17 slices created, ready to dispatch."

## Phase 2 + 3 — Dispatch & Monitor (continuous, viele Cycles)

Dependency-Graph:
```
F1, A0, V3 (parallel-startable)
A1 → A0+F1
B → A1
C → B
D → C
F2 → F1
E → D+F2
F3 → P0 (parallel-startable)
F → E+F3
G → F
H → F
I → D
V0 (parallel throughout)
V1 → E+I
V2 → I
S8 → V0+V1+V2+V3+all
```

Pro Cycle:
1. GET /api/tasks?parentTaskId=<master>
2. Eligible-Filter: `status=draft AND deps satisfied`
3. WIP-Check: GET in-progress count global + per-agent
4. Wenn WIP < 2 global AND target-agent 0 in-progress: dispatch nächsten eligible
5. POST /api/tasks/<id>/dispatch with dispatchTarget=<profile>
6. Auto-pickup-Cron picks für den Worker (existing pipeline)
7. Discord-Report Slice-Dispatched

Beim Receipt-Tracking pro Cycle:
1. GET /api/tasks?parentTaskId=<master> für aktuelle states
2. Wenn neuer `result`-Receipt: Acceptance-Check gegen SPRINT-MATRIX
3. PATCH Slice-Status: done | failed | partial
4. Discord-Report Slice-Result
5. Update handover-file slices[].status

Bei Slice-FAIL:
- Wenn id ∈ {F1, V1}: Discord-Escalation, dependents bleiben blocked, weiter mit independent slices
- Sonst: Discord-Notice, weiter

## Phase 4 — Sprint Close (1 Cycle, wenn alle Slices terminal)

Wenn alle 17 Slices Status terminal (done | failed | partial):

1. Aggregate Status:
   ```
   GET /api/tasks?parentTaskId=<master>
   ```
2. Lese Lens V0 audit: `/home/piet/.openclaw/workspace/memory/05-learnings/v3-atlas-autonomy-audit-2026-04-28.md`
3. Berechne Verdict:
   - GREEN: alle Slices PASS, 0 Eskalationen
   - YELLOW: einige PARTIAL/BLOCKED aber Sprint completed
   - RED: Sprint blocked, manual recovery nötig
4. Schreibe final report:
   - `/home/piet/.openclaw/workspace/memory/05-learnings/v3-sprint-2026-04-29-final.md`
   - Aggregierter Status pro Slice
   - Atlas-Autonomy-Verdict mit Score
   - Operator-Action-Items für morgen-review (Slice G live validation)
5. PATCH master: status=done|partial, resultSummary=<verdict + summary>
6. Final Discord-Report:
   ```
   [V3 SPRINT] Phase: 4 | Slice: ALL
   Status: <verdict>
   Owner: atlas

   Was: Sprint complete. <n>/17 slices PASS. Atlas-Autonomy verdict: <GREEN|YELLOW|RED>.
   Evidence:
   - master task: <id>
   - final report: <path>
   - per-slice: F1=<>, A0=<>, A1=<>, B=<>, C=<>, D=<>, F2=<>, E=<>, F3=<>,
     F=<>, G=<>, H=<>, I=<>, V0=<>, V1=<>, V2=<>, V3=<>
   Open operator actions:
   - Slice G live-task validation (manual UI walk-through on /kanban-v3-preview)
   - Review V0 autonomy audit findings
   Next: <single next action>
   ```

## Discord-Reports — Format & Cadence

Channel: **1495737862522405088** (plain text, NO embeds, NO attachments)

Send via:
```
curl -X POST http://127.0.0.1:3000/api/discord/send \
  -H 'Content-Type: application/json' \
  -d '{"channelId":"1495737862522405088","message":"<plain-text>"}'
```

Cadence (consolidated, no spam):
- 1× nach Phase 0 Done
- 1× nach Phase 1 Done (alle 17 Tasks created)
- 1× pro Slice Dispatched
- 1× pro Slice Result (PASS/FAIL/PARTIAL)
- 1× final Phase 4

→ Erwartete Gesamt-Reports: ~37 Messages über den Tag.

KEINE hourly heartbeats. KEINE Duplicates. KEINE per-Cycle-Reports.

## Hard Rules (aus Mission Control)

- WIP: max 2 global, max 1 pro Agent-Profile
- 1 Decision pro Cycle (du)
- Kein Touch an `/kanban`, `/taskboard`, `/dashboard`, files in `git status --short`
- Slice G autonomous-night: build full + tests gegen MOCK DATA, KEINE live mutations
- Operator-Approval (Hard Rule 8 in plan): falls für Slice nötig, escalate
  via Discord mit exakten command, weiter mit anderen independent slices
  (NICHT ganzen Sprint blocken)

## Kill-Switch

- Test `/home/piet/.openclaw/HALT` vor jeder Decision: wenn vorhanden →
  current cycle clean schließen, save state, exit
- Discord-Listener `!sprint halt` reagiert über `session-health-monitor` cron
- 3 consecutive API-5xx → that-slice auto-HALT, weiter mit anderen

## Begin

Cycle 1: Phase 0. Read this mission file + spec + dispatch-prompt. Confirm
handover-file doesn't exist. Initialize Phase 0 baseline.
