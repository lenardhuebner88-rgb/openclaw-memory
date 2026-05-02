# Playbook: OpenClaw Read-only MCP

## Zweck

Hermes nutzt dieses Playbook fuer aktuelle OpenClaw-Lagebilder im Discord, ohne normale Diagnosen ueber Shell-Break-Glass abzuwickeln.

## Primaere Tools

MCP Server: `openclaw-readonly`

Tools:

- `openclaw_gateway_health`
- `openclaw_services_status`
- `openclaw_recent_logs`
- `openclaw_model_status`
- `openclaw_recent_sessions`
- `openclaw_status_summary`

## Standardablauf

1. `openclaw_status_summary` abrufen.
2. Bei Gateway-Problem: `openclaw_gateway_health` separat pruefen.
3. Bei Discord-Problem: `openclaw_services_status` und begrenzte `openclaw_recent_logs`.
4. Bei Modell-/Fallback-Fragen: `openclaw_model_status`.
5. Bei Laufzeit-/Session-Fragen: `openclaw_recent_sessions` mit begrenztem Zeitraum.

## Reportformat

```text
Problem:
Runbook:
Evidence:
Risk:
Next Action:
```

## Grenzen

Dieses Playbook erlaubt keine Mutationen:

- kein `systemctl restart`
- keine Config-Edits
- keine Tasks, Crons, Agents oder Deploys
- keine Token-Ausgabe
- keine breiten Dateisystem-Scans

## Eskalation

Wenn ein Restart oder Config-Edit sinnvoll erscheint, wechselt Hermes nicht automatisch in Aktion. Hermes nennt:

1. Live-Evidence
2. exakten Service oder Config-Pfad
3. erwarteten Post-Check
4. erforderliche Piet-Freigabe im aktuellen Discord-Thread

Danach gilt das passende Break-Glass-Runbook, z.B. `openclaw-gateway-down.md` oder `openclaw-discord-commands-broken.md`.
