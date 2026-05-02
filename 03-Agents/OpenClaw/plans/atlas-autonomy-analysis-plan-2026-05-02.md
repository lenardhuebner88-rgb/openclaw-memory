# Atlas Autonomie — Deep Analysis & Hardening Plan

Stand: 2026-05-02 23:00 Europe/Berlin
Owner: Atlas
Scope: Autonomie-Fähigkeiten, was funktioniert, Grenzen, Härtungsbedarf, Umsetzungsplan.

## 1. Aktueller Live-Stand

Live-Proof zum Analysezeitpunkt:
- Mission Control `/api/health`: ok
- Worker-Reconciler-Proof: ok, keine Issues
- Pickup-Proof: ok, keine Findings
- Aktive echte Worker-Ausführung: Forge-Task `e630c283-33a5-4d66-92ba-c2420878017b` für Cron-Reroute zu System Bot, `pending-pickup`/`dispatched`
- Mehrere Draft-Follow-ups vorhanden, aber nicht autonom weitergezogen.

Relevante Runtime-Regeln:
- Autonomy Ladder: Preview finding → proposed action → dispatch one bounded task → wait receipt → follow-up preview.
- Safe Autonomy Lane: P2/P3 Analyse, Triage, Verification, Cleanup, Doku, kleine Bugfixes erlaubt, aber nur mit Duplicate Scan, DoD, Anti-Scope, Low Risk, Verify-after-write.
- Hard Stops: keine Cron/Gateway/Restart/Model-Routing-Mutation ohne approved task; keine terminal-task worker reruns; locks respektieren.

## 2. Was Atlas bereits kann

### 2.1 Wahrnehmen / Orientieren
- Live-State lesen: MC Health, Worker Proof, Pickup Proof, Task API, Board Events, lokale Dateien.
- Memory/Vault-Kontext abrufen und mit Live-Proofs abgleichen.
- Zwischen altem Bericht und aktuellem Zustand unterscheiden.
- Degraded Mode verwenden, falls Mission Control API down ist.

### 2.2 Entscheiden / Planen
- Aufgaben clustern nach Agent-Fit: Forge Infra, Pixel UI, Lens Audit/Kosten, Spark klein/ideen, James Research.
- Scope, DoD, Anti-Scope, Owner, Risiko und Verifikation in Worker-Aufgaben formulieren.
- Bounded tasks erstellen und dispatchen.
- Bei riskanten Mutationen stoppen oder Operator-Entscheidung einholen.

### 2.3 Handeln / Delegieren
- Mission-Control-Tasks per API erstellen.
- Tasks dispatchen und anschließend live verifizieren.
- Receipts prüfen, gegen Live-State validieren, nächste Aktionen ableiten.
- Niedrigrisiko-Hygiene durchführen, wenn klare Operatorfreigabe oder Safe-Lane greift.

### 2.4 Kontrollieren / Nachhalten
- Proofs nach Write ausführen.
- Worker- und Pickup-Invarianten prüfen.
- Board-Hygiene wiederherstellen, wenn Blocker nicht mehr real sind.
- Daily/Vault-Checkpoint schreiben.

## 3. Was bereits funktioniert

### Funktioniert stabil
- Board-first Delegation: Tasks mit DoD/Anti-Scope werden sauber angelegt und dispatched.
- Live-Proof statt Bauchgefühl: Health/worker/pickup proofs sind nutzbar und grün.
- Receipt Review: Forge-Ergebnisse können geprüft und daraus konkrete Folgeaktionen abgeleitet werden.
- Safe-Lane Guardrails: Atlas macht nicht blind Cron/Restart/Config, sondern erstellt approved/bounded Tasks.
- Silent Heartbeat Standard: Ohne Anlass bleibt Atlas billig und ruhig.
- Agent-Routing: Fachliche Zuordnung funktioniert praktisch gut.
- Runtime-ID-Disziplin: `system-bot`, `sre-expert`, `main` werden bewusst getrennt.

### Funktioniert teilweise
- Follow-up-Materialisierung: Drafts entstehen, aber brauchen noch bessere Priorisierung/Dedupe, damit keine Draft-Halde entsteht.
- Autonome Blocker-Auflösung: Funktioniert, wenn Blocker live widerlegt werden können; braucht bessere Norm, wann `blocked -> done` erlaubt ist.
- Cron/Model-Hygiene: Analyse funktioniert, Umsetzung braucht wegen Risiko weiterhin bounded Forge-Task.
- Budget-/Kostensteuerung: Modelle sind erkennbar, aber Autonomie entscheidet noch nicht vollständig dynamisch nach Kostenklasse.

## 4. Was noch nicht ausreichend funktioniert / Grenzen

### 4.1 Atlas ist kein freier Autopilot
Atlas kann nicht unbegrenzt selber handeln. Das ist gewollt. Aktuelle Grenze:
- Keine eigenmächtige Änderung an Gateway, Cron, Model-Routing, Secrets, Auth, sudo, Restart.
- Keine Massenschließung oder blindes Redispatch.
- Keine Ausführung auf terminalen Tasks.
- Keine externen Downloads/Installationen ohne Review/Freigabe.

### 4.2 Autonomie ist noch zu prompt-/regelgetrieben
Viele Entscheidungen hängen an HEARTBEAT.md/AGENTS.md und Task-Prompts. Es fehlt noch eine zentrale, maschinenlesbare Policy-Engine:
- Was darf Atlas selbst?
- Was braucht Operator-Freigabe?
- Was darf nur Forge?
- Was ist strikt verboten?

### 4.3 Follow-up-Drafts können Rauschen erzeugen
Aktuell existieren Drafts, die nicht automatisch priorisiert/geschlossen werden. Risiko:
- Board sieht voller aus als operative Realität.
- Atlas muss manuell unterscheiden: wertvoller Follow-up vs. stale Draft.

### 4.4 E2E-Autonomie-Gates sind noch nicht vollständig standardisiert
Für Code/Infra existieren Gate-Muster, aber noch kein einheitlicher Autonomie-Gate-Runner:
- Duplicate scan
- Risk classification
- Lock check
- Dispatch sanity
- Receipt schema check
- Live proof
- Cost proof
- Board proof

### 4.5 Heartbeats sind bewusst zu konservativ
Aktueller Heartbeat darf hauptsächlich lesen und `HEARTBEAT_OK` liefern. Das schützt Kosten/Risiko, begrenzt aber proaktive Wirkung. Wenn mehr Magie gewünscht ist, braucht es explizite Rungs mit Budget/Rate/Grenzen.

## 5. Was Atlas benötigt

### Kurzfristig
- Eine explizite Autonomie-Matrix als Source of Truth.
- Einheitliches Task-Template für autonome Tasks.
- Follow-up-Triage-Job: Drafts deduplizieren, priorisieren, stale schließen nur mit Regeln.
- Receipt- und Proof-Check als wiederverwendbares Script.

### Mittelfristig
- Autonomy Controller: maschinenlesbare Policy + Gate-Runner vor jeder Aktion.
- Budget-Guard pro Autonomie-Lane.
- Risk Classifier mit festen Eskalationspfaden.
- Autonomy Dashboard in Mission Control: was Atlas darf, was pending approval ist, was blockiert ist.

### Langfristig
- Multi-step TaskFlow für dauerhafte Ziele mit Zustand, Wartebedingungen und Receipts.
- Regression-Suite für Autonomie: simulierte Tasks, Locks, Failures, Receipts, stale sessions.
- Autonome Sprint-Planung nur mit operator-approved objectives und Stop-Loss.

## 6. Härtungsplan

### Phase 0 — Baseline & Wahrheit sichern
DoD:
- Current autonomy policy in einem kurzen SSOT-Dokument.
- Liste aller erlaubten/verbotenen Aktionen.
- Live-Proof-Baseline dokumentiert.

Tasks:
1. `atlas-autonomy-policy-matrix-v1` erstellen.
2. Existing rules aus HEARTBEAT/AGENTS/rules-query konsolidieren.
3. Hard-stop-Liste maschinenlesbar machen.

### Phase 1 — Gate-Runner bauen
DoD:
- Ein Script/Endpoint prüft vor autonomer Aktion: duplicate, lock, risk, owner, scope, DoD, anti-scope, budget, proof path.

Tasks:
1. `autonomy-preflight-check` implementieren.
2. Resultat: `allow | require-approval | deny`.
3. Tests für sichere, riskante und verbotene Fälle.

### Phase 2 — Follow-up-Hygiene
DoD:
- Draft-Follow-ups werden nicht blind dispatcht, sondern triagiert.
- Stale/duplicate Drafts werden markiert oder zur Entscheidung vorgelegt.

Tasks:
1. Follow-up classifier: duplicate/stale/actionable/operator-needed.
2. Board report mit Top 5 nächsten sinnvollen Aktionen.
3. Keine auto-close ohne klare Regel und proof.

### Phase 3 — Autonome Safe-Lane erweitern
DoD:
- Atlas darf P3/P2 Readonly/Triage/Doku/kleine Cleanup-Tasks mit Gate-Runner selbst dispatchen.
- Mutationen nur wenn policy erlaubt und E2E-Proof klar ist.

Tasks:
1. Safe-Lane Playbooks je Agent.
2. Standard-Receipts je Tasktyp.
3. Budget cap und max actions per heartbeat/day.

### Phase 4 — Operator-Control Surface
DoD:
- Operator sieht und steuert Autonomie klar in MC.

Tasks:
1. Autonomy dashboard: allowed actions, pending approvals, last autonomous actions, cost.
2. Approve/deny/defer Buttons für Vorschläge.
3. Audit log für jede autonome Entscheidung.

### Phase 5 — Regression & Chaos
DoD:
- Autonomie kann gegen simulierte Failures getestet werden.

Tasks:
1. Test cases: lock conflict, terminal task, missing receipt, stale worker, degraded MC, bad diff, budget exceeded.
2. CI/local proof command.
3. Red-team run pro Sprint.

## 7. Priorisierte nächste Schritte

Empfehlung Reihenfolge:
1. Phase 0: Autonomy Policy Matrix v1.
2. Phase 1: Preflight/Gate-Runner.
3. Phase 2: Follow-up-Draft-Triage.
4. Danach erst mehr autonome Handlungsfreiheit.

## 8. Akzeptanzkriterien für “Atlas Autonomie v1 gehärtet”

- Jede autonome Aktion hat: policy decision, task id, owner, DoD, anti-scope, proof result, receipt.
- Keine Mutation ohne erlaubte Klasse oder Operatorfreigabe.
- Keine Aktion auf terminalen Tasks.
- Keine Session-Lock-Konflikte werden retryt.
- Board bleibt grün: issueCount=0, consistencyIssues=0, worker/pickup proofs ok.
- Kosten bleiben unter definiertem Cap.
- Operator kann Autonomie jederzeit stoppen oder einschränken.
