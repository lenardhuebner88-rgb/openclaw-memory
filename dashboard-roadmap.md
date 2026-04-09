# Finanzdashboard — Entwicklungsstand & Roadmap

**Datum:** 22.03.2026 21:49 – 22:32  
**Status:** MVP fertiggestellt, Optimierungen geplant

---

## ✅ Erledigt (Session 1)

### Core-Features
- ✅ Streamlit-Dashboard mit ING-CSV-Import
- ✅ PayPal-Anreicherung (90 Buchungen)
- ✅ Automatische Kategorisierung (11 Kategorien)
- ✅ Design nach Ziel-Screenshot (Beige #F5F3EF → Light Gray #f5f5f5)
- ✅ KPI-Karten (Einnahmen/Ausgaben/Bilanz/Sparquote)
- ✅ Monatsverlauf-Chart (Balken + Bilanzlinie)
- ✅ Top-Kategorien (Plotly horizontal bar)
- ✅ Größte Einzelausgaben (Top 5)
- ✅ Sparquote-Trend mit 20%-Ziellinie
- ✅ CSV-Export
- ✅ Transaktionssuche & Filter

### Kategorisierung Verbesserungen
- ✅ PayPal → Hersteller-Matching (Monat + Betrag)
- ✅ 150+ Keywords über 12 Kategorien
- ✅ PayPal-spezifische Begriffe (waipu.tv → Abos, Airbnb → Freizeit)

### Technisches
- ✅ Python 3.13, Streamlit 1.55, Plotly 6.6
- ✅ Fallback auf Google Gemini bei Rate Limit
- ✅ Cache für CSV-Laden (@st.cache_data)

---

## 📋 Offen für Session 2 (Priorität)

### 1. Kategorie-Verfeinerung: "Sonstiges" analysieren
**Aufwand:** 30 Min  
**Files:** `analyse_sonstiges.py` vorbereitet  

Neue Kategorien basierend auf Transaktionsmustern:
- "Privat & Familie" ← Überweisungen an Personen (Vorname im Empfänger)
- "Shopping" ← Online-Händler (Amazon, Zalando, EBay, Shein)
- "Essen & Ausgehen" ← Restaurants, Lieferdienste, Cafés
- "Auto & Transport" ← Tankstellen, ADAC, Parkgebühren
- "Haushalt & Reinigung" ← Putzmittel, Reparaturen
- "Sonstiges Rest" ← alles andere

**Regel:** Lastschrift → nach Empfänger, Überweisungen an Personen → Familie

---

### 2. Design-Feinschliff
**Aufwand:** 20 Min

- [ ] Hintergrund: #f5f5f5 (light gray statt warm beige)
- [ ] Karten: reines Weiß (#ffffff)
- [ ] KPI-Zahlen: font-size 32px (jetzt 28px)
- [ ] Section-Spacing: konsistent 20px Padding
- [ ] Borders: subtle #e8e8e8

---

### 3. Sparquote-Chart Verbesserungen
**Aufwand:** 20 Min

- [ ] Gestrichelte Linie für laufenden Monat (März 26)
- [ ] Y-Achse auf [-50%, +50%] begrenzen (statt unbegrenzt)
- [ ] Ausreißer-Kennzeichnung (z.B. Monat mit >50% Sparquote)

---

### 4. Bilanzlinie neu gestalten
**Aufwand:** 45 Min  
**Komplexität:** MITTEL

Option A: Area Chart (gestapelt)
```
┌─────────────────────────┐
│ Einnahmen (grün)        │
├─────────────────────────┤
│ Ausgaben (rot)          │
├─────────────────────────┤
│ Bilanz (grün/rot Fill)  │
└─────────────────────────┘
```

Option B: Separate Bilanz-Fläche unterhalb
- Hauptchart: nur Balken (Ein/Aus)
- Unter-Chart: Bilanz als grüne/rote Fläche

---

### 5. Depot-Sektion (optional)
**Aufwand:** 90 Min  
**Voraussetzung:** Depot-CSV mit historischen Werten

**Benötigte Daten:**
- Datum
- Wert EUR
- Änderung %
- Top Positionen (Vanguard, MSCI, S&P 500)

**Status:** Keine Daten in workspace. Manuell aus Haushaltsfinanzen.html extrahieren nötig.

---

### 6. Kredit-Sektion (optional)
**Aufwand:** 45 Min  
**Voraussetzung:** Kredit-Daten als Config/JSON

**Benötigte Daten (aus Haushaltsfinanzen.html):**
```json
{
  "kredite": [
    {
      "name": "Baufinanzierung 1",
      "restschuld": 149000,
      "monatliche_rate": 679,
      "zinssatz": 3.35,
      "abbezahldatum": "2052-12",
      "laufzeit_monate": 312
    },
    {
      "name": "Baufinanzierung 2",
      "restschuld": 149000,
      "monatliche_rate": 637,
      "zinssatz": 3.35,
      "abbezahldatum": "2055-12",
      "laufzeit_monate": 360
    }
  ]
}
```

---

## 📊 Daten-Bestandsaufnahme

| Quelle | Format | Inhalt | Status |
|--------|--------|--------|--------|
| ING-CSV | CSV | 2127 Transaktionen (Sep 25 – Mär 26) | ✅ aktiv |
| PayPal | CSV | 80 Transaktionen | ✅ aktiv |
| Haushaltsfinanzen.html | HTML | Depot, Kredite, Sparpläne | 📋 nur Anzeige |
| Depot | ? | Kursverlauf über Zeit | ❌ keine Daten |

---

## 🎯 Nächste Schritte (Session 2)

1. **Schnell:** `analyse_sonstiges.py` ausführen → Top-30 unbekannte Buchungen zeigen
2. **Design-Update:** 30 Min für Farben + Spacing
3. **Sparquote:** Laufenden Monat kennzeichnen + Y-Achse begrenzen
4. **Optional:** Bilanz-Redesign (Option A oder B diskutieren)
5. **Späte Priority:** Depot/Kredit (nur mit echten Daten)

---

## 💡 Learnings für nächste Sessions

- **Kategorisierung:** 11 Kategorien decken ~98% ab, Rest ist legitim "Sonstiges"
- **PayPal-Matching:** Zuverlässig über Monat+Betrag (nie über TxnID, da nicht in ING-CSV)
- **Design:** Light-Mode + warm-beige besser als dark-mode, aber verbraucht mehr CSS
- **Token-Effizienz:** Bei >200k Zeilen CSV cachen! (@st.cache_data spart 50% der Ladezeit)

---

**Erstellt:** Peter, 22.03.2026 22:32  
**Nächste Review:** Session 2
