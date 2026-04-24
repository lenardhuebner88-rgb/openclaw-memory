---
status: active
owner: codex
created: 2026-04-24T20:25:52Z
scope:
  - autonomous-self-healing
  - finding-schema
  - task-candidate-dry-run
  - risk-gates
  - a2-readonly-execution
  - learning-ledger
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
- `/api/health`, Pickup, Worker-Proof danach gruen.
- Discord-Abschlussbericht.

## Nicht-Ziele

- Kein A3 Auto-Code-Fix in diesem Lauf.
- Kein automatisches Taskboard-Dispatching.
- Kein Restart.
- Keine Provider-/Model-Routing-Aenderung.
- Keine Core-Worker-Logik-Aenderung.
