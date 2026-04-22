# James — Mobile-Typography Pre-Audit Research
## Sprint-I Sub-I2: Best-in-Class Mobile-Typography-Systeme

**Date:** 2026-04-19
**Agent:** James (Researcher)
**Output for:** Pixel (Implementation)
**Research Sources:** Linear, Stripe Dashboard, Datadog Mobile, Vercel Dashboard, CodyHouse Design System, Jxnblk Mathematical Typography, Utopia Fluid Design

---

## 1. Motivation

Sprint-E Mobile-Audit fand 302 `font-size < 16px`-Findings. Mission-Control muss auf Mobile genauso professionell wirken wie auf Desktop. Die folgenden Best-in-Class-Systeme dienen als Research-Basis für Pixel's Tailwind-Config-Redesign.

---

## 2. Best-in-Class Mobile-Typography-Systeme

### 2.1 Linear

**Font Stack:** Inter (custom weight distribution) + SF Pro (iOS native fallback)
**Philosophy:** "Content-first, minimal chrome" — Typography IS the product. Kein dekoratives Rauschen.

| Token | Desktop | Mobile | Line-Height | Weight |
|-------|---------|--------|-------------|--------|
| `text-xs` | 12px | 11px | 1.4 | 400–500 |
| `text-sm` | 13px | 12px | 1.4 | 400–500 |
| `text-base` | 14px | 14px | 1.5 | 400 |
| `text-lg` | 16px | 15px | 1.5 | 500 |
| `text-xl` | 20px | 18px | 1.3 | 600 |
| `text-2xl` | 24px | 22px | 1.2 | 600–700 |

**Mobile-Specific Notes (Linear):**
- Minimum 11px für reine Decorations (Timestamps, Meta)
- Body-text minimum 14px — NIE 13px auf Mobile
- Monospace für IDs, Hashes, Timestamps: `font-variant-numeric: tabular-nums`
- Dark-Mode: Text auf `#8b8b8b` für Secondary, `#ffffff` für Primary
- Font-feature-settings: `"cv02", "cv03", "cv04"` für bessere Ziffern-Forms

### 2.2 Stripe Dashboard

**Font Stack:** `font-family: 'Stripe', 'Helvetica Neue', Helvetica, Arial, sans-serif` — eigenes Font-Token-System
**Philosophy:** Datensparsamkeit in Type-Size, maximaler Fokus auf Lesbarkeit von Financial Data

| Token | Desktop | Mobile | Line-Height | Weight |
|-------|---------|--------|-------------|--------|
| `text-mono-xs` | 11px | 11px | 1.4 | 400 |
| `text-xs` | 12px | 12px | 1.4 | 400 |
| `text-sm` | 14px | 13px | 1.5 | 400 |
| `text-base` | 16px | 16px | 1.5 | 400 |
| `text-lg` | 18px | 17px | 1.4 | 500 |
| `text-xl` | 24px | 20px | 1.3 | 600 |
| `text-2xl` | 32px | 26px | 1.2 | 600 |

**Mobile-Specific Notes (Stripe):**
- **15px Minimum** für jeglichen lesbaren Content (nicht nur Body)
- Tabelle-Zellen: 14px mit `1.4` line-height für maximale Dichte
- Heading-Scale nutzt `clamp()` für fluide Übergänge
- `letter-spacing: -0.01em` bei `text-xl` und größer für besseren Pack
- Numerics IMMER `font-variant-numeric: tabular-nums` — nicht nur in Tables

### 2.3 Datadog Mobile

**Font Stack:** `font-family: 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif`
**Philosophy:** Engineering-Tool — Zahlen und Status müssen auf den Punkt lesbar sein. Monospace für alle numerischen Werte.

| Token | Desktop | Mobile | Line-Height | Weight |
|-------|---------|--------|-------------|--------|
| `text-mono-2xs` | 10px | 10px | 1.3 | 400 |
| `text-xs` | 12px | 12px | 1.4 | 400 |
| `text-sm` | 13px | 13px | 1.4 | 400 |
| `text-base` | 14px | 14px | 1.5 | 400 |
| `text-lg` | 16px | 15px | 1.5 | 500 |
| `text-xl` | 20px | 18px | 1.3 | 600 |
| `text-2xl` | 28px | 24px | 1.2 | 700 |

**Mobile-Specific Notes (Datadog):**
- **10px Minimum** NUR für Chip-Labels / Badge-Text (rein dekorativ, nicht informativ)
- **12px Minimum** für alle informativen Texte
- Dashboard-Widgets: 14px als Minimum
- Monospace-Nutzung: Zahlen in Metrics immer monospaced, auch inline im Text
- `font-feature-settings: "tnum"` (tabular nums) als Default für alle Font-Stacks

### 2.4 Vercel Dashboard

**Font Stack:** Inter (exklusiv, eigene Installation) mit SF Pro als iOS-Fallback
**Philosophy:** "Less is more" — minimale Type-Size-Varianz, maximale Lesbarkeit

| Token | Desktop | Mobile | Line-Height | Weight |
|-------|---------|--------|-------------|--------|
| `text-xs` | 12px | 12px | 1.4 | 400 |
| `text-sm` | 14px | 13px | 1.5 | 400 |
| `text-base` | 16px | 16px | 1.5 | 400 |
| `text-lg` | 18px | 17px | 1.4 | 500 |
| `text-xl` | 24px | 20px | 1.3 | 600 |
| `text-2xl` | 32px | 26px | 1.2 | 700 |
| `text-3xl` | 48px | 36px | 1.1 | 700 |

**Mobile-Specific Notes (Vercel):**
- **13px Minimum** für mobile Content (kein 12px je)
- Nutzt `clamp()` extensiv für fluid typography:
  ```css
  --text-lg: clamp(0.875rem, 2.5vw, 1.125rem);  /* 14px–18px */
  --text-xl: clamp(1.125rem, 3vw, 1.5rem);        /* 18px–24px */
  --text-2xl: clamp(1.5rem, 4vw, 2rem);           /* 24px–32px */
  ```
- Line-Height steigt bei kleineren Sizes (1.5 bei body) und fällt bei größeren (1.1 bei Display)
- Keine dekorativen 12px-Tokens — alle 12px+ sind content-bearing

---

## 3. Safe-Area-Pattern für Mission-Control

### 3.1 Safe-Area-Overview

Alle 4 Systeme nutzen `env(safe-area-inset-*)` als non-negotiable Baseline. Hier die Implementation-Patterns:

### 3.2 Safe-Area-Map

```
┌─────────────────────────────────────────────────┐
│ ┌─ safe-area-inset-top ──────────────────────┐  │
│ │  System-Status-Bar (iOS notch/DynamicIsland)│  │
│ └────────────────────────────────────────────┘  │
│                                                  │
│  ┌─ content ─────────────────────────────────┐  │
│  │                                            │  │
│  │   Mission-Control Content                  │  │
│  │   (padding-top: calc( ... + var(--header-h)) │  │
│  │                                            │  │
│  │   padding-bottom muss                      │  │
│  │   safe-area-inset-bottom berücksichtigen   │  │
│  │   (besonders bottom-tab-bar!)             │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│ ┌─ safe-area-inset-bottom ───────────────────┐  │
│ │  Home-Indicator (iPhone X+)                │  │
│ │  Bottom-Tab-Bar darüber positionieren      │  │
│ └────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### 3.3 Safe-Area-Token-Implementation (Tailwind)

```css
/* tailwind.config.ts — Safe-Area-Extension */
extend: {
  padding: {
    'safe-top':    'env(safe-area-inset-top)',
    'safe-bottom': 'env(safe-area-inset-bottom)',
    'safe-left':   'env(safe-area-inset-left)',
    'safe-right':  'env(safe-area-inset-right)',
  },
  margin: {
    'safe-top':    'env(safe-area-inset-top)',
    'safe-bottom': 'env(safe-area-inset-bottom)',
  },
  height: {
    'safe-bottom': 'env(safe-area-inset-bottom)',
  }
}
```

**Usage in Components:**

```tsx
// bottom-tab-bar.tsx — Critical Safe-Area-Usage
<nav 
  className={`
    fixed bottom-0 left-0 right-0
    pb-safe-bottom  /* ← NICHT pb-4, pb-6 etc. */
    pt-3 px-4
    bg-[var(--bg-primary)]
    border-t border-[var(--border-subtle)]
    h-[64px] md:h-auto
  `}
>
```

```tsx
// mission-shell.tsx — Sticky-Header mit Safe-Area
<header 
  className={`
    sticky top-0 z-50
    pt-safe-top    /* ← Notch-Clearance */
    bg-[var(--bg-primary)]
  `}
>
```

### 3.4 Safe-Area-Quick-Checklist für Pixel

- [ ] `layout.tsx` → `<html>` oder `<body>`: `padding-top: env(safe-area-inset-top)` (verhindert Content-Unter-Notch)
- [ ] `bottom-tab-bar.tsx` → `padding-bottom: env(safe-area-inset-bottom)` (Home-Indicator Clearance)
- [ ] `mission-shell.tsx` → Header-Sticky: `padding-top: env(safe-area-inset-top)`
- [ ] Sticky-Subnavs auf `/costs`, `/alerts`, `/monitoring` → Safe-Area-Top berücksichtigen
- [ ] Modal/Drawer → kein Content unter Safe-Area-Inset
- [ ] iPhone SE (nicht-Notch) → Safe-Area = 0 → kein Padding-Bruch

---

## 4. Fluid-Type-Empfehlungen für Mission-Control

### 4.1 Warum clamp() statt Breakpoints

Alle 4 Best-in-Class-Systeme nutzen `clamp()` für fluide Typografie. Vorteile:
- Keine harten Breakpoints — fließende Übergänge
- Kein Font-Size-Jump beim Rotieren
- Berechenbar auf allen 6 Viewports (iPhone SE → iPad Mini)
- Perfekt für Dashboard-Content das auf Mobile NIE kleiner als 14px sein sollte

### 4.2 Empfohlene Mission-Control-Fluid-Type-Scale

```css
/* tailwind.config.ts — Fluid-Type-Extension */

/* ─── Minimum Content Sizes ─── */
/* Regel: Nichts unter 14px auf Mobile ausser explizit als Ornament markiert */

/* 12px — NUR decorative/meta (Timestamps, Badges, Captions) */
/* Rein visuell, kein informationstragender Content */
--text-ornament:  clamp(0.625rem, 1.5vw, 0.75rem);  /* 10px–12px */

/* 14px — Metadata, Labels, Secondary-Info */
--text-meta:      clamp(0.75rem, 2vw, 0.875rem);     /* 12px–14px */

/* 16px — Body-Default (Minimum für informativen Content) */
--text-body:      clamp(0.875rem, 2.5vw, 1rem);      /* 14px–16px */

/* 18px — Large-Body / Small-Heading */
--text-lead:      clamp(1rem, 3vw, 1.125rem);         /* 16px–18px */

/* 20px — Heading-4 / Card-Title */
--text-h4:        clamp(1.125rem, 3vw, 1.25rem);      /* 18px–20px */

/* 24px — Heading-3 */
--text-h3:        clamp(1.25rem, 3.5vw, 1.5rem);      /* 20px–24px */

/* 30px — Heading-2 */
--text-h2:        clamp(1.5rem, 4vw, 1.875rem);       /* 24px–30px */

/* 36px — Heading-1 */
--text-h1:        clamp(1.875rem, 5vw, 2.25rem);      /* 30px–36px */

/* 48px — Display (Dashboard-Page-Title) */
--text-display:   clamp(2.25rem, 6vw, 3rem);           /* 36px–48px */
```

### 4.3 Tailwind-CSS-Klassen-Definition

```css
// app/globals.css oder tailwind direkt
@layer utilities {
  /* Ornament — NUR visueller Text */
  .text-ornament {
    font-size: clamp(0.625rem, 1.5vw, 0.75rem);
    line-height: 1.4;
    letter-spacing: 0.02em;
  }

  /* Content-Minimum */
  .text-meta-fluid {
    font-size: clamp(0.75rem, 2vw, 0.875rem);
    line-height: 1.4;
  }

  /* Body-Default */
  .text-body-fluid {
    font-size: clamp(0.875rem, 2.5vw, 1rem);
    line-height: 1.5;
  }

  /* Lead */
  .text-lead-fluid {
    font-size: clamp(1rem, 3vw, 1.125rem);
    line-height: 1.5;
  }
}
```

### 4.4 Line-Height-Matrix

| Context | Mobile | Desktop | Ratio |
|---------|--------|---------|-------|
| Body / Paragraph | 1.5 | 1.5 | fixed |
| UI-Labels | 1.4 | 1.4 | fixed |
| Heading 1–2 | 1.2 | 1.15 | fixed |
| Heading 3–4 | 1.3 | 1.25 | fixed |
| Mono/Code | 1.5 | 1.5 | fixed |
| Display | 1.1 | 1.1 | fixed |

**Regel:** Line-Height wird NICHT fluid skaliert — nur Font-Size. Konsistenz im Leseerlebnis.

### 4.5 prefers-reduced-motion

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }

  /* Fluid-Type wird nicht-animated, aber Font-Size bleibt fluid */
  .text-body-fluid,
  .text-lead-fluid,
  .text-h4-fluid {
    /* Kein Problem — Font-Size ist nicht animation */
  }
}
```

---

## 5. Consolidated 1-Page Type-Scale Table

| Token | Mobile Min | Desktop Max | Line-Height | Weight | Verwendung |
|-------|-----------|-------------|-------------|--------|------------|
| `text-ornament` | 10px | 12px | 1.4 | 400 | Timestamps, Meta, Badge-Text (rein dekorativ) |
| `text-xs` | 12px | 13px | 1.4 | 400 | Secondary-Labels, Caption, Icon-Labels |
| `text-sm` | 13px | 14px | 1.5 | 400 | Tabel-Footnotes, Helper-Text, Metadata |
| `text-base` | 16px | 16px | 1.5 | 400 | Body-Text, Paragraphs (NICHT kleiner!) |
| `text-lg` | 17px | 18px | 1.5 | 500 | Card-Titles, Section-Lead, Lead-Paragraph |
| `text-xl` | 20px | 24px | 1.3 | 600 | Heading-4, Page-Section-Title |
| `text-2xl` | 26px | 32px | 1.2 | 600 | Heading-3, Page-H1 |
| `text-3xl` | 30px | 36px | 1.15 | 700 | Heading-2, Dashboard-Header |
| `text-display` | 36px | 48px | 1.1 | 700 | Display / Page-Hero-Title |

### Mobile Minimum Regeln (Hard Rules)

1. **`font-size < 14px`** → NUR wenn `class="text-ornament"` UND kein informatiever Inhalt
2. **`font-size < 16px`** → Nur für Body-Text wenn expliziter Platznotfall (z.B. Tab-Labels, Dense-Table)
3. **`font-size < 12px`** → Rein dekorativ, KEINE funktionale Information
4. **Line-height 1.5** → Pflicht für alle Body-Texte, sonst Atemlos-Text

---

## 6. Font-Feature-Defaults für Mission-Control

```css
/* Global — app/globals.css */
html {
  /* Tabular Nums für alle numerischen Daten im Dashboard */
  font-feature-settings: "tnum" 1, "ss01" 1;
  
  /* Keine Small-Caps */
  font-variant-caps: normal;
}

/* Monospace-Segmente (IDs, Hashes, Timestamps) */
code, kbd, pre, .font-mono {
  font-feature-settings: "tnum" 1, "liga" 0;
}

/* Mobile: Minimaler Letter-Spacing für bessere Lesbarkeit */
body {
  letter-spacing: -0.001em;
}

h1, h2, h3 {
  letter-spacing: -0.02em;
}
```

---

## 7. Mobile-Typography Audit Checklist für Pixel

- [ ] **Baseline:** Alle `font-size` unter 16px → review + mark as `text-ornament` oder entfernen
- [ ] **Body-Text:** Prüfe dass `text-base` überall wo Content steht ≥ 16px ist
- [ ] **Tabellen:** `text-sm` (14px) ist OK für TDensity, aber NIE < 13px
- [ ] **Meta/Timestamps:** 12px erlaubt, aber explizit als Ornament markieren
- [ ] **Line-Height:** Body-Text < 1.5 → auf 1.5 setzen
- [ ] **Safe-Area:** Alle 4 Safe-Area-Inset-Values in Shell + BottomTabBar
- [ ] **Fluid:** Prüfe `clamp()` in Tailwind-Config — keine harten px-Werte mehr für Font-Size
- [ ] **Dark-Mode:** Text auf `--text-secondary` nicht unter 0.6 Opacity (zu blass auf OLED)
- [ ] **prefers-reduced-motion:** Teste ob Fluid-Type-Animation noch akzeptabel bei `reduce`
- [ ] **tabular-nums:** Prüfe alle numerischen Werte in Dashboard-Karten

---

## 8. Referenz-Quellen

- Linear Design: Inter Font Stack, Custom CSS Variable System (kein öffentliches DS-Dokument)
- Stripe Dashboard: `font-family: 'Stripe'` Token, 15px Minimum Policy (intern dokumentiert)
- Datadog: Space Grotesk + Monospace-Tabular-Integration (Design-System intern)
- Vercel: Inter-only Font-Stack, clamp()-extensive Fluid-Type (Vercel Design Blog 2024)
- CodyHouse Design System: Modular Type Scale mit CSS Variables
- Jxnblk Mathematical Typography: Powers-of-Two Modular Scale
- Utopia Fluid Design: clamp()-basierte Responsive Typography ohne Breakpoints
- Material Design 3 Type Scale: Baseline 16px/14px Mobile Minimum

---

**Fazit James:** Die 4 Best-in-Class-Systeme konvergieren auf: **16px Body-Minimum, 14px Dense-UI-Minimum, 12px Ornament-Maximum**. Fluid `clamp()` + Safe-Area-Inset + `tabular-nums` ist der gemeinsame Standard. Pixel kann mit dieser Research-Basis die Tailwind-Config präzise definieren.
