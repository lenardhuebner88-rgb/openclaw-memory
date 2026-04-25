# Recovery-Belegpfad — Operatives Runbook
**Task:** `2a5ccced-e1fe-4d0b-85d8-f6fdd89d5012`  
**Agent:** James  
**Date:** 2026-04-25  
**Parent:** `5c09bae1-6613-45c7-8329-165eb53697bf`  
**Scope:** Belege für Recovery/Finalize/Proof-Ablauf zusammenfassen

---

## Task-Status-Referenzen

Die drei angefragten Task-IDs (3b356588, 15afa83c, d8d77413) sind im aktuellen MC-Board nicht mehr auffindbar — vermutlich ältere Sessions oder bereits finalisiert. Die nachfolgenden Abläufe sind aus dem aktuellen Board-State und dem Recovery-Ledger vom 2026-04-23 bis 2026-04-24 abgeleitet.

**Aktuelle belastbare Referenz-Tasks (2026-04-23):**
- `5a6a6621-7d4b-4271-abc7-d18796f55ab9` — recovery-action retry → success
- `366c46e1-8790-443f-80cd-55c068bd3041` — recovery-action retry → success
- `2a886861-8ca4-4969-87b6-010dd469c507` — orphaned-dispatch-auto-fail → success (30min timeout)
- `75ad9efb-5598-4f2c-9709-f849af9f6a95` — orphaned-dispatch-auto-fail → success
- `848f7fc5-1d7a-41f1-95fe-f677597a8a10` — orphaned-dispatch-auto-reconcile → success

---

## Ablauf 1 — Finalize (Worker-End ohne Terminal-Receipt)

**Trigger:** Task hängt in `in-progress` mit `receiptStage=accepted|started`, aber Worker antwortet nicht mehr.

**Finalize-Route:** `POST /api/tasks/{id}/finalize`  
**Actor:** human, requestClass=admin|review

```
curl -X POST http://localhost:3000/api/tasks/{id}/finalize \
  -H "x-actor-kind: human" \
  -H "x-request-class: admin" \
  -H "Content-Type: application/json"
```

**Vorbedingungen:**
- `receiptStage` muss `accepted` oder `started` sein
- `receiptStage` = `result|blocked|failed` → bereits final, gibt `{finalized: false}` zurück

**Wirkung:** Task wird auf `status=done`, `executionState=done` gesetzt. Vault-Auto-Write wird ausgelöst. Recovery-Ledger wird nicht beschrieben (das ist finalize-spezifisch).

---

## Ablauf 2 — Orphaned Dispatch Auto-Fail (Worker-Accepted aber stirbt)

**Trigger:** `dispatchState=dispatched`, `executionState=queued`, Worker hat `accepted` receipt gesendet, aber kein `result` nach 30 min.

**Mechanismus:** `POST /api/tasks/{id}/recovery-action` mit `action=retry`

```
curl -X POST http://localhost:3000/api/tasks/{id}/recovery-action \
  -H "x-actor-kind: human|system" \
  -H "x-request-class: admin" \
  -H "Content-Type: application/json" \
  -d '{"action":"retry","taskId":"{id}","agentId":"{targetAgent}"}'
```

**Actor:** human, system, service | requestClass: admin, write

**Alternativ bei orphaned dispatch (kein Worker hat überhaupt acceptet):**
Route: `orphaned-dispatch-auto-fail` — erkennt `dispatched-without-worker-acceptance-timeout` und setzt den Task auf `failed`. Dauer: 30 min.

**Wirkung:** Neuer Dispatch wird ausgelöst. Recovery-Ledger: `kind=recovery-action`, `outcome=success`.

---

## Ablauf 3 — Board Hygiene (R48 Cron)

**Skript:** `/home/piet/.openclaw/scripts/r48-board-hygiene-cron.sh`  
**Cron:** `0 */1 * * *` (stündlich)

### Stale Drafts → admin-close
- `status=draft` + `age > 48h` → `PATCH /api/tasks/{id}/admin-close`
- actorKind: `system`, requestClass: `admin`
- Bedingung: `canceledReason=r48-stale-draft`
- **Ausnahme:** `autoSource=atlas-autonomy` + `operatorLock=true` → 168h (7 Tage)

### Failed ohne completedAt → nur Log
- `status=failed` + `completedAt=null` + `age > 24h` → nur Logeintrag, kein Auto-Modify

### Hygiene-Check (Proof/Hygiene)
```
GET /api/tasks?status=failed&executionState=done   → confirmation что failed mit terminal state
GET /api/tasks?status=draft                        → prüfen ob draft-Filter für Hygiene relevant
```

---

## Ablauf 4 — Meeting Finalize (Dry-Run → Execute)

**Skript:** `/home/piet/.openclaw/scripts/meeting-finalize.sh`

### Dry-Run (kein Execute)
```bash
./meeting-finalize.sh --meeting-id {id} --dry-run
# Output: finalize: dry-run ok meeting={id} mode={mode} file={path} missing={fehlende-signatures}
# Exit: 0 wenn alle Gates bestanden, 4 wenn geblockt
```

### Execute (nur nach Dry-Run bestanden)
```bash
./meeting-finalize.sh --meeting-id {id} --execute
# Wirkung: status → done, tracked-tokens aktualisiert, finalize-Note angehängt
```

### Gate-Checks je nach Modus
| Modus | Gate-Checks |
|---|---|
| debate | claude-bot sig + codex sig + lens sig (wenn beteiligt) + synthesis |
| review | codex sig + synthesis |
| council | atlas sig + claude-bot sig + lens sig + james sig + codex sig + synthesis |

---

## Ablauf 5 — Health-Check / Degraded Detection

**Trigger:** Health-Check erkennt `executionStatus=degraded` mit `attentionCount > 0`

**Recovery-Ledger-Eintrag:**
```json
{"kind":"degraded-operation","outcome":"detected|success","action":"health-check|execution-recovery-drift-watch","reason":"operational-health-degraded|execution-recovery-drift-recovered"}
```

**Recovery bei drift-recovered:** Automatic — vorher `executionStatus=degraded`, nachher `ok`. Kein manuelles Eingreifen nötig.

---

## Recovery-Ledger Referenz (2026-04-23/24 — Belege)

```json
// Orphaned dispatch → auto-fail (Worker gestartet, stirbt ohne result)
{"kind":"recovery-action","action":"orphaned-dispatch-auto-fail","outcome":"success","reason":"accepted-worker-missing-terminal-receipt-timeout","payload":{"timeoutMs":1800000}}

// Orphaned dispatch → auto-reconcile (kein Worker hat überhaupt acceptet)
{"kind":"recovery-action","action":"orphaned-dispatch-auto-reconcile","outcome":"success","reason":"dispatched-without-worker-acceptance-timeout"}

// Recovery drift watch → automatic recovery
{"kind":"degraded-operation","outcome":"success","action":"execution-recovery-drift-watch","reason":"execution-recovery-drift-recovered","payload":{"previous":{"executionStatus":"degraded"},"current":{"executionStatus":"ok"}}}
```

**Speicherort:** `/home/piet/.openclaw/workspace/mission-control/data/recovery-ledger.jsonl`

---

## Offene Punkte / Unschärfen

1. **Task-IDs 3b356588, 15afa83c, d8d77413** — nicht mehr im aktuellen Board auffindbar. Entweder bereits finalisiert oder aus älterer Session. Belastbare substitute: die Recovery-Ledger-Events vom 2026-04-23.

2. **`gemini-embedding-001`** — im Routing-Modell dokumentiert, aber in OpenRouter nicht auffindbar. Wahrscheinlich `text-embedding-004` oder `gemini-2.0-flash-001`. **Verifizierung steht aus.**

3. **Finalize mit workerSessionId** — finalize prüft `receiptStage` aber nicht ob `workerSessionId` noch aktiv ist. Edge-Case: Worker stirbt zwischen accept und progress.

---

*Zusammengestellt von James (agent), 2026-04-25. Keine Änderungen an Config/Code.*
