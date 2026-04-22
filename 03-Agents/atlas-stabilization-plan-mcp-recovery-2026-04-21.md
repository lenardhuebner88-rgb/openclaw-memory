# Atlas Stabilization Plan — MCP-Transport-Recovery & Gateway-OOM-Härtung

**Datum:** 2026-04-21
**Autor:** Atlas (Main-Session Discord)
**Status:** Draft zum Review
**Review durch:** Codex Terminal
**Scope:** Atlas konnte um 12:05 UTC Tasks nicht übers Taskboard-MCP einsteuern (`taskboard__* failed: Not connected`). Plan beschreibt stufenweise Stabilisierung, ohne openclaw-Fork und ohne Mission-Control-Release.

---

## 1. Root Cause (verifiziert)

Atlas' Session (gestartet 2026-04-21 09:29:38 auf Discord) hat zwischen 09:29 und 12:05 einen Gateway-OOM-Kill bei 11:04:12 überlebt, aber nicht ihre MCP-stdio-Verbindung zum `taskboard`-Server.

**Mechanik:**
1. `/home/piet/.openclaw/mcp-servers/taskboard/server.js` läuft als Child des Gateway-Prozesses (ppid=openclaw-gateway). Gateway-Exit killt den Subprocess mit.
2. Session-lokale Bundle-MCP-Runtime (`dist/pi-bundle-mcp-tools-vusm-AE2.js` → `createSessionMcpRuntime`, Z. 350–485) cached `Client`-Objekt + Catalog für die Session-Lebenszeit.
3. **Kein Recovery-Pfad:** weder `onclose`/`onerror`-Listener noch try/catch in `callTool` (Z. 462) invalidiert die cached `sessions.get(serverName)`.
4. Nach Child-Tod ist `client._transport === null` → MCP-SDK wirft in `shared/protocol.js:624` direkt `new Error('Not connected')`. Für immer, bis Session neu startet.

**Gateway-OOM-Kadenz heute (3×):** 06:35, 08:25, 11:04 — Peak 6.8 GB RSS + 774 MB Swap.

**HTTP-Backend gesund:** `curl http://127.0.0.1:3000/api/tasks` → 200 OK. Nur der MCP-Bridge-Client ist tot.

## 2. Ist-Stand-Scaffold (bereits vorhanden)

| Komponente | Stand |
|---|---|
| `/home/piet/.openclaw/scripts/mcp-taskboard-reaper.sh` | Cron `*/15`, `MCP_REAP_CAP=3`, `MAX_AGE=3600s`. Prunt alte Stdio-Children, invalidiert aber keine Session-Client-Caches. |
| `openclaw-gateway.service` | `MemoryMax=7 GB (7340032000)`, `OOMPolicy=stop`, `MemoryHigh=infinity` → kein Soft-Throttle, Kernel schlägt Hard-OOM zu |
| `session-freeze-watcher.sh` | Aktiv, begrenzt Session-State-Blowup |
| `health-monitor` | Gateway-Ping alle 5 min; trackt keine MCP-Child-Counts |

## 3. Plan — gestuft

### P0 — Heute (Minuten, Task-Flow wiederherstellen)

| # | Aktion | Deliverable | Aufwand |
|---|---|---|---|
| 0.1 | Atlas-Session neu starten in Discord (`/new`) | Task-Routing sofort offen | 1 Min |
| 0.2 | `callTool` try/catch-Wrapper in `pi-bundle-mcp-tools-vusm-AE2.js` Z. 462 → bei `Not connected`/`Connection closed` `sessions.delete(serverName)` + `catalog=null` + `disposeSession(session)` | Pre-Crash-Sessions heilen sich nach 1. Fail selbst (2. Call re-init via `getCatalog()`) | 30 Min inkl. Test |
| 0.3 | `/home/piet/.openclaw/scripts/apply-mcp-recovery-patch.sh` + systemd `ExecStartPre` Drop-in | Patch überlebt npm-Update, idempotent via Marker-Grep | 15 Min |

**DoD:** `pkill -f taskboard/server.js` → Atlas' nächster Tool-Call schlägt 1× fehl, zweiter succeedet.

### P1 — Diese Woche (OOM-Kadenz dämpfen)

| # | Aktion | Warum |
|---|---|---|
| 1.1 | `MemoryHigh=3G`, `MemoryMax=4G` (von 7G runter) | Kernel throttled weich, früher Restart bei 4 GB statt 6.8 GB Hard-OOM |
| 1.2 | Reaper `*/15` → `*/5`, `MAX_AGE_SECONDS=1800` | Zombie-Children früher eingefangen |
| 1.3 | Session-Fingerprint in `getSessionMcpRuntimeManager().getOrCreate()` um Gateway-Boot-PID erweitern | Belt-and-suspenders zum P0: Gateway-Restart disposed **aktiv** alle Pre-Crash-Runtimes |
| 1.4 | `ExecStopPost=pkill -f 'mcp-servers/.+/server.js|@tobilu/qmd/src/qmd.ts mcp'` in Gateway-Unit (Drop-in `mcp-child-teardown.conf`) **[DEPLOYED 2026-04-21 12:42]** | Saubere Child-Teardown für taskboard UND qmd vor Restart |
| 1.5 | `mcp-qmd-reaper.sh` analog taskboard-reaper, Cron `*/5`, CAP=3, Orphan-Kill (ppid nicht openclaw-gateway/agent) **[DEPLOYED 2026-04-21 12:40]** | QMD-Stdio-Children akkumulieren bei ~1 neuer Proc pro 5 min, bis zu 26 Procs / 2.35 GB RSS beobachtet. Kein Recovery im Gateway. Analog-Pattern zu taskboard. |

**DoD:** Provozierter OOM (`systemd-run --user --scope -p MemoryMax=100M …`) → sauberer Restart, kein Child-Zombie in `ps auxf`.

### P2 — Nächste Woche (OOM-Root diagnostizieren)

| # | Aktion | Warum |
|---|---|---|
| 2.1 | `NODE_OPTIONS=--heapsnapshot-signal=SIGUSR2` in Gateway-Env | `kill -USR2 PID` dumpt Heap ohne Restart |
| 2.2 | Cron `*/30`: `ps -o rss` des Gateways in `workspace/logs/gateway-mem.log` | Leak-Rate messbar (MB/h) |
| 2.3 | Auto-Heap-Dump bei RSS ≥ 4 GB via Shell-Hook | Dump an der Schwelle, analysierbar in Chrome DevTools |
| 2.4 | Analyse-Sprint: 2–3 Heap-Dumps, Retainer-Set isolieren | Vault-Report benennt Leak-Kandidat (History? MCP-Subprocess-Cache? Sidecars?) |
| 2.5 | Health-Monitor erweitern: `mcp-child-count`, `runtime-manager-size` | Frühwarnung vor OOM statt Killer-Alarm |

**DoD:** Vault-Report mit konkretem Retainer + P3-Fix-Kandidat.

### P3 — Sprint-Ebene (nachhaltige Härtung)

| # | Aktion |
|---|---|
| 3.1 | Upstream-PR in openclaw: `callTool` + Runtime-Manager-Fingerprint → entfernt lokalen Patch |
| 3.2 | **R51 (neue Regel):** MCP-Tool-Fail mit `Not connected`/`Connection closed` ⇒ zuerst Gateway-Restart-History (`journalctl --user -u openclaw-gateway | grep -iE 'oom\|killed\|restart'`) vs. Session-Start-Time prüfen. Kein Fix-Versuch am Tool oder Backend bevor diese Korrelation ausgeschlossen ist. |
| 3.3 | **R52 (neue Regel):** Gateway-Restart heilt keine Session-MCP-Runtimes. Bei Pre-Crash-Sessions: Session-Neustart oder warten auf lazy-recovery nach erstem Fail. |
| 3.4 | **Heartbeat-Kanal reparieren** (separater Codex-Befund, nicht ursächlich für heutigen Incident): `heartbeat/atlas/route.ts` ruft `recordHeartbeat('main')`; Cron `* * * * *` POST → `/api/heartbeat/main`. Verhindert dass echter Atlas-Down-Fall als False-Alarm abgetan wird. |
| 3.5 | Session-Split-Schwelle im `session-freeze-watcher.sh` prüfen/senken — langlebige Discord-Sessions sind selbst OOM-Treiber (Chat-State-Akkumulation). |

**DoD:** R51/R52 in `feedback_system_rules.md`, Upstream-PR mergebereit, Heartbeat-Kanal zeigt Atlas live korrekt.

## 4. Abhängigkeiten

```
P0-Patch (callTool-Recovery) [MUSS heute]
   ├── P1.3 Session-Fingerprint [belt-and-suspenders, parallelisierbar]
   └── P2.* Heap-Profiling [Gateway lebt länger ohne Crash → Leak sichtbar]
         └── P3.1 Upstream-PR [Heap-Dump als Beweis für Maintainer]

Parallelisierbar ohne Blocker: P1.1 / 1.2 / 1.4, P3.2 / 3.3 / 3.4 / 3.5
```

## 5. Fortschrittstracking

| Meilenstein | Metrik |
|---|---|
| P0 | Atlas self-recovert nach provoziertem Child-Kill |
| P1 | Gateway-OOM-Count `journalctl --since -7d | grep oom-kill | wc -l` von 3/Tag → ≤ 1/Tag |
| P2 | Heap-Dump zeigt konkreten Retainer |
| P3 | Upstream-PR gemerged ⇒ lokales Patch-Script gelöscht; R51/R52 committet |

## 6. Nicht im Plan (bewusst out-of-scope)

- **Taskboard-HTTP-API-Hardening:** Backend ist gesund, nicht betroffen.
- **Agent-Migration weg von Discord:** langlebige Sessions sind Treiber, aber Discord-Abhängigkeit ist strategische Entscheidung außerhalb dieses Plans.
- **MCP-Transport-Wechsel stdio → HTTP:** löst zwar Child-Process-Kopplung ans Gateway, aber eigener Sprint (R-Layer-Änderung).

## 7. Codex-Analyse (Heartbeat-Befund) — Einordnung

Codex hat parallel den stale Heartbeat-Store-Kanal diagnostiziert (`.openclaw/heartbeat/agents.json` nicht nachgeführt, `heartbeat/atlas/route.ts` No-Op, Mission-Control-Team-Tab zeigt Atlas fälschlich "down"). **Befund ist korrekt, aber kein Verursacher des 12:05-Incidents.** Atlas' Fehler stammt aus MCP-SDK-Tool-Dispatch (`[tools] taskboard__* failed: Not connected`), nicht aus UI-Panel-Logik. Beide Bugs sind disjoint. Heartbeat-Fix aufgenommen als P3.4.

## 8. Referenzen

- Incident-Memory: `C:\Users\Lenar\.claude\projects\C--Users-Lenar-Neuer-Ordner\memory\incident_taskboard_mcp_not_connected_2026-04-21.md`
- MCP-Client-Throw-Site: `node_modules/@modelcontextprotocol/sdk/dist/cjs/shared/protocol.js:624`
- Bundle-MCP-Runtime: `/home/piet/.npm-global/lib/node_modules/openclaw/dist/pi-bundle-mcp-tools-vusm-AE2.js:350–485`
- Reaper: `/home/piet/.openclaw/scripts/mcp-taskboard-reaper.sh`
- Gateway-Unit: `~/.config/systemd/user/openclaw-gateway.service` + `.d/`-Drop-ins
- Heartbeat-Store: `/home/piet/.openclaw/heartbeat/agents.json`
- Atlas-Heartbeat-Route (No-Op): `/home/piet/.openclaw/workspace/mission-control/src/app/api/heartbeat/atlas/route.ts`
