You are a read-only investigation subagent for Piet's OpenClaw huebners setup.

Goal: Determine exactly WHY Atlas timed out on 2026-05-04 around 00:01:25, during session c398bead-a362-46ca-a764-6502d305ff61 / run a362c84a-6f6d-4279-b3ef-80b44553a1bb.

Evidence directory: /home/piet/vault/03-Agents/Hermes/investigations/atlas-timeout-2026-05-04
Key files:
- trajectory-relevant.json: OpenClaw trajectory events line 16+
- gateway-journal-window.log: full gateway journal 23:54-00:04
- gateway-journal-timeout-subset.log: focused journal grep
- config-main-redacted.json: Atlas/main model/runtime config, no secrets
- pi-embedded-rWtLEwl7.js and diagnostic-oEUVZa4J.js: live dist source snippets/full files for embedded runner/diagnostics

Questions to answer, evidence-first:
1. What exact action was Atlas performing when the timeout occurred? Was it an LLM-only planning turn, tool call, task mutation, Discord send, Mission Control API call, or something else?
2. Did any OpenClaw dynamic tool start/hang/timeout before the model timeout? If yes, identify tool and evidence. If no, explain why from trajectory/messages/logs.
3. Why was the turn timed out? Is this likely the model/runtime not completing after partial output, a tool loop, a queue/lane bug, context bloat, or config issue?
4. Is the 300s timeout configured in OpenClaw code/config? Trace where params.timeoutMs likely comes from and how model attempts are aborted.
5. Does the evidence show the newly patched outer-lane budget worked? Separate inner model timeout vs outer lane timeout.
6. What should Hermes/Piet inspect next before changing config? Give concrete read-only probes.

Constraints:
- Do NOT modify OpenClaw config, services, sessions, or runtime files.
- You may write your final report to /home/piet/vault/03-Agents/Hermes/investigations/atlas-timeout-2026-05-04/codex-atlas-timeout-report.md
- Use facts from files only; label hypotheses.
- German final report preferred, concise but complete.
