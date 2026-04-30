#!/usr/bin/env python3
import json
import re
from pathlib import Path

QUEUE_PATH = Path('/home/piet/.openclaw/research-queue.json')
TOPICS_PATH = Path('/home/piet/.openclaw/research-topics.txt')


def normalize_topic(value: str) -> str:
    return re.sub(r'\s+', ' ', value.strip()).casefold()


def load_queue() -> dict:
    if not QUEUE_PATH.exists():
        return {'queue': []}
    with QUEUE_PATH.open('r', encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, dict):
        return {'queue': []}
    queue = data.get('queue')
    if not isinstance(queue, list):
        data['queue'] = []
    return data


def load_topics() -> list[str]:
    if not TOPICS_PATH.exists():
        return []
    lines = TOPICS_PATH.read_text(encoding='utf-8').splitlines()
    topics: list[str] = []
    for raw in lines:
        text = re.sub(r'\s+', ' ', raw.strip())
        if not text:
            continue
        if text.startswith('#'):
            continue
        topics.append(text)
    return topics


def main() -> int:
    data = load_queue()
    queue = data.get('queue', [])

    existing_norm = set()
    max_id = 0
    max_priority = 0

    for item in queue:
        if not isinstance(item, dict):
            continue
        topic = item.get('topic')
        if isinstance(topic, str) and topic.strip():
            existing_norm.add(normalize_topic(topic))
        try:
            max_id = max(max_id, int(item.get('id', 0)))
        except Exception:
            pass
        try:
            max_priority = max(max_priority, int(item.get('priority', 0)))
        except Exception:
            pass

    added = 0
    skipped = 0
    for topic in load_topics():
        n = normalize_topic(topic)
        if n in existing_norm:
            skipped += 1
            continue
        max_id += 1
        max_priority = max_priority + 1 if max_priority > 0 else 1
        queue.append({
            'id': max_id,
            'priority': max_priority,
            'topic': topic,
            'status': 'open',
        })
        existing_norm.add(n)
        added += 1

    data['queue'] = queue
    QUEUE_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    print(f'RESEARCH_QUEUE_ADD_OK added={added} skipped={skipped} total={len(queue)} queue={QUEUE_PATH}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
