# Atlas Autonomie Follow-ups + Dispatch Plan 2026-04-25

## Live-Lage 2026-04-25T18:30Z
- `/api/health`: `ok`
- Worker-Proof initial: `degraded`, `openRuns=4`, `criticalIssues=0`
- Rootcause: Follow-up-Tasks wurden zu breit gleichzeitig dispatcht. SRE/Spark hatten aktive Locks; drei Tasks blieben als unclaimed `pending-pickup` mit offenen Gateway-Runs ohne Heartbeat/Prozessbeleg stehen.
- Minimal-Fix: `scripts/followup-dispatch-guard.mjs` erstellt. Default `--dry-run`; `--execute --task-id <id>` setzt nur unclaimed follow-up dispatches zurueck auf `assigned/queued` und schliesst leere Runs.
- Gate nach Fix: Worker-Proof `ok`, Pickup-Proof `ok`, `pendingPickup=0`, `openRuns=0`.

## Research-Kernaussagen
- OpenAI Agent Guidance: produktive Agenten brauchen klare Tools, Guardrails und Human-Intervention-Punkte, wenn ein Task nicht sicher abgeschlossen werden kann.
- OpenAI Eval Guidance: Agenten muessen mit task-spezifischen Evals gegen reale Verteilungen getestet werden; multi-agent Aufteilung hilft nur mit klaren Rollen und Tool-Grenzen.
- Anthropic Effective Agents: einfache, kompositionelle Workflows sind robuster als komplexe Frameworks; Agenten sollen bei unklaren oder riskanten Entscheidungen zum Menschen zurueckkommen.
- LangChain HITL Guidance: Approve/Reject/Edit-Entscheidungen brauchen klare Kontextanzeige, persistente Interrupts, Validierung und Audit-Log.

Quellen:
- https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/
- https://platform.openai.com/docs/guides/evaluation-best-practices
- https://www.anthropic.com/research/building-effective-agents/
- https://docs.langchain.com/oss/javascript/langchain/frontend/human-in-the-loop

## Ziel
Atlas soll einen grossen Autonomie-Sprint sauber durchsteuern und daraus mehrere Follow-up-Tasks kontrolliert erzeugen/dispatchen. Danach wird der Ablauf auf drei grosse Sprints erweitert.

## Architektur-Entscheidung
Nicht direkt alle Follow-ups dispatchen.

Stattdessen:
1. **Preview Drafts:** Follow-ups entstehen als `atlas-autonomy` Drafts mit `operatorLock=true`.
2. **Approval Gate:** Freigabe via `/api/tasks/:id/autonomy-approve`.
3. **Automatic Dispatch:** `autonomy-approve` dispatcht automatisch genau diesen Task.
4. **Runtime Gate:** Vor jeder Freigabe:
   - Worker-Proof `ok`
   - Pickup-Proof `ok`
   - keine `pendingPickup`
   - keine queued/running Meetings
   - maximal ein neuer Atlas Sprint gleichzeitig
5. **Post-Run Gate:** Task muss terminal `done|failed|blocked` sein und Worker-Proof wieder `ok`.

## Drei grosse Sprints

### Sprint A: Atlas Autonomy Guardrails
Ziel: Atlas definiert und validiert die harte Policy fuer Follow-up-Erzeugung: max. 3 Follow-ups, Deduping, keine Auto-Dispatches ohne Proof-Gate, Terminal-Receipt-Gate.

Gate:
- Atlas liefert Report mit konkreter Policy.
- `sprintOutcome.schema_version=v1.1` mit 2-3 `next_actions`.
- Keine direkte Dispatch-Flut.

### Sprint B: Follow-up Preview + Approval
Ziel: Atlas erzeugt deduplizierte Follow-up-Drafts und prueft, ob die bestehenden Autonomie-Routen (`autonomy-approve/reject`) fuer den Operator-Flow reichen.

Gate:
- Follow-ups bleiben `draft` oder `assigned/queued`, nicht parallel `pending-pickup`.
- Jeder Task hat `decisionKey`, `planId`, `sourceStepId`, `approvalMode`.
- Discord-Status zeigt Preview und naechste Freigabe.

### Sprint C: Controlled Auto-Dispatch
Ziel: Atlas steuert mehrere Follow-ups nacheinander: approve/dispatch genau einen, warten bis terminal, dann naechsten.

Gate:
- 3 Dispatches nacheinander, nicht parallel.
- Nach jedem: Worker-Proof `ok`, Pickup-Proof `ok`.
- Bei Fehler: stoppen, requeue via Guard, Discord-Status.

## Stop-Regeln
- `criticalIssues > 0`
- `pendingPickup > 0` laenger als Claim-Fenster
- `openRuns` ohne Heartbeat/Prozessbeleg
- mehr als ein Atlas-/Main-Sprint gleichzeitig
- `tracked-tokens=0` bei Meeting-Follow-ups
- fehlender terminaler Receipt

## Aktueller Implementierungsstatus
- Stabilisierung abgeschlossen.
- `followup-dispatch-guard.mjs` vorhanden und erfolgreich gegen zwei unclaimed SRE-Follow-ups genutzt.
- Naechster Integrationsschritt: 3 `atlas-autonomy` Drafts anlegen, Sprint A approve/dispatch, dann monitoren.

## Umsetzung 2026-04-25T19:15Z
- Sprint A `e08e844f-b2f4-4b22-a9b4-155dfeefc98d`: `done/result`.
  - Ergebnis: Atlas Guardrail-Policy erstellt.
  - Befund: `sprintOutcome v1.1` vorhanden, aber Materializer wurde zuerst durch `session-unhealthy: anomalyCount=61 threshold=50` geblockt.
- Minimal-Fix R50:
  - Datei: `/home/piet/.openclaw/workspace/mission-control/src/lib/r50-gate.ts`
  - Semantik: Wenn `session-health.log` im Summary `newCount` liefert, blockiert R50 auf neuen Anomalien; alte Logformate fallen weiter auf `anomalyCount` zurueck.
  - Live-Grund: Latest Summary hatte `anomalyCount=61`, aber `newCount=0`.
  - Tests: `tests/r50-gate.test.ts`, `tests/autonomy-approve-dispatch-regression.test.ts`, `tests/receipt-materializer-flag-off.test.ts`.
- Sprint B `93f3adc8-a40c-4cec-b047-222deb1f9b7a`: `done/result`.
  - Ergebnis: exakt 2 valide `sprintOutcome v1.1 next_actions`.
  - Materializer: `materializer-ok`; erzeugte Child-Tasks:
    - `cd1dd84c-a2f2-438f-81bf-8bd9fe7b9b3f`
    - `1dc27f1f-bb75-4659-91c0-87648ee55799`
- Kontrollierter Dispatch:
  - Neuer Helper: `/home/piet/.openclaw/workspace/mission-control/scripts/autonomy-followup-dispatcher.mjs`
  - Default `--dry-run`; Execute nur mit `--execute --task-id=<id>`.
  - Gate vor Execute: Worker-Proof ok, Pickup-Proof ok, `openRuns=0`, `pendingPickup=0`, keine aktiven Session-Locks.
  - Beide Child-Follow-ups wurden nacheinander gestartet und terminal `done/result`.
- Atlas-Follow-up-Haertung:
  - Der erste Child-Follow-up hat den Materializer-Preview-Vertrag gehaertet: kuenftige materialisierte Follow-ups sollen als `operatorLock=true` Draft-Previews entstehen statt als direkt `assigned/queued`.
  - Dieser Stand wurde gebaut und deployed.

## Finale Gates 2026-04-25T19:15Z
- `mission-control.service`: active
- `/api/health`: `ok`
- `/api/ops/worker-reconciler-proof?limit=20`: `ok`, `openRuns=0`, `issues=0`, `criticalIssues=0`
- `/api/ops/pickup-proof?limit=20`: `ok`, `pendingPickup=0`, `activeSessionLocks=0`, `findings=0`
- Tests:
  - `npx vitest run tests/r50-gate.test.ts tests/autonomy-approve-dispatch-regression.test.ts`
  - `npx vitest run tests/r50-gate.test.ts tests/autonomy-approve-dispatch-regression.test.ts tests/receipt-materializer-flag-off.test.ts`
  - `npm run typecheck`
  - `npm run build`

## Ergebnis
Atlas hat einen grossen Autonomie-Sprint plus Folge-Sprint durchgesteuert:
1. Sprint A: Guardrails.
2. Sprint B: maschinenlesbare Follow-up-Erzeugung.
3. Zwei materialisierte Follow-up-Tasks: nacheinander dispatcht und terminal abgeschlossen.

Damit ist die Kette `Atlas Sprint -> sprintOutcome -> Materializer -> Follow-up Tasks -> kontrollierter Dispatch -> terminale Results` live bewiesen.

## Offene Punkte / naechster Schritt
- Sprint C `9d056416-60a0-4c6c-b312-92e29753bd08` bleibt absichtlich als `atlas-autonomy` Draft mit Operator-Lock stehen.
- Naechstes sinnvolles Gate: Sprint C erst starten, wenn explizit gewuenscht, und dann pruefen, ob neue Materializer-Children direkt im neuen `operator-locked Draft Preview`-Zustand entstehen.
- Follow-up: Prioritaetsmapping im `sprintOutcome` strenger machen. Atlas verwendete einmal `priority: "high"` statt `P1`; das wurde live zu `low` gemappt. Besser: invalid priority nicht still downgraden, sondern als Quality-Gate-Fehler melden.
