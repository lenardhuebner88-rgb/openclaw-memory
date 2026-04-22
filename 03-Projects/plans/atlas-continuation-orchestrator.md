---
title: Atlas Continuation Orchestrator — Plan-Runner Layer
version: 1.0
status: pilot-ready
owner: Principal Systems Architect
created: 2026-04-17
depends_on: atlas-worker-system-hardening.md, atlas-session-memory-operating-model.md, auto-pickup-cron (Feature #9)
---

# Atlas Continuation Orchestrator — Plan-Runner Layer

Die fehlende zweite Automatisierungs-Schicht: **Task-Completion → nächster Plan-Step automatisch triggern**, ohne Operator-Intervention zwischen Steps.

## EXECUTIVE JUDGMENT

Auto-Pickup (Feature #9, seit 2026-04-17 10:35 UTC live) löst **Layer 1**: `pending-pickup` → Worker wird getriggert. Das funktioniert heute grün in der 3h-Autonomous-Run-Session. Aber **Layer 2 fehlt**: Wenn ein Worker-Task `done` ist, passiert nichts automatisch. Atlas weiß nicht, dass sein Plan einen Schritt weiter ist. Der Operator hält den Plan-State im Kopf und triggert Atlas manuell nach jeder Completion ("Pack 3 done, bitte Pack 7 triggern").

Heute konkret gemessen: 56min Arbeitsphase, 4 abgeschlossene Packs, **jeder Pack-Übergang brauchte einen Operator-Prompt an Atlas**. Das ist de-facto halbmanuelle Orchestrierung, nicht Autonomie.

**Fix ist kein weiterer Prompt-Feintuning, sondern ein echter Plan-Runner**: maschinell gelesener Plan-State, Cron-getriebener Advancement, expliziter Kill-Switch. Das ist ein ~150-Zeilen-Python-Script plus YAML-Schema, keine neue Architektur.

## CURRENT GAP

1. **Atlas läuft single-turn.** Jeder `openclaw agent --agent main --message "…"`-Call produziert eine Antwort und endet. Keine Persistenz, keine Wiederkehr, kein Ereignis-Listener.
2. **Kein Completion-Event.** Task-Status-Änderung zu `done` löst nichts aus außer einem Discord-Report an `#execution-reports` und einem board-event-log-Eintrag.
3. **Atlas-Heartbeat-Cron kennt keine Plan-Struktur.** Stündlicher Heartbeat entscheidet zwar über Dispatch, aber nur auf Basis "eligible tasks" — er versteht nicht dass "Pack 3 done → Pack 7 dran" ein kausaler Zusammenhang ist.
4. **Pläne liegen als Markdown in `vault/03-Agents/`** — für Menschen lesbar, für Maschinen opaque. Reihenfolge, Abhängigkeiten, State existieren nur im Kopf.
5. **Operator ist der Event-Bus.** Jede Transition geht durch einen menschlichen (oder in heutiger Run: Orchestrator-Agent-) Prompt.

## ROOT CAUSE

- **Plan-State nicht persistiert maschinell.** Es gibt keine Single Source of Truth für "wo im Plan sind wir gerade".
- **Keine Webhook/Event-Hooks** am Task-Lifecycle. `/api/tasks/<id>/receipt` (result) schreibt nur in die DB, löst keine externe Aktion aus außer Discord.
- **Kein Polling-Layer zwischen Auto-Pickup und Atlas.** Auto-Pickup kümmert sich um *eine* Task, nicht um die *Plan-Kette*.
- **Session-Modell ist definiert, Plan-Ausführung nicht.** Das `atlas-session-memory-operating-model.md` klärt wie Sessions laufen, aber nicht wer sie triggert.

## TARGET MODEL

Drei-Schicht-Orchestrierung:

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 3 — PLAN RUNNER (neu)                                │
│  cron */2 * * * *                                            │
│  Liest active-plans/*.yaml, erkennt Step-Completion,         │
│  triggert Atlas für nächsten Step mit Template-Prompt.       │
└────────────┬────────────────────────────────────────────────┘
             │ triggers Atlas turn
             ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 2 — ATLAS (Orchestrator-Agent)                        │
│  Legt MC-Task an, dispatcht, verifiziert (Phase-2-Hardening).│
└────────────┬────────────────────────────────────────────────┘
             │ creates task + dispatch
             ▼
┌─────────────────────────────────────────────────────────────┐
│  Layer 1 — AUTO-PICKUP (existing, seit 2026-04-17)           │
│  cron * * * * *                                              │
│  Triggert Worker-Agent für pending-pickup Tasks.             │
└─────────────────────────────────────────────────────────────┘
```

**Plan-State als YAML** unter `/home/piet/.openclaw/workspace/memory/working/active-plans/<plan-id>.yaml`:

```yaml
plan_id: worker-hardening-2026-04
title: Worker System Hardening
source_doc: /home/piet/vault/03-Agents/atlas-worker-system-hardening.md
status: active   # active | paused | done | aborted
created_at: 2026-04-17T12:00:00Z
operator: pieter_pan
current_step: 2

steps:
  - id: pack-1
    title: failureReason-Struktur
    agent: sre-expert
    prompt_template_ref: worker-hardening/pack-1
    status: done
    task_id: 2d9923e2-…
    completed_at: 2026-04-17T10:48:28Z

  - id: pack-3
    title: workerSessionId-Validator
    agent: sre-expert
    prompt_template_ref: worker-hardening/pack-3
    status: done
    task_id: 4a263398-…
    completed_at: 2026-04-17T11:48:13Z

  - id: pack-7
    title: admin-close preservation
    agent: sre-expert
    prompt_template_ref: worker-hardening/pack-7
    status: in-progress
    task_id: c5a2006f-…
    started_at: 2026-04-17T11:53:42Z
    retry_count: 0
    max_retries: 2

  - id: pack-2
    title: Receipt-Sequence warn-mode
    agent: sre-expert
    prompt_template_ref: worker-hardening/pack-2
    status: pending
```

**Plan-Runner-Zyklus** (alle 2min):

1. Scanne alle YAMLs mit `status: active`.
2. Pro Plan: finde ersten Step mit `status: in-progress` oder `pending`.
3. **Wenn in-progress**: GET `/api/tasks/<task_id>` → prüfe MC-Status.
   - `done` → Step auf `done` setzen, `completed_at` schreiben, nächsten Step aktivieren (→ 4).
   - `failed` oder `blocked` → Retry wenn `retry_count < max_retries`, sonst Plan auf `paused` setzen + Alert.
   - `in-progress` → nichts tun (warten).
4. **Wenn pending**: Plan-Runner triggert Atlas mit `prompt_template_ref`-resolved Prompt. Setzt Step auf `in-progress`, notiert `started_at`.
5. **Wenn alle Steps done**: Plan auf `done` setzen, Abschluss-Discord-Message.

**Kill-Switch** auf zwei Ebenen:
- Globale ENV `PLAN_RUNNER_ENABLED=0` (Cron).
- Pro-Plan: `status: paused` im YAML (Operator-Edit, kein Code nötig).

**Prompt-Templates** als separate Markdown-Dateien unter `/home/piet/.openclaw/workspace/memory/invariants/plan-prompts/<plan-type>/<step-id>.md`. Plan-Runner substituiert Platzhalter (`{prev_task_id}`, `{prev_result_summary}`, `{step_title}`). Beispiel:

```
/memory/invariants/plan-prompts/worker-hardening/pack-7.md
```

Inhalt: der konkrete Atlas-Prompt für Pack 7, wie ich ihn heute manuell geschrieben habe, mit Platzhaltern für vorigen Step.

## IMPLEMENTATION PACK

Sieben kleine reversible Pakete. Jedes <200 LoC, jedes standalone testbar.

### Pack A — Plan-State-Schema + Validator
- Datei: `/home/piet/.openclaw/scripts/plan_schema.py`
- Pydantic-Model (oder plain dataclass) für Plan + Step.
- Validator: lädt YAML, gibt klare Fehler zurück.
- Test: synthetic-plan.yaml round-trip.

### Pack B — Markdown → YAML-Seed-Konverter
- Datei: `/home/piet/.openclaw/scripts/plan-seed.py`
- Liest `atlas-worker-hardening.md` (und andere), extrahiert "Pack N: Titel" + "agent:" + step-prompts.
- Gibt YAML-Skeleton aus mit allen Steps als `status: pending`.
- Einmal-Tool, nicht im Cron.

### Pack C — Prompt-Template-Bibliothek
- Verzeichnis: `/home/piet/.openclaw/workspace/memory/invariants/plan-prompts/`
- Pro Plan-Type ein Unterordner (`worker-hardening/`, `board-cockpit/`, `session-pilot/`).
- Pro Step eine `.md` mit dem kanonischen Atlas-Prompt inkl. Handoff-Template (Scope / Done / Open / Anti-Scope / Bootstrap-Hint).
- Substitutions-Tokens: `{prev_task_id}`, `{prev_result_summary}`, `{step_title}`, `{plan_doc_url}`.

### Pack D — plan-runner.py (Core)
- Datei: `/home/piet/.openclaw/scripts/plan-runner.py`
- Main-Loop wie oben beschrieben, idempotent, file-lock pro plan-id.
- Atlas-Call via `subprocess.Popen([OPENCLAW, "agent", "--agent", "main", ...])` — gleiche Mechanik wie auto-pickup.
- Logging nach `~/.openclaw/workspace/logs/plan-runner.log`.
- Discord-Alert via Webhook (wiederverwendet `AUTO_PICKUP_WEBHOOK_URL` oder eigener).

### Pack E — Cron-Integration + ENV
- Crontab-Eintrag: `*/2 * * * * flock -n /tmp/plan-runner.lock /home/piet/.openclaw/scripts/plan-runner.py …`
- ENVs: `PLAN_RUNNER_ENABLED`, `PLAN_RUNNER_DRY_RUN`, `PLAN_RUNNER_MAX_STEPS_PER_HOUR`, `PLAN_RUNNER_ALERT_WEBHOOK_URL`.

### Pack F — Retry-Eskalation
- Beim Step-`failed`-Zustand: wenn `retry_count < max_retries` → Plan-Runner triggert Atlas nochmal mit Hinweis "Retry nach Fehler: `<failureReason>`".
- Wenn Retries erschöpft → Plan `paused`, Alert-Discord mit Task-ID, Operator muss manuell `status: active` zurück oder `status: aborted` setzen.

### Pack G — Operator-CLI
- Datei: `/home/piet/.openclaw/scripts/plan-cli.py`
- Commands:
  - `plan-cli status` — listet alle active-plans mit current-step.
  - `plan-cli show <plan-id>` — Details + YAML.
  - `plan-cli pause <plan-id>` — setzt `status: paused`.
  - `plan-cli resume <plan-id>`.
  - `plan-cli skip <plan-id> <step-id>` — überspringt Step (für Pack-Ordering-Override).
  - `plan-cli abort <plan-id>`.
- Atlas kann das via `exec`-Tool nutzen, Operator im SSH.

## FILES / COMPONENTS

| Pack | Files |
|---|---|
| A | new: `scripts/plan_schema.py` |
| B | new: `scripts/plan-seed.py` |
| C | new dir: `workspace/memory/invariants/plan-prompts/<plan-type>/*.md` |
| D | new: `scripts/plan-runner.py` |
| E | edit: crontab (piet user) |
| F | edit: `scripts/plan-runner.py` (Retry-Logik) + Alert-Integration |
| G | new: `scripts/plan-cli.py` |

Neues Verzeichnis: `workspace/memory/working/active-plans/` (Plan-State-YAMLs).

Keine MC-Code-Changes nötig. Der Layer ist orthogonal zum Next.js-Server.

## RISKS

1. **Runaway (Plan ohne End-Bedingung).** Mitigation: `PLAN_RUNNER_MAX_STEPS_PER_HOUR=5` als harter Gate, außerdem kein Step wird doppelt getriggert (file-lock + YAML-State).
2. **Double-Trigger durch Operator + Runner parallel.** Mitigation: Plan-Runner triggert NUR wenn Step `status: pending` ist. Operator-Manuell-Trigger würde Step zuerst auf `in-progress` setzen (Task-Existenz-Check), dann greift Runner nicht mehr.
3. **Stale Plan-State nach MC-Task-Löschung.** Mitigation: Runner check ob Task-ID noch existiert (`GET /api/tasks/<id>`), bei 404 Alert + Plan paused.
4. **Token-Kosten bei aggressiven Polling-Zyklen.** Mitigation: 2min-Interval ist konservativ, nur Atlas-Call wenn echter Step-Advance nötig (nicht jeder Cycle). Erwartet ~1 Atlas-Call pro 10–15min, nicht pro Cycle.
5. **Prompt-Template-Drift.** Mitigation: Templates sind Invariants (`memory/invariants/plan-prompts/`), Änderungen müssen manuell durch Atlas/Operator — gleiche Regel wie andere Invariants.
6. **Atlas-Fehlverhalten** (wie der openclaw.json-Incident 2026-04-17). Mitigation: Prompt-Templates enthalten explizite Anti-Scope-Klauseln, Plan-Runner eskaliert bei Config-Fehler sofort (400/500 auf `/api/tasks` → Plan paused).
7. **Plan-Runner selbst crasht.** Mitigation: systemd-Timer statt Cron für health-restart, oder wie heute crontab + monitor-externer health-check. Cycle-Log schreibt vor + nach Haupt-Loop.

## TEST PLAN

1. **Schema-Round-Trip**: synthetic-plan.yaml lesen, serialisieren, diffen → identisch.
2. **Dry-Run-Cycle**: `PLAN_RUNNER_DRY_RUN=1` mit aktivem Plan, kein Atlas-Call, nur Log-Ausgabe. Prüfe dass korrekte Advancement-Entscheidung geloggt.
3. **Live-Test mit Mini-Plan (2 Steps)**:
   - Plan: "Test-Mini" mit pack-a (sre-expert, simple no-op) und pack-b (sre-expert, simple no-op).
   - Runner startet Step 1 → Atlas legt Task an → Auto-Pickup triggert Forge → Forge done → Runner erkennt done → startet Step 2 → …
   - Acceptance: beide Steps done ohne Operator-Trigger, Gesamtdauer <20min.
4. **Retry-Test**: Forge absichtlich Task failen lassen. Runner retried 1x, dann wenn weiter failed → Plan paused, Discord-Alert kommt.
5. **Kill-Switch-Test**: `PLAN_RUNNER_ENABLED=0` in Cron-Env, Runner-Lauf → sofort Exit, keine Aktion, Log-Eintrag "DISABLED".
6. **Pause/Resume**: via plan-cli, prüfe dass Runner während Pause nichts tut.
7. **Chaos**: Plan-YAML manuell korrumpiert → Validator bricht sauber ab, Alert, anderer Plan läuft weiter.

## ROLLBACK

Drei Ebenen:

1. **Kill-Switch** (sofort, keine Änderung nötig): `crontab -e` → `PLAN_RUNNER_ENABLED=0` setzen. Nächster Cycle ist No-Op.
2. **Pro-Plan**: `plan-cli pause <plan-id>` oder YAML-Edit `status: paused`. Andere Pläne laufen weiter.
3. **Gesamt-Rückbau**: Cron-Zeile entfernen, Script unter `.bak-*` parken, Plan-State-Verzeichnis nach `archive/` verschieben. Alles im Dateisystem, keine DB-Transaktionen.

Keine destructive Ops. Kein Data-Loss-Risiko.

## RECOMMENDED EXECUTION AGENT

- **Forge (sre-expert)** — primary. Python-Script-Implementation (Pack A, B, D, F, G), Cron-Integration (Pack E), Schema + Validator.
- **Atlas (main)** — Definition der Prompt-Templates (Pack C). Atlas schreibt sie selbst für seine eigene Plan-Typen — er ist der beste Autor seiner Turn-Prompts. Jedes Template peer-reviewt von Operator vor Live-Schaltung.
- **Lens (efficiency-auditor)** — Baseline vor Rollout (heute: Operator-Triggers pro Pack = ~4 in 56min), After-Measurement nach 1 Woche Plan-Runner-Betrieb. Metriken: Steps-per-hour, Operator-Interventions, Failure-Rate, Token-Kosten.
- **Pixel (frontend-guru)** — nicht im kritischen Pfad. Optional: UI im Mission Control Board das aktive Pläne anzeigt (nach Board-Cockpit-Rollout).

**Rollen-Invariante**: Forge baut, Atlas schreibt seine eigenen Prompt-Templates, Lens misst. Operator behält Kill-Switch und plan-cli.

## ACCEPTANCE CRITERIA

Messbar gegen Baseline 2026-04-17 (heutige manuelle Orchestrierung):

1. **Vollautonome Mehrschritt-Ausführung**: 3-Step-Synthetic-Plan läuft komplett ohne Operator-Trigger zwischen Steps. Operator startet nur initial.
2. **Continuation-Latenz** zwischen Step-Done und nächstem Step-Triggered: ≤ 3min (Cron-Interval + Atlas-Turn).
3. **Operator-Intervention pro Plan**: ≤ 1 (nur Plan-Start), gemessen über 1 Woche Plan-Runner-Betrieb. Heute Baseline: ~7 pro Plan (bei 7 Steps).
4. **Failed-Step-Retry funktioniert**: Chaos-Test erzeugt failed, Runner retried, bei Retry-Cap pausiert Plan + Alert kommt via Webhook.
5. **Keine Runaway-Events**: `MAX_STEPS_PER_HOUR=5` als harter Gate wird nie überschritten. Kein Plan triggert mehr als 5 Atlas-Turns pro Stunde.
6. **Kill-Switch-Responsetime**: `PLAN_RUNNER_ENABLED=0` → innerhalb 2min kein Trigger mehr. Manuell messbar.
7. **Plan-CLI-Operations idempotent**: pause + pause = keine Doppel-Aktion. resume auf active-Plan = No-Op.
8. **Token-Budget**: Atlas-Turn-Kosten pro Step ≤ heutiger Baseline (= ~100k tokens pro Plan-Delegation-Turn laut heutigen run-logs).
9. **Happy-Path-Regression**: bestehende Auto-Pickup-Smoke-Suite weiter 10/10 grün. Plan-Runner darf Auto-Pickup nicht stören.
10. **Audit-Trail**: jeder Plan-Step-Übergang erzeugt Log-Eintrag + board-event (falls Task betroffen). Grep-fähig.

Pass-Kriterium: 9 von 10. Hard-Stop: #5 (Runaway) oder #6 (Kill-Switch).

---

## Umsetzungsreihenfolge (Prio-geordnet)

1. **Pack A** (Schema) — Foundation für alle anderen.
2. **Pack D** (Core-Runner im Dry-Run-only-Mode) — Code existiert, kann aber nicht schaden.
3. **Pack C** (Prompt-Templates) — Atlas schreibt seine eigenen Templates, basierend auf heutigen Session-Logs.
4. **Pack B** (Seed-Konverter) — einmalig für die 3 bestehenden vault/-Pläne.
5. **Pack E** (Cron + ENVs) — gibt Runner Lauf, aber DRY_RUN=1 für 24h.
6. **Pack G** (Plan-CLI) — Operator-Kontrolle vor Live-Schaltung.
7. **Pack F** (Retry + Eskalation) — letzter Schritt bevor `PLAN_RUNNER_DRY_RUN=0`.

Gesamtdauer: 3–4 Arbeitstage Forge (Pack A/B/D/F/G) + 1 Tag Atlas (Prompt-Templates) + 1h Operator-Review. In Kalenderzeit: 1 Woche bei Paralleler Arbeit.

## Session-Kontrakt

Diese Arbeit fällt in den **Umsetzungs-Session**-Typ gemäß `atlas-session-memory-operating-model.md`: max 40 tool-calls, 30min pro Pack, TodoWrite Pflicht, Scope = genau ein Pack.

Tangenten (z.B. "während ich hier bin, fix ich noch X") → `mcp__ccd_session__spawn_task`, nicht Mitnehmen.

## Abhängigkeits-Karte

```
Auto-Pickup (Layer 1, Feature #9, seit 2026-04-17 live)
         │
         │ triggers worker for pending-pickup
         ▼
Plan-Runner (Layer 3, neu)
  - Pack A (Schema)
  - Pack D (Core-Runner)
  - Pack C (Prompt-Templates)
  - Pack B (Seed-Konverter)
  - Pack E (Cron)
  - Pack G (CLI)
  - Pack F (Retry)
         │
         │ triggers Atlas turn → creates task → Auto-Pickup triggers worker
         ▼
Task lifecycle (MC, bereits gehärtet durch Phase 1/2 + Worker-Hardening Packs 1/3/7)
```

Plan-Runner ist der **reine Orchestrierungs-Layer** — er berührt keinen MC-Code, keine bestehenden Scripts. Nur neue Files unter `/scripts/` und neues Verzeichnis unter `workspace/memory/working/active-plans/`.

## Referenzen

- `/home/piet/.openclaw/scripts/auto-pickup.py` — Feature #9, Layer 1, Vorbild für Cron-getriebene Script-Architektur
- `/home/piet/vault/03-Agents/atlas-worker-system-hardening.md` — 8 Packs die via Plan-Runner automatisiert werden können
- `/home/piet/vault/03-Agents/atlas-board-operator-cockpit.md` — 7 Packs mit paarweisen UI+BE-Abhängigkeiten (Plan-Runner kann diese Pairs als verbundene Steps modellieren)
- `/home/piet/vault/03-Agents/atlas-session-memory-operating-model.md` — Umsetzungs-Session-Kontrakt, Handoff-Format (das Plan-Runner-Prompt-Templates befolgen müssen)
- Session vom 2026-04-17 — Baseline-Daten: 4 Packs in 56min mit 7 manuellen Operator-Triggers zwischen Atlas-Turns
