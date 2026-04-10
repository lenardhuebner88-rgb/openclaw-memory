# Atlas Session Handover

## 1. Aktiver System-Zustand

### Worker-Status
- **Atlas / main:** stabil. Mission Control Build, Deploy, Cleanup und Hardening wurden erfolgreich durchgeführt.
- **Forge / sre-expert:** grundsätzlich nutzbar, aber heute nicht als primärer Wahrheits-/Stabilitätspfad verwendet. Exec-Security wurde auf `allowlist` reduziert.
- **Pixel / frontend-guru:** zuletzt als grundsätzlich stabil/startbar betrachtet; heute kein neuer eigener Blocker von Pixel.
- **Lens / efficiency-auditor:** weiterhin **nicht vertrauenswürdig stabil**. Frühere Root Cause war `LiveSessionModelSwitchError` / instabiler Modellpfad. Noch offen.
- **Researcher:** logisch eingebunden, aber nicht final live-validiert als belastbarer Produktionspfad.

### Offene Blocker + Root Cause
- **Lens instabil:** Root Cause weiter im Modell-/Session-Switch-Pfad, nicht in Mission Control selbst.
- **Tailscale/Mobilzugriff offen:** `allowedOrigins` wurden vorbereitet, aber `tailscale status` lieferte leer und `http://100.109.144.77:18789` war nicht erreichbar. Root Cause liegt sehr wahrscheinlich außerhalb von Mission Control, eher Host-/Tailscale-Zustand.
- **Small-model / sandbox / web-tools:** Security-Audit warnt weiterhin, weil kleine/free Modelle ohne verpflichtende Sandbox und mit Web-/Browser-Kontext möglich sind. Das ist ein strategischer Hardening-Punkt, kein akuter Mission-Control-Blocker.

### Was heute bereits erledigt wurde
- Mission Control Build-Blocker mit alten `backlog`-/`recurring`-Altlasten, `server-only`-Leak und inkonsistenten Importpfaden wurde systematisch behoben.
- `deploy.sh` wurde stabilisiert: alter Server wird vor Build gekillt, stale Next-Locks werden vor Build entfernt.
- Mission Control ist wieder **buildbar** und **deploybar**.
- Task-Lifecycle wurde live repariert und verifiziert:
  - create -> assigned
  - dispatch/send -> in progress
  - resolve -> done
- Board-Cleanup durchgeführt: offene Test-/Validation-/Smoke-Aufgaben wurden bereinigt, Board ist sichtbar ruhiger.
- Hardening umgesetzt:
  - `channels.discord.groupPolicy = allowlist`
  - `channels.telegram.groupPolicy = allowlist`
  - `tools.exec.security = allowlist` für `main`, `sre-expert`, `sre-expert-fresh`
  - `gateway.controlUi.allowedOrigins` gesetzt für lokal/LAN/Tailscale
- `claude-cli/claude-sonnet-4-6` wurde **einmalig für diese Session testweise verwendet** und als **für Session-Nutzung grundsätzlich brauchbar** bewertet; danach wurde wieder auf `openai-codex/gpt-5.4` zurückgestellt.

## 2. Offene Tasks

Hinweis: Der Board-Cleanup hat die offensichtlichen Test-/Validation-Artefakte entfernt. Die folgenden Themen sind die weiterhin relevanten operativen offenen Punkte.

### 1) Lens / Model-Switch-Instabilität beheben
- **ID:** kein sauber gepflegter aktueller Board-Task als endgültige Live-Wahrheit bestätigt; als offener Systemblock behandeln
- **Titel:** Lens / Model-Switch-Instabilität beheben
- **Nächster konkreter Schritt:** Modell-/Session-Pfad von `efficiency-auditor` read-only prüfen, dann minimalen Live-Smoketest mit dem echten Agenten fahren.
- **Zuständiger Worker:** Lens / ggf. Atlas orchestriert, Forge nur bei technischem Fixpfad

### 2) Researcher-Agent live validieren
- **ID:** derzeit nicht als klarer aktiver Board-Task verifiziert
- **Titel:** Researcher-Agent live validieren
- **Nächster konkreter Schritt:** Einfache echte Recherche-Task an `researcher` dispatchen und prüfen, ob Rücklauf + Routing sauber funktionieren.
- **Zuständiger Worker:** Researcher

### 3) Config vs Live-Provider-Truth bereinigen
- **ID:** derzeit nicht als klarer aktiver Board-Task verifiziert
- **Titel:** Config vs Live-Provider-Truth abgleichen
- **Nächster konkreter Schritt:** aktive Modelle/Fallbacks gegen tatsächlich funktionierende Providerpfade abgleichen; nicht belastbare Modellpfade kennzeichnen oder rausnehmen.
- **Zuständiger Worker:** Atlas / Lens

### 4) Tailscale/Mobilzugriff separat prüfen
- **ID:** derzeit nicht als klarer aktiver Board-Task verifiziert
- **Titel:** Tailscale / Mobilzugriff verifizieren
- **Nächster konkreter Schritt:** Host-Tailscale-Zustand prüfen (`tailscale status` / Host-Dienst), danach UI-Zugriff über `100.109.144.77:18789` erneut testen.
- **Zuständiger Worker:** Forge / Atlas

### 5) Heartbeat-/Prompt-Altlasten bereinigen
- **ID:** derzeit nicht als klarer aktiver Board-Task verifiziert
- **Titel:** Heartbeat-/Prompt-Altlasten bereinigen
- **Nächster konkreter Schritt:** veraltete `backlog`-/Legacy-Semantik in HEARTBEAT.md und angrenzenden Texten gegen aktuelles Statusmodell prüfen.
- **Zuständiger Worker:** Atlas / Pixel

### 6) Memory konsolidieren
- **ID:** derzeit nicht als klarer aktiver Board-Task verifiziert
- **Titel:** Memory konsolidieren
- **Nächster konkreter Schritt:** heutige Entscheidungen und neue stabile Betriebsregeln in eine knappe durable Note überführen.
- **Zuständiger Worker:** Atlas

### 7) Update 2026.4.2 prüfen
- **ID:** derzeit nicht als klarer aktiver Board-Task verifiziert
- **Titel:** OpenClaw Update 2026.4.2 prüfen
- **Nächster konkreter Schritt:** nur Changelog/Risiko prüfen, nicht blind updaten.
- **Zuständiger Worker:** Forge / Atlas

## 3. Wichtige Config-Änderungen heute

### `openclaw.json`
Bewusst gesetzt und **nicht rückgängig machen**:
- `channels.discord.groupPolicy = "allowlist"`
- `channels.telegram.groupPolicy = "allowlist"`
- `agents.list[main].tools.exec.security = "allowlist"`
- `agents.list[sre-expert].tools.exec.security = "allowlist"`
- `agents.list[sre-expert-fresh].tools.exec.security = "allowlist"`
- `gateway.controlUi.allowedOrigins = [
  "http://127.0.0.1:18789",
  "http://localhost:18789",
  "http://192.168.178.61:18789",
  "http://100.109.144.77:18789"
]`

**Warum:** Diese Schritte waren die bewusst freigegebenen Security-Hardening-Maßnahmen nach Stabilisierung. Nicht wieder auf `open` oder `full` zurückdrehen, außer mit expliziter neuer Entscheidung.

### `HEARTBEAT.md`
- Keine bestätigte bewusste Dateiänderung in dieser Session final festgehalten.
- Aber: HEARTBEAT-/Prompt-Altlasten gelten weiterhin als späterer Cleanup-Punkt, weil historisch noch Legacy-Semantik vermutet wird.

### `sessions.json`
- Keine operative, bewusst zu bewahrende Schlüsselfestlegung aus heutiger Stabilisierung ableiten.
- Nicht ohne konkreten Anlass daran drehen.

### Mission Control Code / Deploy
Bewusst gesetzte operative Wahrheit:
- `deploy.sh` killt den alten Server jetzt **vor** dem Build.
- `deploy.sh` räumt stale Next-Locks vor dem Build weg.
- Mission Control Build-/Deploy-Pfad ist jetzt wieder stabil genug für normalen Einsatz.

## 4. Operative Leitplanken

### Dispatch-Regeln aktuell
- Create mit gewähltem Agenten landet sinnvoll in **Assigned**.
- Dispatch/Send muss sauber nach **In Progress** gehen.
- Resolve führt nach **Done**.
- `backlog` ist **kein operativer Persistenz-Status mehr**.
- Board/API/Deploy-Wahrheit liegt im kanonischen `workspace/mission-control`, nicht in alten/stalen Runtimes.

### Was NICHT zu tun ist
- **Nicht** den gerade stabilisierten Mission-Control-Kern wieder groß umbauen.
- **Nicht** `groupPolicy` wieder auf `open` stellen.
- **Nicht** `exec security` für die gehärteten Agenten wieder auf `full` stellen, außer mit ausdrücklicher neuer Entscheidung.
- **Nicht** Tailscale-/Host-Erreichbarkeit mit Mission-Control-Core-Problemen vermischen.
- **Forge nicht blind als Wahrheitsquelle** für den Gesamtzustand verwenden; Mission-Control war heute primär über Atlas/Live-Validierung stabilisiert.
- **Lens nicht als stabil annehmen**, bis eigener Live-Smoketest grün ist.
- **Keine blinden globalen Modellwechsel**; `claude-cli/claude-sonnet-4-6` ist für Einzelsession nutzbar, aber nicht als global verifizierter Default bewiesen.
- **Keine parallelen Großbaustellen**: immer ein Systemblock nach dem anderen.

## 5. Erste Aktion nach dem Neustart

Erste Aktion nach der frischen Session: **den stabilen Stand kurz bestätigen und dann Lens/Model-Switch-Instabilität als nächsten echten offenen Systemblock angehen.**

Die Reihenfolge nach Neustart soll sein:
1. kurz bestätigen, dass Mission Control + Hardening-Zwischenstand noch gilt
2. Lens / `efficiency-auditor` read-only prüfen
3. minimalen Live-Smoketest für Lens planen bzw. fahren
4. erst danach Researcher / Config-Truth / Tailscale separat angehen
