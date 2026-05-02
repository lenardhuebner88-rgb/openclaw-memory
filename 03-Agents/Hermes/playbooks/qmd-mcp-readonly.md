# QMD MCP Read-only

Use this when Hermes needs Vault/KB context through the QMD MCP bridge.

## Scope

Read-only QMD access only.

Canonical paths:

- Vault SSoT: `/home/piet/vault`
- KB compiler output: `/home/piet/vault/10-KB/`
- Do not use `/home/piet/Vault`.
- Do not treat `/home/piet/.openclaw/workspace/vault` as SSoT.

## Service Checks

```bash
systemctl --user status qmd-mcp-http.service --no-pager --lines=30
curl -s -H 'Accept: text/event-stream' -o /tmp/qmd_mcp_probe.out -w 'http=%{http_code}\n' http://127.0.0.1:8181/mcp
sed -n '1,20p' /tmp/qmd_mcp_probe.out
```

Expected direct HTTP behavior:

- `406` without `Accept: text/event-stream` means the HTTP MCP endpoint is alive but the client did not use the MCP/SSE accept header.
- `400` with `Server not initialized` after the SSE accept header means the MCP endpoint is reachable but a raw curl request did not perform the MCP initialize handshake.

## Hermes MCP Checks

```bash
hermes mcp list
hermes mcp test qmd-vault
```

Expected:

- `qmd-vault` listed as enabled.
- test connects.
- tools discovered: `search`, `vector_search`, `deep_search`, `get`, `multi_get`, `status`.

Hermes transport:

```yaml
qmd-vault:
  command: /home/piet/.local/bin/qmd
  args:
  - mcp
```

Reason:

- QMD's HTTP endpoint is live on `127.0.0.1:8181/mcp`.
- Raw HTTP probes and repeated Hermes HTTP tests can return `400` when the MCP session header is missing.
- Stdio MCP avoids that session-header instability for Hermes.

## Read-only Tool Boundary

QMD MCP source marks exposed tools with `readOnlyHint: true`.

Permitted uses:

- search for context;
- vector search for related concepts;
- deep search for ambiguous context;
- retrieve known documents by path/docid;
- get index status.

Forbidden in this playbook:

- reindexing;
- embedding generation;
- file writes;
- vault mutation;
- broad recursive scans outside QMD.

## Report Format

```text
Problem:
Evidence:
Risk:
Next Action:
```

If QMD MCP is down, do not restart automatically. Ask Piet for approval and state the exact restart command:

```bash
systemctl --user restart qmd-mcp-http.service
```
