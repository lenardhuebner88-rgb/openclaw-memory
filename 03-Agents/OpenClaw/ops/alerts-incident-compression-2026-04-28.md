# Alerts Incident Compression – 2026-04-28

## Scope
Backend-only redesign of `/api/alerts` counting semantics to separate raw historical log volume from deduped operational incident signals.

## Implemented Contract Changes
Added fields on `GET /api/alerts` response:
- `rawLogAlertCount`
- `returnedAlertCount`
- `activeIncidentCount`
- `historicalNoiseCount`
- `groupedIncidentCounts`
- `topSources`
- `latestPerType`

Existing fields and behavior kept API-compatible (`counts`, `alerts`, `includeSuppressed`, `totalAlerts`, `alertLimit`, ack/mute POST behavior).

## Grouping/Dedupe Logic
Incident grouping key:
- `type + source + kind + normalized(detail) + hour-bucket(ts)`

Normalization:
- lower-case detail
- timestamp tokens collapsed to `<ts>`
- numeric tokens collapsed to `<num>`
- whitespace normalized
- truncated to 180 chars

Incident candidate filter:
- excludes `delivery === "recovered"`
- excludes `severity === "info"`

## Validation
### Build / Runtime
- `ALLOW_BUILD_WHILE_RUNNING=1 npm run build` completed successfully.
- Safe restart executed via `mc-restart-safe`.

### Smoke checks
- `GET /api/alerts?limit=5`: new fields present.
  - sample: `rawLogAlertCount=10945`, `returnedAlertCount=5`, `activeIncidentCount=1657`, `historicalNoiseCount=9288`
- `GET /alerts`: page served (HTML bytes > 0)
- `GET /api/health`: `status=ok`
- `GET /api/board-consistency`: `status=ok`

### Note
`npm run typecheck` currently fails for pre-existing unrelated issue:
- `src/components/ops/dependency-graph.tsx`: missing `mermaid` module/type declarations.

## Changed File
- `mission-control/src/app/api/alerts/route.ts`

## UI impact
No frontend changes required for this backend contract extension.