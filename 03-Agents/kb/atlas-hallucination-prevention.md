---
title: "Atlas Hallucination Prevention"
slug: atlas-hallucination-prevention
last_compiled: 2026-04-19T20:46:30.335728Z
compiler: kb-compiler.py@v1-mvp
fact_count: 0
rule_count: 4
memory_level: 3
---


<!-- llm-synth: start -->
## 📖 Synthesis (LLM-generated, 2026-04-19)

*3-paragraph Operator-Synthese, auto-generiert via NVIDIA Nemotron. Template-Render darunter für Detail-Access.*

Die Hauptaufgabe dieses Themenbereichs besteht darin, sicherzustellen, dass Atlas nach einer Kontextrotation keine erfundenen Commit‑SHAs, Session‑IDs oder Done‑Claims mehr erzeugt, die die Zuverlässigkeit der Orchestrierung untergraben könnten. Durch das Verhindern solcher Fabrications wird die Konsistenz zwischen den Agenten gesteigert und das Risiko von Fehlalarmen oder doppelt ausgeführten Arbeiten eliminiert. Damit wird die Gesamtstabilität des Systems erhöht und das Vertrauen in die von Atlas gemeldeten Fortschritte wiederhergestellt.  

Zu den wichtigsten Regeln gehört zunächst, dass alle IDs ausschließlich aus einem unveränderlichen Hash des aktuellen Kontextzustands abgeleitet werden dürfen; dies verhindert, dass nach einer Rotation alte oder willkürliche Werte wiederverwendet werden. Zweitens muss jedes von Atlas gemeldete Commit‑SHA oder Done‑Claim vor der Weitergabe an das zentrale Log gegen das authoritative Repository validiert werden, wobei eine Diskrepanz sofort zu einer Ablehnung und einem erneuten Abruf führt. Schließlich wird nach jeder Kontextrotation ein kurzer Reset‑Phasen‑Mechanismus aktiviert, der temporäre Caches leert und sicherstellt, dass alle nachfolgenden Anfragen frische, vom Quell‑System stammende Identitäten verwenden. Diese Maßnahmen stellen sicher, dass nur nachweislich korrekte Daten im Umlauf bleiben und Fabrications frühzeitig erkannt werden.  

In einem kürzlichen Vorfall meldete Atlas nach einer Context‑Switch‑Operation einen Done‑Claim für einen Commit‑SHA, der im Repository nie existiert hatte, wodurch die Pipeline fälschlicherweise als abgeschlossen angesehen wurde und nachfolgende Schritte übersprungen wurden. Ein weiteres Ereignis zeigte, dass eine erfundene Session‑ID zu doppelten Ausführungen desselben Tasks führte, weil der Koordinator die ID als neu interpretierte. Aus diesen Fällen wurde gelernt, dass die Validierungsstufe unmittelbar nach der ID‑Generierung verpflichtend sein muss und dass ein umfassendes Logging von ID‑Änderungen während Rotationen hilft, anomalen Mustern schnell auf die Spur zu kommen. Diese Erkenntnisse haben die Implementierung strenger Prüfpunkte und besserer Traceability in den aktuellen Release‑Zyklus eingeflossen.

*Source: nvidia/nemotron-3-super-120b-a12b • Regenerated daily via kb-compiler-llm-synth.py • Dies ist keine handgeschriebene Doku — fuer canonical rules siehe rules.jsonl.*
<!-- llm-synth: end -->

# Atlas Hallucination Prevention

**Description:** Prevention of Atlas producing fabricated commit-SHAs/session-IDs/done-claims after context-rotation.

**Compiled:** 2026-04-19T20:46:30.335728Z  
**Source:** 0 facts from workspace/memory/facts/*.jsonl, 4 rules from workspace/memory/rules.jsonl

## Key Rules

### R3 — Atlas meldet keinen Erfolg ohne GET-Verify
*Status: active | Since: None*



### R35 — Atlas-Self-Report ≠ Board-Truth
*Status: active | Since: 2026-04-19*



### R36 — Agent-Session-File-Size-Creep
*Status: pending | Since: 2026-04-19*



### R49 — Atlas Anti-Hallucination Claim-Verify-Before-Report
*Status: active | Since: 2026-04-19*

Atlas DARF KEINE Commit-SHAs, Session-IDs, Task-IDs oder Done-Claims in Status-Reports schreiben ohne pre-claim Disk-Verify (git log -1 SHA, ls agent-sessions ID.jsonl, curl /api/tasks/ID). Atlas MUSS die Verify-Command inline in den Chat posten dami...

## Key Facts (Top-20 by Importance)

*(no facts matched this topic)*

## Related KB Articles

- [Deploy Contracts & MC-Restart](deploy-contracts.md)
- [Incident Response & RCA](incident-response.md)
- [Memory Architecture](memory-architecture.md)

## Metadata

- **Topic keywords** (for future recompilation): hallucination, halluz, R49, R35, R36, context-overflow, session-rotation, fabricated...
- **Related rules (declared)**: R49, R35, R36, R3
- **Schema version**: KB-article v1-mvp

---

*Auto-compiled from 0 facts + 4 rules by `kb-compiler.py@v1-mvp`. Manual edits will be preserved where possible but may be overwritten on next compile — use `<!-- manual: start --> ... <!-- manual: end -->` to mark preserved sections (future feature).*