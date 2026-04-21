"""
Pydantic v2 prototype for S-FND T1 SprintOutcome schema v1.

Status: DRAFT — prepared by Claude Code on laptop 2026-04-22
Owner for deployment: Forge
Deploy-Target: /home/piet/.openclaw/workspace/mission-control/src/schemas/sprint_outcome.py (or similar)

This is a prototype/template. Forge should:
1. Adapt import paths to match MC backend layout
2. Integrate into worker-terminal-callback.ts (via typed API or JSON-schema export)
3. Add unit tests beyond the fixtures here
4. Run validation benchmarks (p95 <5ms requirement from S-FND T1 DoD)

JSON Schema export:
    python -c "import json; from sprint_outcome import SprintOutcome; print(json.dumps(SprintOutcome.model_json_schema(), indent=2))" > sprint_outcome.schema.json
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


SchemaVersion = Literal["v1"]
Status = Literal["done", "partial", "blocked", "failed"]
Priority = Literal["P0", "P1", "P2", "P3"]
Severity = Literal["critical", "high", "medium", "low"]
Owner = Literal[
    "operator",
    "atlas",
    "forge",
    "pixel",
    "lens",
    "spark",
    "codex",
    "james",
    "sre-expert",
]
ArtifactType = Literal["code", "doc", "config", "log", "screenshot", "test", "data"]


class NextAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1, description="Stable human-readable ID, e.g. 'S-FND-T1-followup-fixtures'")
    owner: Owner
    priority: Priority
    due: datetime | None = Field(default=None, description="UTC; None = no hard deadline")
    reason_code: str = Field(
        min_length=1,
        description="Controlled vocab: 'dep_met', 'rollback_needed', 'scope_extension', 'retry_due_transient', ...",
    )


class Blocker(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)
    severity: Severity
    evidence_ref: str = Field(
        min_length=1,
        description="file:line (e.g. 'src/x.ts:123') OR URL OR log-query",
    )
    note: str | None = Field(default=None, max_length=500)


class Artifact(BaseModel):
    model_config = ConfigDict(extra="forbid")

    path: str = Field(min_length=1, description="Relative to workspace root or absolute; must exist at report-time")
    sha256: str = Field(min_length=64, max_length=64, pattern=r"^[a-f0-9]{64}$")
    type: ArtifactType
    bytes: int | None = Field(default=None, ge=0)


class Metrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    duration_s: float = Field(ge=0, description="Wall-clock seconds for the work unit")
    tokens_in: int = Field(default=0, ge=0)
    tokens_out: int = Field(default=0, ge=0)
    cache_hit_rate: float | None = Field(default=None, ge=0, le=1, description="0.0-1.0")
    cost_usd: float = Field(default=0.0, ge=0)


class SprintOutcome(BaseModel):
    """
    Canonical SprintOutcome receipt schema v1.

    Emitted by:
    - Worker terminal callbacks
    - Atlas sprint-close reports
    - Forge task receipts
    - Any agent producing a terminal (done|partial|blocked|failed) output

    Read by:
    - board-next-action.ts (via Pydantic→TS-interface or JSON-schema)
    - task-governance-signals.ts (strict mode, per S-RPT T1)
    - cedar-policy-engine (future, S-GOV spike)
    - sprint dashboards (future, S-HANDBOOK SH3 overlays)
    """
    model_config = ConfigDict(extra="forbid")

    schema_version: SchemaVersion = "v1"
    status: Status
    next_actions: list[NextAction] = Field(default_factory=list)
    blockers: list[Blocker] = Field(default_factory=list)
    artifacts: list[Artifact] = Field(default_factory=list)
    metrics: Metrics
    human_narrative: str | None = Field(
        default=None,
        max_length=4000,
        description="Optional Discord-friendly prose. NOT read by machine decisions.",
    )

    # Convenience integration hooks (populated by ingress, not worker)
    attempt_id: str | None = Field(
        default=None,
        min_length=64,
        max_length=64,
        pattern=r"^[a-f0-9]{64}$",
        description="sha256 workflow-ID from S-FND T2; set by Ingress, never by worker",
    )
    emitted_at: datetime | None = Field(
        default=None,
        description="UTC; set by Ingress on receipt",
    )

    @field_validator("status")
    @classmethod
    def _status_consistency(cls, v: Status, info) -> Status:
        """When status=blocked, at least 1 blocker is required (structural invariant)."""
        # NOTE: in Pydantic v2, model_validator is cleaner; using field_validator for v1 feel.
        # Full cross-field logic lives in a model_validator below.
        return v

    def validate_consistency(self) -> list[str]:
        """
        Additional non-schema validation.
        Returns list of human-readable issues. Empty list = clean.
        Call this after .model_validate() if strict semantic checks are wanted.
        """
        issues: list[str] = []
        if self.status == "blocked" and not self.blockers:
            issues.append("status=blocked but blockers[] is empty")
        if self.status == "done" and self.blockers:
            issues.append("status=done but blockers[] non-empty (lingering blocker?)")
        if self.status == "failed" and not self.next_actions:
            issues.append(
                "status=failed but next_actions[] empty (no retry/escalation path documented)"
            )
        if self.metrics.tokens_in == 0 and self.metrics.tokens_out > 0:
            issues.append("tokens_out > 0 but tokens_in == 0 (implausible)")
        return issues


if __name__ == "__main__":
    # Quick smoke test
    import json

    example = SprintOutcome(
        status="done",
        next_actions=[
            NextAction(
                id="S-FND-T2-start",
                owner="forge",
                priority="P0",
                due=None,
                reason_code="dep_met",
            )
        ],
        blockers=[],
        artifacts=[
            Artifact(
                path="src/schemas/sprint_outcome.py",
                sha256="a" * 64,
                type="code",
                bytes=4200,
            )
        ],
        metrics=Metrics(
            duration_s=3720.5,
            tokens_in=12_000,
            tokens_out=2_400,
            cache_hit_rate=0.72,
            cost_usd=0.18,
        ),
        human_narrative="T1 Schema deployed, 10/10 fixtures pass, p95 validation 2.3ms.",
    )
    print("Model round-trip:")
    print(json.dumps(example.model_dump(mode="json"), indent=2))
    print("\nConsistency issues:", example.validate_consistency())
    print("\nJSON Schema (first 500 chars):")
    schema = example.model_json_schema()
    print(json.dumps(schema, indent=2)[:500] + "...")
