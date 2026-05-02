# Hermes Sprint H-3: Discord Live + OpenClaw Read-only

Datum: 2026-05-02

## Ziel

Hermes soll im Discord als Shadow-Debug-Assistant aktuelle OpenClaw- und Mission-Control-Lagebilder liefern koennen, ohne fuer normale Diagnosen Terminal-Kommandos zu brauchen.

## Scope

- `openclaw-readonly` MCP fuer Gateway, Discord Bot, Modelle, Sessions und begrenzte Warn-/Error-Logs.
- Skill `openclaw-operator` aktualisieren, damit Hermes MCP-first arbeitet.
- Runbook fuer OpenClaw read-only Betrieb.
- Normalmodus/Break-Glass-Abgrenzung dokumentieren.
- E2E-Testpack fuer Discord und CLI.

## Non-Scope

- Keine neuen Tasks, Crons, Agents oder Deploys.
- Keine OpenClaw-Config-Aenderung.
- Keine OpenClaw- oder Mission-Control-Restarts.
- Keine Token-Rotation.

## Live-Baseline

- OpenClaw Gateway Health: `GET http://127.0.0.1:18789/health` -> HTTP 200, `ok=true`, `status=live`.
- `openclaw-gateway.service`: active.
- `openclaw-discord-bot.service`: active, Commander Channel `1495737862522405088`, Bot logged in as Piet bot user.
- Mission Control Health: HTTP 200, `status=ok`, `severity=ok`, `attentionCount=0`, `recoveryLoad=0`.
- Mission Control board next action: `All clear`, `action=none`.

## Qualitaetsgates

1. Config-Backup vor Hermes-Konfigmutation.
2. MCP Server kompiliert mit `py_compile`.
3. `hermes mcp test openclaw-readonly` erfolgreich.
4. Hermes Gateway nach Konfigaenderung aktiv und listet `openclaw-readonly`.
5. E2E: Hermes nutzt fuer OpenClaw-Lagebild `openclaw-readonly` und empfiehlt keine Mutation ohne Gate.

## Stop Conditions

- `openclaw-readonly` liefert keine Tools.
- Hermes Gateway startet nach Konfigaenderung nicht.
- E2E empfiehlt Restart/Config-Edit ohne Live-Evidence und Piet-Freigabe.
- Unerwartete Drift bei Vault- oder Hermes-Konfigpfaden.
