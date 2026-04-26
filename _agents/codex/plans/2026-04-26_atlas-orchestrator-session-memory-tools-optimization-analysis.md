---
status: implemented
created: 2026-04-26T17:35:48Z
agent: codex
scope: atlas-orchestrator-optimization
sources: live-system + web-research
---

# Atlas Orchestrator Optimization Analysis

## Executive Summary

Atlas ist aktuell betriebsfaehig: `/api/health`, Worker-Reconciler-Proof und Pickup-Proof sind gruen. Der groesste strukturelle Engpass ist nicht ein einzelner Worker-Bug, sondern Atlas/Main-Kontextwachstum: ein Live-Run kompilierte bis zu ca. 240 KB Kontext mit ca. 98 KB Systemprompt, ca. 97 KB Nachrichtenhistorie und ca. 45 KB Tool-Schemas. Dadurch erreicht Atlas schnell Session-Size-Guard-HARD, obwohl die Task-/Worker-Proofs sauber sind.

Meine Bewertung: Systemzustand operativ ca. 8/10, Orchestrator-Effizienz ca. 6.5/10. Ziel 9.5/10 ist realistisch, wenn Atlas weniger Rohkontext injiziert bekommt, Tools nach Modus freigeschaltet werden und Follow-up-Autonomie ueber harte Proof-Gates laeuft.

## Live Evidence

Stand 2026-04-26T17:34Z:

| Bereich | Live-Wert | Bewertung |
|---|---:|---|
| `/api/health` | `status=ok`, `severity=ok`, `openTasks=0`, `pendingPickup=0`, `failed=0`, `attentionCount=0` | gruen |
| Worker-Reconciler-Proof | `openRuns=0`, `issues=0`, `criticalIssues=0` | gruen |
| Pickup-Proof | `pendingPickup=0`, `activeSpawnLocks=0`, `findings=0`, `criticalFindings=0` | gruen |
| Context-Budget-Proof | `status=degraded`, `findings=166`, `criticalFindings=28`, active critical 0 | historisch laut, aktuell nicht kritisch |
| Memory-Proof | `status=degraded`, `criticalFindings=0`, QMD retrieval smoke ok | nutzbar, aber Wartung offen |
| QMD | 1107 Files, 49721 Vectors, 7 pending Embeddings, `mc-src` 1d stale | nicht blockierend |
| Main sessions dir | ca. 390 MB | Session-Artefakte sind Hauptwachstum |
| Injected workspace prompts | `MEMORY.md` 29 KB, `HEARTBEAT.md` 19 KB, `AGENTS.md` 11 KB | zu schwer fuer Dauerinjektion |

Atlas/Main-Session-Evidence:

- Groesste aktuelle Trajectory: `46ffe260-6056-4a00-8cc6-4bc8916e4ecd.trajectory.jsonl` mit 8.18 MB und 392 Events.
- In dieser Datei: 56 `trace.metadata` Events verbrauchen zusammen ca. 5.83 MB, im Mittel ca. 104 KB pro Event.
- Groesster `context.compiled` Event: ca. 245 KB.
- Tooling im kompilierten Kontext: 37 Tools, ca. 44.5 KB Tool-Schema-JSON.
- Einzelne schwere Tools im Schema: `cron` ca. 11.2 KB, `message` ca. 8.3 KB, `exec` ca. 1.8 KB, `sessions_spawn` ca. 1.8 KB.

Systemd/Cron:

- `m7-auto-pickup.timer`, `m7-plan-runner.timer`, `m7-mc-watchdog.timer`, `m7-session-freeze-watcher.timer`, `m7-stale-lock-cleaner.timer`, `m7-worker-monitor.timer` sind aktiv.
- Crontab enthaelt weiter mehrere Defense-/Memory-/Session-Size-Layer. Die wichtigsten sind aktiv, aber die Verantwortlichkeiten ueberlappen teils.

## External Research Synthesis

OpenAI beschreibt Agenten als Kombination aus Modell, Tools und Instruktionen/Guardrails. Fuer Atlas ist besonders relevant: Tools sollen standardisiert, gut dokumentiert, getestet und wiederverwendbar sein; bei wachsender Tool-Anzahl soll man Aufgaben in mehrere Agenten oder Modi trennen. Quelle: OpenAI, Practical Guide to Building Agents, https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/

OpenAI empfiehlt fuer Orchestrierung einen klaren Run-Loop mit Exit-Bedingungen wie strukturiertem Output, Fehler, Tool-Aufruf oder Max-Turns. Das stuetzt fuer Atlas harte Gates statt offener Dauerschleifen. Quelle: gleiche OpenAI-Quelle.

Anthropic trennt Workflows und Agents und nennt den Orchestrator-Workers-Workflow passend fuer komplexe Aufgaben, bei denen Unteraufgaben nicht vorab bekannt sind. Genau das ist Atlas' Rolle. Wichtig ist aber: der Orchestrator zerlegt, delegiert und synthetisiert; er traegt nicht alle Rohdetails dauerhaft selbst. Quelle: Anthropic, Building Effective Agents, https://www.anthropic.com/engineering/building-effective-agents

OpenAI Agents SDK Guardrails zeigen: Input-/Output-/Tool-Guardrails gehoeren an die Workflow-Grenzen und an die Tools; Tool-Guardrails muessen vor/nach jedem mutierenden Tool greifen. Fuer OpenClaw heisst das: Follow-up-Dispatch, Finalize und Cron-/Session-Operationen brauchen eigene Guardrails, nicht nur eine allgemeine Atlas-Regel. Quelle: https://openai.github.io/openai-agents-python/guardrails/

OpenAI Tracing dokumentiert Trace/Span-Strukturen fuer Runs, Tool Calls, Guardrails und Handoffs. Das passt zum vorhandenen Proof-Ansatz, aber Eure lokale `trace.metadata`-Implementierung schreibt zu viel wiederholt in Session-Artefakte. Ziel: Hash + Pointer statt volle Plugin-/Skill-/Prompting-Metadaten pro Run. Quelle: https://openai.github.io/openai-agents-js/guides/tracing/

ReAct stuetzt das Muster, Reasoning und Actions zu verzahnen, damit ein Agent Plaene aktualisiert und externe Quellen nutzt. Fuer Atlas ist das sinnvoll, solange Actions klein, beweisbar und gate-gesteuert bleiben. Quelle: https://arxiv.org/abs/2210.03629

## Atlas Tooling Verdict

Atlas hat zu viel gleichzeitig im aktiven Kontext. 37 Tools sind nicht per se falsch, aber fuer den normalen Discord-/Operator-Orchestrator-Modus zu breit. Das Toolset mischt:

- Read/Data: `read`, `memory_search`, `memory_get`, `qmd__search`, `qmd__status`, `web_fetch`, `taskboard__taskboard_get_task`, `taskboard__taskboard_list_tasks`
- Action: `write`, `edit`, `apply_patch`, `exec`, `process`, `gateway`, `message`, `taskboard__taskboard_create_task`, `taskboard__taskboard_patch_task`, `cron`
- Session/Orchestration: `sessions_list`, `sessions_history`, `sessions_spawn`, `sessions_send`, `sessions_yield`, `agents_list`, `subagents`
- Media/Other: `image`, `tts`, `pdf`, `canvas`, `nodes`

Empfehlung: Atlas braucht vier Tool-Modi statt ein breites Default-Profil:

| Modus | Zweck | Erlaubte Tool-Klassen |
|---|---|---|
| `atlas-default` | Operator-Dialog, Status, Planung | read-only health/proofs, taskboard read, memory/qmd search, discord message |
| `atlas-dispatch` | Follow-up-Drafts und bewusste Dispatches | default + taskboard create/patch mit Preview/Proof-Gate |
| `atlas-sprint-chair` | Grossen Sprint orchestrieren | dispatch + sessions_spawn/send, aber keine Shell/Edit-Tools |
| `atlas-maintenance` | kontrollierte Systemwartung | temporaer: cron/exec/process/edit, nur mit Operator-Go oder Task-Gate |

Das reduziert Prompt- und Tool-Schema-Last und verhindert Fehlentscheidungen durch aehnliche oder konkurrierende Tools.

## Memory And Vault Verdict

Die Vault-Struktur ist als SSOT brauchbar, aber Atlas' Prompt-Injektion ist zu schwer. `MEMORY.md` und `HEARTBEAT.md` sind wertvolle Referenzen, sollten aber nicht vollstaendig in jeden Main-Turn. Zielbild:

| Layer | Inhalt | Zugriff |
|---|---|---|
| L0 Runtime Truth | `/api/health`, Worker-Proof, Pickup-Proof, Session-size state | live, read-only, immer zuerst |
| L1 Operating Kernel | Atlas-Rolle, R49/R50, Top-Stop-Regeln, Ausgabeformat | dauerhaft injiziert, max. 6 KB |
| L2 Current Work | aktive Sprint-/Plan-Dateien, Coordination live | gezielt via Retrieval/Path |
| L3 Memory/Vault | Daily, Reports, alte Meetings, historische Decisions | QMD/RAG, nicht Dauerprompt |
| L4 Forensics | Sessions/Trajectory/Logs | nur fuer RCA, nie in normalen Atlas-Prompt |

Konkreter Befund: `/home/piet/vault/_agents/Atlas` ist klein, das Problem liegt nicht im Atlas-Vault-Ordner. Das Wachstum entsteht in Runtime-Sessions, Trace-Metadaten und langen injizierten Workspace-Dateien.

## Betriebsregeln Verdict

Gut:

- R49/R50, HANDSHAKE und Proof-Gates sind fachlich richtig.
- Worker-/Pickup-Proofs sind aktuell sauber.
- Systemd-Timer fuer M7-Kernfunktionen laufen.
- Session-Size-Guard erkennt das Problem frueh.

Nicht optimal:

- Es gibt keine harte Trennung zwischen Atlas als Chairman und Atlas als Maintenance-Executor.
- Output-Caps sind als Regel vorhanden, aber Context-Budget-Proof zeigt historisch weiter grosse Tool-Ausgaben.
- Trace-Metadaten schreiben pro Run zu viel redundante Struktur.
- Follow-up-Autonomie ist noch nicht sauber in Stufen getrennt: Preview, Dispatch, Execute, Finalize, Audit.
- Cron-/Heartbeat-Verantwortlichkeiten sind sichtbar, aber nicht als Operator-Readout mit "wer prueft was, warum, naechste Aktion" verdichtet.

## Highest-Leverage Plan

### Stufe 1: Atlas Operating Kernel

Ziel: Dauerprompt von Atlas auf eine kleine, stabile Betriebsanweisung reduzieren.

Umsetzung:

- Neues kompaktes Kernel-Dokument: Rolle, Stop-Kriterien, R49/R50, Proof-Reihenfolge, Output-Caps, Follow-up-Contract.
- `MEMORY.md`/`HEARTBEAT.md` nicht mehr voll injizieren, sondern per Retrieval abrufen.

Gate:

- `context.compiled.systemPrompt` sinkt von ca. 98 KB auf Ziel < 35 KB.
- Atlas beantwortet Statusfragen weiter korrekt anhand Live-Proofs.

### Stufe 2: Tool-Mode Routing

Ziel: Atlas bekommt im Default nur die Tools, die fuer Orchestrierung noetig sind.

Umsetzung:

- Tool-Allowlist pro Modus: default, dispatch, sprint-chair, maintenance.
- Mutierende Tools nur in Dispatch-/Maintenance-Modus.
- `cron`, `exec`, `edit`, `process` aus dem Default-Kontext entfernen.

Gate:

- Tool-Schema-JSON im Default-Kontext < 20 KB.
- `/meeting-status`, normaler Taskboard-Status, Follow-up-Preview funktionieren ohne Maintenance-Tools.

### Stufe 3: Trace-Metadata Compaction

Ziel: Trajectory-Dateien nicht mehr durch redundante Metadaten aufblaehen.

Umsetzung:

- Bei wiederholten `trace.metadata`: statt voller `plugins`, `skills`, `prompting`, `config` nur Hash, Version, Pointer in separate Artefaktdatei.
- Vollmetadata nur bei Sessionstart oder Configwechsel.

Gate:

- `trace.metadata` pro Event < 10 KB statt ca. 104 KB.
- Trajectory-Wachstum pro 50 Atlas-Interaktionen < 1 MB.

### Stufe 4: Structured Orchestrator Contract

Ziel: Atlas produziert maschinenlesbare, knappe Abschluss- und Follow-up-Outputs.

Contract:

```yaml
execution_status: done|blocked|needs_operator|failed
proofs:
  health: ok|degraded|fail
  worker: ok|degraded|fail
  pickup: ok|degraded|fail
follow_ups:
  - title:
    priority: P0|P1|P2|P3
    safe_mode: preview|dispatch_allowed|operator_required
    rationale:
operator_decisions:
  - decision:
    reason:
artifacts:
  - path:
```

Gate:

- Atlas kann aus einem Audit drei Follow-ups vorschlagen, aber nur safe-mode-konforme Tasks automatisch dispatchen.
- Kein Auto-Finalize ohne Receipt.

### Stufe 5: Autonomy Ladder

Ziel: Von "Atlas schlaegt vor" zu "Atlas arbeitet kontrolliert weiter".

Stufen:

1. Preview only: Follow-ups werden nur angezeigt.
2. Dispatch read-only: Follow-ups fuer Analyse/Proof ohne Mutationen duerfen automatisch erstellt werden.
3. Dispatch guarded: kleine Fix-Sprints duerfen erstellt werden, Ausfuehrung braucht Proof-Gate.
4. Execute bounded: ein Sprint, ein Agent, kein Fanout, Finalize nur mit Receipt.
5. Sequential autonomy: naechster Sprint erst nach gruenem Proof-Pack.

Gate:

- Ein Atlas-Sprint erzeugt Follow-ups, dispatcht genau die erlaubten, fuehrt sequentiell aus und liefert Proof-Pack.

### Stufe 6: Cron/Heartbeat Readout Consolidation

Ziel: Operator sieht, welche Defense-Layer aktiv und relevant sind.

Umsetzung:

- Ein read-only Proof `/api/ops/cron-heartbeat-proof` oder Script-Report.
- Gruppierung: pickup/worker, session-size, memory, qmd, board hygiene, meeting.
- Markierung: active, migrated-to-systemd, obsolete, duplicate, missing.

Gate:

- Keine Cron-Aenderung ohne separaten Operator-Go.
- Report kann obsolete vs. migrated sauber unterscheiden.

### Stufe 7: Memory Hygiene

Ziel: QMD/Vault retrieval bleibt schnell und praezise.

Umsetzung:

- Pending embeddings und stale `mc-src` beheben.
- Meeting-/Debate-Artefakte komprimiert indexieren: Summary + links, nicht Volltranskript als Default.
- Session-Archive aus Retrieval ausschliessen, nur Forensics.

Gate:

- Memory-Proof `status=ok`.
- Retrieval-Smoke fuer Atlas-Autonomie, Worker-Proofs und Meeting-Reports liefert sinnvolle Top-Treffer.

### Stufe 8: 9.5/10 Soak

Ziel: Beweisen, nicht behaupten.

Test:

- 1 grosser Atlas-Autonomy-Sprint mit 3 Follow-ups.
- 1 Meeting/Debate-Review als Nebenpfad.
- 30-60 Minuten Session-Wachstum beobachten.
- Live-Proofs: health, worker, pickup, context-budget, memory.

Gate:

- Keine neuen critical Findings.
- Kein Session-HARD innerhalb des Testfensters.
- Follow-ups korrekt priorisiert und ohne Fanout.

## Recommended Next Sprints

### Sprint A: Atlas Slim Context

Scope: Operating Kernel + Tool-Mode Konzept implementierbar vorbereiten.

Output:

- Atlas-Kernel-Spezifikation.
- Tool-Allowlist-Matrix.
- Patch-Vorschlag fuer Runtime-Konfiguration, noch ohne riskante Live-Umstellung.

### Sprint B: Trace Metadata Compaction

Scope: `trace.metadata`-Redundanz beheben.

Output:

- RCA der Trajectory-Schreibstelle.
- Small patch: full metadata once, then hash/pointer.
- Regression-Test: metadata event byte size.

### Sprint C: Autonomy Contract

Scope: Follow-up-Autonomie in Preview/Dispatch/Execute/Finalize trennen.

Output:

- Orchestrator-Contract.
- Taskboard-Follow-up-Preview.
- Ein kontrollierter Atlas-Sprint als Proof.

## Operator Decisions

1. Soll Atlas Default ohne `exec/edit/process/cron` laufen und Maintenance nur explizit aktiviert werden?
2. Darf die Runtime Trace-Metadaten komprimieren, wenn volle Details als Pointer-Datei erhalten bleiben?
3. Soll `MEMORY.md`/`HEARTBEAT.md` aus dem Dauerprompt in Retrieval-Only verschoben werden?

Meine Empfehlung: alle drei ja, aber in genau dieser Reihenfolge: Kernel/Tool-Modi, dann Metadata-Compaction, dann Autonomy-Contract.

## Implementation Follow-Up

Umsetzung abgeschlossen in:

- `_agents/codex/plans/2026-04-26_atlas-orchestrator-optimization-implementation-report.md`

Live-Ergebnis:

- Bootstrap-Limits aktiv: `bootstrapMaxChars=16000`, `bootstrapTotalMaxChars=42000`
- Atlas Discord Default Tools reduziert: 37 -> 21
- Neue Trajectory-Compaction aktiv: `trace.metadata` ca. 104 KB -> 3.3 KB, `context.compiled` ca. 245 KB -> 1.5 KB
- Budget-Proof: `/home/piet/.openclaw/scripts/atlas-orchestrator-budget-proof.mjs`, letzter Status `ok`
