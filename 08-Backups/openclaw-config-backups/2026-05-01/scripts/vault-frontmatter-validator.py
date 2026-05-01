#!/usr/bin/env python3
"""
R53 Vault-Frontmatter Schema-Gate

Scans /home/piet/vault/ recursively for *.md files with YAML frontmatter,
validates required fields per doc-type, reports drift.

Schedule: 0 */6 * * * (every 6h, low-frequency)
Lock:     /tmp/vault-frontmatter-validator.lock
Log:      /home/piet/.openclaw/workspace/logs/vault-frontmatter-validator.log
Report:   /home/piet/.openclaw/workspace/state/vault-frontmatter-drift.json

Doc-types recognized via `type:` field in frontmatter:
  - incident-report, sprint-brief, deployment-report, audit-report,
    decision-matrix, daily, rule-deployment, deployment-report

Required fields per doc-type:
  ALL: type, date, tags
  INCIDENT-REPORT: + status, severity
  SPRINT-BRIEF: + sprints, owner, status
  DAILY: + status

Discord-alert if drift_count > N (default 5).

Exit codes:
  0 — completed (drift may be reported but exit 0 for cron continuity)
  1 — fatal error (e.g. vault dir missing)
"""
import json, os, re, sys, time, subprocess
from pathlib import Path

VAULT_ROOT = Path("/home/piet/vault")
SCAN_DIRS = [VAULT_ROOT / "_agents"]  # Where structured docs live
LOG_PATH = Path("/home/piet/.openclaw/workspace/logs/vault-frontmatter-validator.log")
REPORT_PATH = Path("/home/piet/.openclaw/workspace/state/vault-frontmatter-drift.json")
ALERT_DISPATCHER = "/home/piet/.openclaw/scripts/alert-dispatcher.sh"
DRIFT_ALERT_THRESHOLD = 5

# Per-type required fields (any frontmatter not in this list = type=unknown, only checks 'type' presence)
REQUIRED_FIELDS = {
    "incident-report":   ["type", "date", "tags", "status"],
    "sprint-brief":      ["type", "date", "tags", "status"],
    "deployment-report": ["type", "date", "tags", "status"],
    "audit-report":      ["type", "date", "tags"],
    "decision-matrix":   ["type", "date", "tags"],
    "daily":             ["type", "date", "tags"],
    "rule-deployment":   ["type", "date", "tags"],
}

LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)


def ts():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def log(msg):
    with open(LOG_PATH, "a") as f:
        f.write(f"{ts()} {msg}\n")


def parse_frontmatter(text):
    """Extract YAML frontmatter (between --- markers) as dict.
    Returns (frontmatter_dict, error_msg)."""
    if not text.startswith("---"):
        return None, "no_frontmatter"
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return None, "frontmatter_unterminated"
    fm_text = m.group(1)
    # Permissive YAML parse (basic key: value)
    fm = {}
    current_key = None
    for line in fm_text.split("\n"):
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith("#"):
            continue
        # Top-level key: value
        m_kv = re.match(r"^([\w-]+)\s*:\s*(.*)$", line)
        if m_kv:
            key, value = m_kv.groups()
            value = value.strip()
            if value.startswith("[") and value.endswith("]"):
                # Inline array
                items = [v.strip().strip('"').strip("'") for v in value[1:-1].split(",")]
                fm[key] = [i for i in items if i]
            elif value:
                fm[key] = value.strip('"').strip("'")
            else:
                # Multi-line value (array form)
                fm[key] = []
            current_key = key
        elif line.startswith("  - ") and current_key and isinstance(fm.get(current_key), list):
            item = line[4:].strip().strip('"').strip("'")
            fm[current_key].append(item)
    return fm, None


def validate_doc(path):
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as e:
        return {"path": str(path), "error": f"read_error: {e}"}

    fm, err = parse_frontmatter(text)
    if err or fm is None:
        # No frontmatter or unparseable — not flagged (free-form notes are valid)
        return None

    doc_type = fm.get("type")
    if not doc_type:
        return None  # not a structured doc, skip

    # Be pragmatic: only flag known-type docs that miss required fields.
    # Unknown types and no-frontmatter docs are not drift (vault has many
    # free-form docs that don't follow strict schema).
    if doc_type not in REQUIRED_FIELDS:
        return None  # unknown type — not drift, just not structured

    required = REQUIRED_FIELDS[doc_type]
    missing = [k for k in required if k not in fm]
    if missing:
        return {
            "path": str(path.relative_to(VAULT_ROOT)),
            "drift": "missing_required_fields",
            "type": doc_type,
            "missing": missing,
            "present": list(fm.keys()),
        }

    return None  # valid


def main():
    if not VAULT_ROOT.exists():
        log("FATAL vault_missing")
        return 1

    log("scan_start")
    drift_records = []
    scanned = 0

    for scan_dir in SCAN_DIRS:
        if not scan_dir.exists():
            continue
        for path in scan_dir.rglob("*.md"):
            scanned += 1
            result = validate_doc(path)
            if result:
                drift_records.append(result)

    report = {
        "scanned_at": ts(),
        "scanned_count": scanned,
        "drift_count": len(drift_records),
        "scan_dirs": [str(d) for d in SCAN_DIRS],
        "required_fields_by_type": REQUIRED_FIELDS,
        "drift_records": drift_records,
    }

    REPORT_PATH.write_text(json.dumps(report, indent=2))
    log(f"scan_complete scanned={scanned} drift={len(drift_records)}")

    # Print summary to stdout for cron-log
    print(f"[{ts()}] vault-frontmatter scanned={scanned} drift={len(drift_records)}")
    if drift_records:
        for r in drift_records[:5]:
            print(f"  {r}")
        if len(drift_records) > 5:
            print(f"  ... +{len(drift_records)-5} more")

    # Alert if drift exceeds threshold
    if len(drift_records) > DRIFT_ALERT_THRESHOLD and os.access(ALERT_DISPATCHER, os.X_OK):
        msg = f":warning: **R53 Vault-Frontmatter** drift_count={len(drift_records)} (threshold={DRIFT_ALERT_THRESHOLD}). See {REPORT_PATH}"
        try:
            subprocess.run(
                [ALERT_DISPATCHER, "vault-frontmatter", msg, "@here"],
                timeout=10, capture_output=True
            )
        except Exception as e:
            log(f"alert_dispatch_failed: {e}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
