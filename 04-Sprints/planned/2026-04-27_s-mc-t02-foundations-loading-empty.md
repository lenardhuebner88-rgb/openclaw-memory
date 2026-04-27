---
name: Sprint-MC-T02 Foundations Loading + Empty States
description: Atlas-autonomous P1 fixes - Skeleton-Loader-Library + EmptyState-Component + Initial-Render-Race + STALE-Widerspruch.
status: planned
since: 2026-04-27
owner: Operator (pieter_pan)
trigger_phrase: "Atlas Sprint MC-T02 Foundations starten"
related:
  - vault/04-Sprints/planned/2026-04-27_mc-ui-audit-claude-design-prep.md
  - vault/04-Sprints/planned/2026-04-27_s-mc-t01-critical-bug-triage.md
autonomy_mode: full
operator_gates: none
depends_on: Sprint-MC-T01 (T5 ErrorBoundary in Pixel-component-tree muss bestehen vor F1)
---

# Sprint-MC-T02 — Foundations Loading + Empty States (Atlas-autonom)

**Context:** Audit hat 4 systemische UX-Lücken gefunden: kein Skeleton-Loader irgendwo, Empty-States ohne Next-Action, Initial-Render-Race auf Dashboard (Online 0/0 → 6/6), Widerspruch zwischen STALE-Badge und "kein Eingriff nötig"-Text. Diese vier Probleme teilen sich eine Lösung: shared UI-Komponenten + konsistente Loading-/Empty-Patterns.

**Trigger:** `Atlas Sprint MC-T02 Foundations starten`

**Atlas-Mandate:**
- Volle autonome Steuerung — keine Operator-Approval-Gates
- Atlas wartet auf MC-T01 done bevor F-Subs spawnen (depends_on)
- Atlas verifiziert per DoD vor Receipt=result
- Atlas postet Sprint-Done-Report in `frontend-guru` (1486480170763157516) wenn alle 4 Subs done

---

## Scope-Matrix

| Sub | Title | Owner | Estimate | DoD |
|---|---|---|---|---|
| **F1** | Skeleton-Loader Component-Library | Pixel | 2-2.5h | `<Skeleton variant="card\|list\|kpi" />` exportiert + Storybook-Eintrag |
| **F2** | EmptyState Component | Pixel | 1-1.5h | `<EmptyState title subtitle action>` exportiert + Storybook |
| **F3** | Dashboard Initial-Render-Race fix | Forge | 1.5-2h | "Online 0/0" → "6/6" Sprung verschwindet, Skeleton während initial-fetch sichtbar |
| **F4** | STALE-Widerspruch UI fix | Pixel | 30-45 min | Wenn STALE-Badge aktiv → Body-Text wechselt zu "Letzte Aktivität vor Xd" statt "kein Eingriff nötig" |

**Total Estimate:** 5-6h

---

## F1 — Skeleton-Loader Component-Library

### Problem
- `document.querySelector('[class*="skeleton"]')` returns null auf jeder Page
- Pipeline zeigt nur Plain-Text "Loading live pipeline..."
- Initial-Loads sind visuell broken statt skeleton-pulsing

### Fix-Steps für Pixel

1. Erstelle `mission-control/src/components/ui/Skeleton.tsx`:
```tsx
import { cn } from '@/lib/utils'

interface SkeletonProps {
  variant?: 'card' | 'list-row' | 'kpi' | 'text-line'
  className?: string
  count?: number
}

const variantClass = {
  card: 'h-32 w-full rounded-lg',
  'list-row': 'h-12 w-full rounded',
  kpi: 'h-24 w-full rounded-md',
  'text-line': 'h-4 w-3/4 rounded',
}

export function Skeleton({ variant = 'card', className, count = 1 }: SkeletonProps) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className={cn(
            'animate-pulse bg-white/5',
            variantClass[variant],
            className,
          )}
        />
      ))}
    </>
  )
}
```

2. Storybook-Story (oder ein einfacher Demo-File falls kein Storybook): `Skeleton.stories.tsx` mit allen 4 Variants

3. **Anwendung in 3 priorisierten Pages:**
   - `/kanban` Pipeline: ersetze "Loading live pipeline..." text mit `<Skeleton variant="card" count={3} />`
   - `/alerts` Feed: Skeleton-list-row count=8 während fetch
   - `/dashboard` Drei-Karten: Skeleton-kpi count=3 während initial-load

### Verify
```sh
curl -s -H "Cache-Control: no-cache" http://localhost:3000/kanban | grep -c "animate-pulse"
# Expected: ≥1 während initial-render-window (race-condition möglich, daher mehrfach testen)
```
Plus Browser-Inspect: `document.querySelectorAll('[class*="animate-pulse"]').length > 0` während Page-Reload.

---

## F2 — EmptyState Component

### Problem
Alle "0"-Karten zeigen nur "Queue leer", "Signale ruhig", "Recovery frei" ohne Next-Action. Operator weiß nicht was zu tun ist im Idle-State.

### Fix-Steps für Pixel

1. Erstelle `mission-control/src/components/ui/EmptyState.tsx`:
```tsx
import { ReactNode } from 'react'

interface EmptyStateProps {
  icon?: ReactNode  // optional emoji or icon
  title: string
  subtitle?: string
  action?: { label: string; href?: string; onClick?: () => void }
}

export function EmptyState({ icon, title, subtitle, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-8 text-center">
      {icon && <div className="text-3xl opacity-50">{icon}</div>}
      <h3 className="text-base font-medium">{title}</h3>
      {subtitle && <p className="text-sm opacity-60 max-w-sm">{subtitle}</p>}
      {action && (
        <a
          href={action.href}
          onClick={action.onClick}
          className="mt-2 px-4 py-1.5 text-sm bg-purple-600/20 hover:bg-purple-600/40 rounded-md transition"
        >
          {action.label}
        </a>
      )}
    </div>
  )
}
```

2. **Anwendung in 3 priorisierten Pages:**
   - `/dashboard` "Jetzt Handeln" Card wenn `0`: `<EmptyState title="Queue leer" subtitle="Nutze den Board-Scan um manuelle Dispatch-Targets zu prüfen" action={{ label: 'Board öffnen', href: '/kanban' }} />`
   - `/dashboard` "Gefährdet" Card wenn `0`: action=`Risikofilter öffnen` href=`/alerts`
   - `/dashboard` "Stabilisieren" Card wenn `0`: action=`Recovery-Spuren prüfen` href=`/ops`

### Verify
- Browser open `/dashboard` → in jeder 0-Card erscheint genau 1 Action-Button
- DOM-Check: `document.querySelectorAll('[href="/kanban"]').length` aus Dashboard-Empty-State ≥ 1

---

## F3 — Dashboard Initial-Render-Race fix

### Problem
Audit-Beobachtung: `Online 0/0 · Aktiv 0` springt nach Scroll auf `6/6 · 4`. Vermutung: useEffect-fetch ohne initialData → Component rendert mit defaults bevor data kommt.

### Atlas-Heuristic
1. Forge identifiziert Online-Counter Component via `grep -rn "Online" mission-control/src/components/dashboard/ mission-control/src/app/dashboard/`
2. Forge prüft Data-Fetching-Pattern: useState mit defaults `{ online: '0/0', active: 0 }` ist der Bug.

### Fix-Steps für Forge
**Option A (preferred): SSR-Initial-Data**
1. Convert die Komponente zu Server-Component oder mit Next.js' `unstable_cache` für initial-fetch im Server
2. Hand-off zu Client-Component für Live-SSE-updates
3. Pattern:
```tsx
// page.tsx (server)
async function getInitialAgentStatus() {
  const res = await fetch('http://localhost:3000/api/agents/status', { cache: 'no-store' })
  return res.json()
}
export default async function DashboardPage() {
  const initialStatus = await getInitialAgentStatus()
  return <DashboardClient initialStatus={initialStatus} />
}
```

**Option B (fallback): Skeleton während Initial-Fetch**
- useState `data` startet als `null` (nicht `{ online: '0/0' }`)
- Render: `data === null ? <Skeleton variant="kpi" /> : <RealNumbers data={data} />`

Forge wählt A wenn Page bereits server-component ist, sonst B.

### Verify
- Browser DevTools Network: clear cache + reload `/dashboard`
- Beobachte: Online-Counter zeigt entweder `6/6` direkt (Option A) oder Skeleton-pulse → `6/6` (Option B). NIEMALS `0/0` → `6/6` Springen.
- Performance-Check: `LCP < 1500ms` per Lighthouse-mobile

---

## F4 — STALE-Widerspruch UI fix

### Problem
Audit-Beobachtung auf /kanban Spark/James-Cards:
- Roter Badge: `STALE · 1D`
- Body-Text: "No task needs attention right now"  
- Diese zwei Botschaften widersprechen sich

### Fix-Steps für Pixel

1. Identifiziere Pipeline-Card-Component via `grep -rn "needs attention\|STALE" mission-control/src/components/`
2. Conditional-Logic anpassen in der Card-Component:

```tsx
const status = data.staleness === 'stale' ? 'stale' : data.taskCount > 0 ? 'active' : 'idle'

const bodyText = {
  active: 'Aktive Tasks brauchen Aufmerksamkeit',
  idle: 'Kein Eingriff nötig',
  stale: `Letzte Aktivität vor ${data.stalenessAge}`, // z.B. "1d 2h"
}[status]
```

3. Optional Polish: Text-color für `stale` leicht abdimmen (opacity-60) damit visuell klar ist "veraltet, aber nicht akut"

### Verify
- /kanban öffnen
- Spark-Card: Badge bleibt `STALE · 1d`, Body wechselt zu "Letzte Aktivität vor 1d"
- James-Card: gleicher Effekt
- Atlas/Forge mit FRESH-Status: Body bleibt "Kein Eingriff nötig"

---

## Cross-Sprint Receipts + Final-Step

Receipts wie in MC-T01 (R45/R50 Pflicht).

**Atlas-Sprint-Final-Step (no operator gate):**
1. Alle 4 Subs done → Atlas postet Discord-Report in `frontend-guru` (1486480170763157516):
   - F1 Component-Library deployed
   - F2 EmptyState integriert in 3 Cards
   - F3 Render-Race fix per Option A oder B
   - F4 STALE-Widerspruch fixed
2. Atlas renamed Plan-Doc nach `vault/04-Sprints/done/2026-04-27_s-mc-t02-foundations-loading-empty.md`

---

## Notes für Atlas

- F1 + F2 sind parallel-fähig (beide Pixel, aber unabhängige Files)
- F3 muss nach F1 starten (nutzt Skeleton-Component)
- F4 ist unabhängig
- Wenn Pixel-Capacity-Konflikt mit anderem aktivem Sprint → Atlas serialisiert F1→F2→F4, F3 (Forge) parallel
