---
title: Atlas Session & Memory Operating Model
version: 1.0
status: pilot-ready
owner: Principal Systems Architect
created: 2026-04-17
---

# Atlas Session & Memory Operating Model

Betriebsmodell für Session-Führung und Memory-Hygiene in OpenClaw/Mission-Control.
Ziel: Stabilität, Reproduzierbarkeit, Operator-Kontrolle.

## EXECUTIVE JUDGMENT

Das System leidet nicht an zu wenig, sondern an **schlecht typisiertem** Memory und **scope-losen** Sessions. Drei Symptome: (1) Long-Sessions driften in Tangenten, cache verfällt, Kontext schwillt → "Something went wrong". (2) MEMORY.md sammelt Incident-Tagebücher und Architektur-Invariants in derselben Datei — Bootstrap truncated willkürlich (Beleg: MEMORY.md rawChars 22798 → injected 18110 im E2E-Run 2026-04-17). (3) Übergaben sind implizit — Nachfolge-Agent bekommt alles oder nichts. Fix ist nicht mehr Memory, sondern **Schichten-Trennung + Session-Typisierung + Verfallsregeln**.

## ROOT CAUSE

1. **Session-Typ nicht deklariert** → kein Scope-Kontrakt → Agent entscheidet ad-hoc welche Tools, welche Tiefe.
2. **Working Memory und Long-Term Memory im selben File** → Per-File-Limit greift, neue Einträge verdrängen stabile Architektur-Invariants.
3. **Keine Verfallsregel** → 6 Monate alte Task-Lifecycle-Snapshots blockieren Bootstrap-Budget, obwohl die tatsächliche Lifecycle längst migriert ist.
4. **Keine Übergabe-Disziplin** → "Atlas weiß schon" wird zur Fiktion; neue Session startet ohne kondensiertem State.
5. **Keine harten Reset-Trigger** → Agent arbeitet durch bis zum Crash statt bei Degradation abzugeben.

## TARGET SESSION MODEL

Vier Session-Typen, jeweils mit eigenem Kontrakt. Jede Session deklariert ihren Typ im ersten User-Prompt oder System-Tag.

### 1. Incident Session (Sev1/Sev2)
Ziel: MTTR minimieren. MC down, Gateway-Loop, OOM, Data-Loss-Risiko.
- **Max-Tiefe:** 30 Tool-Calls oder 20min — danach Handoff erzwungen.
- **Read-Write-Ratio:** 3:1 (zuerst verstehen).
- **Verbotene Tangenten:** Refactor, Doku, Style-Fixes, Follow-ups. NUR Containment + Root-Cause + Minimal-Fix.
- **Memory-Schreiben:** Nur Incident-Summary nach Containment, nicht während.
- **Bootstrap:** minimal (nur INVARIANTS.md + letzte 3 Incident-Memos).

### 2. Analyse Session (Audit, E2E-Test, Root-Cause-Dig)
Ziel: Findings-Liste + Priorisierung. Kein Fix in derselben Session.
- **Max-Tiefe:** 80 Tool-Calls oder 60min.
- **Pflicht:** TodoWrite vom ersten Moment, jedes Finding als abgeschlossene Todo.
- **Output:** Ein Report-Artefakt (in vault oder /memory/), nicht freier Text in der Session.
- **Memory-Schreiben:** Findings-Index nach Session, nicht pro Finding.

### 3. Umsetzungs Session (gezielter Fix, eine Finding-Nummer)
Ziel: ein Finding, ein Commit-fähiger Change. Kein Scope-Creep.
- **Max-Tiefe:** 40 Tool-Calls oder 30min.
- **Pflicht:** Scope-Statement upfront: "Finding F-X, betrifft Dateien Y, Acceptance Z."
- **Jede Tangente:** `mcp__ccd_session__spawn_task` statt Mitnehmen.
- **Memory-Schreiben:** Nur wenn Invariant geändert (selten).

### 4. E2E / Orchestrator Session (Live-Monitoring, Multi-Agent-Orchestrierung)
Ziel: Ablauf live beobachten, Timeline dokumentieren.
- **Max-Tiefe:** 120 Tool-Calls, aber **Monitor-dominiert** statt Bash-polling.
- **Pflicht:** Background-Tasks für langlaufende Jobs, Monitor mit präziser grep-Alternation, kein Sleep-Polling.
- **Memory-Schreiben:** Run-Protokoll als eigenes File (z.B. `e2e_<thema>_<datum>.md`).

## TARGET MEMORY MODEL

Drei Schichten, physisch getrennte Pfade, unterschiedliche Retention.

### Layer 1 — Long-Term Memory (LTM): `/home/piet/.openclaw/workspace/memory/invariants/*.md`
Inhalt: Architektur-Invarianten, Pfad-Konventionen, Port-Mappings, API-Schemas, "kanonischer X = Y". Alles was über 3 Monate stabil bleibt.
- Wird in Atlas-Bootstrap **immer** geladen (hohes Prio-Budget).
- Schreibregeln: siehe MEMORY HYGIENE RULES.
- Pro Datei max 3 KB. Pro Verzeichnis max 30 KB gesamt.

### Layer 2 — Working Memory (WM): `/home/piet/.openclaw/workspace/memory/working/*.md` + `/vault/01-Daily/YYYY-MM-DD.md`
Inhalt: laufende Vorhaben, Sprint-Status, offene Findings mit Owner, Hypothesen im Test. Alles mit Lebenszeit < 2 Wochen.
- Wird bedingt geladen (bei Session-Start prüft Bootstrap: WM-Files mit `updatedAt > 14d ago` werden ignoriert).
- Nach Abschluss eines Vorhabens: entweder **promoted** zu LTM (wenn Invariant) oder **archived** zu `/memory/archive/YYYY-QN/`.

### Layer 3 — Incident Context (IC): Session-lokal, **nicht persistiert**
Inhalt: Tool-Outputs, Zwischenstände, Debug-Versuche. Stirbt mit der Session.
- Geht NIE in LTM oder WM. Wenn etwas überlebenswert ist → explizite Memory-Write-Entscheidung mit Begründung.
- Session-Ende: wenn nichts geschrieben wurde, ist das OK. Schweigen ist ein valides Ergebnis.

## OPERATING RULES

- **Scope-Deklaration Pflicht:** Jede Session startet mit Session-Typ + einer Zeile Scope. Ohne → Atlas fragt einmal, dann bricht ab.
- **Cache-Fenster respektieren:** Sleeps/Gaps <270s oder ≥1200s, nie dazwischen. Bei Long-Running: Background + Notifications, nicht Polling.
- **Tiefen-Limit = harte Grenze:** Bei Erreichen automatische Handoff-Vorbereitung, kein Weitermachen.
- **Spawn-Regeln für Worker-Sessions:**
  - Nur wenn Scope klar trennbar (ein Agent, eine Task-ID, eine DoD).
  - Worker-Prompt enthält: Task-ID, Ziel, DoD, Return-Format, Verify-Pflicht (§ AGENTS.md).
  - Worker darf KEIN LTM schreiben. Worker-Findings landen im Task-resultSummary, Orchestrator entscheidet Promotion.
- **Reset-Trigger (hart):**
  - 3 consecutive tool failures gleicher Art → Reset.
  - 2 inhaltliche Widersprüche zwischen Memory und Live-State → Reset + Memory-Review.
  - Kontext > 70% geschätzt → Handoff, nicht Compaction.
- **Reset-Typ wählen:**
  - **Weich** (Handoff in gleiche Session-Typ): Default bei Tiefen-Limit.
  - **Hart** (neue Session, neuer Bootstrap): bei Memory/State-Widerspruch, nach Incident-Containment, bei Typ-Wechsel (z.B. Analyse → Umsetzung).

## HANDOFF MODEL

Kein Handoff ohne **Handoff-Artefakt**. Das Artefakt ist ein Markdown-Block mit Pflicht-Feldern:

```
## Handoff: <session-type> → <next-session-type>
- Scope: <1 Zeile>
- Done: <Liste abgeschlossener Todos>
- Open: <Liste offener Todos mit Owner>
- State-Snapshot: <kritische Live-Zustände, z.B. Task-IDs, Service-Status>
- Entschieden: <getroffene Entscheidungen mit Kurz-Why>
- Offen-Entschieden: <Entscheidungen die die Nachfolge braucht>
- Anti-Scope: <was die Nachfolge NICHT tun soll>
- Bootstrap-Hint: <welche LTM/WM-Files sind relevant>
```

Der Artefakt-Text IST der erste User-Prompt der Folge-Session. Kein Freitext, keine Erinnerungs-Aufforderung, keine "wie besprochen".

## MEMORY HYGIENE RULES

### Do (hin)
- Architektur-Invariants mit "Why" und "How to apply" (Format siehe auto-memory-Spec).
- Kanonische Pfad/Port/ID-Zuordnungen.
- Feedback-Muster ("wenn X, dann Y") — reduziert Wiederholungs-Korrekturen.
- Externe-System-Pointer (Grafana-Dashboard-URL, Linear-Projekt).

### Don't (raus)
- Tages-Incidents mit Timestamps, die git log auch zeigt.
- Ergebnis-Logs abgeschlossener Runs (gehören in Run-Protokolle, nicht LTM).
- PR-Nummern, Commit-Hashes, CI-Lauf-IDs.
- Agent-interne Tool-Outputs, auch wenn "spannend".
- Copy-Paste aus Docs/AGENTS.md (redundant, verdrängt).

### Altlasten fernhalten
- **Quarterly Review** (1h/Quartal): jedes LTM-File geprüft auf "gilt das noch im Code?". Grep-Check auf Symbole, URLs, Pfade.
- **Write-Gate:** Vor jedem Memory-Write fragt Atlas sich: "Würde ich das in 6 Monaten noch brauchen?" Nein → WM oder Protokoll-File, nicht LTM.
- **Conflict-Alarm:** Wenn Live-State LTM widerspricht → LTM-Eintrag bekommt `STALE 2026-XX-XX` Tag, Session reset, User informiert.

## PILOT ROLLOUT PLAN

### Woche 0 (Baseline, 2 Tage)
- Metrik-Sammeln: Anzahl Sessions/Tag, "Something went wrong"-Events, Session-Resets, durchschnittliche Tool-Call-Zahl bis Degradation.
- Messinfrastruktur: Log-Parsing aus `~/.openclaw/workspace/logs/` + session-store.
- Kein Regel-Rollout.

### Woche 1 (nur Atlas, 5 Tage)
- Atlas bekommt das Betriebsmodell als verbindliche System-Prompt-Erweiterung.
- Session-Typ-Tag im ersten User-Prompt enforced.
- Handoff-Artefakt-Format Pflicht.
- Memory-Layer-Trennung: `invariants/`, `working/`, `archive/` angelegt, bestehende Einträge manuell einsortiert.

### Woche 2 (Rollout auf Worker, 5 Tage)
- Worker-Agents (Forge, Pixel, Lens) bekommen Worker-Prompt-Template mit "kein LTM-Write".
- Worker-Findings landen nur in Task-resultSummary.
- Orchestrator-Kontrolle: Atlas entscheidet Promotion WM → LTM.

### Review-Gate (Ende Woche 2)
- Acceptance Criteria gegen Baseline vergleichen.
- Entscheidung: produktiv / iterate / abbrechen.

## RECOMMENDED EXECUTION AGENT

- **Atlas (main)** — Owner des Modells, Rollout-Driver, Promotion-Entscheider.
- **Lens (efficiency-auditor)** — misst Baseline + Review-Gate, pflegt Quarterly-Review-Script.
- **Forge (sre-expert)** — baut Memory-Layer-Struktur (Verzeichnisse + Bootstrap-Config-Update), passt Session-Store-Cleanup-Cron an neue Pfade an.
- **Pixel (frontend-guru)** — entkoppelt (kein Mandat hier).

Rollen-Invariante: Nur Atlas darf LTM schreiben. Lens schlägt Promotions vor (Review-Output), Forge führt Infrastruktur-Änderungen aus.

## ACCEPTANCE CRITERIA

Messbar nach Woche 2. Alle Werte relativ zu Baseline Woche 0.

1. **"Something went wrong"-Rate:** −60 % oder absolut ≤ 1/Tag.
2. **Session-Reset-Rate:** −50 %.
3. **Durchschnittliche Tool-Calls bis Degradation:** +40 %.
4. **MEMORY.md Bootstrap-Truncation:** 0 (alle LTM-Files zusammen unter per-file + total limit).
5. **Handoff-Artefakt-Rate:** ≥ 95 % aller Session-Wechsel haben strukturiertes Handoff.
6. **Stale-Memory-Befunde im Quarterly Review:** ≤ 3 pro Durchlauf.
7. **Incident-MTTR:** unverändert oder besser (nicht schlechter — Regeln dürfen Incident nicht verlangsamen).
8. **Worker-LTM-Writes:** 0 (Invariante).
9. **Scope-Creep-Events (Umsetzungs-Session):** ≤ 10 % aller Umsetzungs-Sessions enthalten Tangenten-Arbeit.
10. **User-Meldung "Agent hat es vergessen":** −70 %.

Pass-Kriterium: 7 von 10 erfüllt, keine Regression in MTTR oder User-Meldungs-Rate.

---

## Referenzen

- `/home/piet/.openclaw/workspace/AGENTS.md` — Agent-Rollen, Verify-After-Write (Phase 2 Hardening 2026-04-17)
- `/home/piet/.openclaw/workspace/mission-control/AGENTS.md` — Task Lifecycle Invariants + Post-Write Verification
- `/home/piet/.openclaw/workspace/memory/e2e_orchestrator_run_2026-04-17.md` — E2E-Befund der diesen Plan ausgelöst hat
- Auto-Memory-Spec (CLAUDE.md system): Struktur für LTM-Eintragsformat
