# MEMORY.md — Peter's Knowledge Base

Langzeitgedächtnis für Peter (OpenClaw). Wichtige Informationen, Infrastruktur, Projekte & Entscheidungen.

---

## 🔧 OpenClaw Setup & Infrastruktur

**Version:** 2026.3.13 (stable, security-audited, Windows 10)

### Modelle & Fallback-Chain — KOSTENOPTIMIERUNG (26.03.2026 17:20)

🔴 **NOTFALL-UPDATE:** $50 in 3 Tagen ausgegeben → Anthropic auf Notfall reduziert

**=== MAIN AGENT (Discord + Standard) ===**
**Primary:** `openrouter/nvidia/nemotron-3-super:free` (**FREE** via OpenRouter)
**Fallback 1:** `openrouter/moonshotai/kimi-k2.5` ($0.40/Mtok)
**Fallback 2:** `openrouter/qwen/qwen3.5-plus-02-15` (~$0.80/Mtok)
**Fallback 3:** `openrouter/deepseek/deepseek-chat` (~$0.14/Mtok)
**Fallback 4:** `google/gemini-3.1-pro-preview` (FREE)
**Fallback 5:** `anthropic/claude-haiku-4-5` ($0.80/Mtok — Notfall)
**Fallback 6:** `anthropic/claude-sonnet-4-6` (nur explizit)

**=== OTHER AGENTS (sre-expert, frontend-guru, etc.) ===**
**Primary:** `minimax/minimax-m2-5` ($0.20/Mtok)
**Fallback 1:** `google/gemini-2.0-flash` (FREE)
**Fallback 2:** `minimax/minimax-m2` ($0.255/Mtok)
**Fallback 3:** `anthropic/claude-haiku-4-5` ($0.80/Mtok — Notfall)
**Fallback 4:** `anthropic/claude-sonnet-4-6` (nur explizit)

**Heartbeat:** `google/gemini-2.0-flash`
**Cron-/Recherche-Jobs:** `minimax/minimax-m2-5` (Standard), fallback zu Gemini wenn MiniMax down

**Status GPT-5.4:** PAUSIERT (Rate-Limit erreicht, 6 Tage Cooldown)
**Status Haiku:** Notfall-Only (nicht mehr Standard)

**Tier-System:** siehe `routing-regelwerk.md`
- Tier 0–1: Gemini Free
- Tier 2–3: MiniMax
- Tier 4: Haiku (Notfall)
- Tier 5: Sonnet (explizit)

**Kostendeckel Anthropic:**
- Tagesbudget: max $5.00
- $3.50 → Warnung
- $5.00 → Sperren (nur Gemini + MiniMax)

**Aktive APIs:**
- Google Generative AI (Gemini Free Tier + Paid)
- MiniMax (OAuth via Portal)
- Brave Search (API Key)
- Anthropic (Notfall + explizit nur)

**Bildmodell:** `google/gemini-3.1-pro-preview` (weiterhin für image tool)

### Workspace & Tools
- **Workspace:** `C:\Users\Lenar\.openclaw\workspace` (Windows Path)
- **Obsidian Vault:** Lokal konfiguriert für Workspace-Dateien
- **Timezone:** Europe/Berlin (GMT+1)
- **Shell:** PowerShell (Windows)

### Routing-Dokumentation
- **Hauptdatei:** `routing-regelwerk.md` (Tier-System, Trigger, Kostendeckel)
- **Versioniert:** Dokumentation bei jedem kostenpflichtigen Update
- **Letzte Änderung:** 2026-03-24 19:51 GMT+1 (Anthropic-Blutung Notfall)

---

## 📁 Projekte

### 1. Home Server (🔴 AKTIV — Hardware-Phase)

**Ziel:** Lokaler Server für OpenClaw + Immich (Fotoverwaltung mit Face Recognition als Rondrive-Ersatz)

**Tech-Stack:**
- Docker Compose (OpenClaw + Immich isoliert)
- Strikte Netzwerk-Trennung (OpenClaw hat KEIN Zugriff auf Immich-Fotos)

**Hardware-Anforderungen:**
- CPU: Intel N100 (bevorzugt) oder sparsame Refurbished Tiny PCs
- Budget: 300–500€
- TDP: max 65W
- **Abgelehnt:** i3-8100 (zu viel Stromverbrauch)

**Status:** Hardware bestellt! (Warten auf Lieferung)

**Next Steps:**
- [x] Konkrete Hardware-Modelle vergleichen (Preise, Verfügbarkeit)
- [ ] OS-Installation planen (sobald das Gerät da ist)
- [ ] Docker-Compose Vorlage vorbereiten
- [ ] Netzwerk-Setup planen (Immich ← Fotoupload / ↛ OpenClaw)

---

### 2. Finanzdashboard (✅ MVP FERTIG — Optimierung läuft)

**Tech:** Streamlit 1.55 + Plotly 6.6 + Pandas 2.3.3

**Features:**
- ING-CSV Import (2127 Transaktionen Sep 2025 – Mär 2026)
- PayPal-Anreicherung (90 Buchungen via Monat+Betrag Matching)
- Automatische Kategorisierung (11 Kategorien + PayPal-spezifische Keywords)
- KPI-Karten (Einnahmen/Ausgaben/Bilanz/Sparquote) mit Vormonatsvergleich
- Monatsverlauf-Chart (Balken + Bilanzlinie)
- Top-Kategorien (Plotly horizontal bar)
- Größte Einzelausgaben (Top 5 Buchungen)
- Sparquote-Trend mit 20%-Ziellinie
- CSV-Export, Transaktionssuche & Filter

**Kategorien:** 11 etabliert
- Lebensmittel & Drogerie
- Wohnen & Haushalt
- Transport & Auto
- Kinder & Betreuung
- Abos & Streaming
- Versicherungen
- Gesundheit & Körperpflege
- Freizeit & Restaurants
- Kleidung & Shopping
- Telekommunikation
- Sparen & Investitionen

**Roadmap für Session 2:**
- [ ] Design: Hintergrund #f5f5f5, Karten weiß, KPI-Zahlen größer
- [ ] Sparquote: Gestrichelte Linie für laufenden Monat, Y-Achse [-50%, +50%]
- [ ] "Sonstiges" verfeinern: neue Kategorien für Privat/Familie, Shopping, Essen, Auto
- [ ] Optional: Bilanz-Linie in Area-Chart umwandeln (grün/rot gefüllt)
- [ ] Optional: Depot-Verlauf (wenn Daten-CSV verfügbar)
- [ ] Optional: Kredit-Sektion (Restschuld, Rate, Abbezahldatum)

**Dateien:**
- `dashboard.py` (Main Streamlit App)
- `umsaetze.csv` (ING-Rohdaten)
- `paypal.csv` (PayPal-Transaktionen für Anreicherung)
- `analyse_sonstiges.py` (zur Kategorisierungs-Analyse)
- `dashboard-roadmap.md` (Detaillierte Planung in memory/)

---

## 💰 Finanz-Überblick (aktuell Mär 2026)

### Einnahmen
- **Lenard (Airbus EG10H IG Metall Hamburg + Unterweser):** ~4.300€ netto/Monat
- **Anna (Land Niedersachsen):** ~1.400€ netto/Monat
- **Kindergeld (2 Kinder):** 500€/Monat
- **Gesamt:** ~6.200€ netto/Monat

### Schulden & Kredite
- **Baufinanzierung 1:** 149.000€ Restschuld, 679€/Monat, 3,35% Zinssatz, fällig 02.2052
- **Baufinanzierung 2:** 149.000€ Restschuld, 637€/Monat, 3,35% Zinssatz, fällig 06.2055
- **Summe Schulden:** 298.000€

### Vermögen
- **Depot:** ~25.825€ (Vanguard FTSE All-World, MSCI World, S&P 500, Emerging Markets, Airbus ESPP)
- **Liquidität:** ~5.177€ (Notgroschen + Sparbetreuung)
- **Kindergeld-Sparen:** eigenes Sub-Depot

### Sparquote & Performance
- **Februar 2026:** +2.285€ (31,4% Sparquote) — best month
- **Target:** ≥ 20% Sparquote
- **Sparplan:** 1.500€/Monat (1.000€ Notgroschen, 300€ ETF, 200€ Sondertilgung)

### 🚨 Critical Risk
- **Keine BU-Versicherung vorhanden!** — Mit 2 Kindern + 298k Kredit + Alleinverdiener-Risiko = HÖCHSTE PRIORITÄT
- Empfehlung: 3 Angebote einholen (Check24, Finanztip), je jünger desto günstiger

### Sparziele & Investitionsplan
- **Notgroschen:** 20.000€ Ziel (aktuell: 3.996€ → 1.000€/Monat Plan, ETA 11.2027)
- **Wärmepumpe 2027:** 8.800€ netto (BEG 60% Förderung VOR Auftragserteilung beantragen!)
- **PV-Anlage 2028:** 18.000€ (0% MwSt, 10 kWp, ~10 Jahre Amortisation mit Wärmepumpe)
- **E-Auto 2029:** 38.000€ Anzahlung (nach PV, kostenlos laden mit Eigenstromprivat)
- **Terrassen-Überdachung 2026:** 10.000€ (Handwerkerleistungen zu 20% in Steuererklärung absetzbar)
  - 📅 **Beratungstermin:** Mo, 31.03.2026 14:00 Uhr
  - 📍 **Ort:** Am Urwald 26, 26340 Zetel
  - 🏢 **Firma:** Friedrich Ahlers GmbH (Handwerk seit 1948)
  - 👤 **Kontakt:** Stefan Schlehuber (Verkäufer & Teamleiter)
  - 💡 **Spezialisierung:** Fenster, Haustüren, Wintergärten, Markisen, Terrassenüberdachungen

---

## 📌 Wichtige Entscheidungen & Erkenntnisse

### Kategorisierung
- **11 Kategorien decken ~98% ab**, Rest ist legitim "Sonstiges"
- **PayPal-Matching:** Zuverlässig über Monat+Betrag (nie über TxnID, da nicht in ING-CSV)
- **Lastschriften:** Meist automatisch kategorisierbar (Vodafone → Telekom, Raiffeisen → Lebensmittel)

### Model-Router (Cost-Optimization)
- **Tier 0 (Heartbeat):** Haiku 4-5 (~1€/Mtok)
- **Tier 1 (Einfache Fragen):** Gemini 2.0 Flash (kostenlos, 60req/min)
- **Tier 2 (Moderat):** Haiku 4-5
- **Tier 3 (Komplex):** Sonnet 4-6
- **Tier 4 (Reasoning):** Opus 4-6 oder DeepSeek R1 (noch zu prüfen)

**Einsparung:** ~80% vs always-Sonnet durch Gemini Free Tier + Routing

### OpenClaw Auth
- API-Key basiert (Anthropic, Google) — deutlich einfacher als OAuth für private Nutzung
- **OAuth-Prüfung:** Nicht sinnvoll für lokal-gehostete Services (zu viel Overhead)
- Fallbacks gewährleisten Verfügbarkeit bei Rate Limits

---

## 🔐 Sicherheit & Datenschutz

- **Workspace:** Lokale Windows-Installation (nicht cloud)
- **CSV-Daten:** Sensitiv (Kontonummern, Beträge) — nur lokal, keine Cloud-Sync
- **PayPal-CSV:** Für Matching zweckgebunden, nicht archiviert
- **Credentials:** In `openclaw.json` (lokale Datei), keine Versionskontrolle

---

## 📅 Regelmäßige Aufgaben

- **Heartbeat:** Täglich 300s Interval (Haiku-optimiert)
- **News-Check:** Montag + Donnerstag via Sub-Agent (SkyWise, KI + Dashboards, AI im Procurement)
- **CSV-Import:** Monatlich vom ING Online-Banking (Dashboard aktualisiert automatisch)
- **Finanz-Audit:** Vierteljährlich (Sparquote, Kredittilgung, Depot-Performance)

---

**Erstellt:** 23.03.2026 10:39  
**Nächste Review:** Wöchentlich (Heartbeat-Basis)
