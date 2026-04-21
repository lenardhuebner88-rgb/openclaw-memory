---
title: Next-Level Plan 2026-04-19 — System auf Level 3
version: 1.0
status: ready-for-execution
created: 2026-04-18 abends
owner: Operator + Atlas
---

# Next-Level Plan 2026-04-19

Der Sprung von heute ("funktioniert autonom mit Self-Healing") zu morgen ("produktiv, transparent, skalierbar").

## Level-Definition

| Level | Definition | Status |
|---|---|---|
| L0 Manual | Operator triggert jeden Task einzeln via SSH | vor gestern |
| L1 Auto-Pickup | Dispatched Tasks werden autonom durch Worker abgearbeitet | gestern erreicht |
| **L2 Self-Healing** | System erkennt + fixt Ausfälle autonom (Watchdog, Integrity, Anomaly-Alert) | **heute erreicht** |
| L3 Self-Improving | Atlas + Lens + Self-Optimizer identifizieren + delegieren Verbesserungen autonom | **Ziel morgen** |
| L4 Multi-Plan-Parallel | Mehrere Pläne parallel mit DAG-Dependencies, Load-Balancing | Monat 2+ |
| L5 Autonomous-Scaling | System erkennt Kapazitäts-Bottlenecks + skaliert selbst | Monat 3+ |

## Morgen-Mission: L3 erreichen

Drei Foundation-Säulen die morgen stehen müssen:

### Säule 1 — Plan-Runner live (wirkliche Kontinuität)
- Pack B Seed-Konverter (Vault-Pläne → YAML-State)
- Pack E Cron-Registrierung mit `DRY_RUN=0` (erst nach 24h sauberem Dry-Run)
- Pack F Retry-Eskalation
- **Impact**: Atlas-Plan-Verfolgung automatisch, Operator als CEO-only

### Säule 2 — Observability produktiv (Transparenz)
- Board-Cockpit Phase 2 Navigation-Refactor (13→7 Tabs, James-Patterns liegen bereit)
- Board-Cockpit Zone D Agent-Ladder
- Mobile-UI-Refactor (Spark-Audit liegt bereit)
- Playwright-Smoke-Tests für kritische Screens schreiben
- **Impact**: Operator sieht Zustand in 10 Sekunden auf allen Devices

### Säule 3 — Reliability-Tightening (letzte 3 Schwachstellen)
- WK-18 Config-Live-Reload (worker-monitor etc. laden neue Werte ohne Cron-Restart)
- WK-19 Build-Batching (Debounce bei multiplen TS-Changes)
- WK-21 Artefakte-Work-but-No-Receipt (Agent-Prompt-Standard verschärfen)
- **Impact**: keine halb-erfolgreichen Tasks mehr, kein manueller Restart

## Phasen-Plan (~8h über den Tag verteilt)

### Phase 1 — Morning Start (08:00-09:30, Atlas-Self + Forge)
**Ziel**: Self-Optimizer-Freigabe-Review + Foundation

1. **08:00** — Atlas-Heartbeat bootstrap aus heute-Evening-Report
2. **08:30** — Self-Optimizer-Review nach 24h Dry-Run. Wenn 0 False-Positives → **Live-Schaltung** `SELF_OPT_DRY_RUN=0`. Wenn False-Positives → Welle-von-Regel-Schärfung.
3. **09:00** — Forge Plan-Runner **Pack B Seed-Konverter** (Vault-Pläne → YAML-State). 1-2h.

### Phase 2 — Reliability-Tightening (09:30-11:30, Forge)
4. **09:30** — Forge **WK-18 Config-Live-Reload** (worker-monitor + auto-pickup re-read config pro cycle). 1h.
5. **10:30** — Forge **WK-21 Receipt-Pattern-Enforce** (Agent-Prompt-Template mandatory `accepted` → `result` als Pflicht, Cancel ohne Receipt = Finding). 1h.
6. **11:00** — Forge **Plan-Runner Pack E Cron-Registrierung** + **Pack F Retry-Eskalation**. 1h.

### Phase 3 — UI-Refactor (10:30-15:00 parallel, Pixel + Spark + James)
7. **10:30** — James **Navigation-Pattern-Review** (bestehender Report liegt, 15min Review durch Atlas).
8. **11:00** — Pixel **Phase 2 Navigation-Refactor** 13→7 Tabs. 4h. Nutzt James-Patterns als Input.
9. **13:00** — Spark **Overview-Hero Zone-D UX-Concept** (Agent-Ladder). 30min.
10. **13:30** — Pixel **Zone D Implementation** (Agent-Ladder in Overview-Hero). 1h.
11. **14:30** — Pixel **Mobile-UI-Refactor** (aus Spark-Audit heute). 2h.

### Phase 4 — Worker-Hardening + Testing (11:30-15:00 Forge)
12. **12:00** — Forge **Worker-Hardening Pack 2 Receipt-Sequence** (accepted → progress → result enforcement). 1h.
13. **13:00** — Forge **Worker-Hardening Pack 4 Dispatch-Idempotency** (dispatchToken). 1h.
14. **14:00** — Forge **Worker-Hardening Pack 8 Retry-Single-Path**. 1h.
15. **15:00** — Forge **James Bootstrap-Audit** (MCP-Workspace-Setup, Root-Cause). 2h.

### Phase 5 — Lens-Continuous-Improvement (13:00-14:00)
16. Lens **Daily Cost-Report-Cron** (täglich morgens 07:00, Report in #daily-reports Discord). Setup durch Forge, Content-Logik durch Lens.

### Phase 6 — End-Of-Day (15:00-16:00)
17. **15:00** — Health-Check + Script-Integrity + Self-Optimizer-Live-Status
18. **15:30** — End-Report mit L3-Bestätigung oder Gaps-Liste
19. **16:00** — Memory-Update

## Acceptance Criteria für L3

Pass wenn 8 von 10 erfüllt:

1. Self-Optimizer läuft mit `DRY_RUN=0`, hat erste echte Action-Suggestion autonom durch Atlas getriggert
2. Plan-Runner hat einen Vault-Plan-Step autonom advanced (Step-done erkannt → nächster-step dispatched)
3. Board-Cockpit hat 7 Tabs (statt 13), Navigation konsolidiert
4. Mobile-UI hat 2 der 3 Spark-Empfehlungen umgesetzt
5. Playwright-Smoke-Tests für Overview + Costs + Task-Detail, alle grün
6. WK-18 Config-Live-Reload wirkt (Forge testet mit `kill -HUP worker-monitor`)
7. WK-21 Receipt-Pattern: 0 Artefakte-ohne-Receipt in 24h
8. Agent-Ladder live in Overview-Hero
9. Health ist `ok` ohne kritische Cost-Anomalies (MiniMax-Pool-Reset abgewartet oder Downgrade angestoßen)
10. Keine Crisis-Interventions vom Operator nötig

## Recommended Agents

| Agent | Morgen-Haupt-Rolle |
|---|---|
| Atlas | Orchestrator + Self-Review + Pack-C-Prompts pflegen |
| Forge | Reliability-Ops: WK-18/19/21 + Plan-Runner B/E/F + WH-Packs 2/4/8 + James-Bootstrap-Audit |
| Pixel | UI-Refactor Phase 2 + Zone D + Mobile |
| Lens | Daily-Cost-Report-Setup + weekly-audit continuous |
| Spark | Zone-D UX-Concept + Mobile-Design-Review |
| James | Navigation-Patterns-Review-Support (bestehender Report) |

## Risks

1. **Plan-Runner live ohne saubere Dry-Run-Phase** → Runaway-Trigger. Mitigation: nur nach 24h Dry-Run-Clean.
2. **Pixel überlastet** mit Phase 2 + Zone D + Mobile parallel. Mitigation: sequenziell, nicht parallel für UI-Packs.
3. **WK-18 Config-Live-Reload könnte Race-Conditions erzeugen** wenn während Cycle-Run. Mitigation: atomic-read-at-start.
4. **James-Bootstrap-Audit ist Research-heavy** → Wiederholung des Timeout-Problems. Mitigation: Forge macht es, nicht James.

## Rollback

Pro Task `.bak-next-level-2026-04-19`. Feature-Flags wo möglich. MC-Rebuild nur nach Verify. Keine destructive Ops.

## Abend-Deliverable

Gegen 16:00 UTC End-Report mit:
- L3-Acceptance-Check
- Neue Schwachstellen des Tages
- Empfehlung L4-Zeitpunkt (wahrscheinlich in 1-2 Wochen)
