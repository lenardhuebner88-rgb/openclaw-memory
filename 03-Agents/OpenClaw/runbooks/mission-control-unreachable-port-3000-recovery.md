# Mission Control ist nicht erreichbar — Port 3000 Recovery

Status: active
Owner: Atlas / Forge
Scope: Kontrollierte Diagnose und Wiederherstellung, wenn Mission Control UI/API auf Port 3000 nicht erreichbar ist.
Anti-Scope: Keine Board-Hygiene, keine Task-Fachentscheidung, keine Gateway-/OpenClaw-Config-Änderung, kein Cron-/Secret-Eingriff.

## Ziel

Mission Control sicher wieder erreichbar machen, ohne parallele Builds/Restarts, Datenverlust oder falsche Board-Aussagen zu erzeugen.

## Grundregel

Wenn Port 3000 down ist: nicht raten, nicht mehrfach starten, nicht parallel restarten.

Reihenfolge:

1. Erreichbarkeit prüfen
2. Laufende Build-/Restart-Prozesse prüfen
3. Wenn bereits `mc-restart-safe` läuft: warten, nicht parallel starten
4. Wenn nichts läuft: Safe-Restart nutzen
5. Health/Board/Worker/Pickup-Proofs prüfen
6. Erst danach Board-Aussagen treffen

## Schnellcheck

```bash
curl -fsS -m 3 http://127.0.0.1:3000/api/health | jq
ss -ltnp '( sport = :3000 )'
pgrep -af 'mc-restart-safe|next|mission-control|node.*3000'
```

Interpretation:

- `curl` ok + Health ok: MC ist erreichbar; keine Recovery nötig.
- `curl` down + kein Listener auf 3000: MC ist nicht live.
- `mc-restart-safe` oder `next build` läuft: laufenden kontrollierten Pfad nicht stören.
- Listener vorhanden, Health aber fehlerhaft: Logs/Health prüfen, nicht blind neu starten.

## Degraded Mode

Wenn API/UI down ist, sind UI- und API-Aussagen nicht Board-Wahrheit.

Nur für Diagnose nutzen:

- `/home/piet/.openclaw/state/mission-control/data/tasks.json`
- `/home/piet/.openclaw/state/mission-control/data/worker-runs.json`
- `/home/piet/.openclaw/state/mission-control/data/board-events.jsonl`

Beispiel:

```bash
node - <<'NODE'
const fs=require('fs');
const p='/home/piet/.openclaw/state/mission-control/data/tasks.json';
const data=JSON.parse(fs.readFileSync(p,'utf8'));
const tasks=Array.isArray(data)?data:data.tasks;
const terminal=new Set(['done','canceled','failed']);
const open=tasks.filter(t=>!terminal.has(t.status));
console.log(JSON.stringify(open.map(t=>({id:t.id,title:t.title,status:t.status,dispatchState:t.dispatchState,executionState:t.executionState,updatedAt:t.updatedAt})),null,2));
NODE
```

Wichtig:

- Degraded reads sind nur Ersatzdiagnose.
- Keine Done-/Board-clean-Claims ohne späteren API-Proof.
- Live-Datei nur direkt ändern, wenn API-Transition legitimen Cleanup blockiert und vorher Backup erstellt wurde.

## Kontrollierter Restart-Pfad

Normaler Restart erfolgt über:

```bash
/home/piet/.openclaw/bin/mc-restart-safe <reason>
```

Wenn ein frischer Build nötig ist:

```bash
/home/piet/.openclaw/bin/mc-restart-safe --refresh-build 180 <reason>
```

Regeln:

- Nie `openclaw gateway restart` für Mission Control verwenden.
- Nie manuell `stop && start` als Restart-Ersatz.
- Nie zweiten `mc-restart-safe` parallel starten.
- Wenn Codex/Forge bereits an Pipeline/Build arbeitet: Atlas wartet und prüft nur read-only.

## Wenn ein Safe-Restart bereits läuft

Prüfen:

```bash
pgrep -af 'mc-restart-safe|next build'
ps -o pid,ppid,etime,stat,cmd -p <pid>
pstree -ap <pid>
ss -ltnp '( sport = :3000 )'
```

Dann:

- Wenn Build aktiv: warten.
- Wenn Prozess hängt: Owner fragen oder Forge/Codex-Prozesslage klären.
- Nicht killen, außer Operator fordert es ausdrücklich oder es ist klar ein Zombie ohne Child/Progress.

## Nach Restart: Pflicht-Proofs

```bash
curl -fsS http://127.0.0.1:3000/api/health | jq
curl -fsS http://127.0.0.1:3000/api/board-consistency | jq
curl -fsS 'http://127.0.0.1:3000/api/ops/worker-reconciler-proof?limit=20' | jq
curl -fsS 'http://127.0.0.1:3000/api/ops/pickup-proof?limit=20' | jq
```

Erwartung:

- Health `status=ok`
- Board `issueCount=0` oder klare bekannte Issues
- Dispatch `consistencyIssues=0`
- Execution `recoveryLoad=0` oder begründete bekannte Restlast
- Worker `openRuns=0` oder bekannte aktive Runs
- Pickup `pendingPickup=0`, `criticalFindings=0`

## Wenn Health degraded ist

Nicht sofort restarten. Erst Ursache lesen:

```bash
curl -fsS http://127.0.0.1:3000/api/health | jq '{status,severity,checks,metrics}'
curl -fsS http://127.0.0.1:3000/api/board-consistency | jq
```

Typische Ursachen:

- Board issue: Duplicate, stale draft, state mismatch
- Execution recoveryLoad: blocked/open worker state
- Dispatch consistency issue: dispatchState/worker-run mismatch
- Cost anomaly: separat prüfen, nicht Board-Fix nennen

Dann nur den konkreten Issue bearbeiten. Kein pauschaler Restart.

## Wenn Port 3000 nicht hochkommt

Checkliste:

1. Läuft Build noch?
2. Ist `.next`/Build erfolgreich vorhanden?
3. Gibt es Port-Konflikt?
4. Gibt es offensichtlichen Next/Node Crash?
5. Sind Mission-Control-Daten lesbar und JSON-valide?

Kommandos:

```bash
pgrep -af 'next|mission-control|node.*3000|mc-restart-safe'
ss -ltnp '( sport = :3000 )'
node -e "JSON.parse(require('fs').readFileSync('/home/piet/.openclaw/state/mission-control/data/tasks.json','utf8')); console.log('tasks-json-ok')"
find /home/piet/.openclaw/logs -maxdepth 2 -type f -printf '%TY-%Tm-%Td %TH:%TM %p\n' | sort | tail -30
```

Wenn weiter unklar:

- Forge/Codex übernehmen lassen.
- Atlas bleibt read-only und berichtet Evidenz.

## Harte Stopps

Sofort stoppen und berichten bei:

- parallelem Safe-Restart/Build droht
- unklarem Live-Lock oder aktivem Worker-Run-Konflikt
- Mission-Control-Daten JSON-invalid
- API und Live-Datei widersprechen sich nach Recovery
- Safe-Restart schlägt wiederholt fehl
- Änderung würde Gateway, Config, Secrets, Cron oder Modellrouting betreffen

Format:

```text
BLOCKED: <Grund> | evidence=<Pfad/Command> | proposed=<nächster sicherer Schritt>
```

## Kommunikation

Kurz und beweisorientiert:

- "Port 3000 down, kein Listener, Safe-Restart läuft bereits seit X Minuten im next build. Ich starte nichts parallel."
- "MC wieder live: health ok, board issueCount 0, recoveryLoad 0."
- "MC live, aber degraded wegen board duplicate X/Y; kein Restart nötig, Board-Hygiene nötig."

## Verwandte Runbooks

- `03-Agents/OpenClaw/runbooks/mission-control-board-hygiene-hermes.md`
