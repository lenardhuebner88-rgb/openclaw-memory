# OpenClaw Discord Commander Replacement Matrix (2026-05-04)

## Scope
P0-Matrix nach Abschaltung von `openclaw-discord-bot.service`.
Ziel: Legacy-Funktion -> Ersatzpfad -> Live-Test -> PASS/FAIL -> nächste Aktion.

Prüfzeit: 2026-05-04 00:02-00:04 CEST.

## Matrix
| Legacy-Funktion (Bot) | Frühere Rolle | Ersatzpfad jetzt | Live-Test (heute) | Status | Befund / Gap | Nächste Aktion |
|---|---|---|---|---|---|---|
| `/health` | MC+Host Health in Discord | MC API `GET /api/health` (+ Gateway-seitig Chat-Kommandos) | `curl /api/health` -> `status=ok` | PASS (API) | Health-Daten live; Discord-Slash UX-Ersatz nicht separat E2E belegt | Gateway-`/health` UX explizit einmal E2E screenshoten/protokollieren |
| `/status` | offene Tasks zusammenfassen | MC API `GET /api/tasks` | `curl /api/tasks?limit=20` -> valide Taskliste | PASS (API) | Datenpfad intakt | optional: kompakter read-model endpoint für Operator-Kurzstatus |
| `/agents` | Agent-Load in Discord | MC API `GET /api/board/agent-load` | liefert Agent-Load für 6 Agents | PASS (API) | Feld `ok` ist `null` (Shape inkonsistent, aber Daten da) | API-Contract bereinigen (`ok: true`) |
| `/receipts <id>` | Receipt-Tail je Task | MC API Taskdetail/Reports (`/api/tasks/:id`, task lifecycle reports) | `GET /api/tasks/:id` liefert `task`-Objekt inkl. lifecycle-Feldern (`status/dispatchState/receiptStage/...`) | PASS (API) | Response-Shape ist `{ task, drilldown }` (nicht flat) | Shape im Runbook festhalten |
| `/logs <source>` | Logs im Discord-Flow einsehbar | Host-Shell / MC ops endpoints (`/api/ops/script-health`) | `/api/ops/script-health` liefert `ok`, `summary`, `checks` | PASS | Verbraucherseitig kompatibel gemacht; altes Array-Format wird weiterhin gelesen | Optional: UI auf `summary`-KPIs umstellen |
| `/new` | Commander Session Reset | Gateway-native Command-Pfad | Code-/Runtime-Hinweise auf `/new`/`/reset` im Gateway-Stack vorhanden, aber kein frischer Discord-E2E in diesem Gate | PARTIAL | plausibel verfügbar, jedoch ohne heutigen Interaktionsbeweis | bei nächstem Operator-Command einmal E2E proofen |
| `/help` | Commander Hilfe | Gateway-native Help | Kein frischer Discord-E2E in diesem Gate | UNVERIFIED | weiterhin ohne Interaktionsbeweis | einmal E2E proofen |
| `/sprint-plan` + Buttons | Plan-Preview + Dispatch/Revise/Cancel | Soll über Atlas/Gateway Workflow laufen | Kein gleichwertiger UI-Flow heute verifiziert | FAIL (Parity) | Legacy-UI-Button-Flow ist weg; gleichwertiger Ersatz nicht belegt | P0: definieren, ob ersetzt oder offiziell retired |
| `/meeting-*` | Meeting-Orchestrierung | Script-basierter Pfad über OpenClaw/Atlas | Helper-Skripte vorhanden (`meeting-runner/status-post/turn-next`), aber kein E2E-Discord-Trigger | PARTIAL | Backend-Helfer da, aber keine belegte UX-Parität | P0: einen Meeting-E2E (start->status->turn-next) live beweisen |
| Heartbeat `mc=active bot=alive` | Liveness-Anzeige für Legacy-Bot | entfällt (Bot aus) | Service ist `inactive/disabled` | EXPECTED | bewusst entfernt | keine Aktion nötig |
| Direkter Discord-Post | zentrale Report-Zustellung | MC API `POST /api/discord/send` | `ok:true`, messageId vorhanden | PASS | Zustellpfad lebt ohne Legacy-Bot | als kanonischen Report-Pfad festhalten |

## Höchste Priorität (P0)
1. **Parity-Entscheidung für `/sprint-plan` und `/meeting-*`:**
   - Entweder als `retired` deklarieren (mit Runbook)
   - Oder Gateway/Plugin-nativ mit eindeutigen Kommandos neu aufsetzen.
2. **E2E-Beweis für 4 Operator-Kernflüsse (heute noch):**
   - health/status
   - agents
   - dispatch/approval
   - meeting lifecycle oder klar „deaktiviert“.
3. **API-Contract-Hygiene:**
   - `/api/board/agent-load` `ok`-Feld normalisieren.
   - `/api/ops/script-health` Response-Shape dokumentieren/vereinheitlichen.

## Kurzfazit
- Stabilität verbessert: Kollision durch zweiten Discord-CommandTree ist weg.
- Kritischer Infrastrukturpfad lebt: MC/Gateway + `/api/discord/send` funktionieren.
- Hauptlücke ist Feature-Parität/Operator-UX bei alten Commander-Spezialflows (`/sprint-plan`, `/meeting-*`).

## Implementationsnotiz
- `GET /api/ops/script-health` liefert jetzt einen stabilen Wrapper `{ ok, summary, checks }`.
- `ops-automations` akzeptiert sowohl das alte Array als auch den neuen Wrapper, damit die Automations-Oberfläche nicht bricht.
