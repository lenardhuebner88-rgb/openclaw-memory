#!/bin/bash
# Pre-Dispatch-Gate Hook for Claude Code
# Activates before any Bash command that looks like a Forge/Atlas sprint-dispatch.
# Blocks dispatch if pre-flight-sprint-dispatch.sh returns RED (exit 2).
# Continues if GREEN (exit 0) or YELLOW (exit 1, warns user).
#
# Installation: copy to .claude/hooks/pre-dispatch-gate.sh, chmod +x
# Referenced from .claude/settings.local.json PreToolUse block

set -u

TOOL_INPUT=$(cat)  # hook receives JSON on stdin

# Extract command from tool_input
COMMAND=$(echo "$TOOL_INPUT" | jq -r '.tool_input.command // ""')

# Only activate for sprint-dispatch-looking commands
if ! echo "$COMMAND" | grep -qE '(api/tasks.*/dispatch|sprint-dispatch|atlas.*sprint|forge.*dispatch)'; then
    # not our concern, pass through
    echo '{"continue": true}'
    exit 0
fi

# Run pre-flight on homeserver
PREFLIGHT_OUTPUT=$(ssh homeserver '/home/piet/.openclaw/scripts/pre-flight-sprint-dispatch.sh' 2>&1)
PREFLIGHT_EXIT=$?

case "$PREFLIGHT_EXIT" in
    0)
        # GREEN: safe dispatch
        echo '{"continue": true}'
        exit 0
        ;;
    1)
        # YELLOW: operator discretion
        echo "{\"continue\": true, \"message\": \"⚠️ Pre-flight YELLOW:\\n$PREFLIGHT_OUTPUT\\nProceeding — review before next sprint.\"}"
        exit 0
        ;;
    2)
        # RED: BLOCK
        echo "{\"continue\": false, \"stopReason\": \"🚨 Pre-flight RED — dispatch blocked:\\n$PREFLIGHT_OUTPUT\"}"
        exit 0
        ;;
    *)
        # Script error — fail-open (don't block production)
        echo "{\"continue\": true, \"message\": \"Pre-flight script error (exit $PREFLIGHT_EXIT): $PREFLIGHT_OUTPUT — fail-open.\"}"
        exit 0
        ;;
esac
