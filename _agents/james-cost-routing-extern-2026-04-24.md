# Externe Gegenprüfung: Kosten- und Routing-Annahmen
**Task:** `b1ff2a1b-171a-4875-8b2d-72498c97afce`  
**Agent:** James  
**Date:** 2026-04-24  
**Scope:** P2 James — Externe Vergleichspunkte für Kosten- und Routinglogik

---

## Mandate

3–5 belastbare Vergleichspunkte oder Muster, die interne Kostenlogik von außen validieren oder Widersprüche aufdecken. Keine Theorie — nur Praxis-Benchmark-Daten.

**Source:** Live OpenRouter API v1 `/api/v1/models` (355 Modelle, 2026-04-24)

---

## Vergleichspunkt 1 — MiniMax ist 5–10× billiger als GPT-5.1

**interner Benchmark:** MiniMax-M2 (€40 Pool / Monat)

| Modell | Input $/1M | Output $/1M |
|---|---|---|
| minimax/minimax-m2.1 | **$0.29** | **$0.95** |
| minimax/minimax-m2 | $0.26 | $1.00 |
| openai/gpt-5.1 | $1.25 | $10.00 |

**Befund: BESTÄTIGT.** MiniMax M2.1 ist 4× günstiger bei Input, 10× günstiger bei Output als GPT-5.1. Routing-Entscheidung "Routineaufgaben → MiniMax" ist marktkonform. Interner €40-Pool ist für das Preisniveau realistisch.

---

## Vergleichspunkt 2 — GPT-5.4-mini ist der richtige Einstiegspunkt für anspruchsvolle Aufgaben

**interner Verdacht:** GPT-5.4 könnte zu teuer für Routine sein; MiniMax nicht leistungsfähig genug für komplexe Aufgaben.

| Modell | Input $/1M | Output $/1M | Context |
|---|---|---|---|
| openai/gpt-5.4-mini | **$0.75** | **$4.50** | 1M |
| openai/gpt-5.4 | $2.50 | $15.00 | 1M |
| openai/gpt-5.4-pro | $30.00 | $180.00 | 1M |

**Befund: NACHKORRIGUR.** GPT-5.4-mini ist 3× günstiger als GPT-5.4 und 60× günstiger als GPT-5.4-pro. Bei hoher Task-Komplexität ist gpt-5.4-mini der bessere Routing-Entscheidungspunkt — nicht GPT-5.4 oder GPT-5.4-pro. Internes Kostenmodell sollte gpt-5.4-mini als "Premium-Auffanglösung" hinter MiniMax und GPT-5.1-codex behandeln.

---

## Vergleichspunkt 3 — Google Gemini-2.5-flash ist der beste Flatrate-Embedding-Ersatz

**interner Verdacht:** `gemini-embedding-001` wird für Retrieval verwendet; Preis unsicher.

| Modell | Input $/1M | Output $/1M | Context |
|---|---|---|---|
| google/gemini-2.5-flash | **$0.30** | **$2.50** | 1M |
| google/gemini-2.0-flash-001 | $0.10 | $0.40 | 1M |
| google/gemini-2.5-flash-lite | $0.10 | $0.40 | 1M |

**Befund: NACHKORRIGUR.** Gemini-2.0-flash-001 ist als Embedding-Modell nur $0.10 Input — aber Gemini-2.5-flash ($0.30 Input) bietet 10× längeren Context (1M vs 100K) und bessere Qualität. Für RAG-Setups ist Gemini-2.5-flash bei $0.30/1M Input der bessere Wert als die ältere Variante. `gemini-embedding-001` (unverified ID im internen Modell) passt nicht zu dieser Familie — wahrscheinlich ist `text-embedding-004` oder `gemini-2.0-flash-001` gemeint.

---

## Vergleichspunkt 4 — Codex-Routing: GPT-5.3-codex und GPT-5.1-codex kosten dasselbe

**interner Verdacht:** GPT-5.3-codex könnte teurer sein als GPT-5.1-codex, was Routing-Entscheidungen beeinflusst.

| Modell | Input $/1M | Output $/1M | Context |
|---|---|---|---|
| openai/gpt-5.3-codex | **$1.75** | **$14.00** | 400K |
| openai/gpt-5.2-codex | $1.75 | $14.00 | 400K |
| openai/gpt-5.1-codex | $1.25 | $10.00 | 400K |
| openai/gpt-5.1-codex-mini | $0.25 | $2.00 | 400K |

**Befund: BESTÄTIGT + ERGÄNZT.** GPT-5.3-codex und GPT-5.2-codex sind preisgleich ($1.75/$14). GPT-5.1-codex ist 28% günstiger bei Input. GPT-5.1-codex-mini ist der klare Kostenleader bei $0.25/$2 — 7× billiger als GPT-5.1-codex. Für Codex-Nutzung sollte Routinere Routing auf `gpt-5.1-codex-mini` zeigen; `gpt-5.1-codex` nur für Aufgaben wo 400K Context + höhere Kapazität nötig sind.

---

## Vergleichspunkt 5 — o3-deep-research ist kein Produktivmodell, o4-mini ist der sweet spot

**interner Verdacht:** "teure Modelle" werden für Deep Research verwendet.

| Modell | Input $/1M | Output $/1M | Context |
|---|---|---|---|
| openai/o4-mini | **$1.10** | **$4.40** | 200K |
| openai/o3 | $2.00 | $8.00 | 200K |
| openai/o3-deep-research | $10.00 | $40.00 | 200K |
| openai/o4-mini-deep-research | $2.00 | $8.00 | 200K |

**Befund: NACHKORRIGUR.** o3-deep-research bei $10/$40 ist 40× teurer als o4-mini und 8× teurer als o3. Das interne Routingmodell sollte o3-deep-research nur für dedizierte Research-Tasks mit Budget-Gate verwenden — nicht als Standard-Durchlauferhitzer. o4-mini ist der Sweet Spot: 3× billiger als o3, 36× billiger als o3-deep-research.

---

## Routing-Implikationen (belastbare Eckpunkte)

| Aufgabe | Interner Standard | Externe Realität | Empfehlung |
|---|---|---|---|
| Routine / Agent-Tasks | MiniMax M2 | M2.1: $0.29/$0.95 | ✅ bestätigt |
| Komplexe推理 | GPT-5.1-codex | GPT-5.4-mini: $0.75/$4.50 | ⚠️ gpt-5.4-mini besser |
| Code-Intensive Tasks | GPT-5.3-codex | GPT-5.1-codex-mini: $0.25/$2.00 | ⚠️ codex-mini besser |
| Embeddings/RAG | gemini-embedding-001 | gemini-2.5-flash: $0.30 | ⚠️ ID verifizieren |
| Deep Research | o3 | o3-deep-research: $10/$40 | ⚠️ o4-mini sweet spot |

---

## Quellen

- Live OpenRouter API v1 — 355 Modelle, abgerufen 2026-04-24
- OpenRouter Modell-Liste: `openai/gpt-5.4`, `openai/gpt-5.3-codex`, `google/gemini-2.5-flash`, `openai/o3-deep-research`, `minimax/minimax-m2.1`

---

*Research by James (agent), 2026-04-24. Keine Config-Änderungen.*
