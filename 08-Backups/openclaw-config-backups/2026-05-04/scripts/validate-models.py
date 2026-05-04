#!/usr/bin/env python3
"""
Validate cross-provider model references in openclaw.json.
Only checks: agents.defaults.model (primary + fallbacks) and agents.list[].model (primary + fallbacks).
Native provider model IDs (models[].id within providers) are excluded — they are provider-specific slugs.

Enhancements:
- Persist every run to memory/validators/YYYY-MM-DD.md
- Load false-positive prefixes from config (meta.validateModels.falsePositivePrefixes)
- Optionally create Mission Control follow-up task when real validation errors exist
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib import request

CONFIG_PATH = Path('/home/piet/.openclaw/openclaw.json')
MEMORY_ROOT = Path('/home/piet/.openclaw/workspace/memory/validators')
MISSION_CONTROL_TASKS_API = 'http://127.0.0.1:3000/api/tasks'

VALID_PROVIDER_PREFIXES = [
    'openrouter/', 'anthropic/', 'nvidia/',
    'deepseek/', 'modelstudio/', 'minimax/',
    'minimax-portal/', 'ollama/', 'moonshotai/',
    'qwen/', 'openai/', 'openai-codex/', 'google/',
    'meta-llama/', 'x-ai/', 'stepfun/',
    'xiaomi/', 'z-ai/',
]

DEFAULT_FALSE_POSITIVE_PREFIXES = [
    'minimax/', 'ollama/', 'moonshotai/', 'claude-cli/',
    'openrouter/x-ai/', 'openrouter/meta-llama/', 'openrouter/xiaomi/',
    'openrouter/stepfun/', 'openrouter/z-ai/',
]


def extract_model_refs(obj, path=''):
    """Extract model reference strings from agents.defaults.model and agents.list[].model."""
    results = []
    if isinstance(obj, dict):
        if 'primary' in obj or 'fallbacks' in obj:
            if 'primary' in obj and isinstance(obj['primary'], str):
                results.append((path + '.primary', obj['primary']))
            for i, fb in enumerate(obj.get('fallbacks', [])):
                if isinstance(fb, str):
                    results.append((f'{path}.fallbacks[{i}]', fb))
        for k, v in obj.items():
            results.extend(extract_model_refs(v, path + '.' + k))
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            results.extend(extract_model_refs(item, path + f'[{i}]'))
    return results


def is_valid_model(model_id: str):
    if any(model_id.startswith(p) for p in VALID_PROVIDER_PREFIXES):
        return True
    if re.search(r':(free|paid)$', model_id):
        return True
    return False


def is_false_positive(model_id: str, false_positive_prefixes):
    return any(model_id.startswith(p) for p in false_positive_prefixes)


def load_false_positive_prefixes(config):
    configured = (
        config.get('meta', {})
        .get('validateModels', {})
        .get('falsePositivePrefixes', [])
    )
    if not isinstance(configured, list):
        configured = []
    merged = []
    for p in DEFAULT_FALSE_POSITIVE_PREFIXES + configured:
        if isinstance(p, str) and p and p not in merged:
            merged.append(p)
    return merged


def append_run_log(log_path: Path, ts_iso: str, refs, false_positives, true_invalid):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    lines.append(f'## {ts_iso}')
    lines.append('')
    lines.append(f'- Total refs: {len(refs)}')
    lines.append(f'- True errors: {len(true_invalid)}')
    lines.append(f'- False positives ignored: {len(false_positives)}')
    lines.append('')

    if true_invalid:
        lines.append('### True Validation Errors')
        for path, model in true_invalid:
            lines.append(f'- `{path}` -> `{model}`')
        lines.append('')

    if false_positives:
        lines.append('### Ignored False Positives')
        for path, model in false_positives:
            lines.append(f'- `{path}` -> `{model}`')
        lines.append('')

    with log_path.open('a', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def create_followup_task(true_invalid):
    if not true_invalid:
        return None

    excerpt = '\n'.join([f'- {path}: {model}' for path, model in true_invalid[:25]])
    payload = {
        'title': f'validate-models: {len(true_invalid)} true validation errors',
        'description': (
            'Automatisch erstellt von validate-models.py wegen echter Model-Validation-Fehler.\n\n'
            f'Fehler (Top {min(len(true_invalid), 25)}):\n{excerpt}'
        ),
        'priority': 'P1',
        'tags': ['validators', 'models', 'automation'],
    }

    data = json.dumps(payload).encode('utf-8')
    req = request.Request(
        MISSION_CONTROL_TASKS_API,
        data=data,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        with request.urlopen(req, timeout=8) as resp:
            body = resp.read().decode('utf-8', errors='replace')
            return body
    except Exception:
        return None


def main():
    with CONFIG_PATH.open(encoding='utf-8') as f:
        config = json.load(f)

    refs = extract_model_refs(config)
    false_positive_prefixes = load_false_positive_prefixes(config)

    invalid = [(p, m) for p, m in refs if not is_valid_model(m)]
    false_positives = [(p, m) for p, m in invalid if is_false_positive(m, false_positive_prefixes)]
    true_invalid = [(p, m) for p, m in invalid if not is_false_positive(m, false_positive_prefixes)]

    now = datetime.now(timezone.utc)
    ts_iso = now.isoformat()
    date_str = now.strftime('%Y-%m-%d')
    log_path = MEMORY_ROOT / f'{date_str}.md'
    append_run_log(log_path, ts_iso, refs, false_positives, true_invalid)

    followup = create_followup_task(true_invalid)

    print(f'📝 Validation log updated: {log_path}')
    if followup:
        print('🧩 Mission Control follow-up task created for true validation errors.')

    if true_invalid:
        print(f'⚠️ {len(true_invalid)} TRUE INVALID MODEL IDs FOUND:')
        for path, model in true_invalid:
            print(f'  {path}: {model}')
        if false_positives:
            print(f'ℹ️ Ignored {len(false_positives)} configured false positives.')
        sys.exit(1)

    print(f'✅ All {len(refs)} cross-provider model references valid.')
    if false_positives:
        print(f'ℹ️ Ignored {len(false_positives)} configured false positives.')
    sys.exit(0)


if __name__ == '__main__':
    main()
