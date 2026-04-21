# Worker System Hardening Plan

Datum: 2026-04-21
Scope: Dispatch -> pending-pickup -> accepted -> active -> terminal
Ziel: Weniger stille Failures, weniger Mehrfach-Trigger, klarere Ownership, bessere Recovery

## Kurzfazit

Der heutige Incident war kein Einzelfehler, sondern zeigt mehrere strukturelle Schwachstellen:

1. Dispatch, Pickup-Versuch und echter Worker-Claim sind im aktuellen Modell nicht sauber getrennt.
2. Auto-Pickup und Worker-Monitor teilen sich Teile derselben Recovery-Verantwortung.
3. Receipt-/Retry-Pfade erlauben heute noch zu viel semantisches Rauschen und zu wenig Provenance.
4. Monitoring und Logs zeigen Symptome, aber nicht die kausale Kette pro Spawn-Versuch.

Der bereits umgesetzte Open-Run-Guard stoppt die konkrete Mehrfach-Trigger-Schleife, behebt aber nicht die tieferen Modell- und Ownership-Probleme.

## Findings

### F1 — Run-Placeholder und echter Pickup sind semantisch vermischt

Evidence:

- `dispatchTask()` erzeugt den `worker-runs.json`-Eintrag bereits beim Dispatch, vor jedem Receipt:
  - `/home/piet/.openclaw/workspace/mission-control/src/lib/task-dispatch.ts:127`
  - `/home/piet/.openclaw/workspace/mission-control/src/lib/task-dispatch.ts:281`
- Der Task bleibt danach absichtlich in `status=pending-pickup`:
  - `/home/piet/.openclaw/workspace/mission-control/src/lib/task-dispatch.ts:286`

Risiko:

- Ein offener Run bedeutet heute nur "Dispatch hat einen Placeholder geschrieben", nicht "Worker hat real aufgenommen".
- Operatoren und Automationen koennen daraus falsche Schluesse ziehen.

### F2 — Pending-pickup hat keinen einzigen klaren Owner

Evidence:

- `auto-pickup.py` triggert pending-pickup Tasks direkt.
- `worker-monitor.py` faellt pending-pickup nach Timeout:
  - `/home/piet/.openclaw/workspace/scripts/worker-monitor.py:1097`
- `worker-monitor.py` spawned in Retry-/Bridge-Pfaden selbst wieder Workers:
  - `/home/piet/.openclaw/workspace/scripts/worker-monitor.py:1601`
  - `/home/piet/.openclaw/workspace/scripts/worker-monitor.py:1622`
  - `/home/piet/.openclaw/workspace/scripts/worker-monitor.py:1679`

Risiko:

- Doppel-Owner fuehren zu Retrigger-Rennen, Event-Rauschen und schwer debugbaren Zwischenzustaenden.

### F3 — Retry-Decision Events koennen geschrieben werden, bevor der Terminal-Schritt wirklich gilt

Evidence:

- `/fail` schreibt `retry-decision` vor `applyWorkerTerminalCallback()`:
  - `/home/piet/.openclaw/workspace/mission-control/src/app/api/tasks/[id]/fail/route.ts:51`
  - Konflikt wird erst danach behandelt:
  - `/home/piet/.openclaw/workspace/mission-control/src/app/api/tasks/[id]/fail/route.ts:93`

Risiko:

- Board-Events koennen "Retry geplant" zeigen, obwohl die eigentliche Mutation in einen Konflikt lief.
- Das erzeugt False Positives in Timeline, Reports und RCA.

### F4 — Receipt-Provenance ist zu schwach

Evidence:

- Receipt-Ingress verlangt nur `actorKind in {automation, system}` und `requestClass=system`:
  - `/home/piet/.openclaw/workspace/mission-control/src/app/api/tasks/[id]/receipt/route.ts:241`
- Die Auto-Promotion `pending-pickup -> in-progress` passiert auf dem ersten nicht-terminalen Receipt:
  - `/home/piet/.openclaw/workspace/mission-control/src/app/api/tasks/[id]/receipt/route.ts:618`
- `workerSessionId` wird nur syntaktisch ueber Prefix validiert:
  - `/home/piet/.openclaw/workspace/mission-control/src/lib/worker-session-id.ts:1`

Risiko:

- Ein "formal gueltiger" Receipt kann den Task aktivieren, ohne dass der Spawn-Versuch selbst eindeutig nachgewiesen ist.
- Das beguenstigt manuelle "Geradezieh"-Aktionen, die die echte Fehlerkette verdecken.

### F5 — Gateway-Placeholder bleibt im Ownership-Modell ueberladen

Evidence:

- Gateway-Placeholder gelten in Ownership-Konflikten als Sonderfall:
  - `/home/piet/.openclaw/workspace/mission-control/src/lib/task-terminal-guards.ts:15`
- `syncWorkerRunBinding()` muss Placeholder spaeter als failed schliessen, wenn ein echter Worker uebernimmt:
  - `/home/piet/.openclaw/workspace/mission-control/src/lib/worker-terminal-callback.ts:137`

Risiko:

- Placeholder und echter Worker teilen sich denselben semantischen Raum.
- Rebind-, Terminal- und Recovery-Code muessen Sonderregeln stapeln statt auf einem klaren Modell aufzubauen.

### F6 — Timeout-Politik ist verteilt und unvollstaendig

Evidence:

- `worker-monitor.py` hat agent-spezifische accepted timeouts:
  - `/home/piet/.openclaw/workspace/scripts/worker-monitor.py:38`
- `sre-expert` fehlt dort explizit und faellt auf `default=15`:
  - `/home/piet/.openclaw/workspace/scripts/worker-monitor.py:529`

Risiko:

- Wichtige Agents nutzen implizite Defaults statt bewusst definierter SLA-Werte.
- Analyse- oder Infra-Tasks koennen zu frueh oder zu spaet eskalieren.

### F7 — `worker-pickups` kann blocked-Zustaende wieder als ready anbieten

Evidence:

- `blocked`-Receipt laesst `dispatchState=dispatched` stehen:
  - `/home/piet/.openclaw/workspace/mission-control/src/app/api/tasks/[id]/receipt/route.ts:334`
- `worker-pickups` markiert alles als ready, solange kein echter Worker gebunden ist und `executionState` nicht `done/failed` ist:
  - `/home/piet/.openclaw/workspace/mission-control/src/app/api/worker-pickups/route.ts:29`

Risiko:

- Ein blocked Task kann wieder als pickup-faehig erscheinen.
- Das ist ein Ownership-Leak zwischen "wartet auf Dependency" und "darf wieder gestartet werden".

### F8 — Observability zeigt Symptome, aber nicht die Kausalkette je Attempt

Evidence:

- Auto-Pickup hat Log/Alerting fuer Immediate Exit und Silent Fail, aber keinen stabilen `attemptId`, der Dispatch, Lock, Logfile, Receipt und Run zusammenhaelt.
- Historisch wurde genau dieser Silent-Fail-Pfad bereits als Produktionsmuster dokumentiert:
  - `/home/piet/vault/03-Agents/morning-recovery-report-2026-04-20.md:55`

Risiko:

- RCA braucht heute Quervergleiche zwischen `tasks.json`, `worker-runs.json`, `board-events.jsonl`, `auto-pickup.log`, `auto-pickup-runs/*.log`, Session-Files.
- Das ist zu teuer und zu fehleranfaellig fuer Live-Ops.

## Zielbild

Das Worker-System soll auf 4 Wahrheiten aufgebaut werden:

1. Dispatch ist nicht Pickup.
2. Pickup ist nicht Acceptance.
3. Acceptance ist nur gueltig mit Spawn-Provenance.
4. Genau ein Prozess owns jeden Lifecycle-Abschnitt.

## Bewertung der Atlas-Aussage

Atlas' Aussage ist als Interims-Betriebsregel teilweise gut, aber an mehreren Stellen zu optimistisch.

### Korrekt und beibehalten

- `Board-first` ist richtig.
- `GET-Verify nach jedem Write` ist richtig.
- `Dispatch != Pickup` ist richtig.
- `Recovery statt Blind-Retry` ist richtig.
- `Operator-Lock bleibt massgeblich` ist governance-seitig richtig.

### Nur als Interims-Regel korrekt, nicht als Endzustand

- `pending-pickup + open run -> nicht retriggern`
  - Das ist nach dem aktuellen Guard-Fix operativ die richtige Sofortregel.
  - Es ist aber noch kein sauberes Endmodell, weil ein offener Run heute weiterhin auch nur ein Dispatch-Placeholder sein kann.

- `pending-pickup + kein open run -> Pickup darf angestossen werden`
  - Operativ brauchbar, aber unvollstaendig.
  - Es fehlen weiterhin Provenance-, Lock-, Timeout- und Recovery-Pruefungen.

### In der Aussage zu optimistisch oder technisch zu kurz

- `kein mehrfaches Auto-Pickup auf denselben Task mehr`
  - Fuer den konkreten Auto-Pickup-Retrigger-Pfad jetzt deutlich besser.
  - Systemweit aber noch nicht voll belastbar, weil Split-Ownership zwischen `auto-pickup` und `worker-monitor` weiter existiert.

- `terminale Tasks ... nie neu anwerfen`
  - So absolut ist das nicht korrekt.
  - `failed`-Tasks duerfen ueber explizite Recovery-/Retry-Pfade wieder in einen sauberen Lebenszyklus ueberfuehrt werden.
  - Richtig waere: terminale Tasks nie blind neu anwerfen, nur ueber einen expliziten Recovery-Pfad.

### Was in Atlas' Aussage noch fehlt

- Keine Aussage zur zu schwachen Receipt-Provenance.
- Keine Aussage zum `retry-decision`-Rauschen vor Konfliktpruefung.
- Keine Aussage dazu, dass `worker-pickups` blocked-Zustaende wieder als ready anbieten kann.
- Keine Aussage zur fehlenden Zentralisierung der Timeout-Politik.

## Interims Operations Standard

Bis die Architektur-Haertung umgesetzt ist, sollte Atlas nach diesem engeren Standard fahren:

1. Board-first und GET-Verify nach jedem mutierenden API-Call.
2. `dispatch` nur als Queue-/Trigger-Schritt lesen, nie als Arbeitsbeginn.
3. `accepted|started|progress` nie manuell als Worker-Ersatz "geradeziehen"; dafuer nur explizite Recovery-Pfade verwenden.
4. `pending-pickup + open run` nicht retriggern, sondern monitoren und gezielt recovern.
5. Terminale Tasks nie blind neu starten; nur ueber einen expliziten Recovery-/Retry-Pfad.
6. Bei jeder RCA immer Task-State, board-events, worker-runs und den konkreten Attempt zusammen lesen.

## Priorisierter Plan

### Phase 1 — Lifecycle Truth entflechten

Prioritaet: P0
Aufwand: 1 Tag

Massnahmen:

- Fuehre einen expliziten `pickupState` ein:
  - `not-triggered`
  - `triggered`
  - `accepted`
  - `active`
  - `terminal`
- Trenne in `worker-runs.json` zwischen:
  - `kind=dispatch-placeholder`
  - `kind=spawn-attempt`
  - `kind=worker-run`
- Dispatch soll nicht mehr stillschweigend wie ein echter Run aussehen.
- `workerSessionId` auf dem Task bleibt leer, bis ein echter Claim vorliegt.

Definition of Done:

- Kein Dashboard/Operator kann einen Dispatch-Placeholder mehr mit einem echten Worker-Claim verwechseln.
- RCA fuer einen Task zeigt klar: wann dispatch, wann trigger, wann accepted, wann progress.

### Phase 2 — Single Owner fuer pending-pickup

Prioritaet: P0
Aufwand: 1 Tag

Massnahmen:

- Entscheide klar:
  - `auto-pickup` owns trigger/retrigger
  - `worker-monitor` owns observe/alert/fail
- `worker-monitor` darf pending-pickup nicht mehr direkt re-spawnen.
- Retry-Spawn fuer Specialists nur ueber einen klaren Recovery-Endpunkt, nicht ueber verstreute Sonderpfade.
- `worker-pickups` darf nur `status=pending-pickup` und nicht `blocked` wieder anbieten.

Definition of Done:

- Fuer einen pending-pickup Task gibt es nur noch einen aktiven Trigger-Owner.
- Kein doppelter Spawn desselben Tasks aus zwei unterschiedlichen Daemons.

### Phase 3 — Receipt Provenance haerten

Prioritaet: P0
Aufwand: 1 Tag

Massnahmen:

- Dispatch generiert eine `attemptId` plus kurzlebiges Claim-Token.
- Jeder erste nicht-terminale Receipt muss `attemptId` oder Claim-Token zurueckliefern.
- `accepted` ohne gueltige Attempt-Provenance wird mit `409` abgelehnt.
- Fuer Operator-Reparaturen neuen Pfad einfuehren:
  - `POST /api/tasks/:id/admin-recover`
  - niemals synthetischen Worker-Receipt als Ersatz fuer Recovery schreiben

Definition of Done:

- Manuelles "Geradeziehen" kann nicht mehr wie echter Worker-Claim aussehen.
- Der erste gueltige `accepted` ist immer auf genau einen Trigger-Versuch rueckfuehrbar.

### Phase 4 — Retry- und Event-Hygiene

Prioritaet: P1
Aufwand: 0.5 Tag

Massnahmen:

- `retry-decision` erst nach erfolgreicher terminaler Mutation schreiben.
- Neue Event-Typen trennen:
  - `retry-planned`
  - `retry-applied`
  - `retry-skipped-conflict`
- Konflikte duerfen keine success-aehnlichen Retry-Signale mehr erzeugen.

Definition of Done:

- Board-Event-Stream ist kausal korrekt.
- Keine Retry-Events mehr fuer 409-Konfliktfaelle.

### Phase 5 — Timeout-Policy zentralisieren

Prioritaet: P1
Aufwand: 0.5 Tag

Massnahmen:

- Eine zentrale Timeout-Config fuer:
  - accepted timeout
  - progress heartbeat timeout
  - stale active timeout
  - orphan confidence window
- Explizite Eintraege fuer:
  - `sre-expert`
  - `frontend-guru`
  - `efficiency-auditor`
  - `james`
  - `spark`
  - `main`
- Optional task-spezifische Overrides nur noch ueber ein einheitliches Feld, nicht implizit aus Beschreibungstext.

Definition of Done:

- Kein produktiver Agent faellt mehr auf einen impliziten Default zurueck.
- Timeout-Aenderungen brauchen genau eine zentrale Anpassung.

### Phase 6 — Observability je Attempt

Prioritaet: P1
Aufwand: 1 Tag

Massnahmen:

- Fuehre `attemptId` ueber alle Artefakte:
  - board event
  - worker run
  - auto-pickup log
  - out log
  - receipt payload
- Neue Kennzahlen:
  - dispatch->trigger latency
  - trigger->accepted latency
  - accepted->first-progress latency
  - open-run age
  - manual recoveries
  - retry-conflict count
- Monitoring-View fuer "stuck pickup" und "stuck accepted but no progress".

Definition of Done:

- Ein Incident laesst sich pro Attempt in unter 2 Minuten rekonstruieren.
- Kein Grep ueber 5 verschiedene Files mehr noetig, um die Trigger-Kette zu verstehen.

### Phase 7 — Test-Backbone

Prioritaet: P0
Aufwand: 1 Tag parallel zu Phase 1-6

Pflichttests:

- delayed-pickup with open run -> kein Retrigger
- blocked task darf nicht erneut in `worker-pickups` als ready auftauchen
- `/fail` schreibt kein `retry-decision`, wenn terminal callback konfliktet
- forged `accepted` ohne gueltige attempt provenance wird abgelehnt
- echter worker rebind von gateway-placeholder bleibt erlaubt
- worker-monitor und auto-pickup koennen denselben Task nicht doppelt triggern

Definition of Done:

- Fuer jeden oben genannten Failure-Mode existiert mindestens ein enger Regressionstest.

## Empfohlene Reihenfolge

1. Phase 2 zuerst: Single Owner fuer pending-pickup.
2. Direkt danach Phase 3: Receipt Provenance.
3. Dann Phase 1: Lifecycle Truth sauber modellieren.
4. Parallel Phase 7: Regressionstests.
5. Danach Phase 4-6 fuer Hygiene und Ops.

## Kleinste sinnvolle naechste 3 Umsetzungen

Wenn nur die kleinsten robusten Schritte sofort umgesetzt werden sollen:

1. `worker-pickups` so aendern, dass nur `status=pending-pickup` pickup-ready sein kann.
2. `/fail` so aendern, dass `retry-decision` erst nach erfolgreichem terminal callback geschrieben wird.
3. Einen `attemptId` bereits jetzt im Auto-Pickup einfuehren und in Log + Receipt + worker-runs spiegeln.

## Erfolgskriterien

- Keine Mehrfach-Trigger-Schleifen fuer denselben Task.
- Keine false-positive Retry-Events.
- Kein blocked Task wird still wieder pickup-ready.
- Kein `accepted` ohne Spawn-Provenance.
- RCA fuer einen Pickup-Incident dauert < 2 Minuten.
