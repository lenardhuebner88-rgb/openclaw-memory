---
status: active
owner: codex
created: 2026-04-25T05:59:49Z
scope:
  - worker-hardening
  - meeting-review-hardening
  - phase-c-codex-path
  - 2h-active-monitoring
---

# 2h Meeting/Worker Hardening + Phase C Plan

## Ziel
Die naechsten zwei Stunden werden aktiv begleitet:
- Worker-System ruhig halten.
- Meeting-/Debate-/Review-Pfad praktisch pruefen.
- Phase C als sicherer Codex-Beitragspfad vorbereiten.
- Alle 15 Minuten Status in Discord `1495737862522405088`.

## Ausgangslage
- `mission-control.service`: active.
- `openclaw-discord-bot.service`: active.
- Worker-Proof Baseline: `ok`, `criticalIssues=0`, `openRuns=0`.
- Keine running Meetings.
- Zwei queued Debates:
  - `2026-04-25_0451_debate_meeting-council-safe-mode`
  - `2026-04-25_0452_debate_phase4-readiness-gates`

## Phase C Scope
Phase C bedeutet: Codex-Beitragspfad auf dem Homeserver vorbereiten.

Erlaubt in diesem Lauf:
- `spawn-codex-meeting.sh` als dry-run-first Helper.
- Konkreter Prompt/Command-Vorschlag fuer Codex-Beitrag.
- Lock-, Timeout-, Budget- und Statuschecks.
- Integration in Statusposter als naechste Aktion.

Nicht erlaubt in diesem Lauf:
- Kein Cron.
- Kein dauerhafter Codex-Daemon.
- Kein automatischer rekursiver Codex-Spawn aus dem Runner.
- Kein Force-Execute ohne separates explizites Enable-Flag.

## Umsetzungsschritte
1. Live-Monitor Baseline posten.
2. `spawn-codex-meeting.sh` bauen:
   - Default `--dry-run`.
   - `--meeting-id <id>` Pflicht.
   - Erkennt Meeting-Datei, Modus, Status, Budget, fehlende Signaturen.
   - Gibt Codex-Prompt und optionalen `codex exec` Vorschlag aus.
   - `--execute` nur mit `CODEX_MEETING_PHASE_C_ENABLED=1`; sonst verweigern.
3. Statusposter erweitern:
   - Bei fehlendem Codex-Beitrag Phase-C Helper nennen.
   - Weiterhin read-only.
4. Runner-Text aktualisieren:
   - Codex-Pfad = Phase C helper/manual until explicit execute enable.
5. Gates:
   - `bash -n` fuer alle Meeting-Scripts.
   - `meeting-status-post.sh` auf queued und done Meeting.
   - `spawn-codex-meeting.sh --dry-run` auf queued/running/done Meeting.
   - Worker-Proof bleibt ohne Criticals.
6. 15-Minuten-Reports:
   - Services.
   - Worker-Proof.
   - Meeting-Queue/running.
   - Offene Blocker.
   - Minimal-Fixes falls angewandt.

## Go/No-Go
Go:
- Services active.
- Worker-Proof `criticalIssues=0`.
- Kein running Meeting vor Start eines neuen Laufs.

No-Go:
- `criticalIssues>0`.
- Mehr als ein running Meeting.
- Offener Run ohne Heartbeat, der nicht innerhalb eines normalen Pickup-Zyklus erklaerbar ist.
- Discord-Bot nicht active.

## Erwarteter Endzustand
Nach zwei Stunden liegt ein klarer Prozess vor:
1. `/meeting-debate`, `/meeting-review`, `/meeting-council` legen Dateien an.
2. `/meeting-run-once` startet genau einen Lauf.
3. `/meeting-status` erklaert Fortschritt und naechste Aktion.
4. Phase C Helper erzeugt oder spaeter ausfuehrt den Codex-Beitrag.
5. `meeting-finalize.sh --dry-run` prueft Abschluss.
6. Finalize `--execute` nur nach bestandenen Gates.

## Empfohlener naechster Schritt
Gate-Status nach Atlas-5er-Versuch: Rot, aber mit gutem Befund. Atlas konnte Meeting 1/5 anlegen und alle Stimmen einsammeln, blieb aber vor Chairman-Synthese/Finalize und Taskabschluss haengen.

Empfohlene Reihenfolge:
1. Operator-Go fuer Recovery des stale Atlas-Runs entscheiden:
   - Dry-run ist bereits sauber: `node /home/piet/.openclaw/workspace/mission-control/scripts/worker-reconciler.mjs --dry-run`.
   - Mutierende Option nur mit bewusstem Go: `node /home/piet/.openclaw/workspace/mission-control/scripts/worker-reconciler.mjs --execute --run-id 4bf20a7a-0a58-458b-b466-7b873ca1a4d7`.
2. Danach gezielter Sprint: Atlas Finalizer/Taskabschluss haerten.
   - Wenn alle erwarteten Stimmen vorhanden sind, muss Atlas genau eine Synthese schreiben, `Final Status` fuellen und Meeting auf `done` setzen.
   - Wenn Finalize nicht moeglich ist, muss Atlas das Meeting sauber auf `aborted` setzen und den Worker-Run terminal beenden.
3. Erst danach die restlichen 4 Hardening-Meetings wieder freigeben.

Atlas-Follow-up-Prompt:
```text
Atlas, bitte behebe gezielt den Meeting-Orchestrierungsbruch aus dem Lauf `2026-04-25_0727_debate_worker-pickup-heartbeat-truth`.

Live-Befund:
- Meeting enthaelt Claude-Bot, Lens und Codex/Codex-Interim.
- Meeting blieb trotzdem `status: queued`.
- Statusposter meldet `needs-chairman-finalize`.
- Dein Orchestrierungs-Task `bdb6246d-9c6b-4389-95fd-ffd6a51f1f46` ging in `stalled-warning`.
- Worker-Proof meldete stale heartbeat/no process evidence fuer Run `4bf20a7a-0a58-458b-b466-7b873ca1a4d7`.

Ziel:
1. Baue keinen neuen Fanout.
2. Haerte nur den Finalizer/Taskabschluss:
   - participants complete -> Atlas-Synthese -> Final Status -> status done
   - oder sauber aborted mit Fehlergrund.
3. Liefere einen Real-Test mit genau einem Meeting.
4. Gate: worker-proof criticalIssues=0, kein stale open run, Meeting done/aborted terminal.
```

## Umsetzung 2026-04-25
- Phase C Helper gebaut: `/home/piet/.openclaw/scripts/spawn-codex-meeting.sh`.
- Statusposter nennt Phase-C Helper bei fehlendem Codex-Beitrag.
- Runner-Spawn-Plan nennt Phase-C statt nur manuell/plugin-driven.
- Real-Test 1:
  - `2026-04-25_0451_debate_meeting-council-safe-mode`
  - Claude Bot done, Lens done, Phase C Codex execute rc=0, Finalize done.
- Real-Test 2:
  - `2026-04-25_0452_debate_phase4-readiness-gates`
  - Claude Bot done, Lens done, Phase C Codex execute rc=0, Finalize done.
- Worker-Proof nach beiden Laeufen:
  - `status=ok`
  - `criticalIssues=0`
  - `openRuns=0`
  - `issues=0`

## Erweiterung: Atlas-orchestrierte 5er-Haertung
Operator-Update: Weitere 5 Debatten/Meetings sollen laufen, aber Codex steuert sie nicht selbst. Codex gibt Atlas nur den Orchestrierungsauftrag und ueberwacht.

Themen mit groesstem Hebel:
1. Worker Pickup/Heartbeat Truth:
   - Ziel: klaeren, wann `degraded` nur frische Pickup-Latenz ist und wann ein echter Claim-/Heartbeat-Fehler vorliegt.
2. Phase C Codex Execute Governance:
   - Ziel: entscheiden, ob Phase C Helper weiter manuell bleibt oder als Discord-Command mit harten Gates vorbereitet wird.
3. `/meeting-review` Production Gates:
   - Ziel: Target/Author-Kontext, Codex-Signatur, Synthese, CoVe, Token-/Cycle-Budget als Pflicht-Gates schaerfen.
4. `/meeting-council` Safe Mode:
   - Ziel: No-Fanout-Guard, Participant-Cap, staged-only, explizites Operator-Go und Rollback festzurren.
5. Discord-only Operator UX:
   - Ziel: `/meeting-run-once`, `/meeting-status`, Outcome-Reports, Webhook-Fallback und Handy-only Bedienprozess haerten.

Atlas-Regeln:
- Genau ein Meeting zur Zeit.
- Vor jedem Start: `meeting-runner.sh --dry-run` und Worker-Proof `criticalIssues=0`.
- Nach jedem Meeting: Statusbericht in Discord, dann erst naechstes Meeting.
- Codex beobachtet nur und postet 15-Minuten-Berichte.
- Kein Cron, kein Loop, kein 5-7-Agenten-Fanout ohne neues Operator-Go.

Live-Stand 2026-04-25T07:28Z:
- Atlas-Orchestrierungsauftrag: `bdb6246d-9c6b-4389-95fd-ffd6a51f1f46`.
- Task ist `in-progress/progress`, letzter Heartbeat `2026-04-25T07:26:38Z`.
- Worker-Proof: `status=ok`, `criticalIssues=0`, `openRuns=1`.
- Meeting 1/5 angelegt: `2026-04-25_0727_debate_worker-pickup-heartbeat-truth`.
- Meeting 1/5 enthaelt bereits Claude-Bot-Beitrag plus CoVe, steht aber noch auf `status: queued`.
- Gate: Codex startet die 5 Meetings nicht selbst. Codex beobachtet, ob Atlas den queued Zustand autonom sauber in running/done ueberfuehrt oder daraus einen Blocker meldet.

Live-Stand 2026-04-25T07:34Z:
- Meeting 1/5 enthaelt jetzt Claude-Bot, Lens und Codex/Codex-Interim.
- `meeting-status-post.sh` meldete faelschlich `next-action: none`, obwohl alle Stimmen vorhanden waren und `status: queued` blieb.
- Small-Fix angewandt: Statusposter leitet jetzt `reason=needs-chairman-finalize` ab, wenn alle Teilnehmer-Signaturen vorhanden sind, das Meeting aber noch nicht `done` ist.
- Verify: `bash -n /home/piet/.openclaw/scripts/meeting-status-post.sh` erfolgreich; Statusausgabe nennt `needs-chairman-finalize`.
- Kein Runner-/Cron-/Atlas-Override ausgefuehrt.

Live-Stand 2026-04-25T07:46Z:
- Atlas-Orchestrierungsauftrag ist `in-progress/progress`, aber `executionState=stalled-warning`.
- Letzter Heartbeat: `2026-04-25T07:29:50.889Z`.
- Worker-Proof: `status=degraded`, `criticalIssues=0`, `openRuns=1`, `issues=4`.
- Issues: `open-run-without-heartbeat`, `open-run-without-process-evidence`, `receipt-progress-without-start`, `stale-open-run`.
- Proposed Action im Proof: `fail-stale-open-run-without-process-evidence` fuer Run `4bf20a7a-0a58-458b-b466-7b873ca1a4d7`.
- Gate-Entscheidung: Keine weiteren Meetings dispatchen, solange dieser offene Run nicht terminal geklaert ist. Codex fuehrt den Proposed Action nicht eigenmaechtig aus, da das eine task-/run-mutierende Recovery-Aktion ist.

Live-Stand 2026-04-25T07:53Z:
- Worker-Monitor hat weiterhin nicht terminal geklaert; Task bleibt `in-progress/progress`, `executionState=stalled-warning`.
- `node scripts/worker-reconciler.mjs --dry-run` bestaetigt 1 Proposed Action: `fail-stale-open-run-without-process-evidence` fuer Run `4bf20a7a-0a58-458b-b466-7b873ca1a4d7`.
- Meeting 1/5 ist fachlich vollstaendig, aber orchestratorisch nicht abgeschlossen.
- Gate bleibt rot fuer Meeting 2-5, bis der offene Atlas-Run terminal geklaert ist.

## Beobachtung
- Kurzzeitiges `degraded` direkt nach Dispatch ist normal, solange im naechsten Pickup-Zyklus `CLAIM_CONFIRMED` und Heartbeat folgen.
- Vorherige Spark-Folgeaufgabe hatte Claim-Timeouts; das war getrennt vom Meeting-Pfad. Waehrend der kontrollierten Meeting-Laeufe wurden Main und Lens jeweils sauber claimed.
- Phase C verursacht keine Worker-Runs, sondern laeuft als separater `codex exec` unter explizitem Enable-Flag.
