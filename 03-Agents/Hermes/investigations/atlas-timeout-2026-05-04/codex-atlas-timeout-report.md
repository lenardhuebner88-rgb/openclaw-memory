# Codex RCA: Atlas Timeout 2026-05-04 00:01:25

## Kurzfazit

Atlas hing nicht in einem OpenClaw-Tool. Der erste Modellversuch `openai/gpt-5.4-mini` lief von 2026-05-03 23:56:25.642+02 bis 2026-05-04 00:01:25.643+02 und wurde nach ca. 300s als `timedOut=true`, `aborted=true`, `promptError="codex app-server attempt timed out"` beendet. Danach griff Model-Fallback auf `openai/gpt-5.4`; dieser zweite Versuch startete um 00:01:27.816+02 und war um 00:01:56.314+02 erfolgreich.

Der Timeout war ein innerer Modell-/Assistant-Timeout, kein Beleg fuer einen Tool-Loop, Discord-Send, Mission-Control-API-Call oder einen neuen Outer-Lane-Budget-Abbruch.

## 1. Exakte Aktion beim Timeout

Runtime-Aktion:
- `trajectory-relevant.json` zeigt fuer den ersten Versuch nur `session.started`, `context.compiled`, `prompt.submitted`, danach `model.completed` und `session.ended`; es gibt keine `tool.execution.*`-Events zwischen Prompt und Timeout.
- Der Prompt war nur die Discord-Antwort "Ja mach genau das" im Channel `#atlas-main` (`message_id=1500617042342969386`).
- Der abgebrochene Assistant-Teiltext lautete: "Ich schreibe die vier Dubletten jetzt als `canceled` mit sauberem Grund `duplicate of canonical done task`. Danach pruefe ich die einzelnen Task-States gegen die Live-API."

Semantische Aufgabe:
- Atlas wollte vier Dubletten-Drafts canceln und danach gegen die Live-API verifizieren.

Was nicht belegt ist:
- Im ersten, getimeouteten Versuch ist keine ausgefuehrte Task-Mutation belegt. Der Text kuendigt die Mutation an, aber die Trajectory enthaelt keine Tool-/API-Ausfuehrung.
- Die erfolgreiche Abschlussmeldung kam erst im Fallback-Versuch `openai/gpt-5.4`: vier IDs wurden als bereinigt gemeldet und zwei Drafts als weiter offen aufgelistet.

## 2. Dynamische Tools vor dem Timeout

Kein Tool-Start/Haenger/Timeout ist in der bereitgestellten Trajectory belegt.

Belege:
- Die Toolliste im Kontext hatte 9 dynamische Tools: `agents_list`, `memory_get`, `memory_search`, `session_status`, `sessions_history`, `sessions_list`, `sessions_send`, `sessions_yield`, `subagents`.
- Die Trajectory-Eventtypen enthalten keine `tool.execution.started`, `tool.execution.completed`, `tool.execution.error` oder `tool.execution.blocked`.
- `messagesSnapshot` beim Timeout besteht nur aus User-Message und Assistant-Message; keine Tool-Message, kein Tool-Result.
- Das Gateway-Journalfenster enthaelt um den Timeout nur Websocket-Health, stuck-session diagnostics, embedded timeout/fallback und model-fallback decisions; keinen Toolnamen und keine Tool-Ausfuehrung.

Der Diagnostic-Hinweis um 23:59:28 ist kein Tool-Haenger-Beleg. Er klassifiziert `queued_work_without_active_run`, dann wird Recovery wegen `active_embedded_run` fuer genau `c398bead-a362-46ca-a764-6502d305ff61` uebersprungen. Das heisst: Watchdog sah einen langen Processing-Zustand, liess ihn aber laufen.

## 3. Warum der Turn timed out

Gesicherte Ursache:
- Der `gpt-5.4-mini`-Assistant-Versuch erreichte den inneren Request-/Attempt-Timeout nach ca. 300s.
- OpenClaw interpretierte das als `FailoverError: LLM request timed out.`
- Der Kandidat `openai/gpt-5.4-mini` wurde mit `reason=timeout` als failed markiert; naechster Kandidat war `openai/gpt-5.4`.

Wahrscheinlichste Interpretation:
- Modell/runtime hat nach partieller Ausgabe nicht rechtzeitig abgeschlossen. Dafuer sprechen `assistantTexts` mit sichtbarem Teiltext, `usage.output=893`, `stopReason=aborted` und `errorMessage="codex app-server attempt timed out"`.

Nicht gestuetzt durch diese Evidenz:
- Tool-Loop: keine Tool-Events, keine Tool-Messages.
- Queue/Lane-Bug als Primaerursache: Lane meldet zwar Fehler nach 300745/300746ms, aber der Fehlertext ist der vom inneren LLM-Failover, nicht ein `CommandLaneTaskTimeoutError`.
- Kontext-Bloat als gesicherte Ursache: der erste Versuch hatte `usage.cacheRead=73088`, `total=77335`; das ist gross, aber im Evidence-Set fehlt ein `timeout-compaction`-Log. Hypothese: grosse Session/Cache-Last kann Latenz verstaerkt haben, ist aber hier nicht bewiesen.
- Config-Fehlrouting: Config-Fallbackkette existiert, und Fallback auf `gpt-5.4` funktionierte.

## 4. 300s Timeout / Abort-Pfad

Im redacted Atlas-Config-Snapshot steht kein explizites `timeoutSeconds`; sichtbar sind nur `params.wipLimit=3`, Model-Fallbacks und Tool-/Skill-Kontext.

Aus dem dist snippet:
- `runEmbeddedPiAgent(params)` berechnet `laneTaskTimeoutMs = resolveEmbeddedRunLaneTimeoutMs(params.timeoutMs)`.
- `resolveEmbeddedRunLaneTimeoutMs(timeoutMs)` setzt Outer-Lane-Timeout auf `Math.floor(timeoutMs) + EMBEDDED_RUN_LANE_TIMEOUT_GRACE_MS`.
- `EMBEDDED_RUN_LANE_TIMEOUT_GRACE_MS` ist `10 * 60 * 1000`.
- `params.timeoutMs` wird an den Agent-Harness weitergereicht.
- Bei `timedOut && !timedOutDuringCompaction && !timedOutDuringToolExecution` wird normaler Timeout-/Failover-Pfad betreten.
- Der User-facing Timeout-Text verweist auf `agents.defaults.timeoutSeconds`; daraus ist wahrscheinlich, dass `params.timeoutMs` aus dieser Runtime-/Config-Ebene kommt. Das ist aus den bereitgestellten Dateien aber nur wahrscheinlich, nicht vollstaendig bis zum Caller bewiesen.

Abort/Fallback:
- `shouldRotateAssistant()` wird bei `timedOut` true, sofern nicht Compaction/Tool-Execution betroffen ist.
- Bei Timeout loggt `handleAssistantFailover()` erst "Profile ... timed out. Trying next account..."; wenn keine Profilrotation weiterhilft und Fallback konfiguriert ist, wird `fallback_model` geworfen.
- Genau das sieht man im Journal: `Profile ... timed out`, dann `embedded run failover decision ... decision=fallback_model reason=timeout`, dann `model fallback decision ... candidate_failed ... next=openai/gpt-5.4`.

## 5. Outer-Lane-Budget vs innerer Timeout

Die neue Outer-Lane-Budget-Logik scheint hier nicht die Ursache gewesen zu sein.

Belege:
- Code-Kommentar: Outer command-lane cap soll "comfortably above" dem inneren `params.timeoutMs` liegen; 30s Grace wurde durch 10min Grace ersetzt.
- Bei `params.timeoutMs ~= 300000` waere der neue Global-Lane-Timeout ca. 900000ms.
- Journal meldet nach ca. 300746ms keinen Outer-Lane-Timeout-Typ, sondern `error="FailoverError: LLM request timed out."`
- Direkt danach laeuft der Model-Fallback weiter und `gpt-5.4` succeeded um 00:01:56.647+02. Ein harter Outer-Lane-Abbruch haette diesen Recovery-Pfad eher abgeschnitten.

Interpretation: Innerer Modellversuch timed out; Lane loggte den geworfenen FailoverError. Das gepatchte Outer-Budget hat den Fallback nicht blockiert.

## 6. Naechste read-only Probes vor Config-Aenderungen

1. Session-JSONL fuer `c398bead-a362-46ca-a764-6502d305ff61` um die Events 16-25 herum mit Tool-/lifecycle-Feldern inspizieren:
   - Gibt es dort `toolMetas`, `itemLifecycle`, `currentAttemptAssistant`, `diagnosticTrace`, `requestShaping`, `compactionCount`?
   - Ziel: beweisen, ob wirklich null Tool Calls und null in-attempt compaction vorlagen.

2. Gateway-Logs breiter um 23:56:25-00:01:56 nach diesen Strings lesen:
   - `model.call.started`, `model.call.completed`, `tool.execution`, `timeout-compaction`, `embedded run done`, `run attempt`, `planning-only`, `reasoning-only`, `empty response`.
   - Ziel: klaeren, ob das Evidence-Fenster zu stark gefiltert war.

3. Config read-only vollstaendiger projizieren:
   - `agents.defaults.timeoutSeconds`
   - agent-level `main.timeoutSeconds` oder runtime params
   - provider-level `models.providers.openai.timeoutSeconds`
   - Ziel: `params.timeoutMs=300000` exakt statt nur aus Duration/Errortext zu inferieren.

4. Live sessions/status read-only fuer Atlas um den Zeitraum pruefen:
   - Gewinner-Modell, Fallback-Kandidaten, attempt count, usage, session budget/cache.
   - Ziel: Config-Fallback, Runtime-Fallback und tatsächlichen Modellpfad getrennt belegen.

5. Vor jeder Timeout-Erhoehung mehrere Vergleichsfaelle lesen:
   - Wie oft timed out `gpt-5.4-mini` nach sichtbarem Output?
   - Gibt es Korrelation mit `cacheRead`/grossen Sessions?
   - Gibt es gleiche 300s-Timeouts ohne Tool Calls?

## Quellen im Evidence-Bundle

- `trajectory-relevant.json`: Events 16-25, Prompt, Assistant-Teiltext, Timeout-/Fallback-Versuch.
- `gateway-journal-window.log`: Zeilen 4-14, stuck-session diagnostic, Timeout, Failover, Fallback success.
- `gateway-journal-timeout-subset.log`: fokussierte Wiederholung der Timeout-/Fallback-Zeilen.
- `config-main-redacted.json`: Atlas/main Modellkette, Toolliste, sichtbare Params.
- `pi-embedded-rWtLEwl7.js`: Failover-Policy, Timeout-/Lane-Budget, Harness-Parameter, Timeout-Fallback.
- `diagnostic-oEUVZa4J.js`: Diagnostic-Klassifikation fuer aktive Tools/Model Calls/embedded runs und stuck-session recovery.
