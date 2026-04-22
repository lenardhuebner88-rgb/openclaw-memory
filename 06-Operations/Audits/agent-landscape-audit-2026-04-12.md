# Agent Landscape Audit — 2026-04-12

**Durchgeführt von:** Lens  
**Zweck:** IST-Analyse als Entscheidungsgrundlage für Atlas + Forge-Handover

---

## Agenten-Status (Stand Audit)

| Agent | ID | Modell | Status | Befund |
|-------|-----|--------|--------|--------|
| Atlas | main | GPT-5.4 | ✅ aktiv | Orchestrator, täglich genutzt |
| Forge | sre-expert | GPT-5.3 Codex | ✅ aktiv | Hauptentwickler, täglich genutzt |
| James | researcher | MiniMax M2.7-HS | ✅ aktiv | task-gebunden, sporadisch |
| Pixel | frontend-guru | MiniMax M2.7-HS | ⚠️ unklar | zuletzt 2026-04-09, kein Log seitdem |
| Lens | efficiency-auditor | GPT-5.4 | ⚠️ stabilisiert | LiveSessionModelSwitchError behoben durch Modellwechsel |
| Forge-Opus | forge-opus | Claude Opus 4.6 | ⚠️ konfiguriert | nach Einrichtung 2026-04-07 nicht nachweislich genutzt |
| Flash | flash | MiniMax M2.7-HS | ❌ nicht aktiv | kein Config-Eintrag, nur Konzept |
| Pulse | model-monitor | — | ❌ offline | Entfernung angeordnet 2026-04-07, Status unklar |
| Hermes | — | — | 🗄️ archiviert | 2026-04-10 in 06-Archive verschoben |

**Zombies (aufzuräumen):** ideen, projekte, orchestrator-free, prompt-optimizer, quick, local-runner

---

## Strukturprobleme (bei Audit gefunden)

| # | Problem | Schwere | Status |
|---|---------|---------|--------|
| S1 | Merge-Konflikte in 6 Core-Vault-Files | Kritisch | ✅ behoben |
| S2 | Keine Delegationsregeln formal verankert | Hoch | ✅ behoben |
| S3 | Pixel, Forge-Opus, Flash ohne working-context.md | Hoch | ✅ behoben |
| S4 | Forge-Opus OAuth-Dokumentation falsch (ist API Key) | Mittel | ✅ behoben |
| S5 | Security-Blocked Root-Cause (seit 2026-04-11) | Kritisch | ❌ offen → Forge |
| S6 | Pulse-Entfernung nicht final bestätigt | Hoch | ❌ offen → Forge |
| S7 | Zombie-Agenten in Registry | Mittel | ❌ offen → Forge |
| S8 | sre-expert-fresh undokumentiert | Mittel | ❌ offen → Atlas entscheidet |
| S9 | Heartbeat-Controller existiert nur in Docs, nicht im Code | Hoch | ❌ offen → Atlas entscheidet |
| S10 | Cron-Channels (Lens + cost-report) senden an telegram statt discord | Mittel | ❌ offen → Forge |

---

## Modell-Optimierung

**Vorher:** Atlas auf MiniMax (zu günstig für strategische Arbeit), Lens instabil, Pixel/James ohne explizites Modell

**Nachher:**
- OpenAI Pro €200 (flat): Atlas + Forge + Lens — maximale Auslastung des Flat-Rate-Abos
- MiniMax €40 (token): James + Pixel + Flash — volume-effizient, nicht strategisch-kritisch
- Anthropic API Key: Forge-Opus (Premium-Eskalation, pay-per-use gerechtfertigt)

**Noch nicht live:** Änderungen müssen in `openclaw.json` gesetzt werden (Task für Forge)

---

## Delegationsregel (neu, dauerhaft)

In alle working-contexts eingebaut. Kurzform:

> Atlas dispatcht und entscheidet — handelt nie selbst technisch.
> Jeder Agent löst nur seinen Scope.

Verstöße gegen diese Regel sind die Hauptursache für Kontextverschwendung und Qualitätsverlust.

---

## Empfehlungen für nächsten Stabilitätsfokus

1. Security-Blocked fix (Forge, Priorität 1)
2. Modell-Zuweisungen live setzen (Forge, Priorität 1)
3. Lens Live-Smoketest (nach Modellwechsel)
4. Flash-Aktivierungsentscheidung (Atlas)
5. Heartbeat-Controller-Entscheidung (Atlas → Forge oder Doku-Fix)
