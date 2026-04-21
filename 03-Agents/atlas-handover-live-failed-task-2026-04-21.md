# Atlas Handover — Live Failed Recovery Case — 2026-04-21

## Aktueller verifizierter Zustand

- Mission Control Hardening ist live.
- Produktionsdienst neu gestartet und aktiv.
- `/api/health` ist weiter `degraded`, aber nur noch wegen **eines** echten unresolved Failed-Tasks.
- Live-Signale nach Fix:
  - `metrics.failed = 1`
  - `recoveryLoad = 1`
  - `attentionCount = 1`
  - `blocked = 0`
- Der verbleibende Task ist:
  - `b43472d9-d939-46d8-9981-d8fde9bb60af`
  - `[Sprint-M v1.2.1 M6b] Memory-Orchestrator Crontab-Mutation`
- Verifizierte Failure-Spur:
  - Dispatch: `2026-04-21T05:10:12.318Z`
  - erster `accepted`-Receipt: `2026-04-21T05:46:33.327Z`
  - kein terminaler Worker-Receipt
  - finaler Fail: `2026-04-21T06:21:47.233Z`
  - Reason: `worker runtime ended without terminal receipt (timeout/kill suspected)`

## Verbindliche Betriebsregeln fuer Atlas

1. Board-first: jede mutierende Aktion nur ueber kanonische Endpunkte.
2. Nach jedem mutierenden Call sofort `GET /api/tasks/{id}` verifizieren.
3. Kein Direkt-PATCH nach `in-progress` oder `active`.
4. Kein synthetisches Setzen von `workerSessionId`.
5. Kein synthetischer `accepted`-, `started`- oder `progress`-Receipt als Operator-Reparatur.
6. `failed`- oder `blocked`-Tasks nur ueber `POST /api/tasks/{id}/recovery-action` erneut anlaufen lassen.
7. `admin-close` nur verwenden, wenn prima facie bewiesen ist, dass der Task **kein** echter offener Recovery-Fall mehr ist.
8. Bei side-effectful Tasks mit Live-Mutationen niemals blind retriggern. Zuerst Side-Effects klassifizieren.

## Konkrete Handlungsempfehlung fuer den aktuellen Fall

Dieser Task ist **kein** bloes Metrics-Artefakt. Er wurde angenommen und ist danach ohne terminalen Receipt gestorben. Weil der Scope Live-Crontab und Registry mutiert, ist ein Blind-Retry unzulaessig.

Atlas soll deshalb in genau dieser Reihenfolge arbeiten:

1. Den aktuellen Live-Zustand klassifizieren.
   - Task-State lesen
   - `worker-runs.json` lesen
   - `board-events.jsonl` lesen
   - Live `crontab -l` lesen
   - `/home/piet/.openclaw/cron/registry.jsonl` lesen
   - vorhandene Backup-/Migration-Artefakte lesen
   - relevante Worker-/Cron-Logs um `2026-04-21T05:10Z` bis `2026-04-21T06:22Z` lesen

2. Den Fall in genau eine der drei Klassen einordnen.
   - **Klasse A — kein wirksamer Seiteneffekt:** keine relevante Crontab-/Registry-Mutation wurde angewendet
   - **Klasse B — partieller Seiteneffekt:** Teilmutation oder inkonsistenter Zwischenzustand
   - **Klasse C — Arbeit faktisch erledigt:** Mutation ist korrekt gelandet, nur der terminale Receipt fehlt

3. Nur die zur Klasse passende Aktion ausfuehren.
   - **A:** `recovery-action:retry`, danach GET-Verify auf `pending-pickup`
   - **B:** kein Retry; stattdessen enger Repair-/Rollback-Task oder sauberer Blocker mit RCA
   - **C:** kein Retry; stattdessen RCA dokumentieren, Task sauber abschliessen und nur noetige Follow-up-Task anlegen

4. Den Board-Zustand kanonisch halten.
   - Nie mit synthetischen Worker-Signalen "geradeziehen"
   - Nie aus Bequemlichkeit `failed -> done` patchen
   - Nie offene Side-Effects mit `admin-close` kaschieren

## Copy-Paste Prompt Fuer Atlas

```text
Atlas — uebernimm bitte den aktuellen Live-Recovery-Fall in Mission Control mit maximal enger, evidenzbasierter Betriebsfuehrung.

Kontext:
- Hardening fuer blocked/failed/pending-pickup ist live.
- /api/health ist nur noch wegen genau eines unresolved Failed-Tasks degraded.
- Live-Fail-Task:
  - taskId: b43472d9-d939-46d8-9981-d8fde9bb60af
  - title: [Sprint-M v1.2.1 M6b] Memory-Orchestrator Crontab-Mutation
- Verifizierte Timeline:
  - dispatch: 2026-04-21T05:10:12.318Z
  - accepted receipt: 2026-04-21T05:46:33.327Z
  - failedAt: 2026-04-21T06:21:47.233Z
  - blocker/failure reason: worker runtime ended without terminal receipt (timeout/kill suspected)
- Health-Signale jetzt:
  - metrics.failed=1
  - recoveryLoad=1
  - attentionCount=1
  - blocked=0

Verbindliche Regeln:
1. Board-first. Nur kanonische APIs verwenden.
2. Nach jedem Write sofort GET /api/tasks/{id} verifizieren.
3. Kein Direkt-PATCH nach in-progress/active.
4. Kein synthetisches workerSessionId.
5. Keine synthetischen accepted/started/progress Receipts als Operator-Reparatur.
6. failed/blocked nur ueber POST /api/tasks/{id}/recovery-action erneut anlaufen lassen.
7. admin-close nur, wenn prima facie bewiesen ist, dass kein echter offener Recovery-Fall mehr vorliegt.
8. Weil dieser Task Live-Crontab und Registry mutiert, ist Blind-Retry verboten.

Arbeitsauftrag:
1. Lies und belege zuerst:
   - GET /api/tasks/b43472d9-d939-46d8-9981-d8fde9bb60af
   - data/worker-runs.json fuer diese taskId
   - data/board-events.jsonl fuer diese taskId
   - live crontab -l
   - /home/piet/.openclaw/cron/registry.jsonl
   - vorhandene crontab backups / migration artefakte
   - relevante worker-/cron-logs zwischen 2026-04-21T05:10Z und 2026-04-21T06:22Z

2. Ordne den Fall exakt in eine Klasse ein:
   - Klasse A: kein wirksamer Seiteneffekt
   - Klasse B: partieller/inkonsistenter Seiteneffekt
   - Klasse C: Arbeit faktisch gelandet, nur terminaler Receipt fehlt

3. Fuehre nur die passende Aktion aus:
   - Klasse A: recovery-action retry und danach GET-Verify auf pending-pickup/dispatched/queued
   - Klasse B: kein Retry; stattdessen enger Repair-/Rollback-Plan oder Recovery-Task
   - Klasse C: kein Retry; saubere RCA, Follow-up falls noetig, dann kanonischer Close

4. Liefere die Antwort exakt in dieser Struktur:
   - ## Facts
   - ## Classification
   - ## Decision
   - ## Actions Executed
   - ## Verification
   - ## Remaining Risk

Wichtig:
- Keine allgemeine Review.
- Keine Nebenbaustellen.
- Keine Blind-Retries.
- Keine Board-Kosmetik ohne primaerquellenbasierte Klassifikation.
```

## Betriebsregeln-Check

Aktive, saubere Quellen nach dem heutigen Fix:

- Runtime-Enforcement in Mission Control:
  - `src/app/api/tasks/[id]/dispatch/route.ts`
  - `src/app/api/tasks/[id]/receipt/route.ts`
  - `src/app/api/tasks/[id]/recovery-action/route.ts`
  - `src/app/api/worker-pickups/route.ts`
  - `src/lib/operational-health.ts`
  - `src/lib/historical-failure-artifacts.ts`
- Worker-/Atlas-Prompts:
  - `scripts/worker-monitor.py`
- Kanonische Doku:
  - `vault/03-Agents/Shared/task-lifecycle-canon.md`

Nicht autoritativ, nur historisch:

- alte Sprint-Reports
- Postmortems
- `openclaw-config-backups/`
- archivierte Handoffs

Diese historischen Dateien duerfen fuer Kontext gelesen werden, aber nicht mehr als operative Wahrheit fuer den aktuellen Lifecycle-Vertrag.
