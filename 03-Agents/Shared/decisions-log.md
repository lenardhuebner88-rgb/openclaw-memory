# Decisions Log

## Active decisions
- 2026-04-12: Discord-Reporting aktiv — worker-monitor postet Task-Completions automatisch in #execution-reports (Channel 1488976473942392932) + Completion-Ping an Atlas. Discord-Bot-Token in `.env.local` auf Homeserver hinterlegt. Kein manuelles Monitoring nötig.
- 2026-04-10: Layer-3 canonicalized to `/home/piet/vault` root structure; no `OpenClaw-Memory/*` dependency.
- 2026-04-10: Active retrieval chain is `project-state` → `decisions-log` → `operational-state` → agent `working-context`; daily is opt-in only.
- 2026-04-10: Hermes removed from active agent structure and archived as decommissioned context.
- 2026-04-10: Nested `Openclaw peter` vault path retired from active use to remove retrieval ambiguity.
- 2026-04-09: Result routing follows Discord channel purpose; no default dumping into `#atlas-main`.
- 2026-04-08: Mission Control stays on production service (`next start`) for lower memory and better stability.
- 2026-04-08: Opus stays constrained to high-value cases (root-cause, architecture, severe bugs).

## Historical decisions
- 2026-04-13: [P1][Ops] Mission-Control Restart-Runbook und Dev-Port-Guardrails dokumentieren: Ein kurzes Ops-Runbook mit Restart-Pfad, Dev-Port-Regeln und Fail-safe Port-Guard für Mission Control wurde dokumentiert und versioniert. ## Was wurde gemacht - Neues Runbook `docs <!-- mc:auto-decision:079828fa-bf5f-4475-99a4-c3c16fe9cd2e|result|p1-ops-mission-control-restart-runbook-und-dev-port-guardrails-dokumentieren-ein -->
- 2026-04-13: [P1][Fix] App-Router-Route-Helper aus API-Routen entkoppeln und TypeScript-Contract bereinigen: App-Router-Helper für agents/live und cron-jobs wurden in Shared-Module verlagert, betroffene Page-Imports umgestellt und der TypeScript-Check läuft für diesen Scope wieder sauber  <!-- mc:auto-decision:0716c190-748e-462f-89de-f8bccd0f9091|result|p1-fix-app-router-route-helper-aus-api-routen-entkoppeln-und-typescript-contract -->
- 2026-04-13: [Fix] Trends TypeScript-Blocker in route.ts und TrendsClient.tsx bereinigen: Trends-TypeScript-Blocker in src/app/api/trends/route.ts und src/app/trends/TrendsClient.tsx behoben; npx tsc --noEmit läuft wieder erfolgreich grün. ## Was wurde gemacht - In `src <!-- mc:auto-decision:9e614f19-2836-4092-8c80-e070326b13fa|result|fix-trends-typescript-blocker-in-route-ts-und-trendsclient-tsx-bereinigen-trends -->
- 2026-04-13: [P1][System] Atlas Schritt-8 Trigger-Policy implementieren (harte Signalschwelle) failed: Worker failed <!-- mc:auto-decision:5107c8ab-1ad7-4f3e-8538-f3c1630b49dc|failed|p1-system-atlas-schritt-8-trigger-policy-implementieren-harte-signalschwelle-fai -->
- 2026-04-13: [Fix] Mission Control Restart-Storm + 500er auflösen: Restart-Storm wurde auf Port-3000-Kollisionen durch parallele/alte MC-Instanzen eingegrenzt und mit einem sicheren Start-Guard stabilisiert. ## Was wurde gemacht - Journal-Analyse  <!-- mc:auto-decision:4c41b21f-8e6e-42b4-94d5-c3cd8dc29ed7|result|fix-mission-control-restart-storm-500er-aufl-sen-restart-storm-wurde-auf-port-30 -->
- 2026-04-13: [UI] Spark Relief im Agents-/Team-UI sichtbar integrieren: Spark Relief ist jetzt als eigener Agent in der Team-UI sichtbar, mit expliziter Relief-vor-Forge-Eskalationssemantik und Taskboard-Unterstützung für die Zuweisung. ## Betroffene V <!-- mc:auto-decision:110f5547-4131-4d1a-a162-472207f30c28|result|ui-spark-relief-im-agents-team-ui-sichtbar-integrieren-spark-relief-ist-jetzt-al -->
- 2026-04-13: [Ops] Dispatch- und Recovery-Crons auf Effizienz trimmen: P1/P2 umgesetzt: dispatch-router-cron auf 15 Minuten reduziert, unnötige Recovery-Crons bleiben deaktiviert; erwartete Cron-Last beim Routing sinkt um 66.7% ohne Dispatch-Regressio <!-- mc:auto-decision:21df35da-3eff-4007-8e29-51618daefc5e|result|ops-dispatch-und-recovery-crons-auf-effizienz-trimmen-p1-p2-umgesetzt-dispatch-r -->
- 2026-04-13: [Spark Relief] Agent-Definition + Routing/Board-Regeln umsetzen: Spark Relief ist als dedizierter Agent mit codex-spark modelliert, Routing aktiv und kritische Spark-Fälle werden hart zu Forge eskaliert inkl. Handoff-Block. ## Was wurde gemacht  <!-- mc:auto-decision:861fbdaa-b927-43a5-a183-b0dabcff38d9|result|spark-relief-agent-definition-routing-board-regeln-umsetzen-spark-relief-ist-als -->
- 2026-04-12: [Audit] System Health & Code Quality: Audit abgeschlossen: Kritische Findings identifiziert (wiederholte 500er/Service-Restart-Storm, Secret in Logs), 6 TypeScript-Fehler, keine Cron-Jobs mit consecutiveErrors>0, mehre <!-- mc:auto-decision:55714389-86bf-4b31-b23c-2dc296a80642|result|audit-system-health-code-quality-audit-abgeschlossen-kritische-findings-identifi -->
- 2026-04-12: [RCA] worker-monitor nimmt frisch dispatchte Tasks nicht in echte Runs auf: Root Cause bestätigt: worker-monitor markiert Tasks via /api/worker-runner als active, spawned aber keinen echten Run in ~/.openclaw/subagents/runs.json; dadurch bleiben Tasks ohne <!-- mc:auto-decision:1d8f39d8-4eeb-4671-8851-c455eb5ed3ae|result|rca-worker-monitor-nimmt-frisch-dispatchte-tasks-nicht-in-echte-runs-auf-root-ca -->
- 2026-04-09: MC root-cause documented (`middleware-manifest`, dynamic costs page handling) and production build path validated.
- 2026-04-09: A2 remains blocked until `expectsCompletionMessage` write-path is proven and corrected.
- 2026-04-08: Phase 3 Sprint 1-3 accepted as complete; self-healing/monitoring baseline established.
- 2026-04-08: Dual-subscription model strategy adopted (MiniMax primary, Codex/Opus escalation paths).
- 2026-04-12: Strikte Delegationsregeln in alle Agent-working-contexts eingebaut — Atlas delegiert immer, handelt nie selbst technisch.
- 2026-04-12: Modell-Zuweisung neu geregelt — Atlas+Forge+Lens auf OpenAI Pro (GPT-5.4/5.3), James+Pixel+Flash auf MiniMax M2.7-HS. Noch nicht live in openclaw.json — Forge-Task ausstehend.
- 2026-04-12: Forge-Opus läuft über Anthropic API Key (nicht OAuth). OAuth gilt nur für Atlas/Sonnet via sync-cron.
- 2026-04-12: Execution Contract als Pflichtformat für alle Tasks formalisiert — worker-runner lehnt Tasks ohne task id/objective/definition of done/return format ab.
- 2026-04-12: Sprint Autonomie-Basis erstellt und code-verifiziert — zwei echte Lücken: kein Dispatch-Loop, kein formalisierter Execution Contract.
- 2026-04-12 Abend: Phase-4-Sprint im Closeout — Build ✅, Vitest 135 ✅, E2E 9/9 ✅. Letzter James Gate-Check läuft auf Stand afa88eb.
- 2026-04-12 Abend: Board erstmals clean seit Backup-Restore — failed=0, done=161 (+37), assigned=6, draft=1.
- 2026-04-12 Abend: Root-Cause Phase 4 war echte Integrationslücken (Runtime-Libs, App-Router-Basis, leere Task-Routen) — nicht nur Testnoise.
