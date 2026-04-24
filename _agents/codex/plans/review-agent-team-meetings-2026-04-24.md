---
status: stop
owner: codex
created: 2026-04-24T21:20:00Z
source-plan: /home/piet/vault/03-Agents/agent-team-meetings-plan-2026-04-24.md
decision: no-go-for-build-without-amendments
---

# Review: Agent-Team-Meetings 2026-04-24

## TL;DR

**No-go fuer Phase-1-Build in diesem Lauf.**

Der Plan ist in der Richtung brauchbar, aber zwei zentrale empirische Claims sind zu stark oder falsch zugeordnet:

1. Der ICLR-2025-MAD-Blog sagt nicht "heterogene Modelle schlagen Self-Consistency robust", sondern: MAD-Frameworks schlagen CoT/Self-Consistency **nicht konsistent**; heterogene Modellkombinationen sind nur ein vielversprechender Future-Direction-Befund.
2. CorrectBench stuetzt "CoVe +23% GPQA" nicht. Die Projekt-Tabelle zeigt CoVe auf GPQA mit **+18.85**, Self-Refine mit **+22.13**. Der Plan mischt Methode und Wert.

Zusatzproblem: Das lokale Cron-/Defense-System ist nicht mehr "14 aktive Defense-Crons" im simplen Sinne. Mehrere Soll-Layer sind systemd-migriert oder durch Memory-Orchestrator superseded; ein neuer */5-Cron als "Layer 15" waere ohne Cron-Konsolidierung zu invasiv.

## Verifizierte Fakten

### Empirie

- **MAD-Eval / ICLR Blogposts 2025:** Quelle: https://iclr-blogposts.github.io/2025/blog/mad/  
  Verifiziert: Der Blog evaluiert 5 MAD-Frameworks auf 9 Benchmarks und kommt zu dem Schluss, dass aktuelle MAD-Methoden CoT/Self-Consistency nicht konsistent schlagen. Relevante Stellen: Linien 21-23, 48-50, 91-115, 132-134 im Web-Fetch.

- **Heterogene Modelle:** Quelle: gleicher ICLR-Blog.  
  Verifiziert: Kombinationen verschiedener Foundation Models koennen bessere Accuracy zeigen; der Blog formuliert das aber als "valuable future direction", nicht als robustes Gesetz. Relevante Stellen: Linien 110-115.

- **CorrectBench:** Quellen: https://correctbench.github.io/ und https://openreview.net/forum?id=956KYtqwcU  
  Verifiziert: CorrectBench ist NeurIPS-2025 Datasets/Benchmarks und analysiert Self-Correction. Projektseite zeigt CoVe GPQA **37.41 (+18.85)** und Self-Refine GPQA **40.69 (+22.13)**. OpenReview beschreibt allgemeiner, dass Self-Correction helfen kann, aber Effizienz kostet.

- **MAST / arXiv 2503.13657:** Quelle: https://arxiv.org/abs/2503.13657  
  Verifiziert: Paper existiert. Es beschreibt MAST-Data mit 1600+ Traces, 7 Frameworks, MAST-Taxonomie, 14 Failure-Modes in 3 Kategorien. Plan-Claim "5 Failure-Kategorien" ist so nicht korrekt; die arXiv-Abstract-Version nennt 3 Hauptkategorien und 14 Modi.

- **Karpathy/LLM-Council:** Quelle aus WebSearch zeigt das Pattern als 3-Stufen-LLM-Council mit anonymem Peer-Review, aber ich habe in dieser Runde keine Primärquelle mit stabiler offizieller Repo-Line verifiziert. Confidence deshalb nur Medium.

### Codex-Technik

- **`openai/codex-plugin-cc` existiert.** Quelle: https://github.com/openai/codex-plugin-cc  
  Verifiziert: README beschreibt `/codex:review`, `/codex:adversarial-review`, `/codex:rescue`, `/codex:status`, `/codex:result`, `/codex:cancel`, `/codex:setup`. Requirement: ChatGPT-Subscription oder OpenAI API key. Latest Release im Search-Snippet: v1.0.3, 2026-04-08.

- **Codex OAuth/ChatGPT-Pro ist plausibel.** Quellen: OpenAI Help/Docs  
  `Using Codex with your ChatGPT plan`: Codex ist in Plus/Pro/Business/Edu/Enterprise enthalten; Sign-in mit ChatGPT ist supported.  
  `Codex Authentication`: CLI/IDE unterstuetzen ChatGPT Sign-in und API key; ChatGPT ist Default, wenn keine Session vorliegt.

- **Codex MCP Support ist real.** Quelle: OpenAI Codex MCP docs + lokale CLI.  
  Web: Codex unterstuetzt STDIO-Server und Streamable HTTP-Server mit Bearer/OAuth.  
  Lokal: `codex mcp add --help` zeigt `--url` fuer streamable HTTP und `-- <COMMAND>` fuer stdio; `codex mcp-server` startet Codex als stdio MCP Server.

- **AGENTS.md / Hooks / Subagents / Sandbox-Tiers existieren.** Quellen: OpenAI Codex docs + lokale CLI.  
  AGENTS.md wird vor Arbeit gelesen; Hooks koennen u.a. PreToolUse/Stop verarbeiten; Subagents sind in aktuellen Codex-Releases default aktiv, aber explizit anzufordern; Sandbox/Approval-Kombinationen sind dokumentiert.

### Lokale Infrastruktur

- **HANDSHAKE.md existiert und hat aktuell nur §§ 1-5.**  
  Datei: `/home/piet/vault/03-Agents/_coordination/HANDSHAKE.md`

- **`_coordination/meetings/` existiert noch nicht.**  
  Command: `test -d /home/piet/vault/03-Agents/_coordination/meetings; echo $?` -> `1`

- **`99-Templates/template-meeting.md` existiert noch nicht.**  
  Command: `test -f /home/piet/vault/99-Templates/template-meeting.md; echo $?` -> `1`

- **Crontab ist nicht der einfache 14-Layer-Sollstand.**  
  Command: `crontab -l -u piet` zeigt viele weitere aktive Jobs; `auto-pickup`, `worker-monitor`, `session-freeze-watcher`, `stale-lock-cleaner` sind laut Kommentar systemd-migriert; mehrere Memory-Solljobs sind durch `memory-orchestrator` superseded.

## Widerlegte oder fragwuerdige Claims

### F1 - "ICLR 2025 MAD-Eval: heterogene Modelle schlagen Self-Consistency"

**Status:** widerlegt in der starken Form.

Evidence:
- ICLR-Blog Fazit: aktuelle MAD-Frameworks schlagen CoT/SC nicht konsistent.
- Heterogenitaet wird als moegliche Future Direction und lokaler positiver Befund beschrieben, nicht als robuste allgemeine Aussage.

Impact:
- Debate als Standard "weil empirisch klar ueberlegen" waere ueberverkauft.
- Korrekte Ableitung: Heterogene 2-Agent-Debate ist fuer adversarial review plausibel, aber nur mit engen Scopes, CoVe und Budget-Cap.

Fix-Vorschlag:
- Plan-Claim ersetzen durch: "Heterogene Modelle koennen in einzelnen MAD-Konfigurationen helfen; Current MAD ist gegen SC/CoT nicht robust ueberlegen."

Confidence: High

### F2 - "CorrectBench 2025: CoVe +23% GPQA"

**Status:** falsch zugeordnet.

Evidence:
- CorrectBench-Projektseite: CoVe GPQA `37.41 (+18.85)`.
- Self-Refine GPQA `40.69 (+22.13)`.

Impact:
- CoVe bleibt sinnvoll als Verify-Phase, aber der konkrete +23%-Claim ist nicht sauber.

Fix-Vorschlag:
- Claim auf "CorrectBench zeigt fuer CoVe +18.85 GPQA; Self-Refine erreicht +22.13 GPQA; Effizienz-Kosten beachten" aendern.

Confidence: High

### F3 - "arxiv 2503.13657 MAST-Taxonomie (5 Failure-Kategorien)"

**Status:** fragwuerdig/falsch in der Zahl.

Evidence:
- arXiv-Abstract: 14 Failure-Modes, geclustert in 3 Kategorien: system design issues, inter-agent misalignment, task verification.

Impact:
- Meeting-Template sollte nicht "5 Kategorien" hart kodieren.

Fix-Vorschlag:
- Template mit optionalem MAST-Block: `system-design`, `inter-agent-misalignment`, `task-verification`, plus freie `failure-mode`-Liste.

Confidence: High

### F4 - Review-Modus widerspricht neuem Deliverable

**Status:** Plan-intern inkonsistent.

Evidence:
- Plan sagt bei Review: "kein separates Meeting-File noetig".
- Operator fordert in diesem Auftrag explizit Pilot-Meeting-Output in `_coordination/meetings/...review_memory-L3-audit.md`.

Impact:
- Review-Modus braucht doch ein Meeting-File, mindestens fuer Pilot/Audit-Gates.

Fix-Vorschlag:
- Review-Modus: "Inline nur fuer leichte Pre-Commit-Checks; Meeting-File Pflicht fuer Audit-/Architecture-Review."

Confidence: High

### F5 - "Defense-Layer 15 Cron */5" ist lokal nicht small-risk

**Status:** gebrochenes Infra-Versprechen in der aktuellen Form.

Evidence:
- `crontab -l -u piet` zeigt bereits viele aktive Jobs und mehrere systemd/superseded-Kommentare.
- Neuer Cron kann eingefuegt werden, aber nicht als triviale "Layer 15"-Ergaenzung ohne Konsolidierungs-Entscheidung.

Impact:
- Zusaetzlicher */5-Cron erhoeht Cron-Rauschen und Ownership-Komplexitaet.

Fix-Vorschlag:
- Erst read-only Script + manuelle Probe bauen; Cron-Eintrag als Amendment/Operator-Approval, oder in bestehenden `memory-orchestrator`/ops monitor integrieren.

Confidence: High

## Technische Luecken

- Kein klarer File-Lock-Mechanismus fuer Meeting-Files. Append-only reicht nur, wenn Chairman sequenziell schreibt.
- Token-Tracking ist ohne reale token usage pro Agent nur approximiert. Frontmatter `token-budget` plus `tracked` muss klar als Schaetzung markiert werden.
- Council mit 5-7 Agents und 50k Tokens ist knapp. Bei 7 Teilnehmern bleiben netto nur ca. 7k pro Agent inkl. Synthese/Verify. Realistischer Default: Debate 30k, Review 20k, Council 80k hart capped mit 64k Warnung.
- Optionaler Sonntags-Review darf nicht automatisch alle Agents triggern. Er muss read-only inventory + Vorschlagsliste bleiben.
- Codex-Plugin Review-Gate kann laut Plugin-README Langlauf-Loops und Usage-Limits belasten; nicht default aktivieren.

## Codex-spezifische Anpassungen

- Codex-Auth: OAuth/ChatGPT-Pro ist korrekt als Default-Lane; API-Key nur als Fallback.
- Codex-Plugin wird nicht von Codex selbst installiert; Operator/Claude Code macht Phase 2.
- `/codex:review` ist read-only und nicht steerable; fuer fokussierte Architekturkritik braucht es `/codex:adversarial-review`.
- Codex Subagents existieren, aber fuer diesen Vault-Meeting-Plan sollten sie nicht automatisch/rekursiv genutzt werden. Sonst kollidiert das mit Token-Budget und Coordination.

## Alternative Vorschlaege

1. Phase 1 ohne Cron starten: Template + meetings README + HANDSHAKE §6 + Pilot-Review + manuelles Token-Log. Cron erst nach einem erfolgreichen Pilot.
2. Debate bleibt strikt 2-Agent: Claude-Seite vs Codex. Andere Agents liefern nur Input-Artefakte oder Observer-Notizen, nicht volle Debate-Turns.
3. Council als 5-7-Agent nur on-demand und mit 80k Budget, nicht woechentlich.
4. Review-Modus zweistufig: Lightweight inline fuer Diffs, Meeting-File fuer Architektur-/Memory-Audits.
5. CoVe-Verify-Log im Template als Pflichtfeld fuer jeden Pfad/SHA/Session-ID-Claim.

## Entscheidung

**STOP nach Phase 0 wurde ausgeloest und per Discord gemeldet.**  
Operator-Entscheidung danach: **Option A bleibt**.

Freigegeben:
- Phase 1 mit Amendments.
- Safe Scripts fuer Token-Log und Runner.
- Phase-2-Prep-Dokumente.

Nicht freigegeben:
- Crontab-Live-Aktivierung.
- Bot-Restart oder Wechsel des aktiven Discord-Service.
- Direkter Session-Resume in Claude Bot Session `7c136829`.

## Confidence

- Empirie: High fuer MAD/CorrectBench/MAST; Medium fuer Karpathy-Primärquelle.
- Codex-Technik: High fuer Plugin/MCP/Auth/AGENTS/Hooks/Subagents/Sandbox.
- Lokale Infrastruktur: High fuer HANDSHAKE/Cron/Template/Meeting-Dir.
- Budget-Empfehlung: Medium, weil echte Meeting-Token erst nach Pilot messbar sind.
