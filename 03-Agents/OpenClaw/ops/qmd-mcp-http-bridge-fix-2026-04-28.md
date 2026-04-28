# QMD MCP HTTP Bridge Fix — 2026-04-28

## EXECUTION_STATUS
DONE

## ROOT_CAUSE
Der QMD HTTP-MCP-Server (`/home/piet/.local/lib/node_modules/@tobilu/qmd/src/mcp.ts`) hat `WebStandardStreamableHTTPServerTransport` ohne `sessionIdGenerator` erzeugt und dann dieselbe Transport-Instanz über mehrere `/mcp` Requests wiederverwendet. Das ist ein stateless-reuse Pattern, das im SDK zu HTTP-500 führt (`Stateless transport cannot be reused across requests...`).

## CHANGED_FILES
- `/home/piet/.local/lib/node_modules/@tobilu/qmd/src/mcp.ts`
  - `sessionIdGenerator: () => crypto.randomUUID()` in der HTTP-Transport-Initialisierung ergänzt.

## VALIDATION
- `GET http://127.0.0.1:8181/health` → 200
- `POST /mcp initialize` mit `Accept: application/json, text/event-stream` → 200 + `mcp-session-id`
- Zwei aufeinanderfolgende `POST /mcp tools/list` mit derselben `mcp-session-id` → beide 200
- Logcheck: kein neuer Treffer für `Stateless transport cannot be reused across requests` in `/home/piet/.cache/qmd/mcp.log`
- QMD Suchpfad weiterhin funktionsfähig: `qmd search "alerts" --limit 2` liefert Treffer.

## ROLLBACK
- Datei zurücksetzen auf vorherigen Zustand in `mcp.ts` (Zeile mit `sessionIdGenerator` entfernen).
- QMD MCP Daemon neu starten (`qmd mcp stop && qmd mcp --http --daemon --port 8181`).

## NOTES
- Während der Arbeit lief bereits ein älterer Prozess auf Port 8181. Dieser wurde kontrolliert mit `TERM` beendet und der MCP-Daemon anschließend sauber neu gestartet, damit der Fix aktiv wird.
