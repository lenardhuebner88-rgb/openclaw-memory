---
title: Gateway OOM-Recovery RCA (T8 Chaos-Test Investigation)
date: 2026-04-22
author: Claude Code (remote RCA) + Operator verification
task-ref: 1cabca33-5d18-477a-8225-791c7c847025 ([Forge] Analyse: Gateway OOM-Erkennung und Recovery-Verhalten)
related: S-RELIAB-P0 T8 Chaos-Test-Failure
severity: resolved — no gateway bug, test design flaw
---

# Gateway OOM-Recovery RCA — Ergebnis

## Kernbefund

**Gateway-Recovery funktioniert korrekt.** Der T8 Chaos-Test hat fälschlicherweise "Gateway restartete nicht" gemeldet, weil stress-ng in einem **isolierten systemd-run scope-cgroup** lief, nicht im Gateway-cgroup. Das Gateway bekam den Stress-Test nie zu spüren.

## Evidence: Gateway restartet sauber bei echten OOMs

Aus `journalctl --user-unit=openclaw-gateway.service` (letzte 24h):

```
Apr 22 08:59:20  ✗ Failed with result 'oom-kill'      ← ECHTER OOM
Apr 22 08:59:50  ✓ Started  (30s — RestartSec=30)
Apr 22 09:00:22  ✗ Failed with result 'signal'
Apr 22 09:00:23  ✓ Started
Apr 22 14:41:17  ✗ Failed with result 'signal'
Apr 22 14:41:47  ✓ Started
Apr 22 14:42:43  ✗ Failed with result 'signal'
Apr 22 14:42:44  ✓ Started
```

4 Restart-Zyklen in 24h, alle systemd-driven, alle erfolgreich. `Restart=always` + `OOMPolicy=stop` funktionieren einwandfrei.

## Test-Design-Fehler in T8

Im `/home/piet/.openclaw/workspace/logs/chaos-test.log`:
```
Triggering OOM via Python memory allocation in scoped cgroup...
Gateway health after OOM: 1, old_pid=531579, new_pid=531579   ← PID gleich
```

Der Test triggert OOM **"in scoped cgroup"** (`systemd-run --scope`). Das ist ein separates temporäres cgroup unterhalb `user.slice`. stress-ng wird dort vom Kernel gekillt, aber das Gateway läuft in seinem eigenen cgroup (`.../app.slice/openclaw-gateway.service`) und bleibt davon unberührt.

## Systemd-Konfiguration (alles korrekt)

| Setting | Wert | Check |
|---|---|---|
| `Restart` | `always` | ✅ |
| `RestartSec` | `30s` (restart-policy.conf) | ✅ |
| `OOMPolicy` | `stop` | ✅ Setzt Unit auf stopped, dann triggert Restart |
| `OOMScoreAdjust` | `200` | ✅ Gateway bevorzugt gekillt bei Host-OOM |
| `MemoryMax` | `4G` (memory-tiering.conf) | ✅ |
| `MemoryHigh` | `3G` | ✅ Soft-Limit |
| `MemorySwapMax` | `0` | ✅ Kein swap |
| `StartLimitBurst` | 5 in 120s | ✅ Crash-Loop-Protection |
| `KillMode` | `control-group` | ✅ Inkl. Children |

6 Drop-Ins aktiv: `bonjour-disable`, `mcp-child-teardown`, `memory-hardening-2026-04-17`, `memory-tiering`, `port-guard`, `restart-policy`.

## Sekundär-Befunde

### Stale Children im Gateway-cgroup (7 Stück)
```
531579 openclaw-gateway (main)
583969 sudo apt install -y stress-ng  ← stale (PAM-auth fail residue)
584337 sudo apt install -y stress-ng  ← stale
588599 sudo apt install -y stress-ng  ← stale
587046 node .../taskboard/server.js   ← stale MCP
595442 node .../taskboard/server.js   ← stale MCP
603556 node .../taskboard/server.js   ← stale MCP
606956 node .../taskboard/server.js   ← stale MCP
```

### Drop-In-Drift
`memory-hardening-2026-04-17.conf` ist superseded by `memory-tiering.conf`. Systemd nimmt alphabetisch letzten → `memory-tiering.conf` gewinnt (`MemoryMax=4G`). Funktionell OK, aber Config-Drift.

## Empfehlungen

| ID | Priorität | Action |
|---|---|---|
| **E1** | P1 | T8 Test-Design fix: stress-ng im Gateway-cgroup ODER `kill -KILL $MainPID` als echter Resilienz-Beweis |
| **E2** | P2 | Stale children cleanup: 3× sudo-stress-ng Zombies + 4× taskboard-MCP-node Kinder. Pattern: `pkill -9 -f "sudo apt install -y stress-ng"` + mcp-reaper-Run |
| **E3** | P3 | Drop-in-Drift: `rm memory-hardening-2026-04-17.conf` + `systemctl --user daemon-reload` |
| **E4** | P1 | Re-Test Variante A (kill -KILL) als echten Resilienz-Beweis |

## Task-Completion-Payload

```
EXECUTION_STATUS: DONE

RESULT_SUMMARY:
Gateway-OOM-Recovery funktioniert korrekt. Restart=always + OOMPolicy=stop + RestartSec=30 sind aktiv und haben in den letzten 24h 4× sauber restartet (journalctl 08:59:20/09:00:22/14:41:17/14:42:43 UTC). T8-Test hat fälschlicherweise Gateway-PID als "gleich" gemessen, weil stress-ng in isoliertem scoped-cgroup lief (nicht im Gateway-cgroup) — das Gateway bekam den Test nie zu spüren. Problem liegt im Test-Design, nicht in Gateway-Resilienz.

EVIDENCE:
- systemd: Restart=always, RestartSec=30, OOMPolicy=stop, MemoryMax=4G via `systemctl --user show`
- journalctl: 4 Restart-Zyklen in 24h, alle <60s recovery
- Test-Log zeigt "Triggering OOM via Python memory allocation in scoped cgroup" — Isolations-Problem
- cgroup-Inspect: Gateway-cgroup war nie unter MemoryMax-Pressure während T8

RECOMMENDATIONS:
E1 (P1): T8 Test-Design fix — kill -KILL $MainPID ODER stress-ng im Gateway-cgroup
E2 (P2): Stale children cleanup — 7 Zombies/stale MCP-Kinder entfernen
E3 (P3): Drop-In-Drift — memory-hardening-2026-04-17.conf löschen
E4 (P1): Re-Test mit Variante A (kill -KILL)

BLOCKER: none
```

## Cross-References

- Chaos-Test-Log: `/home/piet/.openclaw/workspace/logs/chaos-test.log`
- Systemd-Unit: `/home/piet/.config/systemd/user/openclaw-gateway.service` + 6 drop-ins
- Sprint: S-RELIAB-P0 T8 (sprints/s-reliab-p0-2026-04-22.md)
