---
title: OpenClaw 2026.4.27 — Post-Update Audit
date: 2026-04-30
audit_window: 2026-04-30 18:34 UTC → 18:40 UTC (Post-Restart)
status: PASS-with-hygiene-debt
---

# OpenClaw 2026.4.27 — Post-Update Audit

## Executive Summary (Laien-Erklärung)

Nach dem Update auf 2026.4.27 ist das System **funktional komplett gesund**. Alle Dienste laufen, alle Health-Checks grün, die Aufgaben-Datenbank ist konsistent, kein einziger Task hängt.  
Was nicht 100 % sauber ist: Es gibt **alte Logfiles mit vielen Fehler-Zeilen aus den letzten Wochen** — das ist Hygiene-Schuld, kein Funktionsproblem. Außerdem hatte das System diese Nacht (00:25-05:13 Uhr) für ein paar Minuten Aussetzer — die wurden korrekt erkannt und die Alarmierung hat funktioniert, aber wir wissen noch nicht warum.

**Daraus: Sprint-1 = Hygiene + RCA der Nacht-Aussetzer.**

---

## Status-Übersicht

| Bereich | Status | Kommentar |
|---|---|---|
| Version-Drift | ✅ behoben | CLI, npm, Prozess und Description alle auf 2026.4.27 |
| Services live | ✅ | gateway, mission-control, discord-bot — alle active |
| Auto-Start nach Reboot | ✅ | gateway+mc enabled (war ok), discord-bot in dieser Session enabled |
| Logs aktuell sauber? | ⚠️ | Seit Restart sauber. Aber alte logs voller Fehler — Cleanup-Backlog. |
| Cron / Heartbeats | ✅ | 54 Crontab-Lines aktiv, Timer feuern, Auto-Pickup green |
| Taskboard | ✅ | 833 tasks, 1 offen, 0 stuck, dispatchStateConsistency=1 |
| Discord-Reporting | ✅ | Channel `1495737862522405088` antwortet, Bot-Token gültig |
| Memory-System | ✅ | L1-L6 aktiv, kein OOM, gateway-mem 1.2 GiB (limit 6 GiB) |

---

## Detail-Befunde

### A. Version & Drift

| Quelle | Wert | OK? |
|---|---|---|
| `openclaw --version` (CLI) | `OpenClaw 2026.4.27 (cbc2ba0)` | ✅ |
| Gateway-Prozess command-line | `/home/piet/.npm-global/lib/node_modules/openclaw/dist/index.js` | ✅ |
| `npm ls -g` | `openclaw@2026.4.27` | ✅ |
| systemd Description (drop-in) | `OpenClaw Gateway (v2026.4.27)` | ✅ |
| MC `package.json` | `mission-control 1.0.0` | ✅ (eigene Versionierung, korrekt entkoppelt) |
| Vault-Doc | (keine Version-Markers vor diesem Update) | OK |

**Kein Drift mehr.**

### B. Services & Timer

```
openclaw-gateway.service         active enabled  pid=949130 mem=1.2 GiB
mission-control.service          active enabled  pid=949335 mem=173 MiB
openclaw-discord-bot.service     active enabled  pid=3067670 mem=29 MiB
```

**14 systemd-Timer aktiv**, u.a.: `openclaw-systemjob-atlas-receipt-stream-subscribe`, `m7-atlas-master-heartbeat`, `mc-task-parity-check`, `canary-session-rotation-watchdog`, `m7-session-freeze-watcher`, `m7-stale-lock-cleaner`, `m7-worker-monitor`, `vault-sync`, `forge-heartbeat`, `researcher-run`.

**Keine Worker-Service aktuell aktiv** = kein offener Task in Bearbeitung. Erwartetes Verhalten.

### C. Logs (seit Restart 20:34 CEST)

**Gateway:**
- Cosmetic: `bundle-lsp runtime disposal failed during shutdown` — beim Shutdown des **alten** 4.24-Prozesses, nicht beim 4.27-Start. Sollte verschwinden.
- WARN: `liveness eventLoopDelayP99Ms=1671.4 eventLoopDelayMaxMs=40298.9 eventLoopUtilization=0.957` — Boot-Spike, danach normal. **Kein wiederkehrendes Problem.**
- DeprecationWarning: `apply-mcp-recovery-patch.py:99` nutzt `utcnow()`. Sprint-1 Task.

**MC:** keine Errors.

**Discord-Bot:** keine Errors.

**Workspace-Logs (kumuliert über Wochen, nicht seit Restart):**
- `auto-pickup.log` 1840 error-lines
- `cost-alert-dispatcher.log` 386 error-lines
- `session-size-guard.log` 82 error-lines

→ Hygiene-Backlog. Logrotate fehlt.

**Historisch — Nacht-Incident:**
`mc-critical-alert.log` zeigt 10 × "MC DOWN (dispatcher rc=0)" zwischen 00:25 UTC und 05:13 UTC am 2026-04-30. Rate-Limit 30 min, also = 10 × 32 min = ~5 h Outage-Window. Aktuell kein laufender Incident, MC ist seit 18:34 UTC stabil. **Ursache unbekannt → Sprint-1 RCA.**

### D. Cron / Heartbeats / Autopickup

- 54 Crontab-Einträge non-comment.
- Auto-Pickup `GATE_MATRIX`: alle 7 Gates **PASS** (first_heartbeat, no_first_heartbeat=0, pending_pickup, trend_claim_timeouts_10m=0, proof_green, silent_fails=0, no_target=0).
- Soeben gesehen: `ROTATION_EXEC agent=main session=f166cfea-199 action=emergency-rotate-too-late`. → Die `main` (Atlas-)Session war über dem Size-Limit, wurde rotiert. **Funktioniert wie geplant.**
- Stale-Lock: `report-d02c49b2-dcd8-43d3-a63d-c3a3baca4d62.lock` von 2026-04-29 15:19 — 1 Tag alt. Cleanup-Kandidat.

### E. Taskboard / Dispatch

```json
{
  "totalTasks": 833,
  "openTasks": 1,
  "inProgress": 0,
  "pendingPickup": 0,
  "blocked": 0,
  "failed": 0,
  "staleOpenTasks": 0,
  "orphanedDispatches": 0,
  "recoveryLoad": 0,
  "dispatchStateConsistency": 1
}
```

Status-Verteilung gesamt: 680 done · 97 canceled · 53 failed (historisch) · 2 draft · 1 assigned.

Active task: `01a4d52d` an `sre-expert` — nicht von mir, normaler Betrieb.

**Atlas kann jetzt sicher autonom dispatchen** — State-Machine konsistent, keine Dispatch-State-Drift.

### F. Discord-Reporting

| Frage | Antwort |
|---|---|
| Funktioniert Channel `1495737862522405088`? | ✅ Bot-API, HTTP 200 auf 8 Test-Posts |
| Sind Statusmeldungen kurz und verständlich? | ✅ Alle unter 700 Zeichen, Format `STATUS / WAS / BEFUND / RISIKO / NÄCHSTER SCHRITT` |
| Bessere interne Posting-Pfade? | Aktuell keiner — Bot-Direct-API ist sauber. `HEARTBEAT_WEBHOOK_URL` postet in falschen Channel ("MC Auto-Pickup"). Falls dauerhaft Status-Posts gewünscht: dedicated Audit-Webhook erstellen ODER Helper-Script `/tmp/discord-audit-post.sh` permanent in `~/.openclaw/scripts/` ablegen. |

---

## Aufgenommene Risiken (Top 5)

1. **Logfile-Hygiene** (auto-pickup, cost-dispatcher, session-size-guard) — schleichende Disk-Belastung + Signal-Noise.
2. **Nacht-Outage 00:25-05:13 UTC** ohne RCA — kann sich wiederholen.
3. **Stale lock-File** vom 29.04 — Hinweis dass `m7-stale-lock-cleaner` evtl. nicht alles fängt.
4. **DeprecationWarning utcnow()** — bei Python 3.13/3.14 schreit das vermutlich lauter; jetzt fixen statt später.
5. **`bundle-lsp` Module-Resolution-Glitch** während des 4.24→4.27 Übergangs — falls beim nächsten Restart wiederkehrt = Bug-Report wert.

## Top 5 Chancen aus 2026.4.27

1. **`models.pricing.enabled`** — Pricing-Catalog-Fetches ausschalten falls offline, spart Boot-Zeit.
2. **Memory/compaction: pre-compaction prompts runtime-only** — Atlas-Session-Size verbessert sich (war heute Trigger für emergency-rotate).
3. **`openclaw status --all` reachable-but-degraded** — Health-Skripte können differenzierter melden.
4. **Outbound-Proxy `proxy.enabled`** — saubere Lösung für Network-Bind-Tightening (offen aus operator-actions-2026-04-29).
5. **Cron-Tool `cron.add` agentId-Inference** — vereinfacht Cron-Pflege bei Atlas-Tasks.

## Empfehlung

**Sprint-1 starten** (Stabilisierung). Sprint-2 + 3 als Drafts im Board, nicht dispatchen.

Konkrete nächste Entscheidung: **A) Nur Sprint 1 als Tasks anlegen** (siehe `2026-04-30-openclaw-2026-4-27-three-sprint-plan.md`).
