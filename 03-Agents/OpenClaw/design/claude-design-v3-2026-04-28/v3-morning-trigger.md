---
title: V3 Sprint — Morning Trigger Instructions
date: 2026-04-29
target: operator
mode: full-atlas-autonomy
---

# V3 Sprint Morning Trigger

## Single command, ein Schuss

Morgens (08:00 oder wann du willst — Atlas läuft autonom egal wann):

```bash
ssh homeserver "curl -sS -X POST http://127.0.0.1:3000/api/tasks \
  -H 'Content-Type: application/json' \
  -d @/home/piet/vault/03-Agents/OpenClaw/design/claude-design-v3-2026-04-28/v3-atlas-bootstrap-task.json"
```

Erwartete Response: `200 OK` mit dem neuen Task-Object inkl. `id`. Notiere die
Task-ID für später (oder finde sie in Mission-Control unter Title `[V3 Sprint]
Atlas Master`).

## Was passiert dann

| Zeit | Phase | Was Atlas tut | Discord-Report |
|------|-------|---------------|----------------|
| T+0–60s | — | Atlas-Auto-Pickup-Cron pickt Master-Task | — |
| T+1min | Phase 0 | Liest 3 Vault-Files, /api/health, board-snapshot, git-status | "Phase 0 — Baseline complete" |
| T+2min...T+18min | Phase 1 | Erstellt 17 Slice-Tasks (1 pro Cycle = ~1/min) | nur 1× am Ende: "Phase 1 — All 17 slices created" |
| T+19min...T+8h | Phase 2+3 | Dispatcht eligible Slices an Workers (sre-expert, frontend-guru, etc.), monitort Receipts, marked done | 1× pro Dispatch + 1× pro Result. ~34 Reports. |
| T+8h..T+12h | Phase 4 | Aggregiert, schreibt Final-Report, PATCH master done | "Phase 4 — Sprint complete" mit Verdict GREEN/YELLOW/RED |

Total Discord-Reports erwartet: **~37 messages** im Channel
`1495737862522405088`. Konsolidiert, keine hourly heartbeats.

## Erwartete Sprint-Dauer

- 17 Slices, max 2 parallel via WIP-Limit
- ~30-90min pro Slice (Worker-Implementation + build + tests)
- → ~8-12h Wallclock, je nach paralleler Effizienz

Wenn du um 08:00 startest: ~16-20:00 Sprint-Close erwartbar.

## Notbremse (während Sprint läuft)

```bash
ssh homeserver "touch ~/.openclaw/HALT"
```

Atlas hält beim nächsten Cycle (binnen 60s) sauber an. State wird in
`v3-atlas-handover.json` und `gates.jsonl` gesichert. Resume später möglich
durch `rm ~/.openclaw/HALT` und einen nudge-Befehl.

Alternative via Discord (falls Listener-Cron läuft):
Post `!sprint halt` im Channel `1495737862522405088`.

## Wenn Atlas nach 5min keinen Phase-0-Report sendet

1. Check Master-Status: `ssh homeserver "curl -sS http://127.0.0.1:3000/api/tasks/<master-id>"`
2. Check Auto-Pickup-Cron: `ssh homeserver "tail -50 ~/.openclaw/logs/auto-pickup.log"`
3. Check Atlas-Worker: `ssh homeserver "systemctl --user status mission-control --no-pager"`
4. Check session-locks: `ssh homeserver "ls ~/.openclaw/locks/"`

## Was du am Ende des Tages siehst (Phase 4 Final-Report)

```
[V3 SPRINT] Phase: 4 | Slice: ALL
Status: GREEN | YELLOW | RED
Owner: atlas

Was: Sprint complete. <n>/17 slices PASS. Atlas-Autonomy verdict: <verdict>.
Evidence:
- master task: <id>
- final report: /home/piet/.openclaw/workspace/memory/05-learnings/v3-sprint-2026-04-29-final.md
- per-slice: F1=PASS, A0=PASS, A1=PASS, B=PASS, C=PASS, D=PASS, F2=PASS, E=PASS,
  F3=PASS, F=PASS, G=PASS-mock-only, H=PASS, I=PASS, V0=audit-attached,
  V1=PASS, V2=PASS, V3=PASS

Open operator actions:
- Slice G live-task validation (manual UI walk-through on /kanban-v3-preview)
- Review V0 autonomy audit findings: <path>

Next: review final report, decide on /kanban migration timeline
```

## Was du danach prüfen willst (post-sprint)

1. **Lens V0 audit:** `/home/piet/.openclaw/workspace/memory/05-learnings/v3-atlas-autonomy-audit-2026-04-29.md`
   → Atlas decision-log, dispatch-latencies, WIP-respect, defense-cron-fires,
     Autonomy-Quality-Score (1-10)
2. **Final Report:** `/home/piet/.openclaw/workspace/memory/05-learnings/v3-sprint-2026-04-29-final.md`
3. **/kanban-v3-preview** im Browser: visual walk-through of V3 layout
4. **/kanban (legacy)** im Browser: confirm unchanged
5. **/dashboard:** confirm unchanged
6. **Slice G:** manuell durch UI klicken: Confirm-Dialogs erscheinen, Mock-Tests grün

## Autonomy-Test-Verdict-Skala

- **GREEN:** alle 17 Slices PASS, 0 Eskalationen, alle Discord-Reports zeitgerecht.
  → Atlas ist production-ready für komplexe Multi-Slice-Sprints.
- **YELLOW:** 1-3 Slices PARTIAL/BLOCKED, Sprint completed mit non-fatal issues.
  → Atlas funktional, aber Verbesserungspotenzial in Edge-Cases.
- **RED:** Sprint blocked oder >3 Slices failed, manual recovery nötig.
  → Atlas-Autonomy braucht weitere Hardening-Sprints bevor Production.

Das ist dein eigentlicher Test-Output.

## Risiken (transparent)

1. **Atlas Phase 1 (Task-Creation):** Wenn Atlas POST /api/tasks-Sequenz nicht
   erfolgreich durchführt, ist Sprint dead. Mitigation: Idempotenz via
   decisionKey, bei Fehler retry pro Cycle.
2. **WIP-Race:** Worker pickup könnte überlappen wenn Atlas zu schnell dispatcht.
   Mitigation: existing R5 (1 decision/cycle) + auto-pickup-existing-pipeline.
3. **Worker-Build-Failures:** wenn `npm run build` failed bei einem Slice,
   Cascade möglich für dependent slices. Mitigation: Atlas markt FAIL, weiter
   mit independent slices.
4. **Slice G**: ist autonomous-night-mode mock-only. Live-Validation muss
   morgen Operator manuell machen. Acceptance kapselt das.

## Pre-Flight Check (heute Abend, optional)

Optional: 5min check ob Bootstrap-File korrekt liegt:

```bash
ssh homeserver "cat /home/piet/vault/03-Agents/OpenClaw/design/claude-design-v3-2026-04-28/v3-atlas-bootstrap-task.json | jq ."
ssh homeserver "ls -la /home/piet/vault/03-Agents/OpenClaw/design/claude-design-v3-2026-04-28/v3-atlas-mission.md"
```

Beide sollten existieren und parsen. Wenn ja: morgens nur den Trigger-Befehl
oben ausführen. Sonst nichts mehr nötig.
