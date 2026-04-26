---
type: briefing
prepared-by: claude-main
intended-trigger: /meeting-debate adversarial-review-meeting-bewertung
purpose: Eingangsdokument für externes Adversarial-Review der Reviewer-Bewertung des /meeting-debate-Setups
related-files:
  - 03-Agents/agent-team-meetings-plan-2026-04-24.md (superseded)
  - 03-Agents/_coordination/HANDSHAKE.md (SSoT)
  - 03-Agents/_coordination/meetings/README.md (SSoT)
---

# Briefing — Adversarial Review der `/meeting-debate`-Bewertung

## Hintergrund

Operator (lenard) bat am 2026-04-25 um eine fundierte Bewertung des `/meeting-debate`-Setups inklusive Web-Quellen. Nach erstem Live-Audit wurde die Bewertung in **3 Punkten revidiert** (Mea-Culpa zu Mode-Tag-Interpretation, HANDSHAKE Section 6 vorhanden, Cron-Layer-15 bewusst weggelassen). Hebel 1+2 (Plan-Doc als superseded markieren + Quellen-Hygiene) wurden umgesetzt — die revidierte Bewertung ist Anhang B.

Dieses Briefing ist Eingangsdokument für `/meeting-debate adversarial-review-meeting-bewertung`. Codex (OpenAI-Provider, heterogene Modell-Stimme nach ICLR-2025-MAD-Eval) ist Hauptchallenger; Lens (MiniMax) als Observer für Cost/Reality-Check; Atlas als Chairman.

## Pflicht-Output-Schema (von Codex zu liefern)

```
## CONFIRMED  — Reviewer hat recht (mit Quelle)
## DISPUTED   — Reviewer falsch oder überzogen (mit Quelle ODER Logik)
## MISSED     — Reviewer hat übersehen (min. 3 Einträge)
## NET VERDICT — 3-5 Sätze, eine konkrete Empfehlung
## CONFIDENCE — pro Sektion A/B/C/D: high/medium/low + Begründung
```

---

## Anhang A — Adversarial-Prompt

**Rolle:** Adversarial Reviewer. Kein höfliches Zustimmen, keine "balanced view". Jeden Punkt aktiv falsifizieren versuchen — durch Quellen-Gegenprüfung, Logik-Lücken, oder übersehene Aspekte.

**Hard Rules:**
- Keine Diplomatie-Floskeln ("insgesamt solide, aber…")
- Jede Behauptung braucht Quelle (URL/Paper-ID) oder ist als "Hypothese" markiert
- Bei nicht-verifizierbarer Quelle: explizit "nicht verifiziert" sagen, nicht extrapolieren
- Form ist kein Argument — der Reviewer-Vorlage nicht folgen, nur weil sie strukturiert wirkt

### Prüfaufträge

**A. Quellen-Faktcheck (R49-Pflicht):**
1. CoVe / "+23% GPQA / CorrectBench 2025" — arxiv 2309.11495 prüfen. Gibt es Follow-Up der CoVe auf GPQA testet? Existiert "CorrectBench 2025"?
2. MAST "3 vs. 5 Kategorien" — arxiv 2503.13657. Reviewer sagt 3 Kategorien, 14 modes. Stimmt das wörtlich?
3. ICLR-2025 MAD-Eval — Paper oder Blogpost? Reviewer-Wiedergabe ("MAD verliert meist gegen SC, Heterogenität hilft manchmal") fair? Andere 2025-Studien (Mixture-of-Agents) prüfen
4. DoorDash/Lanham 2025 — gibt es "Lanham 2025" zu Token-Attribution? Wenn nein: bestätigen

**B. Live-Audit-Verifikation** (SSH-Zugang via `ssh homeserver` ist da):
5. Mode-Verteilung in `_coordination/meetings/` — tatsächlich 16/18 als debate getagged?
6. Inhalt vs. Tag — Reviewer sagt "Files SIND korrekt getagged, ich (Reviewer) habe Topic mit Mode verwechselt". Files lesen, beurteilen ob Reviewer fair zu sich war
7. Codex-Files in `_coordination/live/` statt `meetings/` — Schema-Verletzung oder legitimer separater Use-Case?
8. `99-Templates/template-meeting.md` — wirklich nicht da?
9. HANDSHAKE.md Section 6 — korrekt vom Reviewer beschrieben (Lens, 30k/80k/20k, Bounded Two-Loop)?

**C. Architektur — wo ist Reviewer zu absolut?**
10. "Homogene Claude-Subagent-Debate ist Token-Burn" — Subagents haben unterschiedliche Rollen-Prompts (Auditor/Architekt/Sceptic). Ist "homogen" hier modell-homogen oder rollen-homogen? Wichtig für ICLR-Bezug
11. CoVe als Cron-Nachbrenner — CoVe ist Inference-Time-Pattern, kein Post-Hoc-Audit. Ist Reviewer-Forderung "Cron-Verifikation" überhaupt CoVe oder eher Fact-Checking-Pipeline?
12. OWASP ASI08 Mitigationen (Circuit Breaker, Tenant-Isolation) — Solo-Setup, max 1 Operator. Realistisch oder Overkill?

**D. Empfehlungs-Priorisierung:**
13. P0 (Quellenkorrektur) zuerst statt fehlende Deliverables — richtig?
14. codex-plugin-cc — entweder installieren ODER Empirie revidieren. Gibt es dritten Weg (z.B. aktueller Discord-Bot bleibt, wird ins Audit integriert)?
15. **Übersehenes Risiko** (mind. 3 Einträge): Datenschutz (interne Pfade in Files), Race-Conditions, Long-Term-Storage-Wachstum (18 Files/Tag → ~6500/Jahr), Search-/Recall-Probleme, andere

---

## Anhang B — Reviewer-Bewertung (Prüfobjekt, revidiert nach Live-Audit)

### TL;DR

Plan ist architektonisch solide (3-Layer-Trennung, Anti-Goals, Phasen-Roadmap), aber die Empirie-Begründung enthält drei nicht-verifizierbare oder falsch zitierte Quellen — ironisch da R49 als Guardrail genannt wird. Live-Implementation ist **weiter als das Plan-Doc** behauptet: HANDSHAKE Section 6 + meetings/README sind faktisches Schema; Discord-Trigger live; Lens als 3. Observer (3-Modell-Heterogenität); Token-Tracking pro-Meeting in Frontmatter statt via Cron (R50-konform). Plan-Doc ist deshalb superseded — HANDSHAKE ist Single-Source-of-Truth.

### 1. Faktcheck der Plan-Quellen

| # | Plan-Behauptung | Realität | Verdikt |
|---|---|---|---|
| 1 | "ICLR 2025 MAD-Eval — heterogene Modelle = robust, schlägt Single-Agent" | ICLR-Blogpost (kein Paper): "current MAD frameworks fail to consistently outperform simple single-agent test-time computation strategies"; Heterogenität "does not always have positive influence" | Überverkauft |
| 2 | "CoVe +23% GPQA-Accuracy (CorrectBench 2025)" | CoVe-Paper (arxiv 2309.11495, ACL Findings 2024) testet auf Wikidata, MultiSpanQA, longform — nicht GPQA. "CorrectBench 2025" nicht auffindbar | Fabriziert / R49-Verstoß |
| 3 | "MAST-Taxonomie, 5 Failure-Kategorien" | arxiv 2503.13657 definiert **3 Kategorien** mit **14 sub-modes**, basierend auf 150 Traces, κ=0.88 | Falsch zitiert |
| 4 | "karpathy/llm-council 3-Stage mit Anonymisierung" | Stimmt | OK |
| 5 | "openai/codex-plugin-cc offizielles Plugin" | Existiert offiziell, Slash-Commands stimmen | OK |
| 6 | "OWASP ASI08 2026 Cascading Failures" | Korrekt zitiert; Mitigationen (Circuit Breaker / Fan-Out-Cap / Tenant-Isolation) aber nicht implementiert | OK aber nicht umgesetzt |
| 7 | "DoorDash/Lanham 2025 Token-Attribution" | DoorDash hat "budgeting the loop"-Pattern; "Lanham"-Co-Autor in Suche nicht auffindbar | Halb-richtig / unverifiziert |

### 2. Live-Status

**Vorhanden:**
- HANDSHAKE.md Section 6 (sehr ausführlich — Lens als MiniMax-Observer, Bounded Two-Loop mit Turn-Lock, Budgets 30k/80k/20k pro Modus)
- meetings/README.md (Modi-Tabelle, Retrieval-Reihenfolge, Signaturen)
- 18+ Meeting-Files in `_coordination/meetings/` seit 2026-04-24
- File-Locking (`.lock`) — mitigiert Risiko #7
- Naming-Convention exakt befolgt
- Token-Log-Datei (8185 B), Token-Tracking aber pro-Meeting in Frontmatter (`tracked-tokens: <n>`), nicht via Cron
- Discord-Trigger live via `openclaw-discord-bot.py` + `meeting-runner.sh`

**Fehlend:**
- `99-Templates/template-meeting.md` — Phase-1-Deliverable nie erstellt (aber HANDSHAKE+README sind faktisch Schema)
- `_agents/codex/` — Folder leer trotz HANDSHAKE Section 2 Deklaration als Codex-Home; Codex-Content liegt in `_coordination/live/` und `codex/plans/`
- `codex-plugin-cc` nicht installiert — Codex läuft via Discord-Bot, nicht via Claude-Code-Plugin

### 3. Mea-Culpa zur ersten Bewertungsrunde

Drei Punkte musste der Reviewer revidieren:
- **"Mode-Drift: 16/18 falsch als debate getagged"** → falsch. Files mit Topic `meeting-council-safe-mode` sind Meta-Debates ÜBER Council-Features, nicht Council-Meetings. Mode-Tag korrekt
- **"HANDSHAKE Section 6 fehlt vermutlich"** → falsch. Section ist sehr ausführlich
- **"Cron Layer 15 fehlt"** → falsch. HANDSHAKE explizit "Token-/Runner-Crons nur mit separatem Operator-Go" — bewusst weggelassen, R50-konform

### 4. Architektonische Bewertung

**Stark:** 3-Layer-Trennung, Append-only Markdown, Anti-Goals (kein Framework-Rewrite), Karpathy-3-Stage korrekt übernommen, Hard-Limits quantifiziert.

**Schwach:** Empirie-Begründung trägt nicht (siehe Faktcheck). Wenn ICLR-Aussage gilt — homogenes MAD verliert gegen Single-Agent + SC — dann sind Claude-Subagent-Debates ohne Codex/Lens wahrscheinlich Token-Burn. Aktuell ist 3-Modell-Heterogenität (Claude+Codex+Lens) live, aber NICHT in jedem Meeting durchgesetzt. CoVe-Verify-Log existiert konzeptuell, Operationalisierung unklar.

### 5. Top-Hebel (revidiert) und Status

| # | Hebel | Status |
|---|---|---|
| 1 | Plan-Doc als superseded markieren + HANDSHAKE als SSoT | UMGESETZT 2026-04-25 |
| 2 | Quellen-Hygiene im Plan-Doc (CoVe, MAST, ICLR, Lanham) | UMGESETZT 2026-04-25 |
| 3 | `_agents/codex/`-Drift in HANDSHAKE Section 2 | OFFEN — Operator-Decision |
| 4 | template-meeting.md schreiben | SKIP — HANDSHAKE+README defacto Schema |
| 5 | Memory-Datei updaten | UMGESETZT 2026-04-25 |
| 6 | OWASP ASI08-Mitigationen für Council | OFFEN — vor erstem produktivem Council |

### Sources

- [ICLR-2025 MAD-Eval Blogpost](https://d2jud02ci9yv69.cloudfront.net/2025-04-28-mad-159/blog/mad/)
- [CoVe (arxiv 2309.11495)](https://arxiv.org/abs/2309.11495)
- [MAST (arxiv 2503.13657)](https://arxiv.org/abs/2503.13657)
- [karpathy/llm-council](https://github.com/karpathy/llm-council)
- [openai/codex-plugin-cc](https://github.com/openai/codex-plugin-cc)
- [OWASP Top 10 Agentic 2026 ASI08](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)

---

**Trigger nach Briefing-Ablage:**
```
/meeting-debate adversarial-review-meeting-bewertung
```
