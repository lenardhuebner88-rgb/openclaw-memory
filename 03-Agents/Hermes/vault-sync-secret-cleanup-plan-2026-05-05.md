# Vault Sync Secret Cleanup Plan — 2026-05-05

## Problem
`vault-sync.service` erzeugt lokale Auto-Sync-Commits, aber GitHub lehnt `master -> master` ab:

```text
push declined due to repository rule violations
```

Live-Analyse zeigt in den seit `github/master` ungepushten Dateien Secret-/API-Key-ähnliche Treffer in:

```text
08-Backups/openclaw-config-backups/2026-05-05/openclaw.json
```

Zusätzlich ist die komplette OpenClaw-Config-Backup-Kopie unter `08-Backups/openclaw-config-backups/2026-05-05/` im Push-Diff enthalten.

## Ziel
1. Keine Secrets/Config-Backups in den Remote-Push bringen.
2. Die 31 lokalen Vault-Änderungen seit `github/master` ohne Secret-Backup-Historie neu committen.
3. `vault-sync.service` so ändern, dass Push-Fehler künftig als systemd-Fehler sichtbar werden.
4. Live verifizieren: Push erfolgreich, Timer aktiv, Git sauber, KB/Receipt vorhanden.

## Freigabe
Piet erteilte im Discord-Thread Freigabe: "Ja plane das sauber auf, dokumentiere und setzte das schsritt gpt Schritt um. Anschliesend prüfe live sauber kb alles korrekt ist."

## Umsetzungsschritte

### 1. Vault-Sync kurz einfrieren
Stoppe `vault-sync.timer`, damit während des History-Rewrites kein weiterer Auto-Commit entsteht.

### 2. Backups erstellen
- Git-Sicherungsbranch auf aktuellem `master`.
- Git-Bundle des aktuellen `master`.
- Timestamped Backup von `/home/piet/.config/systemd/user/vault-sync.service`.

### 3. Lokale unveröffentlichte Historie neu aufbauen
- `git reset --soft github/master`
- `08-Backups/openclaw-config-backups/` aus dem Index entfernen, im Arbeitsbaum behalten.
- `.gitignore` um `08-Backups/openclaw-config-backups/` ergänzen.
- Neuen bereinigten Commit erstellen.

### 4. Service-Observability fixen
`vault-sync.service` ersetzen durch robuste Shell-Form:

```bash
set -euo pipefail
cd /home/piet/vault
git add -A
git diff --cached --quiet || git commit -m "auto-sync: $(date +%Y-%m-%d\ %H:%M)"
git push github master
```

Damit schlägt die Unit fehl, wenn GitHub einen Push ablehnt.

### 5. Verifikation
- Kein Secret-like Treffer in `git diff --name-only github/master..master` / zu pushenden Dateien.
- `git push github master` erfolgreich.
- `systemctl --user daemon-reload` und Unit-Syntax verifizieren.
- `vault-sync.timer` wieder starten.
- Direkter `systemctl --user start vault-sync.service` muss mit `Result=success` enden und keinen neuen Commit erzeugen, falls sauber.
- `git status --short --branch` prüfen.
- Receipt in `/home/piet/vault/03-Agents/Hermes/receipts/` schreiben und erneut synchronisieren.

## Rollback
- Lokalen Zustand aus Backup-Branch wiederherstellen:
  `git reset --hard backup/vault-sync-pre-secret-cleanup-<timestamp>`
- Oder aus Bundle importieren.
- Service-Datei aus `.bak-<timestamp>` zurückkopieren und `systemctl --user daemon-reload`.
