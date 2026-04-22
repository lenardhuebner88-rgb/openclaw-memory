# Lens Route × State × Component Coverage Audit — Sprint-I I3

**Datum:** 2026-04-19 23:30 GMT+2
**Agent:** Lens (efficiency-auditor)
**Task:** SPRINT-I-I3-LOADING-STATES-CLS-OPTIMISTIC-UI
**Scope:** 9 Routes × 4 States = 36 Zellen

---

## Coverage-Matrix (9 Routes × 4 States)

| Route | Loading-State | Empty-State | Error-State | Optimistic-UI |
|---|---|---|---|---|
| `/taskboard` | ⚠️ Text-fallback `"Loading task board…"` — kein Skeleton-Component | ✅ `EmptyLane` pro Lane (5 Lanes: waiting/picked/active/stalled/incident) | ❌ Kein Error-Boundary | ✅ `BulkActionBar` mit direktem UI-Update + Retry-Button |
| `/kanban` | ❌ Kein Loading-State (SSR via `PipelineClient`) | ❌ Kein Empty-State | ❌ Kein Error-Boundary | ❓ Unbekannt — `PipelineClient` nicht auditiert |
| `/monitoring` | ❌ Kein Loading-State (SSR + 30s-Polling, kein initial skeleton) | ❌ Kein Empty-State | ⚠️ Silent catch — hält letzte gute Daten, kein User-Feedback | ❌ N/A (lesend) |
| `/alerts` | ❌ Kein Loading-State (SSR) | ❌ Kein Empty-State | ❌ Kein Error-Boundary | ❌ N/A (lesend) |
| `/costs` | ❌ Kein Loading-State (SSR) | ❌ Kein Empty-State | ❌ Kein Error-Boundary | ❌ N/A (lesend) |
| `/dashboard` | ❌ Kein Loading-State (SSR) | ❌ Kein Empty-State | ❌ Kein Error-Boundary | ❌ N/A (lesend) |
| `/overview` | ❌ Kein Loading-State (SSR) | ❌ Kein Empty-State | ❌ Kein Error-Boundary | ❌ N/A (lesend) |
| `/analytics` | ✅ **Pulse-Skeleton** (4 KPI-Cards + 2 Chart-Placeholder, `data-testid="analytics-loading"`) | ❌ Kein Empty-State (kein `data.length === 0` Guard für Trends/Charts) | ✅ **Error-Fallback:** `"Analytics konnten nicht geladen werden."` (rote Box) | ❌ N/A (lesend, SWR mit 60s refresh) |
| `/ops` | ❌ Kein Loading-State (SSR mit Server-Props) | ❌ **Fehlt:** braucht Empty-State für "No scripts monitored" + "No schedulers configured" | ❌ Kein Error-Boundary | ❌ N/A (lesend) |
| `/more` | ❌ N/A (statisches Layout, kein API-Fetch) | ❌ N/A | ❌ N/A | ❌ N/A |

**Coverage-Score: 6/40 Zellen ✅ (15%)**

---

## Detail-Analyse

### Loading-States (Coverage: 2/9 Routes = 22%)

| Route | Status | Pattern | CLS-Risk |
|---|---|---|---|
| `/taskboard` | ⚠️ Minimal | String-fallback in Suspense | Niedrig (kein skeleton) |
| `/analytics` | ✅ Vollständig | `animate-pulse` cards + chart placeholders | Niedrig (matcht post-load layout) |
| Alle anderen 7 Routes | ❌ Fehlt | SSR mit `dynamic = 'force-dynamic'` | **Hoch** — bei langsamer Verbindung kein Feedback |

**Pixel-Impl-Priorität:**
1. `/monitoring` — polling fetch ohne skeleton (30s interval)
2. `/alerts` — SSR mit useEffect-polling fehlt skeleton
3. `/costs` — SSR ohne skeleton
4. `/kanban` — `PipelineClient` braucht `isLoading` guard
5. `/ops` — SSR mit großem payload (Schedulers + Scripts + Health)
6. `/dashboard` + `/overview` — `OverviewDashboard` muss skeleton haben

### Empty-States (Coverage: 1/9 Routes = 11%)

| Route | Status | Pattern |
|---|---|---|
| `/taskboard` | ✅ Pro Lane | `EmptyLane` mit message + pull-hint |
| `/analytics` | ❌ Fehlt | Braucht: "Keine Daten für gewählten Zeitraum" wenn Trends leer |
| `/ops` | ❌ Fehlt | Braucht: "Keine Scripts konfiguriert" + "Keine Scheduler aktiv" |
| Alle anderen 6 Routes | ❌ Fehlt oder N/A | — |

**Fehlende Empty-State-Texte (Pixel-Impl):**
- `/analytics`: "Für die gewählte Zeitspanne liegen keine Daten vor. Standardzeitraum ist 7 Tage."
- `/ops/scripts`: "Noch keine Scripts registriert. Füge Scripts in `/cron-jobs` hinzu."
- `/ops/schedulers`: "Keine Scheduler konfiguriert. Automationen erscheinen hier nach dem ersten Setup."

### Error-States (Coverage: 1/9 Routes = 11%)

| Route | Status | Pattern |
|---|---|---|
| `/analytics` | ✅ Vollständig | Rote Box "Analytics konnten nicht geladen werden." via `analytics.error` |
| `/monitoring` | ⚠️ Silent | `catch { /* keep last good snapshot */ }` — kein User-Feedback |
| Alle anderen 7 Routes | ❌ Kein Error-Boundary | Bei API-Fail: weißer Bildschirm oder Exception |

**monitoring catch-Block-Problem:** Der silent catch behält zwar den letzten State, aber der User weiß nicht, dass ein Fehler auftrat. Sollte einen kurzen gelben Banner zeigen: "Monitoring-Daten veraltet (letzte Aktualisierung: X)".

### Optimistic-UI (Coverage: 1/9 Routes = 11%)

| Route | Status | Pattern |
|---|---|---|
| `/taskboard` | ✅ Bulk-Actions | `BulkActionBar` mit sofortigem UI-Update, Retry-Button bei Fail, Error-Message in Bar |
| `/kanban` | ❓ Unbekannt | `PipelineClient` nicht vollständig auditiert |

**Optimistic-UI für `/taskboard`:**
- Flow: User wählt Tasks → Klickt "Assign"/"Cancel"/"Retry" → UI aktualisiert sofort → API-Call → bei Fail: Error-Message in `BulkActionBar`
- Problem: Kein `useOptimisticBulkAction` Hook — Logik vermischt in `TaskBoardClient`
- Pixel-Impl: `useOptimisticBulkAction` Hook auslagern, IndexedDB-Offline-Queue integrieren

---

## Connection-Status-Indicator (fehlt global)

| Komponente | Status | Details |
|---|---|---|
| `<ConnectionStatus>` in `mission-shell.tsx` | ❌ Fehlt | Shell hat kein Status-Indikator |
| Top-Bar Mini-Dot (green/yellow/red) | ❌ Fehlt | Plan: `mission-shell.tsx` Top-Leiste |
| `navigator.onLine` + EventSource `readyState` | ❌ Nicht implementiert | Braucht `useOnlineStatus` Hook |
| `prefers-reduced-motion` | ❌ Nicht in Shell | Sollte SSE-Flash-Animationen deaktivieren |

**Pixel-Impl:** Mini-Dot in Top-Bar der `MissionShell`, 3 Zustände:
- 🟢 `green`: online + SSE connected
- 🟡 `yellow`: online + SSE reconnecting
- 🔴 `red`: offline

---

## Offline-Action-Queue (fehlt)

| Komponente | Status |
|---|---|
| `public/sw.js` | ❌ Nicht vorhanden |
| ServiceWorker-Registrierung in `layout.tsx` | ❌ Fehlt |
| IndexedDB-Queue für Receipt-Post + Task-Patch | ❌ Fehlt |
| Replay-on-Reconnect Logic | ❌ Fehlt |

**Scope-Notiz (Sprint-I I3):** ServiceWorker-Scaffold nur für Offline-Queue, kein Full-PWA. Real-Impl Timebox: 1h. Falls komplexer → Sprint-K Kandidat.

---

## CLS-Risiken (Critical für Lighthouse ≥ 90)

| Route | Risk | Detail |
|---|---|---|
| `/analytics` | ✅ Gedeckt | Skeleton matcht post-load layout (4 KPI cards, 2 chart areas) |
| `/taskboard` | ⚠️ Mittel | Text-Fallback hat andere Höhe als `TaskColumnSkeleton` → potential shift |
| `/monitoring` | ⚠️ Hoch | Kein skeleton → Cron-Tabelle flackert bei Refresh |
| `/ops` | ⚠️ Hoch | Scheduler + Script Tables brauchen skeleton, sonst layout shift |

**Empfehlung:** `TaskColumnSkeleton` existiert in `skeleton.tsx` aber wird in `taskboard/page.tsx` nicht verwendet. Pixel sollte `Suspense`-Fallback auf `TaskColumnSkeleton` umstellen (count=3 pro Column).

---

## Prioritäts-Matrix für Pixel-Impl (3.5h Budget)

| Priority | Action | Route | Zeit |
|---|---|---|---|
| P0 | SkeletonCard/Table in `skeleton.tsx` erweitern | global | 30min |
| P0 | `/analytics` Empty-State ergänzen | analytics | 15min |
| P0 | `/ops` Empty-States (scripts + schedulers) | ops | 20min |
| P1 | `TaskColumnSkeleton` als Suspense-Fallback in `/taskboard` | taskboard | 15min |
| P1 | Skeleton für `/monitoring` Cron-Tabelle | monitoring | 20min |
| P1 | Skeleton für `/ops` Dashboard | ops | 20min |
| P1 | `useOnlineStatus` Hook + `<ConnectionStatus>` in Shell | global | 30min |
| P2 | `monitoring-client` Silent-Catch → User-Banner | monitoring | 10min |
| P2 | `useOptimisticBulkAction` Hook extrahieren | taskboard | 20min |
| P2 | ServiceWorker-Scaffold + Offline-Queue | global | 45min* |

*Falls SW > 45min → als Sprint-K Kandidat zurücksetzen.

---

## Offene Fragen (an Atlas/Operator)

1. `/kanban` `PipelineClient` vollständig prüfen — Loading/Error/Optimistic-UI Status unklar
2. `prefers-reduced-motion` — soll in Sprint-I I3 oder I2 (Typography) adressiert werden?
3. Connection-Indicator Position: Top-Bar der Shell vs. eigenes `<ConnectionStatus>` in `mission-shell.tsx`?

---

**Ende Lens I3 Pre-Audit**
Lens (efficiency-auditor) — sprint-i-i3-lens-coverage
