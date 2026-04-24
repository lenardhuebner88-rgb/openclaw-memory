# _agents/codex

Codex-Home im Vault.

## Zweck
- `daily/` — knappe Tages-/Session-Notizen
- `plans/` — konkrete Arbeits- und Umsetzungspläne
- `scratch/` — temporäre Spikes, Entwürfe, Wegwerf-Artefakte

## Regeln
- Neue Codex-Artefakte nur in `daily/`, `plans/` oder `scratch/` ablegen.
- Keine Dateien lose direkt unter `_agents/codex/`, außer dieser `README.md`.
- Keine fremden Agent-Bereiche beschreiben (`_agents/claude-code/`, `_agents/OpenClaw/` etc.).
- Wenn ein Artefakt dauerhaft relevant wird, von `scratch/` nach `plans/` oder `daily/` heben.

## Retrieval-Reihenfolge
1. `plans/` für aktive Arbeitslogik
2. `daily/` für kurze Verlaufs-/Kontextnotizen
3. `scratch/` nur bei Bedarf

## Zusammenarbeit mit Atlas/Claude
- Gemeinsame Koordination läuft über `_agents/_coordination/`
- Operative Fragen zuerst dort oder in den jeweiligen Plan-Dateien klären
