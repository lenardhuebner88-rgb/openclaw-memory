# 04-Sprints README

Kurzlogik für Agenten und Operator:

- `planned/` zuerst prüfen, wenn du offene oder dispatch-fähige Sprint-Arbeit suchst.
- `active/` nur für aktuell laufende Sprint-Wellen verwenden.
- `closed/` enthält abgeschlossene Sprint-Pläne als Referenz.
- `reports/` enthält Reports, RCAs, Inventare, Closeouts und Evidenz.
- `superseded/` nur bei Historie, Drift oder Nachfolger-Beziehungen prüfen.

## Empfohlene Retrieval-Reihenfolge
1. `planned/`
2. `active/`
3. `closed/` (nur wenn abgeschlossene Planlogik relevant ist)
4. `reports/` (für Belege, Verlauf, RCA)
5. `superseded/` (nur für Altstände)

## Suchregel
Wenn die Frage lautet "Was ist offen?" oder "Was ist als Nächstes dran?" → **nicht** in `reports/` oder `superseded/` starten.

## Strukturziel
Sprint-Pläne, Abschlussberichte und Altstände bleiben getrennt, damit Agenten keine historische Noise mit operativer Arbeit vermischen.
