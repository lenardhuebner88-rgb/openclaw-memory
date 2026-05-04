# Stable Baseline Snapshot — Mission Control / OpenClaw

Date: 2026-05-04 22:11 Europe/Berlin
Owner: Atlas
Scope: Sanitized stable-state baseline for Mission Control, Atlas runtime budgets, and active OpenClaw config shape.
Anti-Scope: No secrets, no raw API keys/tokens, no restart action, no config mutation.

## Executive Summary

- Mission Control health: `ok` / severity `ok`
- Board: openCount `0`, issueCount `0`
- Execution: recoveryLoad `0`, attentionCount `0`
- Dispatch consistency issues: `0`
- Worker proof: `ok`, openRuns `0`, issues `0`
- Pickup proof: `ok`, pendingPickup `0`, criticalFindings `0`
- Atlas budget proof: `ok-latest`, findings `0`
- Config fingerprint: `b273df41124ad39f` from `/home/piet/.openclaw/openclaw.json`

## Live Proofs

### /api/health
```json
{
  "status": "ok",
  "severity": "ok",
  "checks": {
    "board": {
      "status": "ok",
      "openCount": 0,
      "issueCount": 0
    },
    "dispatch": {
      "status": "ok",
      "consistencyIssues": 0,
      "orphanedDispatches": 0
    },
    "execution": {
      "status": "ok",
      "staleOpenTasks": 0,
      "recoveryLoad": 0,
      "attentionCount": 0
    },
    "costs": {
      "status": "ok",
      "criticalAnomalies": 0
    }
  },
  "metrics": {
    "totalTasks": 1002,
    "openTasks": 0,
    "inProgress": 0,
    "pendingPickup": 0,
    "review": 0,
    "blocked": 0,
    "failed": 0,
    "staleOpenTasks": 0,
    "orphanedDispatches": 0,
    "recoveryLoad": 0,
    "orphanRatio": 0,
    "dispatchStateConsistency": 1,
    "averageTaskAgeMs": 0,
    "criticalCostAnomalies": 0,
    "attentionCount": 0
  },
  "timestamp": "2026-05-04T20:11:06.667Z"
}
```

### /api/board-consistency
```json
{
  "status": "ok",
  "raw": {
    "openCount": 0,
    "issueCount": 0,
    "issues": []
  },
  "normalized": {
    "openCount": 0,
    "issueCount": 0,
    "issues": []
  }
}
```

### Worker Reconciler Proof
```json
{
  "status": "ok",
  "summary": {
    "tasks": 1002,
    "runs": 901,
    "openRuns": 0,
    "issues": 0,
    "criticalIssues": 0,
    "returnedIssues": 0
  }
}
```

### Pickup Proof
```json
{
  "status": "ok",
  "summary": {
    "pendingPickup": 0,
    "openPlaceholderRuns": 0,
    "historicalClaimTimeouts": 7,
    "claimTimeouts": 0,
    "totalClaimTimeoutEvents": 7,
    "activeSpawnLocks": 0,
    "activeSessionLocks": 0,
    "findings": 0,
    "criticalFindings": 0,
    "proposedActions": 0
  }
}
```

### Atlas Budget Proof
```json
{
  "status": "ok-latest",
  "findings": [],
  "gates": {
    "traceMetadataTargetBytes": 40000,
    "contextCompiledTargetBytes": 250000,
    "toolsSchemaTargetBytes": 8000,
    "bootstrapTotalTargetChars": 42000
  },
  "config": {
    "bootstrapMaxChars": 16000,
    "bootstrapTotalMaxChars": 42000,
    "atlasContextLimits": {
      "postCompactionMaxChars": 12000,
      "toolResultMaxChars": 4000,
      "memoryGetMaxChars": 10000
    }
  },
  "latest": {
    "file": "/home/piet/.openclaw/agents/main/sessions/78c61673-80ee-4b5d-a1d3-031be11b8f1a.trajectory.jsonl",
    "bytes": 3078617,
    "latestRun": {
      "runIndex": 14,
      "startedAt": "2026-05-04T20:10:32.486Z",
      "endedAt": null,
      "events": 4,
      "byType": {
        "session.started": 1,
        "trace.metadata": 1,
        "context.compiled": 1,
        "prompt.submitted": 1
      },
      "maxEventBytes": 36137,
      "maxContextCompiledBytes": 601,
      "maxTraceMetadataBytes": 36137,
      "maxPromptSubmittedBytes": 601,
      "maxSystemPromptChars": 0,
      "maxPromptChars": 0,
      "maxMessagesBytes": 4,
      "maxToolsBytes": 4,
      "maxToolsCount": 0,
      "compactedEvents": 0
    }
  }
}
```

### Port 3000
```text
State  Recv-Q Send-Q Local Address:Port Peer Address:PortProcess
LISTEN 2      511                *:3000            *:*    users:(("next-server (v1",pid=1437856,fd=21))
```

### Relevant Processes
```text
1437856 next-server (v15.5.15)
1449435 bash /home/piet/.openclaw/workspace/mission-control/scripts/task-parity-check.sh
1449748 /bin/bash --noprofile --norc -c set -euo pipefail TMP=/tmp/mc-stable-baseline-2026-05-04 mkdir -p "$TMP" # Live proofs; allow individual files to record failures rather than aborting everything. (curl -fsS -m 5 http://127.0.0.1:3000/api/health | jq '{status,severity,checks,metrics,timestamp}' > "$TMP/health.json") || echo '{"error":"health unavailable"}' > "$TMP/health.json" (curl -fsS -m 5 http://127.0.0.1:3000/api/board-consistency | jq '{status,raw:{openCount:.raw.openCount,issueCount:.raw.issueCount,issues:.raw.issues},normalized:{openCount:.normalized.openCount,issueCount:.normalized.issueCount,issues:.normalized.issues}}' > "$TMP/board-consistency.json") || echo '{"error":"board-consistency unavailable"}' > "$TMP/board-consistency.json" (curl -fsS -m 5 'http://127.0.0.1:3000/api/ops/worker-reconciler-proof?limit=20' | jq '{status,summary}' > "$TMP/worker-proof.json") || echo '{"error":"worker proof unavailable"}' > "$TMP/worker-proof.json" (curl -fsS -m 5 'http://127.0.0.1:3000/api/ops/pickup-proof?limit=20' | jq '{status,summary}' > "$TMP/pickup-proof.json") || echo '{"error":"pickup proof unavailable"}' > "$TMP/pickup-proof.json" (node /home/piet/.openclaw/scripts/atlas-orchestrator-budget-proof.mjs | jq '{status,findings,gates,config,latest:{file:.latest.file,bytes:.latest.bytes,latestRun:.latest.latestRun}}' > "$TMP/budget-proof.json") || echo '{"error":"budget proof unavailable"}' > "$TMP/budget-proof.json" (ss -ltnp '( sport = :3000 )' > "$TMP/port-3000.txt") || true (pgrep -af 'mc-restart-safe|next|mission-control|node.*3000' > "$TMP/processes.txt") || true # Sanitized config summary via node to avoid secrets. node - <<'NODE' > "$TMP/config-summary.json" const fs=require('fs'); const crypto=require('crypto'); const p='/home/piet/.openclaw/openclaw.json'; const cfg=JSON.parse(fs.readFileSync(p,'utf8')); const fp=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex').slice(0,16); function modelProviderSummary(providers){   const out={};   for (const [name,p] of Object.entries(providers||{})) {     out[name]={baseUrl:p.baseUrl?'<set>':undefined, auth:p.auth||undefined, api:p.api||undefined, modelCount:Array.isArray(p.models)?p.models.length:0, models:Array.isArray(p.models)?p.models.slice(0,20).map(m=>({id:m.id, contextWindow:m.contextWindow, maxTokens:m.maxTokens, input:m.input})):[]};   }   return out; } const agentsList=Array.isArray(cfg.agents?.list)?cfg.agents.list:[]; const agents=agentsList.map(a=>({   id:a.id,name:a.name,   model:a.model,   heartbeat:a.heartbeat,   thinkingDefault:a.thinkingDefault,   reasoningDefault:a.reasoningDefault,   fastModeDefault:a.fastModeDefault,   contextLimits:a.contextLimits,   bootstrapMaxChars:a.bootstrapMaxChars,   bootstrapTotalMaxChars:a.bootstrapTotalMaxChars,   toolsAllow:a.tools?.allow,   subagents:a.subagents,   params:a.params, })); const summary={   source:p,   sha256_16:fp,   generatedAt:new Date().toISOString(),   topLevelKeys:Object.keys(cfg).sort(),   agentsDefaults:{     model:cfg.agents?.defaults?.model,     compaction:cfg.agents?.defaults?.compaction,     maxConcurrent:cfg.agents?.defaults?.maxConcurrent,     subagents:cfg.agents?.defaults?.subagents,     timeoutSeconds:cfg.agents?.defaults?.timeoutSeconds,     bootstrapMaxChars:cfg.agents?.defaults?.bootstrapMaxChars,     bootstrapTotalMaxChars:cfg.agents?.defaults?.bootstrapTotalMaxChars,     contextLimits:cfg.agents?.defaults?.contextLimits,     memorySearch:cfg.agents?.defaults?.memorySearch ? {provider:cfg.agents.defaults.memorySearch.provider, model:cfg.agents.defaults.memorySearch.model, fallback:cfg.agents.defaults.memorySearch.fallback, sync:cfg.agents.defaults.memorySearch.sync, qmd:cfg.agents.defaults.memorySearch.qmd} : undefined,   },   agents,   session:cfg.session,   memory:cfg.memory,   gateway:cfg.gateway ? {host:cfg.gateway.host, port:cfg.gateway.port, publicBaseUrl:cfg.gateway.publicBaseUrl, cors:cfg.gateway.cors, health:cfg.gateway.health} : undefined,   channels:Object.fromEntries(Object.entries(cfg.channels||{}).map(([k,v])=>[k,{provider:v.provider, enabled:v.enabled, agentId:v.agentId, channelId:v.channelId, guildId:v.guildId, threadId:v.threadId, label:v.label} ])),   models:{mode:cfg.models?.mode, providerSummary:modelProviderSummary(cfg.models?.providers)}, }; console.log(JSON.stringify(summary,null,2)); NODE ls -l "$TMP"
```

## Sanitized Config Baseline

Secrets intentionally omitted. API keys/tokens are not persisted here. Provider entries include only shape, model IDs, context windows, and max token settings.

### Config Summary
```json
{
  "source": "/home/piet/.openclaw/openclaw.json",
  "sha256_16": "b273df41124ad39f",
  "generatedAt": "2026-05-04T20:11:09.650Z",
  "topLevelKeys": [
    "agents",
    "auth",
    "bindings",
    "channels",
    "commands",
    "gateway",
    "mcp",
    "memory",
    "messages",
    "meta",
    "models",
    "plugins",
    "session",
    "skills",
    "tools",
    "wizard"
  ],
  "agentsDefaults": {
    "model": {
      "primary": "openai-codex/gpt-5.5",
      "fallbacks": [
        "minimax/MiniMax-M2.7-highspeed",
        "openai-codex/gpt-5.3-codex",
        "minimax/MiniMax-M2.7",
        "openai-codex/gpt-5.4",
        "openai-codex/gpt-5.4-mini"
      ]
    },
    "compaction": {
      "mode": "safeguard",
      "recentTurnsPreserve": 6,
      "reserveTokens": 16000,
      "maxHistoryShare": 0.6,
      "qualityGuard": {
        "enabled": true,
        "maxRetries": 2
      },
      "memoryFlush": {
        "softThresholdTokens": 12000
      },
      "maxActiveTranscriptBytes": 3000000
    },
    "maxConcurrent": 2,
    "subagents": {
      "maxConcurrent": 4,
      "maxSpawnDepth": 2
    },
    "timeoutSeconds": 600,
    "bootstrapMaxChars": 16000,
    "bootstrapTotalMaxChars": 42000,
    "contextLimits": {
      "postCompactionMaxChars": 16000,
      "toolResultMaxChars": 5000,
      "memoryGetMaxChars": 16000
    },
    "memorySearch": {
      "provider": "openai",
      "model": "google/gemini-embedding-2-preview",
      "fallback": "none",
      "sync": {
        "onSessionStart": false,
        "onSearch": false,
        "watch": false
      },
      "qmd": {
        "extraCollections": [
          {
            "path": "/home/piet/vault",
            "name": "vault",
            "pattern": "**/*.md"
          }
        ]
      }
    }
  },
  "agents": [
    {
      "id": "main",
      "name": "Atlas",
      "model": {
        "primary": "openai-codex/gpt-5.5",
        "fallbacks": [
          "minimax/MiniMax-M2.7-highspeed",
          "openai-codex/gpt-5.3-codex",
          "minimax/MiniMax-M2.7",
          "openai-codex/gpt-5.4",
          "openai-codex/gpt-5.4-mini"
        ]
      },
      "heartbeat": {
        "every": "30m",
        "isolatedSession": true,
        "skipWhenBusy": true,
        "lightContext": true,
        "target": "none",
        "model": "openai-codex/gpt-5.4-mini",
        "timeoutSeconds": 120,
        "ackMaxChars": 80,
        "suppressToolErrorWarnings": true,
        "prompt": "Liveness check only. Do not read files, do not use tools, do not call APIs, do not inspect tasks, and do not continue previous work. Reply exactly HEARTBEAT_OK."
      },
      "thinkingDefault": "low",
      "reasoningDefault": "off",
      "fastModeDefault": true,
      "contextLimits": {
        "postCompactionMaxChars": 12000,
        "toolResultMaxChars": 4000,
        "memoryGetMaxChars": 10000
      },
      "toolsAllow": [
        "agents_list",
        "exec",
        "memory_get",
        "memory_search",
        "read",
        "session_status",
        "sessions_history",
        "sessions_list",
        "sessions_send",
        "sessions_yield",
        "subagents",
        "update_plan"
      ],
      "subagents": {
        "allowAgents": [
          "sre-expert",
          "frontend-guru",
          "efficiency-auditor",
          "james",
          "spark"
        ]
      },
      "params": {
        "wipLimit": 3
      }
    },
    {
      "id": "sre-expert",
      "name": "Forge",
      "model": {
        "primary": "openai-codex/gpt-5.3-codex",
        "fallbacks": [
          "minimax/MiniMax-M2.7-highspeed",
          "openai-codex/gpt-5.5",
          "minimax/MiniMax-M2.7",
          "openai-codex/gpt-5.4",
          "openai-codex/gpt-5.4-mini"
        ]
      },
      "heartbeat": {
        "every": "30m",
        "isolatedSession": true,
        "skipWhenBusy": true,
        "lightContext": true,
        "target": "none",
        "model": "openai-codex/gpt-5.4-mini",
        "timeoutSeconds": 120,
        "ackMaxChars": 80,
        "suppressToolErrorWarnings": true,
        "prompt": "Liveness check only. Do not read files, do not use tools, do not call APIs, do not inspect tasks, and do not continue previous work. Reply exactly HEARTBEAT_OK."
      },
      "thinkingDefault": "medium",
      "reasoningDefault": "off",
      "fastModeDefault": true,
      "subagents": {
        "allowAgents": [
          "main",
          "frontend-guru",
          "efficiency-auditor",
          "james",
          "spark"
        ]
      },
      "params": {
        "wipLimit": 2
      }
    },
    {
      "id": "frontend-guru",
      "name": "Pixel",
      "model": {
        "primary": "openai-codex/gpt-5.5",
        "fallbacks": [
          "minimax/MiniMax-M2.7-highspeed",
          "openai-codex/gpt-5.3-codex",
          "minimax/MiniMax-M2.7",
          "openai-codex/gpt-5.4",
          "openai-codex/gpt-5.4-mini"
        ]
      },
      "heartbeat": {
        "every": "30m",
        "isolatedSession": true,
        "skipWhenBusy": true,
        "lightContext": true,
        "target": "none",
        "model": "openai-codex/gpt-5.4-mini",
        "timeoutSeconds": 120,
        "ackMaxChars": 80,
        "suppressToolErrorWarnings": true,
        "prompt": "Liveness check only. Do not read files, do not use tools, do not call APIs, do not inspect tasks, and do not continue previous work. Reply exactly HEARTBEAT_OK."
      },
      "thinkingDefault": "low",
      "reasoningDefault": "off",
      "fastModeDefault": true,
      "params": {
        "wipLimit": 2
      }
    },
    {
      "id": "efficiency-auditor",
      "name": "Lens",
      "model": {
        "primary": "minimax/MiniMax-M2.7-highspeed",
        "fallbacks": [
          "openai-codex/gpt-5.5",
          "minimax/MiniMax-M2.7",
          "openai-codex/gpt-5.3-codex",
          "openai-codex/gpt-5.4",
          "openai-codex/gpt-5.4-mini"
        ]
      },
      "heartbeat": {
        "every": "30m",
        "isolatedSession": true,
        "skipWhenBusy": true,
        "lightContext": true,
        "target": "none",
        "model": "openai-codex/gpt-5.4-mini",
        "timeoutSeconds": 120,
        "ackMaxChars": 80,
        "suppressToolErrorWarnings": true,
        "prompt": "Liveness check only. Do not read files, do not use tools, do not call APIs, do not inspect tasks, and do not continue previous work. Reply exactly HEARTBEAT_OK."
      },
      "params": {
        "wipLimit": 1
      }
    },
    {
      "id": "james",
      "name": "James",
      "model": {
        "primary": "openai-codex/gpt-5.5",
        "fallbacks": [
          "minimax/MiniMax-M2.7-highspeed",
          "openai-codex/gpt-5.3-codex",
          "minimax/MiniMax-M2.7",
          "openai-codex/gpt-5.4",
          "openai-codex/gpt-5.4-mini"
        ]
      },
      "heartbeat": {
        "every": "30m",
        "isolatedSession": true,
        "skipWhenBusy": true,
        "lightContext": true,
        "target": "none",
        "model": "openai-codex/gpt-5.4-mini",
        "timeoutSeconds": 120,
        "ackMaxChars": 80,
        "suppressToolErrorWarnings": true,
        "prompt": "Liveness check only. Do not read files, do not use tools, do not call APIs, do not inspect tasks, and do not continue previous work. Reply exactly HEARTBEAT_OK."
      },
      "params": {
        "wipLimit": 2
      }
    },
    {
      "id": "system-bot",
      "name": "System Bot",
      "model": {
        "primary": "openai-codex/gpt-5.5",
        "fallbacks": [
          "minimax/MiniMax-M2.7-highspeed",
          "openai-codex/gpt-5.4",
          "minimax/MiniMax-M2.7",
          "openai-codex/gpt-5.4-mini",
          "openai-codex/gpt-5.3-codex"
        ]
      },
      "heartbeat": {
        "every": "30m",
        "isolatedSession": true,
        "skipWhenBusy": true,
        "lightContext": true,
        "target": "none",
        "model": "openai-codex/gpt-5.4-mini",
        "timeoutSeconds": 120,
        "ackMaxChars": 80,
        "suppressToolErrorWarnings": true,
        "prompt": "Liveness check only. Do not read files, do not use tools, do not call APIs, do not inspect tasks, and do not continue previous work. Reply exactly HEARTBEAT_OK."
      },
      "thinkingDefault": "off",
      "reasoningDefault": "off",
      "fastModeDefault": true,
      "toolsAllow": [
        "message",
        "read",
        "session_status",
        "sessions_history",
        "sessions_list"
      ],
      "params": {
        "wipLimit": 1
      }
    },
    {
      "id": "spark",
      "name": "Spark",
      "model": {
        "primary": "openai-codex/gpt-5.3-codex",
        "fallbacks": [
          "minimax/MiniMax-M2.7-highspeed",
          "openai-codex/gpt-5.5",
          "minimax/MiniMax-M2.7",
          "openai-codex/gpt-5.4",
          "openai-codex/gpt-5.4-mini"
        ]
      },
      "heartbeat": {
        "every": "30m",
        "isolatedSession": true,
        "skipWhenBusy": true,
        "lightContext": true,
        "target": "none",
        "model": "openai-codex/gpt-5.4-mini",
        "timeoutSeconds": 120,
        "ackMaxChars": 80,
        "suppressToolErrorWarnings": true,
        "prompt": "Liveness check only. Do not read files, do not use tools, do not call APIs, do not inspect tasks, and do not continue previous work. Reply exactly HEARTBEAT_OK."
      },
      "thinkingDefault": "low",
      "reasoningDefault": "off",
      "fastModeDefault": true,
      "params": {
        "wipLimit": 1
      }
    }
  ],
  "session": {
    "maintenance": {
      "mode": "enforce",
      "pruneAfter": "2d",
      "maxEntries": 60,
      "maxDiskBytes": "500mb",
      "highWaterBytes": "400mb",
      "resetArchiveRetention": "30d"
    }
  },
  "memory": {
    "qmd": {
      "command": "/home/piet/.local/lib/node_modules/@tobilu/qmd/qmd",
      "mcporter": {
        "enabled": false
      },
      "searchMode": "search",
      "limits": {
        "timeoutMs": 20000
      },
      "includeDefaultMemory": true,
      "paths": [
        {
          "path": "/home/piet/vault",
          "name": "vault",
          "pattern": "**/*.md"
        },
        {
          "path": "/home/piet/.openclaw/workspace/mission-control",
          "name": "mc-src",
          "pattern": "**/*.md"
        },
        {
          "path": "/home/piet/.openclaw/workspace/memory/facts",
          "name": "facts",
          "pattern": "**/*.jsonl"
        }
      ],
      "update": {
        "interval": "0m",
        "onBoot": false,
        "embedInterval": "0m"
      },
      "sessions": {
        "enabled": false
      },
      "scope": {
        "default": "allow",
        "rules": [
          {
            "match": {
              "channel": "discord",
              "chatType": "channel"
            },
            "action": "allow"
          }
        ]
      }
    },
    "backend": "qmd"
  },
  "gateway": {
    "port": 18789
  },
  "channels": {
    "telegram": {
      "enabled": true
    },
    "discord": {
      "enabled": true
    }
  },
  "models": {
    "mode": "merge",
    "providerSummary": {
      "nvidia": {
        "baseUrl": "<set>",
        "auth": "api-key",
        "api": "openai-completions",
        "modelCount": 1,
        "models": [
          {
            "id": "nemotron-3-super-120b-a12b",
            "contextWindow": 200000,
            "maxTokens": 8192,
            "input": [
              "text"
            ]
          }
        ]
      },
      "alibaba": {
        "baseUrl": "<set>",
        "auth": "api-key",
        "api": "openai-completions",
        "modelCount": 1,
        "models": [
          {
            "id": "qwen-turbo",
            "contextWindow": 200000,
            "maxTokens": 8192,
            "input": [
              "text"
            ]
          }
        ]
      },
      "modelstudio": {
        "baseUrl": "<set>",
        "api": "openai-completions",
        "modelCount": 6,
        "models": [
          {
            "id": "qwen3.5-plus",
            "contextWindow": 1000000,
            "maxTokens": 65536,
            "input": [
              "text",
              "image"
            ]
          },
          {
            "id": "qwen3-max-2026-01-23",
            "contextWindow": 262144,
            "maxTokens": 65536,
            "input": [
              "text"
            ]
          },
          {
            "id": "qwen3-coder-next",
            "contextWindow": 262144,
            "maxTokens": 65536,
            "input": [
              "text"
            ]
          },
          {
            "id": "glm-5",
            "contextWindow": 202752,
            "maxTokens": 16384,
            "input": [
              "text"
            ]
          },
          {
            "id": "glm-4.7",
            "contextWindow": 202752,
            "maxTokens": 16384,
            "input": [
              "text"
            ]
          },
          {
            "id": "kimi-k2.5",
            "contextWindow": 262144,
            "maxTokens": 32768,
            "input": [
              "text",
              "image"
            ]
          }
        ]
      },
      "ollama": {
        "baseUrl": "<set>",
        "auth": "api-key",
        "api": "openai-completions",
        "modelCount": 2,
        "models": [
          {
            "id": "qwen3.5:4b",
            "contextWindow": 32768,
            "maxTokens": 4096,
            "input": [
              "text"
            ]
          },
          {
            "id": "qwen3.5:latest",
            "contextWindow": 32768,
            "maxTokens": 4096,
            "input": [
              "text"
            ]
          }
        ]
      },
      "minimax-portal": {
        "baseUrl": "<set>",
        "auth": "api-key",
        "api": "openai-completions",
        "modelCount": 2,
        "models": [
          {
            "id": "MiniMax-M2.7-highspeed",
            "contextWindow": 200000,
            "maxTokens": 8192,
            "input": [
              "text"
            ]
          },
          {
            "id": "MiniMax-M2.7",
            "contextWindow": 200000,
            "maxTokens": 8192,
            "input": [
              "text"
            ]
          }
        ]
      },
      "minimax": {
        "baseUrl": "<set>",
        "auth": "api-key",
        "api": "anthropic-messages",
        "modelCount": 2,
        "models": [
          {
            "id": "MiniMax-M2.7",
            "contextWindow": 204800,
            "maxTokens": 131072,
            "input": [
              "text"
            ]
          },
          {
            "id": "MiniMax-M2.7-highspeed",
            "contextWindow": 200000,
            "maxTokens": 8192,
            "input": [
              "text"
            ]
          }
        ]
      },
      "openrouter": {
        "baseUrl": "<set>",
        "auth": "api-key",
        "api": "openai-completions",
        "modelCount": 6,
        "models": [
          {
            "id": "google/gemini-2.0-flash-001",
            "contextWindow": 1000000,
            "maxTokens": 8192,
            "input": [
              "text",
              "image"
            ]
          },
          {
            "id": "openrouter/deepseek-v3.2",
            "contextWindow": 200000,
            "maxTokens": 8192,
            "input": [
              "text"
            ]
          },
          {
            "id": "moonshotai/kimi-k2.6",
            "contextWindow": 256000,
            "maxTokens": 65536,
            "input": [
              "text",
              "image"
            ]
          },
          {
            "id": "deepseek/deepseek-v3.2",
            "contextWindow": 131072,
            "maxTokens": 65536,
            "input": [
              "text"
            ]
          },
          {
            "id": "stepfun/step-3.5-flash",
            "contextWindow": 262144,
            "maxTokens": 65536,
            "input": [
              "text"
            ]
          },
          {
            "id": "xiaomi/mimo-v2-pro",
            "contextWindow": 1048576,
            "maxTokens": 131072,
            "input": [
              "text"
            ]
          }
        ]
      },
      "openai": {
        "baseUrl": "<set>",
        "auth": "api-key",
        "api": "openai-completions",
        "modelCount": 1,
        "models": [
          {
            "id": "text-embedding-3-small",
            "contextWindow": 8191,
            "maxTokens": 8191,
            "input": [
              "text"
            ]
          }
        ]
      }
    }
  }
}
```

## Stable-State Acceptance Criteria

This snapshot is considered healthy when all are true:

- Mission Control `/api/health` returns `status=ok`.
- Board consistency raw + normalized issueCount are `0`.
- Board openCount is `0` or only deliberate current work.
- Execution recoveryLoad is `0`.
- Worker reconciler has `openRuns=0` and `issues=0`.
- Pickup proof has `pendingPickup=0` and `criticalFindings=0`.
- Atlas budget proof is `ok` or any finding is intentionally accepted with a documented gate update.

## Compare-Against Guidance

Use this file when the system becomes unstable. Compare:

- Current `/api/health` vs snapshot health.
- Current board issue/open counts vs snapshot.
- Current worker/pickup proof summaries vs snapshot.
- Current `openclaw.json` sanitized shape/fingerprint vs snapshot.
- Current Atlas budget gates and latest run metrics vs snapshot.

## Related Runbooks

- `03-Agents/OpenClaw/runbooks/mission-control-board-hygiene-hermes.md`
- `03-Agents/OpenClaw/runbooks/mission-control-unreachable-port-3000-recovery.md`
