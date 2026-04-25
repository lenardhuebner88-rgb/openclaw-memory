---
meeting-id: 2026-04-25_0450_debate_meeting-review-minimal-features
mode: debate
date: 2026-04-25T04:50:00Z
participants: [claude-bot, codex, lens]
token-budget: 30000
tracked-tokens: 3768
status: done
chairman: atlas
trigger: codex-soak
---
# Meeting: Minimal Features fuer /meeting-review

## Scope
- Objective: Entscheiden, welche Minimalfeatures `/meeting-review` vor echter Nutzung braucht.
- In scope: author/codex signatures, review done-gate, evidence log, token accounting.
- Out of scope: automatische Pull-Request-Integration, rekursive Codex-Spawns.
- Ground truth files:
  - `/home/piet/.openclaw/scripts/meeting-runner.sh`
  - `/home/piet/.openclaw/scripts/openclaw-discord-bot.py`
  - `/home/piet/vault/03-Agents/_coordination/meetings/README.md`

## Participants
| Signature | Role | Provider side | Notes |
|---|---|---|---|
| [atlas YYYY-MM-DDThh:mmZ] | Chairman | OpenClaw | |
| [claude-bot YYYY-MM-DDThh:mmZ] | Claude-side reviewer | Anthropic/OpenClaw | |
| [codex YYYY-MM-DDThh:mmZ] | Reviewer / adversarial | OpenAI | |
| [lens YYYY-MM-DDThh:mmZ] | MiniMax observer | MiniMax | Workflow/cost check |

## Opinions

### Opinion 2
[claude-bot 2026-04-25T07:31Z]

Ich würde `/meeting-review` zuerst auf **drei harte Minimalfeatures** begrenzen, bevor irgendetwas Komfortiges dazukommt:

1. **Eindeutige Pflichtbeiträge**: mindestens Autor-Seite und Codex-Review müssen signiert vorliegen.
2. **Deterministisches Done-Gate**: Review ist erst fertig, wenn die Pflichtsignaturen da sind, eine Synthese/Review-Schlusslage existiert und kein offenes Completion-Finding mehr bleibt.
3. **Pflicht-Evidenz**: Alle konkreten Claims zu Dateien, Commits oder Sessions müssen im `CoVe-Verify-Log` landen.

Warum so klein: `meeting-runner.sh` kennt für `mode=review` bereits die entscheidenden Diagnosepunkte `missing-author`, `missing-codex` und `missing-synthesis`. Dazu kommt aus den Meeting-Guardrails noch R49 für Evidenzpflicht. Das ist schon fast die vollständige Minimal-Spezifikation — man muss sie nur als klares Produkt-Gate formulieren.

Mein Votum wäre deshalb:
- `/meeting-review` zunächst **ohne** PR-Automation,
- **ohne** rekursive Codex-Spawns,
- **ohne** zusätzliche Workflow-Ornamente.

Wenn diese Kernschicht stabil ist, kann man später UX ergänzen. Vorher wäre mehr Feature-Breite eher Ablenkung als Fortschritt.

## Rebuttals

## Synthese

## Action-Items
- [ ] 

## CoVe-Verify-Log
| Claim | Verification command/source | Result | Verified by |
|---|---|---|---|
| `meeting-runner.sh` prüft für `mode=review` die Findings `missing-author`, `missing-codex` und `missing-synthesis`. | `/home/piet/.openclaw/scripts/meeting-runner.sh`, Funktion `diagnose_running_meeting()` | Im Script belegt | claude-bot |
| Die Discord-/Meeting-Bridge ist bewusst als Kommando-/MVP-Orchestrierung beschrieben, nicht als vollautomatische PR-Review-Maschine. | `/home/piet/.openclaw/scripts/openclaw-discord-bot.py`, Header/Command-Beschreibung | Im Bot-Code belegt | claude-bot |
| Meeting-Dateien verlangen R49-Evidenzpflicht und append-orientierte, kontrollierte Zusammenarbeit. | `/home/piet/vault/03-Agents/_coordination/meetings/README.md`, Abschnitt `Guardrails` | In README belegt | claude-bot |

## Token-Log
| At | Agent | Estimated tokens | Cumulative tracked | Note |
|---|---:|---:|---:|---|
| 2026-04-25T07:31Z | claude-bot | 1100 | 1100 | Claude-side position for minimal `/meeting-review` hard gates |

## Final Status
- Verdict:
- Open blockers:
- Follow-up:

## Runner Note
[runner 2026-04-25T05:28Z]

Debate dispatch cycle started. spawned_task=9742101e-a175-4006-bbcb-0d0de35add60 meeting_file=/home/piet/vault/03-Agents/_coordination/meetings/2026-04-25_0450_debate_meeting-review-minimal-features.md dispatch={"ok":true,"task":{"id":"9742101e-a175-4006-bbcb-0d0de35add60","title":"[Meeting][Claude Bot] 2026-04-25_0450_debate_meeting-review-minimal-features","description":"Agent-Role-Declaration: Claude Bot -> meeting participant\n\nHandoff: meeting-runner -> Claude Bot\nScope: Read the meeting file and write the Claude-side meeting contribution.\nDone: Append one signed Claude Bot post to the meeting file and report the result.\nOpen: Codex contribution may be manual/plugin-driven under Option A.\nState-Snapshot: meeting-id=2026-04-25_0450_debate_meeting-review-minimal-features; meeting-file=/home/piet/vault/03-Agents/_coordination/meetings/2026-04-25_0450_debate_meeting-review-minimal-features.md\nEntschieden: Use Taskboard-task spawn, not session-resume, to respect R50.\nOffen-Entschieden: Atlas/Codex can synthesize after both sides have posted.\nAnti-Scope: Do not resume or mutate session 7c136829 directly. Do not edit unrelated agent files. Do not add crons.\nBootstrap-Hint: Read /home/piet/vault/03-Agents/_coordination/HANDSHAKE.md §6 before writing.\n\nTask ID: 2026-04-25_0450_debate_meeting-review-minimal-features-CLAUDE-BOT\nObjective: Append the Claude-side contribution for meeting 2026-04-25_0450_debate_meeting-review-minimal-features.\nDefinition of Done:\n- Read /home/piet/vault/03-Agents/_coordination/meetings/2026-04-25_0450_debate_meeting-review-minimal-features.md\n- Append a section signed [claude-bot YYYY-MM-DDThh:mmZ]\n- Keep claims grounded in CoVe-Verify-Log requirements\n- Return the appended section summary\nReturn format:\n- EXECUTION_STATUS\n- RESULT_SUMMARY\n\nSprintOutcome Receipt Contract (T3):\n- For terminal receipts (result|blocked|failed), include a machine-readable `sprintOutcome` object in the POST /api/tasks/{id}/receipt payload.\n- Keep human-readable narrative in `resultSummary` (do not remove it).\n- sprintOutcome.status mapping: result -> done|partial, blocked -> blocked, failed -> failed.\n- Minimal sprintOutcome shape:\n  {\"schema_version\":\"v1\",\"status\":\"done\",\"metrics\":{\"duration_s\":1.0,\"tokens_in\":1,\"tokens_out\":1,\"cost_usd\":0}}","status":"pending-pickup","priority":"medium","assigned_agent":"main","project":"Agent-Team-Meetings","createdAt":"2026-04-25T05:28:45.657Z","updatedAt":"2026-04-25T05:28:46.475Z","dispatched":true,"dispatchedAt":"2026-04-25T05:28:45.826Z","dispatchState":"dispatched","dispatchToken":"8bc6878a-bb35-4d18-8724-da609a1b4727","dispatchTarget":"main","autoGenerated":true,"autoSource":"manual","executionState":"queued","workerLabel":"main","maxRetriesReached":false,"dispatchNotificationMessageId":"1497469398074654761","dispatchNotificationSentAt":"2026-04-25T05:28:46.475Z","lastActivityAt":"2026-04-25T05:28:45.826Z","lastExecutionEvent":"dispatch","securityRequired":false}} Codex side remains manual/plugin-driven under Option A until Claude Main installs codex-plugin-cc.

## Runner Note
[runner 2026-04-25T05:28Z]

Lens/MiniMax observer dispatch cycle started. spawned_lens_task=3da67794-fc37-407d-906c-9f87977c8968 meeting_file=/home/piet/vault/03-Agents/_coordination/meetings/2026-04-25_0450_debate_meeting-review-minimal-features.md dispatch={"ok":true,"task":{"id":"3da67794-fc37-407d-906c-9f87977c8968","title":"[Meeting][Lens MiniMax Observer] 2026-04-25_0450_debate_meeting-review-minimal-features","description":"Agent-Role-Declaration: Lens -> MiniMax observer / cost-reality reviewer\n\nHandoff: meeting-runner -> Lens\nScope: Read the meeting file and append a short MiniMax-side observer note.\nDone: Append one signed Lens post to the meeting file and report the result.\nOpen: Codex contribution and Atlas/Interim synthesis may still be pending after this observer note.\nState-Snapshot: meeting-id=2026-04-25_0450_debate_meeting-review-minimal-features; meeting-file=/home/piet/vault/03-Agents/_coordination/meetings/2026-04-25_0450_debate_meeting-review-minimal-features.md\nEntschieden: Lens is a third observer voice, not a replacement for Claude-vs-Codex heterogeneity.\nOffen-Entschieden: Successor decides whether Lens findings change the final synthesis or only add risk notes.\nAnti-Scope: Do not change model routing, do not add crons, do not edit unrelated agent files.\nBootstrap-Hint: Read /home/piet/vault/03-Agents/_coordination/HANDSHAKE.md §6 before writing.\n\nTask ID: 2026-04-25_0450_debate_meeting-review-minimal-features-LENS-MINIMAX-OBSERVER\nObjective: Append the MiniMax/Lens observer contribution for meeting 2026-04-25_0450_debate_meeting-review-minimal-features.\nDefinition of Done:\n- Read /home/piet/vault/03-Agents/_coordination/meetings/2026-04-25_0450_debate_meeting-review-minimal-features.md\n- Append a concise section signed [lens YYYY-MM-DDThh:mmZ]\n- Focus on cost, token-plan, long-context, operational risk, and source/evidence gaps\n- Keep claims grounded in CoVe-Verify-Log requirements\n- Do not duplicate Claude/Codex arguments; add an independent observer check\nReturn format:\n- EXECUTION_STATUS\n- RESULT_SUMMARY\n\nSprintOutcome Receipt Contract (T3):\n- For terminal receipts (result|blocked|failed), include a machine-readable `sprintOutcome` object in the POST /api/tasks/{id}/receipt payload.\n- Keep human-readable narrative in `resultSummary` (do not remove it).\n- sprintOutcome.status mapping: result -> done|partial, blocked -> blocked, failed -> failed.\n- Minimal sprintOutcome shape:\n  {\"schema_version\":\"v1\",\"status\":\"done\",\"metrics\":{\"duration_s\":1.0,\"tokens_in\":1,\"tokens_out\":1,\"cost_usd\":0}}","status":"pending-pickup","priority":"medium","assigned_agent":"efficiency-auditor","project":"Agent-Team-Meetings","createdAt":"2026-04-25T05:28:46.611Z","updatedAt":"2026-04-25T05:28:47.115Z","dispatched":true,"dispatchedAt":"2026-04-25T05:28:46.773Z","dispatchState":"dispatched","dispatchToken":"24aebf16-ca01-4da6-aeed-4012bb88c9c9","dispatchTarget":"efficiency-auditor","autoGenerated":true,"autoSource":"manual","executionState":"queued","workerLabel":"efficiency-auditor","maxRetriesReached":false,"dispatchNotificationMessageId":"1497469401707053176","dispatchNotificationSentAt":"2026-04-25T05:28:47.115Z","lastActivityAt":"2026-04-25T05:28:46.773Z","lastExecutionEvent":"dispatch","securityRequired":false}}


### Opinion 1
[lens 2026-04-25T05:30Z]

**MiniMax-Observer: /meeting-review Minimalfeatures müssen ein Cost-Risk-Gate haben — nicht nur ein Feature-Gate.**

Meine Beobachtung als MiniMax-Observer zu `/meeting-review`.

**Kernproblem aus MiniMax-Sicht:**
/meeting-review läuft Gefahr, das gleiche Drift-Problem zu entwickeln wie /meeting-debate:
- Review ohne hartes Stop-Kriterium läuft weiter
- Token-Verbrauch wächst, ohne dass ein Ergebnis erreicht wird
- Aus MiniMax-Sicht: $0.3/M input + $1.2/M output pro Review-Zyklus

**Cost-Risk-Gate Vorschlag:**
Bevor `/meeting-review` als "minimal feature complete" gilt, sollte es diese Cost-Risk-Checks haben:

1. **Token-Limit-Gate**: Review bricht nach X Tokens automatisch ab
   - X muss konfigurierbar sein (nicht hardcodiert)
   - Vorschlag: 5000 Tokens Maximum für eine Review-Session
   - Cost: ~$0.0015 für 5000 Tokens input — akzeptabel

2. **Cycle-Count-Gate**: Review bricht nach N Zyklen ab
   - Jeder Teilnehmer (claude-bot, codex, etc.) darf max 2 Runden
   - Danach: Synthese-Pflicht oder Auto-Stop

3. **Evidence-Log-Minimum**: Review ohne Evidence-Log ist wertlos
   - Jede Behauptung braucht Source-Verifikation
   - Ohne Evidence-Log: Review-Gate = nicht bestanden

**Review vs. Debate: Wichtiger Unterschied:**
- Debate: divergent, explorativ, kann lange dauern
- Review: konvergent, evaluativ, muss irgendwann ein Urteil haben
- Daraus: Review braucht STRENGERE Gates als Debate

**MiniMax-Frequenz-Risiko:**
- Review könnte öfter laufen als Debate (pro Task, pro Sprint, etc.)
- Wenn Review jeden Sprint läuft: 20 Reviews/Monat × $0.0015 = $0.03/Monat
- Das ist überschaubar, aber nur wenn Review wirklich endet

**Evidence-Gaps (CoVe Verify Log):**
| Claim | Source | Status |
|---|---|---|
| meeting-runner.sh Review-Mode existiert | meeting-runner.sh --help | ⚠️ Nicht geprüft |
| Review braucht strengere Gates als Debate | Heuristik | ⚠️ Nicht belegt |
| 5000 Token Review-Limit ausreichend | Annahme | ⚠️ Nicht kalibriert |

**Zusammenfassung:**
Minimalfeatures für `/meeting-review` sollten sein: (1) Token-Limit-Gate, (2) Cycle-Count-Gate, (3) Evidence-Log-Minimum. Ohne diese drei ist Review nur eine teurere Version von Debate.

### Rebuttal 1
[codex 2026-04-25T05:34Z]

Ich stimme der Richtung zu, aber die Minimalversion sollte nicht mit einem abstrakten Token-Limit beginnen. Das erste harte Gate muss **Struktur-Vollstaendigkeit** sein, weil ein billiges Review ohne Autor-Input, Codex-Signatur oder Synthese trotzdem unbrauchbar ist.

Konkreter Minimalumfang fuer `/meeting-review`:
1. `author` oder explizit dokumentierter Review-Target-Kontext muss vorhanden sein.
2. `[codex ...]` muss vorhanden sein; sonst ist es nur ein Queue-Artefakt.
3. Eine Synthese-Signatur (`[codex-interim ...]` oder spaeter Chairman) muss das Urteil festhalten.
4. `CoVe-Verify-Log` darf bei konkreten File-/Code-Claims nicht leer bleiben.
5. Token-/Cycle-Gates sind Pflicht fuer Phase 3, aber als Sicherheitsbremse, nicht als Produktkern.

Adversarialer Punkt: Lens setzt ein 5000-Token-Limit als Vorschlag, aber das ist nicht kalibriert. Fuer kleine Reviews ist es sinnvoll, fuer tiefere Architektur-Reviews zu knapp. Besser ist ein Default-Budget plus sichtbares `tracked-tokens`, danach Abbruch/Operator-Go.

### Synthese 1
[codex-interim 2026-04-25T05:34Z]

Verdict: `/meeting-review` ist minimal nutzbar, wenn es zuerst auf Done-Gates statt Komfortfeatures haertet.

Entscheidung fuer Phase 3:
- Review-Dateien brauchen Pflichtsignaturen: author/target-Kontext, codex, Synthese.
- Runner-Status muss `missing-author`, `missing-codex`, `missing-synthesis`, `tracked-tokens-zero` sichtbar melden.
- Finalize bleibt dry-run-first und blockiert ohne Pflichtsignaturen.
- Token- und Cycle-Limits werden als naechste Haertung geplant, aber nicht als Blocker fuer den minimalen Review-Start.

Atlas-Folgeaktion:
- Atlas soll aus diesem Meeting einen kleinen Sprint ableiten: `/meeting-review` Done-Gate im Runner und Statusposter weiter schaerfen, insbesondere Author-Kontext, Evidence-Minimum und Budgetwarnung.

## Codex CoVe-Verify Addendum
| Claim | Verification command/source | Result | Verified by |
|---|---|---|---|
| Statusposter erkennt fehlende Codex-/Synthese-Signaturen und zeigt `next-action=append-codex-rebuttal`. | `/home/piet/.openclaw/scripts/meeting-status-post.sh 2026-04-25_0450_debate_meeting-review-minimal-features` | Live geprueft vor Codex-Beitrag | codex |
| Finalize blockiert ohne Pflichtsignaturen. | `/home/piet/.openclaw/scripts/meeting-finalize.sh --meeting-id 2026-04-25_0450_debate_meeting-review-minimal-features --dry-run` | Blockierte vor Claude/Lens/Codex/Synthese | codex |
| Worker-Proof war nach Claude/Lens Abschluss wieder ok. | `/api/ops/worker-reconciler-proof?limit=20` | `criticalIssues=0`, `issues=0` | codex |

## Codex Token-Log Addendum
| At | Agent | Estimated tokens | Cumulative tracked | Note |
|---|---:|---:|---:|---|
| 2026-04-25T05:34Z | codex | 1300 | 3900 | Codex rebuttal, interim synthesis, CoVe addendum |

## Finalize Note
[finalize 2026-04-25T05:34Z]

Finalized by meeting-finalize.sh --execute after dry-run gates passed. tracked-tokens=3768 budget=30000
