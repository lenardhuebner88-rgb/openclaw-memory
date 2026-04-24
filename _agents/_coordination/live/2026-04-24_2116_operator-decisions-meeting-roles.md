---
agent: claude-main
started: 2026-04-24T21:16:09Z
ended: 2026-04-24T21:16:09Z
task: Handover note - Operator-Decisions zu Agent-Team-Meeting-Rollen
touching:
  - /home/piet/vault/03-Agents/_coordination/HANDSHAKE.md (Codex soll dort Paragraph 6 anlegen)
  - /home/piet/vault/03-Agents/agent-team-meetings-plan-2026-04-24.md (Grundlage)
operator: lenard
---
# Handover: Operator-Decisions Meeting-Rollen

**Zweck:** Codex liest diese Notiz VOR dem Phase-1-Build (HANDSHAKE Regel 1: live/ zuerst).

## Operator-Entscheidungen 2026-04-24

### 4 Hauptentscheidungen (bereits im Review-Prompt vermerkt)
1. Codex-Auth: OAuth via ChatGPT-Pro-Sub
2. Scope: Phase 1 + Phase 2
3. Trigger: on-demand + optional Sonntags-Review
4. Budget: 50k Tokens pro Meeting (bestaetigt)

### Zusaetzliche Entscheidung zur Teilnehmer-Matrix

**Meeting-Teilnehmer-Pool (6-7 Agents):**
- Atlas        (Orchestrator / Chairman)
- Codex        (External / Adversarial / Review)
- Forge        (Board / Sprint-Execution)
- Pixel        (Mobile / Frontend-Perspektive)
- Lens         (Deep-Research / Analysis)
- James        (Operator-Dashboard / UX)
- Claude Main  (Claude Code auf Windows-Client des Operators — interaktive Session)

**Claude Main Rolle (vom Operator bestaetigt):** Moderator + Voice
- Moderator-Funktion: Trigger-Layer fuer Operator-gestartete Meetings, Orchestriert Agent-Spawns, aggregiert Synthese
- Voice-Funktion: Spricht als "Claude Bot" im Council UND ist Claude-Seite im Cross-Provider-Debate gegen Codex

**Chairman-Matrix (vom Operator bestaetigt):**
- Council  -> Atlas (kennt Sprint-Historie best, Server-intern)
- Debate   -> Claude Main (Operator-Interface, Cross-Provider-Gegenpart zu Codex)
- Review   -> Autor + Codex (Claude Main nur als Trigger/Relay, nicht als Stimme)

**Operator-Override:** Operator kann jederzeit Chairman-Split aendern.

### Signatur-Konvention in Meeting-Files
Jeder Post in Meeting-Markdown bekommt Signatur-Line:
- [claude-main YYYY-MM-DDThh:mmZ]
- [atlas     YYYY-MM-DDThh:mmZ]
- [codex     YYYY-MM-DDThh:mmZ]
- [forge     YYYY-MM-DDThh:mmZ]
- [pixel     YYYY-MM-DDThh:mmZ]
- [lens      YYYY-MM-DDThh:mmZ]
- [james     YYYY-MM-DDThh:mmZ]

### Parallel zu Codex Phase 1 Work
Claude Main (ich) uebernimmt parallel:
- codex-plugin-cc Install in lokaler Claude-Code-CLI auf Windows (nicht Server)
- Voraussetzung fuer Phase 2 Trigger-Phrases

Dieser Install kann und sollte nicht durch Codex geschehen (Plugin lebt in Claude Code, nicht in Codex CLI).

### Was Codex aus dieser Notiz einbauen soll

In HANDSHAKE.md Paragraph 6 Meeting-Modi:
- Teilnehmer-Matrix wie oben
- Chairman-Matrix wie oben  
- Signatur-Konvention wie oben
- Trigger-Phrases bereits aus Plan-V1 uebernehmen

Token-Budget-Defaults bitte begruendet empfehlen:
- Debate (2 Agents, 4-5 Turns):        Richtwert 50k
- Council (5-7 Agents, 3 Phasen):      wahrscheinlich hoeher, Empfehlung?
- Review (2 Agents, 1-2 Turns):        deutlich niedriger, Empfehlung?

### Keine weiteren Operator-Decisions offen
Codex kann mit Phase 1 loslegen sobald der Hauptprompt geladen ist.
