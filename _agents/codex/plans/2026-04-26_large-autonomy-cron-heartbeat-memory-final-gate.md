---
status: active
owner: codex
created: 2026-04-26T14:20:00Z
scope: large-final-gate-normal-board-autonomy
---

# Large Final Gate: Normal Board Autonomy, Cron/Heartbeat, Models, Meetings, Memory

## Zielbild
Der normale Taskboard-Prozess soll von 6/10 in Richtung 9/10: Operator gibt Atlas ein Audit oder Sprint-Ziel; Atlas arbeitet Schritt fuer Schritt, erzeugt Follow-up-Drafts aus Findings, dispatched nur sichere Tasks nach Gate-Regeln und fragt nur bei Sudo, Modellwechseln oder hohem Risiko.

## Live-Iststand 2026-04-26T14:20Z
- Mission Control: active, `/api/health` ok.
- Worker-Proof: `openRuns=0`, `criticalIssues=0`.
- Pickup-Proof: `pendingPickup=0`, `criticalFindings=0`, `activeLocks=0`.
- Sprint Gate 3: technisch sauber, aber fachlich `BLOCKED` fuer automatische Follow-up-Drafts.
- Draft-Hygiene laut Atlas: 5 Drafts, 3 ohne saubere `approvalMode`/`operatorLock`, 2 Testartefakte.
- Failed-Hygiene laut Atlas: 47 failed Tasks ohne `sprintOutcome`; 3 failed Tasks ohne konkrete `failureReason`.
- QMD CLI: Index vorhanden, 1088 Dateien, 47757 Vektoren, 26 pending embeddings.
- QMD HTTP/MCP: `127.0.0.1:8181` nicht erreichbar.
- Script Health: `gateway-port-guard.sh` dead wegen fehlendem Log.
- Running services: `mission-control`, `openclaw-discord-bot`, `atlas-autonomy-discord`, `openclaw-gateway`.

## Externe Modell-Fakten
- OpenAI Docs: `gpt-5.5` ist das empfohlene Flagship fuer komplexes Reasoning/Coding; `gpt-5.4-mini` und `gpt-5.4-nano` sind die Kosten-/Latenzoptionen.
  Quelle: https://developers.openai.com/api/docs/models
- OpenAI Pricing: `gpt-5.5` $5/M input, $30/M output; `gpt-5.4-mini` $0.75/M input, $4.50/M output; `gpt-5.3-codex` $1.75/M input, $14/M output.
  Quelle: https://developers.openai.com/api/docs/pricing
- OpenRouter: `openai/gpt-5.3-codex` wird mit 400k Context und $1.75/M input, $14/M output gefuehrt; OpenRouter routed ueber verfuegbare Provider/Fallbacks.
  Quelle: https://openrouter.ai/openai/gpt-5.3-codex/providers
- DeepSeek V3.2 ist eine guenstige OpenRouter-/API-Alternative fuer Watcher/Validator-Reads, aber nicht als Ersatz fuer kritische Terminal-/Coding-Gates ohne Gegencheck.
  Quelle: https://openrouter.ai/deepseek/deepseek-v3.2

## Modell-Iststand
- Atlas/main: OpenClaw default `openai-codex/gpt-5.4`, nicht `gpt-5.5`.
- Forge/sre-expert: `anthropic/claude-opus-4-6`, nicht `gpt-5.3-codex`.
- Lens/efficiency-auditor: `deepseek/deepseek-chat-v3-0324:free`, nicht `gpt-5.5`.
- Pixel/frontend-guru: `openai-codex/gpt-5.4`, nicht `gpt-5.5`.
- Modellwechsel sind Operator-Gate, nicht still ausfuehren.

## Sprint-Struktur

### Phase A: Cron/Heartbeat Audit und Optimierung
Ziel: aktive, obsolete, systemd-migrierte und tote Cron-Layer sauber klassifizieren.

Gates:
- Crontab diff gegen Soll-Layer.
- Systemd-migrierte Cron-Kommentare bleiben dokumentiert, nicht geloescht.
- Dead Script Health (`gateway-port-guard.sh`) root-causen.
- Keine Crontab-Aenderung ohne explizite Small-Fix-Kriterien oder Operator-Go.

### Phase B: Follow-up Autonomie
Ziel: Atlas darf Findings in Follow-up-Drafts uebersetzen, aber nur mit `approvalMode=operator`, `operatorLock=true`, `lockReason=atlas-autonomy-awaiting-approval`, `approvalClass`, `riskLevel`, `parentTaskId`, `planId`, `sourceStepId`, `decisionKey`.

Gates:
- Bestehende schmutzige Drafts werden gelistet und als Cleanup-Plan vorgeschlagen.
- Neue Follow-up-Drafts muessen Preview-/Operator-Lock-Regeln erfuellen.
- Keine stille Task-Erzeugung ohne Receipt/Proof.

### Phase C: Modellrouting
Ziel: gewuenschtes Rollenmodell pruefen und als Change-Set vorbereiten.

Empfehlung:
- Atlas/main: `gpt-5.5` fuer Orchestrierung/Planung/Adversarial Gates, `gpt-5.4-mini` fuer leichte Heartbeats.
- Forge/sre-expert: `gpt-5.3-codex` fuer Coding/Terminal-Fixes.
- Lens/efficiency-auditor: `gpt-5.5` fuer Deep Analysis; DeepSeek/MiniMax nur fuer guenstige Vorfilter.
- Pixel/frontend-guru: `gpt-5.5` fuer UI/Frontend-Rootcause; `gpt-5.4-mini` fuer leichte UI Checks.
- Cron/Heartbeat: bevorzugt kein Frontier-Modell; read-only HTTP/Script Checks lokal, bei LLM-Bedarf `gpt-5.4-mini` oder guenstige OpenRouter-Alternative mit hartem Output-Cap.

Gates:
- Kein Modellwechsel ohne Operator-Go.
- Jede Empfehlung mit Istwert, Zielwert, Risiko, Rollback.

### Phase D: Meeting/Debate E2E
Ziel: drei saubere Meetings/Debates E2E ohne Fehlermeldungen und mit Discord-Reports.

Testthemen:
1. Cron/Heartbeat Zielarchitektur.
2. Follow-up Autonomie mit Operator-Lock.
3. Memory/QMD Hardening und Betriebsregeln.

Gates:
- Meeting-Files korrekt unter `_coordination/meetings/`.
- Statusfluss queued -> running -> done/aborted nachvollziehbar.
- Keine Discord-send Fehler.
- Reports ins Discord.

### Phase E: Vault/QMD/Memory
Ziel: Memory-Layer und QMD wieder als verlaesslicher Retrieval-Pfad.

Gates:
- QMD CLI ok, pending embeddings bewertet.
- MCP/HTTP 8181 down root-causen.
- Keine breite QMD-Architekturaenderung im gleichen Sprint.
- Betriebsregeln fuer Memory: was ist SSOT, was ist Mirror, was ist Archive.

## Stop-Kriterien
- Worker- oder Pickup-Proof critical > 0.
- Neue offene Runs ohne Prozess-/Heartbeat-Wahrheit.
- QMD-Fix erfordert Service-Restart oder Architekturwechsel ohne Operator-Go.
- Modellwechsel waere noetig, aber nicht freigegeben.
- Meeting-Runner erzeugt Fanout oder stille Folgetasks.

## Abschlusskriterien 9/10
- Ein grosser Atlas-Sprint laeuft terminal sauber.
- Drei Meeting/Debate-E2E-Laeufe produzieren verwertbare Reports.
- Cron/Heartbeat-Inventar hat klare Keep/Superseded/Dead/Optimize-Klassen.
- Follow-up-Autonomie bleibt gated und erzeugt nur saubere Drafts.
- QMD/MCP-Status ist erklaert und naechster sicherer Fix steht fest.
