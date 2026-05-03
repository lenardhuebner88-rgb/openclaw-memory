# OpenClaw Discord — Geparkte Low-Priority Punkte (2026-05-04)

Quelle: `openclaw-discord-command-replacement-matrix-2026-05-04.md`

## Geparkt (Low Priority)

### LP-4 — `/sprint-plan` Legacy-Button-Flow Parity
- Status: `FAIL (Parity)`
- Befund: Alter Commander-UI-Flow (`Dispatch/Revise/Cancel`) ist nach Bot-Deaktivierung nicht gleichwertig belegt.
- Risiko heute: niedrig bis mittel (kein Core-Outage, eher UX-/Operator-Komfort-Lücke).
- Park-Entscheidung: vorerst bewusst geparkt.
- Revisit-Trigger:
  - Wenn Sprint-Freigaben wieder häufiger per Discord-UI statt Board/API laufen sollen.
  - Wenn Operator den Button-Flow explizit zurückfordert.

### LP-5 — `/meeting-*` UX-Parität
- Status: `PARTIAL`
- Befund: Backend-Helfer vorhanden (`meeting-runner`, `meeting-status-post`, `meeting-turn-next`), aber Discord-E2E-Parität nicht nachgewiesen.
- Risiko heute: niedrig (Funktionalität scriptseitig vorhanden, aber UX nicht auf alter Komfortstufe belegt).
- Park-Entscheidung: vorerst bewusst geparkt.
- Revisit-Trigger:
  - Wenn Meetings wieder als Standard-Discord-Flow betrieben werden sollen.
  - Wenn erste operative Friktion im Meeting-Ablauf auftritt.

## Hinweis
Core-Stabilität und Kernrouting sind nicht betroffen; diese Parkpunkte sind bewusst nachrangig gegenüber Runtime-/Dispatch-/Reporting-Integrität.
