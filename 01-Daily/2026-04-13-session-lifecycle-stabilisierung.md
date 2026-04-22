# Session-Log: Lifecycle-Stabilisierung & Worker-Monitor v5

> Datum: 2026-04-13 | Dauer: ~6h | Operator: Lenard + Claude Code

---

## Ausgangssituation

- 20 Tasks gleichzeitig auf "in-progress" nach Atlas-Massenstart
- Swap 100% voll (4 GB / 4 GB), 254+ MCP-Prozesse
- Worker-Monitor ohne Concurrency-Limits
- Lifecycle-State-Machine nicht vollständig dokumentiert
- Agent-Vault-Dateien veraltet oder leer

---

## Was gemacht wurde

### 1. Lifecycle-Analyse & Dokumentation

- `task-lifecycle-canon.md` erstellt: vollständige Referenz für die 4-dimensionale State-Machine
  (`status × dispatched × dispatchState × executionState`)
- Alle kanonischen Zustandskombinationen, illegale Transitionen, Atlas-Dispatch-Protokoll
- Alle 7 Agent-Vault-Dateien aktualisiert (Atlas, Forge, Pixel, Lens, James, Sre Expert, Frontend Guru)

### 2. Mission Control Fixes

- **`canceled`-Status-Normalisierung** in `taskboard-store.ts` — canceled ließ `dispatchState`/`executionState` undefiniert → `normalizeTaskRecord()` ergänzt
- **`/api/agents/concurrency`** — neuer Endpoint: zeigt pro Agent `inProgress`, `limit`, `available`, `canDispatch`

### 3. Worker-Monitor v5 (15+ Fixes)

| Fix | Beschreibung |
|-----|-------------|
| `validate_gateway_token()` | GW-Token-Prüfung beim Start, Discord-Alert bei fehlendem/ungültigem Token |
| `gw_probe()` | Liveness-Check vor jedem Gateway-Spawn |
| `gw_chat()` capacity-check | `/agents/{id}/status` → abbruch bei busy |
| Per-Agent-Concurrency | `_spawn_specialist()` Guard: Forge=3, Pixel=2, Lens=1, James=1 |
| Gateway-Orphan-Threshold | 60 Min für `gateway:`-Prefix (statt 30) |
| ACCEPTED_TIMEOUT | 10 Min ohne accepted-Receipt → early-fail |
| SPECIALIST_DISPATCH_PROMPT | Expliziter SCHRITT 1: accepted-Receipt als allererste Aktion |
| Priority-Dispatch | `[P0]` → `[P1]` → `[P2]` → Rest in `dispatch_ready_tasks()` |
| `alert_stuck_assigned_tasks()` | assigned Tasks ohne Dispatch nach 120 Min → Discord-Alert |
| Contract-Blocker-Log | fehlende Execution Contracts im Dispatch explizit geloggt |
| maxRetriesReached-Alert | Discord-Notification wenn alle Retries aufgebraucht |
| Direct-Spawn nach Recovery | `_spawn_specialist()` direkt wenn `dispatchTarget` bekannt |
| `pending-pings.json` | Idempotenter Atlas-Ping — Retry über Zyklen bei gw_chat-Fehler |
| `notify_atlas_if_needed()` | Zählt assigned Tasks direkt via `/api/tasks` (nicht nur worker-pickups) |
| TOKEN_ALERT_CHANNEL | Forward-Reference-Bug gefixt (hardcoded String statt DISCORD_CHANNEL_ID) |
| ATLAS_COMPLETION_PROMPT | Expliziter 3-Schritt-Dispatch-Hinweis (Task erstellen → PATCH → Monitor spawnt) |

### 4. Ops-Aktionen

- **Server-Reboot** — Swap geleert (4 GB → 0), MCP-Prozesse von 270 auf 12 reduziert
- **MC-Rebuild** — `/api/agents/concurrency` und alle Fixes in Production gebaut
- **5 Tasks canceled** — 3 von uns erledigt, 2 Security-Tasks bewusst zurückgestellt
- **Vault-Dokumente** erstellt:
  - `03-Projects/next-gen-mc-worker-system.md` — IST/SOLL-Roadmap NextGen
  - `04-Operations/decisions/api-key-rotation-deferred.md` — Security-Entscheidung

### 5. System stabilisiert & gestartet

- 18 Tasks korrekt auf `assigned/queued`, alle mit Execution Contract
- Atlas gepingt mit 18 Tasks → dispatcht in Wellen
- 7 Tasks in-progress (Forge ×3, Pixel ×2, Lens ×1, James ×1)
- Worker-Monitor läuft fehlerfrei durch, Cron aktiv

---

## Offene Punkte (auf Board)

| Task | Beschreibung | Status |
|------|-------------|--------|
| `6890cc87` | Atlas Reporting-Ingestion deterministisch | assigned → Forge |
| `5107c8ab` | Atlas Step-8 Trigger-Policy | assigned → Forge |
| `364dcc89` | Timeout-Escalation Retry-State | in-progress → Forge |
| `b96b7813` | EADDRINUSE Root-Cause code-fix | assigned → Forge |
| `5caa87f1` | dispatchTask agentId-Override im Retry | assigned → Forge |
| `6f05473f` | /trends 404 + /team React-Error | in-progress → Pixel |
| `9e614f19` | TypeScript-Blocker Trends | in-progress → Pixel |
| `de16016f` | Trend-Dashboard Costs + Velocity | assigned → Lens |
| `f67ed79c` | Technologie & Modell-Research | in-progress → James |

---

## NextGen-Trigger

Wenn das System stabil läuft (72h ohne manuelle Eingriffe):
> **"Los starten Next Generation MC / Worker System"**

→ Atlas kennt die 8 NextGen-Tasks aus `03-Projects/next-gen-mc-worker-system.md`

---

## Wichtigste Erkenntnis dieser Session

`/api/worker-pickups` zeigt **nur** Tasks mit `dispatchState=dispatched`.
`assigned/queued` Tasks sind für den Dispatch-Endpoint unsichtbar.
Atlas muss den PATCH-Dispatch machen — worker-monitor spawnt dann die Session.
Der Notify-Bug (Atlas wurde nicht gepingt bei reinen assigned-Tasks) war der Hauptblocker.
