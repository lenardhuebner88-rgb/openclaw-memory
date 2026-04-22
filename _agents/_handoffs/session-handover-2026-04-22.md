---
title: Session-Handover 2026-04-22 — für nächste Claude Code Session
created: 2026-04-22
purpose: Kompakte Startpunkt-Doku für neue Claude-Code-Session. Read-First bei Session-Start.
previous-session: end-of-day-2026-04-22.md
read-first-order:
  - 1. diese Datei
  - 2. /home/piet/vault/03-Agents/_VAULT-INDEX.md (SSOT, nach update)
  - 3. /home/piet/vault/03-Agents/codex-future-plan-protocol.md (Governance)
  - 4. /home/piet/vault/03-Agents/end-of-day-2026-04-22.md (Kontext heute)
---

# Session-Handover für neue Claude Code Session

## Wer liest das

Du bist eine neue Claude Code Session (Windows-Laptop), die SSH-Zugriff auf den Homeserver hat. Hier ist der Kontext wo wir am Ende von 2026-04-22 stehen.

## Aktueller System-Status

```
/api/health: degraded (wegen 15 out-of-scope residue, akzeptiert)
Cron-reconciler: {"ok": true, "drift": []}
Registry-validate: exit 0
Memory-Orchestrator: rc=0 stable since 2026-04-22 13:35 UTC
Open Board-Tasks: 0
```

## Was heute passiert ist (TL;DR)

Sprint-M v1.2.1 **CLOSED** nach 5 Tagen. S-HEALTH 89.7% done. S-FND (Foundation) komplett deployed. Alle Drift-Issues geschlossen. Siehe `end-of-day-2026-04-22.md` für vollen Report.

## Aktive Arbeits-Tracks (keiner läuft autonom aktuell)

Board ist **ruhig**. Atlas hat alle dispatched-Tasks abgeschlossen. Kein pending-pickup, kein in-progress.

## Was als nächstes sinnvoll ist (priorisiert)

### P1 — Bereits im Discord dispatch-ready
Die Prompts sind in Channel `1495737862522405088` verfügbar (copy-paste an Atlas):

**A) S-RPT P0.1 Reader-Hygiene + P0.2a Pydantic-Integration** (Codex+Forge, ~2h autonom)
- Nutzt S-FND T1 Schema
- Consumer-Inventar vorhanden: `vault/03-Agents/task-governance-signals-consumers-2026-04-22.md`
- Plan: `vault/03-Agents/sprints/s-rpt-2026-04-22.md`

**B) S-GOV T8 OTEL-wrap 3 Crons** (Forge Quick-Win, ~30min)
- Infrastruktur läuft (Jaeger :16686, Collector :4317)
- Wrap worker-monitor, mc-watchdog, auto-pickup mit `otel-cron-wrap.sh`

### P2 — Neue Tracks (brauchen Plan+Dispatch-Decision)

**S-HEALTH-2 Residual Investigation** — 15 out-of-scope Items aus S-HEALTH Rest (draft-stale / missing-core-fields / open-fixture). Root-Cause-Investigation, nicht Blind-Fix.

**Gateway-OOM Follow-ups E1-E4** — Test-Design-Fix + Stale-Children-Cleanup + Drop-In-Drift. Operator-Decision: eigener Sprint oder ad-hoc?

### P3 — Queued Sprints (bereits Plan-Docs in Vault)
- `sprints/s-reliab-p0-2026-04-22.md` — F3/F5-F8 + P1.1/P1.3 + P2/P3 (Rest nach done T2/T7)
- `sprints/s-ux-2026-04-22.md` — Phase 2/3 (Pixel-Badge, Stale-Agent, Data-Confidence, SSE)
- `sprints/s-ctx-p0-2026-04-22.md` — CE2-CE10 (CE1 Baseline done)
- `sprints/s-infra-2026-04-22.md` — H6 L1/L3/L4'/L5, H7b Saga
- `sprints/s-integ-w1-2026-04-22.md` — Windows-SSHFS 7d Pre-Flight (separate Timeline)

## Vault-Struktur

```
/home/piet/vault/03-Agents/
├── _VAULT-INDEX.md                 # Master-Index (SSOT) — IMMER zuerst lesen
├── codex-future-plan-protocol.md   # Governance-Regeln für alle Agents
├── end-of-day-2026-04-22.md        # Heutige Details
├── session-handover-2026-04-22.md  # DU liest das gerade
├── sprints/
│   ├── s-fnd-2026-04-22.md         # ✅ DONE
│   ├── s-gov-2026-04-22.md         # ✅ CLOSED (Sprint-M)
│   ├── s-handbook-2026-04-21.md    # ✅ DONE (Codex)
│   ├── s-health-board-cleanup-2026-04-22.md  # 🟡 89.7% (T5 done, 15 residue)
│   ├── s-reliab-p0-2026-04-22.md   # 🟡 teilweise (T2/T7 done)
│   ├── s-rpt-2026-04-22.md         # ⏳ queued (dispatch-ready in Discord)
│   ├── s-ux-2026-04-22.md          # ⏳ queued (Phase 0 deployed)
│   ├── s-ctx-p0-2026-04-22.md      # ⏳ queued (CE1 done)
│   ├── s-infra-2026-04-22.md       # ⏳ queued
│   └── s-integ-w1-2026-04-22.md    # ⏸️ parked (7d Pre-Flight)
├── schemas/
│   └── sprint_outcome.py           # S-FND T1 Pydantic Schema-Template
├── archive/2026-04/                # 15 superseded Plan-Docs
└── [reports, RCAs, pre-work docs]
```

## Wichtige Konventionen

### Vault-Kanon
- **`/home/piet/vault/03-Agents/`** = Single Source of Truth
- **`/home/piet/.openclaw/workspace/vault/`** = Codex-Local-Mirror (nur read, nicht SSOT)

### Scope-Lock (hard rule)
- "Arbeite nur an Sprint X" = STOP nach X + Report, kein Weiterarbeiten
- Siehe `codex-future-plan-protocol.md`

### API-Calls für Board-Operations
- Base: `http://127.0.0.1:3000/api/...` (via `ssh homeserver`)
- Admin-close: **PATCH** (nicht POST), `actorKind: "human"`, `requestClass: "admin"`
- Move: **PUT** (nicht POST)
- Complete: **POST**
- Discord-Send: POST `/api/discord/send` mit `{channelId, message}`, header `x-request-class: admin`

### Discord-Channel
- Main coordination: `1495737862522405088`
- Atlas postet Reports dort
- Pro Message max **2000 Zeichen** (sonst truncate)

### Atlas-Tool-Limits
- `exec` mit `python3 script.py --arg` **nicht erlaubt** in manchen Pfaden
- **Workaround:** Shell-Wrapper-Scripts in `/home/piet/.openclaw/scripts/` (sind whitelisted)
- Bereits deployed: `cron-health-check.sh`, `memory-orch-check.sh`

### Neue Sprints erstellen
Pflicht-Frontmatter (siehe codex-future-plan-protocol.md §3):
```yaml
sprint-id: S-XXX
title: ...
created: YYYY-MM-DD
status: planned | running | done | superseded
priority: P0 | P1 | P2 | P3
owner: { role: agent, ... }
depends-on: [...]
enables: [...]
anti-goals: [...]
pre-flight-gates: [...]
```

## Pending Operator-Decisions

### Gateway-OOM E1-E4
Eigener Sprint oder ad-hoc-Cleanup? Empfehlung in `gateway-oom-rca-2026-04-22.md`.

### S-HEALTH 15 Residue
Als S-HEALTH-2 dispatched ODER weiter parken? 15 Items sind draft-stale, missing-core-fields, open-fixture.

### S-INTEG-W1 Start
Windows-SSHFS-7d-Pre-Flight-Fenster starten? Eigene Timeline, blockt keinen anderen Sprint.

## Anti-Patterns die heute aufgetreten sind (nicht wiederholen)

1. **Tool-Limits nicht antizipiert:** Atlas kann `python3 script.py --arg` nicht direkt → Wrapper-Scripts sind der Weg, nicht erzwungenes Runtime-Config-Debugging.
2. **Blind-Bulk-Fix bei unklaren Root-Causes:** Bei S-HEALTH 15 residue **nicht** pauschal patchen — erst kategorisieren, dann entscheiden.
3. **Composite-Key-Fields partial updaten:** registry.jsonl name+schedule müssen atomic — sonst Drift-ping-pong.
4. **Test im falschen cgroup:** Chaos-Test mit `systemd-run --scope` testet das Parent-cgroup nicht. Für Gateway-OOM-Test: kill -KILL oder cgroup.procs manipulation.
5. **Scope-Creep akzeptieren:** Wenn Agent "gerne mehr macht als bestellt" — dokumentieren als Lesson + Protocol-Update. Hier: Codex SH1→SH5 Scope-Creep.

## Wenn Du jetzt startest...

1. Read diese Datei komplett
2. Read `_VAULT-INDEX.md`
3. Read `codex-future-plan-protocol.md` (wenn Du Agents dispatched)
4. Check Discord-Channel für Operator-Ansagen seit 19:30 UTC (evtl. Updates über Nacht)
5. `curl http://127.0.0.1:3000/api/health` via SSH für aktuellen Live-State
6. Frag den Operator was heute der Fokus ist

## Sag dem Operator

Bei Session-Start ist eine gute Eröffnung:
> "Ich habe das Handover 2026-04-22 gelesen. Stand: Sprint-M closed, Board clean. Was möchtest Du als nächstes — S-RPT dispatch, S-HEALTH-2 planen, oder etwas anderes?"

## Letzter Commit des Tages

Sprint-M v1.2.1 formal closed. Check `_VAULT-INDEX.md` Status-Zeile Sprint-M = CLOSED mit Link zu `sprint-m-final-close-2026-04-22.md`.

---

**Kontakt-Channel:** Discord `1495737862522405088`
**Operator:** pieter_pan.13 (Lenard)
**Vault-SSOT:** `/home/piet/vault/03-Agents/`
**System-Handbook (Codex):** `/home/piet/.openclaw/workspace/docs/system/` (DIRECTORY.md, HUBS.md, AGENT_BOOTSTRAP.md)
