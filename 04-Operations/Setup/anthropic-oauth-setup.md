---
name: Anthropic OAuth Setup
description: Wie Anthropic OAuth für OpenClaw eingerichtet ist und wie der Token-Refresh funktioniert — gilt für Atlas (Sonnet) UND Forge-Opus (Opus)
type: project
---

**Gilt für:** Atlas (`anthropic/claude-sonnet-4-6`) via Claude.ai Pro OAuth, kein API-Key, keine direkten API-Kosten.
**Forge-Opus** (`anthropic/claude-opus-4-6`) läuft separat über direkten Anthropic API Key — nicht OAuth.

Atlas läuft auf `anthropic/claude-sonnet-4-6` via Claude.ai Pro OAuth (kein API-Key, keine Kosten).

**Token-Quelle:** `~/.claude/.credentials.json` → `claudeAiOauth.accessToken`
**Profil in OpenClaw:** `anthropic:claude-code` (type: api_key, OAuth-Token als Key)
**Ablauf:** alle ~5 Stunden

**Refresh-Mechanismus:**
- Claude Code refresht den Token automatisch beim Gebrauch
- Cron-Job alle 2h (um :17) synct neuen Token zu OpenClaw:
  `/home/piet/.openclaw/workspace/scripts/sync-anthropic-token.sh`
- Log: `/tmp/sync-anthropic-token.log`

**Falls Atlas morgens nicht antwortet:**
Einmal `claude` im Terminal starten → Token wird erneuert → Cron synct automatisch nach.

**Why:** Anthropic-API-Direkt-Refresh ist per Cloudflare gesperrt, deshalb indirekter Sync über Claude Code.
**How to apply:** Bei Atlas-Ausfällen zuerst Token-Status prüfen bevor andere Fehlersuche.
