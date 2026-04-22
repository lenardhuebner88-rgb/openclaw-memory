#!/usr/bin/env python3
"""
Parse feedback_system_rules.md into rules.jsonl (one rule per line).
Each rule extracts: id, title, category, since, status, severity, body, markers.
"""
import json
import re
import sys
from pathlib import Path

SRC = Path('/home/piet/.openclaw/workspace/feedback_system_rules.md') if len(sys.argv) < 2 else Path(sys.argv[1])
DST = Path('/home/piet/.openclaw/workspace/memory/rules.jsonl') if len(sys.argv) < 3 else Path(sys.argv[2])

# Also parse from local detailed file if given
if not SRC.exists():
    print(f'Source not found: {SRC}', file=sys.stderr)
    sys.exit(1)

content = SRC.read_text(encoding='utf-8')

# Strip frontmatter if present
if content.startswith('---\n'):
    parts = content.split('---\n', 2)
    if len(parts) >= 3:
        content = parts[2]

# Find all rule sections. Header patterns: "### R<N> — <title>" or "## R<N> — <title>"
# Category: "## <category name>" (without R<N>)
lines = content.split('\n')
current_category = 'uncategorized'
rules = []
current_rule = None

for line in lines:
    # Category header (## XXX where XXX doesn't start with R<number>)
    m_cat = re.match(r'^##\s+(?!R\d+)(.+?)(\s*\(.*\))?$', line)
    if m_cat and not re.match(r'^##\s+R\d+', line):
        current_category = m_cat.group(1).strip()
        continue

    # Rule header: "### R<N> — <title>" or "## R<N> — <title>"
    m_rule = re.match(r'^##+\s+(R\d+)\s+[—\-]+\s+(.+)$', line)
    if m_rule:
        if current_rule:
            rules.append(current_rule)
        current_rule = {
            'id': m_rule.group(1),
            'title': m_rule.group(2).strip(),
            'category': current_category,
            'body_lines': []
        }
        continue

    # Collect body lines
    if current_rule is not None:
        current_rule['body_lines'].append(line)

if current_rule:
    rules.append(current_rule)

# Enrich each rule: extract structured fields from body
def extract_fields(body):
    fields = {}
    # Pattern: **Label:** content
    for match in re.finditer(r'\*\*([^*]+?):\*\*\s*(.+?)(?=\n\*\*|\n\n|\Z)', body, re.DOTALL):
        label = match.group(1).strip()
        value = match.group(2).strip()
        fields[label] = value
    return fields

# Status inference: look for Live-Case dates, Fix labels, Prevention etc.
def infer_status(fields, body):
    body_lower = body.lower()
    if 'deployment' in fields or 'fix' in str(fields).lower():
        return 'resolved'
    if 'prevention (geplant)' in body_lower or '(geplant)' in body_lower:
        return 'pending'
    if 'prevention' in fields or 'policy' in fields or 'rule' in fields:
        return 'active'
    return 'active'

# Derive since-date from Live-Case or Quelle
def infer_since(fields, body):
    # Look for 2026-MM-DD patterns
    dates = re.findall(r'2026-\d{2}-\d{2}', body)
    if dates:
        return sorted(dates)[0]
    return None

# Enrich
out = []
for r in rules:
    body = '\n'.join(r['body_lines']).strip()
    fields = extract_fields(body)
    rec = {
        'id': r['id'],
        'title': r['title'],
        'category': r['category'],
        'status': infer_status(fields, body),
        'since': infer_since(fields, body),
        'rule': fields.get('Rule', fields.get('Policy', '')),
        'motivation': fields.get('Motivation', fields.get('Warum', '')),
        'live_case': fields.get('Live-Case', fields.get('Incident-Ref', '')),
        'source': fields.get('Quelle', fields.get('Source', '')),
        'fix': fields.get('Fix', fields.get('Deployment', fields.get('Fix 2026-04-19 12:05 (C2)', fields.get('Fix 2026-04-19 12:15 UTC', '')))),
        'prevention': fields.get('Prevention', fields.get('Absicherung', '')),
        'related_rules': re.findall(r'\bR\d+\b', body),
        'related_upstream': re.findall(r'#\d{4,6}|PR #\d+|Issue #\d+', body),
        'full_body': body
    }
    # Deduplicate related_rules, remove self-ref
    rec['related_rules'] = sorted(set(rec['related_rules']) - {rec['id']})
    out.append(rec)

# Write JSONL
DST.parent.mkdir(parents=True, exist_ok=True)
with DST.open('w', encoding='utf-8') as f:
    for rec in out:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')

print(f'Parsed {len(out)} rules')
print(f'Wrote to {DST}')
print(f'Categories:')
from collections import Counter
for cat, n in Counter(r['category'] for r in out).most_common():
    print(f'  {cat}: {n}')
