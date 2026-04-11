# Decisions Log

## Active decisions
- 2026-04-10: Receipt blocked task blocked: Needs human decision <!-- mc:auto-decision:receipt-blocked-task|blocked|receipt-blocked-task-blocked-needs-human-decision -->
- 2026-04-10: Layer-3 canonicalized to `/home/piet/vault` root structure; no `OpenClaw-Memory/*` dependency.
- 2026-04-10: Active retrieval chain is `project-state` → `decisions-log` → `checkpoints` → agent `working-context`; daily is opt-in only.
- 2026-04-10: Hermes removed from active agent structure and archived as decommissioned context.
- 2026-04-10: Nested `Openclaw peter` vault path retired from active use to remove retrieval ambiguity.
- 2026-04-09: Result routing follows Discord channel purpose; no default dumping into `#atlas-main`.
- 2026-04-08: Mission Control stays on production service (`next start`) for lower memory and better stability.
- 2026-04-08: Opus stays constrained to high-value cases (root-cause, architecture, severe bugs).

## Historical decisions
- 2026-04-10: P3 Shared State and Working Context autowrite proof: Canonical decision: shared state only for persistent cross-agent facts <!-- mc:auto-decision:p3-autowrite-proof|result|p3-shared-state-and-working-context-autowrite-proof-canonical-decision-shared-st -->
- 2026-04-09: MC root-cause documented (`middleware-manifest`, dynamic costs page handling) and production build path validated.
- 2026-04-09: A2 remains blocked until `expectsCompletionMessage` write-path is proven and corrected.
- 2026-04-08: Phase 3 Sprint 1-3 accepted as complete; self-healing/monitoring baseline established.
- 2026-04-08: Dual-subscription model strategy adopted (MiniMax primary, Codex/Opus escalation paths).


### DEC-20260411-02 — Writer-Strang und P11 als vorerst grün behandeln
- Date: 2026-04-11
- Owner: Atlas
- Status: accepted
- Context: Nach fokussierter Worker-/Board-Entlastung wurden Canonical-Hierarchy-Writer-Fixes, Runtime-Wiring-Fixes und Smokepack-Validierung sequenziell abgearbeitet.
- Decision: Writer-Strang als abgeschlossen behandeln und P11 auf Basis von 7/7 Smokepack-Pass vorerst als grün/faktisch erfüllt führen; keine weiteren Mikro-Fixes ohne neuen roten Smoke oder sichtbaren Nutzerschaden.
- Rationale: Der aktuelle Pack ist grün, Board/Worker-Fokus ist stark reduziert, und weitere Iteration hätte sinkenden Grenznutzen bei steigendem Kontextverbrauch.
- Impact: Nächster Schritt soll ein neuer echter Stability-Fokus sein; Embedding-Quota/Fallback-Qualität nur beobachten.
- Supersedes: 


## 2026-04-09 — Session Updates

### Behoben
- Gateway Crash-Loop (Discord streaming Format)
- Mission Control Crash-Loop (Node v22 + NEXT_DIST_DIR)
- tmux-claude chmod 1777→700
- ChromaDB Docker Container entfernt
- Telegram Bridge: 6 Bugs (NameError, Modell-ID, OAuth, qwen3.5:4b, Typing-Heartbeat, Timeout 300→600s)

### Memory System
- OpenAI Embeddings (text-embedding-3-small) als Provider
- short-term-recall.json von 7386→500 Eintraege truncated
- SQLite tmp files (15x 11MB) bereinigt
- Vault-Support fuer alle Agent-IDs hinzugefuegt

### Infrastruktur
- /home/piet/bin/openclaw Node v22 Wrapper erstellt
- Altes /usr/bin/openclaw geloescht
- vault-sync Timer fuer auto Git-Commits
- HTTP API aktiviert (POST /v1/chat/completions)

### Offene Punkte
1. GitHub SSH Key (~/.ssh/id_github) muss zu Account piet-huebner hinzugefuegt werden
2. NIEMALS npm uninstall -g openclaw ausfuehren - Wrapper nutzen
3. Nach Gateway-Updates Mission Control ggf. neu builden
4. Vault->Embeddings Pipeline fehlt noch