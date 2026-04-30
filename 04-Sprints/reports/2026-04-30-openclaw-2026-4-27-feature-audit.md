---
title: OpenClaw 2026.4.24 → 2026.4.27 — Feature-Audit
date: 2026-04-30
scope: 3 Releases (4.25 + 4.26 + 4.27)
sources: /home/piet/.npm-global/lib/node_modules/openclaw/CHANGELOG.md
related: 2026-04-30-openclaw-2026-4-27-update-report.md, 2026-04-30-openclaw-2026-4-27-three-sprint-plan.md
---

# Phase 4 — Feature-Audit Diff 2026.4.24 → 2026.4.27

## TL;DR (Laien-Erklärung)

Zwischen den drei Releases (4.25, 4.26, 4.27) sind **vier Features besonders relevant für uns**, weil sie konkrete Schmerzpunkte adressieren, die wir gerade haben:

1. **OpenTelemetry für Memory-Pressure** (4.25) → wir können Atlas' Session-Size-Druck endlich live sehen statt nachträglich aus Logs rekonstruieren.
2. **Compaction-Preflight `maxActiveTranscriptBytes`** (4.26) → genau das Tool gegen das Problem, das heute morgen `emergency-rotate-too-late` ausgelöst hat.
3. **Cron-Tasks: Recovery aus durable run logs** (4.25) → unsere 50 Crons werfen weniger `backing session missing` False-Positives.
4. **`models.pricing.enabled` opt-in** (4.27) → schnellerer Gateway-Boot wenn Pricing-Catalog-Fetches abgeschaltet werden.

Plus **eine Migrations-Pflicht**: `agentRuntime.id` ist neuer canonical key — `openclaw doctor --fix` migriert die alte `runtime-policy`-Config automatisch. Sollten wir bald einmal anstoßen.

---

## Methodik

CHANGELOG der drei Releases gelesen, dann Filter auf für unser System relevante Themen: **security, memory, gateway, MCP, model-calls, autonomy, agents, cron, observability/OTel, session, taskboard, control-ui, auth**. Andere Themen (TTS-Provider, Channels/Telegram/QQBot/Yuanbao, Browser-Automation, Plugin-SDK-Internals) absichtlich übersprungen.

Bewertungs-Achsen:
- **Nutzen** ★/★★/★★★ — wie direkt löst das einen aktuellen Schmerzpunkt?
- **Aufwand** S/M/L (Stunden/Tage)
- **Risiko** niedrig/mittel/hoch (Config-Drift, Service-Crash, Datenverlust)
- **Empfehlung** **JETZT** / **SPRINT-2** / **DEFER** / **SKIP**

---

## Top-Auswahl (was wir direkt nutzen sollten)

### 1. ★★★ OpenTelemetry-Coverage für Memory-Pressure (4.25)

**Was:** OTel-Metrics für model calls, token usage, tool loops, harness runs, exec processes, outbound delivery, context assembly **und Memory-Pressure** — bounded low-cardinality.

**Warum für uns:** Heute Morgen hat Atlas `emergency-rotate-too-late` ausgelöst. Wir wissen erst aus dem Log nachher dass die Session zu groß war. Mit OTel-Memory-Pressure-Metriken sehen wir live (im Jaeger / Dashboard) wann Atlas an Limits kommt und können gegensteuern bevor `too-late`.

**Aufwand:** S — wir haben Jaeger schon laufen (Port 16686), OTLP auf 4317/4318. Config-Anpassung auf `openclaw.json`.

**Risiko:** niedrig — bounded low-cardinality heißt kein Cardinality-Explosion-Risiko.

**Empfehlung:** **JETZT** (Sprint-2 T1 candidate). Gibt sofortige Sichtbarkeit ohne Code-Änderungen.

### 2. ★★★ Compaction-Preflight `maxActiveTranscriptBytes` (4.26)

**Was:** Opt-in `agents.defaults.compaction.maxActiveTranscriptBytes` triggert lokale Compaction wenn JSONL-Transcript wächst, **bevor** harte Rotation greift. Successor-File ist kleiner statt raw-byte-Split.

**Warum für uns:** Direkter Fix für Atlas-Session-Size-Druck. Heute hatten wir `emergency-rotate-too-late` — das ist exakt was dieser Preflight-Trigger verhindern soll.

**Aufwand:** S — Config-Eintrag in `openclaw.json` unter `agents.defaults.compaction.maxActiveTranscriptBytes`. Empfohlener Wert: 80 % des bisherigen Hard-Rotate-Threshold. Watchen für 7 Tage.

**Risiko:** niedrig — Opt-in, falls kontraproduktiv: Config wegnehmen.

**Empfehlung:** **JETZT** (Sprint-2 T2 candidate). Adressiert ein P0-Symptom.

### 3. ★★★ Cron-Tasks: Recovery aus durable run logs (4.25)

**Was:** Cron-Task-Ledger-Records aus durable run logs + job state recovern, bevor `lost` markiert wird. Reduziert false `backing session missing` Audit-Errors.

**Warum für uns:** 50 active Crons + isolated cron runs — unsere `r48-board-hygiene-cron`, `cron-runs-tracker`, `mcp-taskboard-reaper` werfen vermutlich genau diese False-Positives. Indirekt Grund für Logfile-Spam.

**Aufwand:** S — automatisch aktiv ab 4.25.

**Risiko:** niedrig — Bug-Fix, kein neues Verhalten.

**Empfehlung:** **JETZT** (verifizieren dass aktiv). Wahrscheinlich schon bemerkbar — in den nächsten 24 h beobachten ob `auto-pickup.log` Fehler-Rate sinkt.

### 4. ★★★ `models.pricing.enabled` opt-in (4.27)

**Was:** Pricing-Catalog-Fetches an OpenRouter/LiteLLM beim Boot **abschaltbar**.

**Warum für uns:** Heute hatten wir Gateway-Boot-Eventloop-Delay 40 s (Phase-3-Befund). Pricing-Fetch ist ein Teil davon. Wenn wir die Preise eh statisch tracken, spart das Boot-Zeit.

**Aufwand:** S — `"models": { "pricing": { "enabled": false } }` in `openclaw.json`. Vorher messen, nachher messen.

**Risiko:** niedrig — Pricing-Werte fallen auf statische zurück.

**Empfehlung:** **SPRINT-2** — Boot-Zeit-Vergleich als Acceptance-Kriterium.

### 5. ★★ Plugins-Diagnostics `model_call_started`/`model_call_ended` Hooks (4.25)

**Was:** Metadata-only Hooks für Provider/Modell-Call-Telemetry. **Kein** Prompt-Inhalt, **keine** Header, **keine** Request-Bodies.

**Warum für uns:** Saubere Cost-Audit-Layer. Aktuell haben wir `cost-alert-dispatcher.py` der heuristisch arbeitet. Mit echten Hook-Events kann unser cost-tracking präziser werden ohne Privacy-Bedenken.

**Aufwand:** M — eigene Plugin schreiben oder in bestehende Hooks-Pipeline integrieren.

**Risiko:** niedrig.

**Empfehlung:** **DEFER** — nice-to-have, kein akuter Schmerz.

### 6. ★★ Agents-Tools: Loop-Detection scoped to active run (4.26)

**Was:** Tool-Loop-Detection-History wird auf den aktiven Run beschränkt. Heartbeat-Cycles erben keine stale repeated-call counts mehr.

**Warum für uns:** Wir haben Heartbeat-Crons (m7-master-heartbeat, atlas-receipt-stream-subscribe, forge-heartbeat) — die könnten von stale loop-detection-State betroffen sein. Symptom wäre: Heartbeats werden fälschlich als "loop" markiert und unterdrückt.

**Aufwand:** S — automatisch aktiv ab 4.26.

**Risiko:** niedrig.

**Empfehlung:** **JETZT** (verifizieren dass aktiv). Beobachten ob unerklärte Heartbeat-Lücken weniger werden.

### 7. ★★ Gateway-Auth: Stale Device-Tokens clear (4.27)

**Was:** Wiederverwendete stale device tokens werden gelöscht, kein reconnect-loop bei device-token-mismatch.

**Warum für uns:** Indirekt relevant für unser OAuth-Drama (Anthropic-Token 19.5 Tage abgelaufen). Bei Token-Rotation hat das vor 4.27 Loops verursacht.

**Aufwand:** S — automatisch aktiv ab 4.27.

**Empfehlung:** **JETZT** (verifizieren beim nächsten OAuth-Refresh — S1-T6).

### 8. ★★ Agents-Compaction: Token-Estimate persistent (4.26)

**Was:** Post-Compaction-Token-Estimate wird persistiert wenn Provider keine usage-Metadaten zurückgibt. `/status` und Session-Lists zeigen weiter fresh context usage.

**Warum für uns:** Wenn wir auf einen Provider switchen der keine usage-Metadata schickt (z.B. einige Local-LLM), bleibt die Anzeige sinnvoll.

**Empfehlung:** **JETZT** (automatisch).

### 9. ★ `openclaw status --all` reachable-but-degraded (4.27)

**Was:** Scope-limited Gateway-Probes melden jetzt `reachable-but-degraded` statt `unreachable`.

**Warum für uns:** Unsere Health-Skripte (`cron-health-audit.sh`, `mc-ops-monitor.sh`) können differenzierter alerten.

**Aufwand:** M — Skript-Edit + Discord-Alert-Logik anpassen.

**Empfehlung:** **SPRINT-2** — Bessere Discord-Statusmeldungen.

### 10. ★ `proxy.enabled` Outbound-Proxy + `ALL_PROXY` Support (4.27 + 4.26)

**Was:** Operator-managed outbound proxy mit strict http://-Validation, loopback-only Gateway-bypass, env-cleanup beim Exit. Plus `ALL_PROXY`/`all_proxy` honored in Undici.

**Warum für uns:** Saubere Lösung für Network-Bind-Tightening (offen aus `operator-actions-2026-04-29.md`). Aktuell exposed: Gateway 0.0.0.0:18789, Jaeger 16686, OTLP 4317/4318.

**Aufwand:** L — Konzept + Test-Lauf + Rollback-Plan + Operator-Approval.

**Risiko:** mittel — falls falsch konfiguriert, isoliert sich Gateway.

**Empfehlung:** **SPRINT-2 als Konzept-Doc** (T4 im 3-Sprint-Plan), kein Prod-Switch ohne Operator.

---

## Migrations-Pflicht

### `agentRuntime.id` als canonical config key (4.25)

**Was:** `agentRuntime.id` ist neuer canonical key. Legacy `runtime-policy`-Configs werden via `openclaw doctor --fix` migriert.

**Aktion:** Bei nächstem geplanten Restart einmalig `openclaw doctor --fix` laufen lassen. Backup vorher (`openclaw.json` ist im Backup-Ordner enthalten).

**Empfehlung:** **JETZT** (low-risk, safety-net schon vorhanden via Backup).

---

## Übersicht Tabelle

| # | Feature | Version | Nutzen | Aufwand | Risiko | Empfehlung |
|---|---|---|---|---|---|---|
| 1 | OTel Memory-Pressure | 4.25 | ★★★ | S | niedrig | **JETZT** |
| 2 | Compaction-Preflight maxActiveTranscriptBytes | 4.26 | ★★★ | S | niedrig | **JETZT** |
| 3 | Cron-Tasks Recovery aus durable logs | 4.25 | ★★★ | S | niedrig | **JETZT** (verify) |
| 4 | models.pricing.enabled opt-in | 4.27 | ★★★ | S | niedrig | SPRINT-2 |
| 5 | model_call_started/ended Hooks | 4.25 | ★★ | M | niedrig | DEFER |
| 6 | Tool-Loop scoped to active run | 4.26 | ★★ | S | niedrig | **JETZT** (verify) |
| 7 | Gateway-Auth stale device-tokens clear | 4.27 | ★★ | S | niedrig | **JETZT** (verify mit S1-T6) |
| 8 | Compaction Token-Estimate persistent | 4.26 | ★★ | S | niedrig | **JETZT** (automatisch) |
| 9 | status --all reachable-but-degraded | 4.27 | ★ | M | niedrig | SPRINT-2 |
| 10 | proxy.enabled + ALL_PROXY | 4.27/4.26 | ★ | L | mittel | SPRINT-2 (Konzept) |
| MIG | agentRuntime.id canonical | 4.25 | n/a | S | niedrig | **JETZT** (doctor --fix) |

---

## Was wir absichtlich SKIPPEN

| Feature | Grund |
|---|---|
| TTS-Upgrades + neue TTS-Provider (Azure, Xiaomi, ElevenLabs v3, Inworld, Volcengine) | Wir nutzen kein TTS. |
| Channels (Yuanbao, QQBot, Telegram-Bot, Slack-Socket-Mode, Mattermost, Feishu, LINE) | Wir nutzen Discord exklusiv. |
| Apps (Peekaboo 3.0, ElevenLabsKit, Swabble, macOS/iOS SwiftPM) | Server-only Setup. |
| Browser automation safer tab URLs | Pixel-Workflow nutzt Chrome-MCP, anderer Pfad. |
| Plugin SDK Refactors (channel-route normalization, focused fixture subpaths, modelCatalog manifest moves) | Wir schreiben keine Plugins. |
| Codex Computer-Use install | Atlas/Forge nutzen kein Computer-Use. |
| iOS/Android node.presence.alive | Kein Mobile-Pairing. |
| Sandbox/Docker GPU passthrough | Kein Sandbox-Container-Setup. |
| Codex `--thinking minimal -> low` Translation | Auto-fix ohne unser Eingreifen. |
| DeepInfra Provider Bundle | Bestehende Provider-Auswahl reicht. |

---

## Konkrete Umsetzungs-Reihenfolge (Sprint-2 Vorbereitung)

Falls Sprint-1 (Stabilisierung) abgeschlossen ist, schlage ich für Sprint-2 diese 5 Tasks vor (in dieser Reihenfolge):

1. **F1** — `agentRuntime.id` Migration via `openclaw doctor --fix` (5 min, low-risk)
2. **F2** — Compaction-Preflight `maxActiveTranscriptBytes` aktivieren + 7 Tage Beobachtung
3. **F3** — OTel-Memory-Pressure-Dashboard in Jaeger sichtbar machen (Config + Visualisierung)
4. **F4** — `models.pricing.enabled=false` testen + Boot-Zeit-Vergleich (vorher/nachher)
5. **F5** — Verify Sprint (1 h): F6 stale-token-clear + F7 cron-recovery + F8 tool-loop-scoping → Logs prüfen, Erfolg dokumentieren

**Gemeinsamer Aufwand:** ~6-8 h.

**Risiko:** niedrig — alles opt-in oder automatisch, klare Rollback-Pfade über Backup.

---

## Empfehlung

- **Phase 5** (3-Sprint-Plan) bleibt unverändert — Sprint-1 als drafts angelegt, Sprint-2/3 dokumentiert.
- Diese Feature-Auswahl **ergänzt** den Sprint-2-Inhalt mit konkreten Tasks F1-F5 (oben).
- Vor Sprint-2-Dispatch: Sprint-1 T1-T6 als ready (S1-T1 RCA Nacht-Outage P0 zuerst).

**Keine zusätzlichen Tasks im Board angelegt** — entspricht der Empfehlung "A) Nur Sprint 1 als Tasks". Sprint-2-Tasks würden erst nach Sprint-1-Closure und expliziter Operator-Freigabe entstehen.
