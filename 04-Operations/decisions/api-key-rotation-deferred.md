# Entscheidung: API-Key-Rotation vorerst nicht angehen

> Datum: 2026-04-13 | Entscheider: Lenard

## Betroffene Tasks (canceled)

- `90fa4b17` — [P0][Security] Betroffenen produktiven API-Key rotieren + Log-Audit
- `a08758e4` — [P0][Security] Leaked BRAVE_API_KEY rotieren + Log-Redaction härten

## Entscheidung

Beide Tasks wurden bewusst vom Board entfernt. Die API-Keys werden **vorerst nicht rotiert**.

## Begründung

Bewusste Priorisierungsentscheidung — die Keys werden zu einem späteren Zeitpunkt angegangen wenn der richtige Rahmen dafür besteht.

## Was das bedeutet

- Kein Agent soll eigenständig Key-Rotation-Tasks erstellen oder angehen
- Atlas soll diese Findings **nicht** als Follow-up-Tasks neu aufnehmen
- Log-Redaction-Verbesserungen dürfen als separate technische Tasks ohne Key-Rotation angegangen werden

## Wiedervorlage

Explizit von Lenard zu triggern — kein automatischer Retry.
