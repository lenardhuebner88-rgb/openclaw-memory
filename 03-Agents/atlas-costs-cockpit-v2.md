---
title: Mission Control Costs Cockpit v2 — Operator-Level Financial Control
version: 1.0
status: pilot-ready
owner: Principal Product-System Architect
created: 2026-04-17
depends_on: atlas-board-operator-cockpit.md, atlas-session-memory-operating-model.md, incident_gateway_oom_2026-04-17.md
multi_agent: true
---

# Costs-Tab v2 — vom Donut-Dashboard zum Operator-Finanzcockpit

Umfassende Aufwertung des Costs-Tabs im Mission Control Board. Alle sechs Agents (Atlas, Forge, Pixel, Lens, James, Spark) sind beteiligt.

## EXECUTIVE JUDGMENT

Der heutige Costs-Tab zeigt **Daten**, aber kein **Urteil**. Live-Befund 2026-04-17 16:25 UTC: $76.95 heute verbrannt (3h-Autonomous-Run), Budget-Status `red`, MiniMax-Subscription **268 % überzogen** (`statusLabel=CRITICAL`, `usedCost=$71.09 / monthlyBudget=$40`) — aber **der Operator hat das nicht gemerkt**. Es gibt einen Alert-Text als String im API-Response, keinen Discord-Push, kein sichtbares Eskalations-Muster.

Das Grundproblem ist nicht fehlende Daten. Die vorhandene Cost-Pipeline (30 Tage Timeline, Donut pro Modell, Subscription-Status, detailRows mit Session-Attribution) ist **sehr gut**. Was fehlt:

1. **Attribution**: Kosten hängen an Session-Files, nicht an Tasks oder Plänen. Ich kann nicht sagen "Pack 3 hat $X gekostet".
2. **Semantik**: `budget.todayPct=25.6 %` bei $76.95/$3-Tagesbudget = rechnerisch 2565 %. Die Logik ist offensichtlich kaputt oder missdeutet.
3. **Aktion**: Ein `🔴 CRITICAL`-Status ohne Eskalations-Pfad ist Kosmetik.
4. **Vergleichbarkeit**: Kein Benchmark gegen Provider-Preise, kein "Cost per Task", kein "Token-Efficiency-Ratio".
5. **Operator-Erfassung**: 11+ Felder im API-Response — der Operator bräuchte 3 Signale in 5s.

Der Tab hat alle Rohzutaten, aber keine Komposition. Diese Transformation ist ein perfekter Multi-Agent-Test: Lens leitet fachlich (Kosten-Audit ist ihre Domäne), Forge baut Backend, Pixel UI, James liefert Provider-Benchmarks, Spark UX-Ideen, Atlas orchestriert.

## BILLING MODEL AWARENESS (kritisch — Plan-Anpassung 2026-04-17)

Der Operator nutzt **mehrere Abrechnungsmodi parallel**, die fundamentale Cockpit-Darstellungen bedingen. Monolithisches $-Dashboard ist inadäquat:

### Mode 1 — Flatrate (OAuth Pro-Abo): GPT-5.4
- Operator zahlt fixen Monatsbetrag, OAuth-Login, **keine echten Token-Kosten** pro Request.
- Heutiger API-Response zeigt $63.72 für gpt-5.4 — das ist **implied/theoretical cost**, nicht was tatsächlich bezahlt wurde.
- Primäre Metrik: **Usage-Utilization gegen Soft-Caps** (Messages/Tag, Sessions/Hour, Token-Cap/Session falls existent) — NICHT $.
- Secondary: **Implied-Saving** ($ das pay-per-use gekostet hätte → Rechtfertigung des Abos).
- Risiko-Metrik: **Cap-Exhaustion-Forecast** ("2h bis Message-Cap bei aktuellem Tempo").
- UI-Label: `FLATRATE`, Farbakzent grün solange <80% Cap.

### Mode 2 — Prepaid-Pool: MiniMax M2.7 40 €/Monat
- Operator kauft monatliches Token-Guthaben (40 €), Pool shrinkt, Reset am Monatsersten.
- Heutiger Alert `268 %` = Pool um 168 % über-ausgenutzt (oder: auf Token-Basis anders gerechnet — James muss Semantik klären).
- Primäre Metrik: **Pool-Rest in € + Exhaust-Forecast-Datum**, NICHT $/Tag.
- Risiko-Metrik: **"Pool leer in N Tagen bei aktuellem Burn"**.
- Rate-Limit separat: 20M TPM (aus Alert-Text) — eigener Heartbeat.
- UI-Label: `PREPAID`, gelb bei <30 % Rest, rot bei <5 %.

### Mode 3 — Pay-per-Use: Rest (z.B. openrouter/auto, Gemini-Embedding)
- Klassisches $/Tag, $/Monat, Budget-Alert.
- Heutiger Anteil ist klein (<$0.10).
- UI-Label: `PAY-PER-USE`.

### Mixed-Mode-Composite
Zone-A Feld 4 zeigt **tatsächlich zu zahlendes $** heute:
```
effective_today = flatrate_monthly_fee/30  +  prepaid_pool_used_today_in_eur  +  payperuse_today
```
NICHT die Summe der Implied-Costs. Das `$76.95 today` im aktuellen Response ist **irreführend** — in Wirklichkeit hat der Operator heute vielleicht `$22/30 + $2.33 + $0.10 ≈ $3.15` real bezahlt.

### Konfiguration — neue Datei `config/billing-modes.yaml`
```yaml
providers:
  openai-codex:
    mode: flatrate
    subscription: "GPT-5.4 Pro (OAuth)"
    monthly_fee_eur: 22        # zu validieren — James Research
    billing_cycle_day: 1
    soft_limits:
      messages_per_day: 500    # zu recherchieren
      sessions_per_hour: 10    # zu recherchieren
      token_cap_per_session: null
    models: [gpt-5.4, gpt-5.4-mini, gpt-5.3-codex, gpt-5.3-codex-spark]
  minimax:
    mode: prepaid
    pool_monthly_eur: 40
    reset_day: 1
    rate_limit_tpm: 20000000   # 20M Tokens/Min aus Alert-Text
    models: [MiniMax-M2.7, MiniMax-M2.7-highspeed]
  openrouter:
    mode: pay-per-use
    daily_budget_eur: 1
    models: [openrouter/auto]
  gemini:
    mode: pay-per-use
    daily_budget_eur: 0.5
    models: [gemini-embedding-001, google/gemini-2.0-flash-001]
```
Diese Datei wird von Lens (Policy) + James (Research) gemeinsam in Phase 1 final gemacht.

## CURRENT STATE ANALYSIS

Live-API-Stichprobe `GET /api/costs` 2026-04-17 16:25 UTC:

### Was vorhanden ist (+)
- **Overview**: today, month, projected-month-end, flatrate-savings (gut aggregiert).
- **Donut**: 5 Modelle mit Cost-Breakdown (gpt-5.4 $63.72 = 83 %, dominant).
- **Timeline**: 30 Tage, provider-aufgespalten (claude/gemini/gpt/other).
- **detailRows**: Session-granular mit inputTokens/outputTokens/cost/source-file.
- **subscriptionStatus**: pro Provider (minimax, openai-codex, etc.) mit usedCost/usedPct/tone/alert-Text.
- **anomalies + anomalyStats + confidence**: existieren als Felder (nicht tief inspiziert).
- **freshness + telemetry**: Aktualitäts-Indikatoren.
- **gpt54Status + flatrateTasks**: Spezial-Status für flatrate-Preismodelle.

### Was schwach ist (-)
1. **Budget-Logik inkonsistent**: `dailyBudget=3`, `todayPct=25.65 %`, actual today `$76.95` → Prozent stimmt nicht. Entweder wird `todayPct` gegen Monats-Budget gerechnet (30 × $3 = $90, 76.95/90 = 85.5 % — stimmt auch nicht), oder die Logik ist ein Altlast-Bug.
2. **Subscription-Alert ist passiv**: MiniMax `268 %` liefert nur einen emoji-String (`🔴 CRITICAL`) — kein Webhook-Fire, keine persistente board-event, keine Rate-Limit-Drosselung.
3. **Keine Task/Plan-Attribution**: detailRows referenziert `agents/main/sessions/<id>.jsonl` — aber nicht welche Task-ID, welcher Plan, welcher Pack. Ich kann nicht fragen "was hat Worker-Hardening Pack 3 gekostet".
4. **Timeline ist nur Total**: `date/total/claude/gemini/gpt/other` — kein per-Agent-Drilldown, kein per-Session-Drilldown, keine Hover-Details.
5. **Projections unrealistisch**: projected-month-end $135.79 bei today $76.95 am 17. → extrapoliert nicht korrekt (müsste mindestens $135 × 30/17 = ~$240 sein).
6. **Keine Token-Effizienz-Metrik**: Cost per Task, Tokens pro $, Cache-Hit-Ratio (heute sieht man in Atlas-Turns 985k cache-reads vs 30M input — das ist nicht im Cockpit).
7. **Keine Agent-Role-Anomalie**: Warum kostet `main` $61.88 in einer Session? Das ist der heutige Multi-Pack-Delegation-Turn, aber das Board sagt nur "Session $61.88".
8. **Fehlende Operator-Aktion**: bei `red`-Status — kein Button "Model-Fallback aktivieren" oder "Budget erhöhen (audit)".

### Was fehlt ganz (x)
- Per-Agent-Breakdown (nur per-Model heute)
- Per-Plan / Per-Pack-Cost-Attribution
- Burn-Rate-Anzeige (h/Tag)
- Projected-Exhaust-Time bei aktuellem Tempo
- Provider-Benchmark-Overlay (wie teuer ist $X bei Konkurrenz?)
- Cost-Story-Feature (welche Tasks haben die meisten Kosten erzeugt, warum?)
- Discord-Alert-Auslöser bei Budget-Breach
- Flatrate-vs-Pay-per-use-Switching-Empfehlung
- Kosten-pro-Erfolg (z.B. $/done-Task vs $/failed-Task)

## TARGET COCKPIT MODEL

Vier-Zonen-Layout à la `atlas-board-operator-cockpit.md`, aber Kosten-spezifisch:

```
┌────────────────────────────────────────────────────────────────┐
│ ZONE A — FINANCIAL HEARTBEAT (4 Ampeln, 1 Zeile)              │
│ [●Today $77/$90]  [🔴Subscription: MiniMax 268%]               │
│ [⚠Burn: $26/h]    [●Projected EOM: $240]                       │
├────────────────────────────────────────────────────────────────┤
│ ZONE B — NEXT BEST ACTION (1 Satz + 1 Button)                  │
│ "MiniMax 268% über Budget — Fallback auf flatrate-gpt5.4?"     │
├────────────────────────────────────────────────────────────────┤
│ ZONE C — COST STORY (was hat gerade Geld verbrannt)            │
│ Top-3 Sessions heute (Click → Task/Plan-Attribution):          │
│  1. [Atlas 3h-Autonomous-Run] $61.88 — 4 Packs delegiert       │
│  2. [Forge Pack 3 Build] $6.23 — 3 Rebuilds                    │
│  3. [Lens Baseline-Messung] $0.01 — 1 Task                     │
├────────────────────────────────────────────────────────────────┤
│ ZONE D — AGENT-COST-LADDER (6 Balken, $ + Token-Effizienz)     │
│ Atlas  ████████  $62 | 30M in / 81k out | cache 985k (32x)     │
│ Forge  ██        $8.4 | ...                                     │
│ Pixel  ▁        $0    | idle                                    │
└────────────────────────────────────────────────────────────────┘
```

**Kern-Invarianten:**
- Jede Zahl ist klickbar → Drilldown auf Detail-Panel.
- Alle Ampeln haben eskalations-Pfad (rot → Discord-Alert via Webhook).
- Cost-Story **attribuiert auf Task + Plan + Pack**, nicht nur Session.
- Agent-Ladder zeigt **Display-Aliases** (Atlas/Forge/…), nicht Runtime-IDs.

## INFORMATION ARCHITECTURE

### Main View (Costs-Tab Landing)
Zone A + B + C + D, 10-Sekunden-Erfassung. Alles Wichtige above the fold.

### Detail Panels (Click-Drilldown)
- **Session-Panel**: gleiche Session aufgeschlüsselt auf Task-IDs und Plan-IDs (via source-file + board-event-log-Match).
- **Agent-Panel**: 30-Tage-Verlauf des Agent, Token-Efficiency-Trend, Cache-Hit-Ratio, typische Tasks.
- **Provider-Panel**: Subscription-Status, flatrate-Usage, Budget-Restmenge, Fallback-Ziel.
- **Plan-Panel** (neu!): Pro Vault-Plan die Summen-Kosten aller zugehörigen Tasks (z.B. "Worker-Hardening gesamt bisher: $8.42").

### Archive / Historical
Zeitraum-Filter (7d/30d/90d), Export als CSV, Monats-Vergleich.

## PRIMARY OPERATOR SIGNALS

Genau vier Signale decken 95 % der finanziellen Operator-Fragen:

1. **Today-Budget-Heartbeat** (Zone A, Feld 1). Tagesbudget konfigurierbar, Ampel rot bei >100 %.
2. **Subscription-Overruns** (Zone A, Feld 2). Aktuell live: MiniMax 268 % — ist rot, aber passiv. Neu: trigger Webhook.
3. **Burn-Rate** (Zone A, Feld 3). $ pro Stunde in letzten 60min. Eskaliert wenn >3 × Tagesdurchschnitt.
4. **Next Best Action** (Zone B). Regel-getrieben aus den drei Heartbeats:

| Prio | Bedingung | NBA |
|---|---|---|
| 1 | Subscription >200 % | "Provider X überzogen — auf flatrate Y umschalten?" |
| 2 | Today >150 % Tagesbudget | "Tagesbudget gerissen — Session-Cap aktivieren?" |
| 3 | Burn-Rate >10× Durchschnitt | "Burn-Rate anomalie — Agent X läuft heiß" |
| 4 | Projected-EOM >2× Monatsbudget | "Projektion kritisch — Plan-Runner pausieren?" |
| 5 | Alles grün | "$X spent today, $Y/h avg, no anomalies" |

## IMPLEMENTATION PACK (8 Packs, Multi-Agent)

Jedes Pack hat einen **Lead-Agent** und optionale Mithelfer. Reihenfolge ist prio-geordnet.

### Pack 1 — Cost-Attribution-Foundation (Backend)
- **Lead: Forge** | Unterstützung: Lens (Attribution-Regeln)
- Neue Felder in `/api/costs/detailRows`: `taskId`, `planId`, `packId` wenn aus Session-File ableitbar (via board-event-log-Match).
- Neuer Endpoint: `GET /api/costs/by-task/<task-id>` → aggregierte Kosten.
- Neuer Endpoint: `GET /api/costs/by-plan/<plan-id>` → Sum pro Plan.
- DB-seitig: keine Änderung, Ableitung zur Query-Time aus bestehenden Quellen.

### Pack 2 — Budget-Engine **Multi-Mode** mit Alerts (Backend)
- **Lead: Lens** (definiert Policy pro Mode) | **Exec: Forge**
- Konfig: `config/billing-modes.yaml` (siehe BILLING MODEL AWARENESS oben).
- Engine erkennt Mode pro Provider und evaluiert **Mode-spezifische** Schwellen:
  - `flatrate`: `soft_limit_used_pct > 80` = warn, `> 95` = critical
  - `prepaid`: `pool_remaining_pct < 30` = warn, `< 10` = critical, `< 5` = emergency
  - `pay-per-use`: klassisch `daily/monthly` vs actual
- Endpoint `GET /api/costs/budget-status` → Array mit allen aktiven Limits + Mode + pct + tone + eta.
- Policy-Events ins board-event-log: `budget-breach`, `budget-warn`, `pool-low`, `flatrate-cap-approach`.

### Pack 3 — Burn-Rate + Projection **per Billing-Mode** (Backend)
- **Lead: Forge** | Unterstützung: Lens (Formel-Review)
- Fix: `projectedMonthEnd` korrekte Extrapolation für pay-per-use Anteil.
- **Flatrate**: Burn-Rate = `messages_per_hour` + `sessions_per_hour`, Projection = "Cap erreicht in X h" wenn Rate anhält.
- **Prepaid**: Burn-Rate = `pool_eur_burned_per_day_avg_7d`, Projection = Tage bis Pool leer + Vergleich zu Reset-Datum.
- **Pay-per-use**: klassisch `$/h`, Projection bis Budget.
- Zusätzlich: `implied_pay_per_use_cost_today` pro Provider (damit Flatrate-Saving sichtbar).

### Pack 4 — Anomalie-Detection-v2 **Mode-Aware** (Backend)
- **Lead: Lens** (definiert Thresholds pro Mode) | **Exec: Forge**
- Klassisch:
  - Session-Cost >10× Median (nur pay-per-use relevant)
  - Provider-Switch mid-session
  - Cache-Miss >90 % bei wiederholter Session
  - Output-zu-Input-Ratio <1 % (zu viel Context, zu wenig Ergebnis)
- **Flatrate-spezifisch**:
  - `flatrate-cap-approaching`: >80 % Messages-per-Day-Cap
  - `flatrate-rate-spike`: Messages/h spike >5× 7d-Baseline
- **Prepaid-spezifisch**:
  - `prepaid-burn-above-baseline`: täglicher Pool-Burn >2× 7d-Schnitt
  - `prepaid-exhaust-before-reset`: Pool-Forecast vor Reset-Datum leer
  - `prepaid-rate-limit-hit`: 429-Responses vom Provider wegen TPM-Cap
- **Billing-Mismatch**:
  - Ein Request geht an ein Model das im falschen Mode konfiguriert ist
- Alle Anomalien → board-event + Discord-Alert via Pack 5.

### Pack 5 — Discord-Alert-Kette (Infra)
- **Lead: Forge** | Unterstützung: Atlas (Alert-Copy-Review)
- Webhook-Integration wiederverwendet `AUTO_PICKUP_WEBHOOK_URL` oder eigener `COSTS_ALERT_WEBHOOK_URL`.
- Rate-Limit: 1 Alert pro Anomaly-Typ pro 15min.
- Format: `🚨 **cost-alert subscription-overrun** — MiniMax 268% ($71/$40) — consider flatrate switch`.

### Pack 6 — UI-Redesign Zone A/B/C/D **Billing-Mode-aware** (Frontend)
- **Lead: Pixel** | Unterstützung: Spark (UX-Story-Feature), Atlas (NBA-Wording)
- Komponenten: `<CostHeartbeat/>`, `<CostNextAction/>`, `<CostStory/>`, `<CostAgentLadder/>`.
- **Zone A Ampeln differenziert pro Mode**:
  - Flatrate-Ampel pro Provider: `"GPT-5.4 Pro (OAuth) — 210/500 msg heute · 42%"` + grüner Farbakzent bis 80%, orange bis 95%, rot >95%.
  - Prepaid-Ampel pro Provider: `"MiniMax — €11 / €40 Pool · 28% · Reset in 13d"` + gelb bei <30% Rest, rot <5%.
  - Pay-per-Use-Ampel (composite): `"Pay-per-use heute: $0.10 / $1.00 Budget"`.
  - Composite-Effective-$: `"Effektiv heute: Flatrate-Fee $0.73 + Prepaid-verbraucht $2.33 + PayPerUse $0.10 = $3.16"` — **prominent**, weil echter Geldfluss.
- **Implied-Cost-Overlay**: pro Session-Row in Zone C kleiner Text `"implied $62 (flatrate — saved)"` für Transparenz.
- **Zone D Agent-Ladder**: Pro Agent auch Badge für Mode des verwendeten Modells.
- Responsive Desktop-Primary, Mobile fallback auf Stack.
- Framer-motion Transitions bei Mode/Threshold-Wechsel.

### Pack 7 — Provider-Benchmark + **Billing-Mode-Research** (Research)
- **Lead: James** | Unterstützung: Lens (Validierung & Policy-Ableitung)
- **Scope erweitert um Billing-Modes** (2026-04-17 Update):
- **Teil 1 — Pricing-Tiers** (wie vorher): aktuelle $/1k-Tokens für alle Modelle in `openclaw.json`. Für flatrate-Provider dient das als **Implied-Cost-Referenz**, nicht als real-bezahlt.
- **Teil 2 — Flatrate Soft-Limits für OAuth-Pro-Abos** (NEU, kritisch):
  - Welche Messages/Tag-Soft-Caps gelten für GPT-5.4 via OpenAI-Codex-OAuth-Pro-Abo?
  - Welche Sessions/Stunde-Caps?
  - Token-Cap pro Session?
  - Was passiert beim Soft-Cap-Erreichen (Throttle, hard-block, fallback)?
  - Kosten des Abos (€/Monat)?
  - Quelle: OpenAI-Dokumentation, ChatGPT-Help-Center, Community-Threads, heutige Stichprobe aus eigener Nutzung.
- **Teil 3 — Prepaid-Pool-Semantik für MiniMax 40€-Plan** (NEU):
  - Wie genau wird der Pool gerechnet (Token-Anzahl, €-Äquivalent)?
  - Was bedeutet `20M TPM` aus dem heutigen Alert-Text?
  - Was passiert bei Pool-Exhaustion (429, Fallback, Pause, Auto-Recharge)?
  - Wann ist Reset-Datum (Monatsersten, Kaufdatum-Zyklus)?
  - Heutige Stichprobe: API meldet `used_cost=$71.09` bei `monthly_budget=40` → 268 %. Ist das Token-basiert gerechnet oder $-basiert? Disclosure notwendig.
- **Teil 4 — Mixed-Mode-Best-Practices** (NEU, kurz):
  - Wie stellen etablierte Tools (Cursor, Anthropic-Console, Datadog-seat-based) Flatrate + Prepaid + Pay-per-Use nebeneinander dar?
  - 2-3 Referenz-Screenshots oder Design-Pattern.
- **Outputs**:
  - `workspace/memory/invariants/provider-pricing.yaml` — Pricing-Tiers (min. 8 Modelle)
  - `workspace/memory/invariants/billing-modes-reference.yaml` — Soft-Caps + Pool-Semantik je Provider (final konfigurierbar für Pack 2)
  - Research-Report-Markdown mit Quellen-URLs
- Quartals-Refresh-Cron (Pricing kann sich ändern, soft-caps auch).
- **Validierungs-Protokoll**: Lens prüft alle Werte auf Plausibilität gegen heutige Stichprobe vor Übernahme in Config.

### Pack 8 — Cost-Story-Feature (UX-Innovation)
- **Lead: Spark** (Idee + UX-Prototyp) | **Exec: Pixel** | Unterstützung: Forge (Data-Provider)
- Feature: auf Klick einer Zeile in Zone C → Modal mit "Narrative": welche Tasks/Packs hat diese Session bearbeitet, welche Tools, wie viele Receipts, Retry-Count.
- Datenquelle: session-file.jsonl + board-event-log + task-resultSummaries.
- Ziel: Operator versteht in 15s **warum** $60 in einer Session verbrannt wurden — nicht nur dass.

## FILES / COMPONENTS

| Pack | Lead | Files |
|---|---|---|
| 1 | Forge | `src/app/api/costs/route.ts`, new: `src/app/api/costs/by-task/[id]/route.ts`, new: `src/app/api/costs/by-plan/[id]/route.ts`, new: `src/lib/cost-attribution.ts` |
| 2 | Lens+Forge | new: `config/budgets.yaml`, new: `src/app/api/costs/budget-status/route.ts`, new: `src/lib/budget-engine.ts` |
| 3 | Forge | edit: `src/lib/cost-projection.ts` (new), integriert in costs/route.ts |
| 4 | Lens+Forge | new: `src/lib/cost-anomaly-detector.ts` |
| 5 | Forge | new: `scripts/cost-alert-dispatcher.py` (oder MC-server-side), crontab |
| 6 | Pixel | new: `src/app/costs/components/cost-heartbeat.tsx`, `cost-next-action.tsx`, `cost-story.tsx`, `cost-agent-ladder.tsx`, edit: `src/app/costs/costs-client.tsx` |
| 7 | James | new: `workspace/memory/invariants/provider-pricing.yaml`, research-report-file |
| 8 | Spark+Pixel | new: `src/app/costs/components/cost-story-modal.tsx` |

Alle Edits mit `.bak-costs-v2-<pack>-2026-04-17`. Keine openclaw.json-Änderungen (R4 beachten).

## MULTI-AGENT-CHOREOGRAPHY

Dies ist der **erste Multi-Agent-Plan**. Alle sechs Rollen werden orchestriert:

| Agent | Rolle | Beteiligt an Packs |
|---|---|---|
| **Atlas (main)** | Orchestrator, Policy-Review, NBA-Wording | Alle (Delegation) |
| **Lens (efficiency-auditor)** | Fachlicher Lead für Kosten, Baseline, Thresholds | Pack 2, 3, 4, 7 |
| **Forge (sre-expert)** | Backend-Execution, Infra | Pack 1, 2, 3, 4, 5 |
| **Pixel (frontend-guru)** | UI-Execution | Pack 6, 8 |
| **James (james)** | Provider-Research, Benchmark-Kurationen | Pack 7 |
| **Spark (spark)** | UX-Innovation, Cost-Story-Konzept | Pack 8 |

**Delegation-Reihenfolge (Atlas als Dispatcher):**

```
Phase 1 (Baseline + Foundation):
  - Lens → Cost-Audit-Baseline (Task 1): liest 30-Tage-Timeline, identifiziert Top-Kosten-Treiber
  - James → Provider-Benchmark-Research (Pack 7, Task 2)

Phase 2 (Backend-Foundation):
  - Forge → Pack 1 (Attribution)
  - Forge → Pack 3 (Burn-Rate + Projection-Fix)
  - Forge + Lens → Pack 2 (Budget-Engine mit Policy von Lens)

Phase 3 (Intelligence + Alerts):
  - Forge + Lens → Pack 4 (Anomaly-Detector)
  - Forge → Pack 5 (Discord-Alerts)

Phase 4 (UI + UX):
  - Spark → Pack 8 Concept-Draft (UX-Prototyp als markdown + mockup)
  - Pixel → Pack 6 (Zone A/B/C/D-Komponenten)
  - Pixel + Spark → Pack 8 Implementation

Phase 5 (Integration + Go-Live):
  - Lens → After-Measurement gegen Baseline
  - Atlas → Gesamt-Review, NBA-Copy-Finalisierung
  - Operator → Smoke-Test 10-Sekunden-Erfassung
```

Jeder Agent liefert pro Task einen strukturierten resultSummary. Atlas sammelt, Lens reviewt gegen Metrics, Pack nächster Phase erst wenn Previous-Acceptance durch.

## RISKS

1. **Attribution-Gap**: Nicht alle Sessions haben saubere Task-/Plan-Links (Legacy-Sessions). Mitigation: `unattributed`-Bucket in UI, schrittweise Migration durch source-file-pattern-matching.
2. **Budget-Policy-Konflikt**: Lens' Thresholds könnten zu strikt sein → False-Positive-Alerts. Mitigation: 7-Tage-Kalibrierungs-Phase mit Warn-Only-Mode bevor Discord-Alerts live gehen.
3. **Provider-Pricing-Drift**: James' yaml wird stale. Mitigation: Quartals-Refresh-Cron + Age-Indicator im UI.
4. **Cost-Story-Overload**: Wenn Modal zu datengetrieben wird, wird Operator erschlagen. Mitigation: Spark macht UX-Prototyp VOR Pixel-Implementation, Lens prüft Signal-Relevanz.
5. **Rate-Limit Discord**: bei vielen Anomalien Flooding. Mitigation: Pack 5 Rate-Limit 15min pro Typ.
6. **Multi-Agent-Chaos**: 6 Agents gleichzeitig → Gateway-Last (siehe Incident 2026-04-17 16:11). Mitigation: Phasen seriell, innerhalb Phase max 2 parallel. MC-Watchdog aktiv (seit heute).
7. **Mutual-Waiting-Deadlock**: Pack 6 wartet auf Pack 1–5, Pack 8 wartet auf 6, falls einer hängt blockiert alles. Mitigation: Phasen-Gates mit Max-Zeit (72h pro Phase), sonst Operator-Eskalation.

## TEST PLAN

### Phase-Gate-Tests
Pro Phase ein Acceptance-Gate durch Lens:
- Phase 1: Baseline-Report vollständig, Benchmark-yaml validierbar.
- Phase 2: `GET /api/costs/by-task/<id>` liefert plausible Summen für 3 zufällige Task-IDs.
- Phase 3: Synthetic-Budget-Breach (Test-Task $5 in 1min) → Anomaly + Discord-Alert binnen 2min.
- Phase 4: 10-Sekunden-Test — Operator erkennt Budget-Status in ≤10s.
- Phase 5: End-to-End — gleichen heutigen 3h-Run (oder kleineres Beispiel) durchspielen, Story-Modal zeigt korrekte Pack-Attribution.

### Chaos-Test
Künstliches Szenario: MiniMax-Usage auf 400 %, alle anderen Provider auf 120 %, Tagesbudget bei 250 % → NBA muss Prio-1 rendern (Subscription-Overrun zuerst), Discord-Alert feuert 1× (Rate-Limit ok), Agent-Ladder zeigt roten Top-Spender.

## ROLLBACK

Pro Pack:
- Backend: `.bak-costs-v2-<pack>-*` restore, Deploy-Sequenz.
- UI: Pack 6 hat Feature-Flag `NEXT_PUBLIC_COSTS_COCKPIT_V2=0` → Fallback auf altes Dashboard.
- Discord-Alerts: `COSTS_ALERTS_ENABLED=0` in crontab-env.

Gesamt-Kill-Switch: `/api/costs` liefert bei Panic ein `{ degraded: true, cause }` payload, UI fällt auf "Summen-Only"-Mode zurück.

## RECOMMENDED EXECUTION AGENT SEQUENCING

Atlas als Gesamt-Dispatcher. Keine parallele Plan-Runner-Logik (nicht live, siehe `atlas-continuation-orchestrator.md`). Ablauf:

1. Operator triggert Atlas mit Gesamtplan-Referenz.
2. Atlas legt Phase-1-Tasks für Lens und James an (parallel).
3. Nach Abschluss Phase 1: Atlas delegiert Phase-2-Packs an Forge (ggf. sequenziell via Auto-Pickup-Concurrency=1).
4. Atlas triggert Pack-Pair-Teams: Forge+Lens für Pack 2, Pack 4.
5. Nach Phase-3-Acceptance durch Lens: Atlas triggert Spark (Pack 8 Concept), dann Pixel (Pack 6 + 8).
6. Lens misst nach Phase 5 gegen Baseline, Atlas moderiert Gesamt-Acceptance.

Gesamt-Kalenderdauer: ~7 Arbeitstage bei Paralleler Agent-Arbeit.

## ACCEPTANCE CRITERIA

Messbar gegen Baseline 2026-04-17 16:25 UTC. Pass = 9 von 12.

1. **10-Sekunden-Test**: Operator erkennt aus kaltem Cockpit korrekt (a) heutiges Budget-Status, (b) größter Kostentreiber heute, (c) Subscription-Overrun, (d) nächste Aktion. Pass: 4/4 in ≤10s bei 5 synthetischen Zuständen.
2. **Attribution-Coverage**: ≥90 % aller detailRows der letzten 30 Tage haben `taskId` oder `planId` zugeordnet. Unattributed-Bucket ≤10 %.
3. **Budget-Logik korrekt**: `todayPct` = `today / dailyBudget × 100`, keine Inkonsistenz.
4. **Projection realistisch**: `projectedMonthEnd` bei heutiger Stichprobe = today × (30/17) ± 10 %.
5. **Subscription-Overrun triggert Discord-Alert** binnen 2min nach Erkennung (heute: kein Alert bei 268 %).
6. **NBA-Regel-Trefferrate**: 20 synthetische Zustände → 19/20 korrekte Prio.
7. **Cost-Story-Modal** zeigt für `main`-Session heute die 4 delegierten Packs + Tokens + Dauer.
8. **Agent-Ladder-Genauigkeit**: manuelle Summen-Stichprobe pro Agent vs UI = 100 %.
9. **Provider-Benchmark-yaml** enthält alle 11 Modelle aus aktuellem `openclaw.json`.
10. **Keine Regression** im bestehenden `/api/costs`: existing Klienten brechen nicht.
11. **Happy-Path-Regression**: Auto-Pickup-Smoke-Suite weiter 10/10, Task-Lifecycle unberührt.
12. **Multi-Agent-Lieferfähigkeit**: alle 6 Agents haben mindestens einen Task-resultSummary mit `status=done` im End-Zustand.

Hard-Stop-Kriterien: #1 (10-Sek-Test) oder #11 (Regression).

**Zusätzliche Mode-spezifische Kriterien (pflicht):**
13. **Flatrate-Awareness**: Composite-Effective-$ in Zone A zeigt nicht Implied-Cost, sondern nur real-bezahlbaren Anteil. Demo: heutiger Wert ~$3-5 statt $77.
14. **Prepaid-Forecast-Korrektheit**: Pool-Exhaust-Forecast für MiniMax innerhalb ±10 % gegen manuelle Re-Rechnung.
15. **Implied-Saving sichtbar**: Flatrate-Saving-Zahl (was pay-per-use gekostet hätte) wird in UI prominent dargestellt, rechtfertigt das Abo.

---

## Umsetzungsreihenfolge (Phasen, prio-geordnet)

| Phase | Packs | Agents | Dauer |
|---|---|---|---|
| 1 Baseline + Research | Lens-Cost-Audit, Pack 7 | Lens, James | 2 Tage |
| 2 Backend-Foundation | 1, 3, 2 | Forge (Lead), Lens (Review Pack 2) | 2 Tage |
| 3 Intelligence + Alerts | 4, 5 | Forge (Lead), Lens (Thresholds) | 1 Tag |
| 4 UX + UI | 8-Concept, 6, 8-Impl | Spark, Pixel, Atlas (Wording) | 2 Tage |
| 5 Acceptance + Go-Live | Lens-Measurement, Atlas-Review | Lens, Atlas, Operator | 0.5 Tag |

Gesamt: ~7 Arbeitstage.

## Abhängigkeits-Karte

```
Pack 7 (James-Benchmark) ────┐
                              ├─▶ Pack 2 (Budget-Engine, Lens+Forge) ─┐
Pack 1 (Attribution, Forge) ─┤                                         │
Pack 3 (Burn-Rate, Forge) ───┘                                         │
                                                                       ▼
                              Pack 4 (Anomaly, Lens+Forge) ─▶ Pack 5 (Alerts, Forge)
                                                                       │
                                                                       ▼
                              Pack 8-Concept (Spark)  ─▶ Pack 6 (UI, Pixel) ─▶ Pack 8-Impl (Pixel+Spark)
                                                                       │
                                                                       ▼
                                                            Phase 5 (Acceptance, Lens+Atlas)
```

## Referenzen

- **Live-Analyse-Quelle**: `GET /api/costs` 2026-04-17 16:25 UTC (dokumentiert in CURRENT STATE ANALYSIS oben)
- **Parallele Pläne**: `atlas-board-operator-cockpit.md` (Pattern für Zone-A/B/C/D-Layout), `atlas-continuation-orchestrator.md` (könnte in Phase 2+ den Multi-Agent-Flow automatisieren)
- **Regeln**: `feedback_system_rules.md` — speziell R4 (openclaw.json unberührt), R7 (Build-Sequenz), R12 (nur Atlas schreibt LTM, also James' yaml muss Atlas-freigegeben sein), R15 (atomare Deploy)
- **System-State**: `system_state_2026-04-17.md` — aktuelle Infrastruktur (Auto-Pickup live, MC-Watchdog live, Gateway gehärtet)
