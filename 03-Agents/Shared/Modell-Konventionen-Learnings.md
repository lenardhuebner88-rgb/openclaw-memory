# Modell-Konventionen & Naming (2026-04-28)

## Gültige Modell-IDs

### minimax (Provider: minimax)
| ID | Name | Bemerkung |
|---|---|---|
| `minimax/MiniMax-M2.7-highspeed` | MiniMax M2.7 highspeed | reasoning-fähig, primär |
| `minimax/MiniMax-M2.7` | MiniMax M2.7 (Standard) | non-highspeed |

> **Achtung:** `minimax/MiniMax` existiert NICHT — war ein Fake/Invalide in der Config. Immer vollen Suffix nutzen.

### OpenRouter-Modelle
| ID | Provider | Bemerkung |
|---|---|---|
| `openrouter/moonshotai/kimi-k2.6` | Kimi ( moonshot AI) | reasoning-fähig |
| `openrouter/deepseek/deepseek-v3.2` | DeepSeek | |
| `openrouter/xiaomi/mimo-v2-pro` | Xiaomi | |
| `openrouter/auto` | Auto-Select | generischer Fallback |
| `openrouter/anthropic/claude-sonnet-4-20250514` | Anthropic via OR | |
| `openrouter/google/gemini-2.0-flash` | Google via OR | |

## Warum gültige IDs wichtig sind
- Ungültige IDs in Fallback-Ketten = Router findet Modell nicht → überspringt zu nächster Stufe
- Zirkuläre Ketten (z.B. kimi → MiniMax → kimi) verursachen redundante Aufrufe und Kosten
- Falsche Provider-Pfade: `minimax/MiniMax` vs `minimax/MiniMax-M2.7` —是不同的 Modelle

## Typische Fehler
1. `minimax/MiniMax` statt `minimax/MiniMax-M2.7` oder `minimax/MiniMax-M2.7-highspeed`
2. OpenRouter-Modelle ohne `openrouter/` Prefix referenzieren
3. Zirkuläre Fallback-Ketten (Primary als Fallback wiederholen)

## Validierung
Nach Config-Änderungen: `openclaw doctor` → Errors: 0

## Safe Fallback-Kette (2026-04-28)
Für Agenten mit kimi-k2.6 Primary:
`kimi-k2.6 → MiniMax-M2.7-highspeed → MiniMax-M2.7 → deepseek-v3.2 → openrouter/auto`

Für Agenten mit MiniMax-M2.7-highspeed Primary:
`MiniMax-M2.7-highspeed → MiniMax-M2.7 → deepseek-v3.2 → openrouter/auto`
