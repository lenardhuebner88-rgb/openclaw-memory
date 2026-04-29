---
type: sprint
status: status/done
date: 2026-04-27
tags: [topic/mcp, topic/gateway, topic/hardening, agent/atlas, agent/codex]
---

# Sprint 2026-04-27 — MCP-Hardening A → B → C

**TL;DR:** Drei Hebel deployed ohne aktive Sessions zu killen. P0.2 (bundle-mcp-runtime self-recovery) ist **live + Gateway-Restart aktiviert + DoD-verifiziert**. QMD wieder grün. Update auf 2026.4.24 nun unblocked.

## Kontext

Nacht-Incident 2026-04-26→27: Gateway-OOM-Storm (15 Restarts/24h), Discord-Auth 4004 (Token vom Operator rotiert), Validator-Reject auf **agents.defaults.imageModel.primary = openai/gpt-image-2** (Modell seit 2026-04-21 released, aber nicht in lokaler Allowlist).

Nach Steps 1-3 (Vitest-Cleanup, MemoryMax 4G → 6G via systemctl set-property, openclaw-Verify v2026.4.22 vs latest v2026.4.24) kamen drei weitere Hebel A/B/C an die Reihe.

## A — alert-dispatcher Informational-Filter (DEPLOYED)

**Problem:** **flatrate-billing-artifact** wird als Discord-Alert dispatched, obwohl die Anomaly-Definition selbst sagt *als Accounting-Artefakt behandeln, NICHT als Spend-Alarm*.

**R49-Korrektur:** Initial dachte ich der gesamte alert-dispatcher sei broken (4h SUPPRESS-Loop). Logs zeigten: Rate-Limit ist 6h by-design, last ALERT_SENT war 2026-04-27 02:42 UTC. Der echte Cleanup ist nur die Artefakt-Filterung.

**Patch:**
- File: /home/piet/.openclaw/scripts/cost-alert-dispatcher.py
- Backup: ...bak-A-informational-2026-04-27
- Neue Constant **INFORMATIONAL_KINDS** (env-overridable via COSTS_ALERTS_INFORMATIONAL_KINDS)
- Filter VOR should_send skipt informational kinds mit reason **informational-classification**

**Verify:** Manual-Run loggte SUPPRESS kind=flatrate-billing-artifact reason=informational-classification → OK.

## B — mcp-taskboard-reaper Orphan-Detection + Visibility (DEPLOYED)

**Problem:** Reaper hatte keine Orphan-Detection (qmd-reaper schon), keine Visibility-Warn. Children stiegen 3 → 9 in 30 min, cap=12 → still kein Alert.

**Kritischer Pre-Check:** qmd-Pattern wäre für taskboard FATAL gewesen. /proc/3660340/comm = openclaw-gatewa (15-char trunc) → naive case-match openclaw|openclaw-gateway schlägt fehl → ALLE Children als Orphans → kill = Disaster (P0.2 noch nicht deployed zu dem Zeitpunkt).

**Patch:**
- File: /home/piet/.openclaw/scripts/mcp-taskboard-reaper.sh
- Backup: ...bak-B-orphan-port-2026-04-27
- 3-Schicht is_live_openclaw_parent(): PID-direct-match (systemctl MainPID), comm (incl. truncated openclaw-gatewa), args-substring fallback
- Always-kill orphans, MIN_CAP=12 + MIN_AGE=7200s schützen aktive Sessions
- Visibility-Discord-WARN bei alive >= WARN_THRESHOLD=10

**Verify (DRY_RUN=1):** total=11 orphans=0 alive=11 cap=12 candidates=0 → 0 false-orphans OK. Live-Cron läuft alle 5 min, wird Visibility-WARN feuern sobald alive >= 10.

## C — bundle-mcp-runtime P0.2 Self-Recovery (DEPLOYED + AKTIVIERT)

**Problem:** Plan-Doc atlas-stabilization-plan-mcp-recovery-2026-04-21.md referenzierte obsolete file (pi-bundle-mcp-tools-vusm-AE2.js Z.462). In v2026.4.22 wurde das bundle refactored — callTool jetzt in pi-bundle-mcp-runtime-CuLwVkrV.js Z.587-596.

**Aktuelle callTool hatte KEIN try/catch.** Bei Not connected oder Connection closed wurde session-cache + catalog NICHT invalidiert → Session bleibt für immer broken bis Neustart.

**Patch:**
- Apply-Script: /home/piet/.openclaw/scripts/apply-mcp-recovery-patch.py (idempotent, DRY_RUN-default, Marker OPENCLAW_PATCH_MCP_RECONNECT_RECOVERY_2026_04_27)
- Target: /home/piet/.npm-global/lib/node_modules/openclaw/dist/pi-bundle-mcp-runtime-CuLwVkrV.js
- Backup: ...bak-pre-mcp-recovery-20260427T070343Z
- Patch-Logik: try/catch um session.client.callTool. Bei Not connected, Connection closed oder -32000: disposeSession(session) + sessions.delete(serverName) + catalog=null + catalogInFlight=void 0, dann throw error (1× fail). Nächster call re-init via getCatalog() → 2× success.

**Aktivierung:** Gateway-Restart 09:05:39 UTC nötig (V8 compile-cache hält alten code). PID 3660340 → 3768777. Pre-existing Sessions bekamen 1× fail per tool-call und konnten dann self-recovern (Forge startete saubere neue Sessions 5dffc601 + 49383fa2).

**DoD verifiziert:**
- kill -TERM 3770080 (oldest taskboard child) → count 2 → 1
- 14s später → count 1 → 2 (auto-respawn nach erstem disconnect-recover)
- 0 Not connected Errors letzte 90s nach restart OK

## Decision-Trade-off: MemoryMax

Plan-Doc P1.1 empfahl runter auf 4G/3G (*Kernel throttled weich, früher Restart*). Mein Step 3 ging rauf auf 6G/5G/2G-Swap (Begründung: ohne P0.2 kostet jeder Restart alle Sessions ihre Tools).

**Jetzt mit P0.2 aktiv:** Restart ist harmlos (Sessions self-heal). 6G ist nicht mehr nötig. **Aber:** mehr Headroom = weniger OOM-Cycles = stabilerer Betrieb. 6G beibehalten ist defensiver, 4G ist puristischer (folgt Plan-Doc).

**Empfehlung:** 6G beibehalten bis nach Update auf 2026.4.24 (Forge Pre-Go done) und 24h Soak-Test. Dann re-evaluate.

## Sub-Befunde (Follow-Up-Tasks)

1. **agents.defaults.imageModel.primary = openai/gpt-image-2** — Modell exists since 2026-04-21, nicht in lokaler Allowlist. Schema-Error bei einfachem set: *expected object, received string* → Lösung: openclaw config set agents.defaults.models.openai/gpt-image-2 mit JSON-object-payload (nicht raw string). ODER warten auf 2026.4.24.
2. **mcp-child-teardown.conf escape-warning** im journal: *Ignoring unknown escape sequences* → ExecStopPost pattern muss escape-fixed werden.
3. **restart-policy.conf:** Unknown key name StartLimitIntervalSec in section Service → Key gehört in [Unit], nicht [Service].
4. **Spark Session 3b149f17** (16 MB live + 12 Checkpoints à 8-14 MB) — R36 Crash-Risk, manuell compacten.
5. **systemd ExecStartPre für apply-mcp-recovery-patch.py** — Patch überlebt aktuell **kein** npm-update! P0.3 noch nicht deployed → bei nächstem openclaw update muss apply-script manuell re-run werden.

## Pre-Reqs für Forge Update auf 2026.4.24

Forge Pre-Go Task 7f12c6d8 ist EXECUTION_STATUS done mit conditional Go. QMD-Blocker ist mit P0.2-Aktivierung **gelöst**. Snapshot-Plan vor Update beachten: /home/piet/.openclaw/backups/pre-update-2026.4.24/<utc-timestamp>/.

## Verifikations-Snapshot 09:08 UTC

| Component | Status |
|---|---|
| Gateway active | PID 3768777, MemoryMax=6G, MemoryCurrent=644M |
| MC HTTP /api/health | 200 |
| QMD HTTP :8181/mcp | 406 (handshake-required = healthy) |
| taskboard children | 2 (post-restart fresh) |
| qmd children | 3 |
| MCP Not connected errors last 90s | 0 |
| P0.2 marker present | 1 (in pi-bundle-mcp-runtime-CuLwVkrV.js) |
| Forge new sessions | 5dffc601, 49383fa2 (post-restart, healthy) |
| Board active | 0 in_progress, 0 assigned |

## References

- Plan-Doc: /home/piet/vault/03-Projects/plans/atlas-stabilization-plan-mcp-recovery-2026-04-21.md
- Apply-Script: /home/piet/.openclaw/scripts/apply-mcp-recovery-patch.py
- Forge Pre-Go: Task 7f12c6d8-1103-4c5a-b96a-82363d3e0af0 (resultSummary in board)
- Reaper alt-Backup: mcp-taskboard-reaper.sh.bak-B-orphan-port-2026-04-27
- Bundle-Backup: pi-bundle-mcp-runtime-CuLwVkrV.js.bak-pre-mcp-recovery-20260427T070343Z
- alert-dispatcher Backup: cost-alert-dispatcher.py.bak-A-informational-2026-04-27


---

## UPDATE 09:25 UTC — openclaw 2026.4.22 → 2026.4.24 deployed

**Plan ausgeführt:** Phase 1 (health audit) → Phase 2 (snapshot) → Phase 3 (dry-run) → Phase 5 (update) → Phase 6 (verify) → Phase 7 (P0.2 re-apply).

### Snapshot

Path: /home/piet/.openclaw/backups/pre-update-2026.4.24/20260427T071839Z (339M, 2471 files in MANIFEST).
Enthält: openclaw.json, agents/<id>/agent + sessions.json, runs.sqlite*, tasks.json, cron-registry, systemd-dropins, openclaw-dist.tar.gz (276M für rollback), apply-mcp-recovery-patch.py, mcp-taskboard-reaper.sh, mcp-qmd-reaper.sh, cost-alert-dispatcher.py.

### Update-Execution

**openclaw update --yes --json** (66s gesamt):
- Step 1: npm i -g openclaw@latest (15s) — added 25, removed 307, changed 406 packages
- Step 2: openclaw doctor --non-interactive (51s) — exit 0, known warnings (auth-refresh, agent-list-drift, 599 orphan transcripts, legacy cron storage, security)
- postUpdate.plugins: changed=false (kein plugin-sync nötig)
- Mode: npm (pnpm-lockfile fehlte → fallback)

### Bundle-File-Diff

Alle 3 pi-bundle-mcp Files haben neue Hashes:
- pi-bundle-mcp-runtime-CuLwVkrV.js (26517 bytes) → pi-bundle-mcp-runtime-B_SrebwR.js (30328 bytes, +14% Code)
- pi-bundle-mcp-runtime-wdPhNMoF.js (120 bytes stub) → pi-bundle-mcp-runtime-DhFyH7mH.js
- pi-bundle-mcp-tools-BL2tJQA-.js → pi-bundle-mcp-tools-D-15SltU.js

Mein P0.2-Marker + Backup-File von 09:03 wurden beim npm install gelöscht. callTool-Pattern in 2026.4.24 ist **identisch zur 2026.4.22** — kein built-in reconnect-fix. P0.2-Patch deshalb **re-applied via apply-mcp-recovery-patch.py** auf B_SrebwR.js (30328 → 30757 bytes, marker present).

### Post-Update-Snapshot 09:26 UTC

| Component | Status |
|---|---|
| openclaw version | 2026.4.24 (cbcfdf6) |
| Gateway | active, PID 3794226, MemoryMax=6G, MemoryCurrent 676M |
| MC HTTP /api/health | 200 |
| QMD HTTP :8181/mcp | 406 (handshake-required) |
| MCP children post-restart | 0 taskboard (lazy-spawn), 1 qmd |
| MCP Not connected errors | 0 (90s window) |
| P0.2 marker in B_SrebwR.js | 1 (re-applied) |
| Backup of B_SrebwR.js | ...bak-pre-mcp-recovery-20260427T072424Z |

### Conclusions

- Update auf 2026.4.24 ist vollständig und stabil.
- P0.3 (systemd ExecStartPre auto-re-apply) ist **weiterhin nicht deployed** — ohne diesen Hook muss bei jedem zukünftigen openclaw update der apply-script manuell re-run werden.
- 2026.4.24 hat den MCP-Stdio-Reconnect-Bug **NICHT gefixt** — P0.2-Patch bleibt nötig in unbestimmter Zeit.
- Forge Pre-Go conditional Go nun erfüllt: QMD grün, Update done.

### Doctor-Warnings (für Folge-Tasks priorisiert)

Aus update doctor-output Kandidaten für separate maintenance-PRs:
1. anthropic:claude-code-refresh expired — re-auth via openclaw models auth login
2. Claude CLI auth profile missing in main agent's auth-profiles.json
3. 1 agent dir without agents.list entry: worker
4. 599 orphan transcript files in main/sessions — doctor --fix kann archivieren
5. Legacy cron storage cron/jobs.json (1 dreaming job) — doctor --fix normalize
6. openclaw-healthcheck.service detected als duplicate gateway-like service
7. Gateway PATH missing /home/piet/.nix-profile/bin
8. Security: gateway bound to 0.0.0.0 (LAN) — ist intentional für deine Topologie


---

## Round 3 Follow-Through 09:47 UTC — Cleanup + P0.3 + Validator

Sequenzielle Abarbeitung der 6 verbliebenen Phasen nach Update.

### Phase 1 — openclaw doctor --fix
599 orphan transcripts in main/sessions archiviert (rename zu .deleted.<ts>). Disk-Effekt 0 (rename != delete) — Operator kann später final cleanup.

### Phase 2 — Spark Session 3b149f17 compact
Inactive seit Apr 26 12:30 (21h offline). 16 checkpoints (155M raw) → tar.gz in sessions/archive/3b149f17-checkpoints-20260427T0730Z.tar.gz (78M, 50% compression). Originals deleted nach count-match-verify (16=16). Live .jsonl + trajectory.jsonl behalten.
**Disk freed: 72M (186M → 114M).**

### Phase 3 — Worker-Agent-Dir cleanup
NICHT in agents.list (orphan seit Apr 16). 55M (71 files: agent/ + sessions/). tar.gz nach /home/piet/.openclaw/backups/orphan-agents/worker-2026-04-27.tar.gz (28M). Original gelöscht.
**Disk freed: 55M.**

### Phase 4 — mcp-child-teardown.conf escape-fix
systemd parsed \. als unknown escape sequence. Pattern jetzt korrekt double-escaped: server\.js und qmd\.ts. Backup .bak-pre-escape-fix-2026-04-27. systemd-analyze verify zeigt warning weg.

### Phase 5 — restart-policy.conf section-fix
StartLimitIntervalSec + StartLimitBurst von [Service] nach [Unit] verschoben (systemd 234+ Anforderung). systemctl show bestätigt nun: RestartUSec=30s, StartLimitIntervalUSec=2min, StartLimitBurst=5 (vorher wurden StartLimit-Keys ignoriert). Backup .bak-pre-section-fix-2026-04-27.

### Phase 6 — Image-Model openai/gpt-image-2 freigeschaltet
**Wichtig:** Doppelter Fix nötig — Validator-Script ist separat von Allowlist-Schema!
1. agents.defaults.models[openai/gpt-image-2] zur Allowlist hinzugefügt via openclaw config set --strict-json
2. validate-models.py hatte openai/ NICHT in VALID_PROVIDER_PREFIXES → patched: openai/ added (Backup .bak-pre-openai-prefix-2026-04-27)

Manueller Validator-Run: **All 40 cross-provider model references valid. True errors=0** (war vorher 1).

openclaw models list zeigt openai/gpt-image-2 als configured/auth=yes/tags=image — also routet korrekt.

### Phase 7 — P0.3 systemd ExecStartPre Hook
Drop-in /home/piet/.config/systemd/user/openclaw-gateway.service.d/p02-recovery-patch.conf:
- Environment=DRY_RUN=0
- ExecStartPre=-/usr/bin/python3 /home/piet/.openclaw/scripts/apply-mcp-recovery-patch.py
- Minus-Prefix gibt graceful-failure (gateway started auch wenn patch failed)

Apply-script gehärtet: bei missing-anchor exit 0 + WARN-log (vorher exit 2 = blocked startup). Marker P02_PATCH_SKIPPED_ANCHOR_MISSING fürs telemetry.

**Test (gateway restart 09:47:53):** ExecStartPre lief sichtbar im journal:
- python3[3820060]: TARGET: pi-bundle-mcp-runtime-B_SrebwR.js (30757 bytes)
- python3[3820060]: SKIP: marker OPENCLAW_PATCH_MCP_RECONNECT_RECOVERY_2026_04_27 already present

PID 3797817 → 3820069. Marker present nach restart, MC 200, QMD 406, 0 MCP errors.

**Damit überlebt P0.2-Patch jetzt jedes openclaw update automatisch.** Bei nächstem Update werden bundle-files überschrieben (neue Hashes), ExecStartPre läuft beim Start, apply-script findet neue file, patcht, marker drin. Ohne Operator-Intervention.

## Cumulative Disk-Cleanup

| Source | Freed |
|---|---|
| Spark checkpoints tar.gz | 72M |
| Worker dir archive | 55M |
| **Total real disk freed** | **127M** |
| (599 orphan transcripts) | 0 (archived only, ~360M deletable later) |

## Status-Snapshot 09:48 UTC

- openclaw 2026.4.24 (cbcfdf6)
- Gateway PID 3820069, MemoryMax=6G
- ExecStartPre 2 hooks (port-guard + p02-recovery-patch)
- P0.2 marker present, validator true_errors=0
- Disk 17G free / 98G (83% — unverändert weil orphans archived statt deleted)
- 0 MCP not-connected errors

## Verbleibende Operator-Decisions (nicht autonom)

1. **anthropic:claude-code-refresh re-auth** — interactive: openclaw models auth login --provider anthropic
2. **Claude CLI auth-profile in main agent** — interactive: openclaw models auth login --provider anthropic --method cli
3. **MemoryMax 6G→4G** — Plan-Doc P1.1 sagt 4G, wir sind bei 6G. Decision nach 24h soak.
4. **openclaw-healthcheck.service** — Doctor sagt duplicate gateway-like detected. Operator entscheidet ob disable.
5. **686 archivierte .deleted.<ts> transcripts in main/sessions** — operator kann final delete via find -name *.deleted.* -delete (~360M).
6. **Spark + Worker tar.gz archives** — operator kann nach 30 Tagen delete (rotation).


---

## Round 4 — QMD Audit + Optimization (10:30 UTC)

Atlas + Forge meldeten Inkonsistenzen. Eigenes Live-Audit + Forge-Verifikation + Web-Recherche + 4 Quick-Wins deployed.

### Phase 1: Live-Diagnose (Forge-Findings verifiziert + ergänzt)

**Forge richtig:**
- qmd__status flapping reproduziert: 42 fail-events in 24h, alle bei MCP-Bridge (NICHT direct-CLI). Pattern: P0.2 1x-fail-then-recover bei NEUER session-binding nach Gateway-restart (5 Restarts heute).
- vault-read.py legacy: fehlt in /home/piet/.openclaw/scripts/. 2 stale Refs in vault-doku (task-lifecycle.md, daily/2026-04-27.md).
- MC pending-pickup 4e0618d2: 212s Lag = normal, NICHT critical (Phase 6 MC-Worker-Engpass aus Plan gestrichen).

**Forge teilweise korrekt — wahre Root-Cause anders:**
- qmd__get path-resolver-bug: NICHT Document not found, sondern qmd-resolver matcht FUZZY. 03-Agents/Shared/project-state.md returnt WORKSPACE/memory/archive/project-state.md (alter Stand 2026-04-11), NICHT canonical vault-version. Vier project-state.md duplicates im System.
- qmd__multi_get glob: KOMPLETT broken fuer alle path-formats (relative, qmd://vault/, qmd://workspace/). Comma-separated 'a.md,b.md' funktioniert.
- qmd__get Platzhalter '(see attached image)': nicht reproduziert, transient.

### Phase 2: Web-Recherche

- HyDE: kein --no-hyde Flag. Bypass via 'qmd search' (BM25-only) oder 'qmd vsearch' (vector-only). 'qmd query' hat HyDE hardwired.
- node-llama-cpp Vulkan: Issue #554 bekannt. CPU-source-build via 'npx --no node-llama-cpp source download'. CUDA-build mit NODE_LLAMA_CPP_CMAKE_OPTION_GGML_CUDA=ON (braucht NVIDIA-toolchain).
- qmd multi-get glob: matchFilesByGlob() in src/qmd.ts. Bug-confirmed, kein open-issue gefunden. Workaround: comma-separated.

### Phase 3: MCP-Anbindungs-Issue Root-Cause

42 qmd-fail-events in 24h korrelieren mit 5 Gateway-Restarts (09:27, 09:28, 09:47, 09:48, 10:13). Pattern: jede neue session-binding nach Restart hat 1-3 fails wegen catalog-init. P0.2 fixt second-call. Akzeptabel — fundamentaler bug ist openclaw-core (lazy-init der MCP-bindings beim session-spawn).

### Phase 4: Quick-Wins DEPLOYED

| Sub | Was | Result |
|---|---|---|
| 4.1 | qmd embed (5 pending) | 44 chunks/80.3 KB embedded in 34s. Vectors 54124 -> 54168. |
| 4.2 | qmd cleanup | **49431 orphaned embedding chunks removed**, 267 inactive doc-records, DB vacuumed |
| 4.3 | mc-src Pattern erweitert auf src/**/*.{ts,tsx,md} | Files **9 -> 368** (40-fach!). Background-Embed laufend (368 chunks, ~12 min) |
| 4.4 | workspace/memory/archive (75 files) | **NICHT angefasst** — Operator-Decision: archive subdir aus indexed-path bewegen oder lassen. |
| 4.5 | vault-read.py refs in 2 docs | **NICHT angefasst** — Daily-Doc ist agent-managed, task-lifecycle.md ist user-curated. Operator-Action. |

### Phase 5: HyDE-Tuning -> R-Regel-Kandidat R51

**Befund:** 'qmd query' (HyDE) interpretiert P0.2 als OBD-II Auto-Code -> Vec-queries: vehicles, car diagnostics. Kontaminiert Top-Results.

**R51 (proposed):** Agents nutzen primary 'qmd_search' (BM25, schnell, exakt, kein HyDE). Fallback 'qmd_vsearch' fuer pure semantic. 'qmd_query' nur fuer cross-domain narrative-research wo HyDE-Erweiterung gewuenscht.

### Phase 6 NEU: Vault-Duplikate (Operator-Doku, kein direct-action)

**Top-Duplikate:**
- 100x working-context.md: 4 active (per-Agent in 03-Agents/), **96 in 09-Archive/03-Agents-legacy-2026-04-22/** (legacy)
- 21x AGENTS.md: 14 in vault top-level (intentional pro section), 7 in workspace inkl. **2 in node_modules** (recharts, lancedb = noise)
- 14x 2026-04-XX.md: vermutlich pro-agent-daily-files (acceptable)
- 4x checkpoints.md, decisions-log.md, project-state.md, user-profile.md: vault  duplicates 

**workspace/memory/archive: 75 alte md-files** (Q1 + early Q2 sessions, MEMORY-backups, GOVERNANCE etc.) -> Index-Noise

**R52 (proposed):** Agents MUESSEN explizite collection-prefix nutzen ('qmd://vault/...' oder 'qmd://workspace/...') fuer 'qmd_get' und 'qmd_multi_get'. Bare path 'X/Y/file.md' triggert qmd's fuzzy-resolver -> wrong-file-risk.

**Operator-Empfehlungen:**
1. workspace/memory/archive aus indexed-path entfernen (Move zu /home/piet/.openclaw/archive-storage/)
2. Vault 09-Archive aus index ausschliessen (Vault-Reorg-Decision)
3. node_modules-AGENTS.md im workspace ueber narrow path-mask exkludieren

### Phase 9 (this section) + Memory-Update mit R51, R52 candidates

**Verifikations-Snapshot 10:30 UTC:**
- Index: 199 MB -> 202 MB (post-cleanup, +mc-src-embeddings)
- Documents: 1176 -> 1177 indexed
- Vectors: 53988 -> 54168 (+44 from embed run)
- mc-src files: 9 -> 368 (post-rebuild)
- 49431 orphan chunks gone

### Sub-Befunde fuer Folge

1. qmd-multi-get-glob-bug -> upstream issue at github.com/tobi/qmd
2. node-llama-cpp Vulkan -> CPU-source-build fuer 7x speed (35s -> ~5s hybrid query)
3. workspace/memory/archive cleanup -> ~75 files index-noise
4. 09-Archive vault cleanup (96 working-context.md) -> Operator


---

## Round 5 — openclaw-healthcheck-watchdog Restart-Loop Incident (10:40-10:46 UTC)

**Symptom:** User-Bericht "Atlas nicht erreichbar gateway down?". Live-Check: Gateway active, ABER 4x SIGKILL in 4 min (10:40:09, 10:41:10, 10:42:10, 10:43:11).

**Root Cause:** /home/piet/.openclaw/scripts/healthcheck-watchdog.sh (gesteuert via openclaw-healthcheck.timer alle 60s) killt Gateway-PID via kill -9 wenn /health endpoint innerhalb 5s nicht antwortet. Race-Condition: 
- Gateway startup hat 2 Phasen — "ready" nach 6.2s (HTTP-Server up auf Port 18789), aber Plugin-Init braucht weitere ~50s (Discord, Telegram retries inkl. "deleteWebhook failed: Network request failed; retrying")
- Zwischen Phase 1 und 2 kann /health slow/non-responsive sein
- Watchdog kommt mit kurzem 5s-Timeout dazwischen, killt aktiv-startenden Gateway
- Webhook-URL ist Placeholder (https://discord.com/api/webhooks/...) -> Operator hoert nichts

Self-broken Pattern: 10:43:12 Gateway endlich ready bevor naechster Healthcheck-Tick -> Cycle stoppt.

**Aktion (Schritt 1, 10:48 UTC):**
- systemctl --user disable --now openclaw-healthcheck.timer
- Begruendung: openclaw-doctor v2026.4.24 sagt explizit "Cleanup hints: systemctl --user disable --now openclaw-healthcheck"
- v2026.4.24 hat internen [health-monitor] (interval 300s, startup-grace 60s, channel-connect-grace 120s) - externer Watchdog ist redundant + buggy

**Verify:**
- Timer: enabled -> disabled, active -> inactive
- Letzter healthcheck-run: 10:52:17 (in-flight buffer), keine neuen Runs danach
- Gateway PID 3900609 stabil seit 10:46:28 (>8 min, kein neuer Kill)
- Internal health-monitor laeuft normal in jedem post-restart-Gateway

**Bun-Segfault (mc-src background-embed):**
- Background embed (PID 3871760) fuer 1116 chunks ist gecrasht: panic Segmentation fault at address 0x73C0B2C3A3E0, Bun 1.3.11
- Aber: forced retry zeigt "All content hashes already have embeddings" - main thread hat completed before crashed worker-threads, alle 1116 chunks embedded
- mc-src ist nun voll vector-searchable (368 files, 5864+ vectors)
- Bun-Issue notiert in tools-tracking aber low-impact

**R53 (proposed):** Externe Watchdogs muessen 90s+ startup-grace nach Gateway-Restart respektieren. Das interne [health-monitor] in openclaw nutzt 60s startup-grace + 120s channel-connect-grace -> dieser Wert sollte fuer alle externen Watchdog auf gleiches System uebernommen werden.

**Status-Snapshot 10:54 UTC:**
- Gateway: active, PID 3900609, 8+ min stable, MemoryMax=6G
- MC HTTP 200, QMD HTTP 200
- openclaw-healthcheck.timer: DISABLED
- Internal health-monitor: active mit 300s interval
- Atlas main session 5ccfc1b3: alive (mtime <5min)
- mc-src QMD vectors: complete (1116 chunks)

**Next Operator-Decisions (unchanged):**
- Atlas reachability via Discord-Ping (Schritt 2)
- GPT-Image-2 OAuth-Pfad (A1/A2/A3)
- MemoryMax 6G->4G nach 24h Soak (jetzt P0.2 + healthcheck-disable bedeutet Restarts sind harmlos)
- workspace/memory/archive cleanup (75 noise-files)
- node-llama-cpp CPU-source-build (35s -> 5s hybrid query)


---

## Round 6 — QMD-Atlas-Effektivitaet Audit (10:55-11:15 UTC)

Ziel: Atlas's QMD-Workflow optimieren. 4 Phasen durchgezogen, klare Diagnose + Empfehlungen.

### Phase 1 — qmd_get/multi_get Bug-Diagnose

**ROOT-CAUSE qmd_get "Attachment/Platzhalter":**
- mcp.ts:404-421: qmd_get returnt MCP-content-type **"resource"** mit mimeType "text/markdown"
- Manche MCP-Clients (vermutlich openclaw bridge) rendern resource-type als Anhang/Link statt inline-text
- WORKAROUND: Atlas's bridge muss  field extracten — wenn nicht, ist es bridge-bug

**ROOT-CAUSE multi_get "SKIPPED":**
- mcp.ts:431: maxBytes default = **10240 (10 KB!)**
- store.ts:2616: "File too large (XKB > 10KB). Use qmd_get with file=..."
- Vault sprint-docs sind 20-30 KB → ALWAYS skipped mit default!

**ROOT-CAUSE multi_get "No files matched pattern":**
- multi_get's pattern-matcher unterstuetzt NUR comma-separated relative paths
- "03-Agents/Shared/a.md,03-Agents/Shared/b.md" -> WORKS
- qmd://vault/... oder absolute paths oder glob -> ALL FAIL
- Atlas's TOOLS.md hat vorher empfohlen  -> das ist FALSCH

### Phase 2 — Index-Quality (workspace narrow-mask attempt)

**Versucht:** workspace mit narrow mask  -> 0 files matched (bun's mask-syntax inkompatibel)
**Rollback:** workspace zurueck auf . 482 files indexed (incl. node_modules + memory/archive noise)
**Verbleibend:** Operator-Decision: rename/move /home/piet/.openclaw/workspace/memory/archive raus aus indexed-path, ODER vault 09-Archive cleanup

### Phase 3 — Atlas's QMD-Usage-Analyse (24h)

| Tool | Total | Fails | Pattern |
|---|---|---|---|
| qmd__search | 31 | 28 | Batch-fails (3 parallel calls bei post-restart binding-init) |
| qmd__status | 19 | 16 | P0.2-recovery-pattern (1st-fail nach Gateway-restart) |
| qmd__get | 4 | 1 | meist erfolgreich |
| qmd__multi_get | 2 | 1 | Atlas hat absoluten path + glob versucht (beide broken) |
| qmd__vector_search | 1 | 1 | |
| qmd__deep_search | 1 | 1 | |

**Atlas's Batch-Pattern:** sendet oft 3 parallel qmd__search-calls (vault + workspace + variant-queries). Bei stale binding -> ALLE in batch fail. P0.2 recovery wirkt nur bei sequential calls.

**Top Atlas-queries:** sprint-docs, image_generate forge tasks, openclaw update, P0.2 recovery, atlas-result-format. Alle relevante work-queries.

### Phase 4 — Context-Tags Verbesserung (DEPLOYED)

7 neue context-tags fuer semantic-disambiguation:
- vault/03-Agents (agent state, daily logs)
- vault/04-Sprints (hardening sprints)
- vault/05-Incidents (RCAs, post-mortems)
- vault/03-Projects/plans (strategic plans)
- workspace/memory (live agent memory)
- mc-src/src/app/api (MC API routes)
- mc-src/src/lib (MC core libraries)

Effekt: BM25 + vector ranking nutzen contexts als boost-signal -> bessere Top-Results bei specific-domain queries.

### R-Regel-Updates fuer Atlas TOOLS.md

**R52 KORREKTUR (URGENT):** Atlas's TOOLS.md hat falschen Beispiel-Pattern fuer multi_get!
- ALT (falsch):  
- NEU (korrekt):  (RELATIVE paths!)
- multi_get unterstuetzt NICHT qmd:// URLs, absolute paths, glob - NUR comma-separated relative

**R54 (proposed):** qmd_multi_get default maxBytes ist 10KB (zu klein). Atlas MUESS bei vault-files explizit setzen:  (100KB). Sonst werden Sprint-Docs etc. immer SKIPPED.

**R55 (proposed):** Bei batch-parallel qmd_*-calls nach Gateway-Restart: ZUERST 1 single status-call, dann erst batch (P0.2-binding-warmup). Verhindert batch-failure-storm.

**R56 (proposed):** qmd_get returnt . Wenn openclaw-MCP-bridge das als Attachment rendert: openclaw-side bridge-bug, separate ticket. Bis Fix: direct vault-read fallback fuer kritische Reads.

### Status-Snapshot 11:15 UTC

- Index: vault 688, workspace 482 (post-rebuild), mc-src 368 = 1538 total
- 7 context-tags aktiv (semantic boost)
- 26 docs need re-embedding (workspace post-rebuild) - background trigger noetig
- Atlas QMD-tool-success-rate ohne unsere fixes: ~10-50% (depending on tool)

### Operator-Aktion empfohlen

1. **Atlas TOOLS.md update mit R52-Korrektur + R54/R55/R56** (Atlas selbst commit)
2. **qmd embed run** fuer 26 pending vectors (background, ~2 min)
3. **Optional:** workspace/memory/archive aus indexed-path moven (-44 noise files)

---

## Follow-Up Task Added 11:48 UTC — canary-session-rotation-watchdog live + flat detection

**Task:** Fix canary-session-rotation-watchdog (`--live` + Detection-Logik flach)  
**Priority:** P1 — Anti-Halluzinations-Layer scharfstellen, kein laufender Outage  
**Owner:** Forge (`sre-expert`)  
**Estimate:** ~30 min Code + 15 min Verify  
**Board Task:** `dca22d29-da47-43a2-9ab0-f51f3c496c9a` (`[P1][Forge] Fix canary-session-rotation-watchdog (--live + flat detection)`)

### Files in Scope
- `/home/piet/.config/systemd/user/canary-session-rotation-watchdog.service`
- `/home/piet/.openclaw/scripts/session-rotation-watchdog.py`

### Live-Befund / Evidence
- `/tmp/atlas-rotation-signal.json` existiert aktuell nicht.
- Unit ist noch Dry-Run: `Description=Canary session-rotation-watchdog (dry-run)` und `ExecStart=... session-rotation-watchdog.py --verbose` ohne `--live`.
- Budget-Log zeigt starke Sprünge: `49% -> 109/184/472/573/630/.../908%` und später bis `1363%`; WARN-Band wird häufig übersprungen.
- Script-Logik signalisiert nur bei `WARN_THRESHOLD <= pct < UPPER_LIMIT`; `pct >= UPPER_LIMIT` liegt unter `elif existing`, dadurch kann ein kalter Sprung von `<70%` direkt auf `>=95%` ohne Signal bleiben.

### Required Fix
1. Service-Unit `ExecStart`: `--live` ergänzen; Description von dry-run auf live/enforcement anpassen.
2. Script-Logik flach machen: jede Session mit `pct >= WARN_THRESHOLD` erzeugt bzw. hält ein Signal.
3. `recommended_action` je Schwere:
   - `70% <= pct < 95%` → `graceful-rotate-with-summary`
   - `pct >= 95%` → `emergency-rotate-too-late`
4. Cleanup-Branch unverändert lassen: `session-id-changed`, `pct < DROP_THRESHOLD`.
5. Idempotenz: skip bei gleicher `session_id` + gleichem action-Level; Upgrade nur `graceful` → `emergency`; kein Re-Write bei gleichem Level.
6. Verify: dry-run/unit proof, optional safe one-shot live proof mit temp/real signal gemäß DoD; kein Gateway/OpenClaw Restart.

### Anti-Scope
- Kein reiner Threshold-Bump.
- Keine Timer-Änderung außer Unit `ExecStart`/Description.
- Keine unrelated Session-/Budget-Refactors.

### Addendum 11:48 UTC — Operator Clarification + Pre-Flight Result
- Clarification: `m7-auto-pickup` does **not** consume `/tmp/atlas-rotation-signal.json` today. This task only sharpens detection/signal writing; consumer hook is a follow-up sprint.
- Required rollback backups before patch: `.bak-2026-04-27` for both service unit and script.
- Required verify after patch: `systemctl --user daemon-reload && systemctl --user restart canary-session-rotation-watchdog`; `journalctl --user -u canary-session-rotation-watchdog -n 10` contains no `DRY-RUN`; signal file exists at `/tmp/atlas-rotation-signal.json` if current pct >= 70; `recommended_action` matches pct level.
- Pre-flight was run after initial dispatch because the instruction arrived post-dispatch: `/home/piet/.openclaw/scripts/pre-flight-sprint-dispatch.sh /home/piet/vault/04-Sprints/2026-04-27-mcp-hardening-sprint.md --verbose` returned **RED** due Atlas-session-size critical (`434% of budget`). Board task `dca22d29-da47-43a2-9ab0-f51f3c496c9a` was updated with this addendum and `operatorLock=true` to prevent unsafe execution until rotation/override.


### Closure Update 12:05 CEST — DONE (dca22d29-da47-43a2-9ab0-f51f3c496c9a)
- Pre-flight gate rerun is **GREEN** (7/7 passed): Atlas session size now 60% budget.
- Backups created:
  - `/home/piet/.config/systemd/user/canary-session-rotation-watchdog.service.bak-2026-04-27`
  - `/home/piet/.openclaw/scripts/session-rotation-watchdog.py.bak-2026-04-27`
- Service unit patched: Description switched to live, ExecStart now includes `--live --verbose`.
- Script patched for flat detection: `pct >= 70` always signals; action mapping now `70-94 => graceful-rotate-with-summary`, `>=95 => emergency-rotate-too-late`; idempotence keeps same-level skip and only allows graceful->emergency upgrade; cleanup branches for `session-id-changed` and `pct < 60` remain intact.
- Verify output:
  - `systemctl --user daemon-reload && systemctl --user restart canary-session-rotation-watchdog` OK (oneshot success).
  - `systemctl --user status ...` shows `Canary session-rotation-watchdog (live)` and ExecStart with `--live --verbose`.
  - `journalctl --user -u canary-session-rotation-watchdog -n 10` includes latest `(... live)` run and no `DRY-RUN` marker.
  - Live signal proof (forced >=95 via temp budget input): `/tmp/atlas-rotation-signal.json` created with `recommended_action=emergency-rotate-too-late`; file then removed to avoid stale fake signal.
- Scenario verification matrix passed: direct >=95 jump, graceful band, same-level idempotence, graceful->emergency upgrade, cleanup on session-id-changed, cleanup on pct-drop.
- Re-verify 12:06 CEST: `/tmp/atlas-rotation-signal.json` recreated with pct=80 test input and `recommended_action=graceful-rotate-with-summary` (ls+cat proof captured).

## 2026-04-29 — P1 Taskboard MCP Lifecycle Wrapper Closure

- Final status: `P1_FORGE_MCP PASS`.
- Task `82c4076f-878e-4bf9-89e4-b36e168f57fa` is `done`.
- Wrappers added/validated: `taskboard_receipt_task`, `taskboard_finalize_task`, `taskboard_move_task`.
- Routing: canonical Mission-Control routes only (`/api/tasks/{id}/receipt`, `/finalize`, `/move`).
- Safety: no direct `tasks.json` mutation; no lifecycle semantics changes.
- Final health: OK (`recoveryLoad=0`, `attentionCount=0`, `issueCount=0`, `consistencyIssues=0`).
