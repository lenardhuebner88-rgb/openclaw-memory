---
title: openclaw Update Plan 4.15 → 4.21 (gestaffelt)
date: 2026-04-22
status: DRAFT — awaits operator approval
author: Claude Code deep-analysis (2 research agents + web)
---

# openclaw Upgrade-Plan — 4.15 → 4.21

## IST-Zustand (verifiziert 2026-04-22 19:35 CEST)

| Item | Wert |
|---|---|
| Installed | `openclaw@2026.4.15` (seit 2026-04-18, dist re-patched 2026-04-21 20:11) |
| Registry latest | `2026.4.21` (6 stable-releases Rückstand) |
| Update-Checker meldet | `2026.4.11` — **CHECKER DEFEKT** (R12) |
| Lokale Patches | sessionkey-hotfix (21.04), PR68846 cherry-pick (19.04) |
| Lokale Wrapper | auto-pickup.py mit `x-request-class:admin` + 4 new env-vars |
| M7 Cron→systemd-Timer | Rollback armed (21.04 00:03), Completion unklar |
| Config-Schema | **1344 B Stub** — 13 top-level keys NICHT im Schema (auth, mcp, memory, session, skills, tools, channels, plugins, commands, bindings, messages, models, meta) |
| Config-Anomalie 22.04 18:14 | 17.4 KB precheck-snap (normal 29 KB) — **ungeklärt** |

## Nutzen-Score vs Pain-Points

**5 HIGH-DIRECT Fixes in 4.18-4.21:**
- **#69377** gateway config-patch guard → fixt genau den 25-min Outage-Muster vom 20.04
- **#69404** sessions maintenance entry-cap+age-prune at load → Gateway-OOM (17.04) root-fix
- **#65986** stale agent-scoped session reject → R50 Session-Lock-Governance
- **#69381** allowRequestSessionKey template-rendered gate → macht unseren SessionKey-Hotfix obsolet
- **#67886** gateway codex-ACP crash fix

**2 HIGH-STRATEGIC:**
- **#63105** cron `jobs-state.json` split (runtime vs git-tracked) — direkt für Sprint-K
- **openclaw doctor --fix** + `gateway/status` tri-split — könnte H9-H13 erledigen

**1 NO-FIX:**
- Taskboard-MCP reconnect (21.04 Incident) — nicht adressiert, eigene Arbeit nötig

## Top 3 Nightmare-Szenarien (Red-Team)

1. **Silent Patch Stripping** — Hashed-dist-chunks ändern Namen → sessionkey-patch-check-script findet `COPfBHma` nicht mehr → exit 0 silent → auto-pickup `--session-key` unknown-option → alle Agents idle → board-hygiene (R48) schließt als ghost-stalled → **6+ h silent-down**.
2. **Config-Schema-Lockout** — wenn neue Version `additionalProperties: false` enforced → **13 unknown keys** crashen config-load → Gateway restart-loop → `last-good`-config ist identisch invalid → manuelle Reduktion nötig.
3. **Discord Dual-Token-Split-Brain** — bundled channel setup/secret-contract vs. custom-bot → 2 Tokens an 3 Stellen (`.../Mb3BKg0` vs `.../AbAsgI`) → beide Bots antworten → Discord rate-limits → flap-loop → Operator verliert Mobile-Dispatch genau im Outage-Moment.

## Gestaffelter Upgrade-Plan

### Phase 0 — Pre-Flight-Hardening (VOR jedem npm-install)

**Blocking-Gates (alle müssen grün):**

1. **Dist-Tarball-Snapshot**:
```sh
tar czf /home/piet/.openclaw/backups/dist-pre-upgrade-$(date +%s).tgz   -C /home/piet/.npm-global/lib/node_modules/openclaw dist package.json CHANGELOG.md
```

2. **Sessionkey-Patch-Check-Script refactorn** auf marker-grep (nicht hardcoded `COPfBHma`):
```sh
# Pseudocode: TARGET=$(grep -rln 'agentViaGatewayCommand' dist/ | head -1)
```

3. **PR68846 Auto-Reapply-Hook** anlegen (analog sessionkey-patch.path) — watched `package.json`.

4. **Schema-Gate (R51-Kandidat)**: Diff neue-Version-Schema (aus Ziel-tarball) vs. unser `openclaw.json`. Wenn `additionalProperties: false` + unknown-keys → ABORT.

5. **Update-Checker reparieren** (R12) — sonst operator blind-flying.

6. **.env-Audit**: kein OPENCLAW_* in workspace-.env — ✅ bereits clean.

7. **Discord-Token-Triple konsolidieren** auf 1 Source-of-Truth VOR Phase 2.

8. **bin/openclaw-Symlink-Anomalie klären** (leer) — ggf. `npm rebuild openclaw`.

9. **7-Gate Pre-Flight-Sprint-Dispatch** (R-System existiert) laufen lassen.

10. **Config-Anomalie 22.04 18:14 root-causen** — was hat den 17KB-Shrink-Write ausgelöst?

### Phase 1 — 4.15 → 4.18 (Stability-Release)

- Gewinn: codex-ACP crash-fix, Telegram polling-leak, sqlite-vec dedup, Active Memory 120s ceiling
- Risk: **minimal** (1 Zwischen-Major)
- Commands:
```sh
systemctl --user stop openclaw-gateway openclaw-discord-bot openclaw-healthcheck.timer
systemctl --user stop openclaw-sessionkey-patch.path
npm -g install openclaw@2026.4.18
bash /home/piet/.openclaw/scripts/openclaw-sessionkey-patch-check.sh  # reapply
bash /home/piet/.openclaw/scripts/pr68846-reapply.sh  # NEU anlegen
systemctl --user start openclaw-healthcheck.timer openclaw-sessionkey-patch.path
systemctl --user start openclaw-gateway openclaw-discord-bot
```
- Monitor 48h: codex-crash-rate, gateway-logs, auto-pickup success

### Phase 2 — 4.18 → 4.20 (HIGH-IMPACT, HIGH-RISK)

- Gewinn: **4 unserer 5 HIGH-DIRECT Pain-Points gefixt**
- Risk: **moderat** — 2 Majors, channel-contract + schema-changes
- MANDATORY vor Start: Phase 1 stabil 48 h, Phase 0 Gates re-checken
- Zusätzlich:
  * Post-install: `openclaw doctor --fix` dry-run
  * Smoke-Test: manueller agent-turn via gateway mit `--session-key`
  * Discord `/health` Smoke
  * Cron `jobs-state.json` Migration (#63105) planen in separatem Step

### Phase 3 — 4.20 → 4.21 (Fix-only)

- Gewinn: owner-command fix (#69774), BlueBubbles Timeout, MINIMAX SSRF
- Risk: minimal

### No-Go Conditions (Abbruch + Rollback)

- Phase-1 codex/gateway crash-rate > baseline
- Config-load failure mit unknown-key-error
- sessionkey-patch reapply silent-fail
- auto-pickup Error-Rate > 5% über 10 min

### Rollback-Kommando

```sh
systemctl --user stop openclaw-gateway openclaw-discord-bot
npm -g install openclaw@2026.4.15
tar xzf /home/piet/.openclaw/backups/dist-pre-upgrade-<TS>.tgz   -C /home/piet/.npm-global/lib/node_modules/openclaw
cp /home/piet/.openclaw/backups/openclaw-config-guard/openclaw.json.last-good   /home/piet/.openclaw/openclaw.json
systemctl --user start openclaw-gateway openclaw-discord-bot
```

## Active Memory Plugin (parallel / optional)

- **Already available** seit 4.12 (bereits installiert, nicht aktiviert)
- **Komplementär** zu L1 (offline-KB) + L2 (graph) + qmd
- **Konflikt** mit L3 Retrieval-Feedback + L5 Budget-Meter → needs coordination
- **Empfehlung:** Aktivieren mit `mode:message` nach Phase 2, 7 Tage monitoring via L5+L3, promote zu `recent` nur bei messbarem Gain

## Priorisierung

| Item | Impact | Risk | Priorität |
|---|---|---|---|
| Phase 2 (4.20) — Outage-class + OOM + Session-lock fixes | 10 | 4 | **P0** |
| Phase 0 Pre-Flight-Hardening | 9 | 1 | **P0-Blocking** |
| Phase 1 (4.18) — codex-crash fix | 7 | 2 | **P1** |
| Cron jobs-state.json Migration | 6 | 3 | **P1** (Sprint-K) |
| Active Memory Experiment | 5 | 3 | **P2** |
| Phase 3 (4.21) | 4 | 1 | **P2** |
| Update-Checker Repair | 3 | 1 | **P1** (Pre-Req) |
| Taskboard-MCP reconnect | 5 | — | **NOT in scope** |

## Offene Fragen für Operator

1. **Grünes Licht** für gestaffelten Plan (Phase 1 → 48 h → Phase 2 → 48 h → Phase 3)?
2. **Wer führt** die npm-Installs aus — Atlas-Sprint oder manuell?
3. **Wann** soll Phase 1 starten? Empfehlung: nicht vor 23 UTC um Cron-Konflikte zu minimieren.
4. **Active Memory** experimentell testen? (Kein Muss für Upgrade-Pfad)
5. **Schema-Gate** als R51 in `feedback_system_rules.md` codieren?

---
**Referenzen:**
- `/home/piet/.npm-global/lib/node_modules/openclaw/CHANGELOG.md` (4.15-Linie)
- Registry: `npm view openclaw versions` (latest=4.21)
- `/home/piet/.openclaw/patches/openclaw-sessionkey.patch`
- `/home/piet/.openclaw/patches/PR68846-applied.md`
- `/home/piet/.openclaw/backups/openclaw-config-guard/`
- Memory: `session_2026-04-19_full_day.md`, Outage 2026-04-20 Morning-Report
