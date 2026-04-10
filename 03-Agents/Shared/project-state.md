# Project State

## Vault / Retrieval Stability
- Status: Consolidated (2026-04-10)
- Canonical vault root: `/home/piet/vault`
- Active shared context: `03-Agents/Shared/*` + `03-Agents/OpenClaw/operational-state.md`
- Hermes: decommissioned and moved to `06-Archive/2026-04/decommissioned/Hermes`
- Nested placeholder vault `Openclaw peter`: archived under `06-Archive/2026-04/decommissioned/Openclaw-peter-nested-vault`

## Home Server
- Status: Active
- Scope: OpenClaw + Immich host setup via Docker Compose (strict network separation)
- Notes: Hardware prepared; OpenClaw already running on Linux home server

## Phase 3 Self-Optimization
- Status: Sprint 1-3 completed (2026-04-08)
- Delivered: validator, health monitor, build integrity, auto-restart, DB CRUD/search/migration, model status + fallback alerts
- Next: continue quality loop and stabilize long-running workers

## Mission Control (Production)
- Status: Running in production mode via systemd on port 3000
- URL: http://192.168.178.61:3000
- Known issue: `next build` can fail due to OOM/SIGKILL in constrained env
- Mitigation: Build in frontend workspace, deploy artifacts

## Mission Control Mobile Phase 2
- Status: Task created and assigned
- Scope: bottom nav, full-screen modals, 44px touch targets, lane gestures

## Finance Dashboard
- Status: MVP done
- Remaining: design polish, optional portfolio/credit modules

## Claude Code Telegram Bridge
- Status: Stable in systemd user service
- Capabilities: model switching, health/status, agent/cron/task/log utilities
