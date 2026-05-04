#!/usr/bin/env python3
'''
apply-mcp-recovery-patch.py — P0.2 from atlas-stabilization-plan-mcp-recovery-2026-04-21.md

Patches createSessionMcpRuntime.callTool() in pi-bundle-mcp-runtime-*.js to invalidate
session cache on stdio MCP transport disconnect. Allows long-lived sessions to
self-recover from gateway-OOM/restart cycles without manual session restart.

Re-targeted for bundle architecture in v2026.4.22+ (callTool moved from
pi-bundle-mcp-tools-vusm-AE2.js Z.462 to pi-bundle-mcp-runtime-CuLwVkrV.js Z.587).

STATUS: AWAITING CODEX REVIEW. Do NOT enable systemd ExecStartPre auto-apply
until Codex has signed off in vault/03-Projects/plans/atlas-stabilization-plan-mcp-recovery-2026-04-21.md.

Usage:
  DRY_RUN=1 ./apply-mcp-recovery-patch.py    # default: show diff, no write
  DRY_RUN=0 ./apply-mcp-recovery-patch.py    # actually apply (with backup)

Idempotent: marker comment in patched file prevents double-application.
'''
import sys, os, re, datetime, shutil

BUNDLE_DIR = os.environ.get('BUNDLE_DIR', '/home/piet/.npm-global/lib/node_modules/openclaw/dist')
DRY_RUN = os.environ.get('DRY_RUN', '1') == '1'
MARKER = 'OPENCLAW_PATCH_MCP_RECONNECT_RECOVERY_2026_04_27'

# Find live runtime bundle (skip the small stub *-wdPhNMoF.js at 120 bytes)
candidates = sorted(
    [f for f in os.listdir(BUNDLE_DIR) if f.startswith('pi-bundle-mcp-runtime-') and f.endswith('.js')],
    key=lambda f: -os.path.getsize(os.path.join(BUNDLE_DIR, f))
)
if not candidates:
    print(f'FAIL: no pi-bundle-mcp-runtime-*.js in {BUNDLE_DIR}')
    sys.exit(1)
target = os.path.join(BUNDLE_DIR, candidates[0])
print(f'TARGET: {target} ({os.path.getsize(target)} bytes)')

with open(target) as f:
    content = f.read()

if MARKER in content:
    print(f'SKIP: marker {MARKER} already present — patch already applied')
    sys.exit(0)

# Match exact current callTool — uses tab-indented source as bundle is generated
old_pattern = (
    '\t\tasync callTool(serverName, toolName, input) {\n'
    '\t\t\tfailIfDisposed();\n'
    '\t\t\tawait getCatalog();\n'
    '\t\t\tconst session = sessions.get(serverName);\n'
    '\t\t\tif (!session) throw new Error(`bundle-mcp server "${serverName}" is not connected`);\n'
    '\t\t\treturn await session.client.callTool({\n'
    '\t\t\t\tname: toolName,\n'
    '\t\t\t\targuments: isMcpConfigRecord(input) ? input : {}\n'
    '\t\t\t});\n'
    '\t\t},'
)

new_block = (
    '\t\tasync callTool(serverName, toolName, input) {\n'
    '\t\t\tfailIfDisposed();\n'
    '\t\t\tawait getCatalog();\n'
    '\t\t\tconst session = sessions.get(serverName);\n'
    '\t\t\tif (!session) throw new Error(`bundle-mcp server "${serverName}" is not connected`);\n'
    '\t\t\ttry {\n'
    '\t\t\t\treturn await session.client.callTool({\n'
    '\t\t\t\t\tname: toolName,\n'
    '\t\t\t\t\targuments: isMcpConfigRecord(input) ? input : {}\n'
    '\t\t\t\t});\n'
    f'\t\t\t}} catch (error) {{ /* {MARKER} */\n'
    '\t\t\t\tconst msg = String((error && error.message) || error || "");\n'
    '\t\t\t\tif (msg.includes("Not connected") || msg.includes("Connection closed") || msg.includes("-32000")) {\n'
    '\t\t\t\t\ttry { await disposeSession(session); } catch (_) {}\n'
    '\t\t\t\t\tsessions.delete(serverName);\n'
    '\t\t\t\t\tcatalog = null;\n'
    '\t\t\t\t\tcatalogInFlight = void 0;\n'
    '\t\t\t\t}\n'
    '\t\t\t\tthrow error;\n'
    '\t\t\t}\n'
    '\t\t},'
)

if old_pattern not in content:
    print('WARN: callTool anchor pattern not found — bundle structure may have changed')
    print('      P0.2 patch skipped this run; investigate via \"grep -n callTool\" on target')
    print('      Marker for telemetry: P02_PATCH_SKIPPED_ANCHOR_MISSING')
    sys.exit(0)  # graceful: do not block gateway startup

new_content = content.replace(old_pattern, new_block, 1)
delta = len(new_content) - len(content)
print(f'PATCH_PREVIEW size_delta=+{delta} bytes (added try/catch + recovery)')

if DRY_RUN:
    print('=== DRY_RUN: not writing (set DRY_RUN=0 to apply) ===')
    print('--- NEW callTool block ---')
    print(new_block)
    sys.exit(0)

ts = datetime.datetime.now(datetime.UTC).strftime('%Y%m%dT%H%M%SZ')
backup = f'{target}.bak-pre-mcp-recovery-{ts}'
shutil.copy2(target, backup)
print(f'BACKUP: {backup}')

with open(target, 'w') as f:
    f.write(new_content)
print(f'APPLIED: bytes={len(new_content)} marker_check={MARKER in new_content}')
