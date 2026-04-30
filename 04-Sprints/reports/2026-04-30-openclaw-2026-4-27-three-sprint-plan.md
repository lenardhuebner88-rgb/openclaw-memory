---
title: OpenClaw 2026.4.27 — 3-Sprint-Plan
date: 2026-04-30
status: draft (Sprint-1 ready to dispatch, Sprint-2/3 require operator approval)
related: 2026-04-30-openclaw-2026-4-27-update-report.md, 2026-04-30-openclaw-2026-4-27-post-update-audit.md
---

# 3-Sprint-Plan nach OpenClaw-Update 2026.4.27

## Übersicht

| Sprint | Ziel | Owner | Estimate | Risiko | Empfehlung |
|---|---|---|---|---|---|
| **Sprint-1 Stabilisierung** | System nach Update beweisbar sauber, Hygiene-Debt abbauen, Nacht-Outage RCA | Forge primary, sre-expert support | 8-12 h | niedrig | **JETZT als drafts anlegen, nach Operator-Sichtung dispatchen** |
| **Sprint-2 4.27-Features** | Konkrete Mehrwert-Features aus Changelog produktiv nutzen | Forge / Atlas (config) | 12-16 h | mittel | **Erst nach Sprint-1 grün** |
| **Sprint-3 Autonomie** | Atlas selbständiger machen, mit klaren Stop-Regeln | Atlas (selbst) + Operator | 16-20 h | hoch | **Erst nach Sprint-1 + 2** |

---

## Sprint-1: Stabilisierung nach Update

**Ziel:** Nach dem Update auf 2026.4.27 ist nachweisbar nichts kaputt, alle Hygiene-Themen sind sortiert, der Nacht-Outage hat eine Ursache.

**Tasks (drafts, sprint-tag `update-2026.4.27-stab`):**

### S1-T1 — Nacht-Outage RCA (mc-critical-alert 10× MC DOWN)
- **Beschreibung:** Zwischen 2026-04-30 00:25 UTC und 05:13 UTC hat `mc-critical-alert.py` 10× "MC DOWN (dispatcher rc=0)" gepostet. Aktuell läuft MC stabil. Ursache klären.
- **Schritte:** journalctl --user-unit mission-control --since '2026-04-30 00:00' --until '06:00' analysieren; check ob OOM-Kill, Restart-Loop, External-Cause; check `restart-policy.conf` Drop-in.
- **Akzeptanz:** RCA-Doc unter `vault/04-Sprints/reports/2026-04-30-mc-night-outage-rca.md` mit Root-Cause + Fix-Empfehlung. Falls Ursache nicht eindeutig: "needs-monitoring" markieren mit klaren Watch-Punkten.
- **Live-Prüfbefehl:** `journalctl --user -u mission-control.service --since '2026-04-30 00:00' --until '06:00' | grep -iE 'restart|exit|oom|fatal' | wc -l` sollte > 0 sein und Beweise liefern.
- **Stop:** Wenn Outage wieder auftritt während RCA → sofort stoppen + Discord-Alert.
- **assigned_agent:** sre-expert
- **Priority:** P0

### S1-T2 — Logrotate für 3 Spam-Logfiles
- **Beschreibung:** `auto-pickup.log` (1840 errors), `cost-alert-dispatcher.log` (386), `session-size-guard.log` (82) wachsen unkontrolliert.
- **Schritte:** `~/.config/logrotate.d/openclaw-workspace` anlegen oder den existierenden um diese 3 Files erweitern. Daily rotate, 14 days keep, gzip.
- **Akzeptanz:** Nach 24 h ist die größte aktive Logdatei < 50 MB. Alte Files als `.1.gz` rotiert.
- **Live-Prüfbefehl:** `du -h /home/piet/.openclaw/workspace/logs/*.log | sort -hr | head -3` sollte alle < 50 MB zeigen.
- **Rollback:** logrotate-config rückgängig machen, Files bleiben.
- **assigned_agent:** sre-expert
- **Priority:** P1

### S1-T3 — Stale lock-File cleanup-Verifikation
- **Beschreibung:** `report-d02c49b2-dcd8-43d3-a63d-c3a3baca4d62.lock` von 2026-04-29 15:19 (1 Tag alt) — sollte von `m7-stale-lock-cleaner` weggeräumt werden, ist es nicht.
- **Schritte:** Cron-Skript-Logik prüfen, age-threshold sehen, ggf. anpassen oder Bug fixen. Diese eine Datei manuell entfernen.
- **Akzeptanz:** Nach 24 h sind in `mission-control/data/locks/` keine Files älter als 6 h.
- **assigned_agent:** sre-expert
- **Priority:** P2

### S1-T4 — DeprecationWarning utcnow() in apply-mcp-recovery-patch.py
- **Beschreibung:** Zeile 99 nutzt `datetime.datetime.utcnow()` (deprecated). Auf `datetime.datetime.now(datetime.UTC)` umstellen.
- **Akzeptanz:** Nach Restart kein DeprecationWarning mehr in journalctl.
- **assigned_agent:** sre-expert
- **Priority:** P2

### S1-T5 — bundle-lsp disposal-error verifizieren
- **Beschreibung:** Beim Shutdown des alten 4.24-Prozesses kam `Cannot find module .../pi-bundle-lsp-runtime-BCcRJbYl.js`. Beim nächsten Restart prüfen ob das wegbleibt (Module-Resolution-Glitch beim Versions-Übergang) oder wiederkehrt (Bug-Report).
- **Akzeptanz:** Nach 1 controlled restart kein bundle-lsp-Fehler in den letzten 60 s journalctl.
- **assigned_agent:** sre-expert
- **Priority:** P2

### S1-T6 — Operator-OAuth-Refresh + OpenRouter-Topup verifizieren
- **Beschreibung:** Aus `operator-actions-2026-04-29.md`. Anthropic-OAuth war 19.5 Tage abgelaufen, OpenRouter empty. Operator (Lenard) prüft Status. Task = nur Verify, kein Fix durch Agenten.
- **Akzeptanz:** `openclaw doctor | grep expir` zeigt keine expired tokens; OpenRouter API key call funktioniert.
- **assigned_agent:** operator
- **Priority:** P0 (parallel zu S1-T1)

### S1-Akzeptanzkriterien (gesamt)
- Nach 48 h `journalctl --user -u openclaw-gateway --since 'now -24h' | grep -iE 'error|fatal' | grep -v 'session store' | wc -l` < 10
- `/api/health` zeigt durchgehend `severity=ok`
- Kein neues mc-critical-alert "MC DOWN" innerhalb 7 Tagen
- 3 große Logfiles < 50 MB nach Rotate

### S1-Stop-Kriterien
- Health degraded → sofort Pause, RCA, Operator-Approval vor Fortsetzung
- mehr als 1 Service-Restart in 60 min → Pause
- failed-Task-Rate >5 in 1 h → Pause

### Atlas/Forge-Prompt für Discord (kurz)
> `[Sprint-1-Stab] Forge primary. Bearbeite tasks S1-T1..T5 sequentiell, T1 first (P0 RCA). Live-prüfbefehle und Akzeptanzkriterien stehen im Plan. Stop bei health-degraded oder >1 service-restart/60min. Report nach jeder Task in Discord-Channel 1495737862522405088. Plan: workspace/memory/2026-04-30-openclaw-2026-4-27-three-sprint-plan.md`

---

## Sprint-2: Neue Features produktiv nutzen

**Ziel:** Konkrete Features aus 2026.4.27 einführen, die uns direkt Mehrwert bringen.

**Auswahl-Kriterien:** (1) direkter Mehrwert für Atlas/MC/Memory, (2) niedriger Implementierungsaufwand, (3) low-risk.

**Tasks (drafts, sprint-tag `update-2026.4.27-feat`):**

### S2-T1 — `models.pricing.enabled` opt-in evaluieren
- **Beschreibung:** Neu in 4.27. Pricing-Catalog-Fetches an OpenRouter/LiteLLM beim Boot abschalten falls wir die Preise statisch tracken.
- **Aufwand:** Config-Änderung in `openclaw.json` + Boot-Test.
- **Risiko:** niedrig. Falls aktiv, fallback aufs static config.
- **Akzeptanz:** Boot-Zeit Gateway < 90 s (vorher messen). Logs zeigen kein "fetching pricing catalog".
- **Priority:** P1

### S2-T2 — Memory/compaction `pre-compaction prompts runtime-only` verifizieren
- **Beschreibung:** Neu in 4.27. Compaction-Prompts erscheinen nicht mehr im Transcript / `chat.history`. Atlas-Session-Size hat heute emergency-rotate ausgelöst → relevant.
- **Aufwand:** Verify dass Feature aktiv ist (default), check `session-size-guard.log` ob neue rotations seltener.
- **Risiko:** niedrig.
- **Akzeptanz:** Über 7 Tage messen: Atlas-session-size grows pro Stunde -20% vs. baseline der letzten Woche.
- **Priority:** P1

### S2-T3 — `openclaw status --all` differenziert in Health-Skripten
- **Beschreibung:** Neu in 4.27. Scope-limited probes melden jetzt "reachable-but-degraded" statt "unreachable". Unsere `cron-health-audit.sh` und `mc-ops-monitor.sh` ggf. updaten.
- **Aufwand:** Skript-Edit + Test-Run.
- **Risiko:** niedrig.
- **Akzeptanz:** Health-Skripte unterscheiden zwischen "down" und "degraded" und liefern bessere Discord-Alerts.
- **Priority:** P2

### S2-T4 — Outbound-Proxy `proxy.enabled` für Network-Bind-Tightening
- **Beschreibung:** Neu in 4.27. Saubere Lösung für gewünschte Loopback-Bind-Tightening (Gateway 0.0.0.0:18789, Jaeger 16686, OTLP 4317/4318). Aus `operator-actions-2026-04-29.md`.
- **Aufwand:** Konzept + 1 Test-Run mit Forward-Proxy + Rollback-Plan.
- **Risiko:** **mittel** — falls falsch konfiguriert, isoliert sich der Gateway.
- **Akzeptanz:** Konzept-Doc + Test-Lauf in Staging-Equivalent. Kein Prod-Switch ohne Operator-Approval.
- **Priority:** P2

### S2-T5 — Cron-Tool `cron.add agentId inference`
- **Beschreibung:** Neu in 4.27. Vereinfacht Cron-Anlage durch automatische Session-Agent-Übernahme.
- **Aufwand:** Beim nächsten neuen Cron ausprobieren, Doc-Update.
- **Priority:** P3

### S2-Akzeptanzkriterien
- 2 von 5 Features aktiv und gemessen.
- Keine Service-Crashs durch neue Configs.

### S2-Stop-Kriterien
- Sprint-1 noch nicht alle P0/P1 grün → nicht starten.
- T4 Proxy-Test failt → nicht in Prod, RCA.

### Atlas/Forge/Pixel-Prompt
> `[Sprint-2-Feat] Forge primary fuer T1+T2+T5; Atlas fuer T3 (script-edit); T4 nur als Konzept, kein Prod. Voraussetzung: Sprint-1 alle P0/P1 done. Stop bei Service-Crash.`

---

## Sprint-3: Autonomie erhöhen

**Ziel:** Atlas wird selbständiger — mit harten Stop-Regeln und sichtbaren Gates.

**Voraussetzung:** Sprint-1 + Sprint-2 grün. Erst dann starten.

### S3-T1 — Atlas Auto-Task-Creation aus Routine-Findings
- **Beschreibung:** Wenn Atlas in einem Heartbeat-Cycle ein Hygiene-Issue findet (z.B. Logfile zu groß, stale Lock, Drift in Service-Description), legt er **selbst** einen draft-Task an mit klarem Titel + Owner-Vorschlag.
- **Schritte:** Whitelist von erlaubten Auto-Task-Templates definieren. POST /api/tasks mit `status=draft`. **Kein Auto-Dispatch.**
- **Akzeptanz:** Atlas erzeugt mindestens 3 sinnvolle drafts pro Woche, davon ≥80 % vom Operator akzeptiert.
- **Priority:** P1

### S3-T2 — Whitelist-Auto-Dispatch für sichere Sprint-Typen
- **Beschreibung:** Sprint-Typen `update-stab` und `vault-cleanup` darf Atlas autonom dispatchen wenn (a) Plan-Doc PlanSpec-validiert, (b) Pre-Flight-Gate green, (c) WIP < 1 active, (d) keine Open-Critical-Alerts.
- **Schritte:** Whitelist-Config + Pre-Flight-Bridge.
- **Risiko:** mittel. Cancel-Switch via Discord-Bot `/atlas-pause`.
- **Akzeptanz:** Erste 3 Auto-Dispatches haben 0 manuelle Korrekturen.
- **Priority:** P2

### S3-T3 — Atlas Follow-up-Erzeugung
- **Beschreibung:** Wenn Task `done` mit `result.followups[]`, legt Atlas die Follow-up-Tasks selbst an (draft).
- **Akzeptanz:** Follow-up-Generator pickt 100 % der explizit gemarkten followups, 0 false-positives.
- **Priority:** P2

### S3-T4 — WIP-Limits enforced
- **Beschreibung:** Hard-Limits: max 1 active task pro Agent, max 3 active total. Bei Überschreitung wird neue Task in `pending-pickup` gehalten.
- **Schritte:** Config in `openclaw.json` `dispatch.wipLimits`. Test mit künstlichem 4-Task-Burst.
- **Akzeptanz:** Bei 5 simultanen Dispatches: 3 active, 2 pending. Keine Race-Conditions.
- **Priority:** P1

### S3-T5 — Review-/Finalize-Gate für destructive ops
- **Beschreibung:** Tasks mit Tag `destructive` (drop tables, delete files, rm-rf, force-push) brauchen explizites Discord-`/approve` vom Operator vor Dispatch.
- **Akzeptanz:** 0 destructive ops ohne Operator-Approval seit 7 Tagen.
- **Priority:** P0 (gehört zu Autonomie-Sicherheit)

### S3-T6 — Stop-Regeln bei Anomalien
- **Beschreibung:** Wenn (a) failed-rate > 20 % in 1 h, ODER (b) >5 Service-Restarts/24 h, ODER (c) recoveryLoad > 5 → Atlas-Auto-Dispatch pausiert. Discord-Alert + Operator-Approval zum Wiederaufnehmen.
- **Akzeptanz:** Stop-Regel triggert bei künstlichem Test, kommt korrekt in Discord, Auto-Dispatch hält.
- **Priority:** P0

### S3-T7 — Discord-Daily-Digest
- **Beschreibung:** Kurzer täglicher Bericht in Audit-Channel: Tasks geschlossen, Tasks geöffnet, Outages, OAuth-Status, Top-3 Risiken.
- **Akzeptanz:** Daily 09:00 UTC Post in Channel `1495737862522405088`, < 1500 Zeichen, Laien-verständlich.
- **Priority:** P2

### S3-Akzeptanzkriterien (gesamt)
- 7 Tage Auto-Dispatch ohne menschlichen Eingriff bei 0 Stop-Trigger.
- 0 destructive ops ohne explizite Approval.
- Operator-Reaktionszeit auf Atlas-Drafts < 4 h Mittelwert.

### S3-Stop-Kriterien
- jede Stop-Regel feuert → Sprint pausieren, RCA, manuelle Approval zum Wiederaufnehmen.

### Atlas-Prompt (sehr kurz, Discord-tauglich)
> `[Sprint-3-Auto] Atlas, du fuehrst diesen Sprint zum Teil selbst. Beachte: NUR drafts erzeugen ohne Operator-Approve. Whitelist-Auto-Dispatch erst nach S3-T4 (WIP-Limits) und S3-T6 (Stop-Regeln) green. Plan: workspace/memory/2026-04-30-openclaw-2026-4-27-three-sprint-plan.md.`

---

## Empfohlene nächste Entscheidung

**A) Nur Sprint 1 als Tasks anlegen** — und Operator entscheidet pro Task ob dispatch.

Begründung: Sprint-1-RCA des Nacht-Outage ist Voraussetzung für jede Aussage über Stabilität. Ohne RCA fehlt die Basis für Sprint-2/3.
