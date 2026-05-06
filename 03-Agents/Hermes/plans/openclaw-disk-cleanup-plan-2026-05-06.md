# OpenClaw / huebners Disk Cleanup Plan — 2026-05-06

> **Scope:** Plan only. No cleanup executed. No services restarted. No config changed.

**Goal:** Reduce root filesystem usage from `87%` toward `<80%` with lowest operational risk first.

**Architecture:** Use a gated cleanup ladder: remove inert build artefacts first, then old caches/backups, then only later touch runtime/session/state data. Every destructive step must be preceded by a dry-run list and followed by `df -h /` plus targeted health checks.

**Live evidence timestamp:** 2026-05-06 08:24–08:27 CEST

---

## 1. Current disk state

```text
/ filesystem: 98G total, 81G used, 13G free, 87% used
journals: 523.1M
/home/piet total scanned under same filesystem: ~45.7G
```

Largest top-level user-space areas:

```text
20.1G  /home/piet/.openclaw
 4.8G  /home/piet/ollama
 4.2G  /home/piet/.ollama/models
 4.2G  /home/piet/backups
 3.7G  /home/piet/.cache
 2.4G  /home/piet/.local
 2.0G  /home/piet/.npm-global
 2.0G  /home/piet/.hermes
```

Key OpenClaw breakdown:

```text
8.7G  /home/piet/.openclaw/workspace
4.1G  /home/piet/.openclaw/agents
1.6G  /home/piet/.openclaw/backups
1.3G  /home/piet/.openclaw/lib
1.3G  /home/piet/.openclaw/memory
604M  /home/piet/.openclaw/npm
```

---

## 2. Best cleanup levers ranked by risk-adjusted value

| Rank | Candidate | Est. reclaim | Risk | Recommendation |
|---:|---|---:|---|---|
| 1 | Mission Control non-live `.next*` build artefacts | ~4.9G gross / ~3.5–4.5G realistic | Low to medium | First cleanup target. Keep live `.next`; keep one latest verified rollback build initially. |
| 2 | Large old general backup `2026-05-04-pi-route-all-agents...` | ~3.76G | Medium | Archive/compress/offload first; do not delete blind because it contains agent session snapshots. |
| 3 | User/package caches: npm, pip, pnpm, node-gyp | ~1.0G | Low | Safe after no active installs/builds. Regenerable. |
| 4 | OpenClaw update/preupdate backups | ~1.1G | Medium-low after 24–48h stable | Keep newest 2026.5.4 update backup until plugin/version coherence is settled. Delete older preupdate backups later. |
| 5 | System journal/log retention | ~0.5–0.7G | Low-medium | Vacuum to bounded size after incident evidence is no longer needed. |
| 6 | Playwright browser cache | ~628M | Low if no E2E/browser jobs needed immediately | Regenerable, but deleting slows next browser test. |
| 7 | Agent `codex-home` / logs / sessions | ~2G+ possible | Medium-high | Do not delete first. Need retention policy; contains forensic/debug value. |
| 8 | QMD model cache | ~2.1G | High operational cost | Do not delete unless QMD reranker/query expansion intentionally disabled. Re-download expensive. |
| 9 | Ollama models | ~4.2G | High / product decision | Only if Piet confirms no local Ollama models needed. Not OpenClaw-update-related. |

---

## 3. Phase 1 — lowest-risk cleanup: Mission Control non-live `.next*`

### Evidence

Mission Control is started with:

```text
WorkingDirectory=/home/piet/.openclaw/workspace/mission-control
NEXT_DIST_DIR=.next
ExecStart=... next start -p 3000
```

Live `.next` exists and is ~469M. Non-live `.next*` candidates total ~4.94G. `/proc/<mission-control-pid>/fd` showed `count 0` open files under old `.next*` dirs at scan time.

Largest non-live candidates:

```text
456.7M .next-hermes-ab-both-rollback              BUILD_ID=false
456.7M .next-hermes-ab-diagnostics-rollback       BUILD_ID=false
456.7M .next-hermes-fullcopy-current              BUILD_ID=false
456.7M .next-hermes-cache-diagnostic              BUILD_ID=false
403.1M .next-hermes-precommit-verify-20260506T001338 BUILD_ID=true
403.1M .next-hermes-atlas-verify-20260506T000756     BUILD_ID=true
403.1M .next-hermes-final-verify                  BUILD_ID=true
397.8M .next-hermes-readonly-build                BUILD_ID=true
392.4M .next-mobile-hidden-audit                  BUILD_ID=true
386.6M .next-verify                               BUILD_ID=true
```

### Recommended action

**First pass:** remove non-live diagnostic `.next*` folders without `BUILD_ID`, plus old small proof/debug builds. Keep:

- `.next` — live runtime, never delete while Mission Control runs.
- One latest successful rollback/verified build for 24–48h, preferably `.next-hermes-precommit-verify-20260506T001338` or `.next-hermes-final-verify`.

### Expected reclaim

- Conservative: ~2.2G by removing obvious no-`BUILD_ID` diagnostic copies.
- Aggressive but still reasonable after keeping one known-good rollback: ~4.0G.

### Approval-gated command sketch

Dry-run first:

```bash
cd /home/piet/.openclaw/workspace/mission-control
python3 - <<'PY'
import os
keep={'.next','.next-hermes-precommit-verify-20260506T001338'}
for n in sorted(os.listdir('.')):
    if n.startswith('.next') and n not in keep:
        print(n)
PY
```

Actual delete only after explicit approval:

```bash
cd /home/piet/.openclaw/workspace/mission-control
rm -rf -- \
  .next-hermes-ab-both-rollback \
  .next-hermes-ab-diagnostics-rollback \
  .next-hermes-fullcopy-current \
  .next-hermes-cache-diagnostic \
  .next-hermes-final-verify \
  .next-hermes-atlas-verify-20260506T000756 \
  .next-hermes-readonly-build \
  .next-mobile-hidden-audit \
  .next-verify \
  .next-kpi-badges \
  .next-smoke \
  .next-actionable-blockers \
  .next-v3-tab-proof \
  .next-debug-taskboard \
  .next-ux-polish-dev \
  .next-v3-debug \
  .next-v3-proof \
  .next-ui-preview-smoke \
  .next-e2e \
  .next-hermes-fslog \
  .next-hermes-observability-build \
  .next-hermes-fsexact \
  .next-hermes-cpuprof \
  .next-hermes-fsfix* \
  .next-hermes-raw-diagnostic \
  .next-hermes-diagnose-live \
  .next.bak-hermes-20260503T192025Z
```

Post-check:

```bash
df -h /
curl -fsS --max-time 5 http://127.0.0.1:3000/api/health | jq '.status,.severity'
```

---

## 4. Phase 2 — low-risk regenerable caches

### Evidence

```text
632.7M /home/piet/.npm/_cacache
199.6M /home/piet/.cache/pip
120.9M /home/piet/.cache/pnpm
106.4M /home/piet/.cache/node-gyp
628.1M /home/piet/.cache/ms-playwright
278.1M /var/cache/apt
```

### Recommended action

After no active build/install is running:

- `npm cache clean --force` for user npm cache.
- `pip cache purge` for pip cache.
- `pnpm store prune` if pnpm is installed/used.
- Remove node-gyp cache if no native module build is in progress.
- `sudo apt clean` for apt package cache.
- Playwright cache only if browser/E2E jobs are not needed soon.

### Expected reclaim

- Without Playwright: ~1.0–1.2G.
- With Playwright: ~1.6–1.8G.

### Risk

Low: these caches are regenerated. Operational impact is slower next install/build/test.

---

## 5. Phase 3 — backups: high value but retention-gated

### Evidence

General backup root:

```text
3.76G /home/piet/backups/2026-05-04-pi-route-all-agents-20260504T184051Z
```

OpenClaw backups:

```text
498.0M /home/piet/.openclaw/backups/openclaw-update-2026-5-4-20260506T052705Z
326.7M /home/piet/.openclaw/backups/pre-update-2026.4.24
311.2M /home/piet/.openclaw/backups/openclaw-preupdate-20260429T210804Z
73.2M  /home/piet/.openclaw/backups/openclaw-update-20260430-195843
```

### Recommended action

1. Keep the newest `openclaw-update-2026-5-4...` backup until:
   - OpenClaw core/plugin versions are coherent, and
   - at least 24–48h stable runtime after update.
2. Compress/offload `/home/piet/backups/2026-05-04-pi-route-all-agents...` before deletion because it contains agent-session snapshots and duplicated QMD/Codex caches.
3. Older preupdate backups can be deleted after verifying they are superseded by newer backup points.

### Expected reclaim

- Delete/offload big pi-route backup: ~3.76G.
- Delete old OpenClaw preupdate backups except newest: ~0.7G.
- Keep newest update backup for now.

### Risk

Medium. Good reclaim, but backup deletion reduces rollback/forensics. Prefer compression/offhost copy first.

---

## 6. Phase 4 — logs and journals

### Evidence

```text
systemd journals: 523.1M
/var/log/journal: 584M
/var/log/syslog.1: 88.4M
/var/log/syslog: 21.6M
```

### Recommended action

Bound journal size rather than deleting individual logs:

```bash
sudo journalctl --vacuum-size=256M
```

Optionally after incident evidence is archived:

```bash
sudo logrotate -f /etc/logrotate.conf
```

### Expected reclaim

~250–400M.

### Risk

Low-medium. Reduces older incident evidence. Do only after today’s update audit/cleanup plan is preserved.

---

## 7. Do not touch in first cleanup pass

### QMD cache/models

Evidence:

```text
2.145G /home/piet/.cache/qmd/models
459M   /home/piet/.cache/qmd/index.sqlite
```

Do not delete. Models are active QMD capability/cost cache; index is current and updated 2026-05-06 08:15.

### Active OpenClaw/Mission Control runtime

Do not delete:

```text
/home/piet/.npm-global/lib/node_modules/openclaw
/home/piet/.openclaw/npm
/home/piet/.openclaw/workspace/mission-control/.next
/home/piet/.openclaw/openclaw.json
/home/piet/.openclaw/memory/*.sqlite
```

### Agent sessions/codex-home

Evidence:

```text
1.33G main agent/codex-home
299.6M main agent/codex-home/logs_2.sqlite
288.3M sre-expert sessions
231.6M sre-expert agent/codex-home
141.2M sre-expert logs_2.sqlite
134.6M main sessions
```

Do not delete manually in Phase 1. These need a retention policy and possibly OpenClaw-aware compaction/archive tooling.

### Ollama models

Evidence:

```text
4.17G /home/piet/.ollama/models
```

Large, but product decision. Only remove if Piet confirms local models are not needed.

---

## 8. Recommended execution order

### Step A — Safe reclaim, no service restart expected

1. Dry-run Mission Control `.next*` candidate list.
2. Delete only non-live `.next*` artefacts, keeping `.next` and one latest verified rollback build.
3. Run `df -h /`.
4. Check Mission Control `/api/health`.

Expected result: root frees ~2–4G and likely drops from 87% to roughly 83–85%.

### Step B — Cache cleanup

1. Confirm no build/install is active.
2. Clean npm/pip/pnpm/node-gyp/apt caches.
3. Optionally remove Playwright cache if no immediate browser testing.
4. Run `df -h /`.

Expected result: additional ~1–1.8G.

### Step C — Backup retention decision

1. Keep newest OpenClaw 2026.5.4 update backup until runtime/plugin coherence is stable.
2. Compress/offload big `/home/piet/backups/2026-05-04-pi-route-all-agents...`.
3. Delete superseded older preupdate backups only after offhost copy or explicit acceptance of rollback loss.

Expected result: additional ~0.7–4.5G depending on retention choice.

### Step D — Retention policy follow-up

Create a stable policy for:

- Mission Control `.next-hermes-*` build artefacts: keep live `.next` + newest one verified build + newest one rollback copy; expire older after 48h.
- OpenClaw backups: keep newest update backup + last known-good preupdate + offhost weekly archive.
- Agent sessions/codex logs: do not manual-delete; use OpenClaw-aware archive/compact if available.

---

## 9. My concise recommendation

**Best first move:** delete stale Mission Control `.next*` artefacts only, keeping live `.next` and one verified rollback build. This is the largest low-risk lever: ~2–4G reclaim without touching OpenClaw state, QMD, sessions, or active packages.

**Second:** clean regenerable caches for another ~1G.

**Third:** decide backup retention/offload for the 3.76G pi-route backup and older OpenClaw preupdate backups.

**Avoid for now:** QMD models/index, OpenClaw memory DBs, active package roots, agent sessions/codex-home, Ollama models unless explicitly intended.
