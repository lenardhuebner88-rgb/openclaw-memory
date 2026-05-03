---
title: Codex Audit - Embedded Run Timeout / Lane Stall
created: 2026-05-03T21:58Z
agent: codex
scope: read-only-audit
status: completed
---

# Kurzurteil

Der vorgeschlagene Patch ist notwendig, aber nicht hinreichend.

Er behebt plausibel den konkreten Sekundärfehler `Command lane "main" task timed out after 330000ms`, weil der äußere Lane-Timeout jetzt nicht mehr `params.timeoutMs + 30000`, sondern `params.timeoutMs + 600000` ist. Er behebt aber nicht die Primärursache der wiederkehrenden `codex app-server attempt timed out` / `FailoverError: LLM request timed out`-Ereignisse und auch nicht die Session-Stalls, bei denen Recovery wegen `active_embedded_run` nur beobachtet.

# Evidenz

- Incident-Plan benennt die drei Symptome gemeinsam: `codex app-server attempt timed out`, `FailoverError: LLM request timed out`, `Command lane "main" task timed out after 330000ms`, plus `queued_work_without_active_run` und `active_embedded_run`: `03-Agents/Hermes/plans/openclaw-atlas-forge-codex-runtime-incident-2026-05-03.md:18-24`.
- Nachhaltigkeitsplan trifft den engen 330s-Bug korrekt: innerer Codex-Versuch läuft ca. 300s, danach schneiden 30s Grace den Retry/Compaction-Pfad ab: `03-Agents/Hermes/plans/openclaw-embedded-run-timeout-fix-plan-2026-05-03.md:20-31`.
- Installierte JS ist bereits gepatcht: `EMBEDDED_RUN_LANE_TIMEOUT_GRACE_MS = 10 * 60 * 1e3` und `resolveEmbeddedRunLaneTimeoutMs()` addiert diese Grace: `/home/piet/.npm-global/lib/node_modules/openclaw/dist/pi-embedded-rWtLEwl7.js:1433-1442`.
- Der Timeout wird auf die globale Command-Lane angewendet: `/home/piet/.npm-global/lib/node_modules/openclaw/dist/pi-embedded-rWtLEwl7.js:1538-1543`.
- Der alte Backup-Stand hatte noch `3e4`: `/home/piet/.npm-global/lib/node_modules/openclaw/dist/pi-embedded-rWtLEwl7.js.bak-20260503T213136Z-embedded-lane-timeout:1433`.
- Regression-Checker bestätigt statisch: `old_30s_constant_absent=True`, `outer_ms=900000`: `/home/piet/.openclaw/scripts/check-embedded-run-lane-timeout-patch.py:15-33`, ausgeführt am 2026-05-03T21:55Z.
- OpenClaw Command-Lane gibt die Lane nach Timeout frei, lässt das Task-Promise aber weiter unwind-en und loggt späte Rejections: `/home/piet/.npm-global/lib/node_modules/openclaw/dist/command-queue-Bkbt0KSa.js:15-24` und `:108-130`. Das erklärt, warum ein größerer Lane-Budget sinnvoll ist, aber keine echte App-Server-Recovery ersetzt.
- Codex-App-Server markiert 300s-Timeouts direkt im Attempt: `/home/piet/.npm-global/lib/node_modules/openclaw/dist/run-attempt-CektiLYp.js:3205-3224`; Cleanup und `clearActiveEmbeddedRun` passieren erst im `finally`: `:3319-3351`.
- Aktive-Run-Registry hat bereits `abortAndDrainEmbeddedPiRun()` und `forceClearEmbeddedPiRun()`, aber der beobachtete Recovery-Pfad nutzt sie nicht automatisch für `active_embedded_run`: `/home/piet/.npm-global/lib/node_modules/openclaw/dist/runs-DWPap98a.js:351-397`, `:473-481`, `:533-553`.
- Journal belegt vor Patch den exakten 330s-Abbruch: `journalctl --user -u openclaw-gateway.service --since '2026-05-03 16:00'`: Zeilen 396-399 und 1582-1584 im Audit-Output.
- Journal belegt nach Patch/Restart weiterhin `active_embedded_run`-Stalls kurz vor Gateway-ready: seit `23:31`, Zeilen 2-3; Gateway wurde danach ready: Zeilen 38 und 81.
- Aktuelle Config hat für `agents.defaults`, Atlas und Forge die Minimax-Fallbacks entfernt: `/home/piet/.openclaw/openclaw.json:483-489`, `:607-615`, `:711-720`. Das reduziert den kaputten `Model provider minimax not found`-Verstärker für diese Pfade.

# Reicht der Fix?

Nein, nicht allein.

Der 10-Minuten-Grace-Patch ist für den 330s-Lane-Abbruch passend. Er verhindert, dass Compaction/Fallback direkt nach einem 300s-App-Server-Timeout vom äußeren Lane-Timeout abgeschnitten wird.

Er reicht aber nicht gegen:

- wiederkehrende 300s `codex app-server attempt timed out` auf OpenAI-Codex-Modellen;
- Sessions, deren Diagnostic-Recovery wegen `active_embedded_run` nur `observe_only` macht;
- alte/bloated Discord-Session-Stores und stale Overrides;
- Provider-Routing-Fehler, wenn irgendein Agent noch `minimax/...` über den Codex-App-Server lädt, obwohl dieser Runtime-Kontext den Provider nicht findet;
- nicht persistente Dist-Patches nach OpenClaw-Update.

# Erforderliche Änderungen

1. Code: Lane-Budget behalten, aber update-persistent machen.
   - Patch nicht nur direkt in `dist` halten. Entweder Upstream-Quelle/Plugin-Build patchen oder einen bewusst dokumentierten ExecStartPre-Reapply-Guard ergänzen.
   - Der Checker `/home/piet/.openclaw/scripts/check-embedded-run-lane-timeout-patch.py` sollte nach jedem OpenClaw-Update laufen.

2. Code: Stuck-Recovery für `active_embedded_run` ergänzen.
   - Bei `queued_work_without_active_run` + `active_embedded_run` + Alter > definierter Schwelle nicht dauerhaft `observe_only`.
   - Erst `abortAndDrainEmbeddedPiRun(sessionId, settleMs)` nutzen, danach bei fehlendem Drain kontrolliert `forceClearEmbeddedPiRun(..., reason='stuck_recovery_timeout')`.
   - Guard: nicht forcieren, wenn aktuelle Trajectory noch neue Events schreibt.

3. Config: Fallback-Ketten agentweit konsolidieren.
   - Für Atlas/Forge ist Minimax aktuell aus den Fallbacks entfernt. Das muss für alle Agenten und Defaults verifiziert bleiben.
   - Entweder Minimax im Codex-App-Server-Kontext wirklich registrieren oder keine `minimax/...`-Fallbacks in Codex-Runtime-Ketten verwenden.

4. Session: Forge/SRE Discord-Session rotieren.
   - Plan ist richtig: nur `agent:sre-expert:discord:channel:1486480146524410028` rotieren, mit Backup.
   - Direkte Forge/Atlas-Sessions nicht blind löschen.
   - Zusätzlich prüfen: stale `modelOverride`, riesige Tokenhistorie, `activeSessionId=be1f1492-...` nicht mehr als Recovery-Blocker.

5. Runtime/Model: Codex-App-Server-Timeouts separat behandeln.
   - `timeoutSeconds=300` ist aktuell zentral gesetzt: `/home/piet/.openclaw/openclaw.json:588`.
   - Mehr Lane-Grace macht aus einem langsamen/abbrechenden Modell keinen stabilen App-Server. Nötig sind kürzere Tasks, aggressive Session-Rotation bei >150k Tokens, und ggf. weniger fragile Primärmodelle für Discord-Responder.

6. Mission-Control-Health-Fix nicht als Runtime-Fix werten.
   - `/api/models/health`-Änderungen verbessern Diagnose/Semantik (`skipped`, Summary, MiniMax-Ping), siehe `/home/piet/.openclaw/workspace/mission-control/src/lib/model-health-ping.ts:18-24`, `:65-115`, `:117-168` und Route-Summary `src/app/api/models/health/route.ts:38-50`.
   - Das behebt keine OpenClaw-Gateway-Lanes und keine Codex-App-Server-Children.

# Tests / Gates

Minimaler Akzeptanz-Gate:

1. `python3 /home/piet/.openclaw/scripts/check-embedded-run-lane-timeout-patch.py` muss grün bleiben.
2. Nach Gateway-Restart: `journalctl --user -u openclaw-gateway.service --since <ready-time>` ohne neue `CommandLaneTaskTimeoutError`, `codex app-server attempt timed out`, `active_embedded_run`, `queued_work_without_active_run` über mindestens 15 Minuten.
3. Direkter Atlas-Smoke und Forge-Smoke müssen je einen vollständigen Reply schreiben.
4. Session-Health muss `suspectedStuck=0` und keine `active_embedded_run`-Recovery-Skips zeigen.
5. Fallback-Test: kein `Model provider minimax not found` in Journal, solange Minimax nicht als Codex-App-Server-Provider bewiesen ist.
6. Regression-Tests für Diagnostics sind sinnvoll vorhanden: Klassifikation von `provider_not_found`, `codex_app_server_timeout`, `command_lane_timeout` in `/home/piet/.openclaw/workspace/mission-control/tests/openclaw-readonly-diagnostics.test.ts:75-81`.

# Risiken

- 900s äußerer Lane-Timeout kann echte Hänger länger blockieren, wenn keine aktive Stuck-Recovery ergänzt wird.
- Direkte Dist-Patches sind update-flüchtig.
- Session-Rotation kann Kontext verlieren; deshalb nur betroffene Discord-Session und mit Backup.
- Health-Endpoint kann falsche Sicherheit geben: `ok/skipped` dort bedeutet nicht, dass OpenClaw-Gateway-Fallbacks real ausführbar sind.

# Empfehlung

Patch nicht zurückrollen. Er adressiert einen echten Race zwischen innerem 300s-Timeout und äußerem 330s-Lane-Cap.

Vor "sufficient" fehlen aber zwei Pflichtstücke: automatische `active_embedded_run` Abort/Drain/ForceClear-Recovery mit Trajectory-Freshness-Guard und agentweite Fallback-/Session-Hygiene. Erst danach ist der wiederkehrende Stall-Pfad belastbar entschärft.
