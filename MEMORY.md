# MEMORY.md — Langzeitgedächtnis

Nur dauerhafte, aktuell gültige Informationen. Historisches → `memory/archive-*.md`

---

## 📡 Ergebnis-Routing (Discord Channels)

| Ergebnistyp | Ziel-Channel |
|-------------|--------------|
| System-Alerts, Cron-Fails, auto-fix, Security | `#alerts` (1491148986109661334) |
| News, Blogwatcher, SkyWise, AI Procurement | `#news-hub` (1491150772224659649) |
| Ideen/Kurz-Analyse (Mention) | `#spark` (1487143853038502092) |
| News, Blogwatcher, SkyWise, AI Procurement | `#news-hub` (1491150772224659649) |
| Research, Analysen, Reports | `#status-reports` (1486480074491559966) |
| Infra, Cron, Config, Forge-specific | `#sre-expert` (1486480146524410028) |
| UI, Design, Components, Pixel-specific | `#pixel-frontend-guru` (1486480170763157516) |
| Architektur, Koordination, Entscheidungen | `#atlas-main` (1486480128576983070) |

**Regel:** Ergebnisse NICHT automatisch nach #atlas-main — nur wenn Entscheidungen nötig sind.
**Channel-Status:** #lens und #james existieren NICHT — nicht nutzen.

## 🔧 System-Grundsätze
- Config-Wahrheit: `openclaw.json` + Live-Verifikation > alte Doku
- Modelle: kostenbewusst, Stabilität vor Sparsamkeit
- Model-Auswahl: Wenn Nutzer ein Modell explizit benennt (z.B. "nimm Opus", "use /use-opus") → das Modell nutzen ohne nachzufragen. Ansonsten Model-Default des Agents.

## 🎯 Opus-Eskalation (Qualität auf Anfrage)

**Opus via OpenRouter** (`anthropic/claude-opus-4-6`) — nur wenn nötig, zahlt sich aus:

**Trigger:** "Opus", "Qualität", "deep analysis", "architektur" oder 2x MiniMax-Fehler hintereinander
**Kosten:** ~$0.015/1K tokens (15x teurer als MiniMax)

**Eskalations-Kette:**
1. MiniMax M2.7-highspeed (Default, quota-basiert)
2. Ollama/qwen3.5:4b (lokal, kostenlos, bei Failover)
3. Opus via OpenRouter (nur bei explizitem Zuruf oder 2x Failover)
- Agent-ID-Mapping: `resolveRuntimeAgentId()` in `task-assignees.ts` = Single Source of Truth

## 🔄 Subagent-Management
- Subagent-Sessions nach Abschluss automatisch aufräumen (nicht liegen lassen)
- `subagents kill <target>` wenn manuell eingreifen nötig
- maxConcurrent: 8 (verhindert zu viele parallele Subagenten)
- Bei vielen Child Sessions → prüfen ob Atlas/SRE Subagenten unnötig hält

## 📁 Projekte

### Home Server
- Lokaler Server für OpenClaw + Immich | Docker Compose | Budget 300-500€
- OpenClaw läuft bereits auf dem HomeServer (Linux) | Hardware bestellt (N100 oder ähnlich)
- OpenClaw darf NICHT auf Immich-Fotos zugreifen (strikte Netzwerk-Trennung)

### Phase 3 — Selbst-Optimisierung & Qualitätssicherung
- **2026-04-08: Sprint 1-3 ABGESCHLOSSEN** — Atlas hat SYS-Tasks autonom abgearbeitet:
  ✅ Sprint 1.1 Config-Validator | Sprint 1.2 Health-Monitor | Sprint 1.3 Build-Integrity | Sprint 1.4 Gateway Auto-Restart
  ✅ Sprint 2.1 SQLite+CRUD+Search | Sprint 2.3 DB-Migration
  ✅ Sprint 3.1 Model Status API | Sprint 3.2 Smart Concurrent Fallback | Sprint 3.3 All-Models-Down Alert
- Plan: `/home/piet/.openclaw/workspace/ATLAS_PHASE_3_PLAN.md`
- Status: **Phase 3 Sprint 1-3 DONE — Selbst-Entwicklung funktioniert! Selbstheilung + Monitoring aktiv.**

### Claude Code Telegram Bridge (2026-04-08)
- Bot: `@piet_huebners_claude_bot` | Token: `8649383877:AAEE_utODbRdXafZSq41499IXF9_-8VxqYc`
- Service: systemd user (`claude-telegram-bridge`), läuft stabil
- Commands: `/model qwen|sonnet|opus`, `/status`, `/health`, `/agents`, `/crons`, `/tasks`, `/logs`, `/ping`, `/disk`, `/uptime`, `/fail`, `/task`, `/alert`, `/restart`
- Modelle: qwen (Ollama, kostenlos), sonnet (Claude Pro), opus (Claude Pro)
- File: `/home/piet/.openclaw/scripts/claude-telegram-bridge.py`

### Mission Control — Production Mode (2026-04-08, updated 2026-04-09)
- **Service:** systemd user (`mission-control.service`), Port 3000, `next start` (Production)
- **URL (PC/Handy):** http://192.168.178.61:3000 | Binding: 0.0.0.0 (LAN)
- **Build:** Kopiert von `workspace-frontend-guru/mission-control-src/.next`
- **Memory:** ~60MB (Production, deutlich weniger als Dev)
- **Hinweis:** `next build` schlägt fehl (Prozess wird von SIGKILL beendet, OOM/Docker-Limit)
  → Bei Build-Bedarf: Build in `workspace-frontend-guru/mission-control-src` ausführen, dann hierher kopieren

### Finanzdashboard
- MVP fertig (Streamlit + Plotly) | ING-CSV Import, Kategorien, KPIs
- Offen: Design-Polish, Depot/Kredit optional

## 📱 MC Mobile Optimierung Phase 2
- Task `2f428841-44ef-4edd-af55-747069c9d1cb` erstellt, Pixel assigned
- Scope: Bottom-Nav, Vollbild-Modals Mobile, Touch-Targets 44px+, Lane-Gestures
- Bestehende Mobile-Optimierungen (2026-04-01) erhalten

## 🔧 MC Stability
- MC build bleibt gelegentlich hängen → HTTP 500
- **Nächste Aktion:** MC als systemd Service einrichten (offen seit 2026-04-08)

## 💰 Finanzen
- **Einkommen:** ~6.200€ netto (Lenard 4.300 + Anna 1.400 + Kindergeld 500)
- **Baufinanzierung:** 298.000€ Restschuld
- **Depot:** ~25.825€ | **Liquidität:** ~5.177€
- **⚠️ Keine BU-Versicherung** — Hochrisiko mit 2 Kindern + Kredit
- **Sparziele:** Notgroschen 20K, Wärmepumpe 2027, PV 2028, E-Auto 2029

## 🧭 Atlas Operating Rules
- Orchestrator, nicht Implementierer
- Task Board = Single Source of Truth
- Eine Entscheidung pro Zyklus, keine Parallelbaustellen
- Delegation: klarer Scope, ein Owner, klares Ergebnis

### Routing-Matrix
- UI/UX → frontend-guru | Infra/Code → sre-expert | Analyse → efficiency-auditor
- Quick → main | Ideation → ideen (Channel-basiert, nicht Agent) | Recherche → researcher
- **Premium (Opus):** → forge-opus (schwere Bugs, Root-Cause, Architektur)
- **Agent-Status:**
  - ✅ Aktiv: main (Atlas), sre-expert (Forge), frontend-guru (Pixel), efficiency-auditor (Lens), researcher (James), forge-opus
  - 🔄 In Rekonfiguration: quick (Flash) — local-runner Setup für Ollama Qwen 3.5
  - 💡 Channel-Konzept: ideen — Discord Channel mit Mention-Trigger für Analyse
  - ⚠️ Zombie (ENTFERNT): projekte, orchestrator-free, acp-defaultagent, model-monitor (Pulse)

### Modell-Routing (HARTE REGEL)
- KEIN Modellrouting über sessions_spawn(model: ...) — funktioniert unzuverlässig
- Modellwahl NUR über Agent-Auswahl

### Dual-Subscription Stack (2026-04-08)
| Abo | Kosten | Modelle | Nutzung |
|-----|--------|---------|---------|
| **ChatGPT Pro** | €200/Monat | `openai-codex/gpt-5.4` (Primary), GPT-5.4-mini, GPT-5.3-Codex | Codex Primary für forge-opus, Fallback für alle Agents |
| **MiniMax Tokenplan Plus** | €40/Monat | `minimax/MiniMax-M2.7-highspeed` (Primary), MiniMax M2.7 | Primary für alle Standard-Agents |
| **OpenRouter** | ~$10/Monat | DeepSeek, Gemini, Ollama | Reserve-Fallbacks, kostenlose Modelle |

### Agent-Modell-Zuordnung
| Agent | Primary | Fallback 1 | Fallback 2 | Fallback 3 | Fallback 4 |
|-------|---------|-----------|-----------|-----------|-----------|
| main (Atlas) | MiniMax M2.7 HS | MiniMax M2.7 | Codex GPT-5.4 | openrouter/auto | **Ollama Qwen 3.5** |
| sre-expert (Forge) | **Codex GPT-5.3** | MiniMax M2.7 HS | Codex GPT-5.4 | openrouter/auto | **Ollama Qwen 3.5** |
| frontend-guru (Pixel) | MiniMax M2.7 HS | Codex GPT-5.4 | openrouter/auto | **Ollama Qwen 3.5** | — |
| efficiency-auditor (Lens) | MiniMax M2.7 HS | Codex GPT-5.4 | openrouter/auto | **Ollama Qwen 3.5** | — |
| researcher (James) | MiniMax M2.7 HS | Codex GPT-5.4 | openrouter/auto | **Ollama Qwen 3.5** | — |
| forge-opus | **Opus 4.6** | MiniMax M2.7 HS | Codex GPT-5.4 | openrouter/auto | **Ollama Qwen 3.5** |
| local-runner | **Ollama Qwen 3.5** | openrouter/auto | — | — | — |

**Trigger forge-opus:** Root-Cause, schwere Bugs, Architekturentscheidungen, komplexe Refactors
**Trigger Codex (Standard-Agents):** Wenn MiniMax Timeout oder Rate-Limit

### Worker-Contract
**Single Source of Truth:** `HEARTBEAT.md` — vollständige Worker/Heartbeat-Dokumentation.

### Config Safety
1. Feld identifizieren → 2. Werte belegen → 3. Minimal ändern → 4. Validieren → 5. Bei Fehler stoppen

## 🔄 Worker Contract
**Single Source of Truth:** `HEARTBEAT.md`

## 🧪 Adaptive Learning Loop
- **Error → Learning:** Jeder Cron-Error, Worker-Crash, Model-Fehler → POST /api/learnings
- **Correction → Learning:** Wenn Lenard korrigiert ("Nein", "Falsch", "Mach das anders") → sofort loggen mit Kategorie `correction`
- **Pattern Detection:** Sonntag 05:00 → scannt learnings.md nach Mustern → erstellt Tasks
- **Nightly Build:** scannt learnings.md als Verbesserungsquelle (Skill v2)

## 🔐 Sicherheit
- Betrieb lokal, Finanz-/CSV-Daten sensitiv, Credentials in openclaw.json

## MC Fix — 2026-04-09
- MC down nach `.next`-Clear (dev-server Buildkorruption)
- Root cause: Next.js 15 dev-server braucht `middleware-manifest.json` (wird nicht automatisch generiert wenn kein middleware exists)
- Fix: Production-Build (`NODE_OPTIONS=--max-old-space-size=4096 npx next build`)
- Costs-Page hatte `statSync` auf gelöschte Session-Files → `export const dynamic = 'force-dynamic'` in `src/app/costs/page.tsx`
- Service jetzt: `next start` + `NODE_ENV=production` (nicht mehr dev mode)
- BUILD ID exists in `.next/BUILD_ID`
