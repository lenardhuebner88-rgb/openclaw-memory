---
name: Sprint-MC-T01 Critical Bug Triage
description: Atlas-autonomous P0 fixes from Mission Control UI-Audit 2026-04-27 — 5 production-bugs, no operator gates.
status: planned
since: 2026-04-27
owner: Operator (pieter_pan)
trigger_phrase: "Atlas Sprint MC-T01 Critical Bug Triage starten"
related:
  - vault/04-Sprints/planned/2026-04-27_mc-ui-audit-claude-design-prep.md
autonomy_mode: full
operator_gates: none
---

# Sprint-MC-T01 — Critical Bug Triage (Atlas-autonom)

**Context:** Live-Audit der Mission-Control-Routes (2026-04-27 ~14:00 UTC) hat 5 P0-Bugs aufgedeckt. Vor jeder weiteren UX-Arbeit müssen diese gefixt sein damit die Baseline ehrlich ist.

**Trigger:** `Atlas Sprint MC-T01 Critical Bug Triage starten`

**Atlas-Mandate:**
- Volle autonome Steuerung — keine Operator-Approval-Gates
- Atlas trifft Decisions selbst per Heuristics in jedem Sub-Task definiert
- Atlas verifiziert jeden Sub-Task per DoD-Check vor Receipt=result
- Atlas postet Sprint-Done-Report nach Channel `sre-expert` (1486480146524410028) wenn alle 5 Subs done

---

## Scope-Matrix

| Sub | Title | Owner | Estimate | DoD |
|---|---|---|---|---|
| **T1** | /automate Dead-Link Resolution | Forge | 30-45 min | curl /automate → 200 OR Nav-Link weg |
| **T2** | Mermaid-Render in /ops fixen | Forge | 1-1.5h | /ops Dependency-Graph zeigt SVG, nicht <pre>-Code |
| **T3** | DATA: FALLBACK Root-Cause Investigation + Fix | Forge | 2-3h | /kanban zeigt ≤1 Card mit DATA: FALLBACK |
| **T4** | Cost Source-of-Truth Konsolidierung | Forge | 1.5-2h | /costs und /analytics zeigen identischen Daily-Cost-Wert |
| **T5** | ErrorBoundary global einziehen | Pixel | 45-60 min | React-Throw-Test triggert Error-UI statt White-Screen |

**Total Estimate:** 6-8h

---

## T1 — /automate Dead-Link Resolution

### Problem
Top-Nav-Link "Automate" führt auf 404. Operator-Vertrauen-Killer.

### Atlas-Heuristic (no-operator-gate)
1. Forge führt aus: `grep -r "/automate" /home/piet/.openclaw/workspace/mission-control/src/app/ /home/piet/.openclaw/workspace/mission-control/src/lib/ 2>/dev/null`
2. **Decision-Tree:**
   - Wenn `app/automate/page.tsx` ODER `app/api/automate/` existiert → Route ist halb-implementiert → Sub-Task: Page implementieren oder als 503-WIP-Page rendern (Title: "Automate", Body: "Coming soon"). Nav-Link bleibt.
   - Wenn KEIN automate-Code existiert → Atlas-Decision: Nav-Link aus `src/components/MissionControlNav.tsx` (oder wo immer der Top-Nav lebt) entfernen. Commit mit Subject `fix(nav): remove dead /automate link until route exists`.

### Fix-Steps für Forge
- Locate Nav-Component via `grep -rn "Automate" mission-control/src/components/` 
- Edit + Build + Restart MC
- Receipt=progress nach Edit, Receipt=result nach Build success

### Verify (Forge muss vor Receipt=result laufen lassen)
```sh
curl -sS -o /dev/null -w "%{http_code}\n" http://localhost:3000/automate
# Expected: 200 (wenn implemented) ODER Nav-Link entfernt → kein User-facing Link mehr
curl -s http://localhost:3000/dashboard | grep -c "Automate" 
# Expected: 0 wenn Nav entfernt
```

---

## T2 — Mermaid-Render in /ops

### Problem
`/ops` Dependency-Graph rendert Raw-Mermaid-Code als `<pre>`-Block statt SVG.

### Atlas-Heuristic
- `mermaid` npm-Package vermutlich nicht installiert ODER nicht in der Component verdrahtet
- Forge prüft: `cd /home/piet/.openclaw/workspace/mission-control && grep -i mermaid package.json`

### Fix-Steps für Forge
1. `npm install mermaid` falls fehlend
2. Identifiziere Ops-Page-Component: vermutlich `src/app/ops/page.tsx` oder `src/components/ops/DependencyGraph.tsx`
3. Pattern für Next.js Mermaid-Render:
   - Dynamic-import (`next/dynamic` mit `ssr: false`)
   - In `useEffect`: `mermaid.initialize({ startOnLoad: false }); mermaid.render(id, graphDef)`
4. Build + restart MC

### Verify
```sh
curl -s http://localhost:3000/ops | grep -E "<svg|mermaid-svg" | head -3
# Expected: ≥1 hit
curl -s http://localhost:3000/ops | grep -c '<pre>graph TD'
# Expected: 0
```

---

## T3 — DATA: FALLBACK Root-Cause + Fix

### Problem
5 von 6 Agent-Cards auf /kanban zeigen `DATA: FALLBACK` (nur Forge zeigt CACHED). Live-Stream funktioniert nicht für die meisten Agents.

### Atlas-Heuristic (Investigation)
1. Forge greppt nach FALLBACK-Logic: `grep -rn "FALLBACK\|fallback" mission-control/src/app/api/agents/ mission-control/src/lib/ 2>/dev/null`
2. Forge checkt SSE-Stream: `curl -N --max-time 5 http://localhost:3000/api/agents/stream` → notiert welche agent-IDs im Stream auftauchen
3. Forge vergleicht mit `tasks.json` agent-Liste
4. **Hypothesen-Reihenfolge:**
   - **H1:** SSE-stream emittiert nur agents die aktuell in-progress sind → idle agents fallen auf cache zurück. Fix: SSE-stream emittiert alle 6 registered agents mit ihrem letzten bekannten Stand.
   - **H2:** Agent-ID-Mismatch zwischen SSE (`sre-expert`) und Display (`Forge`) → resolveRuntimeAgentId() Bug. Fix: Mapping reparieren.
   - **H3:** Cache-Source-Stream blockiert weil OOM oder file-lock. Fix: Cache-Source diagnostizieren.

### Fix-Steps für Forge
- Forge debugged sequenziell H1→H2→H3 bis Root-Cause klar
- Fix in entsprechender Datei (api-route oder lib)
- Receipt=progress nach Investigation done (mit "root-cause: HX")
- Receipt=result nach Fix deployed

### Verify
```sh
curl -s http://localhost:3000/api/tasks | jq '[.tasks[] | .assigned_agent] | unique'
# Expected: alle 6 agents im Output
# Browser: /kanban öffnen → max 1 DATA: FALLBACK card sichtbar
```

---

## T4 — Cost Source-of-Truth Konsolidierung

### Problem
- `/analytics` zeigt: `Cost Pressure €134.77 · Daily €134.77`
- `/costs` Cockpit zeigt: `Today $0.00 / $20.00`
- Operator weiß nicht welcher Wert stimmt → Vertrauen-Killer

### Atlas-Decision (autonom, ohne Operator)
**Source-of-Truth = `/api/analytics/cost-pressure`** (SSE-fed, Live).

Reasoning (Atlas-Heuristic):
- Analytics zeigt €-Currency mit konsistenten Werten zur Subscription-Status (€34.04 / €40.00 MiniMax)
- Costs Cockpit $0.00 ist nicht-initialisierter State (today-budget pay-per-use, aber MiniMax ist subscription → $0.00 "korrekt" aber misleading)
- Single-Source-Strategie: `/costs` verbraucht `/api/analytics/cost-pressure` als primäre Quelle

### Fix-Steps für Forge
1. Identifiziere `/costs`-Page Component und sein Data-Fetching
2. Refactor: ersetze direkten `/api/costs`-call mit `/api/analytics/cost-pressure` derived data
3. `/api/costs` Endpoint behalten als fallback (markiert deprecated im Source)
4. Currency-Consistency: alle Werte als € rendern (USD-Felder removen oder konvertieren)
5. Composite-Effective-$-Card: rename zu "Effective Cost" mit klarer Tooltip "PPU = Pay-per-Use prepaid balance"

### Verify
```sh
ANALYTICS=$(curl -s http://localhost:3000/api/analytics/cost-pressure | jq -r '.daily // .pressure')
COSTS=$(curl -s http://localhost:3000/api/costs | jq -r '.today.actual // .daily')
echo "analytics=$ANALYTICS costs=$COSTS"
# Expected: identische Werte
```

---

## T5 — ErrorBoundary global einziehen

### Problem
`document.querySelector('[class*="error-boundary"]')` returns null. React-Render-Error führt zu White-Screen.

### Fix-Steps für Pixel
1. Erstelle `mission-control/src/app/error.tsx` (Next.js App-Router-Convention):
```tsx
'use client'
import { useEffect } from 'react'
export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  useEffect(() => { console.error('App-level error:', error) }, [error])
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
      <h2 className="text-2xl font-semibold">Etwas ist schiefgelaufen</h2>
      <p className="text-sm opacity-70">{error.message || 'Unbekannter Fehler'}</p>
      <button onClick={reset} className="px-4 py-2 bg-purple-600 rounded hover:bg-purple-700">
        Erneut versuchen
      </button>
    </div>
  )
}
```
2. Optional: `app/(routes)/error.tsx` per Tab für scoped error-handling
3. Build + restart MC

### Verify
- Manuelle Throw-Test im Dev-Mode (Pixel triggert via injecting `throw new Error('test')` in eine Component) → Error-UI erscheint
- DOM-Check via `curl + grep "Etwas ist schiefgelaufen"` ist nicht möglich (server-rendered nur on-error). Pixel postet Screenshot als Receipt-attachment.

---

## Cross-Sprint Receipts-Discipline (R45/R50 Pflicht)

Atlas und alle Sub-Agents:
- `taskboard_post_receipt(taskId, receipt=accepted, summary=<plan>)` direkt nach Task-Pickup
- Major-Steps: `taskboard_post_receipt(taskId, receipt=progress, summary=<step done>)`
- Final: `taskboard_post_receipt(taskId, receipt=result, summary=<full report>, status=done|failed)`

**Atlas-Sprint-Final-Step (no operator gate):**
1. Wenn alle 5 Subs `done` → Atlas postet Sprint-Done-Report in Discord channel `1486480146524410028` (sre-expert) mit:
   - Welcher Sub mit welchem Commit-SHA fixed
   - Welche /api oder /route urls verifiziert wurden
   - Outstanding issues für Followup-Sprint
2. Atlas markiert Sprint-Plan-Doc `status: done` und renamed nach `vault/04-Sprints/done/2026-04-27_s-mc-t01-critical-bug-triage.md`

---

## Notes für Atlas

- Pre-Flight-Sprint-Dispatch laufen lassen vor Sub-Task-Spawning: `ssh homeserver "/home/piet/.openclaw/scripts/pre-flight-sprint-dispatch.sh /home/piet/vault/04-Sprints/planned/2026-04-27_s-mc-t01-critical-bug-triage.md"`
- Subs sequenziell oder parallel: T1+T2+T5 können parallel laufen (independent), T3 muss vor T4 laufen (T4 könnte von T3 Source-of-Truth profitieren). T5 (Pixel) kann unabhängig parallel.
- Bei DATA: FALLBACK-Root-Cause unklar nach 90 min Investigation: Atlas postet Hilfe-Anfrage im Channel statt zu eskalieren — Operator entscheidet on-call.
