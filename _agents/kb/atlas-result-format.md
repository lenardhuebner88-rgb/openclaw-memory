# Atlas Result Format

## EXECUTION_STATUS
- done | failed | partial

## RESULT_SUMMARY
- 1–3 Sätze: was getan wurde, was rausgekommen ist.

## GATES
- Was geprüft wurde.
- Ergebnis jedes Gates.

## FOLLOW_UPS
- Liste offener Drafts.
- Jeder Eintrag: Titel, approvalClass, riskLevel.

## OPERATOR_DECISIONS
- Was der Operator entscheiden oder freigeben muss.

## Example
```md
EXECUTION_STATUS: done
RESULT_SUMMARY: Reportingformat dokumentiert und Rule ergänzt.
GATES: File existiert; 5 Felder vorhanden; Regel eingetragen.
FOLLOW_UPS: - [Draft] ... | approvalClass=gated-mutation | riskLevel=medium
OPERATOR_DECISIONS: Stufe 8 erst nach grünem Stufe-7-Gate starten.
```