# Tag-Konvention

> Ziel: Tags als Filter nutzbar machen. Namespace `bereich/wert` statt flat.

## Namespaces

### `type/*` — Dokument-Art

`type/sprint` · `type/incident` · `type/handover` · `type/kb` · `type/rule` · `type/project` · `type/daily` · `type/decision` · `type/research`

### `status/*` — Lifecycle

`status/planning` · `status/active` · `status/in-progress` · `status/blocked` · `status/done` · `status/deprecated` · `status/archived`

### `agent/*` — Ownership

`agent/atlas` · `agent/forge` · `agent/lens` · `agent/james` · `agent/pixel` · `agent/spark` · `agent/operator`

### `topic/*` — Thema

`topic/memory-system` · `topic/mission-control` · `topic/observability` · `topic/governance` · `topic/security` · `topic/ci-cd`

### `priority/*` — Optional

`priority/p0` · `priority/p1` · `priority/p2` · `priority/p3`

## Rules

1. **Tags nur in Frontmatter** (`tags: [type/sprint, status/done]`), nicht inline `#foo`
2. **Maximal 5 Tags** pro Dokument
3. **Jedes `type/*` braucht ein `status/*`** (außer `type/kb`)
4. **`agent/*` nur wenn eindeutig ein Agent owner ist**
5. **Nicht-Namespace-Tags** (`#learnings`, `#cron`) nur noch in Legacy-Files — neue Docs nutzen Namespace

## Discord-Cross-Refs

Strings wie `#atlas-main`, `#execution-reports` sind **Discord-Channel-Namen**, keine Obsidian-Tags. Schreibweise-trennung: Discord-Refs in Prosa-Text (werden nicht als Obsidian-Tags behandelt wenn im Body; Vorsicht bei Frontmatter).

## Migration bestehender Tags

Phase 1 (jetzt): neue Dokumente nutzen Namespace.
Phase 2 (später): Bulk-Migration vorhandener `#tasks`, `#learnings`, `#cron` etc. per Librarian-Cron.
