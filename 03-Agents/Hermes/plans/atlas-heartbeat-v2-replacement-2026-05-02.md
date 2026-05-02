# Atlas-Control-Heartbeat-v2 Replacement Plan

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** Ein sicherer Atlas-Master-Heartbeat-Cron, der als reines Shell/Systemd-Job läuft (keine Agent-Session), read-only MC-API liest, nur bei echtem State-Drift alertet, und die Atlas/Gateway-Session nicht saturatiert.

**Architektur:**
- Neues Shell-Script `atlas-state-watchdog.sh` — read-only MC-API + bounded receipt touch
- Systemd-Timer (10min interval) — kein OpenClaw-Agent-Session-Overhead
- Pattern: `ATLAS_WATCHDOG_OK touched=N` / `ATLAS_WATCHDOG_ERROR ...`
- Alert nur bei echtem State-Drift (stale >30min, state-machine violations)

**Tech Stack:** bash, curl, jq, systemd user timer

---

## Task 1: Read-only Analyse — Bestehende Scripts inspizieren

**Objective:** Bestehende heartbeat/watchdog Scripts vollständig verstehen als Baseline.

**Files:**
- Inspect: `/home/piet/.openclaw/scripts/m7-atlas-master-heartbeat.sh`
- Inspect: `/home/piet/.openclaw/scripts/mcp-zombie-killer.sh`
- Inspect: `/home/piet/.openclaw/scripts/openclaw-systemjob-runner.py`

**Step 1: Lies m7-atlas-master-heartbeat.sh**

```
cat /home/piet/.openclaw/scripts/m7-atlas-master-heartbeat.sh
```

Erwartet: 43 Zeilen, MC-API GET /tasks + jq filter + bounded POST /receipt, M7_HEARTBEAT_OK pattern.

**Step 2: Lies mcp-zombie-killer.sh**

```
cat /home/piet/.openclaw/scripts/mcp-zombie-killer.sh
```

Erwartet: Python-inline, ps-based process killing, MCP_ZOMBIE_KILLER_OK/WARN pattern.

**Step 3: Lies openclaw-systemjob-runner.py (relevant für Timer-Integration)**

```
cat /home/piet/.openclaw/scripts/openclaw-systemjob-runner.py
```

Erwartet: Systemd timer/unit management, successPattern/failurePattern matching.

---

## Task 2: Neues Script atlas-state-watchdog.sh entwerfen

**Objective:** Ein read-only Atlas-Watchdog-Script, das nur MC-API liest und bei State-Drift alertet — kein eigenes POST ausser bounded receipt touch.

**Files:**
- Create: `/home/piet/.openclaw/scripts/atlas-state-watchdog.sh`

**Step 1: Erstelle das Script**

```bash
#!/usr/bin/env bash
set -euo pipefail

# Atlas State Watchdog v2 — read-only board hygiene check
# Only alerts on real state drift; no agent session overhead.
# Runs as systemd user timer (isolated from OpenClaw agent sessions).

API_BASE="${MC_API_BASE:-http://127.0.0.1:3000/api}"
STALE_THRESHOLD_MINUTES="${STALE_THRESHOLD_MINUTES:-30}"
DRY_RUN="${DRY_RUN:-0}"

# ── Read-only board scan ──────────────────────────────────────────
json="$(curl -fsS "$API_BASE/tasks?limit=400" || { echo "ATLAS_WATCHDOG_ERROR curl_failed"; exit 1; })"

# Filter: Atlas Master tasks in non-terminal states
candidates="$(jq -c '
  [.tasks[]
   | select(.status | test("assigned|in-progress|pending-pickup"; "i"))
   | select(.title   | test("Atlas|master"; "i"))
  ]' <<<"$json")"

count="$(jq 'length' <<<"$candidates")"

# ── Anomaly detection ────────────────────────────────────────────
# Check 1: stale in-progress (no receipt update > threshold)
stale_in_progress="$(jq -c '
  [.[]
   | select(.status == "in-progress")
   | select((.updatedAt // 0 | tonumber) < (now | floor - ('"$STALE_THRESHOLD_MINUTES"' * 60)))
  ]' <<<"$candidates")"

stale_count="$(jq 'length' <<<"$stale_in_progress")"

# Check 2: orphaned pending-pickup (assigned long ago, never picked up)
orphaned_pickup="$(jq -c '
  [.[]
   | select(.status == "pending-pickup")
   | select((.updatedAt // 0 | tonumber) < (now | floor - ('"$STALE_THRESHOLD_MINUTES"' * 60)))
  ]' <<<"$candidates")"

orphaned_count="$(jq 'length' <<<"$orphaned_pickup")"

# ── Alert on real drift only ──────────────────────────────────────
if [[ "$stale_count" -gt 0 ]] || [[ "$orphaned_count" -gt 0 ]]; then
  echo "ATLAS_WATCHDOG_ALERT stale_in_progress=$stale_count orphaned_pending_pickup=$orphaned_count"
  # Log detail for operator review
  if [[ "$DRY_RUN" == "1" ]]; then
    echo "DRY: would alert for:"
    jq -c '.[] | {id, status, title}' <<<"$stale_in_progress" 2>/dev/null || true
    jq -c '.[] | {id, status, title}' <<<"$orphaned_pickup" 2>/dev/null || true
  fi
  exit 1
fi

# ── Bounded receipt touch (kein eigener Write ausser dieses) ─────
touched=0
while IFS= read -r task; do
  task_id="$(jq -r '.id' <<<"$task")"
  dispatch_token="$(jq -r '.dispatchToken // empty' <<<"$task")"

  # Only touch receipt for tasks that exist and are still active
  if [[ "$dispatch_token" != "" ]]; then
    payload="$(jq -n \
      --arg stage "progress" \
      --arg ws "cron:atlas-state-watchdog" \
      --arg wl "atlas-state-watchdog" \
      --arg rs "heartbeat-timer" \
      --arg dt "$dispatch_token" \
      '{stage:$stage,workerSessionId:$ws,workerLabel:$wl,resultSummary:$rs,actor_kind:"system",request_class:"system"} + {dispatchToken:$dt}')"

    curl -fsS -X POST "$API_BASE/tasks/$task_id/receipt" \
      -H 'Content-Type: application/json' \
      -d "$payload" >/dev/null 2>&1 || true
    touched=$((touched + 1))
  fi
done < <(jq -c '.[]' <<<"$candidates")

echo "ATLAS_WATCHDOG_OK candidates=$count touched=$touched"
exit 0
```

**Step 2: Mache es ausführbar**

```bash
chmod +x /home/piet/.openclaw/scripts/atlas-state-watchdog.sh
```

**Step 3: Dry-run Test**

```bash
DRY_RUN=1 /home/piet/.openclaw/scripts/atlas-state-watchdog.sh
```

Erwartet: `ATLAS_WATCHDOG_OK candidates=N touched=N` oder `ATLAS_WATCHDOG_ALERT` wenn Anomalien.

---

## Task 3: Systemd Timer Unit erstellen

**Objective:** Systemd user timer + service unit für das neue Script, analog zu mcp-zombie-killer/systemJob pattern.

**Files:**
- Create: `/home/piet/.config/systemd/user/openclaw-systemjob-atlas-state-watchdog.timer`
- Create: `/home/piet/.config/systemd/user/openclaw-systemjob-atlas-state-watchdog.service`

**Step 1: Erstelle Timer Unit**

```ini
[Unit]
Description=Atlas State Watchdog timer (10min interval)
PartOf=openclaw-systemjob-atlas-state-watchdog.service

[Timer]
OnCalendar=*:0/10
Persistent=true
Unit=openclaw-systemjob-atlas-state-watchdog.service

[Install]
WantedBy=timers.target
```

**Step 2: Erstelle Service Unit**

```ini
[Unit]
Description=Atlas State Watchdog — read-only MC-API board hygiene check
After=network.target

[Service]
Type=oneshot
WorkingDirectory=/home/piet
ExecStart=/home/piet/.openclaw/scripts/atlas-state-watchdog.sh
TimeoutSec=45
Environment="MC_API_BASE=http://127.0.0.1:3000/api"
Environment="STALE_THRESHOLD_MINUTES=30"

# Pattern matching for openclaw-systemjob-runner compatibility
SuccessExitStatus=0 1

[Install]
WantedBy=default.target
```

**Step 3: systemd daemon-reload**

```bash
systemctl --user daemon-reload
```

**Step 4: Timer aktivieren und starten**

```bash
systemctl --user enable --now openclaw-systemjob-atlas-state-watchdog.timer
```

**Step 5: Verify**

```bash
systemctl --user list-timers | grep atlas-state-watchdog
```

Erwartet: Timer aktiv, nächste Ausführung in <10min.

---

## Task 4: jobs.json SystemJob-Config hinzufügen

**Objective:** OpenClaw jobs.json um den SystemJob-Eintrag ergänzen (für Konsistenz mit anderen migrated Jobs).

**Files:**
- Modify: `/home/piet/.openclaw/cron/jobs.json`

**Step 1: Backup erstellen**

```bash
cp /home/piet/.openclaw/cron/jobs.json /home/piet/.openclaw/cron/jobs.json.bak.$(date +%Y%m%d%H%M%S)
```

**Step 2: Neuen Job-Eintrag nach dem atlas-control-heartbeat-v1 Eintrag einfügen (innerhalb des jobs Arrays)**

Der neue Job-Eintrag (nach Zeile 605 in jobs.json):

```json
    {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "agentId": "sre-expert",
      "sessionKey": "agent:sre-expert:main",
      "name": "atlas-state-watchdog-10min",
      "description": "Read-only Atlas board hygiene watchdog via systemd systemJob. Alerts only on real state drift (stale in-progress >30min, orphaned pending-pickup). Replaces disabled atlas-control-heartbeat-v1.",
      "enabled": false,
      "createdAtMs": 1746234000000,
      "schedule": {
        "kind": "cron",
        "expr": "*/10 * * * *",
        "tz": "Europe/Berlin"
      },
      "sessionTarget": "isolated",
      "wakeMode": "now",
      "payload": {
        "kind": "agentTurn",
        "message": "RUN: /home/piet/.openclaw/scripts/atlas-state-watchdog.sh\nIf output starts with ATLAS_WATCHDOG_OK, reply exactly NO_REPLY.\nIf output starts with ATLAS_WATCHDOG_ALERT, reply with first 5 lines of output.\nIf command fails, reply with first 5 lines of error.\nSTOP.",
        "timeoutSeconds": 120,
        "model": "openai-codex/gpt-5.4-mini"
      },
      "delivery": {
        "mode": "none"
      },
      "failureAlert": {
        "after": 1,
        "mode": "announce",
        "channel": "discord",
        "to": "1491148986109661334",
        "cooldownMs": 600000
      },
      "disabledReason": "migrated-to-systemd-systemjob",
      "systemJob": {
        "enabled": true,
        "cwd": "/home/piet",
        "unit": "openclaw-systemjob-atlas-state-watchdog.timer",
        "command": [
          "/home/piet/.openclaw/scripts/atlas-state-watchdog.sh"
        ],
        "timeoutSeconds": 45,
        "successPattern": "^ATLAS_WATCHDOG_OK",
        "failurePattern": "ATLAS_WATCHDOG_(ERROR|ALERT)|ERROR|FAILED",
        "summaryMaxLines": 10,
        "migratedFrom": "agentTurn",
        "migratedAt": "2026-05-02T23:00:00Z",
        "runner": "/home/piet/.openclaw/scripts/openclaw-systemjob-runner.py"
      },
      "dailyTokenBudget": 1000000,
      "state": {}
    }
```

**Step 3: Diff zur Backup-Datei prüfen**

```bash
diff /home/piet/.openclaw/cron/jobs.json.bak.* /home/piet/.openclaw/cron/jobs.json | head -50
```

Erwartet: Nur der neue Job-Eintrag wurde hinzugefügt.

---

## Task 5: Inline-Test des Watchdog Scripts

**Objective:** Script im Live-Betrieb testen (read-only, keine Alerts bei sauberem Board).

**Step 1: Script trocken laufen lassen**

```bash
/home/piet/.openclaw/scripts/atlas-state-watchdog.sh
```

Erwartet (Board clean): `ATLAS_WATCHDOG_OK candidates=N touched=N` → Exit 0

**Step 2: Mit erzwungenem Alert-Test (DRY_RUN + manipulierte STALE_THRESHOLD_MINUTES)**

```bash
STALE_THRESHOLD_MINUTES=0 DRY_RUN=1 /home/piet/.openclaw/scripts/atlas-state-watchdog.sh
```

Erwartet: `ATLAS_WATCHDOG_ALERT stale_in_progress=N orphaned_pending_pickup=N` → Exit 1

---

## Task 6: Playbook-Dokumentation schreiben

**Objective:** Laufende Dokumentation für den Betrieb.

**Files:**
- Create: `/home/piet/vault/03-Agents/Hermes/playbooks/atlas-state-watchdog-v2.md`

**Content:**
```markdown
# Atlas State Watchdog v2 Playbook

## Was es macht
- Read-only MC-API Board-Scan aller Atlas/Master-Tasks
- Alert bei: stale in-progress (>30min ohne receipt), orphaned pending-pickup
- Bounded receipt POST nur für aktive Tasks (kein Write bei sauberem Board)
- Läuft als systemd user timer (10min), keine OpenClaw-Agent-Session

## Warum替代 atlas-control-heartbeat-v1
- atlas-control-heartbeat-v1 nutzte `systemEvent` payload + `main` session → Gateway/Atlas saturation
- Neues Design: Shell-only, kein Agent-Overhead, nur bei echtem Drift

## Troubleshooting
- Script direkt: `/home/piet/.openclaw/scripts/atlas-state-watchdog.sh`
- Timer status: `systemctl --user list-timers | grep atlas-state-watchdog`
- Letzter Lauf: `journalctl --user -u openclaw-systemjob-atlas-state-watchdog.service -n 20`
- Dry-run: `DRY_RUN=1 /home/piet/.openclaw/scripts/atlas-state-watchdog.sh`
```

---

## Verification Checklist

- [ ] Script ausführbar und trocken lauffähig
- [ ] Systemd timer aktiv und next-run sichtbar
- [ ] jobs.json backup existiert
- [ ] jobs.json neuer SystemJob-Eintrag korrekt eingefügt
- [ ] Playbook-Dokumentation erstellt
- [ ] Keine Agent-Session wird für heartbeat-Ausführung geöffnet
- [ ] Alert-Cooldown (10min) verhindert Alert-Flutung
