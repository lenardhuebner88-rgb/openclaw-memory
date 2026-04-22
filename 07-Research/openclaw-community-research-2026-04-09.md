# OpenClaw Community Research — 2026-04-09

**Recherche:** Sprint 5.5 | **Datum:** 9. April 2026

---

## 1. GitHub Issues — Top Feature Requests & Offene Probleme

### High-Voted Open Issues

---

## ISSUE: Internationalization (i18n) & Localization Support
- **Votes/Reactions:** ~120 (⚡ icon on issue page)
- **Status:** Open
- **URL:** https://github.com/openclaw/openclaw/issues/3460
- **Beschreibung:** Zentrales Tracking-Issue für i18n. Wanted: zh-CN, zh-TW, pt-BR, ko, ja, es, fr, de, vi, fil. OpenClaw-Team hat kein Bandwidth aktuell — keine Timeline.
- **Relevance fuer uns:** **Hoch** — DE/DE timezone Nutzer, deutsches Interface wäre Value-add
- **ROI-Score:** 7/10

---

## ISSUE: Linux/Windows Clawdbot Apps
- **Votes/Reactions:** ~78
- **Status:** Open
- **URL:** https://github.com/openclaw/openclaw/issues/75
- **Beschreibung:** macOS/iOS/Android Apps existieren, aber Linux & Windows fehlen. Similar feature set zu macOS ideally.
- **Relevance fuer uns:** **Mittel** — Wir betreiben auf Linux, native App weniger relevant als Gateway/node deployment
- **ROI-Score:** 5/10

---

## ISSUE: [Bug] sessions_spawn returns "gateway closed (1008): pairing required"
- **Votes:** ~12 (aktuell gestern gemeldet)
- **Status:** Open
- **URL:** https://github.com/openclaw/openclaw/issues/63776
- **Beschreibung:** Subagent spawning via sessions_spawn schlägt mit Pairing-Fehler fehl. Blockiert Multi-Agent-Workflows.
- **Relevance fuer uns:** **Hoch** — Wir nutzen Subagents direkt (Coding Agent Skill)
- **ROI-Score:** 9/10

---

## ISSUE: [Bug] Multi-ollama provider routing still broken after #61776
- **Votes:** ~8 (aktuell gestern)
- **Status:** Open
- **URL:** https://github.com/openclaw/openclaw/issues/63775
- **Beschreibung:** Requests gehen trotz multi-provider config immer an ersten Provider. Routing-Logik kaputt nach letztem Fix.
- **Relevance fuer uns:** **Hoch** — Falls wir Ollama mit mehreren Providern nutzen wollen
- **ROI-Score:** 8/10

---

## ISSUE: [Bug] Isolated cron agentTurn jobs still hard-killed at ~300s despite fix
- **Votes:** ~5 (heute gemeldet)
- **Status:** Open
- **URL:** https://github.com/openclaw/openclaw/issues/63805
- **Beschreibung:** Cron-Jobs mit explizitem timeoutSeconds werden trotz Fix in v2026.4.9 nach ~300s gekillt. Long-running cron tasks betroffen.
- **Relevance fuer uns:** **Hoch** — Wir nutzen Cron-Jobs für Heartbeats/Periodische Tasks
- **ROI-Score:** 9/10

---

## ISSUE: [Bug] Discord channel missing from bundled sidecar fix in 2026.4.8/2026.4.9
- **Votes:** ~6 (heute)
- **Status:** Open + Regression
- **URL:** https://github.com/openclaw/openclaw/issues/63774
- **Beschreibung:** Discord channel fehlt im bundled sidecar fix → bricht auf Homebrew Installation. Unser Setup = Discord + Homebrew → direkt betroffen.
- **Relevance fuer uns:** **Kritisch** — Wir nutzen Discord als primären Kanal
- **ROI-Score:** 10/10

---

## ISSUE: Session lock file not released after LLM idle timeout
- **Votes:** ~4 (heute)
- **Status:** Open
- **URL:** https://github.com/openclaw/openclaw/issues/63784
- **Beschreibung:** Lock-Datei wird nach idle timeout nicht freigegeben → kein Gateway-Restart nötig, aber Session-Logik kaputt.
- **Relevance fuer uns:** **Mittel**
- **ROI-Score:** 6/10

---

## ISSUE: ACP completion delivery-mirror does not activate next turn after sessions_yield
- **Votes:** ~3 (heute)
- **Status:** Open
- **URL:** https://github.com/openclaw/openclaw/issues/63779
- **Beschreibung:** ACP-Kompletions spiegeln nicht in nächste Turn nach sessions_yield. Subagent-Koordination betroffen.
- **Relevance fuer uns:** **Hoch** — Wir nutzen Subagents mit sessions_yield
- **ROI-Score:** 8/10

---

## ISSUE: [Bug] v2026.4.9 voicecall outbound double-binds serve.port — EADDRINUSE
- **Votes:** ~5 (heute)
- **Status:** Open
- **URL:** https://github.com/openclaw/openclaw/issues/63771
- **Beschreibung:** Voicecall outbound bindet Port doppelt → EADDRINUSE. Edge-Case aber reproduzierbar.
- **Relevance fuer uns:** **Niedrig** — Voice-Features nicht aktiv im Einsatz
- **ROI-Score:** 3/10

---

## ISSUE: Browser plugin config validator rejects object-format streaming config
- **Votes:** ~2 (heute)
- **Status:** Open
- **URL:** https://github.com/openclaw/openclaw/issues/63788
- **Beschreibung:** Browser plugin config validator rejectet object-format streaming config — schluckt keine Objekte.
- **Relevance fuer uns:** **Mittel** — Falls Browser-Automation genutzt wird
- **ROI-Score:** 5/10

---

## 2. Security — Offene CVE / Security Issues

---

## SECURITY: CVE-2026-32922 (CVSS 9.9) — Device Pairing Privilege Escalation
- **Severity:** Critical (CVSS 9.9)
- **Status:** Offen (März 2026 Tsunami — 15+ CVEs in 30 Tagen)
- **URL:** https://github.com/openclaw/openclaw/security
- **Beschreibung:** Jedes gepaarte Device kann vollen Admin-Zugang + RCE mit einem API-Call erhalten. 135.000+ exponierte Instanzen.
- **Relevance fuer uns:** **Kritisch** — Unsere Node-Pairing-Architektur direkt betroffen
- **ROI-Score:** 10/10

---

## SECURITY: CVE-2026-33579 (CVSS 8.1–9.8) — Pairing Privilege Escalation
- **Severity:** High
- **Status:** Offen
- **URL:** https://github.com/openclaw/openclaw/security/advisories
- **Beschreibung:** /pair approve erlaubt Scope-Escalation zu Full Admin. Gepatcht in 2026.3.28 — aber viele Instanzen noch ungepatched.
- **Relevance fuer uns:** **Hoch** — Pairing-Flow ist Kern unsrer Architektur
- **ROI-Score:** 9/10

---

## SECURITY: ClawHavoc Supply Chain Attack (Jan 2026)
- **Severity:** Critical
- **Status:** Abgewehrt — aber Nachwirkungen
- **Beschreibung:** 341 bösartige Skills (Atomic Stealer Malware), 2.419 verdächtige Skills entfernt. ~12% aller ClawHub Packages kompromittiert.
- **Relevance fuer uns:** **Hoch** — Skills-Installationen brauchen Sicherheits-Audit
- **ROI-Score:** 8/10

---

## 3. ClawHub.ai — Skills

### Top 10 Popular Skills (nach Downloads)

| Skill | Downloads | Kategorie | Relevance fuer uns |
|---|---|---|---|
| Capability Evolver | 35.581+ | AI/ML | Niedrig — self-evolution, riskant |
| Wacli | 16.415+ | Utility | Mittel |
| ByteRover | 16.004+ | Utility | Mittel |
| Self-Improving Agent | 15.962+ | AI/ML | Niedrig — security risk |
| ATXP | 14.453+ | Utility | Niedrig |
| **GOG** (Google Workspace) | 14.313+ | Development | **Hoch** — Gmail, Calendar, Drive |
| **Agent Browser** | 11.836+ | Web | **Hoch** — Web automation |
| **Summarize** | 10.956+ | Productivity | **Hoch** — Content processing |
| **GitHub** | 10.611+ | Development | **Hoch** — PR/Issue Management |
| Sonoscli | 10.304+ | Media | Niedrig |

### Skills die zu unserem Setup passen

- **Discord** (clawhub.ai/steipete/discord) — 2K+ downloads — Community management, bot control
- **Mission Control** — Morning briefings, aggregiert Cal + Messages + GitHub — **direkt passend zu unsrem Setup**
- **Slack** — 6K+ downloads — Team messaging automation
- **Telegram** —技能的 Telegram integration (separates skill)
- **GOG** — Google Workspace (Gmail, Calendar, Drive) — **passt zu google-calendar skill**
- **Tavily Search** — 8K+ downloads — AI-optimized web search

### Security Warning
ClawHub: nach ClawHavoc ~7.6% aller Skills als gefährlich eingestuft. Virustotal-Scanning jetzt Standard, aber weiterhin bösartige Uploads. **100/3 Regel:** 100+ Downloads UND 3+ Monate alt = sicherer.

---

## 4. Community — Discord & Diskussion

### Discord Server (discord.com/invite/clawd)
- **100.000+ Mitglieder** (Januar 2026 gegründet → schnellstes Wachstum)
- Community-Namensgebung: "Friends of the Crustacean"
- **Crypto-Ban** nach CLAWD Token Scam (Feb 2026) — alle Crypto-Diskussionen verboten
- Server-Regeln: "Clawd has feelings too" — lockerer Ton
- Haupt-Diskussionsthemen:
  - Setup-Fragen (bes. Discord + Telegram Kanal-setup)
  - Security hardening nach CVE-Flut
  - Skill-Empfehlungen
  - Self-hosting auf VPS
  - Gateway-Restart-Probleme

### Hacker News / Reddit Mentions
- OpenClaw übertrifft React als #1 GitHub Starred Project (März 2026) — 250K+ Stars in 60 Tagen
- Jetzt 346K GitHub Stars, 3.2M Nutzer, 500K Instanzen
- 135.000+ exponierte Instanzen im Internet — Security-Scorecard
- Meta hat interne OpenClaw-Nutzung eingeschränkt nach Februar CVE disclosures

### Versions-Tracking
- **Aktuell:** v2026.4.9 (Latest — 9. April 2026)
- Letzte Stable: v2026.3.13 Line
- Browser-Control im Wandel: Weg von Chrome Extension Relay → User Browser Attachment
- Neueste Features: Gemma 4, Ollama Vision, Webhook TaskFlows, Memory Wiki (v2026.4.7)

---

## 5. Top 10 Feature-Requests — ROI-Score Sortiert

| # | Feature | ROI-Score | Warum |
|---|---|---|---|
| 1 | **Discord channel fix (regression in 2026.4.8/9)** | **10** | Unser Primary Channel — bricht auf aktuellem Build |
| 2 | **CVE-2026-32922 Patch applyen** | **10** | Crit security — sofort handeln |
| 3 | **Cron hard-kill Bug fix (~300s)** | **9** | Heartbeat/Cron-System betroffen |
| 4 | **sessions_spawn pairing fix** | **9** | Multi-Agent Workflows blockiert |
| 5 | **Multi-Ollama Provider Routing fix** | **8** | Falls Ollama-Multi-Provider gewünscht |
| 6 | **ACP completion mirror nach sessions_yield** | **8** | Subagent-Koordination |
| 7 | **i18n / Localization (DE)** | **7** | Deutsch-Interface für unsren Nutzer |
| 8 | **Mission Control Skill** | **7** | Passt perfekt zu unsrem Morning-Briefing-Setup |
| 9 | **GOG (Google Workspace) Skill** | **7** | Erweitert google-calendar skill um Drive + Gmail |
| 10 | **Security Auditor Skill (ClawHub)** | **6** | ClawHavoc-Nachwirkung — Skills sicher verifizieren |

---

## 6. Sofort-Aktionen fuer unsren Setup

1. **Security:** Upgrade auf v2026.4.9 (CVE-2026-33579 Patch in 2026.3.28 enthalten)
2. **Discord-Regression:** Issue #63774 beobachten — Workaround: nicht via Homebrew installieren bis fix
3. **Cron-Bug:** Heartbeat-Crons mit kürzerem timeout konfigurieren als 300s bis Patch
4. **ClawHub Skills:** Vor Installation immer Quellcode lesen + 100/3 Regel anwenden
5. **CANVAS_HOST=127.0.0.1** setzen (0.0.0.0 Binding ist Sicherheitsrisiko)
6. **Mission Control Skill evaluieren** — perfekter Fit für Morning Briefing Pipeline

---

*Research by Subagent | Sprint 5.5 | 2026-04-09*
