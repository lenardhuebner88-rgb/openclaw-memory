# MC Audit P4 Follow-up Plan

Status: planned
Owner: Atlas
Created: 2026-04-24T13:39:30Z
Source report: `/home/piet/vault/03-Projects/reports/audits/2026-04-24_mc-orchestrated-audit-gate-report.md`
Mode: read-only second review

## Live-Gate Snapshot

- Probe time: 2026-04-24T13:38Z
- `/api/health` → `ok`
- `/api/ops/pickup-proof` → active `claimTimeouts = 0`
- `/api/ops/worker-reconciler-proof?limit=20` → `criticalIssues = 0`, `openRuns = 0`
- `/api/ops/runtime-soak-proof` → no worker/runtime criticals, but still `blockedBy = agent-session-lock-clear`
- `/api/board/snapshot?view=live` → compact, `returnedTasks = 1`, `totalTasks = 492`

## P4.1 Titel
**Board/API-Payload/Refresh-Stabilität härten**

- **Problem**
  - Normaler Board-/Dashboard-Flow hängt noch zu breit an `/api/tasks`, obwohl der Snapshot-Pfad deutlich kompakter ist.
- **Evidence aus Report/live Probe**
  - Report: `/api/tasks` ~1.82 MB bei ~492 Tasks, Snapshot ~2 KB.
  - Live 13:38Z: Snapshot weiter kompakt (`returnedTasks = 1`, `totalTasks = 492`).
- **Scope**
  - Normale Board-/Operator-Pfade auf Snapshot/scoped reads priorisieren.
  - Refresh-Verhalten stabil halten, ohne breite Datenlayer-Neuarchitektur.
- **Anti-Scope**
  - Kein Full data-layer rewrite
  - Keine Search-/QMD-Änderung
  - Keine breiten UI-Umbauten
- **betroffene Dateien/Module**
  - `mission-control/src/app/api/board/snapshot/**`
  - `mission-control/src/components/system-pulse.tsx`
  - `mission-control/src/components/overview-dashboard.tsx`
  - `mission-control/src/components/operational-summary.tsx`
  - `mission-control/src/lib/search-index.ts`
  - `mission-control/src/app/costs/components/cost-story-modal.tsx`
- **Acceptance Gates**
  - Normaler Taskboard-Refresh braucht nicht standardmäßig `/api/tasks`
  - Snapshot/scoped routes decken den Live-Board-Flow ab
  - Kein sichtbarer Functional Drift im Board
- **Real-Test-Cases**
  - `/taskboard` laden und mehrfach refreshen
  - Live-Draft/Open-Card anzeigen und Lane-Stabilität prüfen
  - Netzwerkpfad im normalen Board-Flow gegen `/api/tasks`-Fallback prüfen
- **Risiko**
  - Mittel: versteckte Sekundär-Views können noch implizit an Full-Task-Payload hängen.

## P4.2 Titel
**Worker-proof Noise für legitime Atlas/Main-Runs reduzieren**

- **Problem**
  - Gültige Atlas/Main-Audit-Runs können Worker-Proof temporär degraded aussehen lassen, obwohl keine echten kritischen Issues vorliegen.
- **Evidence aus Report/live Probe**
  - Report 13:21Z: `openRuns = 1`, `criticalIssues = 0`, degraded nur wegen aktivem Atlas-Audit-Run.
  - Live 13:38Z: final wieder sauber (`openRuns = 0`, `criticalIssues = 0`).
- **Scope**
  - Proof-Semantik so schärfen, dass legitime Main/Atlas-Runs nicht als verdächtiges Noise erscheinen.
  - Echte Orphans/fehlende Heartbeats weiterhin klar sichtbar lassen.
- **Anti-Scope**
  - Keine mutierenden Reconciler-Endpunkte
  - Kein breiter Worker-Refactor
  - Keine Änderung an Dispatch-Policy
- **betroffene Dateien/Module**
  - `mission-control/src/app/api/ops/worker-reconciler-proof/**`
  - zugehörige Proof-Helper unter `mission-control/src/lib/**`
- **Acceptance Gates**
  - Legitimer Atlas/Main-Audit-Run erzeugt keine irreführende degraded-Lage mehr
  - `criticalIssues` bleibt nur für echte Probleme reserviert
  - Offene Orphans bleiben weiterhin sichtbar
- **Real-Test-Cases**
  - Einen legitimen Atlas-Audit-Run beobachten
  - Danach finalen Clean-State prüfen
  - Einen künstlich stale/open-run Fall in Tests weiter als echte Issue sichtbar halten
- **Risiko**
  - Mittel: zu breite Ausnahme könnte echte Main-Probleme verdecken.

## P4.3 Titel
**Self-lock vs. echter Runtime-Soak-Blocker klar trennen**

- **Problem**
  - Runtime-soak proof bleibt `blocked`, obwohl alle echten worker/runtime criticals grün sind; Ursache ist nur ein legitimer aktiver Main-Session-Lock.
- **Evidence aus Report/live Probe**
  - Report 13:36Z: keine runtime criticals, aber `blockedBy = agent-session-lock-clear`.
  - Live 13:38Z bestätigt denselben Zustand.
- **Scope**
  - Proof-Ausgabe semantisch schärfen: self-lock / expected active lock vs. echter blocker.
  - Operatoren sollen sofort sehen, ob nur ein legitimer aktiver Lock oder echte Instabilität vorliegt.
- **Anti-Scope**
  - Keine Canary-Policy-Neuerfindung
  - Kein breiter Session-/Gateway-Umbau
  - Keine Modell-/Routing-Änderungen
- **betroffene Dateien/Module**
  - `mission-control/src/app/api/ops/runtime-soak-proof/**`
  - Lock-/proof-Klassifizierung unter `mission-control/src/lib/**`
- **Acceptance Gates**
  - Self-lock liest sich nicht mehr wie generischer Runtime-Blocker
  - Echter Lock-/Orphan-Block bleibt hart und sichtbar
  - Proof bleibt für Operatoren kurz und verständlich
- **Real-Test-Cases**
  - Aktiven legitimen Main-Lock prüfen
  - Clean-State ohne Main-Lock prüfen
  - Echten Problemfall in Tests weiter als blocker markieren
- **Risiko**
  - Mittel: zusätzliche Semantik kann verwässern, wenn Benennung/States nicht glasklar bleiben.

## EXECUTION_STATUS

done

## RESULT_SUMMARY

- **empfohlene Sprint-Reihenfolge**
  1. **P4.1 Board/API-Payload/Refresh-Stabilität**
  2. **P4.2 Worker-proof Noise für legitime Atlas/Main-Runs reduzieren**
  3. **P4.3 Self-lock vs. echter Runtime-Soak-Blocker klar trennen**

- **warum diese Reihenfolge**
  - P4.1 hat den höchsten operativen Hebel und das klarste Evidence-/Payload-Problem.
  - P4.2 räumt danach irreführende Proof-Noise aus echten Audit-Läufen weg.
  - P4.3 ist wichtig, aber primär semantische/operatorische Schärfung auf bereits grüner Runtime-Basis.

- **Live-Gate-Status**
  - health ok
  - pickup active claimTimeouts 0
  - worker criticalIssues 0
  - runtime keine worker/runtime criticals; remaining block nur `agent-session-lock-clear`
  - board snapshot compact and clean
