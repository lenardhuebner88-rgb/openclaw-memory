# Plan: QMD OpenRouter Embedding — 2026-04-20

## Status

| Item | Status |
|------|--------|
| Script existiert | ✅ `/home/piet/.openclaw/scripts/qmd-openrouter-embed.py` |
| vec0 Extension | ✅ vorhanden |
| OpenRouter Key | ✅ `sk-or-v1-109511...` |
| Cron-Wrapper | ✅ `/home/piet/.openclaw/scripts/qmd-openrouter-embed-cron.sh` |
| Cron-Job | ⏳ noch nicht aktiv |

## Was das Script macht

1. Liest alle Dokumente aus QMD's SQLite-DB (`~/.cache/qmd/index.sqlite`)
2. Findet Docs OHNE Vector-Embeddings (`hash NOT IN content_vectors`)
3. Chunked Text in 900-Token-Blöcke mit 15% Overlap
4. Ruft `text-embedding-3-small` via OpenRouter auf
5. Schreibt Vektoren in beide Tabellen:
   - `content_vectors` (Metadaten)
   - `vectors_vec` (vec0 Binary Blob)

## Kosten

- `text-embedding-3-small`: $0.02 / 1M tokens
- Geschätzt ~2.000 Chunks × ~200 Token = $0.000008 pro Run
- QMD hat aktuell 654 Docs, 1.866 Chunks → <$0.01 pro Vollindex

## Cron-Setup

**Aktuell:** nur `qmd update` (Text-Reindex, 30min), KEINE Vector-Embeddings.

**Neu:** nach jedem `qmd update` auch Embedding-Run:

```
*/30 * * * * flock -n /tmp/qmd-update.lock /home/piet/.local/lib/node_modules/@tobilu/qmd/qmd update >> /home/piet/.openclaw/workspace/logs/qmd-update-cron.log 2>&1
*/30 * * * * flock -n /tmp/qmd-openrouter-embed.lock /home/piet/.openclaw/scripts/qmd-openrouter-embed-cron.sh >> /home/piet/.openclaw/workspace/logs/qmd-openrouter-embed.log 2>&1
```

Beide parallel (30min Lock verhindert Overlaps).

## Alternativen (aus Chat)

| Option | Aufwand | Zeit | Kosten |
|--------|---------|------|--------|
| A: OpenRouter Quick-Script | 30min | sofort | $0.10-0.30 |
| B: Ollama + QMD-GPU | 15min Setup + Code | komplex | gratis |
| C: Einfach warten | 0 | 37min | gratis |
| D: QMD-Embedding API-Support | 1-2h Dev | 1-2h | gratis |

**Entscheidung:** Option A (OpenRouter Script) — bereits implementiert und lauffähig.

## Offen

- [ ] Cron-Job aktivieren (crontab edit)
- [ ] Ersten Run testen (leerer Run erwartet — alle 654 Docs sind aktuell)
- [ ] QMD Status prüfen nach erstem erfolgreichem Run mit echten pending Docs
