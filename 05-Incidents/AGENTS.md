# 05-Incidents — Incident Reports, RCAs, Outages

**Purpose:** Postmortem ground-truth for production incidents.
**Writers:** SRE-Expert + human (primary) + Atlas (coordination).
**Readers:** Everyone (lessons compound into `10-KB/incident-response.md`).

## Rules
- Naming: `<type>-<slug>-YYYY-MM-DD.md` (types: `rca-`, `outage-`, `incident-`).
- Every file MUST link forward to the fix sprint in `04-Sprints/` and to the R-rule in `feedback_system_rules.md` that was born/validated.
- Once a fact is stable, tag it `status: compiled-to-kb` so the KB-compiler can consume.

## Never touch
- Historical incidents — they are append-only.
