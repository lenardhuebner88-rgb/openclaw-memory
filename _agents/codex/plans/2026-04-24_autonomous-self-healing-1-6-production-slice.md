---
status: monitoring
owner: codex
created: 2026-04-24T20:25:52Z
scope:
  - autonomous-self-healing
  - finding-schema
  - task-candidate-dry-run
  - risk-gates
  - a2-readonly-execution
  - learning-ledger
  - eval-suite
  - a3-small-fix-lane
sources:
  - https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/
  - https://openai.github.io/openai-agents-python/guardrails/
  - https://developers.openai.com/api/docs/guides/evaluation-best-practices
  - https://openai.github.io/openai-agents-js/guides/tracing/
  - https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
  - https://www.anthropic.com/research/trustworthy-agents
---

# Autonomous Self-Healing 1-6 Production Slice

## Ziel

In diesem Lauf wird kein unbegrenztes Autonomie-System freigeschaltet. Ziel ist ein produktionsreifer, sicherer A2-Durchstich:

1. Proofs werden zu einheitlichen Findings normalisiert.
2. Aus Findings werden Task-Kandidaten im Dry-run erzeugt.
3. Risiko-Gates A0-A5 entscheiden, was erlaubt ist.
4. Dry-run zeigt, was Atlas tun wuerde, ohne zu mutieren.
5. Genau ein A2 read-only Autonomie-Test wird lokal ausgefuehrt.
6. Ein Learning-Ledger schreibt Vorher/Nachher/Verdict.
7. Eine Eval-/Regression-Suite prueft die wichtigsten Autonomie-Guardrails.
8. Eine eng begrenzte A3-Small-Fix-Lane wird an einem konkreten Tokenplan-Statusfix validiert.

## Quellenprinzipien

- OpenAI beschreibt produktive Agenten als Zusammenspiel aus Modell, Tools und klaren Instructions/Guardrails; nicht jede Aufgabe braucht das staerkste Modell.
- OpenAI empfiehlt inkrementelles Vorgehen statt sofort vollautonomer komplexer Architekturen.
- OpenAI Guardrails muessen vor riskanten Tool-/Action-Ausfuehrungen greifen.
- OpenAI Tracing zeigt: Agent-Runs, Tool Calls, Handoffs und Guardrails muessen beobachtbar sein.
- OpenAI und Anthropic betonen Evals/Regressionen, sonst ist nicht messbar, ob Autonomie wirklich besser wird.

## Live-Startzustand

- Mission-Control Git-Tree ist bereits breit dirty/untracked; dieser Lauf bleibt eng auf neue Autonomie-Dateien und Tests begrenzt.
- Letzte bekannte Live-Gates: Health ok, Pickup ok, Worker critical 0.
- Bekannte Restschwaeche: Kosten-/Status-Semantik fuer Tokenplan/Abo kann noch false criticals erzeugen.

## Implementierungsreihenfolge und Gates

### Gate 1 - Plan + Live-Preflight

Ergebnis:
- Dedicated Plan geschrieben.
- Live-Proofs erfasst.
- Discord-Checkpoint.

Gate:
- `/api/health` erreichbar.
- Worker-/Pickup-Proof ohne aktive Criticals oder Blocker.

### Gate 2 - AUT-1 Finding-Schema + Registry

Umsetzung:
- Neue read-only Library `src/lib/autonomy-self-healing.ts`.
- Neuer read-only Endpoint `/api/ops/autonomy-self-healing`.
- Findings haben `id`, `source`, `severity`, `riskTier`, `ownerAgent`, `evidence`, `recommendedAction`, `dedupeKey`.

Gate:
- Unit-Tests fuer Cost-Governance, Pickup und Runtime-Findings.
- Endpoint liefert 200 und `readOnly=true`.

### Gate 3 - AUT-2 Task-Kandidaten-Dry-run

Umsetzung:
- Aus Findings werden `taskCandidates` erzeugt.
- Jeder Kandidat hat Titel, Agent, DoD, Anti-Scope, Verify-Schritte, Dedupe-Key.
- Keine Taskboard-Mutation.

Gate:
- Dry-run zeigt Kandidaten.
- Keine Doppelkandidaten mit gleichem Dedupe-Key.

### Gate 4 - AUT-3 Risiko-Gates A0-A5

Umsetzung:
- Policy-Funktion klassifiziert:
  - A0/A1: observe/draft only.
  - A2: read-only auto erlaubt.
  - A3: kleine reversible Fixes nur mit Rollback/Test.
  - A4/A5: proposal-only/blocked.

Gate:
- Tests fuer alle Tier-Entscheidungen.
- Runtime-/Provider-/Restart-Aktionen koennen nicht auto-dispatchen.

### Gate 5 - AUT-4 Dry-run Autonomie

Umsetzung:
- Lokales Script `scripts/autonomy-self-heal.mjs`.
- Default `--dry-run`.
- Ruft den Endpoint ab und zeigt Findings/Kandidaten/Policy kompakt.

Gate:
- Dry-run laeuft gegen Live-System.
- Keine Dateien ausser Log/STDOUT werden veraendert.

### Gate 6 - AUT-5 + AUT-6 A2 Read-only Test + Learning-Ledger

Umsetzung:
- Script `--execute --finding-id <id>` erlaubt nur A2 read-only.
- Preflight-Proofs werden gelesen.
- Postflight-Proofs werden gelesen.
- Ledger schreibt JSONL nach `data/autonomy-learning-ledger.jsonl`.

Gate:
- Genau ein Ledger-Eintrag mit pre/post/verdict.
- Verdict ist `improved`, `stable`, `neutral`, `worsened` oder `inconclusive`.
- Keine Mission-Control Task-Mutation, kein Restart, keine Provider-/Runtime-Aenderung.

## Abschlussgate

- Targeted Vitest.
- `npm run typecheck`.
- Live Dry-run.
- Genau ein A2 Execute.
- Eval-Suite 100%.
- A3 Small-Fix fuer MiniMax Tokenplan-Status: `tone=warn` statt hard critical.
- `/api/health`, Pickup, Worker-Proof danach gruen.
- Discord-Abschlussbericht.

## Gate Log

### Gate 1 - Plan + Live-Preflight

Discord: `1497333299566346300`.

Result:
- `/api/health`: ok.
- Pickup critical 0.
- Worker critical 0.
- Plan angelegt.

### Gate 2 - AUT-1 Finding-Schema + Registry

Discord: `1497333832834220225`.

Result:
- `src/lib/autonomy-self-healing.ts`.
- `/api/ops/autonomy-self-healing`.
- `tests/autonomy-self-healing.test.ts`: 5/5 gruen.
- `npm run typecheck`: gruen.

### Gate 3 - AUT-2 Task-Kandidaten-Dry-run

Discord: `1497334119518966002`.

Result:
- Findings erzeugen Task-Kandidaten mit DoD, Anti-Scope, Verify-Steps, Dedupe-Key.
- Keine Taskboard-Mutation.

### Gate 4 - AUT-3 Risk Tiers A0-A5

Discord: `1497334121674838249`.

Result:
- A2 ist read-only executable.
- A3 bleibt small-fix eligible mit Test/Rollback-Pflicht.
- A4/A5 bleiben proposal-only/blocked.

### Gate 5 - AUT-4 Live Dry-run

Discord: `1497336116016320553`.

Result:
- Live Endpoint deployed.
- Dry-run: 5 Findings, 5 Candidates, 2 A2 executable, 1 A4 proposal-only.
- Keine Mutation.

### Gate 6 - AUT-5/AUT-6 A2 Execute + Learning-Ledger

Discord: `1497336478714298388`.

Result:
- A2 read-only local execute fuer `cost:openai-codex:flatrate-billing-artifact:cost_in_flatrate_mode`.
- Ledger: `data/autonomy-learning-ledger.jsonl`.
- Verdict nach korrigierter read-only Probe: `stable`.

### Gate 7 - AUT-7 Eval Suite

Result:
- `scripts/autonomy-eval-suite.mjs`.
- Live Eval: 10/10, Score 100%.

### Gate 8 - AUT-8 A3 Small-Fix Lane

Discord: `1497338181677220072`.

Result:
- Konkreter A3 Small-Fix: MiniMax `TOKEN_PLAN` wird im Budgetstatus als `mode=token-plan`, `metric=token_plan_usage_tokens`, `tone=warn` dargestellt.
- Kein Provider-/Routing-/Runtime-Change.
- Targeted tests: 12/12 gruen.
- Typecheck gruen.
- Build + Restart gruen.

### Eingeschobener Sprint - MC Board/Pipeline UI Live Test

Discord: `1497342027195748352`.

Result:
- Pipeline-API liest pro Agent nur noch einen begrenzten Session-Tail statt ganze JSONL-Dateien.
- Pipeline-Tab zeigt Summary-Layer: Pipeline-Signal, aktive Tools, Read-Budget.
- Taskboard-Header nutzt neuesten Task-Update-Timestamp statt unsortiertem `tasks[0]`.
- Targeted Vitest: 12/12 gruen.
- Typecheck gruen.
- Build + Restart gruen.
- Live-Probes: `/api/health` ok, `/api/pipeline` summary ok, `/kanban` 200, Board-Snapshot 1023 bytes.
- Real browser smoke: `/taskboard` Detail-Button oeffnet Modal ohne client-side exception; `/kanban` zeigt Summary-Layer.

## Monitoring

Started: 2026-04-24T20:48Z.

Artifact:
- `/tmp/autonomy-monitor-2026-04-24.jsonl`

Plan:
- 13 Samples alle 10 Minuten.
- Jede Probe: health, pickup, worker, runtime, autonomy, eval.
- A2-Ledger-Checks bei Sample 1, 7 und 13.
- Discord status after approximately 1h and final after 2h.

## Nicht-Ziele

- Kein A3 Auto-Code-Fix in diesem Lauf.
- Kein automatisches Taskboard-Dispatching.
- Kein Restart.
- Keine Provider-/Model-Routing-Aenderung.
- Keine Core-Worker-Logik-Aenderung.
