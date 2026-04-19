# R47 Scope-Lock Design (2026-04-19)

## Context (Live-Case Sprint-F)
- Incident: Sprint-F war auf einer Draft-Task `operatorLock=true`, wurde aber über neue Task-IDs umgangen.
- Folge: Atlas konnte trotz Lock weitere Sprint-F/G/H Tasks erstellen.
- Root cause: Lock hing an Task-ID statt am Scope (Plan-Dokument).

## 3-Layer Architecture

### Layer 1: Governance Rule
- `memory/rules.jsonl`: R47 auf `status=active` gesetzt.
- Regeltext (kanonisch):
  - Atlas MUSS vor Sprint-Dispatch das Plan-Doc-Frontmatter lesen.
  - Wenn `operatorLock: true`, darf NICHT dispatcht werden, unabhängig von Task-IDs.
- `AGENTS.md`: R47-Section auf aktiv + 3-Layer-Enforcement aktualisiert.

### Layer 2: Audit Tool
- Neues Script: `scripts/sprint-plan-lock-check.py`
- Funktion:
  - Scan aller `vault/03-Agents/sprint-*-plan-*.md`
  - Frontmatter-Parse
  - Report für `operatorLock: true` mit Sprint + Pfad
- Output-Formate: Tabelle (default) oder JSON (`--format json`)

### Layer 3: Dispatcher Hook (POST /api/tasks)
- Datei: `mission-control/src/app/api/tasks/route.ts`
- Verhalten:
  - Wenn Titel `Sprint-<X>` enthält, wird passendes Plan-Doc unter `vault/03-Agents` gesucht.
  - Frontmatter wird gelesen, `operatorLock` geprüft.
  - `R47_ENFORCEMENT_MODE=warn` (default): Task wird erstellt + Warning Header
  - `R47_ENFORCEMENT_MODE=block`: HTTP 403
- Block-Error:
```json
{"error":"Sprint plan locked by operator","lockedPlan":"sprint-f-ops-inventory","reason":"operatorLock=true"}
```

## James-Research Summary
- Status: pending (James-Lieferung noch ausstehend zum Zeitpunkt dieses Reports).

## Implementation Delta
- `memory/rules.jsonl` (R47 aktiv + finaler Regeltext)
- `AGENTS.md` (R47 section: aktiv + layer spec)
- `scripts/sprint-plan-lock-check.py` (neu)
- `mission-control/src/app/api/tasks/route.ts` (R47 Hook + warn/block flag)

## Test-Anleitung

### 1) Audit-Script
```bash
python3 /home/piet/.openclaw/workspace/scripts/sprint-plan-lock-check.py --format json
```

### 2) API-Test (warn mode)
```bash
R47_ENFORCEMENT_MODE=warn
curl -i -X POST http://127.0.0.1:3000/api/tasks \
  -H 'content-type: application/json' \
  -d '{"title":"Sprint-F lock test","description":"Agent-Role-Declaration: Atlas -> sre-expert\n\nHandoff: x\nScope: x\nDone: x\nOpen: x\nState-Snapshot: x\nEntschieden: x\nOffen-Entschieden: x\nAnti-Scope: x\nBootstrap-Hint: x\n\nPrompt-Cache Static Prefix Contract:\n- Rule 01: keep static labels unchanged; move unique task facts to the dynamic tail.\n- Rule 02: keep static labels unchanged; move unique task facts to the dynamic tail.\n- Rule 03: keep static labels unchanged; move unique task facts to the dynamic tail.\n- Rule 04: keep static labels unchanged; move unique task facts to the dynamic tail.\n- Rule 05: keep static labels unchanged; move unique task facts to the dynamic tail.\n- Rule 06: keep static labels unchanged; move unique task facts to the dynamic tail.\n- Rule 07: keep static labels unchanged; move unique task facts to the dynamic tail.\n- Rule 08: keep static labels unchanged; move unique task facts to the dynamic tail.\n- Rule 09: keep static labels unchanged; move unique task facts to the dynamic tail.\n- Rule 10: keep static labels unchanged; move unique task facts to the dynamic tail.\n- Rule 11: keep static labels unchanged; move unique task facts to the dynamic tail.\n- Rule 12: keep static labels unchanged; move unique task facts to the dynamic tail.\n- Rule 13: keep static labels unchanged; move unique task facts to the dynamic tail.\n- Rule 14: keep static labels unchanged; move unique task facts to the dynamic tail.\n- Rule 15: keep static labels unchanged; move unique task facts to the dynamic tail.\n- Rule 16: keep static labels unchanged; move unique task facts to the dynamic tail.\n\nTask ID: TEST\nObjective: test\nDefinition of Done:\n- test\nReturn format:\n- EXECUTION_STATUS\n- RESULT_SUMMARY","assigned_agent":"sre-expert"}'
```
Erwartung: 201 + Header `x-r47-warning` wenn Sprint-Plan gelockt ist.

### 3) API-Test (block mode)
```bash
R47_ENFORCEMENT_MODE=block
curl -i -X POST http://127.0.0.1:3000/api/tasks ...
```
Erwartung: 403 + JSON-Fehler `Sprint plan locked by operator`.
