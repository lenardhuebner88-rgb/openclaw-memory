---
agent: codex
created: 2026-04-25T21:16:54Z
status: active
operator: lenard
scope: "Atlas Autonomie Phase 1-4, Meeting-Live-Diskussion, Abschlussgate Sprint D"
outcome_channel_id: "1497707654087446559"
---

# Atlas Autonomie Phase 1-4: Plan zum 9/10-Gate

## Live-Iststand

- Mission Control: `/api/health` meldet `status=ok`.
- Worker-Proof: `/api/ops/worker-reconciler-proof?limit=50` meldet `openRuns=0`, `issues=0`, `criticalIssues=0`.
- Pickup-Proof: `/api/ops/pickup-proof?limit=50` meldet `pendingPickup=0`, `activeSessionLocks=0`, `criticalFindings=0`.
- Meeting-Runner: `meeting-runner.sh --dry-run` meldet keine queued/running Meetings.
- Board: aktuell keine `in-progress`, `pending-pickup`, `running` oder `assigned` Tasks.
- Mission-Control-Service: `active`.

## Bewertung des Atlas-Plans

Der Plan ist fachlich richtig, aber inzwischen teilweise bereits umgesetzt. Die aktuelle Reihenfolge muss deshalb nicht bei Sprint C beginnen, sondern beim beweisbaren Abschlussgate.

Bereits live erledigt:

- Priority-Schema-Fix: Task `4388b041-9259-44bc-87b0-41f2993b02d2`, `done/result`.
- Finalize als explizites Gate: Task `844c7720-9fad-4c06-b761-08913dd32c45`, `done/result`.
- Terminal-Receipt-Gap: Task `4b810b3b-17a3-4af3-bb53-5666ee9e631c`, `done/result`.
- `/meeting-status`: Task `275f4773-598e-4be9-8478-5df6c9e2c62c`, `done/result`.
- `/meeting-run-once`: Task `3422b50d-24cf-41b6-8a6f-18d2b890c293`, `done/result`.
- Sprint C: Task `9d056416-60a0-4c6c-b312-92e29753bd08`, `done/result`; kontrollierte Follow-up-Dispatches wurden sequentiell bewiesen.

Nicht erneut blind tun:

- Keine Cron-Aktivierung.
- Kein Fanout.
- Keine stille Follow-up-Erzeugung.
- Keine implizite Auto-Finalisierung.
- Keine parallele Autonomie-Kette.

## Meeting auf das nächste Level

Ja, echte Agenten-Diskussion in Discord ist möglich, aber nur als moderierter Turn-Prozess.

Operator-Entscheid 2026-04-25: Meeting-/Debate-Outcome wird zusätzlich in den dedizierten Discord-Kanal `1497707654087446559` gepostet. Der Webhook bleibt Secret-Material und wird nicht in Vault-Reports wiederholt.

Technische Grundlage:

- Discord-Interactions brauchen eine erste Antwort innerhalb von 3 Sekunden; längere Arbeit muss defer/follow-up nutzen: <https://docs.discord.com/developers/interactions/receiving-and-responding>
- Discord-Threads können als eigener Diskussionsraum pro Meeting dienen; Webhooks/Bots können in Threads posten: <https://docs.discord.com/developers/topics/threads>
- Rate-Limits müssen über Header/Retry-After respektiert werden, nicht hart kodiert: <https://docs.discord.com/developers/topics/rate-limits>
- OpenAI empfiehlt bei autonomeren Agenten explizite Guardrails, Tool-Risiko-Klassen und Human-Intervention bei Schwellwerten: <https://openai.com/business/guides-and-resources/a-practical-guide-to-building-agents/>

Empfohlene Zielstufe:

1. `/meeting-debate` erstellt Meeting-Datei und Discord-Thread.
2. Atlas moderiert strikt über `bounded-two-loop`: Claude, Codex, Lens, Atlas, dann zweite Reaktionsrunde Claude, Codex, Lens, Atlas.
3. Alle Kernrollen lesen vorherige Beiträge und reagieren darauf; Lens ist zusätzlicher Reality-/Kosten-/Long-Context-Reviewer, aber nicht die einzige Reaktionsrolle.
4. Jeder Agent postet mit Signatur, Timestamp, Meeting-ID und Token-/Budget-Zähler.
5. Pro `/meeting-turn-next` startet genau ein Turn; `turn-lock` und offene Meeting-Tasks blockieren den nächsten Turn.
6. Atlas finalisiert nur mit explizitem Finalize-Gate.
7. Follow-ups entstehen nur als Preview/Draft, nicht automatisch dispatched.

Nicht empfohlen für jetzt:

- Freier Live-Chat ohne Turn-Lock.
- Mehrere parallele Meetings.
- Cron-basierter Meeting-Runner.
- Agenten dürfen andere Agenten ungeprüft nachspawnen.

## Abschlussgate: Sprint D

Ein einziger großer Atlas-Sprint wird angestoßen. Codex begleitet nur, prüft Proofs und greift nur bei Gate-Bruch oder minimalem Fix ein.

Titel:

`[AUTO-SPRINT-D][Atlas] Autonomie-Architektur 9/10 Audit: Heartbeat, Crons, Gates, Reporting, Rollen`

Ziel:

Atlas soll live und evidenzbasiert prüfen, ob das System von 6/10 auf mindestens 9/10 für kontrollierte Autonomie gehoben werden kann.

Scope:

- Heartbeat-Definition: Was ist Heartbeat, was ist echter Worker, was ist Meeting-Turn?
- Cron-Inventar: Welche Crons sind notwendig, welche bleiben read-only, welche sind zu riskant?
- Gate-Inventar: Worker-Proof, Pickup-Proof, Terminal-Receipts, Finalize, Priority, Meeting-Status.
- Architekturprüfung: aktive Session vs. isolierte Subprozesse vs. HTTP/read-only Watcher.
- Reporting-Standard: einheitliches Ergebnisformat, damit Follow-up-Drafts sauber erzeugt werden können.
- Rollenmodell: Atlas, Forge, Pixel, Lens, James, Codex, Claude Bot, Operator.
- Meeting-Level-Next: Vorschlag für Discord-Thread-Debatten mit Turn-Lock.

Return-Format:

- `EXECUTION_STATUS`
- `LIVE_EVIDENCE`
- `GATE_RESULTS`
- `ARCHITECTURE_VERDICT`
- `ROLE_MATRIX`
- `REPORTING_STANDARD`
- `FOLLOW_UP_PREVIEWS` mit maximal drei Draft-Vorschlägen, alle strikt `P0|P1|P2|P3`
- `STOP_CONDITIONS`

Harte Stop-Kriterien:

- Worker-Proof oder Pickup-Proof wird rot.
- Ein Run bleibt offen ohne Heartbeat/Receipt.
- Unklare Signatur oder fehlendes Terminal-Receipt.
- Fanout oder parallele Kette entsteht.
- Follow-up wird ohne Operator-/Preview-Gate dispatched.
- Token-/Budgetdaten sind unplausibel.

## Qualitätsgates

Vor Dispatch:

- `/api/health` ok.
- Worker-Proof critical=0.
- Pickup-Proof critical=0.
- Keine laufenden Tasks.
- `meeting-runner.sh --dry-run` sieht keine laufenden Meetings.

Während Sprint:

- Genau ein Atlas-Task in `pending-pickup|in-progress`.
- Keine neuen unerwarteten Children.
- Keine offenen Worker-Runs ohne Receipt.
- Discord-Status nach größeren Schritten.

Nach Sprint:

- Task terminal mit `receiptStage=result` oder sauberem `blocked`.
- Worker-Proof critical=0.
- Pickup-Proof critical=0.
- Meeting-Runner weiter read-only und leer.
- Follow-ups nur als Draft/Preview oder als Bericht, nicht ungeprüft dispatched.

## Nächste konkrete Umsetzung

1. Plan in Discord melden.
2. Outcome-Poster für Meeting/Debate-Status in Kanal `1497707654087446559` aktivieren.
3. Sprint-D-Task für Atlas erstellen.
4. Task genau einmal dispatchen.
5. Fortschritt überwachen.
6. Ergebnis auswerten, Proofs prüfen.
7. Abschlussbericht in Discord und Session-Datei schließen.
