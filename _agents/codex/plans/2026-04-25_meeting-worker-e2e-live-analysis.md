# Meeting-/Worker-E2E Live-Analyse 2026-04-25

Fenster: 2026-04-25T11:00Z bis 2026-04-25T13:00Z, nur Live-Daten aus API, Meeting-Dateien und Logs.

## Kurzfazit
Das Meeting-Konzept ist im Kern tragfaehig: Ein Discord-getriggertes Debate-Meeting lief E2E bis `done`, mit Claude-Bot, Lens/MiniMax, Codex, CoVe, Token-Tracking und Finalize. Das Worker-System ist aktuell gruen (`worker-proof ok`, `openRuns=0`, `criticalIssues=0`). Fuer echte Automation sind aber drei Brueche noch hochhebelig: Discord-Slash-Interaction-Timeouts, Plan-Runner-Version-Gate nach Update auf 2026.4.22, und zu schwache automatische Klassifikation von transienten Worker-Claim-/Stall-Signalen.

## Live-Belege
- `/api/health`: `status=ok`.
- `/api/ops/worker-reconciler-proof?limit=50`: `status=ok`, `openRuns=0`, `issues=0`, `criticalIssues=0`, keine Proposed Actions.
- `meeting-runner.sh --dry-run`: keine running Meetings, keine queued Meetings.
- Meeting im 2h-Fenster: `2026-04-25_1150_debate_bereits-f-r-phase-c-meeting-phase-erstellung-plan-und-um.md`.
- Meeting-Status: `done`, `tracked-tokens=3200/30000`, Signaturen `claude-bot=ok,lens=ok,codex=ok,codex-interim=ok`.
- Claude-Bot Task `c2182de9`: `done/result/done`, completed `2026-04-25T12:09:53Z`.
- Lens Task `ec87e987`: `done/result/done`, completed `2026-04-25T12:07:39Z`.
- Finalize Note: `meeting-finalize.sh --execute after dry-run gates passed`, `tracked-tokens=3200`.
- Vorheriger Atlas-Stale-Run `bdb6246d` ist inzwischen terminal `failed`; alter Open-Run blockiert nicht mehr.

## E2E-Bewertung
### Was funktioniert
1. Discord kann Meeting-Dateien erzeugen.
2. `meeting-runner.sh --once` startet genau einen Lauf und spawnt Claude-Bot + Lens.
3. Worker claimen beide Meeting-Teilnehmer mit akzeptabler Latenz:
   - `c2182de9` Claim nach ca. 100s.
   - `ec87e987` Claim nach ca. 99s.
4. Contributions landen korrekt im Meeting-File.
5. Codex-Phase-C-Beitrag kann CoVe und Token-Log ergaenzen.
6. Finalize setzt terminal `done`.
7. Nach Abschluss ist Worker-Proof wieder sauber.

### Was noch nicht autonom genug ist
1. **Discord Interaction Timeout:**
   - `openclaw-discord-bot.log` zeigt `Unknown interaction` fuer `/meeting-run-once` und `/meeting-status`.
   - Relevante Stellen: `openclaw-discord-bot.py:697` (`await interaction.response.defer()` in `cmd_meeting_status`) und Meeting-Runner-Command-Pfad.
   - Impact: Aus Operator-Sicht wirkt ein Command kaputt, obwohl Backend/Runner spaeter korrekt weiterarbeiten koennen.
2. **Plan-Runner blockiert nach Update:**
   - `plan-runner.jsonl` schreibt laufend `version-gated`.
   - Live-Version: `OpenClaw 2026.4.22 (00bd2cf)`.
   - Allowlist: nur `2026.4.21 (f788c88)`.
   - Impact: Autonome Folgetasks/Selbstheilung sind nicht verlaesslich, solange der Runner bewusst gated.
3. **Worker-Signale sind operativ noch zu verrauscht:**
   - `alert-dispatcher.log` zeigt im Fenster `worker-dispatch-claim-mismatch` und `worker-stall`; mehrere davon wurden spaeter sauber terminal.
   - Beispiel: `f5fe029e` claimte erst nach 340s, endete aber `done`.
   - Impact: Ohne Policy-Matrix wird aus normaler Latenz/Recovered-State schnell ein falscher Rot-Alarm.
4. **Alert-Routing ist inkonsistent:**
   - `alert-dispatcher.log`: `No webhook configured` fuer Worker-Mismatch/Stall-Warnungen.
   - Gleichzeitig funktionieren MC-API-Discord-Posts.
   - Impact: Operator sieht kritische Automationssignale nicht im richtigen Kanal.
5. **Meeting-Produktisierung ist fachlich, aber noch nicht automatisch:**
   - Aktueller Stand sagt selbst: `kontrolliert vorbereitbar`, nicht produktiv freigegeben.
   - No-loop/No-fanout ist gut, aber Phase-D braucht klare Go/No-Go-Gates.

## Hebel nach Wirkung
1. **Slash-Command Robustness zuerst fixen.**
   - Ziel: `/meeting-status` und `/meeting-run-once` muessen sofort ack/defer oder fallbacken, auch wenn Helper langsam sind.
   - Gate: 5x hintereinander `/meeting-status` und `/meeting-run-once` ohne `Unknown interaction`.
2. **Plan-Runner Allowlist/Version-Gate bewusst aktualisieren.**
   - Ziel: 2026.4.22 freigeben oder Runner bewusst in Dry-run lassen, aber nicht still version-gated laufen lassen.
   - Gate: `plan-runner.jsonl` zeigt keine neuen `version-gated` Events und erzeugt/haelt Folgeaufgaben nach Policy.
3. **Worker Policy-Matrix in Code/Status sichtbar machen.**
   - Ziel: `fresh pickup latency`, `transient recovered`, `stalled-warning`, `hard-fail` sauber trennen.
   - Gate: Recovered Tasks wie `f5fe029e` erscheinen nicht mehr als gleichwertiger harter Blocker.
4. **Alert-Routing vereinheitlichen.**
   - Ziel: Worker-Mismatch/Stall, Meeting-Finalize-Blocker und Plan-Runner-Gate gehen in denselben Operator-Kanal.
   - Gate: Test-Alert landet im Discord-Statuskanal; keine `No webhook configured` fuer diese Klassen.
5. **Meeting Phase-D nur als kontrollierter Autopilot.**
   - Ziel: Discord-only Bedienung bleibt; Automatik darf nur nach sauberem Preflight genau ein Meeting starten, Status posten, Beitragsluecken melden, Finalize-Dry-run ausfuehren. Execute bleibt explizit.
   - Gate: 3 Meetings hintereinander: queued -> running -> contributions -> dry-run finalize -> done, ohne offene Runs und ohne Unknown-Interaction-Fehler.

## Empfohlene Sprint-Reihenfolge
1. P1: Discord Slash Interaction Guard.
2. P1: Plan-Runner 2026.4.22 Gate-Entscheidung.
3. P1/P2: Worker-Recovered-State Policy-Matrix.
4. P2: Alert-Routing in Discord vereinheitlichen.
5. P2: Phase-D Controlled Autopilot fuer Meetings.
