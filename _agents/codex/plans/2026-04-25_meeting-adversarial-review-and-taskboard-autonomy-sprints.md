---
title: Meeting Adversarial Review + Taskboard Autonomy Sprints
type: plan
status: ready-for-atlas
created: 2026-04-25T21:48Z
owner: codex
scope:
  - meeting-debate-adversarial-review
  - normal-taskboard-autonomy
sources:
  - https://arxiv.org/abs/2309.11495
  - https://correctbench.github.io/
  - https://openreview.net/pdf?id=956KYtqwcU
  - https://arxiv.org/abs/2503.13657
  - https://iclr-blogposts.github.io/2025/blog/mad/
  - https://link.springer.com/article/10.1007/s44443-025-00353-3
  - https://owasp.org/www-project-mcp-top-10/2025/MCP08-2025%E2%80%93Lack-of-Audit-and-Telemetry
---

# Adversarial Review: `/meeting debate`

## CONFIRMED (Reviewer hat recht)
- [2] `arXiv:2503.13657` bestaetigt 14 Failure-Modes in 3 Kategorien, nicht 5 Kategorien. Quelle: https://arxiv.org/abs/2503.13657. Beleg: Abstract nennt 14 unique modes, clustered into 3 categories.
- [3] MAD-Eval ist ein ICLR-2025-Blogpost, kein normales Peer-Review-Paper. Quelle: https://iclr-blogposts.github.io/2025/blog/mad/. Die Kernaussage ist nuanciert: MAD schlaegt CoT/Self-Consistency nicht konsistent.
- [5] Live-Audit zeigt aktuell 19 Meeting-Files, davon 18 `mode: debate` und 1 `mode: review`; kein `mode: council`. Der Reviewer-Wert 16/18 ist als alter Snapshot plausibel, aktuell ist die Debate-Dominanz sogar staerker.
- [6] `meeting-council-safe-mode.md` und `meeting-review-minimal-features.md` sind als `mode: debate` getaggt, behandeln aber inhaltlich Council-/Review-Features. Das ist keine harte Schema-Verletzung, aber ein echtes Analytics-/Retrieval-Problem.
- [9] Kein Meeting-Token-/Layer-15-Cron ist in der aktuellen `crontab -l -u piet` sichtbar. Die Token-Log-Datei kann existieren, aber die Cron-Befuellung ist aktuell nicht als Defense-Layer belegt.
- [13] R49-Hygiene ist nicht Kosmetik: falsche Quellen im Plan wuerden direkt die Autonomie-Entscheidungen vergiften. Mindestens die Quellenlage muss im aktiven Handshake/README korrigiert bleiben.

## DISPUTED (Reviewer falsch oder ueberzogen)
- [1] Reviewer: CorrectBench/GPQA sei fabriziert. Wirklich gilt: Das originale CoVe-Paper `arXiv:2309.11495` testet nicht GPQA, aber CorrectBench 2025 existiert und testet CoVe auf GPQA. Quelle: https://correctbench.github.io/ und https://openreview.net/pdf?id=956KYtqwcU. Beleg: CorrectBench Table 1 fuehrt CoVe mit GPQA `37.41 (+18.85)`; der Text nennt CoVe-GPQA +23.24% als prozentuale Verbesserung. Die Planformulierung muss sauber sagen: "CorrectBench 2025, nicht originales CoVe-Paper."
- [3] Reviewer: Heterogenitaet sei praktisch wertlos. Wirklich gilt: MAD-Eval ist skeptisch gegen MAD allgemein, aber untersucht auch Modell-Mischung; zusaetzlich berichtet A-HMAD 2025 Vorteile heterogener Rollen/Modelle gegen homogene Debatte. Quelle: https://link.springer.com/article/10.1007/s44443-025-00353-3. Das rettet nicht jede Meeting-Automation, aber es widerlegt die absolute Aussage "homogene/heterogene Debate ist nur Token-Burn".
- [7] Reviewer: Codex-Files in `_coordination/live/` sind Schema-Verletzung. Wirklich gilt: Codex-Session-/Arbeitsdateien gehoeren nach Live; Meeting-Artefakte gehoeren nach `meetings/`. Das Problem ist nicht der Ort von Codex-Live-Files, sondern ob Codex-Beitraege im Meeting-Artefakt signiert und referenziert werden.
- [8] Reviewer: `template-meeting.md` fehlt. Live falsch. `find /home/piet/vault -name 'template-meeting*'` findet `/home/piet/vault/99-Templates/template-meeting.md`.
- [9] Reviewer: HANDSHAKE §6 sei vermutlich nicht vorhanden. Live falsch. `HANDSHAKE.md` enthaelt `## 6. Meeting-Modi`, Discord-Trigger und Bounded Two-Loop Discussion.
- [11] Reviewer: CoVe muss als Cron-Nachbrenner erzwungen werden. Das ist methodisch schief. CoVe ist ein Inference-/Verification-Pattern; ein Cron, der spaeter Claims prueft, ist eher Fact-Checking-/Audit-Pipeline. Fuer OpenClaw sinnvoll: CoVe-Log im Task/Meeting-Receipt erzwingen, optional spaeter Audit-Cron als R49-Watcher.
- [12] Reviewer: ASI08/Circuit-Breaker sofort voll ausrollen. Ueberzogen fuer Solo-Operator, aber das Grundprinzip ist richtig: Observability, Stop-Kriterien und Least-Agency reichen als naechster Schritt. OWASP MCP08 fordert strukturierte Audit-/Telemetry-Logs; harte Multi-Tenant-Isolation ist hier nicht die erste Baustelle.
- [14] Reviewer: codex-plugin-cc installieren oder Empirie revidieren. Dritter Weg ist valide: Codex bleibt ueber `_coordination/live/` plus signierte Meeting-/Taskboard-Beitraege eingebunden, solange die Beitraege in den Meeting-/Task-Artefakten referenziert und auditierbar sind.

## MISSED (Reviewer hat uebersehen)
- Datenschutz/Geheimnisse: Meeting- und Task-Files koennen interne Pfade, Webhook-IDs, Channel-IDs und Operationsdetails enthalten. Fuer Autonomie braucht es eine Redaction-Regel vor breiterem Reporting.
- Storage-/Retrieval-Wachstum: 19 Meeting-Files in ~1 Tag skaliert auf tausende Files/Jahr. Ohne Index-/Archive-Regel wird Retrieval lauter und die falschen Debates werden als "aktuell" gezogen.
- Mode-vs-Topic-Schema: `mode: debate` und Topic `meeting-review-*` sind beide legitim, aber ohne zweites Feld wie `subject-mode: review|council|board` werden Reports und Boards falsche Schluesse ziehen.
- Receipt-Maschinenlesbarkeit: Live-Taskboard zeigt bei aktuellen Atlas-/Meeting-Tasks `sprintOutcome=false`, obwohl Prompts es verlangen. Das ist ein groesserer Autonomie-Blocker als weitere Debate-Features.
- Fanout-Risiko: Der aktuelle Smoke-Test bewies einen echten Runner-Fehler: Lens wurde parallel zu Claude gespawnt. Das wurde gecancelt und der Smoke als `blocked` markiert. Diese Ehrlichkeit ist wichtig: Meeting Phase-C ist nicht produktionsgruen.
- Normale Board-Arbeit hat hoeheren Hebel als Meeting. Die Operator-Zielvorstellung ist: "Ich gebe Atlas ein Audit, Atlas arbeitet es ab, erstellt Follow-ups, holt nur bei sudo/Modellwechseln Freigabe." Das ist Taskboard-Governance, nicht Meeting-UX.

## NET VERDICT
Die Reviewer-Bewertung haelt teilweise: Mode-Drift, fehlender Meeting-Cron und falsche bzw. unklare Quellenverweise sind echte Befunde. Sie ist aber bei CorrectBench, Template und HANDSHAKE live falsch bzw. ueberzogen. Der naechste Schritt sollte nicht weiteres `/meeting`-Feature-Wachstum sein, sondern normale Taskboard-Autonomie: Receipt-/Gate-Vertraege maschinenlesbar erzwingen, Follow-up-Previews kontrolliert materialisieren, und Atlas genau einen grossen Sprint sequentiell durchsteuern lassen.

Vor Akzeptanz nochmals zu verifizieren:
- `sprintOutcome` muss bei terminalen Receipts wirklich im Task-Objekt landen.
- Follow-up-Tasks muessen Preview/Draft bleiben, bis Operator oder definierte Policy sie freigibt.
- Sudo und Modellwechsel muessen als harte Approval-Klassen im Taskboard sichtbar sein.

## CONFIDENCE
- A Quellen-Faktcheck: high. Primaerquellen fuer CoVe, CorrectBench, MAST und MAD-Eval wurden geprueft.
- B Live-Audit: high. Befunde stammen aus `find`, `awk`, `crontab`, `rg`, `meeting-status-post` und Proof-Endpoints.
- C Architektur-Argumente: medium. Die Richtung ist gut belegt, aber "bestes" Debate-Design ist weiterhin empirisch uneindeutig.
- D Priorisierung: high. Live-Gates zeigen keine Worker-Blocker, aber terminale Tasks ohne `sprintOutcome` sind ein konkreter Board-Autonomie-Blocker.

# Wechsel: Zwei Sprints fuer normale Taskboard-Autonomie

## Zielbild fuer Operator
Der Operator schreibt in Discord/Board: "Atlas, mach Audit XY." Danach:
1. Atlas nimmt genau einen Parent-Task an.
2. Atlas arbeitet Schritt fuer Schritt mit sichtbaren Receipts.
3. Nach jedem Gate schreibt Atlas einen kurzen Status ins Reporting.
4. Atlas erstellt maximal 3 Follow-up-Previews mit Prioritaet, Owner, DoD und Gate.
5. Das System dispatcht Follow-ups nur, wenn Policy es erlaubt. Sudo und Modellwechsel bleiben immer Operator-Go.
6. Am Ende gibt es ein maschinenlesbares `sprintOutcome`, Gate-Ergebnis und naechste Handlungsempfehlung.

## Sprint 1: Board Autonomy Policy + Receipt Enforcement

**Ziel:** Aus Konventionen eine kleine, pruefbare Taskboard-Policy machen.

Scope:
- Normaler Taskboard-Prozess, keine weitere `/meeting`-Feature-Arbeit.
- Klassen definieren: read-only audit, safe small-fix, gated mutation, sudo-required, model-switch-required.
- Terminal-Receipt-Vertrag erzwingen: `receiptStage=result|blocked|failed`, `resultSummary`, `gate_results`, `sprintOutcome`.
- Reporting vereinheitlichen: accepted/progress/result in ein Format.
- Cron-/Heartbeat-Grenze festziehen: Heartbeat beobachtet, Worker arbeitet, Atlas orchestriert, Cron dispatcht keine stillen Follow-ups.

Deliverables:
- `03-Agents/codex/plans/taskboard-autonomy-policy-2026-04-25.md`
- Atlas-Task-Prompt fuer einen Policy-Proof-Run.
- Live-Gate-Report mit Proof-Endpoints.

Quality Gates:
- `/api/health` ok.
- `/api/ops/worker-reconciler-proof?limit=50` critical=0.
- `/api/ops/pickup-proof?limit=50` criticalFindings=0 und pendingPickup=0.
- Ein Atlas-Proof-Task endet mit `sprintOutcome != null`.
- Keine Follow-up-Preview wird automatisch dispatched.
- Keine sudo/model-switch Aktion ohne Operator-Go.

Stop-Kriterien:
- Offener Worker-Run ohne Heartbeat/Receipt.
- Parent-Task done, aber `sprintOutcome` fehlt.
- Follow-up verlaesst Draft/Preview ohne explizites Go.
- Mehr als ein Atlas-Autonomie-Strang parallel.

## Sprint 2: Controlled Follow-up Chain + One Big Atlas Sprint

**Ziel:** Atlas fuehrt einen grossen Audit-Sprint autonom aus und erzeugt daraus sichere Follow-ups.

Scope:
- Ein Parent-Sprint: "Taskboard Autonomy Operating Model Audit".
- Maximal 3 Follow-up-Previews.
- Danach genau ein Follow-up ausfuehren, wenn es safe/read-only ist.
- Keine Cron-Aktivierung, kein Fanout, kein Modellwechsel.

Deliverables:
- Ein grosser Atlas-Sprint im Board.
- 3 Follow-up-Preview-Drafts mit `approvalMode`.
- Ein ausgefuehrter safe Follow-up-Task als Proof.
- Abschlussbericht mit Score gegen 9/10.

Quality Gates:
- Parent-Task terminal und `sprintOutcome` vorhanden.
- Follow-up-Drafts enthalten `decisionKey`, `sourceStepId`, `owner`, `priority`, `objective`, `definition_of_done`, `approvalMode`.
- Nur der freigegebene safe Follow-up wird dispatched.
- Nach Follow-up erneut Health/Worker/Pickup-Proofs gruen.
- Discord-Report nennt: Was lief automatisch, was brauchte Freigabe, was bleibt blockiert.

Stop-Kriterien:
- Atlas erzeugt mehr als 3 Follow-ups.
- Ein Follow-up braucht sudo/model-switch und wird trotzdem dispatched.
- Receipt fehlt oder ist nur Freitext ohne maschinenlesbares Ergebnis.
- Claim-timeout/pickup drift taucht live wieder auf.

## Rollenbild
| Rolle | Aufgabe | Freigabegrenze |
|---|---|---|
| Operator | Ziel geben, sudo/model-switch freigeben, final Go/No-Go | Muss nicht jeden normalen Audit-Schritt bestaetigen |
| Atlas | Parent-Sprint chair, Gates pruefen, Follow-up-Previews erstellen | Kein sudo, kein Modellwechsel, kein unlimitierter Fanout |
| Forge | Runtime/Cron/Worker-Fixes bei klarer DoD | Keine UX-/Produktentscheidung |
| Lens | Kosten-/Risiko-/Recherchecheck | Keine Runtime-Mutation |
| Pixel/James | UI-/Reporting-Nutzbarkeit | Keine Control-Plane-Mutation |
| Codex | Minimal-Fixes, Code-/Policy-Review, harte Gate-Pruefung | Nicht Atlas als Board-Chair ersetzen |

## Atlas Start-Prompt fuer Sprint 1

```text
Atlas, starte einen normalen Taskboard-Autonomie-Sprint, NICHT /meeting:

Ziel: Board Autonomy Policy + Receipt Enforcement pruefen und haerten.

Read-first:
- /home/piet/vault/03-Agents/codex/plans/2026-04-25_meeting-adversarial-review-and-taskboard-autonomy-sprints.md
- /home/piet/.openclaw/workspace/reports/atlas-autonomy-architecture-9of10-2026-04-25.md

Auftrag:
1. Pruefe live /api/health, worker-proof und pickup-proof.
2. Dokumentiere die Board-Autonomie-Policy: heartbeat beobachtet, worker arbeitet, Atlas orchestriert, Cron dispatcht nicht still.
3. Fuehre genau einen Proof-Task aus, der terminal mit sprintOutcome endet.
4. Erzeuge maximal 3 Follow-up-Previews, aber dispatchte keine davon.
5. Markiere sudo/model-switch immer als operator-go-required.
6. Poste nach jedem Gate einen kurzen Status in Discord.

Stop sofort bei: worker/pickup critical, fehlendem terminal receipt, fehlendem sprintOutcome, Follow-up ohne Approval, mehr als einem parallelen Atlas-Strang.

Return:
- EXECUTION_STATUS
- LIVE_EVIDENCE
- GATE_RESULTS
- POLICY_DELTA
- FOLLOW_UP_PREVIEWS
- SCORE_0_TO_10 mit Begruendung
```

## Atlas Start-Prompt fuer Sprint 2

```text
Atlas, starte Sprint 2 erst wenn Sprint 1 gruen ist:

Ziel: Controlled Follow-up Chain + One Big Atlas Sprint.

Auftrag:
1. Fuehre einen grossen Audit-Sprint aus: "Taskboard Autonomy Operating Model Audit".
2. Arbeite sequentiell: keine parallele Kette, kein Fanout.
3. Erzeuge genau 3 Follow-up-Preview-Drafts mit owner, priority, DoD, approvalMode.
4. Dispatchte nur einen safe/read-only Follow-up, wenn alle Proof-Gates gruen sind.
5. Sudo und Modellwechsel bleiben hart operator-go-required.
6. Abschluss: Score gegen 9/10, konkrete Luecken, naechster kleiner Schritt.

Gates:
- health ok
- worker critical=0
- pickup criticalFindings=0
- parent sprintOutcome vorhanden
- follow-up preview nicht still dispatched
- ein safe follow-up terminal gruen
```

