# OpenClaw Discord Bot Shutdown — Impact, Priorities, Next Actions (2026-05-04)

## Executive Summary
Die Abschaltung von `openclaw-discord-bot.service` war technisch sinnvoll (Kollision mit Gateway-Slash-Commands), aber sie hat eine funktionale Lücke hinterlassen: ein Teil der früheren Commander-Funktionen ist nicht als gleichwertiger, verifizierter Ersatz dokumentiert.

## Was der Bot vorher für eine Rolle gespielt hat
Quelle: `/home/piet/.openclaw/scripts/openclaw-discord-bot.py`, Plan-Doku 2026-05-03.

Primärrollen des Legacy-Bots:
- Discord-Commander-Bridge zwischen Operator und Mission Control/OpenClaw APIs.
- Read-Only Ops-Commands: `/health`, `/status`, `/agents`, `/receipts`, `/logs`, `/help`.
- Meeting-Orchestrierung: `/meeting-*` Commands inkl. `meeting-run-once`, `meeting-status`, `meeting-turn-next`.
- Sprint-Preview/Approval UI: `/sprint-plan` mit Button-Flow (`Dispatch/Revise/Cancel`).
- Session Utility: `/new`.

Nicht-Rolle:
- Der Bot war nicht die einzige Runtime für MC/Gateway. MC/Gateway laufen unabhängig.

## Live-Befund nach Abschaltung
Prüfzeit: 2026-05-04 00:02 CEST.

- `openclaw-discord-bot.service`: `inactive (dead)`, `disabled`.
- `mission-control.service`: `active (running)`.
- `openclaw-gateway.service`: `active (running)`.
- `POST /api/discord/send` via Mission Control funktioniert weiterhin (`ok: true`, Message-ID geliefert).

## Bereits sichtbare Auswirkungen
1. Entferntes Collision-Risiko:
- Vorher: `CommandNotFound`, off-channel command warnings im Legacy-Bot-Log.
- Nachher: zweiter CommandTree-Consumer ist weg.

2. Wegfall Legacy-Commander-Funktionsoberfläche:
- Die alten `openclaw-discord-bot.py` Slash-Commands stehen nicht mehr durch diesen Service zur Verfügung.

3. Kommunikations-/Betriebskontinuität bleibt grundsätzlich erhalten:
- Direkter Discord-Post über MC API funktioniert.
- MC/Gateway-Core bleibt online.

## Noch nicht identifizierte bzw. nicht abgesicherte Probleme
1. Funktions-Mapping-Lücke:
- Kein abschließendes, evidenzbasiertes Mapping „Legacy Command -> neuer Gateway/MC Pfad -> getestet (PASS/FAIL)“.

2. Meeting-Flow-Risiko:
- `/meeting-*` war stark an Legacy-Bot gekoppelt. Ersatzpfad ist konzeptionell genannt, aber nicht als produktiver Runbook+Smoke vollständig abgeschlossen.

3. Sprint-Approval-UI-Risiko:
- Legacy-`/sprint-plan` Button-Flow entfällt; unklar, ob operatorfreundlicher Ersatz in gleicher UX/Taktung bereits aktiv genutzt wird.

4. Governance-Lücke:
- Kein finales RCA-Dokument mit klaren GO/NO-GO Kriterien, Ownern und akzeptierten Degradierungen in einem zentralen Abschluss-Record.

## Höchste Priorität — Was als nächstes getan werden muss
## P0 (sofort, heute)
1. Feature-Impact-Matrix finalisieren und live testen.
- Tabelle pro Legacy-Funktion:
  - Legacy-Funktion
  - Neuer Pfad (Gateway/MC/API/Script)
  - Live-Testkommando
  - Ergebnis PASS/FAIL
  - Owner
- Ohne diese Matrix bleibt Blindflug bei Operator-Flows.

2. Kritische Operator-Flows E2E verifizieren (mit Beweis).
- Pflichtflüsse:
  - Task-Status/Board-Read in Discord
  - Dispatch/Approval Standardpfad
  - Receipt/Result-Reporting in Zielkanäle
  - Meeting-Start + Status + Turn-Advance (oder explizit als „derzeit deaktiviert“ markieren)

3. Betriebsentscheidung dokumentieren (harte Klarheit).
- Entweder:
  - A) Legacy-Bot bleibt dauerhaft off (bevorzugt), dann Ersatzpfade als offiziell kanonisch abnehmen.
  - B) Teilfunktion als neuer namespaced Gateway-/Plugin-Pfad zurückbringen (ohne zweite Discord-App-CommandTree-Kollision).

## P1 (kurzfristig, 24-48h)
1. Runbook „Operator ohne Legacy Commander“ schreiben.
- 1-Page: Welche Kommandos jetzt wo laufen, inkl. Fallback API-Aufrufe.

2. Monitoring ergänzen.
- Alarm, wenn kritische Discord-Bridge-Funktion (z. B. `/api/discord/send`) fehlschlägt.
- Alarm, wenn Task-Lifecycle-Reports in Zielkanal ausbleiben.

3. Decision-Record abschließen.
- Dokumentieren, welche alten Features bewusst retired sind und welche ersetzt wurden.

## Empfohlene Zielarchitektur (ohne Rollback in alte Kollision)
- `openclaw-discord-bot.service` bleibt deaktiviert.
- Nur Gateway besitzt die aktive Slash-Command-Oberfläche für das gemeinsame Discord-App-Objekt.
- Spezielle frühere Commander-Funktionen werden als:
  - Gateway-native Kommandos, oder
  - klar namespaced Plugin-Funktionen
  zurückgeführt, jeweils mit E2E-Test und Ownership.

## Konkrete nächste Umsetzungsschritte (ausführbar)
1. Build der Impact-Matrix (P0.1) in einer neuen Datei `.../openclaw-discord-command-replacement-matrix-2026-05-04.md`.
2. Durchführung von 6-8 Live-Smokes (P0.2), Ergebnis in Matrix eintragen.
3. GO/NO-GO Entscheidung für „dauerhaft off“ dokumentieren (P0.3).

## Aktueller Risikostatus
- Runtime-Stabilität: besser als zuvor (Collision entfernt).
- Operator-UX/Feature-Vollständigkeit: potenziell unvollständig, bis Matrix + Smokes abgeschlossen sind.
