# Research Report: OpenClaw Excel Workflow — Tools & Best Practices

**Datum:** 2026-04-09
**Kontext:** OpenClaw hat Probleme mit Excel-Generierung (npm xlsx-Library hatte Layout-Probleme). openpyxl (Python) wurde bereits erfolgreich eingesetzt. Ziel: beste langfristige Strategie finden.

---

## 1. Tool-Vergleich für Excel-Generierung

### 1.1 Node.js Libraries

| Feature | **xlsx-populate** | **ExcelJS** | **SheetJS (xlsx)** | **xlsx (npm)** |
|---|---|---|---|---|
| **Read/Modify/Write** | ✅ Perfekt | ❌ Probleme | ❌ Datenverlust | ❌ Probleme |
| **Formeln erhalten** | ✅ | ⚠️ Teilweise | ❌ Verloren | ❌ |
| **Datenvalidierungen** | ✅ Preserved | ❌ Dupliziert (Bug) | ❌ Verloren | ❌ |
| **Verbundene Zellen** | ✅ | ⚠️ | ❌ | ❌ |
| **Zeichnungen/Charts** | ✅ | ❌ Verloren | ❌ Verloren | ❌ |
| **Styles/Formatierung** | ✅ | ⚠️ Meist | ❌ Verloren | ❌ |
| **Cross-Sheet Dropdowns** | ✅ | ❌ Kaputt | ❌ Verloren | ❌ |
| **NPM Downloads/Woche** | ~50k | ~500k | ~2M | Teil von SheetJS |
| **Maintenance** | Niedrig | Mittel | Hoch | — |

#### Detaillierte Findings (aus Real-World Test, mfyz.com):

**ExcelJS Bug bei Datenvalidierungen:**
ExcelJS parsed Bereiche wie `C2:C1013` in einzelne Zellen (C2, C3, C4… C1013) und sortiert diese alphabetisch. Dabei wird `C10 < C2`, weil "1" < "2" im Stringvergleich. Resultat: überlappende Ranges, duplizierte Validierungsregeln (7 → 14). Workbook wird corrupted.

**SheetJS (xlsx npm):** Free-Version stripped alle Datenvalidierungen, ~90% der Styles, und Drawings komplett. File-Größe wuchs um 375KB wegen unoptimiertem Output.

**xlsx-populate:** Einzige Node.js-Library, die XML-Struktur original erhält. Read/Modify/Write funktioniert 1:1 — keine Neugenerierung, keine Transformation. Alle validations, cross-sheet refs, drawings, styles bleiben exakt erhalten.

#### Limitation von xlsx-populate:
- Nur ~50k Downloads/Woche — weniger Mainstream
- Letztes Release teilweise älter
- Kein Streaming für Very-Large-Files
- Reines Read/Modify/Write-Tool, kein "from scratch"-Generator

---

### 1.2 Python: openpyxl

| Feature | **openpyxl** |
|---|---|
| **Template-Befüllung** | ✅ Exzellent |
| **Formeln setzen/erhalten** | ✅ (=SUM(), =IF(), =HOUR() etc.) |
| **Datumsformate (DE)** | ✅ TT.MM., TT.MM.JJJJ |
| **Zeitformate** | ✅ h:mm, hh:mm |
| **Zellformate kopieren** | ✅ Style-Kopie zwischen Zellen |
| **Merged Cells** | ✅ intact |
| **Farben/Fonts** | ✅ |
| **Spaltenbreiten** | ✅ aus Template übernehmen |
| **Bedingte Formatierung** | ✅ |
| **Charts/Bilder** | ✅ |
| **Cross-Sheet Validations** | ✅ |
| **Maintenance** | Aktiv (PyPI) |
| **Python Availability** | Fast überall vorinstalliert |

**bekannte Caveats bei openpyxl:**
- `load_workbook()` mit `data_only=False` behält Formeln bei
- Datumswerte müssen als Python `datetime`-Objekte oder Excel-Seriennummern übergeben werden
- Bei gecachten Formelwerten: nach dem Öffnen `data_only=True` verwenden, um berechnete Werte zu lesen

---

## 2. Workflow-Optionen Bewertung

### Option A: Template-basiert mit Python/openpyxl ✅ **EMPFOHLEN**

```
User → OpenClaw → python3 excel-fill.py \
  --template zeiterfassung.xlsx \
  --data '{"rows": [{"date": "09.04.2026", ...}]}' \
  --output result.xlsx
```

**Vorteile:**
- Perfekte Formatierung, Formeln, Styles — kein Quality-Verlust
- Gut verständliche CLI mit argparse
- Template kann alles enthalten: verbundene Zellen, Farben, Druckbereich, Formeln
-openpyxl ist state-of-the-art für Excel-Automatisierung
- Einfach zu debuggen (Python direkt ausführbar)

**Nachteile:**
- Python muss auf dem System verfügbar sein
- Für HEAVY concurrency (1000 simultane Requests): Python GIL, aber bei OpenClaw normalerweise kein Problem

### Option B: Node.js nativ ❌ **NICHT EMPFOHLEN**

- xlsx/npm: Formel-/Style-Probleme (OpenClaw hat es bereits erlebt)
- ExcelJS: Datenvalidierungs-Bug, verliert Drawings
- xlsx-populate: gut für Read/Modify/Write, aber weniger maintained, kein "from scratch"
- Fazit: Kein Node.js-Paket bietet derzeit die Zuverlässigkeit von openpyxl

### Option C: Hybrid (Python + Node.js) ⚠️ **NUR BEGRÜNDET**

- Python für komplexe Excel-Tasks (Formeln, Templates)
- Node.js für einfache CSV→XLSX-Konvertierung
- Problem: Zwei Systeme = mehr Wartungsaufwand
- Nur sinnvoll wenn OpenClaw WIRKLICH beides braucht

---

## 3. Spezifische Excel-Probleme — Lösung mit openpyxl

### Formeln
```python
ws['E5'] = '=SUM(E2:E4)'        # Normale Formeln
ws['F5'] = '=IF(E5>8,"OK","NG")'  # IF-Logik
ws['G5'] = '=HOUR(E5)'           # Zeit-Funktionen
```

### Datumsformate (Deutsch)
```python
from datetime import datetime
ws['A2'] = datetime(2026, 4, 9)
ws['A2'].number_format = 'DD.MM.'        # Kurzes Format
ws['A3'].number_format = 'DD.MM.YYYY'     # Langes Format
```

### Zeitformate
```python
ws['B2'].value = datetime(1900, 1, 1, 9, 30)  # 09:30
ws['B2'].number_format = 'hh:mm'               # oder 'h:mm'
```

### Zellformate aus Template kopieren
```python
from openpyxl.styles import PatternFill, Font, Border
# Style einer Referenz-Zelle auslesen
source_cell = ws['B2']
target_cell = ws['C2']
target_cell.font = source_cell.font.copy()
target_cell.fill = source_cell.fill.copy()
target_cell.border = source_cell.border.copy()
target_cell.number_format = source_cell.number_format
```

### Merged Cells & Spaltenbreiten
```python
# Merged Cells — openpyxl erhält sie automatisch beim Laden
wb = openpyxl.load_workbook('template.xlsx')
print(wb.active.merged_cells)  # Zeigt alle verbundenen Bereiche

# Spaltenbreiten auslesen
for col in ws.column_dimensions:
    width = ws.column_dimensions[col].width
```

---

## 4. Best Practice für OpenClaw

### 4.1 Architektur: Zentraler Excel-Service

```
┌─────────────────────────────────────────────┐
│  excel-service.py                            │
│  (Python CLI + Library)                       │
│                                              │
│  python3 excel-service.py \                  │
│    fill --template X --data JSON --out Y     │
│                                              │
│  python3 excel-service.py \                  │
│    create --schema JSON --out X              │
└─────────────────────────────────────────────┘
          ▲
          │ CLI call / HTTP / message
          │
    ┌─────┴─────┐
    │ OpenClaw   │
    │ Mission    │
    │ Control    │
    └───────────┘
```

### 4.2 Vorlagen-System

**Upload-Flow:**
1. User lädt `.xlsx`-Template in OpenClaw hoch (z.B. via Discord Attachment)
2. Template wird in definierten Ordner gespeichert (`~/.openclaw/excel-templates/`)
3. Template hat benannte Zellen/Platzhalter: `{{name}}`, `{{datum}}`, `{{stunden}}`
4. OpenClaw füllt Platzhalter via openpyxl aus

**Alternative: Strukturierte Befüllung:**
- Template definiert Layout (Farben, Spalten, Formeln, verbundene Zellen)
- Daten werden als JSON/CSV übergeben
- Zeilen werden dynamisch eingefügt, Style der Header-Zeile wird复制

### 4.3 Integration in Mission Control

```python
# excel-service.py als Flask/FastAPI Microservice
@app.post('/excel/fill')
def fill_template():
    template = request.files['template']
    data = request.get_json()
    # ... openpyxl logic ...
    return send_file(result)
```

Oder als simpler CLI-Wrapper:
```javascript
// OpenClaw Node.js ruft Python auf
const { execSync } = require('child_process');
const result = execSync(
  `python3 ${OPENCLAW_ROOT}/scripts/excel-fill.py --template ${tpl} --data '${json}'`,
  { encoding: 'utf8' }
);
```

---

## 5. Security

### Python Scripts ausführen?
- **Trust-Level abhängig:** Wenn OpenClaw das Script selbst kontrolliert (keine User-Uploads von Code): **sicher**
- **Bei User-Uploads:** Template-Dateien sind XLSX (kein ausführbarer Code), ABER:
  - XLSX kann Makros enthalten (.xlsm) → niemals .xlsm akzeptieren
  - User-Upload: nur `.xlsx` erlauben
  - OpenClaw-internes Python-Script: kein Problem, da kontrollierter Code

### Sandboxing
- Für User-Upload-Templates: XLSX ist eine ZIP-Datei → prüfen ob Inhalt sinnvoll ist
- Kein exec() von User-Input
- User-Template wird in isoliertem Verzeichnis verarbeitet

---

## 6. KLARE EMPFEHLUNGEN

### 1. Welches Tool?
**openpyxl (Python)** als primäres Excel-Tool für OpenClaw.

Node.js Alternative nur für einfache Fälle: **xlsx-populate** für Read/Modify/Write wenn Python nicht verfügbar.

### 2. Warum?
- **Formel-Erhaltung:** openpyxl liest und schreibt Formeln zuverlässig (=SUM, =IF, =HOUR etc.)
- **Template-Treue:** Verbundene Zellen, Spaltenbreiten, Farben, Fonts bleiben erhalten
- **Bewährt:** Bereits erfolgreich im OpenClaw-Einsatz
- **Vergleich:** Alle getesteten Node.js-Libraries haben kritische Bugs bei complexen Excel-Features (ExcelJS Duplication Bug, SheetJS Data Loss). xlsx-populate funktioniert, ist aber weniger maintained.
- **openpyxl:** Aktiv maintained, vollständige Feature-Coverage, einfache Python-CLI mit argparse

### 3. Idealer Workflow

```
User request →
  OpenClaw empfängt Daten (Discord/Telegram/MC) →
    Ruft excel-service.py --template [name] --data [JSON] →
      openpyxl: Template laden, Zellen füllen, Formeln setzen →
        Output speichern oder direkt senden
```

**Zwei Betriebsmodi:**
- **CLI-Modus:** `python3 scripts/excel-fill.py --template zeit.xlsx --data '{"name":"Hans", "stunden":42}' --output out.xlsx`
- **Interactive Fill:** Template mit vordefinierten Spalten, Daten als JSON übergeben, offene Fragen an User

### 4. Was muss installiert werden?

```bash
pip3 install openpyxl
# Optional für schnellere Ausführung:
pip3 install openpyxl[lxml]  # lxml beschleunigt XML-Parsing
```

**Auf Raspberry Pi / Debian:**
```bash
sudo apt-get install python3-openpyxl
# Oder pip:
pip3 install --user openpyxl
```

**Auf macOS:**
```bash
pip3 install openpyxl
# oder: brew install python3 && pip3 install openpyxl
```

**Node.js-Abhängigkeit:** KEINE für Excel-Generierung. Nur für die OpenClaw-Integration (exec call).

### 5. Konkreter nächster Schritt

**Phase 1: Excel-Service als Python-CLI aufsetzen**
```python
# ~/.openclaw/scripts/excel-fill.py
import argparse, json, sys
import openpyxl
from datetime import datetime

def fill_template(template_path, data, output_path):
    wb = openpyxl.load_workbook(template_path)
    ws = wb.active
    # ... fill logic based on data dict ...
    wb.save(output_path)
    return output_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--template', required=True)
    parser.add_argument('--data', required=True)  # JSON string
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    data = json.loads(args.data)
    fill_template(args.template, data, args.output)
    print(f"DONE:{args.output}")
```

**Phase 2: Integration in OpenClaw**
- Excel-Template ordner anlegen: `~/.openclaw/excel-templates/`
- Bekannte Templates vorbereiten (Zeiterfassung, Stundenzettel, etc.)
- OpenClaw Mission Control: Endpunkt der excel-fill.py aufruft
- Discord/Telegram: User kann Template wählen, Daten eingeben, fertige Datei erhalten

**Phase 3: Template-System erweitern**
- User können eigene .xlsx-Templates hochladen
- OpenClaw erkennt Platzhalter (z.B. {{name}}, {{datum}}) und füllt sie
- Vordefinierte Style-Zeile als Vorlage für neue Zeilen

---

## Zusammenfassung

| Aspekt | Empfehlung |
|---|---|
| **Tool** | `openpyxl` (Python) |
| **Workflow** | Template-basiert, CLI-Aufruf aus Node.js |
| **Output** | Zuverlässige .xlsx mit Formeln, Styles, Merged Cells |
| **Maintenance** | Ein Python-Script, leicht zu debuggen |
| **Node.js Rolle** | Nur Orchestration — keine Excel-Logik in JS |
| **Security** | Nur .xlsx erlauben, keine Makros, kontrollierter Code |
| **Nicht empfohlen** | npm xlsx, exceljs (kritische Bugs), SheetJS free (Datenverlust) |
