---
title: Mission Control
type: project
status: active
started: 2026-03-01
owner: { orchestrator: Atlas, ui: Pixel, backend: Forge }
tags: [type/project, status/active, topic/mission-control]
---

# Mission Control

> Operatives Cockpit für das Multi-Agent-System. Next.js-App auf `http://192.168.178.61:3000`.

## TL;DR

Mission Control (MC) ist die Web-UI für das gesamte Agent-Orchestration-System: Task-Board, Agent-Status, Heartbeats, Kosten, Pipelines. Atlas delegiert Operatives hierhin; Operator beobachtet hier. Läuft auf Homeserver Port 3000, Gateway auf 18789.

## Architektur (Kurz)

- **Frontend:** Next.js 15 (App Router), React, TailwindCSS, Zustand für State
- **Backend:** Next.js API-Routes + `/api/gateway` für Worker-Kommunikation
- **Live-Updates:** SSE via `/api/board/events`
- **Storage:** SQLite in `/home/piet/.openclaw/workspace/taskboard.sqlite`
- **Build:** `npm run build` (nicht `next build` direkt — Mission-Control-Wrapper)

## Aktueller Stand

- ✅ Cockpit live (Zone A-D: Heartbeat, NBA-Banner, Flow-Lanes, Agent-Load Sidebar)
- ✅ Costs-v2 (Budget-Engine, Burn-Rate, Discord-Alerts)
- ✅ Pending-Pickup Lifecycle (Smoke + Cron)
- ✅ Handoff-Block Pflichtfeld (POST /api/tasks)
- ⚠️ Mobile-Data-Validität teilweise offen (siehe [[mc-mobile-data-validitaet-2026-04-09]])

## Sub-Documents

| File | Inhalt |
|------|--------|
| [[mc-mobile-data-validitaet-2026-04-09]] | Audit der Mobile-Views (Dashboard/Agents/Tasks/Team/More) |
| [[dashboard-roadmap]] | ⚠️ Legacy (Finanzdashboard, gehört nicht hierhin — zu archivieren) |
| [[Mission-Control]] | Diese MOC |

## Aktive Workstreams

- [[04-Sprints/s-rpt-2026-04-22|S-RPT]] — Reporting-Pipeline
- [[04-Sprints/s-health-board-cleanup-2026-04-22|S-Health]] — Board-Cleanup
- [[04-Sprints/sprint-n-e2e-stabilization-2026-04-22|Sprint-N]] — E2E-Stabilization
- [[04-Sprints/atlas-morning-sprint-s-fnd-t1-2026-04-22|S-FND T1]] — Foundation Layer
- [[04-Sprints/sprint-i-mobile-polish-plan-2026-04-19|Sprint-I]] — Mobile-Polish (done)

## Relevante Incidents

- [[05-Incidents/gateway-oom-rca-2026-04-22|Gateway-OOM RCA]] 2026-04-22
- [[05-Incidents/context-overflow-fix-abschluss-2026-04-20|Context-Overflow-Fix]] 2026-04-20
- [[05-Incidents/rca-2026-04-19-incident-cluster|RCA Incident-Cluster]] 2026-04-19
- [[05-Incidents/forge-g1-broken-scheduler-fix-2026-04-19|G1 Scheduler-Fix]]

## Key References

- **Vault-Index:** [[_agents/_VAULT-INDEX]] — Plan-Status
- **Board-Hygiene:** [[10-KB/board-hygiene]]
- **Deploy-Contracts:** [[10-KB/deploy-contracts]]
- **Sprint-Orchestration-Pattern:** [[10-KB/sprint-orchestration]]
- **Atlas-Working-Context:** [[_agents/Atlas/working-context]]

## Endpoints (lokal)

| URL | Zweck |
|-----|-------|
| `http://192.168.178.61:3000` | Mission-Control-UI |
| `http://192.168.178.61:18789` | Gateway (Worker-API) |
| `/api/board/events` | SSE Live-Stream |
| `/api/board/next-action` | NBA-Banner |
| `/api/board/agent-load` | Agent-Slot-Utilization |
| `/api/tasks` | CRUD Board-Tasks |
| `/api/agents/concurrency` | Slot-Limits pro Agent |
| `/api/health` | Heartbeat-Strip |

## Operative Leitplanken (verbindlich)

- `groupPolicy = allowlist` für Discord + Telegram
- `exec.security = allowlist` für `main`, `sre-expert`, `sre-expert-fresh`
- Build nur per `npm run build` (kein direktes `next build`)
- Forge nicht blind als Wahrheitsquelle nutzen (R-Hallucination-Prevention)
- Keine parallelen Großbaustellen

## Roadmap (offen)

- [ ] Mobile-Data-Validität endgültig schließen (nach `mc-mobile-data-validitaet` Report)
- [ ] `dashboard-roadmap.md` archivieren (gehört nicht in MC-Projekt)
- [ ] Flash-Agent-Aktivierung (Decision pending)
- [ ] S-RPT + S-Health-Board-Cleanup Abschluss
- [ ] Observability-Dashboard (Phase-3)
