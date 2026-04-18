---
title: Agent-Display-Konventions-Guide (Mission Control UI)
date: 2026-04-18
author: Operator direct (Spark-Task-Übernahme)
status: reference — dev-ready
purpose: Single source of truth für Agent-Darstellung in allen MC-UI-Flächen. Verhindert Name/Emoji/Color-Drift zwischen Komponenten.
scope: Taskboard, Pipeline-Tab, Agents-Tab, Memory-Tab, Mobile-Views, Notifications
---

# Agent-Display-Konventions-Guide

## 0. Design-Prinzip (härteste Regel)

**Zwei Namensräume getrennt:**

| Räumlich | Beispiel | Wo |
|---|---|---|
| **Runtime-ID** | `main`, `sre-expert`, `frontend-guru`, `efficiency-auditor`, `spark`, `james` | APIs, Routing, Dispatch, Keying, Scoring, Worker-Sessions |
| **Display-Name** | `Atlas`, `Forge`, `Pixel`, `Lens`, `Spark`, `James` | UI, Labels, Reports, Human-Reading |

**Umwandlung ausschließlich über `task-assignees.ts` helpers:**
- `resolveRuntimeAgentId()` — Display → Runtime
- `resolveAssigneeAlias()` — Runtime → Display
- `normalizeAssignee()` — beides in Display-Form

**Niemals:** Display-Name hardcoden in Routing/Scoring/Keying. Runtime-ID hardcoden in User-facing Labels.

---

## 1. Agent-Signatur-Tabelle (Single Source of Truth)

| Agent | Runtime-ID | Display | Emoji | Primary-Color | Short-Code | Tailwind-Accent |
|---|---|---|---|---|---|---|
| Atlas | `main` | **Atlas** | 🦅 | amber-400 | `ATL` | `border-amber-400/30 bg-amber-400/10 text-amber-200` |
| Forge | `sre-expert` | **Forge** | 🔨 | orange-400 | `FRG` | `border-orange-400/30 bg-orange-400/10 text-orange-200` |
| Pixel | `frontend-guru` | **Pixel** | 🎨 | pink-400 | `PIX` | `border-pink-400/30 bg-pink-400/10 text-pink-200` |
| Lens | `efficiency-auditor` | **Lens** | 🔍 | cyan-400 | `LNS` | `border-cyan-400/30 bg-cyan-400/10 text-cyan-200` |
| Spark | `spark` | **Spark** | ✨ | violet-400 | `SPK` | `border-violet-400/30 bg-violet-400/10 text-violet-200` |
| James | `james` | **James** | 📚 | slate-400 | `JMS` | `border-slate-400/30 bg-slate-400/10 text-slate-200` |

**Farb-Logik:**
- Atlas/Forge/Pixel → warm (Leitung/Handwerk/Kreation)
- Lens/Spark/James → kühl (Analyse/Inspiration/Wissen)
- Jeder Hue eindeutig — kein Overlap

**Dark-Mode-First:** Alle Werte sind auf MCs Dark-Theme kalibriert (`#0a0a0a` background). Light-Mode später mit Sättigung +15%.

---

## 2. Patterns (mit Code-Referenz-Snippets)

### A) Badge (klein, in Task-Card oder Tab-Header)
**Use:** Chip neben Agent-Namen, 1-Zeile-Attribution
```
[ 🔨 Forge ]      ← Desktop full
[ 🔨 FRG ]        ← Mobile short (<640px)
```
Format: `{emoji}{space}{name-or-short}`. Padding `px-2 py-1`, border-radius `full`.

### B) Avatar-Chip (rund, Agent-Owner-Display)
**Use:** Top-right der Task-Card, neben Title
```
⬤ 🦅        ← Icon only (Mobile)
( Atlas )   ← Label hover-expand (Desktop)
```
Size: `h-7 w-7` (mobile) / `h-8 w-8` (desktop), centered emoji, bg `{color}-400/15`, border `{color}-400/30`.

### C) Status-Pill (innerhalb Agent-Heartbeat-Zone)
**Use:** Zone D "Agent Load" in Taskboard
```
Atlas   0/1 IDLE
Forge   3/3 LOADED
```
Format: `{name}   {active}/{wip-limit} {status-word}`. `status-word`:
- `IDLE` — zero active + zero queued
- `OK` — 0 < active < wipLimit
- `LOADED` — active + queued == wipLimit (auslastungs-warnung)
- `OVERLOAD` — queued > wipLimit (roter Badge)

Meter-Bar darunter: progressbar mit gradient `{color}-400 → {color}-400/30`.

### D) Mobile-Short (Sparse-Layout <640px)
**Use:** Wenn horizontaler Platz knapp (Status-Pill-Reihe, Lane-Tab, Card-Overflow)
```
🦅    ← Emoji-only (most compact)
ATL   ← Code-only (wenn Emoji nicht rendered)
ATL 🦅 ← beide (wenn Platz für 4-5 chars)
```

Breakpoint-Regel:
- `≥1024px`: Emoji + Full-Name (`🦅 Atlas`)
- `640–1023px`: Emoji + Name truncated via CSS (`🦅 Atlas`)
- `<640px`: Emoji-only ODER Short-Code, kontextabhängig

### E) Attribution-Line (in Text-Reports, NBA, Heartbeats)
**Use:** Klartext-Sätze wie "Forge hat A2 fertiggestellt"
```
Forge completed A2 — Next-Best-Action rule now reactive  ✓
sre-expert completed...                                  ✗ (nie Runtime-ID in UI-Text)
🔨 Forge completed...                                     🟡 (Emoji optional, kontextabhängig)
```

---

## 3. Do / Don't

### ✅ DO
- Lens' Three-Source-of-Truth in `task-assignees.ts` als Einzige zentrale Map nutzen
- In neuen Components Agent-Color via `AGENT_COLOR_CLASSES[agentId]` konstante aus `src/lib/agent-ui.ts` importieren (siehe §5)
- Emoji + Name zusammen anzeigen bei erster Attribution einer UI-Fläche; danach Emoji-only wiederholen
- Runtime-ID nur in technischen Tooltip/Raw-JSON-Drawer zeigen, klar gekennzeichnet als "Runtime: sre-expert"

### ❌ DON'T
- Display-Name in Arrays für Scoring/Keying mischen (`['atlas', 'forge', 'frontend-guru']` — gestern Live-Bug WK-NEW in `taskboard-intelligence.ts:126`)
- Emoji ohne Name verwenden bei erster Nennung
- Farbe willkürlich zuordnen — Hue ist semantisch (Leitung/SRE/UI/Analyse/Kreativ/Wissen)
- Agent-spezifische Logic hardcoden außerhalb `task-assignees.ts` (z.B. Escalation-Chains) — führt zu L2-Pattern (konkurrierende Mutation-Channels)

---

## 4. Accessibility

- Emoji ergänzen, nicht ersetzen: Screen-Reader liest "Atlas" — Emoji ist dekorativ, mit `aria-hidden="true"` umwickeln
- Farbe nie als einziger Träger von Information — immer Name/Code daneben (WCAG 1.4.1)
- Short-Code (ATL/FRG/etc.) ist Fallback wenn Emoji nicht rendert (Browser ohne Emoji-Font)
- Kontrast mind. 4.5:1 (`text-{color}-200` auf `bg-black` = bestanden)

---

## 5. Implementation-Hint: neue `src/lib/agent-ui.ts`

Als Follow-up eine zentrale TS-Konstante empfohlen — NIEMALS in Components inline:

```ts
// src/lib/agent-ui.ts
export const AGENT_DISPLAY = {
  main:       { name: 'Atlas',  emoji: '🦅', short: 'ATL', hue: 'amber'  },
  'sre-expert':       { name: 'Forge',  emoji: '🔨', short: 'FRG', hue: 'orange' },
  'frontend-guru':    { name: 'Pixel',  emoji: '🎨', short: 'PIX', hue: 'pink'   },
  'efficiency-auditor': { name: 'Lens', emoji: '🔍', short: 'LNS', hue: 'cyan'   },
  spark:      { name: 'Spark',  emoji: '✨', short: 'SPK', hue: 'violet' },
  james:      { name: 'James',  emoji: '📚', short: 'JMS', hue: 'slate'  },
} as const;

export function agentColorClasses(runtimeId: string, variant: 'badge' | 'avatar' | 'pill' = 'badge') {
  const hue = AGENT_DISPLAY[runtimeId]?.hue ?? 'zinc';
  // returns matching Tailwind-Classes je nach variant
}
```

Implementation-Task soll das erstellen + bestehende hardcoded colors ersetzen.

---

## 6. Migration — wo aktuell falsch

Live-Bugs gefunden 2026-04-18 abends:
- `taskboard-intelligence.ts:126` — Array `['atlas', 'forge', 'pixel', 'lens', 'spark', 'frontend-guru', 'james']` — mischt Display+Runtime (behoben durch Naming-P1-B)
- `dream-health-data.ts` — SRE-Expert als eigener Agent neben Forge (behoben durch Naming-P1-A)
- `costs-data.ts:ALL_PRO_AGENTS` — mischt `atlas` (Display) + `sre-expert` (Runtime) (behoben durch Naming-P1-C)
- `worker-monitor.py:AGENT_DISPLAY_TO_GW_ID` — `'james': 'researcher'` (falsch) + Spark fehlt (behoben durch Operator 2026-04-18)

Für weitere `new AGENT_*`-Files: zuerst via grep prüfen, diese Map als Ground-Truth nehmen.

---

## 7. Kurze Daten-Schnittstelle

Wenn ein UI-Component Agent-Data konsumiert, erwartet er dieses Interface:

```ts
type AgentDisplay = {
  runtimeId: string;      // "sre-expert"
  name: string;           // "Forge"
  emoji: string;          // "🔨"
  short: string;          // "FRG"
  hue: string;            // "orange"
  // optional per-context:
  status?: 'idle' | 'ok' | 'loaded' | 'overload';
  activeCount?: number;
  wipLimit?: number;
};
```

Ein `useAgentDisplay(taskOrAgentId)`-Hook oder Server-Helper stellt das bereit. Kein Component darf die Felder einzeln aus verschiedenen Quellen zusammenbauen.

---

## Zusammenfassung für Devs

- 6 Agents, je 1 Emoji + Name + Color + Short-Code (Tabelle §1)
- 5 Patterns: Badge / Avatar / Status-Pill / Mobile-Short / Attribution-Line (§2)
- Runtime-ID = API; Display-Name = UI (§0)
- Alles zentral in `src/lib/agent-ui.ts` konstante + `task-assignees.ts` lookup
- Accessibility: Emoji dekorativ, Name informativ

Alle neuen Features bauen gegen diese Tabelle. Drift = Build-Breaker + Operator-Vertrauen-Verlust.
