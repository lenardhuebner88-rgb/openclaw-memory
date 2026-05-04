#!/usr/bin/env python3
"""
openclaw-config-validator.py — R51-Schema-Gate validator for openclaw.json

Runs structural + invariant checks beyond what `openclaw doctor` catches.
Called by openclaw-config-guard.sh when CHANGE_DETECTED fires.

Exit codes:
  0 — all checks pass
  1 — JSON parse failure
  2 — schema violation
  3 — invariant violation (agents.list empty, bad slug, size-shrink)
  4 — unexpected error

Each non-zero exit logs a reason to stdout (captured by config-guard).

Source-of-truth: /home/piet/.openclaw/openclaw.json
Schema: /home/piet/.openclaw/schemas/openclaw.json.schema.json
Last-good: /home/piet/.openclaw/backups/openclaw-config-guard/openclaw.json.last-good
"""
import json
import os
import re
import sys
import time

CONFIG_PATH = "/home/piet/.openclaw/openclaw.json"
SCHEMA_PATH = "/home/piet/.openclaw/schemas/openclaw.json.schema.json"
LAST_GOOD = "/home/piet/.openclaw/backups/openclaw-config-guard/openclaw.json.last-good"

# Invariant thresholds
MIN_FILE_BYTES = 5_000          # below this = likely truncated/wiped
MIN_AGENTS_LIST_LEN = 3         # we have 6 agents — anything < 3 is suspicious
MAX_SIZE_SHRINK_PCT = 50        # reject if file shrunk >50% vs last-good
SLUG_PATTERN = re.compile(r"^[a-z][a-z0-9-]*\/[A-Za-z0-9._\/-]+$")


def fail(code: int, reason: str) -> None:
    print(f"VALIDATION_FAIL code={code} reason={reason}")
    sys.exit(code)


def load_json(path: str) -> dict:
    with open(path) as f:
        return json.load(f)


def main() -> int:
    # 1. Existence + size
    if not os.path.exists(CONFIG_PATH):
        fail(1, "config_missing")
    size = os.path.getsize(CONFIG_PATH)
    if size < MIN_FILE_BYTES:
        fail(3, f"file_too_small bytes={size} min={MIN_FILE_BYTES}")

    # 2. Size-shrink check vs last-good
    if os.path.exists(LAST_GOOD):
        last_size = os.path.getsize(LAST_GOOD)
        if last_size > 0:
            shrink_pct = ((last_size - size) / last_size) * 100
            if shrink_pct > MAX_SIZE_SHRINK_PCT:
                fail(3, f"file_shrunk_too_much old={last_size} new={size} pct={shrink_pct:.1f}")

    # 3. JSON parse
    try:
        cfg = load_json(CONFIG_PATH)
    except Exception as e:
        fail(1, f"json_parse_error {e}")

    # 4. Schema validation — RE-ENABLED 2026-04-29 with v2 schema (model:object)
    #    Schema-File at /home/piet/.openclaw/schemas/openclaw.json.schema.json
    #    was updated 2026-04-29 to match runtime shape.
    try:
        import jsonschema
        if os.path.exists(SCHEMA_PATH):
            schema = load_json(SCHEMA_PATH)
            try:
                jsonschema.validate(instance=cfg, schema=schema)
                print("INFO schema_check_passed")
            except jsonschema.ValidationError as e:
                fail(2, f"schema_violation path={list(e.path)[:5]} msg={str(e.message)[:120]}")
        else:
            print("WARN schema_file_missing — invariants only")
    except ImportError:
        print("WARN jsonschema_not_installed — invariants only")

    # 5. Invariants
    agents = cfg.get("agents", {})
    agent_list = agents.get("list", [])
    if not isinstance(agent_list, list):
        fail(3, "agents.list_not_array")
    if len(agent_list) < MIN_AGENTS_LIST_LEN:
        fail(3, f"agents.list_too_short len={len(agent_list)} min={MIN_AGENTS_LIST_LEN}")

    # Each agent must have id + model.primary
    for i, a in enumerate(agent_list):
        if not isinstance(a, dict):
            fail(3, f"agent[{i}]_not_object")
        aid = a.get("id")
        if not aid or not isinstance(aid, str):
            fail(3, f"agent[{i}]_missing_id")
        model = a.get("model", {})
        primary = model.get("primary")
        if not primary or not isinstance(primary, str):
            fail(3, f"agent[{aid}]_missing_primary")
        # Slug format check (e.g. minimax/MiniMax-M2.7, openai-codex/gpt-5.5)
        if not SLUG_PATTERN.match(primary):
            fail(3, f"agent[{aid}]_invalid_primary_slug primary={primary[:50]}")
        fbs = model.get("fallbacks", [])
        if not isinstance(fbs, list):
            fail(3, f"agent[{aid}]_fallbacks_not_array")
        for j, fb in enumerate(fbs):
            if not isinstance(fb, str) or not SLUG_PATTERN.match(fb):
                fail(3, f"agent[{aid}].fallbacks[{j}]_invalid_slug fb={str(fb)[:50]}")

    # 6. Spark special-case (operator-required per Atlas patch; updated 2026-05-03)
    # ChatGPT Pro/Codex setups can use either legacy openai-codex/* or
    # openai/gpt-* when the agent runtime is explicitly Codex. The older
    # invariant rejected the recommended openai/gpt-* + agentRuntime.id=codex
    # route and caused config-guard rollbacks of valid model migrations.
    spark = next((a for a in agent_list if a.get("id","").lower() == "spark"), None)
    if spark:
        sp = spark.get("model",{}).get("primary","")
        runtime = spark.get("agentRuntime") or agents.get("defaults", {}).get("agentRuntime", {})
        runtime_id = runtime.get("id") if isinstance(runtime, dict) else ""
        spark_ok = sp.startswith("openai-codex/") or (sp.startswith("openai/gpt-") and runtime_id == "codex")
        if not spark_ok:
            fail(3, f"spark_primary_must_be_codex_route got={sp} runtime={runtime_id}")

    # 7. Defaults sanity
    defaults_model = agents.get("defaults", {}).get("model", {})
    dp = defaults_model.get("primary")
    if not dp or not SLUG_PATTERN.match(dp):
        fail(3, f"defaults.primary_invalid {dp}")

    # 8. openrouter/auto must be LAST in any chain that contains it
    for a in agent_list:
        fbs = a.get("model", {}).get("fallbacks", [])
        if "openrouter/auto" in fbs and fbs[-1] != "openrouter/auto":
            fail(3, f"agent[{a.get('id')}].fallbacks_openrouter_auto_not_last")

    # All good
    print(f"VALIDATION_OK size={size} agents={len(agent_list)} ts={time.strftime('%FT%TZ', time.gmtime())}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as e:
        fail(4, f"unexpected_error {type(e).__name__}: {e}")
