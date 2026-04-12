# Atlas Session Handover

## Stand: 2026-04-12 — Lens-Analyse + Vault-Bereinigung abgeschlossen

---

## 1. Was heute gemacht wurde

### Vault-Bereinigung (komplett)
- Merge-Konflikte in 6 Core-Vault-Files aufgelöst: Atlas, Forge, James, Lens working-context + project-state + decisions-log
- Strikte Delegationsregeln in alle working-contexts eingebaut (Atlas delegiert immer, handelt nie selbst technisch)
- Fehlende working-context.md erstellt für: Pixel, Forge-Opus, Flash (Platzhalter)
- Forge-Opus: korrekt dokumentiert als Anthropic API Key (nicht OAuth — OAuth gilt nur für Atlas/Sonnet)

### Modell-Zuweisung neu geregelt (noch nicht live in openclaw.json)
| Agent | Modell | Pool |
|-------|--------|------|
| Atlas | `gpt-5.4` | OpenAI Pro (€200 flat) |
| Forge | `GPT-5.3 Codex` | OpenAI Pro (fix, unverändert) |
| Lens | `gpt-5.4` | OpenAI Pro |
| James | `minimax/MiniMax-M2.7-highspeed` | MiniMax (€40 token) |
| Pixel | `minimax/MiniMax-M2.7-highspeed` | MiniMax |
| Flash | `minimax/MiniMax-M2.7-highspeed` | MiniMax (noch nicht aktiv) |
| Forge-Opus | `anthropic/claude-opus-4-6` | Anthropic API Key |

---

## 2. Offene Tasks — priorisiert

### Sofort → an Forge dispatchen:

**[1] Modell-Zuweisungen live setzen**
- `openclaw.json` anpassen gemäß Tabelle oben
- Atlas: MiniMax → `gpt-5.4`
- Lens: instabiler Pfad → `gpt-5.4`
- James + Pixel: explizit auf `minimax/MiniMax-M2.7-highspeed` setzen
- Verifizieren: `/api/agents/live` zeigt korrekte Modelle

**[2] Security-Blocked Root-Cause klären**
- Seit 2026-04-11 blockt ein globales `security-check-failed` alle Task-Terminierungen
- 8+ Tasks betroffen (Atlas, Forge, James, Lens)
- Ein Task (`Dispatch UX → Contract-Fix`, commit 150cbad) ist fachlich fertig — wartet nur auf Terminalisierung
- Forge-Brief liegt bereit: [[../../04-Operations/Audits/security-check-diagnose-2026-04-12]]
- Forge soll Root-Cause identifizieren und Fix-Pfad beschreiben, du entscheidest dann

**[3] Pulse-Entfernung final bestätigen**
- Angeordnet seit 2026-04-07, Status unklar
- `model-monitor` aus `TEAM_AGENT_ORDER` / `route.ts` prüfen
- Cron deaktivieren (nicht löschen), dann als DONE schließen

### Danach → an Forge:

**[4] Zombie-Agenten aus openclaw.json entfernen**
- ideen, projekte, orchestrator-free, prompt-optimizer, quick
- kein Cron, kein Channel, kein Mandat — einfach raus

**[5] Cron-Channels korrigieren**
- `efficiency-auditor-heartbeat`: sendet an `telegram` → auf `discord` ändern
- `daily-cost-report`: sendet an `telegram` → auf `discord` ändern

**[6] sre-expert-fresh klären**
- Taucht in exec-security-allowlist auf, hat keine Vault-Dokumentation und keine Rolle
- Entweder sauber einführen oder aus Config entfernen

### Deine Entscheidung erforderlich:

**[7] Flash aktivieren?**
- Platzhalter-Context liegt in `03-Agents/Flash/working-context.md`
- Aktivierungs-Checkliste steht dort
- Entscheide: jetzt oder später?

**[8] Heartbeat-Controller: implementieren oder Doku anpassen?**
- HEARTBEAT.md beschreibt einen Loop der im Code nicht existiert
- Option A: echten Controller implementieren (Aufwand groß, Forge-Opus-Kandidat)
- Option B: HEARTBEAT.md an Realität anpassen (schnell, kein Mehrwert) — Korrekturvorlage liegt bereit: [[../../04-Operations/Audits/heartbeat-realitaet-2026-04-12]]
- Entscheide Richtung, dann Forge dispatchen

**[9] Lens Smoketest**
- Lens gilt als instabil (LiveSessionModelSwitchError) bis eigener Smoketest grün
- Mit neuem Modell `gpt-5.4` sollte Instabilität behoben sein
- Beauftrage einen minimalen Live-Smoketest um Lens als stabil zu bestätigen

---

## 3. Systemregel (neu, ab heute aktiv)

**Atlas delegiert immer — handelt nie selbst technisch.**

| Aufgabe | Agent |
|---------|-------|
| Code, Infra, Build, Deploy | Forge |
| Root-Cause, Architektur-Risiko | Forge-Opus |
| Recherche, externe Vergleiche | James |
| UI, Frontend, Dashboard | Pixel |
| Kosten, Audit, Konsolidierung | Lens |
| Leichte Forge-Entlastung | Flash (sobald aktiv) |

Details stehen in jedem `working-context.md`.

---

## 4. Operative Leitplanken (unverändert gültig)

- `groupPolicy = allowlist` für Discord + Telegram — nicht zurückdrehen
- `exec.security = allowlist` für main, sre-expert, sre-expert-fresh — nicht zurückdrehen
- Mission Control bleibt auf `next start` (production, nicht dev)
- Forge nicht blind als Wahrheitsquelle für Gesamtzustand verwenden
- Keine parallelen Großbaustellen — ein Block nach dem anderen

---

## 5. Erste Aktion nach Sessionstart

1. `project-state.md` + `decisions-log.md` kurz bestätigen (sind aktuell)
2. Scope-Entscheidung Heartbeat-Controller treffen (minimal vs. voll) — 5 Min
3. Sprint starten: [[../../04-Operations/Validations/sprint-autonomie-basis]]
4. P1-A + P1-B gleichzeitig an Forge dispatchen
5. Modell-Zuweisung parallel an Forge (unabhängig vom Sprint)
