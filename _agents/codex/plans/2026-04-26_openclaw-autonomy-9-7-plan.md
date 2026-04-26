---
status: updated-after-adversarial-review
created: 2026-04-26T17:58Z
owner: codex
target: openclaw-autonomy-9.7
---

# OpenClaw Autonomie 9.7 Plan

## Live-Ist

- Atlas Kernel v1 aktiv: Budget-Proof `status=ok`, latest trajectory 10.5 KB, findings `[]`.
- Mission Control: `/api/health=ok`.
- Pickup-Proof: `status=ok`, `pendingPickup=0`, `criticalFindings=0`.
- Worker-Proof: `status=ok`, `criticalIssues=0`, ein legitimer offener `sre-expert` Run fuer Task `76a89795...`.
- Bekannter frischer Fix: Task `76a89795...` hatte kein `dispatchTarget`; minimal auf `sre-expert` gebunden, danach Auto-Pickup ok.

## Review-Korrektur 2026-04-26T18:05Z

Adversarial Review wurde eingearbeitet:

- Die Zahl `9.7/10` ist kein belastbarer Messwert. Ab jetzt wird sie nur als Zielbild-Label verwendet, nicht als Erfolgsbeweis.
- Erfolg wird ueber binäre Gates gemessen: Health ok, Pickup ok, Worker ok, Reporting-Vertrag vollstaendig, Follow-up-Drafts klassifiziert, keine unerlaubte Mutation, keine parallele Autonomie-Kette.
- Cron-Inventar braucht explizite Worker-Zuweisung. Atlas allein darf nicht nur planen; er muss sequentiell Aufgaben an passende Worker geben oder klar begruenden, warum er den read-only Teil selbst erledigt.
- Auto-Pickup-Gate-Hardening ist eine Vorbedingung fuer weitere Cron-/Heartbeat-Autonomie. Live-Stand: Task `76a89795...` ist `done`, damit ist die Sequenz wieder sauber.
- Keine weitere Follow-up-Ausfuehrung, bis die drei vom Atlas-Cron-Sprint erzeugten Drafts einzeln geprueft und priorisiert sind.

## Zielbild

Operator gibt Atlas einen groesseren Auftrag. Atlas zerlegt ihn in kontrollierte Schritte, erzeugt nur beweisbare Follow-ups, dispatcht sequentiell, stoppt bei Gates und fragt nur bei Sudo, Modellwechseln, Cron-Aktivierung oder riskanten Mutationen.

## Messbare Readiness-Gates

Das Zielbild "9.7/10" wird nicht als Metrik verwendet. Gruen ist nur, wenn alle Gates erfuellt sind:

1. `/api/health.status=ok`
2. pickup-proof `status=ok`, `criticalFindings=0`
3. worker-proof `status=ok`, `criticalIssues=0`
4. Atlas-Result enthaelt `EXECUTION_STATUS`, `RESULT_SUMMARY`, `GATES`, `FOLLOW_UPS`, `OPERATOR_DECISIONS`, `CREATED_TASKS`
5. Jeder Follow-up-Draft enthaelt `approvalClass`, `riskLevel`, Owner und Anti-Scope
6. Kein Cron-/systemctl-/Modell-/Sudo-Change ohne Operator-Go
7. Maximal eine aktive Autonomie-Kette pro Runtime-Agent
8. Abschluss erzeugt einen pruefbaren Vault-/Board-Record

## Stufe A - Reporting-Vertrag festziehen

Jeder Atlas-Result muss enthalten:

- `EXECUTION_STATUS`
- `RESULT_SUMMARY`
- `GATES`
- `FOLLOW_UPS`
- `OPERATOR_DECISIONS`
- `CREATED_TASKS`

Gate:

- Result eines echten Atlas-Sprints enthaelt alle Felder.
- Follow-ups sind als Preview/Draft oder bewusst als nicht erzeugt markiert.

## Stufe B - Autonomie-Gate vor jedem Dispatch

Vor Dispatch eines Follow-ups:

- `/api/health` ok oder begruendete Operator-Decision
- pickup-proof ok
- worker-proof criticalIssues=0
- keine zweite parallele Autonomie-Kette fuer denselben Agent
- keine offene Gate-Hardening-Arbeit, die denselben Pfad beruehrt

Gate:

- Proof-Snapshot wird im Sprint-Result referenziert.
- Wenn ein Vorlaeufer-Sprint noch aktiv ist, wird der neue Sprint nur als Draft erzeugt, nicht dispatched.

Status 2026-04-26T18:05Z:

- Auto-Pickup-Gate-Hardening `76a89795...`: done.
- Atlas Cron-Inventar-Sprint `2b6fa6d0...`: done.
- Health/Pickup/Worker nach beiden Sprints: ok.

## Stufe C - Cron/Heartbeat Inventar Sprint

Atlas orchestriert, aber die Ausfuehrung muss explizit zugewiesen sein:

- Atlas/main: Chairman, Scope, Gate-Checks, Follow-up-Drafts.
- Forge/sre-expert: Cron-/Timer-/Script-Inventar und technische Konsolidierungsanalyse.
- Lens: Modell-/Kosten-/Heartbeat-Frequenzbewertung, nur read-only.
- Codex: externer Gate-Reviewer und minimale reversible Fixes bei Proof-Fehlern.

Ausfuehrung bleibt sequentiell. Erst wenn ein Worker-Teil fertig ist, darf der naechste Follow-up dispatched werden.

Thema:
`Cron-/Heartbeat-Inventar: Welche Crons bleiben, welche sind obsolet, welche haben hoechsten Hebel, welche Heartbeats/Gates fehlen, wie wird Reporting vereinheitlicht?`

Erwartete Outputs:

- Inventar: systemd Timer + user crontab + relevante `.openclaw/scripts`
- Klassifikation: behalten / optimieren / beobachten / obsolet-vorschlag
- keine Cron-Aenderung ohne Operator-Go
- mindestens 3 Follow-up-Drafts:
  - safe-read-only Audit
  - gated-mutation Hardening
  - operator-decision fuer riskante Cron-/Modell-/Sudo-Themen

Gate:

- Atlas Sprint terminal `done`
- Worker/Pickup/Health danach gruen
- Discord-/Vault-Report vorhanden
- Mindestens ein konkretes Inventar-Artefakt oder ein Draft fuer ein Ledger existiert.

Status 2026-04-26T18:05Z:

- Sprint `2b6fa6d0...` ist done.
- Drei Drafts wurden erzeugt, aber noch nicht ausgefuehrt:
  - `3093af3d-6c60-4a85-b8cf-aec71fc1b589` - Cron/Timer Source-of-Truth Ledger, safe-read-only, main.
  - `29307251-d2bc-4b1b-ac78-f046b8442329` - m7-Kernel-Timer vs Legacy-Crons Migration-Beschluss, gated-mutation, sre-expert.
  - `0d6737ec-2cda-4e9c-996d-fe9495222c0d` - Heartbeat-Timeline / Worker-Liveness Coverage Matrix, safe-read-only, main.
- Naechster erlaubter Schritt: nur den Ledger-Draft `3093af3d...` pruefen und ggf. read-only ausfuehren. Keine parallele Ausfuehrung der anderen Drafts.

Status 2026-04-26T18:09Z:

- Ledger-Draft `3093af3d...` wurde nach Review auf `sre-expert` umgebunden und als einziger Follow-up ausgefuehrt.
- Ergebnis: `done`, keine Mutationen.
- Inventar: 26 aktive Cron-Eintraege und 12 User-Timer klassifiziert.
- Kategorien:
  - Keep: operative Kern-Crons/Timer wie `mc-ops-monitor.sh`, `memory-size-guard.sh`, `session-size-alert.sh`, `script-integrity-check.sh`, `m7-auto-pickup.timer`, `m7-worker-monitor.timer`, `m7-session-freeze-watcher.timer`, `forge-heartbeat.timer`.
  - Optimize: `qmd update`, `qmd-pending-monitor.sh`, `session-size-guard.py --log-only`, `per-tool-byte-meter.py`, `vault-search-daily-checkpoint.sh`, `qmd-native-embed-cron.sh`, `launchpadlib-cache-clean.timer`.
  - Observe: `minions-pr-watch.sh`, `cron-health-audit.sh`, `agents-md-size-check.sh`, `pr68846-patch-check.sh`, `system-handbook-refresh.timer`, `researcher-run.timer`.
  - Obsolete-suggest: kommentierte Legacy-/superseded Cron-Linien und potenziell temporaer `pr68846-patch-check.sh` nach PR-Relevanzpruefung.
- Abschluss-Gate danach:
  - pickup-proof: ok
  - worker-proof: ok
  - critical findings/issues: 0

## Stufe D - Minimaler System-Fix nur bei belegtem Gate

Codex greift nur ein, wenn:

- ein Proof kritisch rot ist
- der Fix ein einzelnes Feld oder ein kleines reversibles Script betrifft
- kein Restart/Fanout/Sudo noetig ist

## Stop-Kriterien

- offener Worker ohne Heartbeat > 15 min
- `criticalIssues > 0`
- `criticalFindings > 0`
- fehlende Receipt-Signatur
- mehr als ein neuer Child ohne Gate
- Cron-Aktivierung oder Modellwechsel ohne explizites Operator-Go

## Naechste Ausfuehrung

1. Nicht sofort weiter dispatchen.
2. Erst Ledger-Ergebnis operatorseitig pruefen.
3. Danach optional genau einen weiteren read-only Draft ausfuehren: `0d6737ec...` Heartbeat-Timeline / Worker-Liveness Coverage Matrix.
4. `29307251...` bleibt Operator-Decision/gated-mutation und wird nicht automatisch ausgefuehrt.
5. Vor jeder weiteren Ausfuehrung erneut Health/Pickup/Worker proofen.
