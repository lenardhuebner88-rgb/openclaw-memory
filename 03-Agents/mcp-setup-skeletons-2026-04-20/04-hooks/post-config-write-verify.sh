#!/bin/bash
# Post-Config-Write-Verify Hook for Claude Code
#
# Activates after any Bash command that MIGHT have modified openclaw.json or
# scripts/*.py on the homeserver. Runs `openclaw doctor` — if Config invalid,
# ALERT loudly with revert instructions.
#
# This hook would have caught the 2026-04-20 06:00 UTC incident in <10 seconds
# instead of 25 minutes.
#
# Installation: copy to .claude/hooks/post-config-write-verify.sh, chmod +x
# Referenced from .claude/settings.local.json PostToolUse block

set -u

TOOL_INPUT=$(cat)  # hook receives JSON on stdin

COMMAND=$(echo "$TOOL_INPUT" | jq -r '.tool_input.command // ""')

# Only activate if command touched openclaw.json or a script file
if ! echo "$COMMAND" | grep -qE '(openclaw\.json|scripts/.*\.(py|sh))'; then
    echo '{"continue": true}'
    exit 0
fi

# Run doctor on server
DOCTOR_OUTPUT=$(ssh homeserver 'PATH=/home/piet/.openclaw/bin:$PATH openclaw doctor 2>&1')
DOCTOR_EXIT=$?

if echo "$DOCTOR_OUTPUT" | grep -q "Config invalid"; then
    # Invalid config — signal CRITICAL
    cat <<EOF
{
  "continue": true,
  "message": "🚨 CRITICAL: openclaw.json is now Config-INVALID after this command.\\n$DOCTOR_OUTPUT\\n\\nImmediate action: Revert via:\\n  ssh homeserver 'cp /home/piet/.openclaw/openclaw.json.bak /home/piet/.openclaw/openclaw.json'\\n\\nOr run: openclaw doctor --fix"
}
EOF
    # Also send Discord alert (fire-and-forget)
    WEBHOOK=$(ssh homeserver 'jq -r ".discord.webhookUrl // empty" /home/piet/.openclaw/openclaw.json.bak 2>/dev/null || echo ""')
    if [ -n "$WEBHOOK" ]; then
        curl -sS -X POST -H 'Content-Type: application/json' \
            -d "{\"content\": \"🚨 Claude Code Post-Hook: openclaw.json became INVALID after recent command. See logs.\"}" \
            "$WEBHOOK" > /dev/null 2>&1 || true
    fi
    exit 0
fi

# All good — silent pass
echo '{"continue": true}'
exit 0
