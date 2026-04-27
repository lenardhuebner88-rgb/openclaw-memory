---
name: Sprint-MC-T03 Alert Quality + Suppress-vor-Persist
description: Atlas-autonomous Alert-Fatigue Bekämpfung - 9624 Alerts/7d eindämmen, Severity-Hierarchy, Acknowledge/Mute, Suppress vor Persist statt nach Display.
status: planned
since: 2026-04-27
owner: Operator (pieter_pan)
trigger_phrase: "Atlas Sprint MC-T03 Alerts starten"
related:
  - vault/04-Sprints/planned/2026-04-27_mc-ui-audit-claude-design-prep.md
  - vault/04-Sprints/planned/s-mc-alerts-dashboard-audit-2026-04-23.md
autonomy_mode: full
operator_gates: none
---

# Sprint-MC-T03 — Alert Quality + Suppress (Atlas-autonom)

**Context:** Audit hat 9624 Alerts in 7d gefunden, davon 5404 (=56%) sind `cost · flatrate-rate-spike SUPPRESS reason=rate_limit`. Diese werden GEPOSTET und DANN suppressed — d.h. der Alert-Feed wird mit Spam geflutet während CRITICAL-Alerts (z.B. canary-session-rotation-watchdog status=CRITICAL) in derselben Liste untergehen. Dazu fehlen Acknowledge/Mute-Aktionen pro Alert.

**Trigger:** `Atlas Sprint MC-T03 Alerts starten`

**Atlas-Mandate:**
- Volle autonome Steuerung — keine Operator-Approval-Gates
- Atlas verifiziert Drop-Rate (5404 → ≤100 erwartet) per DoD vor Receipt=result
- Atlas postet Sprint-Done-Report in `sre-expert` (1486480146524410028) wenn alle 4 Subs done

---

## Scope-Matrix

| Sub | Title | Owner | Estimate | DoD |
|---|---|---|---|---|
| **A1** | Suppress-vor-Persist (Backend) | Forge | 2-2.5h | Neue rate_limit-suppress Alerts werden NICHT mehr in Feed-Storage geschrieben, nur in counter.log |
| **A2** | Backfill-Cleanup historische Suppress-Spam | Forge | 1-1.5h | /alerts Feed-Count drops von ~9624 auf ≤4500 (5400 weg) |
| **A3** | Severity-Hierarchy + Group-Collapse UI | Pixel | 2-2.5h | /alerts zeigt 4 Severity-Tabs (critical/error/warn/info) + collapsible-groups by source+kind |
| **A4** | Acknowledge + Mute pro Alert + per Group | Forge + Pixel | 1.5-2h | Jede Alert-Card hat Ack-Button + Mute-Button, persistiert in DB |

**Total Estimate:** 6-7h

---

## A1 — Suppress-vor-Persist (Backend)

### Problem
- `cost-alert-dispatcher.log` schreibt Alert-Records mit `suppress: rate_limit` IN den Feed-Storage
- UI zeigt diese im Alerts-Feed als "alert (suppress=rate_limit)"
- Result: 5404 Spam-Einträge in 7d

### Atlas-Heuristic
1. Forge identifiziert Dispatcher: `find /home/piet/.openclaw -name "cost-alert-dispatcher*" -o -name "alert-dispatcher*"` 
2. Forge versteht Persist-Path: vermutlich Python script writes to `workspace/memory/alerts/<date>.jsonl` oder ähnlich

### Fix-Steps für Forge
1. Im Dispatcher-Code: pre-persist-check
```python
if suppress_reason == 'rate_limit':
    counter_log_only(alert)  # bumps counter, no feed-write
    return
persist_to_feed(alert)
```
2. Counter-Log-File: `workspace/memory/alerts/_counters.jsonl` mit `{ts, kind, count, source}` für Visibility ohne Feed-Spam
3. Alle anderen Suppress-Reasons (z.B. `duplicate`, `rate_limit_v2`, etc) gleich behandeln — Atlas-Heuristic: `if suppress_reason and suppress_reason != 'manual_review'` → counter-only

### Verify
- Forge wartet 5 Minuten nach Deploy
- `tail -100 /home/piet/.openclaw/workspace/memory/alerts/<today>.jsonl | grep -c "suppress.*rate_limit"` → Expected: 0
- `cat /home/piet/.openclaw/workspace/memory/alerts/_counters.jsonl | wc -l` → Expected: ≥1 (counter funktioniert)
- /alerts Feed-Count darf NICHT wachsen mit rate_limit-Einträgen während des 5-min-Windows

---

## A2 — Backfill-Cleanup

### Problem
Existing 5404 historische rate_limit-suppress Alerts müllen den Feed jetzt weiter zu, auch nachdem A1 deployed ist.

### Atlas-Heuristic
- **Decision:** Nicht hard-deleten, sondern in Archive-Folder verschieben. Audit-Trail bleibt, Feed wird sauber.

### Fix-Steps für Forge
1. Backup-First:
```sh
cp -r /home/piet/.openclaw/workspace/memory/alerts /home/piet/.openclaw/workspace/memory/alerts.bak-pre-cleanup-2026-04-27
```
2. Migration-Script `workspace/scripts/alert-backfill-cleanup.py`:
```python
import json
from pathlib import Path
SRC = Path('/home/piet/.openclaw/workspace/memory/alerts')
ARCHIVE = SRC / '_archived_suppress'
ARCHIVE.mkdir(exist_ok=True)
moved = 0
for jsonl in SRC.glob('*.jsonl'):
    if jsonl.name.startswith('_'): continue
    keep, archive = [], []
    with jsonl.open() as f:
        for line in f:
            try:
                rec = json.loads(line)
                if rec.get('suppress_reason') == 'rate_limit':
                    archive.append(line); moved += 1
                else:
                    keep.append(line)
            except: keep.append(line)
    if archive:
        (ARCHIVE / jsonl.name).write_text(''.join(archive))
        jsonl.write_text(''.join(keep))
print(f'Moved {moved} suppress-records to {ARCHIVE}')
```
3. Run + verify count
4. /api/alerts Endpoint: keine Code-Änderung nötig (filter geht über filesystem)

### Verify
```sh
ssh homeserver "wc -l /home/piet/.openclaw/workspace/memory/alerts/*.jsonl 2>/dev/null | tail -1"
# Expected: ~4200 statt vorher 9624
ssh homeserver "wc -l /home/piet/.openclaw/workspace/memory/alerts/_archived_suppress/*.jsonl 2>/dev/null | tail -1"  
# Expected: ~5400
curl -s http://localhost:3000/api/alerts | jq '.total'
# Expected: drops to ~4200
```

---

## A3 — Severity-Hierarchy + Group-Collapse UI

### Problem
- /alerts zeigt alle Alerts in einer flachen Liste
- CRITICAL `system · canary-session-rotation-watchdog` steht visuell gleichwertig neben suppressed cost-spike
- Keine Group-Collapse für gleichartige Alerts

### Fix-Steps für Pixel

1. /alerts Page-Component erweitern:
```tsx
// Severity-Tabs (oberhalb der Filter-Pills)
<SeverityTabs value={severity} onChange={setSeverity}>
  <Tab value="critical" count={counts.critical} color="red" />
  <Tab value="error" count={counts.error} color="orange" />
  <Tab value="warn" count={counts.warn} color="yellow" />
  <Tab value="info" count={counts.info} color="blue" />
  <Tab value="all" count={counts.total} />
</SeverityTabs>
```

2. Severity-Mapping vom Backend (Forge stellt sicher):
- Alle alerts mit `kind === 'system' && status === 'CRITICAL'` → severity=critical
- Alle alerts mit `kind === 'mcp-zombie' || kind === 'patch-drift'` → severity=warn
- Alle alerts mit `kind === 'cost' && !suppress_reason` → severity=info
- (weitere Mappings nach Bedarf — Forge dokumentiert die Liste)

3. Group-Collapse-Logic:
- Gruppiere by `kind + source`
- Wenn ≥3 alerts mit gleichem `kind+source` in 1h → collapse zu 1 group-card mit "X mal in 1h"
- Click → expand zu individual entries

4. Color-Tokens (Tailwind):
- critical: `border-red-500/50 bg-red-950/40`
- error: `border-orange-500/40 bg-orange-950/30`  
- warn: `border-yellow-600/40 bg-yellow-950/30`
- info: `border-blue-500/30 bg-blue-950/20`

### Verify
- /alerts: 4 Tabs sichtbar mit Counts
- Click "critical" → nur 1-2 Entries (canary-session-rotation-watchdog, etc)
- Click "info" → cost-alerts noch sichtbar (post A1+A2 viel weniger)
- Group-Collapse: jede gruppe ≥3 ist 1 Card mit count badge

---

## A4 — Acknowledge + Mute pro Alert + Group

### Problem
- Operator hat keine Möglichkeit "habe gesehen" zu markieren
- Keine "mute for 1h"-Action für Repeating-Source

### Fix-Steps für Forge (Backend) + Pixel (UI)

**Forge — Endpoints:**
1. `POST /api/alerts/:id/ack` body: `{ack_by, note?}` → markiert alert als `acknowledged_at`, `acknowledged_by`
2. `POST /api/alerts/:id/mute` body: `{duration_min}` → markiert source+kind als gemuted bis `now + duration_min`. Backend dispatcher checkt mute-list before persist.
3. `POST /api/alerts/groups/mute` body: `{source, kind, duration_min}` → mutet ganze Gruppe
4. Storage: `workspace/memory/alerts/_mutes.jsonl` (append-only mit expiry-check)

**Pixel — UI:**
1. Pro Alert-Card: `[Ack]` + `[Mute 1h]` Dropdown (Optionen: 1h / 4h / 24h)
2. Gemutete Cards: opacity-40 + small "muted until HH:MM" Badge
3. Group-Card: `[Mute Group 4h]` Action

**Atlas-Heuristic für Mute-Cleanup:**
- Forge fügt Cron `0 * * * *` hinzu der `_mutes.jsonl` rotated (expired entries removen)

### Verify
- /alerts Critical-Tab: pick erste critical alert → click [Ack] → Card bekommt grünen "✓ acknowledged"-Badge
- Pick warn-Group → click [Mute Group 4h] → Group verschwindet aus Active-Tab, erscheint in "Muted"-Tab (neuer 5. Tab) für 4h
- 4h+1m später (oder via test-time-mock): Group erscheint wieder

---

## Cross-Sprint Receipts + Final-Step

Receipts laut R45/R50.

**Atlas-Sprint-Final-Step:**
1. Alle 4 Subs done → Atlas postet Discord-Report in `sre-expert`:
   - A1 Backend deployed: `<commit-sha>`
   - A2 Backfill: X records archived, Y remaining
   - A3 UI: 4 severity tabs + group-collapse live
   - A4 Endpoints: /ack /mute deployed, UI verdrahtet
2. Atlas renamed Plan-Doc nach `vault/04-Sprints/done/`

---

## Notes für Atlas

- A1 + A3 + A4 können parallel: A1+A4 Backend (Forge serialisiert), A3 Frontend (Pixel)
- A2 (Backfill) MUSS nach A1 laufen sonst werden während Backfill neue Spam-Records angelegt
- Risiko-Note: Wenn A1-Patch versehentlich legitime Alerts droppt — A1 hat Backup im counter-log via `_counters.jsonl`. Forge muss das nach 1h Soak-Test verifizieren.
