---
title: Agent-Team-Meetings & Cross-Provider-Kollaboration
type: project
status: planning
started: 2026-04-24
owner: lenard
stakeholders: [Atlas, Main/Claude, Codex, James, Lens, Pixel, Forge]
priority: P1
depends-on:
  - _coordination/HANDSHAKE.md
  - _agents/codex/README.md
related:
  - atlas-autonomy-phase1-phase2-plan-2026-04-22-v1.2.md
tags: [type/project, status/planning, topic/meta-orchestration, topic/multi-agent]
---

# Agent-Team-Meetings — Operativer Plan

## Kernbefund der Recherche

**Cross-Provider-Debate (Claude vs Codex) ist einer der wenigen Multi-Agent-Debate-Fälle, in denen das Pattern empirisch Single-Agent mit Self-Consistency schlägt** (ICLR 2025 MAD-Eval). Homogene Debates (z.B. Claude vs Claude) verlieren dagegen meist gegen einen gut-prompteten Single-Agent mit langem CoT.

**Implikation:** Der Operator-Instinkt, Codex dazu zu holen, ist datengestützt richtig — nicht aus Gefühl, sondern aus Benchmarks. Der Meeting-Nutzen skaliert mit Model-Heterogenität, nicht mit Agent-Count.

## Mission

Strukturierte **Meeting-Modi** über der existierenden `_coordination/`-Infrastruktur, damit Agents (Claude/MC-Subagents + Codex + Atlas) gemeinsam Schwachstellen analysieren und Feature-Diskussionen führen können — mit empirisch belegten Patterns und harten Guardrails.

## Status

- **Pre-Existing:** `_coordination/HANDSHAKE.md` + `_agents/codex/` + live/archive-Sessions laufen bereits.
- **Missing:** Kein formales Meeting-Protokoll (Debate/Council/Review). Kein Anonymisierungs-Mechanismus. Kein Token-Attribution pro Meeting. Kein CoVe-Post-Filter.
- **This plan:** Ergänzt 3 Meeting-Modi + Template + Guardrails auf das bestehende HANDSHAKE.

---

## Architektur: 3 Layer

### Layer A — Runtime (wer spricht)

**Pragmatisch gewählt** (nicht LangGraph/AutoGen/CrewAI — weil bestehendes Claude-Code-Setup):

- **Claude Code Subagents** (SDK `AgentDefinition`) für Claude-seitige Rollen (`Auditor`, `Architekt`, `Sceptic`).
- **Codex CLI** via **`openai/codex-plugin-cc`** (offizielles Plugin) für Codex-Handoffs über Slash-Commands (`/codex:review`, `/codex:adversarial-review`).
- **Atlas** als Orchestrator bleibt wie gehabt.
- **Keine rekursiven Subagents** (Claude SDK erlaubt das ohnehin nicht).

### Layer B — Protocol (wo gesprochen wird)

Auf existierendem `_coordination/`-Board aufbauen:

- Neue Folder: `_coordination/meetings/` (für Meeting-Artifacts).
- File-Naming: `YYYY-MM-DD_HHMM_<mode>_<topic>.md` (`mode` ∈ {`debate`, `council`, `review`}).
- **Append-only Markdown** mit Signatur-Line pro Post: `[claude-auditor 2026-04-24T10:12Z]` / `[codex 2026-04-24T10:14Z]`.
- Parallel: Vault-Memory-MCP-Tags `msg:meeting:<topic>` für maschinelles Recall.
- **Ownership:** Meeting-Files gehören `_coordination/` — keiner der Agents räumt sie um (Handshake-Regel 2 gilt).

### Layer C — Guardrails (was schiefgehen darf)

Harte Limits, die Cost-Explosion und Cascading-Hallucinations verhindern:

1. **Max-Turns pro Meeting:** 6 (2 pro Teilnehmer + 1 Chairman-Synthese + 1 CoVe).
2. **Token-Budget pro Meeting:** 50k Gesamtbudget, Abbruch bei 80%.
3. **Token-Attribution** pro Agent als neue Defense-Cron-Layer 15 (Logging in `/home/piet/.openclaw/workspace/memory/meeting-tokens.log`).
4. **R49 gilt:** Jede Commit-SHA / File-Path / Session-ID im Meeting muss verifiziert sein (sonst Halluzination).
5. **Anonymisierung im Council** (Phase 2): Posts als `[Reviewer A]`, `[Reviewer B]` maskieren, Chairman kennt Mapping.
6. **Hard-Stop Hook:** Bei Budget-Überschreitung → Meeting abbrechen, Teil-Ergebnis speichern.

---

## Meeting-Modi (3 Pattern-Mix)

### Mode 1: Debate — für Schwachstellen-Analyse

**Zweck:** Adversarial Review von Code/Architektur/Memory-Layer.
**Teilnehmer:** Claude-Auditor + Codex (heterogene Foundation-Modelle — Pflicht!).
**Flow:**

1. Operator/Atlas definiert Scope (Files, Commit-Range, Frage).
2. Claude-Auditor verfasst First-Opinion (≤500 tokens).
3. Codex verfasst parallele First-Opinion (≤500 tokens).
4. Beide kritisieren die Gegen-Opinion (Rebuttal-Round, ≤300 tokens).
5. Atlas synthetisiert Konsens/Dissens-Punkte + Action-Items.
6. **CoVe-Nachbrenner:** Alle Claims werden gegen Ground-Truth verifiziert (git log / file-ls / grep).

**Empirie:** +23% GPQA-Accuracy via CoVe; MAD schlägt Self-Consistency bei heterogenen Modellen.
**Output:** `_coordination/meetings/YYYY-MM-DD_HHMM_debate_<topic>.md` + Action-Items als Board-Tasks.

### Mode 2: Council — für Feature-Brainstorming

**Zweck:** Welches Feature bringt uns am meisten weiter? Welches ist Scope-Creep?
**Teilnehmer:** 3-5 Claude-Subagents mit unterschiedlichen Rollen (Architekt, Ops-Engineer, Memory-Specialist, Security-Reviewer) + optional Codex als externe Stimme.
**Flow (Karpathy-Pattern):**

1. **Phase 1 First Opinions:** Jeder schreibt unabhängig eine Meinung (nicht sichtbar für andere).
2. **Phase 2 Review (anonymisiert):** Opinions werden maskiert (`[Reviewer A-E]`) — jeder rankt/kritisiert die anderen.
3. **Phase 3 Chairman-Synthese:** Atlas aggregiert zu finaler Empfehlung mit Dissens-Erwähnung.

**Guardrail:** Anonymisierung verhindert Brand-Favoritismus (Claude-Subagents haben Bias zugunsten `Claude`-gelabelter Antworten).
**Output:** `_coordination/meetings/YYYY-MM-DD_HHMM_council_<topic>.md` + Feature-Ranking.

### Mode 3: Review — für Pre-Commit-Verifikation

**Zweck:** Schnell-Review vor Commit/Deploy. Nicht für Discovery, sondern Safety-Check.
**Teilnehmer:** Atlas (Autor) + Codex (Reviewer) via `/codex:review` oder `/codex:adversarial-review`.
**Flow:** Atlas übergibt Diff → Codex liefert Review → Atlas entscheidet Accept/Rework.
**Empirie:** Das ist der use-case, für den das `codex-plugin-cc` gebaut wurde.
**Output:** Inline-Review-Post im aktuellen `_coordination/live/`-File (kein separates Meeting-File nötig).

---

## Roadmap (3 Phasen)

### Phase 1 — MVP Manual Meeting (2-3h)

- [ ] `99-Templates/template-meeting.md` schreiben (Frontmatter + Sections)
- [ ] `_coordination/meetings/` folder + README mit Modi-Übersicht
- [ ] HANDSHAKE erweitern: neue Section `6. Meeting-Modi`
- [ ] **Pilot-Meeting Debate** manuell durchführen: Topic = `Schwachstellen im Memory-Level-3-Setup (L1-L6)`
- [ ] Token-Log-Cron als Defense-Layer 15 (`meeting-tokens-log.sh` */5min)

**Exit-Kriterium:** 1 erfolgreicher Debate-Durchlauf, Output in Vault, Token-Budget eingehalten.

### Phase 2 — Codex-Plugin-Integration (3-4h)

- [ ] `openai/codex-plugin-cc` in Claude Code installieren (Dokumentation prüfen: tool-restrictions, auth, sandbox)
- [ ] Slash-Commands testen: `/codex:review`, `/codex:adversarial-review`, `/codex:status`, `/codex:cancel`
- [ ] Meeting-Trigger-Phrases definieren:
  - `"Team-Meeting Debate zu <topic>"` → Atlas spawned Debate-Subagents + Codex
  - `"Team-Meeting Council zu <topic>"` → Atlas spawned 4 Subagent-Rollen
  - `"Team-Meeting Review"` → Reine Codex-Review via Plugin
- [ ] Auto-Session-File-Write in `_coordination/live/` bei Meeting-Start (conform zu HANDSHAKE Regel 1)

**Exit-Kriterium:** 1 Debate + 1 Council vollautomatisch abgelaufen, Output-Quality mindestens Niveau Manual-Meeting.

### Phase 3 — Production-Hardening (6-8h, optional)

- [ ] Anonymisierungs-Middleware für Council (Post-Labels rotieren)
- [ ] Meeting-Budget-Hook (Claude-Code-Hook + pre-tool-use) — bei Budget-Überschreitung Hard-Stop
- [ ] MCP-Server `meeting-room` (optional) — Pub-Sub statt File-Polling, falls Latency-Probleme
- [ ] Memory-Integration: jedes Meeting-Fazit als Fact in `facts/YYYY-MM-DD.jsonl` (feed L3 Retrieval-Loop)
- [ ] Dashboard-Section in `memory-dashboard.md`: letzte 5 Meetings + Token-Kosten

**Exit-Kriterium:** Kosten pro Meeting <0.50 USD, Meetings finden ohne Operator-Intervention statt.

---

## Vor- und Nachteile

### Pro

| # | Vorteil | Evidenz |
|---|---------|---------|
| 1 | Cross-Provider-Debate schlägt Single-Agent empirisch | ICLR 2025 MAD-Eval (heterogene Modelle = robuster Gewinn) |
| 2 | Baut auf existierendem HANDSHAKE/Coordination | Kein Rewrite, minimales Risiko |
| 3 | Deckt beide Operator-Ziele ab (Schwächen + Features) | Mode 1 + Mode 2 direkt mappable |
| 4 | Verhindert Sycophancy-Bias in Self-Review | Codex als externe Stimme bricht Echo-Chamber |
| 5 | CoVe reduziert Halluzinationen nachweislich | +23% GPQA (CorrectBench 2025) |
| 6 | Token-Attribution pro Meeting isoliert Cost-Overruns | DoorDash/Lanham 2025 |
| 7 | Nutzt offizielles OpenAI-Plugin — keine Eigenbau-Bridge | codex-plugin-cc hat OpenAI-Maintenance |
| 8 | Council-Anonymisierung mildert Brand-Favoritism | Karpathy-llm-council-Pattern |
| 9 | Append-only Markdown = Git-versionierbar | Review-trail out-of-the-box |
| 10 | Meetings werden als Facts in L3 eingefüttert | Positive Rückkopplung in Memory-Layer |

### Contra / Risiken

| # | Nachteil | Mitigation |
|---|----------|------------|
| 1 | Cost-Explosion bei Multi-Agent-Calls | Hard Token-Budget + Max-Turns-Cap |
| 2 | Cascading Hallucination (Agent A Halluzination wird Agent B Ground-Truth) | R49 greift, CoVe-Post-Filter pflicht |
| 3 | Codex-Plugin = Dependency auf OpenAI-Stack (API-Key + Sub) | Fallback auf Claude-only-Council möglich (Phase 2 graceful degradation) |
| 4 | Homogenes Council (nur Claude-Subagents) verliert laut MAD-Eval gegen Single-Agent | Pflicht: bei Council mindestens ein Codex-Teilnehmer ODER Single-Agent-Mode |
| 5 | Premature Convergence bei Round-Robin ohne Moderator | Chairman-Synthese ist Pflicht, kein flat Round-Robin |
| 6 | Bandwagon/Position-Bias im Council | Anonymisierung + Order-Shuffle |
| 7 | File-Lock-Contention bei parallelem Writing | Turn-basiert (sequenziell pro Meeting), nicht parallel pro File |
| 8 | Verbosity-Bias (lange Posts gewinnen) | Hard Word-Limit pro Post (≤500 tokens First-Opinion, ≤300 Rebuttal) |
| 9 | Kein Framework-Support bei AutoGen/CrewAI-Migration später | Bewusst als Trade-off gewählt — Eigenbau bleibt aber framework-unabhängig |
| 10 | Debugging komplex bei Multi-Turn-Fehler | Meeting-File ist append-only + timestamped = vollständiges Audit |

### Wann NICHT benutzen

- Einfache Bug-Fixes → Single-Agent-Claude mit CoT reicht (und kostet 5x weniger).
- Quick-Greps / Lookups → Overkill.
- Zeitkritische Incidents (P0) → R45 Freeze-Watcher reagiert schneller.
- Tasks mit eng definiertem Scope und klarer Antwort → CoVe allein reicht.

---

## Offene Entscheidungen (Operator-Input nötig)

1. **Codex-Auth:** ChatGPT-Pro-Sub vs. API-Key? (Memory vermerkt: api-key quota exhausted, user prefers OAuth.)
2. **Phase-Scope:** Starten wir mit Phase 1 only (Manual Meeting) oder direkt Phase 1+2? → Empfehlung: 1 erst, dann 2 nach Pilot-Success.
3. **Meeting-Frequenz:** On-demand via Trigger-Phrase oder geplant (z.B. wöchentlich Sonntag nach importance-recalc)?
4. **Anonymisierung sofort oder nachziehen?** Empfehlung: Phase 2 (Council-Rollout), nicht MVP.
5. **Hard-Budget pro Meeting:** 50k Tokens zu viel/zu wenig? (Basierend auf historischen Sprint-Kosten?)

---

## Anti-Goals (explizit nicht in diesem Projekt)

- Kein Rewrite der existierenden Agent-Infrastruktur.
- Kein eigenes Framework (AutoGen/CrewAI/LangGraph) — nur Meeting-Layer on top.
- Kein Real-Time-Streaming zwischen Agents — turn-basiert reicht.
- Kein A2A-Protokoll (Overkill für Solo-Setup).
- Keine rekursiven Subagents (Claude SDK verbietet das ohnehin).
- Keine wöchentliche All-Hands-Meetings mit allen Agents (Token-Kosten explodieren, Signal-to-Noise niedrig).

---

## Referenzen

**Empirie:**

- ICLR 2025 MAD-Eval — Multi-Agent Debate robust nur bei heterogenen Modellen
- CorrectBench 2025 — CoVe +23% GPQA-Accuracy
- arxiv 2503.13657 — Why Do Multi-Agent LLM Systems Fail? (MAST-Taxonomie, 5 Failure-Kategorien)
- karpathy/llm-council — 3-Stage-Pattern mit Anonymisierung
- OWASP ASI08 2026 — Cascading Failures in Agentic AI

**Tools:**

- `openai/codex-plugin-cc` — offizielles Slash-Commands-Plugin für Claude Code
- Claude Agent SDK `AgentDefinition` — Subagents mit Tool-Restrictions
- `doobidoo/mcp-memory-service` — MCP-Pattern für shared Meeting-State (als Referenz, nicht als Dependency)

**Bestehende Infrastruktur:**

- `_coordination/HANDSHAKE.md` — Atlas↔Codex-Handshake (Grundlage)
- `_agents/codex/README.md` — Codex-Home-Structure
- 14 Defense-Crons — Guardrails-Fundament (neue Layer 15 kommt für Meeting-Token-Log)
- R1-R50 Rules — R49 (Anti-Hallucination) + R50 (Session-Lock-Governance) gelten auch in Meetings
