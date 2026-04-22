# Abschlussbericht: QMD OpenRouter Embedding — 2026-04-20

**Typ:** Umsetzung  
**Status:** ✅ Abgeschlossen  
**Dauer:** ~15 min

---

## Was wurde getan

QMD Vector-Embeddings werden jetzt automatisch alle 30 Minuten via OpenRouter (`text-embedding-3-small`) generiert und in QMD's SQLite-DB geschrieben.

### Komponenten

| Komponente | Pfad | Status |
|---|---|---|
| Embedding-Script | `/home/piet/.openclaw/scripts/qmd-openrouter-embed.py` | ✅ Vorhanden |
| Cron-Wrapper | `/home/piet/.openclaw/scripts/qmd-openrouter-embed-cron.sh` | ✅ Neu |
| Crontab-Eintrag | `*/30 * * * *` | ✅ Aktiv |
| Log-Datei | `/home/piet/.openclaw/workspace/logs/qmd-openrouter-embed.log` | ✅ |

### Crontab-Zeile

```
*/30 * * * * flock -n /tmp/qmd-openrouter-embed.lock /home/piet/.openclaw/scripts/qmd-openrouter-embed-cron.sh >> /home/piet/.openclaw/workspace/logs/qmd-openrouter-embed.log 2>&1
```

Läuft ab sofort parallel zu `qmd update` (beide `*/30`).

### Wrapper-Features

- `flock`-basiertes Lockfile (`/tmp/qmd-openrouter-embed.lock`) — verhindert Overlap
- Stale-Lock-Removal (>10min)
- Korrektes Exit-Code-Handling
- Logs nach `/home/piet/.openclaw/workspace/logs/qmd-openrouter-embed.log`
- Backup-Cleanup via `trap`

### Funktionsweise

1. `qmd update` (30min-Cron) — indexed neue/geänderte Markdown-Dateien in QMD's SQLite
2. `qmd-openrouter-embed.py` — findet Docs ohne Vector-Embeddings, generiert Chunks (900 tokens, 15% overlap), ruft `text-embedding-3-small` via OpenRouter auf, schreibt in `content_vectors` + `vectors_vec`

### Kosten

- `text-embedding-3-small`: $0.02 / 1M tokens
- Geschätzt: <$0.01 pro Vollindex (654 Docs, ~1.866 Chunks)
- Vernachlässigbar bei 48 Runs/Tag

### Vorher/Nachher

| | Vorher | Nachher |
|---|---|---|
| Vector-Embeddings | Manuell (oder gar nicht) | Automatisch alle 30min |
| Embedding-Modell | Lokal (GGUF, CPU-intensiv) | OpenRouter API |
| Mechanismus | `qmd embed` (lokal) | `qmd-openrouter-embed.py` via Cron |

### Backup

Crontab gesichert: `memory/crontab.bak-20260420-qmd-embed.txt`

---

## Verification Commands

```bash
# Crontab prüfen
crontab -l | grep qmd

# Log anschauen
tail -f /home/piet/.openclaw/workspace/logs/qmd-openrouter-embed.log

# QMD Status
/home/piet/.local/lib/node_modules/@tobilu/qmd/qmd status

# Offene Embeddings
python3 -c "
import sqlite3
conn = sqlite3.connect('/home/piet/.cache/qmd/index.sqlite')
pending = conn.execute(\"SELECT COUNT(*) FROM documents d WHERE d.hash NOT IN (SELECT hash FROM content_vectors)\").fetchone()[0]
print(f'Pending: {pending}')
"
```
