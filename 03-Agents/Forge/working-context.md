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
- task: e80e7cd2-7cb7-4a8b-b295-e1675fda260e [NOW] [AUDIT] Forge: Data Stability + Backend Hardening
- stage: BLOCKED
- next: resolve blocker, then continue
- checkpoint: Security check failed (critical)
- blocker: Security check failed (critical)
- updated: 2026-04-12T07:53:27.856Z
<!-- mc:auto-working-context:end -->
