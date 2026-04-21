# Sprint O — QMD Minimization (2026-04-22)

Status: PLAN ONLY
Gate: KEIN Execute, KEIN Dispatch aus diesem Sprint-Plan
Owner: Atlas
Review-Gate: Forge

## Entscheidung zu `.config-reload-pending` / `memory.qmd.limits`

Live-Prüfung:
- `/home/piet/.openclaw/workspace/mission-control/.config-reload-pending` existiert aktuell nicht.
- Damit gibt es keinen belastbaren Live-Beleg für ein noch wartendes `memory.qmd.limits`-Reload-Paket in genau diesem Pfad.

Arbeitsentscheidung:
- Das offene `memory.qmd.limits`-Tuning wird **nicht** in Sprint O hineingezogen, solange kein aktueller Pending-Marker oder expliziter Operator-Befehl für Config-Apply vorliegt.
- Wenn die Absicht war, ein bereits vorbereitetes, aber nicht reloadtes Tuning doch noch mitzunehmen, brauche ich den korrekten Live-Pfad oder die konkrete Pending-Artefaktquelle. Bis dahin bleibt es **out of execution scope** und wird nur als Review-Frage geführt.

## Live-Evidenz

```text
.config-reload-pending check:
cat: /home/piet/.openclaw/workspace/mission-control/.config-reload-pending: No such file or directory
```

```text
QMD live memory note (2026-04-21):
- Live QMD findings on 2026-04-21: index healthy and usable; keyword search and CLI vector search worked, MCP deep/vector calls were intermittently unstable (`Connection closed` / timeout), so QMD core health should be validated via CLI/status, not inferred only from MCP behavior.
Source: memory/2026-04-21.md
```

```text
Target evidence to be verified during Forge review / pre-execute validation:
- deep_search timeouts at 20:23 / 20:38 / 21:01 UTC+2
- orphan-reaper log
- mcp-child-teardown.conf:13 escape-seq bug
- vault size reference: 305 files / 56 MB
```

```text
Current live vault size snapshot:
5067
56 /home/piet/vault
```

```text
memory_search registration check in /home/piet/.openclaw/openclaw.json:
- grep for `memory_search` returned no live hit
- current working assumption: `memory_search` is not explicitly registered there as MCP tool-name
- implication for review: treat `memory_search` as a facade/target concept that may need completion rather than assuming it already exists as a registered MCP tool in openclaw.json
```

## Milestones

### O1 — QMD-Nutzung auf Minimalbedarf zurückschneiden
- **Ziel**
  - QMD nur dort behalten, wo keyword/vector retrieval echten Mehrwert liefert; fragile deep-search-Pfade aus dem operativen Default-Pfad entfernen.
  - Falls `memory_search` nicht bereits als registrierter MCP-Endpunkt vorliegt, ist O1 als `memory_search` komplettieren zu lesen, nicht als komplett neue Capability aus dem Nichts bauen.
- **Betroffene Bereiche**
  - `qmd__deep_search`
  - `qmd__search`
  - `qmd__vector_search`
  - Call-Sites im Workspace, die heute QMD reflexhaft statt gezielt verwenden
- **Konkrete Aktion**
  - Den Standardpfad für Retrieval auf `memory_search` plus nur notwendige QMD-Fallbacks reduzieren. `qmd__deep_search` soll nicht mehr als impliziter Routinepfad für operative Workflows dienen.
- **Acceptance-Kriterium**
  - Es existiert eine dokumentierte Zielmatrix: welche Retrieval-Fälle auf `memory_search` gehen, welche auf `qmd__search`, welche auf `qmd__vector_search`, und welche explizit nicht mehr `qmd__deep_search` nutzen.
  - Für jeden entfernten/vermiedenen deep-search-Pfad gibt es einen klaren Ersatzpfad.

### O2 — Instabile Nebenpfade und Child-Teardown-Härte isolieren
- **Ziel**
  - MCP-/Teardown-bedingte Folgestörungen vom eigentlichen Retrieval entkoppeln, damit QMD-Minimierung nicht durch Randfehler verwässert wird.
- **Betroffene Bereiche**
  - `mcp-child-teardown.conf` inklusive Zeile 13 Escape-Sequenz-Bug
  - orphan-reaper / child teardown Verhalten
  - Logpfade, die Timeout/Teardown-Rauschen erzeugen
- **Konkrete Aktion**
  - Separiere den Escape-/Teardown-Bug als klar benannten Randpfad und definiere, ob er vor Sprint O Fix, parallel observiert oder strikt außerhalb des Umsetzungsumfangs gehalten wird. Sprint O soll kein Mischsprint aus Retrieval-Policy und MCP-Teardown-Reparatur werden.
- **Acceptance-Kriterium**
  - Es gibt eine explizite Abgrenzung zwischen QMD-Minimierung und Teardown-/Orphan-Reaper-Fehlern.
  - Ein möglicher Execute-Task für Sprint O kann benennen, welche dieser Randbefunde blockers sind und welche nur beobachtet werden.

### O3 — Sicheren Rollback-Pfad mit QMD-parallel definieren
- **Ziel**
  - Minimierung nur mit kontrolliertem Rückweg, ohne harte Einbahnstraße.
- **Betroffene Bereiche**
  - Retrieval-Routing
  - qmd__*-Call-Sites
  - Beobachtungsfenster nach Umstellung
- **Konkrete Aktion**
  - Definiere einen 7-Tage-Rollback-Pfad mit QMD-parallel: reduzierte Default-Nutzung live, aber QMD-Fallbacks bleiben verfügbar und gezielt zuschaltbar. Kein harter Abbau ohne Beobachtungsphase.
- **Acceptance-Kriterium**
  - Rollback-Strategie ist konkret beschrieben, inklusive Triggern für Rücknahme.
  - Parallelbetrieb für die Beobachtungsphase ist benannt, ohne QMD komplett auszubauen.

## Call-Site-Inventar & Mapping

| Tool | Authoritative Call-Site | Ziel-Routing | Owner |
|---|---|---|---|
| `qmd_search` | `/home/piet/.openclaw/workspace/scripts/retrieval-feedback-loop.py:39` + `/home/piet/.openclaw/workspace/memory/SCHEMA.md:166` | `memory_search` (rg-first) | Atlas |
| `qmd_query` | `/home/piet/.openclaw/workspace/memory/SCHEMA.md:166` (hybrid BM25+vector+rerank) | `memory_search` (full hybrid path) | Atlas |
| `qmd_vsearch` | `/home/piet/.openclaw/workspace/memory/SCHEMA.md:166` | `memory_search` (semantic-hint only) | Atlas |
| `qmd_get` | `/home/piet/.openclaw/workspace/memory/SCHEMA.md:169` | `vault_find + Read` | Forge |
| `qmd_deep_search` | `/home/piet/.openclaw/workspace/scripts/retrieval-feedback-loop.py:39` | manual/forensic only, kein Default | Forge |
| `memory_search` | `/home/piet/.openclaw/workspace/scripts/retrieval-feedback-loop.py:39` | facade target, prüfen ob bereits registriert/teil-implementiert | Atlas |

Kontext, nicht Teil der Call-Site-Tabelle:
- MCP-Server-Registration in `openclaw.json` relevant bei `/home/piet/.openclaw/openclaw.json:504`, `:544`, `:595`, `:649`, `:682`, `:725`, `:767` (per-agent) sowie `:1069`, `:1096` (server-def)

## Rollback-Trigger im 7-Tage-Fenster

| Trigger | Grenzwert | Messquelle | Aktion |
|---|---|---|---|
| Facade-Timeout-Rate Warning | > 10% pro 1h | Retrieval-/Facade-Logs, Sprint-O Beobachtungsreport | Warning im Tagesreport, kein automatischer Rollback |
| Facade-Timeout-Rate Hard Rollback | > 20% pro 1h | Retrieval-/Facade-Logs, Incident-Zeitfenster | Sofort-Rollback auf `memory_search -> 100% QMD` für betroffenen Retrieval-Pfad |
| Retrieval-Fehlerrate bei non-path-Queries | > 30% mit `<3 Hits` | Beobachtungsreport + Query-Sample-Auswertung | Day-Report-Flag, Mapping-Prüfung und Rücknahme einzelner Minimierungsregeln |
| Manual-Override-Requests | > 5 pro Tag | Operator-/Agent-Overrides, Beobachtungsreport | Semantic-Sidecar als Sprint P priorisieren, kein stilles Weiterso |

Zusätzliche Beobachtungspflicht:
- täglicher 08:00-UTC-Checkpoint-Cron: Script `/home/piet/.openclaw/scripts/vault-search-daily-checkpoint.sh`
- Cron-Zeile: `0 8 * * *`
- Output-Target: `/home/piet/vault/03-Agents/vault-search-observation-<YYYY-MM-DD>.md`
- QMD bleibt während des 7-Tage-Fensters parallel funktionsfähig und gezielt zuschaltbar

## Exit-Gate
- Forge-Review liegt vor
- Review beantwortet explizit:
  - Breaking-Change-Audit aller `qmd__*` Call-Sites
  - Mapping zu `memory_search`
  - Rollback-Path via QMD-parallel über 7 Tage
- Es ist entschieden, wie der fehlende `.config-reload-pending`-Marker für `memory.qmd.limits` zu interpretieren ist
- Kein Execute vor expliziter Freigabe nach Review

## Rollback
- Retrieval-Minimierung nur mit QMD-parallel-Rückweg, kein harter Cutover
- Wenn `memory_search` + reduzierte QMD-Fallbacks operativ Lücken erzeugen, wird auf dokumentierten Parallelmodus zurückgeschaltet
- Kein Entfernen von QMD-Komponenten in Sprint O selbst

## Out-of-Scope
- **QMD deinstallieren**
  - Sprint O ist Minimierung und Routing-Härtung, kein Komplettausbau.
- **llm-embed-Sidecar**
  - Das wäre eine neue Architekturkomponente und vergrößert den Scope unnötig.
- **Plattform-Migration**
  - Nicht Teil dieses Stabilitäts-/Minimierungssprints.
- **Ungesichertes `memory.qmd.limits`-Config-Tuning ohne Live-Pending-Artefakt**
  - Ohne belastbaren Pending-Marker wäre das Raten statt sauberer Sprint-Planung.