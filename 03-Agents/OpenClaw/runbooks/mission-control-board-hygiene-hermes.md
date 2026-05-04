# Mission Control Board Hygiene & Hermes Pilot Tasks

Status: active
Owner: Atlas
Scope: Operative Regeln für Mission-Control-Task-Erstellung, Board-Hygiene und Hermes-Test-/Pilot-Tasks.
Anti-Scope: Kein Restart-/Port-3000-Recovery. Dafür separates Runbook nutzen.

## Ziel

Mission Control soll nur echte, entscheidbare Arbeit zeigen. Test-, Pilot- und Auto-Follow-up-Müll darf nicht als offene operative Arbeit liegen bleiben.

## Schnellregel

- Erstelle einen Task nur, wenn es einen klaren Owner, DoD und Verification-Pfad gibt.
- Öffne nie mehrere fast gleiche Tasks für denselben Zweck.
- Wenn ein Test/Pilot blockt: erst Ursache dokumentieren, dann entscheiden: canceln oder genau einen sauber formulierten Nachfolge-Task erstellen.
- Nach jeder Board-Mutation: Task-GET + Health/Board-Proof prüfen.

## Task erstellen: Mindeststandard

Jeder neue Task braucht:

- Eindeutigen Titel: `[P?][Area/Owner] konkretes Ziel`
- Owner/Agent: Forge, Pixel, Lens, Spark, James, Hermes etc.
- Definition of Done: prüfbar, nicht nur Absicht
- Anti-Scope: was ausdrücklich nicht gemacht wird
- Verification-Pfad: API, Test, Build, Screenshot, Report oder Datei
- Risiko-/Approval-Klasse: z.B. safe-read-only, gated-mutation, sudo-required
- Bei Worker-Tasks: Terminal Receipt mit `sprintOutcome` v1.1 und `next_actions[]`

Nicht erstellen bei:

- unklarer Zuständigkeit
- reinem Gedanken/Reminder ohne konkrete Aktion
- bereits vorhandenem gleichwertigem offenen Task
- Auto-Follow-up ohne neuen Erkenntniswert
- Test/Pilot, der nur ein Guardrail-/Adapter-Verhalten wiederholt

## Board-Status-Regeln

- `draft`: nur vorbereitete Arbeit, noch nicht zur Ausführung freigegeben.
- `assigned`: klarer Owner, aber noch nicht dispatched.
- `pending-pickup`: dispatched, wartet auf Pickup.
- `in-progress`: Worker/Agent arbeitet aktiv.
- `blocked`: offen, aber mit belastbarem `blockerReason`.
- `done`: erledigt mit Ergebnis/Receipt.
- `failed`: terminal fehlgeschlagen.
- `canceled`: bewusst geschlossen, nicht weiter bearbeiten.

Wichtig:

- Drafts sind keine operative Arbeit. Alte Drafts regelmäßig canceln/rejecten.
- Blocked Tasks brauchen einen sinnvollen Blocker-Grund, keinen Platzhalter.
- Gleicher Titel + gleicher Zweck + offen = Duplicate. Einer bleibt höchstens offen.

## Duplicate-Regel

Duplicate liegt vor, wenn mindestens zwei offene Tasks denselben Zweck erfüllen, auch wenn Beschreibung leicht variiert.

Vorgehen:

1. Beide Tasks per GET prüfen.
2. Entscheiden, welcher Task die beste Historie/den besten Scope hat.
3. Den anderen schließen:
   - normaler stale Draft: `admin-close` auf `canceled`
   - Atlas-Autonomy-Draft mit Approval-Lock: `autonomy-reject`
   - blocked/test duplicate: `admin-close` oder API-Cancel, je nach erlaubtem Transition-Pfad
4. Reason setzen: `stale/superseded/duplicate; do not dispatch`.
5. Danach Board-Proof prüfen.

## Auto-Follow-ups

Auto-materialisierte Follow-ups sind nur Vorschläge, keine Pflichtarbeit.

Behalten, wenn:

- Parent-Receipt ein echtes neues Risiko nennt
- Owner und DoD konkret sind
- Arbeit nicht bereits erledigt/superseded ist

Canceln/rejecten, wenn:

- generisch formuliert
- aus altem E2E/Pilot stammt
- kein aktueller operativer Nutzen erkennbar ist
- nur Materializer-Restmüll nach Terminal Receipts ist

Merksatz: Auto-Follow-up ist verdächtig, bis ein Mensch/Atlas den konkreten Wert bestätigt.

## Hermes: Einsatzregel

Hermes nur nutzen für:

- klar abgegrenzte read-only Reviews
- Adapter-/Pilot-Smoke-Tests
- kleine, risikoarme Validierungen

Hermes nicht nutzen für:

- Config-/Secret-/Sudo-Änderungen
- Restart/Pipeline-Eingriffe
- unscharfe Exploration ohne DoD
- Wiederholung fast identischer Guardrail-Failures

## Hermes-Test/Pilot-Task schreiben

Gute Hermes-Tasks:

- sagen explizit `read-only`
- enthalten nur notwendige Pfade/Artefakte
- haben eine kleine DoD
- enthalten Anti-Scope ohne unnötige Guardrail-Trigger-Wörter
- fordern ein klares Receipt an

Beispielstruktur:

```text
Title: [P3][Hermes Pilot] Read-only review smoke test
Objective: Perform dry-run adapter acceptance for this read-only review task only.
Definition of Done:
- Adapter dry-run returns ok=true.
- Receipt posted with result summary.
Anti-Scope:
- No file edits.
- No service lifecycle actions.
- No credential/config changes.
Return format:
- EXECUTION_STATUS
- RESULT_SUMMARY
- sprintOutcome v1.1
```

## Wenn Hermes blockt

Nicht sofort blind neu erstellen.

Checkliste:

1. Blocker lesen: War es Guardrail, Adapter, Prompt, Tooling oder echter Scope-Konflikt?
2. Ist der Task nur ein Test/Pilot?
   - Ja: canceln, wenn Erkenntnis ausreichend ist.
   - Nein: Scope korrigieren oder Owner wechseln.
3. Wenn Nachfolge nötig:
   - exakt einen neuen Task erstellen
   - Titel eindeutig ändern
   - alte blockierte Variante canceln oder klar verlinkt lassen
4. Danach Board-Proof prüfen.

## Cleanup-Prozess

Vor Cleanup:

```bash
curl -fsS http://127.0.0.1:3000/api/health | jq
curl -fsS http://127.0.0.1:3000/api/board-consistency | jq
curl -fsS http://127.0.0.1:3000/api/tasks/<id> | jq
```

Cleanup-Pfade:

- normaler Draft/Blocked/Test-Duplicate: bevorzugt API/Admin-Pfad nutzen
- Atlas-Autonomy-Draft mit Approval-Lock: `POST /api/tasks/<id>/autonomy-reject`
- wenn API Transition-Guard einen legitimen Cleanup blockiert: erst Backup, dann minimaler Live-Data-Fix, danach API/Health-Proof

Nach Cleanup:

```bash
curl -fsS http://127.0.0.1:3000/api/health | jq '.status,.checks,.metrics'
curl -fsS http://127.0.0.1:3000/api/board-consistency | jq
curl -fsS 'http://127.0.0.1:3000/api/ops/worker-reconciler-proof?limit=20' | jq
curl -fsS 'http://127.0.0.1:3000/api/ops/pickup-proof?limit=20' | jq
```

Erfolgskriterien:

- Health `status=ok`
- Board `openCount` nur echte offene Arbeit
- Board `issueCount=0`
- Dispatch `consistencyIssues=0`
- Execution `recoveryLoad=0`
- Worker/Pickup Proof ohne kritische Findings

## Harte Stopps

Stoppen und berichten, wenn:

- Mission Control API down ist und keine degraded Live-Datei reicht
- ein Cleanup Terminal-Tasks reaktivieren würde
- ein Session-/Spawn-Lock aktiv ist
- API und Live-Datei widersprüchliche Wahrheit zeigen
- Config, Secrets, Cron, Restart oder Port-3000-Pipeline betroffen wären

## Separates Runbook

Restart/Port-3000/Pipeline gehört nicht hierher. Dafür eigenes Runbook:

`Mission Control Safe Restart / Port 3000 Recovery`
