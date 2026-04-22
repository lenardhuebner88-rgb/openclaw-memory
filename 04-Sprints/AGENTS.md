# 04-Sprints — Sprint Plans & Results

**Purpose:** Canonical home for sprint-related docs (plans, reports, audits, postmortems).
**Writers:** Atlas (planning) + Forge/SRE (execution reports) + human.
**Readers:** Anyone.

## Rules
- Naming: `sprint-<letter-or-name>-<slug>-YYYY-MM-DD.md` (e.g., `sprint-k-infra-hardening-plan-2026-04-19.md`).
- Every sprint plan MUST have PlanSpec frontmatter (`title`, `created`, `priority`, `owner`, `depends-on`, `anti-goals`, `pre-flight-gates`). Pre-commit hook validates this.
- Sprint reports reference their plan via wikilink in body.

## Never touch
- Legacy pre-PlanSpec sprints (2026-04-19 and earlier) — pre-commit hook flags them; they stay as historical record.
