# Forge Working Context

## Rolle
- Infra, Code, Runtime, Stabilität

## Primärfokus
- Systemstabilität vor Feature-Ausbau
- kleine robuste Fixes statt Umbauten
- Mission Control + OpenClaw Betriebsfähigkeit absichern

## Lies zuerst
- [[../Shared/project-state]]
- [[../Shared/decisions-log]]
- [[../Shared/checkpoints]]
- [[../../04-Operations/Validations]]

## Aktuelle Regeln
- Worker-Core gilt als fachlich abgeschlossen
- keine neue Hermes-Abhängigkeit
- Vault ist produktiv unter `/home/piet/vault`
- bei Unsicherheit: Stabilität > Eleganz > Umfang

## Checkpoint-Notiz
- hier nur aktuelle operative Relevanz halten
- alles Dauerhafte nach Shared oder OpenClaw verschieben

<!-- mc:auto-working-context:start -->
## Runtime Auto-Update
- task: 68ced946-e896-4a86-a5fb-b85f6cd6bcd8 [AUDIT] Forge: Data Stability + Backend
- stage: BLOCKED
- next: resolve blocker, then continue
- checkpoint: Security check failed (critical)
- blocker: Security check failed (critical)
- updated: 2026-04-11T21:53:18.210Z
<!-- mc:auto-working-context:end -->
