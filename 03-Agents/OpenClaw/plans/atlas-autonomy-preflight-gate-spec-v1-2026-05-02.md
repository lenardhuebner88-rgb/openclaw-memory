# Atlas Autonomy Preflight Gate Spec v1

Stand: 2026-05-02  
Owner: Forge (Draft)

## Goal
Provide a minimal machine-checkable gate before autonomous action execution.

## Decision Output
`decision = allow | require-approval | deny`

## Input Contract (v1)
```json
{
  "taskId": "string|null",
  "actionType": "read|write|dispatch|cron-mutation|gateway-restart|model-change|cleanup|other",
  "riskLevel": "low|medium|high",
  "targetScope": ["files|service|task|cron|model|secrets|external"],
  "hasApprovedTask": true,
  "isTerminalTaskTarget": false,
  "hasSessionLockConflict": false,
  "requiresSudo": false,
  "touchesSecretsAuth": false,
  "proofPlan": {
    "preChecks": ["..."],
    "postChecks": ["..."],
    "evidencePaths": ["..."]
  },
  "dod": "string",
  "antiScope": "string",
  "owner": "agent-id"
}
```

## Output Contract (v1)
```json
{
  "decision": "allow|require-approval|deny",
  "reasonCode": "string",
  "summary": "string",
  "requiredApprovals": ["operator"],
  "requiredProof": ["..."],
  "audit": {
    "policyVersion": "autonomy-policy-matrix-v1-2026-05-02",
    "evaluatedAt": "ISO-8601",
    "inputsHash": "sha256",
    "evaluator": "atlas-preflight-v1"
  }
}
```

## Evaluation Rules (ordered)
1. If `requiresSudo=true` -> `deny` (`DENY_SUDO`).
2. If `isTerminalTaskTarget=true` -> `deny` (`DENY_TERMINAL_RERUN`).
3. If `hasSessionLockConflict=true` -> `deny` (`DENY_LOCK_CONFLICT_R50`).
4. If `touchesSecretsAuth=true` and not read-only approved path -> `deny` (`DENY_SECRET_AUTH_MUTATION`).
5. If `proofPlan.evidencePaths` empty for write/dispatch -> `deny` (`DENY_MISSING_EVIDENCE`).
6. If `actionType` in `{cron-mutation,gateway-restart,model-change}` and `hasApprovedTask=false` -> `deny` (`DENY_UNAUTHORIZED_FANOUT`/scope-specific).
7. If `actionType` in `{cron-mutation,gateway-restart,model-change}` with approved task -> `require-approval` (scope-specific reason).
8. If low-risk bounded DoD+Anti-Scope+proofPlan present -> `allow` (`OK_LOW_RISK_BOUNDED`).
9. If read-only with proof plan -> `allow` (`OK_READONLY_PROOFED`).
10. Else -> `require-approval` (`NEEDS_APPROVAL_UNCLASSIFIED`).

## Failure Modes
- Missing required input keys -> `deny` (`DENY_INVALID_INPUT`).
- Evidence path inaccessible -> `deny` (`DENY_MISSING_EVIDENCE`).
- Policy version mismatch -> `require-approval` (`NEEDS_APPROVAL_POLICY_MISMATCH`).

## Audit Event Schema
```json
{
  "event": "autonomy_preflight_decision",
  "taskId": "string|null",
  "decision": "allow|require-approval|deny",
  "reasonCode": "string",
  "actionType": "string",
  "riskLevel": "string",
  "owner": "agent-id",
  "proofPaths": ["..."],
  "timestamp": "ISO-8601"
}
```

## E2E Acceptance Tests (must-pass)
1. Safe read-only analysis -> `allow` + `OK_READONLY_PROOFED`.
2. P2 bounded cleanup with DoD/Anti-Scope/proof -> `allow` + `OK_LOW_RISK_BOUNDED`.
3. Cron mutation without approved task -> `deny` (`DENY_UNAUTHORIZED_FANOUT`).
4. Sudo command -> `deny` (`DENY_SUDO`).
5. Default model/provider change with approved task -> `require-approval` (`NEEDS_APPROVAL_MODEL_MAJOR`).
6. Terminal task redispatch -> `deny` (`DENY_TERMINAL_RERUN`).
7. Live lock conflict -> `deny` (`DENY_LOCK_CONFLICT_R50`).
8. Missing receipt/proof path for mutation -> `deny` (`DENY_MISSING_EVIDENCE`).

## Phase-1 Task Split
- P1.1: Implement pure evaluator module (no side effects).
- P1.2: Add JSON schema validation for input/output.
- P1.3: Integrate evaluator before autonomous dispatch/mutation paths.
- P1.4: Emit audit events to board-events stream.
- P1.5: Add E2E fixture suite for the 8 acceptance tests.

## Can implementation safely start next?
Yes, for evaluator-only phase (read-only + decision logging) with zero mutation rights. Mutation enforcement should follow after fixture pass.
