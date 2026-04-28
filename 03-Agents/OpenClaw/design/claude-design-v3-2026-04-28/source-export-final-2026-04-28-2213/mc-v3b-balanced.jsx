// V3B — Balanced Kanban + Details Drawer (DESKTOP)
// Comfortable density. 5 visible lanes (Failed + Done collapsed at right).
// Designed for: cross-team operator + IC, drawer-driven review, calmer chrome.
// Frame: 1440 × 900.

const V3B_W = 1440, V3B_H = 900;

function V3BDesktop() {
  return (
    <div style={{
      width: V3B_W, height: V3B_H,
      background: "#0a0a0d", color: "white",
      fontFamily: "var(--font-sans)",
      display: "flex", flexDirection: "column",
      overflow: "hidden",
    }}>
      <V3BTopChrome/>
      <div style={{
        flex: 1, display: "grid",
        gridTemplateColumns: "188px 1fr",
        minHeight: 0,
      }}>
        <V3BSidebar/>
        <V3BMain/>
      </div>
    </div>
  );
}

function V3BTopChrome() {
  return (
    <div style={{
      height: 52, padding: "0 18px",
      display: "flex", alignItems: "center", gap: 12,
      borderBottom: "1px solid rgba(255,255,255,.06)",
      background: "rgba(0,0,0,.35)",
      flexShrink: 0,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <div style={{
          width: 24, height: 24, borderRadius: 6,
          background: "linear-gradient(135deg,#7c3aed,#22d3ee)",
          display: "grid", placeItems: "center",
          fontFamily: "var(--font-mono)", fontSize: 11, fontWeight: 700, color: "#0a0a0d",
        }}>MC</div>
        <div style={{ fontSize: 13, fontWeight: 600 }}>Mission Control</div>
      </div>

      <div style={{
        marginLeft: 24, display: "flex", alignItems: "center", gap: 6,
        padding: "6px 10px", borderRadius: 7,
        background: "rgba(255,255,255,.04)", border: "1px solid rgba(255,255,255,.06)",
        width: 360,
      }}>
        <span style={{ fontSize: 12, color: "var(--text-dim)" }}>⌕</span>
        <span style={{ fontSize: 12, color: "var(--text-dim)", flex: 1 }}>
          Search tasks, agents, run ids…
        </span>
        <span style={{
          fontFamily: "var(--font-mono)", fontSize: 10, fontWeight: 600,
          color: "var(--text-dim)", padding: "1px 5px", borderRadius: 3,
          border: "1px solid rgba(255,255,255,.10)",
        }}>⌘K</span>
      </div>

      <div style={{ flex: 1 }}/>

      {/* health is calmer: counters not alerts */}
      <div style={{ display: "flex", alignItems: "center", gap: 14,
        padding: "5px 12px", borderRadius: 999,
        background: "rgba(255,255,255,.03)", border: "1px solid rgba(255,255,255,.06)",
      }}>
        <HealthBeat label="Active"  value="2" color="#5eead4"/>
        <HealthBeat label="Review"  value="1" color="#c4b5fd"/>
        <HealthBeat label="Stale"   value="1" color="#fcd34d"/>
        <HealthBeat label="Failed"  value="2" color="#fda4af"/>
      </div>

      <div style={{
        padding: "5px 11px", borderRadius: 6,
        background: "rgba(124,58,237,.16)", border: "1px solid rgba(124,58,237,.32)",
        color: "#c4b5fd", fontSize: 12, fontWeight: 600,
        cursor: "pointer",
      }}>+ New task</div>

      <div style={{
        width: 28, height: 28, borderRadius: 999,
        background: "linear-gradient(135deg,#3b82f6,#7c3aed)",
        display: "grid", placeItems: "center",
        fontFamily: "var(--font-mono)", fontSize: 10.5, fontWeight: 700,
      }}>PP</div>
    </div>
  );
}

function HealthBeat({ label, value, color }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
      <span style={{
        width: 6, height: 6, borderRadius: 1, background: color,
      }}/>
      <span style={{
        fontSize: 9.5, color: "var(--text-dim)",
        letterSpacing: ".14em", textTransform: "uppercase", fontWeight: 600,
      }}>{label}</span>
      <span style={{
        fontFamily: "var(--font-mono)", fontSize: 12, fontWeight: 600, color: "white",
      }}>{value}</span>
    </div>
  );
}

function V3BSidebar() {
  const items = [
    { icon: "▦", label: "Taskboard", active: true },
    { icon: "↗", label: "Pipeline" },
    { icon: "◐", label: "Workers" },
    { icon: "!",  label: "Alerts", badge: 4 },
    { icon: "✓", label: "Done" },
  ];
  const filters = [
    { dot: "#fcd34d", label: "Stale", count: 1 },
    { dot: "#fda4af", label: "Failed", count: 2 },
    { dot: "#c4b5fd", label: "Review", count: 1 },
    { dot: "#5eead4", label: "Active", count: 2 },
  ];
  return (
    <div style={{
      borderRight: "1px solid rgba(255,255,255,.06)",
      padding: "14px 12px",
      display: "flex", flexDirection: "column", gap: 18,
      background: "rgba(0,0,0,.2)",
    }}>
      <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
        {items.map(it => (
          <div key={it.label} style={{
            display: "flex", alignItems: "center", gap: 8,
            padding: "7px 10px", borderRadius: 6,
            color: it.active ? "white" : "var(--text-soft)",
            background: it.active ? "rgba(255,255,255,.05)" : "transparent",
            border: `1px solid ${it.active ? "rgba(255,255,255,.08)" : "transparent"}`,
            fontSize: 12.5, fontWeight: 500, cursor: "pointer",
          }}>
            <span style={{ width: 14, color: "var(--text-dim)", textAlign: "center" }}>{it.icon}</span>
            <span style={{ flex: 1 }}>{it.label}</span>
            {it.badge && (
              <span style={{
                fontFamily: "var(--font-mono)", fontSize: 10, fontWeight: 700,
                background: "rgba(244,63,94,.18)", color: "#fda4af",
                padding: "1px 5px", borderRadius: 3,
              }}>{it.badge}</span>
            )}
          </div>
        ))}
      </div>

      <div>
        <Eyebrow style={{ marginBottom: 8, padding: "0 4px" }}>Saved views</Eyebrow>
        <div style={{ display: "flex", flexDirection: "column", gap: 2 }}>
          {filters.map(f => (
            <div key={f.label} style={{
              display: "flex", alignItems: "center", gap: 8,
              padding: "5px 10px", borderRadius: 5,
              fontSize: 11.5, color: "var(--text-soft)",
              cursor: "pointer",
            }}>
              <span style={{
                width: 6, height: 6, borderRadius: 1, background: f.dot,
              }}/>
              <span style={{ flex: 1 }}>{f.label}</span>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: 10.5, color: "var(--text-dim)" }}>
                {f.count}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div>
        <Eyebrow style={{ marginBottom: 8, padding: "0 4px" }}>Workers</Eyebrow>
        <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
          {[
            ["Atlas", "AT", "#14b8a6", 4, "ok"],
            ["Forge", "FO", "#f97316", 7, "warn"],
            ["Pixel", "PX", "#d946ef", 5, "ok"],
            ["Lens",  "LN", "#eab308", 3, "ok"],
            ["James", "JM", "#10b981", 2, "ok"],
            ["Spark", "SP", "#ec4899", 1, "idle"],
          ].map(([name, badge, color, n, st]) => (
            <div key={name} style={{
              display: "flex", alignItems: "center", gap: 7,
              padding: "3px 4px", fontSize: 11.5, color: "var(--text-soft)",
            }}>
              <AgentBadge name={name} size="xs"/>
              <span style={{ flex: 1, fontWeight: 500 }}>{name}</span>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: 10.5,
                color: st === "warn" ? "#fcd34d" : "var(--text-dim)",
              }}>{n}</span>
              <span style={{
                width: 5, height: 5, borderRadius: 999,
                background: st === "warn" ? "#f59e0b" : st === "ok" ? "#22c55e" : "#52525b",
              }}/>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ── main: 5 visible lanes + drawer overlay ───────────────────── */
function V3BMain() {
  // primary lanes for board scan; failed lives in a separate "incident strip" above
  const primaryLanes = V3_LANES.filter(l => ["draft","ready","assigned","active","review"].includes(l.id));
  const closedLanes  = V3_LANES.filter(l => ["done","failed"].includes(l.id));

  return (
    <div style={{
      position: "relative",
      display: "flex", flexDirection: "column", minHeight: 0,
      background: "#08080a",
    }}>
      {/* incident strip — only when something is actually wrong */}
      <V3BIncidentStrip/>

      {/* board */}
      <div style={{
        flex: 1, padding: "12px 14px 14px",
        display: "grid",
        gridTemplateColumns: "repeat(5, 1fr)",
        gap: 10,
        minHeight: 0,
      }}>
        {primaryLanes.map(lane => <V3BLane key={lane.id} lane={lane}/>)}
      </div>

      {/* closed-lanes summary footer */}
      <V3BClosedFooter lanes={closedLanes}/>

      {/* drawer overlay docked right */}
      <V3BDrawer/>
    </div>
  );
}

function V3BIncidentStrip() {
  return (
    <div style={{
      margin: "10px 14px 0",
      padding: "10px 12px",
      borderRadius: 8,
      background: "linear-gradient(90deg, rgba(244,63,94,.10) 0%, rgba(244,63,94,.04) 70%, transparent 100%)",
      border: "1px solid rgba(244,63,94,.22)",
      display: "flex", alignItems: "center", gap: 12,
    }}>
      <span style={{
        width: 6, height: 6, borderRadius: 999, background: "#f43f5e",
        boxShadow: "0 0 8px #f43f5e",
        animation: "mc-live-glow 2s ease-in-out infinite",
        flexShrink: 0,
      }}/>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: 12, fontWeight: 600, color: "#fda4af",
          letterSpacing: ".06em", textTransform: "uppercase",
        }}>Needs operator · 3 tasks</div>
        <div style={{ fontSize: 12.5, color: "var(--text-soft)", marginTop: 2 }}>
          MC-T17 failed (operatorLock) · MC-T18 accepted-no-heartbeat 8m · MC-T22 stale 2d high-risk
        </div>
      </div>
      <div style={{
        padding: "5px 11px", borderRadius: 5,
        background: "rgba(244,63,94,.18)", border: "1px solid rgba(244,63,94,.32)",
        color: "#fda4af", fontSize: 11.5, fontWeight: 600,
        cursor: "pointer",
      }}>Triage all</div>
      <div style={{
        padding: "5px 11px", borderRadius: 5,
        background: "rgba(255,255,255,.04)", border: "1px solid rgba(255,255,255,.10)",
        color: "var(--text-soft)", fontSize: 11.5, fontWeight: 500, cursor: "pointer",
      }}>Dismiss</div>
    </div>
  );
}

function V3BLane({ lane }) {
  const tasks = V3_TASKS_BY_LANE(lane.id);
  return (
    <div style={{
      display: "flex", flexDirection: "column", minHeight: 0,
      background: "rgba(255,255,255,.02)",
      border: "1px solid rgba(255,255,255,.04)",
      borderRadius: 10,
      padding: "10px 8px",
      gap: 8,
    }}>
      <V3LaneHeader lane={lane} count={tasks.length}/>
      <div style={{
        flex: 1, display: "flex", flexDirection: "column", gap: 7,
        overflow: "hidden",
      }}>
        {tasks.map(t => (
          <V3Card key={t.id} task={t}
            selected={t.id === "v3_4"}
          />
        ))}
        {tasks.length === 0 && (
          <div style={{
            margin: 4, padding: "20px 10px",
            border: "1px dashed rgba(255,255,255,.08)", borderRadius: 8,
            fontSize: 11.5, color: "var(--text-dim)",
            textAlign: "center", lineHeight: 1.5,
          }}>
            <div style={{ opacity: .4, marginBottom: 4 }}>—</div>
            no tasks in {lane.name.toLowerCase()}
          </div>
        )}
      </div>
    </div>
  );
}

function V3BClosedFooter({ lanes }) {
  return (
    <div style={{
      borderTop: "1px solid rgba(255,255,255,.06)",
      padding: "10px 14px",
      background: "rgba(0,0,0,.2)",
      display: "flex", alignItems: "center", gap: 14,
      flexShrink: 0,
    }}>
      {lanes.map(l => {
        const tasks = V3_TASKS_BY_LANE(l.id);
        const t = V3_TONE[l.tone];
        return (
          <div key={l.id} style={{
            display: "flex", alignItems: "center", gap: 8,
            padding: "5px 11px", borderRadius: 6,
            background: t.bg, border: `1px solid ${t.border}`,
            cursor: "pointer",
          }}>
            <span style={{ width: 6, height: 6, borderRadius: 1, background: t.solid }}/>
            <span style={{ fontSize: 10.5, fontWeight: 600, color: t.fg,
              letterSpacing: ".14em", textTransform: "uppercase",
            }}>{l.name}</span>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "white", fontWeight: 600 }}>
              {String(tasks.length).padStart(2, "0")}
            </span>
            <span style={{ fontSize: 10.5, color: "var(--text-dim)" }}>{l.hint}</span>
          </div>
        );
      })}
      <div style={{ flex: 1 }}/>
      <div style={{ fontSize: 11, color: "var(--text-dim)", fontFamily: "var(--font-mono)" }}>
        last sync 4s ago · 13 tasks · 6 agents
      </div>
    </div>
  );
}

/* ── drawer (compact) ─────────────────────────────────────────── */
function V3BDrawer() {
  const t = V3_DETAIL_TASK;
  return (
    <div style={{
      position: "absolute", top: 0, right: 0, bottom: 0,
      width: 460,
      background: "#0a0a0d",
      borderLeft: "1px solid rgba(255,255,255,.10)",
      boxShadow: "-24px 0 48px rgba(0,0,0,.4)",
      display: "flex", flexDirection: "column",
      overflow: "hidden",
    }}>
      <V3DrawerContent task={t} variant="compact"/>
    </div>
  );
}

Object.assign(window, { V3BDesktop, V3B_W, V3B_H, V3BDrawer });
