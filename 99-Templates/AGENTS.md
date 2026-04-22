# 99-Templates — Vault-Vorlagen

## Zweck

Vorlagen für häufig erzeugte Dokumente. Nutzung via Obsidian Templater oder manuelles Copy.

## Writers

- Lenard (manuell)
- Librarian (wenn neue Template-Patterns kanonisiert werden)

## Rules

- Neue Vorlagen erst dann, wenn ein Format >3x wiederholt auftritt
- Frontmatter-Keys konsistent halten (siehe template-sprint, template-incident als Referenz)
- Keine machine-only-Files hier — wenn Agents Templates brauchen, eigenes `_agents/_templates/`

## Templates

| Datei | Zweck |
|-------|-------|
| [[template-sprint]] | Neuer Sprint-Plan |
| [[template-incident]] | RCA / Post-Mortem Vorlage |
| [[template-handover]] | Session-Handover zwischen Claude-Sessions |
| [[template-kb-article]] | KB-Artikel (L1-KB-Compiler output style) |
| [[template-rule]] | Neue R-Rule |
| [[template-project]] | Neues Projekt in 03-Projects |
| [[template-daily]] | Daily-Note (manual) |

## Frontmatter-Konvention

Alle Templates nutzen YAML-Frontmatter. Gemeinsame Keys:

- `type`: sprint | incident | handover | kb | rule | project | daily
- `status`: planning | active | in-progress | done | deprecated | archived
- `tags`: Liste von `type/*` und `status/*` Namespace-Tags
- `owner`: Verantwortlicher (Agent oder Person)

Datums-Felder immer ISO-8601 (`YYYY-MM-DD` oder `YYYY-MM-DDTHH:mmZ`).
