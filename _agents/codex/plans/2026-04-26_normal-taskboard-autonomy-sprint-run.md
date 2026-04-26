---
title: Normal Taskboard Autonomy Sprint Run
type: execution-plan
status: in-progress
created: 2026-04-26T06:39Z
owner: codex
parent_plan: 2026-04-25_meeting-adversarial-review-and-taskboard-autonomy-sprints.md
---

# Ziel

Wechsel weg von `/meeting`/`debate` hin zum normalen Taskboard-Prozess.

Operator-Zielbild:
- Operator gibt Atlas ein Audit oder einen Sprint.
- Atlas arbeitet sequentiell und autonom ab.
- Atlas erstellt Follow-up-Previews mit Gates.
- Nur sudo und Modellwechsel brauchen explizite Operator-Freigabe.
- Kein stiller Fanout, keine versteckte Cron-Automation, keine parallelen Atlas-Ketten.

# Live Startzustand 2026-04-26T06:36Z

Gates:
- `/api/health`: ok
- Worker-Proof: `criticalIssues=0`, `openRuns=2`
- Pickup-Proof: `criticalFindings=0`, `pendingPickup=0`, `claimTimeouts=0`, `historicalClaimTimeouts=11`
- Meeting-Runner: no running meetings, no queued meetings
- Aktive Board-Tasks:
  - `6c867848-d303-4312-b0af-63e8d6da74da` — Main/Atlas, `Nightly self-improvement build 2026-04-26`, `in-progress`, `receiptStage=progress`
  - `ae8474f4-e379-4b70-a6e9-606b6bc1ffe7` — SRE, `Make sqlite memory maintenance skip cleanly`, `in-progress`, `receiptStage=progress`

Entscheidung:
- Sprint 1 wird nicht parallel zu einem aktiven Main-/Atlas-Task dispatched.
- Codex beobachtet den bestehenden Main-Task bis terminal oder eindeutig idle, danach erst Sprint 1.

# Sprint 1: Board Autonomy Policy + Receipt Enforcement

Dispatch-Bedingung:
- Main/Atlas hat keinen anderen aktiven Task oder der aktive Task ist terminal.
- Health/Worker/Pickup bleiben gruen.

DoD:
- Atlas erzeugt einen terminalen Parent-Task.
- Terminales Task-Objekt enthaelt `sprintOutcome != null`.
- Policy klaert Heartbeat vs Worker vs Cron vs Atlas-Orchestrierung.
- Follow-ups bleiben Preview/Draft und enthalten Approval-Klassen.
- Sudo/model-switch sind `operator-go-required`.

Stop:
- Neuer Worker-/Pickup-Critical.
- Mehr als ein Atlas-Strang.
- Terminal ohne `sprintOutcome`.
- Follow-up ohne Approval dispatched.

# Sprint 2: Controlled Follow-up Chain + One Big Atlas Sprint

Dispatch-Bedingung:
- Sprint 1 gruen.
- Keine offenen Main-/Atlas-Runs.

DoD:
- Ein grosser Atlas-Audit-Sprint laeuft sequentiell.
- Genau 3 Follow-up-Previews werden erzeugt.
- Maximal ein safe/read-only Follow-up wird ausgefuehrt.
- Alle finalen Proofs sind gruen.

# Statuslog

- 2026-04-26T06:39Z Run gestartet; Gate 0 gruen, aber Main/Atlas bereits aktiv. Sprint 1 wartet auf terminal/idle.
- 2026-04-26T06:44Z Main/Atlas Nightly ist terminal `done/result`, aber ohne `sprintOutcome`; das wird als Live-Gap in Sprint 1 aufgenommen. Sprint 1 wurde als Task `9ca9a7ca-9174-470b-92f1-92f1c5baf1b3` an Main/Atlas dispatched.
- 2026-04-26T07:10Z Sprint 1 terminal `done/result`. Gate war zuerst rot, weil `sprintOutcome` nicht persistiert wurde. Root Cause: Receipt-Route reichte `sprintOutcome` nur an Reporting weiter, aber nicht in terminale Task-Patches; Taskboard-Store/Type/PATCH kannten das Feld nicht. Minimal-Fix deployed, Regressionstest + Typecheck + Production Build passed, Service active, Sprint-1-Task backfilled mit `sprintOutcome`, Health/Worker/Pickup gruen.
- 2026-04-26T07:12Z Sprint 2 als Task `2e90a060-7a1a-4411-aa7e-2c834f00a99e` dispatched: Controlled Follow-up Chain + One Big Board Sprint.
