---
title: Normal Taskboard Autonomy Sprint 1-2 Final Report
type: report
status: done-partial
created: 2026-04-26T07:25Z
owner: codex
related_tasks:
  - 9ca9a7ca-9174-470b-92f1-92f1c5baf1b3
  - 2e90a060-7a1a-4411-aa7e-2c834f00a99e
  - ce4d2da5-9bcf-4ea1-bbe4-30fdce57cb10
---

# Ergebnis

Der Wechsel in den normalen Taskboard-Modus ist vollzogen. Zwei Sprints wurden ueber Atlas/Main durchgezogen:

1. **Sprint 1:** Board Autonomy Policy + Receipt Enforcement  
   Task: `9ca9a7ca-9174-470b-92f1-92f1c5baf1b3`  
   Ergebnis: `done/result`, nach Fix mit persistiertem `sprintOutcome`.

2. **Sprint 2:** Controlled Follow-up Chain + One Big Board Sprint  
   Task: `2e90a060-7a1a-4411-aa7e-2c834f00a99e`  
   Ergebnis: `done/result`, `sprintOutcome.status=partial`.

3. **Safe Follow-up Proof:** Lens read-only Audit  
   Task: `ce4d2da5-9bcf-4ea1-bbe4-30fdce57cb10`  
   Ergebnis: `done/result`, `sprintOutcome.status=done`.

# Was funktioniert jetzt

- Atlas kann einen normalen Board-Sprint aufnehmen und terminal abschliessen.
- Atlas kann genau 3 Follow-up-Previews erzeugen.
- Atlas kann genau einen safe/read-only Follow-up dispatchen und auf terminal warten.
- Sudo/model-switch wurden nicht dispatched und bleiben Operator-Freigabe.
- `sprintOutcome` wird ab jetzt auf Task-Objekten persistiert.

# Fix

Root Cause:
- `sprintOutcome` wurde in `/api/tasks/:id/receipt` zwar angenommen und an Reporting weitergegeben, aber nicht in terminale Task-Patches geschrieben.
- `Task` und `taskboard-store` kannten das Feld nicht dauerhaft.
- `PATCH /api/tasks/:id` konnte `sprintOutcome` nicht nachtragen.

Geaenderte Mission-Control-Dateien:
- `/home/piet/.openclaw/workspace/mission-control/src/app/api/tasks/[id]/receipt/route.ts`
- `/home/piet/.openclaw/workspace/mission-control/src/app/api/tasks/[id]/route.ts`
- `/home/piet/.openclaw/workspace/mission-control/src/lib/taskboard-store.ts`
- `/home/piet/.openclaw/workspace/mission-control/src/lib/taskboard-types.ts`
- `/home/piet/.openclaw/workspace/mission-control/tests/receipt-typescript-gate.test.ts`

Tests:
- `npx vitest run tests/receipt-typescript-gate.test.ts` -> passed
- `npm run typecheck` -> passed
- `npm run build` nach Stop von `mission-control.service` -> passed
- `mission-control.service` -> active

# Live Gates nach Abschluss

- `/api/health`: ok
- Worker Proof: `openRuns=0`, `criticalIssues=0`
- Pickup Proof: `pendingPickup=0`, `criticalFindings=0`, `claimTimeouts=0`
- Aktive Board-Tasks: 0

# Wichtige Schwachstelle

Lens-Audit fand: Von 538 historischen Atlas-done-Tasks hatten nur 1/538 ein `sprintOutcome`, und das war der Codex-Backfill nach dem Fix. Das ist historisch erklaerbar, aber fuer 9/10 noch nicht gut genug.

Interpretation:
- Ab jetzt sollte `sprintOutcome` persistieren.
- Historische Tasks bleiben unvollstaendig, bis wir einen kontrollierten Backfill-/Klassifizierungs-Sprint machen.
- Sprint 2 ist deshalb `partial`, nicht voll gruen.

# Naechste 2 Schritte

1. **P1 Backfill-/Klassifizierungs-Sprint**
   - Read-only zuerst: Liste terminaler Atlas-Tasks ohne `sprintOutcome` erzeugen.
   - Danach nur fuer klar klassifizierbare Tasks Backfill-Vorschlag, nicht blind mutieren.
   - Gate: neue Tasks ab Fix muessen 100% `sprintOutcome` haben.

2. **P1 Autonomy Policy Surface**
   - Eine kleine kanonische Policy fuer Approval-Klassen:
     - safe-read-only = autonom moeglich
     - gated-mutation = Preview/Operator
     - sudo-required = Operator
     - model-switch-required = Operator
   - Gate: Follow-up-Drafts muessen `approvalMode`, `approval_class`, Owner, Priority und DoD tragen.

# Score

Aktueller Normal-Board-Autonomie-Score: **8.4/10**.

Warum nicht 9/10:
- Historische `sprintOutcome`-Coverage ist schwach.
- Approval-Klassen sind im Text vorhanden, aber noch nicht ueberall als harte maschinenlesbare Felder erzwungen.

Warum deutlich besser als Start:
- Der zentrale Receipt-Persistenzfehler ist behoben und deployed.
- Zwei normale Board-Sprints liefen ohne Meeting-System.
- Follow-up-Dispatch wurde auf genau einen safe/read-only Task begrenzt.
- Final live gates sind gruen.
