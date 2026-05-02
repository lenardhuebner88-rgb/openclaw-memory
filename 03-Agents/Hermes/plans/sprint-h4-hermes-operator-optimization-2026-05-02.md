# Hermes Sprint H-4: Operator Optimization

Datum: 2026-05-02

## Ziel

Hermes soll im Discord ruhiger, schneller und eindeutiger als Shadow-Debug-Assistant arbeiten:

- keine neue Discord-429-Schleife;
- weniger Channel-Prompt-Ballast;
- MCP-first statt Shell-first;
- Normalmodus und Break-Glass klar trennen;
- nach jeder Aenderung ein kleines E2E-Testset.

## Scope

1. Discord 429 Zustand nach `DISCORD_COMMAND_SYNC_POLICY=off` verifizieren.
2. Discord Channel Prompt in `/home/piet/.hermes/config.yaml` kuerzen.
3. Tool-/MCP-Nutzung im Normalmodus dokumentieren und per Prompt/Skill klarer machen.
4. E2E-Checks: Modell/Fallback, OpenClaw, Mission Control, Vault/QMD, Break-Glass-Simulation.
5. Receipt mit Befund, geaenderten Dateien und offenen Risiken.

## Non-Scope

- Kein `ProtectSystem=strict` / `ProtectHome=read-only`.
- Keine OpenClaw- oder Mission-Control-Restarts.
- Keine Tasks, Crons, Agents oder Deploys.
- Keine Token-Rotation.
- Keine weitere Discord-Command-Sync-Aktivierung.

## Baseline 2026-05-02 23:25

- `privacy.redact_pii=true`.
- `DISCORD_COMMAND_SYNC_POLICY=off` aktiv.
- `NoNewPrivileges=yes`, `PrivateTmp=yes`, `MemoryHigh=1536M`, `MemoryMax=2G` aktiv.
- `ProtectSystem=no`, `ProtectHome=no` bewusst offen.
- Hermes Gateway active/running.
- In den letzten 10 Minuten keine neuen Discord 429 Journalzeilen nach dem letzten Restart sichtbar.
- MCP Server konfiguriert: `qmd-vault`, `mc-readonly`, `openclaw-readonly`.

## Qualitaetsgates

Gate 1 - Backup:

- Backup von `/home/piet/.hermes/config.yaml` vor Prompt-Aenderung.

Gate 2 - Config Validate:

- YAML parsebar.
- `privacy.redact_pii=true` bleibt erhalten.
- `DISCORD_COMMAND_SYNC_POLICY=off` bleibt aktiv.

Gate 3 - Restart + Post-check:

- `systemctl --user restart hermes-gateway.service`.
- Hermes active/running.
- Keine neuen Discord 429 im Post-check-Fenster.
- `hermes mcp test openclaw-readonly`, `mc-readonly`, `qmd-vault` PASS.

Gate 4 - E2E Behavior:

- OpenClaw Lagebild nutzt `openclaw-readonly`.
- Mission Control Lagebild nutzt `mc-readonly`.
- Vault/Token-Rotation nennt bekannten Runbook-Pfad zuerst, QMD nur fokussiert.
- Break-Glass Simulation fuehrt nichts aus und nennt Approval-Gate.

## Stop Conditions

- Hermes Gateway startet nicht.
- MCP-Tests failen nach Restart.
- Discord 429 kommt trotz Sync-Policy sofort wieder.
- Prompt-Aenderung entfernt zentrale Safety-Gates.
- Neue Mutationsvorschlaege ohne Live-Evidence/Approval tauchen im E2E auf.
