---
agent: codex
date: 2026-04-26
status: active
scope: "Steps 1-3: autonomy follow-up, QMD 8181, cron/model cleanup"
operator: lenard
---

# Steps 1-3 Stabilisierung

## Ziel

Das vorherige Large Gate war im Kern gruen, aber funktional blockiert durch:

1. Atlas-Autonomy-Follow-up-Drafts waren noch nicht sauber genug gegated.
2. QMD CLI/Search war gesund, aber HTTP/MCP auf `127.0.0.1:8181` war nicht erreichbar.
3. Cron-/Heartbeat-Schicht enthielt mindestens einen aktiven obsoleten Noise-Job.
4. Modellrouting sollte explizit auf die Zielmatrix gezogen werden.

Zielbild fuer diesen Lauf: kleinste reversible Fixes, dann Sprint Gate 3 erneut pruefen.

## Live-Startdaten

- Mission Control: `/api/health` ok nach Deploy.
- Worker Proof: `openRuns=0`, `criticalIssues=0`.
- Pickup Proof: `pendingPickup=0`, `criticalFindings=0`.
- Modelle vor Fix: Atlas/main effektiv noch `openai-codex/gpt-5.4`; Forge/Lens/Pixel bereits wie Zielmatrix.
- QMD: `qmd status` gesund, `qmd search` funktioniert, Port `8181` nicht listening.
- Cron: `lens-cost-check.timer` aktiv, aber Service-Logs zeigen KeyError/JSONDecodeError und fachlich ueberholte OpenRouter-USD-Logik.

## Modellmatrix

| Rolle | OpenClaw Agent-ID | Zielmodell | Status |
|---|---:|---|---|
| Atlas | `main` | `openai-codex/gpt-5.5` | umgesetzt |
| Forge | `sre-expert` | `openai-codex/gpt-5.3-codex` | verifiziert |
| Lens | `efficiency-auditor` | `openai-codex/gpt-5.5` | verifiziert |
| Pixel | `frontend-guru` | `openai-codex/gpt-5.5` | verifiziert |

Backup: `/home/piet/.openclaw/backup/audit-2026-04-26/model-switch/openclaw.json.before-atlas-gpt55.bak`

## Schritt 1 - Auto-Follow-up/Approval-Guards

### Rootcause

`PATCH /api/tasks/:id` konnte `approvalClass` nicht sauber setzen, weil:

- `approvalClass` im PATCH-Body-Typ und in `allowedKeys` fehlte.
- Atlas-Autonomy-PATCH validierte nur unvollstaendig.
- `updateTask()` bekam viele `undefined`-Felder und konnte dadurch bestehende Felder wie `operatorLock`/`lockReason` leeren.

### Fix

- `src/app/api/tasks/[id]/route.ts`
  - `approvalClass` fuer PATCH erlaubt.
  - Atlas-Autonomy-PATCH erzwingt jetzt:
    - `approvalMode=operator`
    - valide `approvalClass`
    - valide `riskLevel`
    - `operatorLock=true`
    - `lockReason=atlas-autonomy-awaiting-approval`
  - PATCH-Payload filtert `undefined` vor `updateTask()`.

### Tests

- `npx vitest run tests/autonomy-draft-create-regression.test.ts tests/autonomy-approve-dispatch-regression.test.ts`
- `npm run typecheck`
- `npm run build`

Alle Gates bestanden.

### Live-Reparatur

Die zwei aktuellen `autoSource=atlas-autonomy` Test-Drafts wurden per PATCH mit `approvalClass=safe-read-only` repariert. Lock-Vertrag blieb erhalten.

## Schritt 2 - QMD 8181

### Rootcause

QMD selbst ist nicht kaputt:

- `qmd status` zeigt gesunden Index.
- `qmd search` funktioniert.
- OpenClaw nutzt im aktiven Config-Pfad QMD per stdio-MCP.

Das Problem lag in der HTTP-Expose-Schicht:

- `qmd mcp --http --daemon` meldet zwar `Started`, der Prozess ist danach aber sofort wieder weg.
- `qmd mcp --http --port 8181` laeuft im Vordergrund stabil.
- Der vorhandene `mcp-qmd-reaper.sh` hat bereits eine Ausnahme fuer einen gepinnten HTTP-Daemon auf 8181.

### Fix

Neuer User-Service:

- `/home/piet/.config/systemd/user/qmd-mcp-http.service`
- `ExecStart=/home/piet/.local/lib/node_modules/@tobilu/qmd/qmd mcp --http --port 8181`
- `Restart=on-failure`
- aktiviert mit `systemctl --user enable --now qmd-mcp-http.service`

### Verify

- `systemctl --user is-enabled qmd-mcp-http.service` -> `enabled`
- `systemctl --user is-active qmd-mcp-http.service` -> `active`
- `curl http://127.0.0.1:8181/health` -> `{"status":"ok",...}`
- `DRY_RUN=1 mcp-qmd-reaper.sh` -> `orphans=0 alive=1 keep=1 kills=0`

Rollback:

```bash
systemctl --user disable --now qmd-mcp-http.service
rm -f /home/piet/.config/systemd/user/qmd-mcp-http.service
systemctl --user daemon-reload
```

## Schritt 3 - Cron-/Heartbeat-Cleanup

### Rootcause

`lens-cost-check.timer` war aktiv, aber:

- `lens-cost-check.service` lief am 2026-04-24 und 2026-04-25 mit `KeyError: 'openrouter:default'`.
- Danach folgten `JSONDecodeError` und `ValueError`, trotzdem endete der Service mit Erfolg.
- Inhaltlich ist der Job ueberholt, weil Lens/MiniMax als Tokenplan/Kontingent und nicht als pauschaler USD-Kostenalarm behandelt werden soll.

### Fix

- Backup:
  - `/home/piet/.openclaw/backup/audit-2026-04-26/cron-cleanup/lens-cost-check.timer.bak`
  - `/home/piet/.openclaw/backup/audit-2026-04-26/cron-cleanup/lens-cost-check.service.bak`
- `systemctl --user disable --now lens-cost-check.timer`

### Verify

- `systemctl --user is-enabled lens-cost-check.timer` -> `disabled`
- `systemctl --user is-active lens-cost-check.timer` -> `inactive`

Bewusst nicht geaendert:

- Doppelte Session-Size-Guards bleiben vorerst, weil sie unterschiedliche Frequenzen/Modi bedienen.
- Alte kommentierte Cron-Stubs bleiben als Historie.
- Keine neuen Cron-Jobs.

## Gate fuer Weiterlauf

Sprint Gate 3 wird erst nach diesen Probes erneut gestartet:

- `/api/health`
- `/api/ops/worker-reconciler-proof?limit=20`
- `/api/ops/pickup-proof?limit=20`
- `curl http://127.0.0.1:8181/health`
- `systemctl --user is-active mission-control.service qmd-mcp-http.service`

## Sprint Gate 3 Recheck

Gate-Task:

- `77653831-3002-4522-994f-57945ccd90e0`
- Titel: `[Gate 3][Atlas] Recheck autonomy after Codex fixes`
- Worker: Atlas/main
- Ergebnis: `done`

Atlas-Verdict:

- `PASS-WITH-FOLLOW-UP`
- Keine harten Gate-3-Blocker mehr.
- Gruen genug fuer genau einen kontrollierten Atlas-Autonomy-Sprint.
- Nicht gruEN genug fuer breite Auto-Dispatch-Oeffnung oder Fanout.

Atlas-Live-Proofs:

- `/api/health`: `ok`
- Worker Proof: `openRuns=0`, `criticalIssues=0`
- Pickup Proof: `pendingPickup=0`, `criticalFindings=0`
- QMD CLI: gesund
- QMD HTTP 8181: `ok`
- Modelle: Atlas `gpt-5.5`, Forge `gpt-5.3-codex`, Lens `gpt-5.5`, Pixel `gpt-5.5`
- `autoSource=atlas-autonomy` Drafts: 2 vorhanden, beide operator-gated mit `approvalMode=operator`, `approvalClass=safe-read-only`, `riskLevel=low`, `operatorLock=true`, `lockReason=atlas-autonomy-awaiting-approval`

Naechster einzelner Autonomy-Schritt laut Atlas:

- Genau einen operator-gated Follow-up-Draft aus dem naechsten approved Atlas-Finding erstellen.
- Danach Approval-Metadaten, Lock-Vertrag und keine-Fanout-Regel verifizieren.
- Dann stoppen.

## Abschluss-Probes 2026-04-26T14:56Z

- `/api/health`: `status=ok`, `severity=ok`
- Worker Proof: `tasks=656`, `runs=630`, `openRuns=0`, `issues=0`, `criticalIssues=0`
- Pickup Proof: `pendingPickup=0`, `openPlaceholderRuns=0`, `activeSpawnLocks=0`, `activeSessionLocks=0`, `criticalFindings=0`
- `qmd-mcp-http.service`: `active`
- `mission-control.service`: `active`
- `curl http://127.0.0.1:8181/health`: `status=ok`
- `mcp-qmd-reaper`: echter Cronlauf respektiert QMD HTTP-Daemon; `alive=1`, `kills=0` fuer den Daemon.

## Offene Rest-Risiken

- `qmd mcp --http --daemon` selbst ist weiterhin buggy; der User-Service umgeht das stabil. Spaeter kann upstream/Package-Code repariert werden.
- `gateway-port-guard.sh` bleibt ein Script-Health-Noise-Kandidat, weil der Endpoint ein fehlendes Log als dead bewertet; das ist nicht Teil dieses Small-Fix-Schritts.
- Autonome Follow-up-Erzeugung bleibt absichtlich operator-gated; Auto-Dispatch darf erst nach einem sauberen Atlas-Gate geoeffnet werden.
