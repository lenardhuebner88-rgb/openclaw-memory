#!/usr/bin/env python3
import json, re, os
from pathlib import Path
from collections import defaultdict, Counter

ROOT = Path('/home/piet/.openclaw')
OUT = Path('/home/piet/vault/03-Agents/Hermes/investigations/atlas-timeout-2026-05-04/rootcause')
LOG = OUT/'gateway-24h.log'

def jloads(line):
    try: return json.loads(line)
    except Exception: return None

# 1) Journal timeout/fallback sequence
journal_events=[]
for line in LOG.read_text(errors='replace').splitlines():
    if any(s in line for s in ['codex app-server attempt timed out','model fallback decision','lane task error','stuck session','recovery skipped','timeout-compaction','fetch-timeout','nativeHook.invoke','tool timeout','dynamic tool timeout']):
        m_ts=re.search(r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+\+\d{2}:\d{2})', line)
        model_from=re.search(r'from=([^ ]+)', line)
        candidate=re.search(r'candidate=([^ ]+)', line)
        requested=re.search(r'requested=([^ ]+)', line)
        nextm=re.search(r'next=([^ ]+)', line)
        lane=re.search(r'lane=([^ ]+)', line)
        dur=re.search(r'durationMs=(\d+)', line)
        cls='other'
        if 'codex app-server attempt timed out' in line: cls='codex_timeout'
        if 'model fallback decision' in line: cls='fallback_decision'
        if 'lane task error' in line: cls='lane_error'
        if 'stuck session' in line or 'recovery skipped' in line: cls='stuck_diag'
        if 'timeout-compaction' in line: cls='timeout_compaction'
        if 'dynamic tool timeout' in line or 'tool timeout' in line: cls='tool_timeout'
        journal_events.append({
            'ts': m_ts.group(1) if m_ts else line[:15], 'class':cls,
            'model_from': model_from.group(1) if model_from else None,
            'candidate': candidate.group(1) if candidate else None,
            'requested': requested.group(1) if requested else None,
            'next': nextm.group(1) if nextm else None,
            'lane': lane.group(1) if lane else None,
            'durationMs': int(dur.group(1)) if dur else None,
            'line': line,
        })

# 2) Trajectory model.completed events: timeout/success, tool event count nearby
trajectory_events=[]
for p in sorted((ROOT/'agents').glob('*/sessions/*.trajectory.jsonl')):
    agent=p.parts[-3]
    lines=p.read_text(errors='replace').splitlines()
    last_ctx=None; last_prompt=None; in_attempt_events=[]
    for i,line in enumerate(lines,1):
        e=jloads(line)
        if not e: continue
        typ=e.get('type'); data=e.get('data') or {}; model=e.get('modelId')
        if typ=='context.compiled':
            last_ctx=data
            in_attempt_events=[]
        elif typ=='prompt.submitted':
            last_prompt=data.get('prompt')
            in_attempt_events=[]
        elif typ and typ.startswith('tool.'):
            in_attempt_events.append((i,typ,data.get('name') or data.get('toolName')))
        elif typ=='model.completed':
            usage=data.get('usage') or {}
            msg=data.get('messagesSnapshot') or []
            assistant_texts=data.get('assistantTexts') or []
            user_tail=''
            try:
                user_tail=str(msg[0].get('content',''))[-400:]
            except Exception: pass
            trajectory_events.append({
                'agent':agent,'session':p.stem.replace('.trajectory',''),'file':str(p),'line':i,
                'model':model,'timedOut':data.get('timedOut'),'aborted':data.get('aborted'),
                'promptError':data.get('promptError'),'usage':usage,
                'toolCountInContext': len((last_ctx or {}).get('tools') or []),
                'toolEventsBeforeComplete': list(in_attempt_events),
                'assistantText': '\n'.join(assistant_texts)[:1000],
                'userTail':user_tail,
            })
            in_attempt_events=[]

# 3) Session jsonl assistant messages with error/success for model stats
message_events=[]
for p in sorted((ROOT/'agents').glob('*/sessions/*.jsonl')):
    if p.name.endswith('.trajectory.jsonl'): continue
    agent=p.parts[-3]
    for i,line in enumerate(p.open(errors='replace'),1):
        e=jloads(line)
        if not e or e.get('type')!='message': continue
        m=e.get('message') or {}
        if m.get('role')=='assistant':
            message_events.append({
                'agent':agent,'session':p.stem,'file':str(p),'line':i,
                'timestamp': e.get('timestamp') or m.get('timestamp'),
                'model': m.get('model'), 'provider':m.get('provider'),
                'stopReason':m.get('stopReason'), 'errorMessage':m.get('errorMessage'),
                'usage':m.get('usage') or {},
                'text': str(m.get('content'))[:500]
            })

# Summaries
summary={}
summary['journal_counts']=Counter(e['class'] for e in journal_events)
summary['journal_timeout_models']=Counter(e['model_from'] or e['candidate'] for e in journal_events if e['class']=='codex_timeout')
by_model=defaultdict(lambda: Counter())
for e in trajectory_events:
    by_model[e['model']]['timeout' if e['timedOut'] else 'success'] += 1
summary['trajectory_by_model']={k:dict(v) for k,v in by_model.items()}
msg_by_model=defaultdict(lambda: Counter())
for e in message_events:
    key=e['model']
    if e['errorMessage']: msg_by_model[key]['error']+=1
    elif e['stopReason']=='stop': msg_by_model[key]['stop']+=1
    else: msg_by_model[key][str(e['stopReason'])]+=1
summary['messages_by_model']={k:dict(v) for k,v in msg_by_model.items()}

# Write artifacts
(OUT/'journal-timeout-events.json').write_text(json.dumps(journal_events,indent=2,ensure_ascii=False))
(OUT/'trajectory-model-events.json').write_text(json.dumps(trajectory_events,indent=2,ensure_ascii=False))
(OUT/'session-message-events.json').write_text(json.dumps(message_events,indent=2,ensure_ascii=False))
(OUT/'timeout-correlation-summary.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False,default=lambda x: dict(x)))

print(json.dumps(summary,indent=2,ensure_ascii=False,default=lambda x: dict(x)))
print('\nTimeout trajectory events:')
for e in trajectory_events:
    if e['timedOut']:
        print(f"- {e['agent']} {e['session']} line {e['line']} model={e['model']} err={e['promptError']} usage={e['usage']} toolEvents={e['toolEventsBeforeComplete']} text={e['assistantText'][:120]!r}")
print('\nRecent message errors:')
for e in message_events:
    if e['errorMessage']:
        print(f"- {e['timestamp']} {e['agent']} {e['session']} line {e['line']} model={e['model']} err={e['errorMessage']} usage={e['usage']} text={e['text'][:120]!r}")
