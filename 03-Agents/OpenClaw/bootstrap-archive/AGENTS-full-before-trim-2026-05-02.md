# OpenClaw Agenten

> **Einordnung (siehe `CONTEXT_MAP.md`):**
> `AGENTS.md` beschreibt Rollen, Delegation und Arbeitsregeln (Prio 4).
> **Konkrete Modell-/Runtime-Zuordnung kommt aus** `/home/piet/.openclaw/openclaw.json` + Live-Verifikation.

## Sub-Agent-Preamble (READ FIRST on every Task-Pickup)

This consolidated preamble supersedes the failed H5 attempt to write to `agents.defaults.systemPrompt` in openclaw.json (schema-invalid, rolled back 2026-04-20 06:31 UTC). Content lives here in AGENTS.md (workspace-wide, read by every agent-session bootstrap).

**6 Pflicht-Checks on Task-Pickup:**

1. **R45 First-Action (within 60s)**: first non-terminal receipt (`accepted|started|progress`) must be posted within 60s after pickup-claim/dispatch-ack. This 60s window measures claim/ack responsiveness, **not** the later worker `accepted/session-ready` timestamp. Kanonischer Ablauf: `draft -> assigned -> dispatch -> pending-pickup -> claim/ack -> receipt -> in-progress`.
2. **R45 Major-Steps**: After every git-commit, build, route-add, playwright-run -> `POST receipt=progress`. Minimum every 5min while working.
3. **R45 Final**: On task-end -> `POST receipt=result {status:"done"|"failed", summary:"<full>"}`. Audit note: do not flag red by conflating dispatch/claim-ack timing with worker session-ready timing.
4. **R44 Board-First**: If no Board-Task exists for your work -> STOP. Call `taskboard_create_task` first. No sessions_spawn-only work.
   If the task is delegated to another agent, task creation/assignment alone is NOT enough: you must also dispatch it and verify via `GET /api/tasks/<id>` that the task reached `status=pending-pickup` with `dispatchState=dispatched`. `assigned/queued` is not pickup-ready.
5. **R42/R46 Restart-Discipline**: Use `mc-restart-safe <timeout> <tag>`. **NEVER** `systemctl --user restart mission-control` directly. See Tool-Wrapper-Policy below.
6. **R50 Session-Locks**: Don't retry same session on lock-conflict. Auto-pickup handles orphan detection. See R50 section below.

**Full rule-details:** `feedback_system_rules.md` (49 rules R1-R50, auto-rendered from `memory/rules.jsonl`).

---

## Tool-Wrapper-Policy (seit 2026-04-20)

### MC Live-Change Abschlussregel (verbindlich)

Wenn eine Mission-Control-Änderung erst nach Build/Restart live wirksam werden kann, gilt ein Task erst dann als sauber abgeschlossen, wenn **alle 3 Ebenen** erfüllt sind:
1. **Code-/Test-Gates grün**
2. **Safe Restart erfolgreich** (`mc-restart-safe`, nie direkter Restart)
3. **Betroffener Live-Endpunkt auf `http://127.0.0.1:3000` zeigt die beabsichtigte neue Semantik**

Wenn Punkt 3 noch nicht erfüllt ist:
- Task **nicht blind als voll fertig** werten
- stattdessen entweder `blocked` mit klarem Live-Blocker
- oder einen **engen Verify-/Finalize-Follow-up** schneiden

Kanonisches Runbook:
- `/home/piet/.openclaw/workspace/docs/operations/mission-control-build-safe-restart-endpoint-verify-runbook.md`

**Verboten (NIE direkt):**

| Command | Pflicht-Wrapper |
|---|---|
| `systemctl --user restart mission-control` | `mc-restart-safe <timeout> <tag>` |
| `deploy.sh restart` | `mc-restart-safe` |
| `sudo systemctl restart` | `systemctl --user` + wrapper |
| Direkte `openclaw.json` Edits ohne Schema-Verify | edit + `openclaw doctor` + rollback-on-invalid |

**Erlaubt (Read-Only):** `systemctl --user status`, `curl localhost:3000/api/health`, `ps`, `tail`, `openclaw doctor`.

**Wrapper-Pfade:** `mc-restart-safe` → `/home/piet/.openclaw/bin/mc-restart-safe` | `pre-flight-sprint-dispatch.sh` + `stale-lock-cleaner.sh` → `/home/piet/.openclaw/scripts/`

Rationale + Live-Cases: R42, R46 in `feedback_system_rules.md`.

---

## Kern-Agenten (Rollen)
| Display | Agent-ID | Rolle |
|---------|----------|-------|
| Atlas | main | Orchestrator |
| Forge | sre-expert | Infra/Code |
| Pixel | frontend-guru | UI/Frontend |
| Lens | efficiency-auditor | Kosten/Analyse |
| James | james | Recherche |
| Spark | spark | Forge-Entlastung für kleine Coding-/Ops-Aufgaben |

## Delegationsregeln
- Subagenten erlaubt: `sre-expert`, `frontend-guru`, `efficiency-auditor`, `james`, `spark`.
- Agent-ID-Auflösung und Runtime-Mapping erfolgen im Code (`resolveRuntimeAgentId()` in `task-assignees.ts`) und in der aktiven Config.
- **Routing-Regel (2026-04-18):** UI/Frontend-Tasks → Pixel. Forge nur für Backend (API-Routes, Config, Infra, Security).
- **Forge-Concurrency:** sre-expert limit=5 (erhöht von 3 am 2026-04-18).
- **Spark-Aktivierung (2026-04-18):** Spark für kleine Coding-Tasks, Ops-Reviews, parallele Threads. Darf small Fixes eigenständig via PATCH abschließen wenn DoD klar. limit=3.
- **Tool-Conventions-Header (effective 2026-04-27):** Bei Worker-Tasks/Dispatch-Prompts folgenden Header aufnehmen: `TOOL-CONVENTIONS: qmd__search primary (BM25); qmd__deep_search/qmd_query nur narrative-research; qmd__get immer qmd://collection/...; qmd__multi_get nur comma-separated relative paths, kein qmd://, kein glob, maxBytes 102400 für Vault/Sprint-Dateien; MCP "Not connected" beim ersten Call identisch retryen, nicht sofort reporten.`
- **Terminal-Receipt v1.1 Contract (effective 2026-04-29):** Worker-Agenten (`sre-expert`, `frontend-guru`, `efficiency-auditor`, `james`, `spark`) sollen für `result|blocked|failed` Receipts ein `sprintOutcome` mit `schema_version="v1.1"` mitsenden. Kanonische Templates + Agent-Hooks: `docs/operations/worker-sprintoutcome-v11-templates.md`. `resultSummary` bleibt menschenlesbar und task-spezifisch.
- Für Worker-/Heartbeat-Verhalten ist `HEARTBEAT.md` maßgeblich.

## Channel-Konzepte (stabil)
| Channel | ID | Zweck |
|---------|-----|-------|
| `#spark` | `1487143853038502092` | Spark — Research/Ideen-Analyse |
| `#execution-reports` | (Discord) | Technische Task-Lifecycle-/Execution-Reports |
| `#alerts` | `1491148986109661334` | System-Alerts, Cron-Fails |
| `#atlas-main` | (Discord) | Kuratierte Orchestrierungs-/Entscheidungs-Updates |

Kanonische Regelquelle: `docs/operations/REPORTING_ROUTING_TRUTH.md`

## Build-Regeln (verbindlich)
> **Kanonischer Build-Pfad:** `npm run build` — ausschließlich über diesen Wrapper
> **Verboten:** `node_modules/.bin/next build`, `next build`, direkter Next.js-Binary-Aufruf

Nur `npm run build` aktiviert: `scripts/build.mjs` (Lock + Stability-Preflight + Freshness-Check).

## Hinweise zur Pflege
- Historische/entfernte Agenten nur in Archiv-/History-Dateien dokumentieren, nicht als aktive Liste.
- Detaillierte Tageszustände, Umkonfigurationen oder temporäre Experimente gehören in `memory/daily/YYYY-MM-DD.md`.

## Arbeitsregeln: Verify-After-Write (HARDENED 2026-04-17)

**Regel:** Nach jedem schreibenden MC-API-Call ist ein verifizierendes `GET /api/tasks/<id>` Pflicht.

| Operation | Muss-Felder im GET |
|---|---|
| POST /api/tasks | `id`, `status`, `assigned_agent`, `description` enthält Execution-Contract-Marker |
| Delegation after POST /api/tasks | `POST /api/tasks/:id/dispatch` ist Pflicht für echte Worker-Übergabe; `assigned/queued` allein zählt nicht als Dispatch |
| PATCH status | `status` == Zielwert |
| POST dispatch | `status==pending-pickup`, `dispatched==true`, `dispatchedAt` gesetzt, `dispatchTarget` gesetzt |
| POST receipt (erstes) | `status==in-progress`, `executionState==active`, `startedAt` gesetzt |
| POST receipt (result) | `status` ∈ {done, failed}, `completedAt` gesetzt, `resultSummary` nicht leer |
| PATCH admin-close | `status==canceled`, `resolvedAt` gesetzt |

Bei Mismatch: max. 1 Retry. Danach klar als Failure melden. GET ist nie optional — HTTP-OK ≠ persistierter Zielzustand.

**Context Overflow Guard (Worker):** Bei session_tokens >= 70% → Compaction triggern. Bei >= 90% → dringender Checkpoint. Kein Compaction-Tool → Terminalpfad (result/failed/blocked), nie still sterben.

**Board-Scan vor Task-POST:** `GET /api/tasks` mit Title-Substring-Match Pflicht. Bei Duplikat-Verdacht: abbrechen, nicht doppelt anlegen.

**Follow-up Result Lookup:** Wenn eine konkrete Task-ID bekannt ist (z. B. Folge-Task, Verify-Task, P4.x-Kette), immer zuerst `GET /api/tasks/<id>` auf genau diese ID ausführen; globale Recent-Task-Listen nur als Fallback nutzen.

**Heartbeat Sleep-Mode:** Vor Heartbeat-basierter Task-Anlage für Agent X: prüfen ob bereits `assigned_agent=X, status=in-progress` existiert. Wenn ja: überspringen.

## Session-Modell (AKTIV seit 2026-04-17)

Vollständige Spec: `/home/piet/vault/03-Agents/atlas-session-memory-operating-model.md`

| Typ | Max Tiefe | Max Dauer | Scope |
|---|---|---|---|
| Incident | 30 tool-calls | 20 min | Containment + Root-Cause + Minimal-Fix |
| Analyse | 80 tool-calls | 60 min | Findings-Liste, kein Fix in derselben Session |
| Umsetzung | 40 tool-calls | 30 min | Genau ein Finding / eine DoD |
| E2E/Orchestrator | 120 tool-calls | — | Monitor-dominiert, Background-Tasks |

**Memory-Schichten:** LTM → `memory/invariants/*.md` (max 3KB/file) | WM → `memory/working/*.md` (<14d) | IC → session-lokal, nie persistiert.

**Write-Gate:** "Würde ich das in 6 Monaten noch brauchen?" Nein → WM oder Protokoll-File.

**Worker-Agents:** dürfen KEIN LTM schreiben. Findings → Task-resultSummary, Atlas entscheidet Promotion.

**Reset-Trigger (hart):** 3 consecutive tool failures | 2 Memory↔Live-Widersprüche | Kontext >70%.

**Handoff-Artefakt Pflicht** bei Session-Wechsel — Format: Scope / Done / Open / State-Snapshot / Entschieden / Offen-Entschieden / Anti-Scope / Bootstrap-Hint. Artefakt-Text IST der erste User-Prompt der Folge-Session.

## Memory-Tools & Retrieval (seit 2026-04-19)

QMD (Quick Markdown Search) ist als MCP-Server verfügbar. Tools: `search`, `deep_search`, `vector_search`, `get`, `multi_get`, `status`.

**Benutze QMD wenn:** Du suchst "was haben wir über X schon dokumentiert?" | Du brauchst verwandte Dokumente | Du kennst den Dateinamen nicht genau.

**Retrieval-Reihenfolge:** Fuer `vault` zuerst `search` (BM25) nutzen. Wenn BM25 nichts Brauchbares liefert, `vector_search` als Fallback. `deep_search` aktuell nicht als Standardpfad fuer Vault-Kontext verwenden; der Pfad ist unter CPU-Last timeout-anfaellig.

**Benutze File-Read wenn:** Du kennst den genauen Pfad | Live-Datei (tasks.json) | Du willst die komplette Datei.

| Collection | Pfad | Inhalt |
|---|---|---|
| `vault` | `/home/piet/vault/` | Obsidian PKM: Plans, RCAs, Reports (177 Files) |
| `workspace` | `/home/piet/.openclaw/workspace/` | Agent-Memory: MEMORY.md, AGENTS.md, invariants (789 Files) |
| `mc-src` | `/home/piet/.openclaw/workspace/mission-control/` | Next.js source (76 Files) |

Beispiel: `search "R26 Sprint Plan"` | Fallback: `vector_search "welche Plaene haengen von R26 ab?"` | QMD-MCP: `http://127.0.0.1:8181/mcp`.

**Sprint-B:** Fact-Extractor → `scripts/memory-fact-extractor.sh` | Facts → `memory/facts/YYYY-MM-DD.jsonl` | Precompact → `scripts/agent-precompact-wrapper.sh`.

## Session-Size Discipline (R36, seit 2026-04-19)

Bei Session-Datei >5 MB droht Context-Overflow mit `compactionAttempts=0`.

**Aktiv:** `compaction.mode=safeguard` | `recentTurnsPreserve=6` | `softThresholdTokens=20000` | `postCompactionMaxChars=16000`.

**Hard-Rule R36:** Context-Overflow-Error → AUFHÖREN, Zustand in MEMORY promoten, neue Session. Nicht retry im gleichen Context.

Bei >100 tool-calls oder Operator meldet "Session ist bei 5MB": Early-Exit mit result-Receipt + "Session-Rotation empfohlen".

## Rules R42–R53 — Index *(Full detail: feedback_system_rules.md)*

| Rule | One-liner |
|---|---|
| R42/R46 | MC-Restart via `mc-restart-safe 120 "sub-<agent>-<id>"` only. Two MC-restart tasks → NIE parallel. |
| R45 | Receipt: `accepted` <60s → `progress` every major-step/5min → `result` at end. >20min no receipt = hard-escalation. |
| R47 | `operatorLock` check in plan-doc before sprint-dispatch. If `true` → stop, ask operator. |
| R48 | Auto-cancel: `draft AND age>48h` → canceled. `failed AND completedAt=null AND age>24h` → completedAt set. |
| R49 | No SHA/session-ID/task-ID/done-claim without disk-verify (`git log`, `ls sessions/`, `curl api/tasks/`). Context-loss → ask for re-prompt, never fabricate. |
| R50 | Session-lock: skip if alive <120s. Stale (>=120s or PID dead) → force new session-ID. `stale-lock-cleaner.sh` */5min. |
| R51 | `openclaw-config-guard.sh` (*/1min): detects openclaw.json changes, runs `openclaw doctor`, rollback on invalid. |
| R52 | `auto-pickup.py`: immediate exit after trigger = silent-fail (`TRIGGER_SILENT_FAIL`) → alert. |
| R53 | `config-snapshot-to-vault.sh` daily 03:00 UTC → `vault/03-Agents/openclaw-config-backups/YYYY-MM-DD/`, 30d retention. |
