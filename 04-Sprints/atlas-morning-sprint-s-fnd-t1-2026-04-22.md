---
title: Atlas Morning-Sprint S-FND T1 Pydantic Deploy
created: 2026-04-21 (für 2026-04-22 morning execution)
trigger-phrase: "Atlas — Morning-Sprint: S-FND T1 Pydantic SprintOutcome Schema Deploy."
scope: S-FND T1 ONLY (Single-Task Sprint)
owner: Atlas (orchestration) → Forge (execution)
depends-on: [Lens T0 APPROVE, S-GOV T4 3h-Observation green, /api/health ok]
estimated-duration: ~2h autonomous (Forge)
operator-presence-required: nein (nach GO-Signal)
---

# Atlas Morning-Sprint — S-FND T1 Pydantic SprintOutcome Schema Deploy

## Trigger-Phrase (copy-paste an Atlas)

```
Atlas — Morning-Sprint: S-FND T1 Pydantic SprintOutcome Schema Deploy.
```

Atlas lädt dann diesen Plan und führt die Morning-Check-Sequenz aus, dann Dispatch.

---

## Morning-Check (Atlas macht das automatisch, <1 Min)

Atlas verifiziert **3 Gates** bevor Dispatch:

```bash
# Gate 1: Lens T0 Re-Review APPROVED?
# Check Discord 1495737862522405088 für neueste Lens-Response
# Alternativ: /api/tasks/<lens-task-id>/status grep

# Gate 2: S-GOV T4 3h-Observation grün?
ssh homeserver "tail -30 /home/piet/.openclaw/workspace/logs/memory-orchestrator-hourly.log | grep qmd-update"
# Erwartet: 3+ consecutive 'rc=0', 0× 'rc=1' in den letzten 3h

# Gate 3: /api/health = ok?
ssh homeserver "curl -fsS http://127.0.0.1:3000/api/health | jq .status"
# Erwartet: "ok"
```

**Wenn alle 3 grün → Dispatch unten.**
**Wenn nicht alle grün → STOP, Operator-Ping mit Report welches Gate rot.**

---

## Dispatch an Forge

```
Forge — Execute S-FND T1 Pydantic SprintOutcome Schema Deploy.

READ-FIRST:
- /home/piet/vault/04-Sprints/s-fnd-2026-04-22.md (T1 section)
- /home/piet/vault/03-Agents/schemas/sprint_outcome.py (Template, Pydantic v2)
- /home/piet/vault/03-Agents/schemas/fixtures_valid.json (10 cases)
- /home/piet/vault/03-Agents/schemas/fixtures_invalid.json (10 cases)
- /home/piet/vault/03-Agents/codex-future-plan-protocol.md (Scope-Lock)

AUFTRAG:

1. Deploy Template nach MC-Backend:
   - Target-Pfad wählen in /home/piet/.openclaw/workspace/mission-control/src/
   - Empfehlung: src/schemas/sprint_outcome.py oder src/lib/schemas/sprint_outcome.py
   - Backup bei existierenden Files mit .bak-pre-sfnd-t1 Suffix
   - Adapt imports an MC-Stack falls nötig

2. Fixture-Tests:
   - 10 valid Fixtures müssen accept (exit 0, alle Felder validiert)
   - 10 invalid Fixtures müssen reject (mit passendem Error)
   - Run via MC-Test-Harness (pytest oder node test runner je nach Stack)

3. JSON-Schema-Export:
   python -c "from schemas.sprint_outcome import SprintOutcome; import json; print(json.dumps(SprintOutcome.model_json_schema(), indent=2))" > sprint_outcome.schema.json

4. p95-Latency-Benchmark:
   - 100 Iterations model_validate() mit realistischem Payload
   - p95 messen, Target < 5ms
   - Als Comment im Commit-Message dokumentieren

5. Feature-Flag OUTCOME_SCHEMA_V1_ENABLED=0 default setzen:
   - In MC config oder .env
   - Schema ist passive bis Folge-Sprints einschalten
   - Kein Consumer-Wiring an worker-terminal-callback.ts

6. 1 Commit im MC-Repo:
   Message: "feat(s-fnd-t1): SprintOutcome schema v1 + fixtures + JSON-schema export"
   Body: Include DoD-Checklist + p95-Benchmark-Wert

ANTI-GOALS (hart):
- KEIN Consumer-Wiring (worker-terminal-callback.ts unangetastet)
- KEINE breaking API-Changes
- KEIN Schema-Change an existierenden Contracts
- Feature-Flag bleibt default OFF
- KEIN S-FND T2 / T3 / T4
- KEIN anderer Sprint

DoD:
- 10/10 valid Fixtures: 100% accept
- 10/10 invalid Fixtures: 100% reject mit korrektem Error-Type
- p95-Latency < 5ms dokumentiert
- JSON-Schema .schema.json committed
- Smoke-Test `python sprint_outcome.py` oder entsprechender MC-Test exit 0
- Feature-Flag-Default 0 verifiziert (keine Consumer-Activation)

REPORT (alle via Discord 1495737862522405088):
- Deploy-Start: "🏗️ S-FND T1: deployed to <path>"
- After Tests: "✅ S-FND T1: 10/10 valid + 10/10 invalid pass, p95 <Xms"
- After Commit: "✅ S-FND T1 DONE: <commit-sha>, ready for S-RPT T2 consumer-wiring"
- Bei Blocker: "🔴 S-FND T1 blocked: <reason + evidence>"

ABORT-TRIGGER:
- Fixture-Tests red → revert .bak-pre-sfnd-t1, Operator-Ping
- p95 > 5ms → Operator-Ping (Pydantic-Version oder MC-Python-Version prüfen)
- Scope-Creep (Versuchung T2/T3/T4 mitzunehmen) → STOP + Report
- MC-Tests red durch Deploy → revert Commit, Operator-Ping

Status: Execute sofort bei diesem Dispatch.
```

---

## Expected Timeline

| Phase | Duration | Trigger |
|---|---|---|
| Morning-Check | <1 Min | Atlas startet automatisch |
| GO-Signal | <1 Min | Atlas bestätigt Ready |
| Deploy + Tests | ~60 Min | Forge autonomous |
| Benchmark + JSON-Schema | ~30 Min | Forge autonomous |
| Commit + Report | ~15 Min | Forge → Atlas → Discord |
| **Total** | **~2h** | kein Operator-Input nach GO |

## Wenn S-FND T1 done → Nächste Schritte (nicht Teil dieses Sprints)

- S-RPT T2 kann consumer-wiring starten (nutzt dieses Schema)
- S-RELIAB-P1 F4 Signed Receipt-Chain kann Schema als Basis nutzen
- S-GOV T10 OTEL kann Schema für structured spans nutzen

**Diese Follow-ups NICHT heute morgen starten** — abends wenn Du zuhause bist.

---

## Abort/Rollback-Plan

Falls T1 rot:

```bash
# Revert deploy
ssh homeserver "cd /home/piet/.openclaw/workspace/mission-control/src/schemas && mv sprint_outcome.py.bak-pre-sfnd-t1 sprint_outcome.py"

# Revert commit (wenn schon committed)
ssh homeserver "cd /home/piet/.openclaw/workspace/mission-control && git revert HEAD --no-edit"

# MC-Service restart (nur wenn nötig)
ssh homeserver "systemctl --user restart mission-control"
```

## Source-References

- Template: `/home/piet/vault/03-Agents/schemas/sprint_outcome.py` (Claude Code Prototype 2026-04-22)
- Plan: `/home/piet/vault/04-Sprints/s-fnd-2026-04-22.md`
- Protocol: `/home/piet/vault/03-Agents/codex-future-plan-protocol.md`
- End-of-Day-Context: `/home/piet/vault/03-Agents/end-of-day-2026-04-21.md`
