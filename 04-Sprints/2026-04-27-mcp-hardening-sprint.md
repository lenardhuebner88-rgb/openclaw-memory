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
