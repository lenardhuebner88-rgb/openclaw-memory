---
title: Minions Migration-Plan — PR #68718 Adoption
date: 2026-04-19 13:30 UTC
author: Operator (pieter_pan) direkt
scope: Durable SQLite Job-Queue Adoption (replaces R30/R37/R39/R40 fragile paths)
status: watch-mode (PR still open)
source: https://github.com/openclaw/openclaw/pull/68718
---

# Minions Migration-Plan

## Executive Summary

PR [#68718](https://github.com/openclaw/openclaw/pull/68718) "minions: durable SQLite-backed job queue" ist der strukturelle Fix fuer 4 von 6 Incident-Klassen die wir heute muehsam mit Punkt-Fixes mitigiert haben. Sobald gemergt → migrations-plan ausfuehren.

### Aktueller Status (2026-04-19 13:30 UTC)
- State: **open**, mergeable_state: **clean**, draft: **false**
- 11 commits, 49 files, +5840/-187 LOC, Size XL
- Head: `b45d69976d32`
- Updated: heute 11:15 UTC
- Auto-watch via `/home/piet/.openclaw/scripts/minions-pr-watch.sh` hourly Cron → Discord-Alert bei merge/commit/close

## Was minions liefert vs. unsere aktuellen Fixes

| Unser aktueller Fix (heute deployed) | Minions-Ersatz | Was gespart wird |
|---|---|---|
| **R38** `mcp-taskboard-reaper.sh` Cron + Discord-Alert | minions lifecycle-supervised, parent-death = cascade-cancel | Cron + external zombie-counter |
| **R37** `auto-pickup.py` Wake-vs-Task IPC-Markers | minions state-machine (9 states explicit) | Heartbeat-Classifier-Guessing |
| **R39** `atlas-orphan-detect.sh` Cron (Alert-only) | minions crash-recovery via stall re-queue (sub-second) | Cron + manuelles Resume |
| **R40** `STALL_WARN=2min/HARD=5min` Thresholds | minions lock-heartbeat sub-second stall-detection | 2-5min Latency bis Auto-Fail |
| **Pack-4** dispatchToken idempotency | minions idempotency via partial unique index | Manueller Token-Management |
| **PR #68846 cherry-pick** + `pr68846-patch-check.sh` | minions subsystem sauberer (nicht direct mcp child) | Patch-fragility gegen npm-update |

### Was NICHT abgelöst wird
- **R30 Root-Cause (MCP-Child-Cleanup)**: bleibt relevant — minions track subagent jobs, aber MCP-Taskboard-Server sind eigene Prozesse. PR #68846 bleibt notwendig.
- **R35 Atlas-Self-Report ≠ Board-Truth**: minions loesst keine prompt-engineering.
- **R36 Session-Size-Creep**: minions nicht im Scope.
- **R41 QMD vor File-Read**: memory-architecture-fix, unabhaengig von minions.

## Migrations-Schritte (wenn merged)

### Phase 1 — Audit (5 min)
```sh
# 1. Check current version
/home/piet/.openclaw/bin/openclaw --version

# 2. Check package.json lock-state
cat /home/piet/.npm-global/lib/node_modules/openclaw/package.json | python3 -c "import json,sys; print(json.load(sys.stdin).get('version'))"

# 3. Check our custom patches before update
ls /home/piet/.openclaw/patches/
ls /home/piet/.npm-global/lib/node_modules/openclaw/dist/*.bak-2026-04-19* 2>/dev/null
```

### Phase 2 — Safe npm-update mit Rollback (15 min)
```sh
# 1. Stop all crons that would run during update
systemctl --user stop openclaw-gateway mission-control
sleep 5

# 2. Backup current install
tar czf /home/piet/.openclaw/backups/openclaw-pre-minions-$(date +%Y%m%d).tar.gz \
    /home/piet/.npm-global/lib/node_modules/openclaw/dist

# 3. Update
npm install -g openclaw@latest

# 4. Check if PR #68846 is superseded
grep -q 'cleanupBundleMcpOnRunEnd || params.spawnedBy' \
    /home/piet/.npm-global/lib/node_modules/openclaw/dist/attempt-execution.runtime-*.js \
    && echo "PR #68846 still needed" || echo "PR #68846 merged or path changed"

# 5. Re-apply PR #68846 patch if still needed (or verify it's in upstream)
# If patch-check-cron already reapplied, skip. If not:
# Edit attempt-execution.runtime-*.js line 371:
# cleanupBundleMcpOnRunEnd: params.opts.cleanupBundleMcpOnRunEnd || params.spawnedBy != null

# 6. Restart
systemctl --user start openclaw-gateway
sleep 15
systemctl --user start mission-control
sleep 30
curl -sS -o /dev/null -w 'gw=%{http_code} mc=%{http_code}\n' http://localhost:18789/healthz http://localhost:3000/api/health
```

### Phase 3 — Shadow-Write Mode (24h Validierung)
```json
// openclaw.json — start in legacy (default behavior but minion_jobs gets populated)
{
  "minions": {
    "durability": "shadow"
  }
}
```

Dieser Mode schreibt in die minion_jobs-Table, aber wirkt nicht. Wir koennen 24h beobachten:
- Populiert sich die Table?
- Stimmen die States mit unserer tasks.json ueberein?
- Keine Double-Writes / Konflikte?

### Phase 4 — Flip Durability-On (nach 24h shadow-ok)
```json
{
  "minions": {
    "durability": "active"
  }
}
```

Jetzt minions supervised den spawn-lifecycle. Crash-Recovery, Idempotency, Stall-Detection auf minions.

### Phase 5 — Deprecate aktuelle Cron-Fixes (nach 72h durability-stable)
```sh
# Remove now-redundant cron entries (keep scripts as archival)
crontab -l | grep -v 'atlas-orphan-detect\|mcp-taskboard-reaper\|pr68846-patch-check' | crontab -

# Update worker-monitor.py to skip stall-detect (minions does it sub-second)
# Or: retain as defense-in-depth (no harm, just redundant)
```

### Phase 6 — Retire Rules R38/R39/R40
```sh
# In memory/rules.jsonl: mark deprecated + supersededBy
python3 - << 'EOF'
import json
path = '/home/piet/.openclaw/workspace/memory/rules.jsonl'
rules = []
with open(path) as f:
    for line in f:
        r = json.loads(line)
        if r['id'] in ('R38','R39','R40'):
            r['status'] = 'superseded'
            r['supersededBy'] = 'minions-subsystem PR #68718'
            r['deprecated_at'] = '2026-04-XX'  # fill in
        rules.append(r)
with open(path, 'w') as f:
    for r in rules:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
EOF

# Re-render
/home/piet/.openclaw/scripts/rules-render.sh
```

## Rollback-Strategie

Bei jedem Schritt ist Rollback moeglich:
- **Phase 2**: Backup-Tarball wiederherstellen + `systemctl restart openclaw-gateway`
- **Phase 3-4**: Flag zurueck auf `legacy` / entfernen
- **Phase 5-6**: Cron-Eintraege re-add aus Backup, Regeln un-deprecate in JSONL

## Risiken

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| npm update bricht andere Funktionalitaet | mittel | hoch | Backup-Tarball, Test-Suite run |
| PR #68846 ist in upstream aber inaktiv | niedrig | mittel | Patch-Check-Cron detected drift, reapplied |
| minions.durability shadow zeigt Inkonsistenzen | mittel | niedrig | 24h observation fenster, dann entscheiden |
| minions verbraucht mehr Disk (SQLite growth) | niedrig | niedrig | maintenance-cron `minion_jobs cleanup` (should be included) |

## Watch-Automation Status

- **Script:** `/home/piet/.openclaw/scripts/minions-pr-watch.sh`
- **Cron:** `23 * * * *` (hourly at :23)
- **State-file:** `/home/piet/.openclaw/workspace/logs/minions-pr-watch.state.json`
- **Log:** `/home/piet/.openclaw/workspace/logs/minions-pr-watch.log`
- **Discord-Alert:** via `$AUTO_PICKUP_WEBHOOK_URL`
- **Triggers:**
  - **MERGED:** Full alert + migration-plan pointer
  - **NEW COMMITS:** Alert with SHA diff
  - **CLOSED without merge:** Alert "check for successor PR"

## Pre-Merge Tracking Points

Diese Issues verweisen auf die Problem-Domain; bei Referenzen in PR-Comments relevant:
- [#68451](https://github.com/openclaw/openclaw/issues/68451) RFC Process Registry (PR-Motivation)
- [#68406](https://github.com/openclaw/openclaw/issues/68406) 191 orphaned MCPs with PPID=1
- [#62026](https://github.com/openclaw/openclaw/issues/62026) uvx minimax leak 6GB
- [#61610](https://github.com/openclaw/openclaw/issues/61610) tasks cancel + stuck-running prune
- [#39305](https://github.com/openclaw/openclaw/issues/39305) Escalating stall recovery
- [#35802](https://github.com/openclaw/openclaw/issues/35802) No centralized agent registry

## Decision-Tree bei Merge

```
minions merged
├── Our custom cron-stack still works? (atlas-orphan, reaper, patch-check)
│   ├── YES → shadow-mode 24h, then flip durability=active
│   └── NO (conflicts) → shadow-mode only, keep custom crons, investigate
│
├── PR #68846 still needed?
│   ├── YES (not in upstream) → maintain cherry-pick
│   └── NO (upstream includes fix) → patch-check-cron auto-detects + logs
│
└── Session-Rotation config compatible?
    ├── YES → proceed
    └── NO → adjust safeguard params
```

## Signed-off

Operator (pieter_pan) 2026-04-19 13:30 UTC. Watch-cron aktiv, Migration-Plan dokumentiert, trigger on merge detected.
