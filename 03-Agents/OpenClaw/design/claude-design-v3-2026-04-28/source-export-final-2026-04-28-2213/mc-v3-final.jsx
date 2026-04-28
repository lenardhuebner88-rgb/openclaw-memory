// V3 Finalized — recommended hybrid, state-driven via unified V3ControlBar.
//   Density:  Comfy ↔ Dense       (card padding, font sizes)
//   Truth:    Off   ↔ On          (toggles V3A right-rail in place)
//   Mode:     Board ↔ Triage      (toggles V3C inversion in place)
// One control bar. No page reload. Uses V3B chrome as base.

const { useState: useStateFinal } = React;

/* ════════════════════════════════════════════════════════════════
   UNIFIED CONTROL BAR
   ════════════════════════════════════════════════════════════════ */

function V3ControlBar({ state, set, compact = false }) {
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: compact ? 6 : 8,
    }}>
      <V3Seg
        ariaLabel="Density"
        items={[{ id: "comfy", label: "Comfy" }, { id: "dense", label: "Dense" }]}
        value={state.density}
        onChange={v => set({ density: v })}
        compact={compact}
      />
      <V3Seg
        ariaLabel="Mode"
        items={[{ id: "board", label: "Board" }, { id: "triage", label: "Triage", tone: "rose" }]}
        value={state.mode}
        onChange={v => set({ mode: v })}
        compact={compact}
      />
      <V3Toggle
        label="Truth rail"
        value={state.truthRail}
        onChange={v => set({ truthRail: v })}
        compact={compact}
      />
    </div>
  );
}

function V3Seg({ items, value, onChange, ariaLabel, compact }) {
  return (
    <div role="radiogroup" aria-label={ariaLabel} style={{
      display: "flex", gap: 1, padding: 2,
      background: "rgba(255,255,255,.04)", borderRadius: 6,
      border: "1px solid rgba(255,255,255,.06)",
    }}>
      {items.map(it => {
        const on = value === it.id;
        const tone = it.tone ? V3_TONE[it.tone] : null;
        const bg = on
          ? (tone ? tone.bg : "rgba(255,255,255,.08)")
          : "transparent";
        const fg = on ? (tone ? tone.fg : "white") : "var(--text-soft)";
        const bd = on && tone ? `inset 0 0 0 1px ${tone.border}` : "none";
        return (
          <button
            key={it.id} role="radio" aria-checked={on}
            onClick={() => onChange(it.id)}
            style={{
              all: "unset", cursor: "pointer",
              padding: compact ? "3px 8px" : "4px 10px",
              borderRadius: 4,
              fontSize: compact ? 10.5 : 11,
              fontWeight: 600, letterSpacing: ".01em",
              color: fg, background: bg, boxShadow: bd,
            }}
          >{it.label}</button>
        );
      })}
    </div>
  );
}

function V3Toggle({ label, value, onChange, compact }) {
  const on = !!value;
  return (
    <button
      role="switch" aria-checked={on}
      onClick={() => onChange(!on)}
      style={{
        all: "unset", cursor: "pointer",
        display: "inline-flex", alignItems: "center", gap: 7,
        padding: compact ? "3px 9px 3px 7px" : "4px 11px 4px 8px",
        borderRadius: 6,
        background: on ? "rgba(124,58,237,.14)" : "rgba(255,255,255,.04)",
        border: `1px solid ${on ? "rgba(124,58,237,.32)" : "rgba(255,255,255,.06)"}`,
        color: on ? "#c4b5fd" : "var(--text-soft)",
        fontSize: compact ? 10.5 : 11, fontWeight: 600, letterSpacing: ".01em",
      }}
    >
      <span style={{
        position: "relative",
        width: compact ? 22 : 24, height: compact ? 12 : 13,
        borderRadius: 999,
        background: on ? "rgba(124,58,237,.55)" : "rgba(255,255,255,.10)",
        transition: "background 120ms ease",
      }}>
        <span style={{
          position: "absolute",
          top: 1, left: on ? (compact ? 11 : 12) : 1,
          width: compact ? 10 : 11, height: compact ? 10 : 11,
          borderRadius: 999,
          background: on ? "white" : "var(--text-soft)",
          transition: "left 120ms ease",
        }}/>
      </span>
      {label}
    </button>
  );
}

/* ════════════════════════════════════════════════════════════════
   FINALIZED DESKTOP — V3B chrome, state-driven layout.
   ════════════════════════════════════════════════════════════════ */

function V3FinalDesktop({ initial, label }) {
  const [state, setStateInternal] = useStateFinal({
    density: "comfy",
    mode:    "board",
    truthRail: false,
    ...(initial || {}),
  });
  const set = (patch) => setStateInternal(s => ({ ...s, ...patch }));

  // health derived from sample data (would come from server in prod)
  const health = useV3Health();

  return (
    <div style={{
      width: V3B_W, height: V3B_H,
      background: "#0a0a0d", color: "white",
      fontFamily: "var(--font-sans)",
      display: "flex", flexDirection: "column",
      overflow: "hidden",
    }}>
      <V3FinalTopChrome health={health}/>
      <V3FinalSubBar state={state} set={set} health={health}/>
      <div style={{
        flex: 1, display: "grid",
        gridTemplateColumns: state.truthRail ? "176px 1fr 304px" : "176px 1fr",
        minHeight: 0,
      }}>
        <V3FinalSidebar/>
        <V3FinalMain state={state} health={health}/>
        {state.truthRail && <V3FinalTruthRail health={health}/>}
      </div>
    </div>
  );
}

/* ── derived health (single source — drives chrome, control bar, rail) ── */
function useV3Health() {
  return useMemoV3(() => {
    const counts = {
      active:  V3_TASKS.filter(t => t.status === "active").length,
      review:  V3_TASKS.filter(t => t.status === "review").length,
      stale:   V3_TASKS.filter(t => t.status === "noheartbeat" || t.status === "stale").length,
      failed:  V3_TASKS.filter(t => t.status === "failed" || t.status === "blocked").length,
    };
    const incidentCount = counts.failed + counts.stale;
    return { ...counts, incidentCount, hasIncident: incidentCount > 0 };
  }, []);
}

/* ── top chrome — calmer: no big health pill, just a tight beat row ── */
function V3FinalTopChrome({ health }) {
  return (
    <div style={{
      height: 44, padding: "0 16px",
      display: "flex", alignItems: "center", gap: 14,
      borderBottom: "1px solid rgba(255,255,255,.06)",
      background: "rgba(0,0,0,.4)",
      flexShrink: 0,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <div style={{
          width: 22, height: 22, borderRadius: 5,
          background: "linear-gradient(135deg,#7c3aed,#22d3ee)",
          display: "grid", placeItems: "center",
          fontFamily: "var(--font-mono)", fontSize: 10.5, fontWeight: 700, color: "#0a0a0d",
        }}>MC</div>
        <div style={{ fontSize: 12.5, fontWeight: 600 }}>Mission Control</div>
        <span style={{ color: "var(--text-dim)", margin: "0 2px" }}>/</span>
        <div style={{ fontSize: 12.5, color: "var(--text-soft)" }}>Taskboard</div>
      </div>

      <div style={{ flex: 1 }}/>

      {/* Search — slim */}
      <div style={{
        display: "flex", alignItems: "center", gap: 6,
        padding: "4px 9px", borderRadius: 6,
        background: "rgba(255,255,255,.04)", border: "1px solid rgba(255,255,255,.06)",
        width: 320,
      }}>
        <span style={{ fontSize: 11, color: "var(--text-dim)" }}>⌕</span>
        <span style={{ fontSize: 11.5, color: "var(--text-dim)", flex: 1 }}>
          Search · jump to task, agent, run id…
        </span>
        <span style={{
          fontFamily: "var(--font-mono)", fontSize: 10, fontWeight: 600,
          color: "var(--text-dim)", padding: "1px 5px", borderRadius: 3,
          border: "1px solid rgba(255,255,255,.10)",
        }}>⌘K</span>
      </div>

      {/* New task */}
      <button style={{
        all: "unset", cursor: "pointer",
        padding: "4px 11px", borderRadius: 6,
        background: "rgba(124,58,237,.14)", border: "1px solid rgba(124,58,237,.32)",
        color: "#c4b5fd", fontSize: 11.5, fontWeight: 600,
      }}>+ New task</button>

      <div style={{
        width: 26, height: 26, borderRadius: 999,
        background: "linear-gradient(135deg,#3b82f6,#7c3aed)",
        display: "grid", placeItems: "center",
        fontFamily: "var(--font-mono)", fontSize: 10, fontWeight: 700,
      }}>PP</div>
    </div>
  );
}

/* ── sub-bar — health beats + control bar (Density/Mode/Truth) ── */
function V3FinalSubBar({ state, set, health }) {
  return (
    <div style={{
      height: 38, padding: "0 16px",
      display: "flex", alignItems: "center", gap: 14,
      borderBottom: "1px solid rgba(255,255,255,.06)",
      background: "rgba(0,0,0,.2)",
      flexShrink: 0,
    }}>
      {/* Honest health beats — calm by default, only colored chips when nonzero */}
      <V3Beat label="Active"  value={health.active}  color="#5eead4" />
      <V3Beat label="Review"  value={health.review}  color="#c4b5fd" emphasize={health.review > 0}/>
      <V3Beat label="Stale"   value={health.stale}   color="#fcd34d" emphasize={health.stale > 0}/>
      <V3Beat label="Failed"  value={health.failed}  color="#fda4af" emphasize={health.failed > 0}/>

      <span style={{
        fontSize: 11, color: "var(--text-dim)",
        fontFamily: "var(--font-mono)", marginLeft: 6,
      }}>13 tasks · 6 agents · last sync 4s ago</span>

      <div style={{ flex: 1 }}/>

      <V3ControlBar state={state} set={set}/>
    </div>
  );
}

function V3Beat({ label, value, color, emphasize = false }) {
  const dim = !emphasize && value === 0;
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 6,
      opacity: dim ? .55 : 1,
    }}>
      <span style={{
        width: 6, height: 6, borderRadius: 1,
        background: color,
        boxShadow: emphasize ? `0 0 6px ${color}` : undefined,
      }}/>
      <span style={{
        fontSize: 9.5, color: "var(--text-dim)",
        letterSpacing: ".16em", textTransform: "uppercase", fontWeight: 600,
      }}>{label}</span>
      <span style={{
        fontFamily: "var(--font-mono)", fontSize: 12, fontWeight: 600,
        color: emphasize ? "white" : "var(--text-soft)",
      }}>{value}</span>
    </div>
  );
}

/* ── sidebar — lighter than V3B's ── */
function V3FinalSidebar() {
  const items = [
    { icon: "▦", label: "Taskboard", active: true },
    { icon: "↗", label: "Pipeline" },
    { icon: "◐", label: "Workers" },
    { icon: "!",  label: "Alerts", badge: 4 },
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
      padding: "14px 10px",
      display: "flex", flexDirection: "column", gap: 18,
      background: "rgba(0,0,0,.2)",
    }}>
      <div style={{ display: "flex", flexDirection: "column", gap: 1 }}>
        {items.map(it => (
          <div key={it.label} style={{
            display: "flex", alignItems: "center", gap: 8,
            padding: "6px 9px", borderRadius: 5,
            color: it.active ? "white" : "var(--text-soft)",
            background: it.active ? "rgba(255,255,255,.05)" : "transparent",
            border: `1px solid ${it.active ? "rgba(255,255,255,.08)" : "transparent"}`,
            fontSize: 12, fontWeight: 500, cursor: "pointer",
          }}>
            <span style={{ width: 14, color: "var(--text-dim)", textAlign: "center" }}>{it.icon}</span>
            <span style={{ flex: 1 }}>{it.label}</span>
            {it.badge && (
              <span style={{
                fontFamily: "var(--font-mono)", fontSize: 10, fontWeight: 700,
                background: "rgba(244,63,94,.16)", color: "#fda4af",
                padding: "0 5px", borderRadius: 3,
              }}>{it.badge}</span>
            )}
          </div>
        ))}
      </div>

      <div>
        <Eyebrow style={{ marginBottom: 7, padding: "0 4px" }}>Saved views</Eyebrow>
        <div style={{ display: "flex", flexDirection: "column", gap: 1 }}>
          {filters.map(f => (
            <div key={f.label} style={{
              display: "flex", alignItems: "center", gap: 8,
              padding: "5px 9px", borderRadius: 5,
              fontSize: 11.5, color: "var(--text-soft)",
              cursor: "pointer",
            }}>
              <span style={{ width: 5, height: 5, borderRadius: 1, background: f.dot }}/>
              <span style={{ flex: 1 }}>{f.label}</span>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: 10.5, color: "var(--text-dim)" }}>
                {f.count}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div>
        <Eyebrow style={{ marginBottom: 7, padding: "0 4px" }}>Workers</Eyebrow>
        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
          {[
            ["Atlas",  4, "ok"],
            ["Forge",  7, "warn"],
            ["Pixel",  5, "ok"],
            ["Lens",   3, "ok"],
            ["James",  2, "ok"],
            ["Spark",  1, "idle"],
          ].map(([name, n, st]) => (
            <div key={name} style={{
              display: "flex", alignItems: "center", gap: 7,
              padding: "2px 4px", fontSize: 11.5, color: "var(--text-soft)",
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

/* ── main board — switches between Board and Triage modes in place ── */
function V3FinalMain({ state, health }) {
  return (
    <div style={{
      display: "flex", flexDirection: "column", minHeight: 0,
      background: "#08080a",
      overflow: "hidden",
    }}>
      {/* Incident strip — only when there is something to triage */}
      {health.hasIncident && state.mode === "board" && <V3FinalIncidentStrip health={health}/>}

      {state.mode === "board"
        ? <V3FinalBoard density={state.density}/>
        : <V3FinalTriage density={state.density}/>}
    </div>
  );
}

function V3FinalIncidentStrip({ health }) {
  return (
    <div style={{
      margin: "10px 14px 0",
      padding: "8px 12px",
      borderRadius: 8,
      background: "linear-gradient(90deg, rgba(244,63,94,.10) 0%, rgba(244,63,94,.04) 70%, transparent 100%)",
      border: "1px solid rgba(244,63,94,.22)",
      display: "flex", alignItems: "center", gap: 12, flexShrink: 0,
    }}>
      <span style={{
        width: 6, height: 6, borderRadius: 999, background: "#f43f5e",
        boxShadow: "0 0 8px #f43f5e",
        animation: "mc-live-glow 2s ease-in-out infinite",
        flexShrink: 0,
      }}/>
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 11.5, fontWeight: 600, color: "#fda4af",
          letterSpacing: ".06em", textTransform: "uppercase",
        }}>Needs operator · {health.incidentCount} {health.incidentCount === 1 ? "task" : "tasks"}</div>
        <div style={{ fontSize: 12, color: "var(--text-soft)", marginTop: 1,
          whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
        }}>
          MC-T17 failed (operatorLock) · MC-T18 accepted-no-heartbeat 8m · MC-T22 stale 2d high-risk
        </div>
      </div>
      <button style={{
        all: "unset", cursor: "pointer",
        padding: "4px 10px", borderRadius: 5,
        background: "rgba(244,63,94,.18)", border: "1px solid rgba(244,63,94,.32)",
        color: "#fda4af", fontSize: 11, fontWeight: 600,
      }}>Triage all</button>
      <button style={{
        all: "unset", cursor: "pointer",
        padding: "4px 10px", borderRadius: 5,
        background: "rgba(255,255,255,.04)", border: "1px solid rgba(255,255,255,.10)",
        color: "var(--text-soft)", fontSize: 11, fontWeight: 500,
      }}>Dismiss</button>
    </div>
  );
}

/* BOARD MODE — V3B layout, density-aware */
function V3FinalBoard({ density }) {
  const primary = V3_LANES.filter(l => ["draft","ready","assigned","active","review"].includes(l.id));
  const closed  = V3_LANES.filter(l => ["done","failed"].includes(l.id));
  return (
    <>
      <div style={{
        flex: 1,
        padding: density === "dense" ? "10px 12px 12px" : "12px 14px 14px",
        display: "grid",
        gridTemplateColumns: "repeat(5, 1fr)",
        gap: density === "dense" ? 8 : 10,
        minHeight: 0,
      }}>
        {primary.map(lane => <V3FinalLane key={lane.id} lane={lane} density={density}/>)}
      </div>
      <V3FinalClosedFooter lanes={closed}/>
    </>
  );
}

function V3FinalLane({ lane, density }) {
  const tasks = V3_TASKS_BY_LANE(lane.id);
  return (
    <div style={{
      display: "flex", flexDirection: "column", minHeight: 0,
      background: "rgba(255,255,255,.02)",
      border: "1px solid rgba(255,255,255,.04)",
      borderRadius: 10,
      padding: density === "dense" ? "8px 6px" : "10px 8px",
      gap: density === "dense" ? 6 : 8,
    }}>
      <V3LaneHeader lane={lane} count={tasks.length}/>
      <div style={{
        flex: 1,
        display: "flex", flexDirection: "column",
        gap: density === "dense" ? 5 : 7,
        overflow: "hidden",
      }}>
        {tasks.length === 0
          ? <V3FinalEmptyLane lane={lane}/>
          : tasks.map(t => (
            <V3Card key={t.id} task={t} dense={density === "dense"}/>
          ))
        }
      </div>
    </div>
  );
}

function V3FinalEmptyLane({ lane }) {
  return (
    <div style={{
      margin: 4, padding: "16px 10px",
      border: "1px dashed rgba(255,255,255,.08)", borderRadius: 8,
      fontSize: 11, color: "var(--text-dim)",
      textAlign: "center", lineHeight: 1.5,
    }}>
      <div style={{ opacity: .4, marginBottom: 4, fontSize: 13 }}>—</div>
      no {lane.name.toLowerCase()}
    </div>
  );
}

function V3FinalClosedFooter({ lanes }) {
  return (
    <div style={{
      borderTop: "1px solid rgba(255,255,255,.06)",
      padding: "9px 14px",
      background: "rgba(0,0,0,.2)",
      display: "flex", alignItems: "center", gap: 10,
      flexShrink: 0,
    }}>
      {lanes.map(l => {
        const tasks = V3_TASKS_BY_LANE(l.id);
        const t = V3_TONE[l.tone];
        return (
          <button key={l.id} style={{
            all: "unset", cursor: "pointer",
            display: "flex", alignItems: "center", gap: 7,
            padding: "4px 10px", borderRadius: 6,
            background: t.bg, border: `1px solid ${t.border}`,
          }}>
            <span style={{ width: 5, height: 5, borderRadius: 1, background: t.solid }}/>
            <span style={{ fontSize: 10, fontWeight: 600, color: t.fg,
              letterSpacing: ".16em", textTransform: "uppercase",
            }}>{l.name}</span>
            <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "white", fontWeight: 600 }}>
              {String(tasks.length).padStart(2, "0")}
            </span>
            <span style={{ fontSize: 10.5, color: "var(--text-dim)" }}>· {l.hint}</span>
          </button>
        );
      })}
      <span style={{ flex: 1 }}/>
      <span style={{ fontSize: 10.5, color: "var(--text-dim)", fontFamily: "var(--font-mono)" }}>
        last sync 4s ago · 13 tasks · 6 agents
      </span>
    </div>
  );
}

/* TRIAGE MODE — incidents on top, healthy compressed */
function V3FinalTriage({ density }) {
  const incidents = V3_TASKS.filter(t =>
    t.status === "failed" || t.status === "blocked" || t.status === "noheartbeat"
  );
  const review = V3_TASKS.filter(t => t.status === "review");
  const active = V3_TASKS.filter(t => t.status === "active");
  const quiet = [
    { lane: "draft",    tasks: V3_TASKS_BY_LANE("draft")    },
    { lane: "ready",    tasks: V3_TASKS_BY_LANE("ready")    },
    { lane: "assigned", tasks: V3_TASKS_BY_LANE("assigned").filter(t => t.status !== "noheartbeat") },
    { lane: "done",     tasks: V3_TASKS_BY_LANE("done")     },
  ];
  return (
    <div style={{
      flex: 1, padding: density === "dense" ? "10px 12px 12px" : "14px 16px 16px",
      display: "flex", flexDirection: "column",
      gap: density === "dense" ? 10 : 14,
      overflow: "auto",
    }}>
      <V3TriageBlock title="Incidents · needs operator now" tone="rose" count={incidents.length}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: density === "dense" ? 8 : 10 }}>
          {incidents.map(t => <V3TriageIncidentCard key={t.id} task={t}/>)}
        </div>
      </V3TriageBlock>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: density === "dense" ? 10 : 12 }}>
        <V3TriageBlock title="Review needed" tone="violet" count={review.length}>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {review.map(t => <V3Card key={t.id} task={t} dense/>)}
          </div>
        </V3TriageBlock>
        <V3TriageBlock title="In progress · healthy" tone="teal" count={active.length}>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {active.map(t => <V3Card key={t.id} task={t} dense/>)}
          </div>
        </V3TriageBlock>
      </div>

      <V3TriageBlock title="Quiet lanes · click to expand" tone="zinc">
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 8 }}>
          {quiet.map(q => <V3QuietChip key={q.lane} laneId={q.lane} tasks={q.tasks}/>)}
        </div>
      </V3TriageBlock>
    </div>
  );
}

function V3TriageBlock({ title, tone, count, children }) {
  const t = V3_TONE[tone];
  return (
    <section>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
        <span style={{ width: 6, height: 6, borderRadius: 1, background: t.solid,
          boxShadow: tone !== "zinc" ? `0 0 6px ${t.solid}` : undefined,
        }}/>
        <span style={{ fontSize: 10.5, fontWeight: 700, color: t.fg,
          letterSpacing: ".18em", textTransform: "uppercase",
        }}>{title}</span>
        {typeof count === "number" && (
          <span style={{
            fontFamily: "var(--font-mono)", fontSize: 11, color: "white", fontWeight: 600,
          }}>{String(count).padStart(2, "0")}</span>
        )}
      </div>
      {children}
    </section>
  );
}

function V3TriageIncidentCard({ task }) {
  const s = V3_STATUS[task.status];
  const tone = s.intent === "danger" ? V3_TONE.rose : V3_TONE.amber;
  return (
    <div style={{
      padding: 11,
      borderRadius: 10,
      background: `linear-gradient(180deg, ${tone.bg} 0%, rgba(255,255,255,.02) 100%)`,
      border: `1px solid ${tone.border}`,
      display: "flex", flexDirection: "column", gap: 7,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        <StatusBadge status={task.status} showIntent/>
        <PriorityBadge priority={task.priority}/>
        <span style={{ flex: 1 }}/>
        <AgentBadge name={task.agent} size="xs"/>
        <AgeTag age={task.age} stale={!!task.stale}/>
      </div>
      <div style={{
        fontSize: 13, fontWeight: 600, lineHeight: 1.3,
        color: "white",
        display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical",
        overflow: "hidden",
      }}>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 11,
          color: "var(--text-dim)", marginRight: 6,
        }}>{task.code}</span>
        {task.title}
      </div>
      <div style={{ fontSize: 11.5, lineHeight: 1.4, color: tone.fg, fontWeight: 500 }}>
        {s.intent === "danger" ? "⛔ " : "⚠ "}{task.signal}
      </div>
      <div style={{ display: "flex", gap: 5, marginTop: 1 }}>
        <V3Btn primary tone={s.intent === "danger" ? "rose" : "amber"}>Triage</V3Btn>
        <V3Btn>Logs</V3Btn>
      </div>
    </div>
  );
}

function V3QuietChip({ laneId, tasks }) {
  const lane = V3_LANES.find(l => l.id === laneId);
  const t = V3_TONE[lane.tone];
  return (
    <button style={{
      all: "unset", cursor: "pointer",
      padding: 9, borderRadius: 8,
      background: "rgba(0,0,0,.25)",
      border: `1px solid ${t.border}`,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 7 }}>
        <span style={{ width: 5, height: 5, borderRadius: 1, background: t.solid }}/>
        <span style={{ fontSize: 10, fontWeight: 600, color: t.fg,
          letterSpacing: ".16em", textTransform: "uppercase",
        }}>{lane.name}</span>
        <span style={{ flex: 1 }}/>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "white", fontWeight: 600 }}>
          {String(tasks.length).padStart(2,"0")}
        </span>
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 3 }}>
        {tasks.slice(0,4).map(task => (
          <span key={task.id} style={{
            fontFamily: "var(--font-mono)", fontSize: 10,
            padding: "1px 5px", borderRadius: 3,
            background: "rgba(255,255,255,.04)",
            color: "var(--text-soft)",
          }}>{task.code}</span>
        ))}
        {tasks.length > 4 && (
          <span style={{ fontSize: 10, color: "var(--text-dim)" }}>
            +{tasks.length - 4}
          </span>
        )}
      </div>
    </button>
  );
}

/* TRUTH RAIL — opt-in V3A panel, slimmed */
function V3FinalTruthRail({ health }) {
  return (
    <div style={{
      borderLeft: "1px solid rgba(255,255,255,.06)",
      background: "rgba(0,0,0,.3)",
      display: "flex", flexDirection: "column",
      overflow: "hidden",
    }}>
      <div style={{ padding: "12px 14px 8px",
        borderBottom: "1px solid rgba(255,255,255,.06)",
      }}>
        <Eyebrow>Truth · system state</Eyebrow>
      </div>

      <div style={{ padding: 12, display: "flex", flexDirection: "column", gap: 10, overflow: "auto" }}>
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
          <TruthChip label="Active" value={String(health.active).padStart(2,"0")} tone="teal"  detail="hb green"/>
          <TruthChip label="Review" value={String(health.review).padStart(2,"0")} tone="violet" detail="awaits operator"/>
          <TruthChip label="Stale"  value={String(health.stale).padStart(2,"0")}  tone="amber"  detail="no heartbeat"/>
          <TruthChip label="Failed" value={String(health.failed).padStart(2,"0")} tone="rose"   detail="needs review"/>
        </div>

        <div style={{
          padding: 10, borderRadius: 8,
          background: "rgba(124,58,237,.08)", border: "1px solid rgba(124,58,237,.28)",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
            <span style={{
              width: 16, height: 16, borderRadius: 3,
              background: "rgba(124,58,237,.20)", color: "#c4b5fd",
              display: "grid", placeItems: "center",
              fontFamily: "var(--font-mono)", fontSize: 9, fontWeight: 700,
            }}>AT</span>
            <div style={{ fontSize: 10.5, fontWeight: 600, color: "#c4b5fd",
              letterSpacing: ".14em", textTransform: "uppercase",
            }}>Atlas · suggests next</div>
          </div>
          <div style={{ fontSize: 12.5, lineHeight: 1.45, color: "white" }}>
            Review <span style={{ fontFamily: "var(--font-mono)", color: "#fda4af" }}>MC-T17</span> failure: payload schema rejected operatorLock. Two follow-ups already drafted.
          </div>
          <div style={{ display: "flex", gap: 6, marginTop: 8 }}>
            <V3Btn primary>Open MC-T17</V3Btn>
            <V3Btn>Dismiss</V3Btn>
          </div>
        </div>

        <div>
          <Eyebrow>Selected · MC-T17</Eyebrow>
          <div style={{ marginTop: 6, padding: 10, borderRadius: 8,
            background: "rgba(244,63,94,.06)", border: "1px solid rgba(244,63,94,.20)",
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
              <StatusBadge status="failed" showIntent/>
              <PriorityBadge priority="P2"/>
              <span style={{ flex: 1 }}/>
              <AgeTag age="12m" stale/>
            </div>
            <div style={{ fontSize: 12.5, fontWeight: 600, lineHeight: 1.35, marginBottom: 6 }}>
              mc-pending-pickup-smoke.sh · operatorLock missing in payload
            </div>
            <ReceiptDots/>
            <div style={{ marginTop: 8, fontSize: 11.5, lineHeight: 1.45, color: "#fda4af" }}>
              ⛔ Result · failed · payload schema rejected
            </div>
            <div style={{ display: "flex", gap: 6, marginTop: 9 }}>
              <V3Btn primary tone="rose">Review failure</V3Btn>
              <V3Btn>Open drawer</V3Btn>
            </div>
          </div>
        </div>

        <div style={{
          padding: "8px 10px", borderRadius: 6,
          background: "rgba(255,255,255,.02)", border: "1px solid rgba(255,255,255,.06)",
          display: "flex", flexDirection: "column", gap: 4,
        }}>
          <Eyebrow>Worker session</Eyebrow>
          <div style={{ fontFamily: "var(--font-mono)", fontSize: 10.5, color: "var(--text-soft)" }}>
            ws_01HX7N4C7E2K5J · Forge · region us-east-1
          </div>
          <div style={{ fontFamily: "var(--font-mono)", fontSize: 10.5, color: "var(--text-soft)" }}>
            dt_2K9P7M · run_4K2P9M7B
          </div>
        </div>
      </div>
    </div>
  );
}

/* ════════════════════════════════════════════════════════════════
   MOBILE FINAL — tighter, calmer, sticky control bar inline
   ════════════════════════════════════════════════════════════════ */

function V3MobileFinal() {
  const [state, setStateInternal] = useStateFinal({ density: "comfy", mode: "board" });
  const set = (patch) => setStateInternal(s => ({ ...s, ...patch }));
  const health = useV3Health();

  return (
    <PhoneFrame width={390} height={844} dark>
      <div style={{
        position: "absolute", inset: 0,
        paddingTop: 47,
        display: "flex", flexDirection: "column",
        background: "transparent", color: "white",
        fontFamily: "var(--font-sans)",
      }}>
        {/* sticky header — calmer than before, no rose pill, just truth row */}
        <div style={{
          padding: "9px 14px 10px",
          borderBottom: "1px solid rgba(255,255,255,.06)",
          background: "rgba(0,0,0,.5)",
          backdropFilter: "blur(12px)",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 9 }}>
            <div style={{ fontSize: 15, fontWeight: 700, letterSpacing: "-0.01em" }}>Taskboard</div>
            <span style={{ flex: 1 }}/>
            <span style={{
              fontFamily: "var(--font-mono)", fontSize: 10,
              color: "var(--text-dim)",
            }}>13 · 6 agents</span>
            <div style={{
              width: 26, height: 26, borderRadius: 999,
              background: "linear-gradient(135deg,#3b82f6,#7c3aed)",
              display: "grid", placeItems: "center",
              fontFamily: "var(--font-mono)", fontSize: 9.5, fontWeight: 700,
            }}>PP</div>
          </div>

          {/* truth strip — same numbers as desktop sub-bar */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 4 }}>
            {[
              ["Active", health.active, "#5eead4", false],
              ["Review", health.review, "#c4b5fd", health.review > 0],
              ["Stale",  health.stale,  "#fcd34d", health.stale > 0],
              ["Failed", health.failed, "#fda4af", health.failed > 0],
            ].map(([l, n, c, em]) => (
              <div key={l} style={{
                padding: "4px 7px", borderRadius: 5,
                background: em ? "rgba(255,255,255,.04)" : "transparent",
                border: `1px solid ${em ? "rgba(255,255,255,.08)" : "rgba(255,255,255,.04)"}`,
                display: "flex", alignItems: "center", gap: 5,
                opacity: !em && n === 0 ? .55 : 1,
              }}>
                <span style={{ width: 5, height: 5, borderRadius: 1, background: c,
                  boxShadow: em ? `0 0 5px ${c}` : undefined,
                }}/>
                <span style={{ fontSize: 9, color: "var(--text-dim)",
                  letterSpacing: ".12em", textTransform: "uppercase", fontWeight: 600,
                }}>{l}</span>
                <span style={{ flex: 1 }}/>
                <span style={{
                  fontFamily: "var(--font-mono)", fontSize: 11.5, fontWeight: 700,
                  color: em ? "white" : "var(--text-soft)",
                }}>{n}</span>
              </div>
            ))}
          </div>

          {/* unified control bar — compact */}
          <div style={{ marginTop: 9 }}>
            <V3ControlBar
              state={{ ...state, truthRail: false }}
              set={(p) => set(p.density || p.mode ? p : {})}
              compact
            />
          </div>
        </div>

        <div style={{ padding: "10px 12px 0", overflow: "auto", flex: 1 }}>
          {state.mode === "board"
            ? <V3MobileBoardFeed density={state.density}/>
            : <V3MobileTriageFeed density={state.density}/>
          }
        </div>

        <BottomTabBar active="tasks"/>
      </div>
    </PhoneFrame>
  );
}

function V3MobileBoardFeed({ density }) {
  return (
    <>
      {/* Incident pin — only if needed */}
      <div style={{
        padding: 10, borderRadius: 10,
        background: "linear-gradient(180deg, rgba(244,63,94,.12) 0%, rgba(244,63,94,.04) 100%)",
        border: "1px solid rgba(244,63,94,.30)",
        marginBottom: 12,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 5 }}>
          <span style={{ width: 5, height: 5, borderRadius: 1, background: "#f43f5e",
            boxShadow: "0 0 6px #f43f5e",
          }}/>
          <span style={{ fontSize: 9.5, fontWeight: 700, color: "#fda4af",
            letterSpacing: ".18em", textTransform: "uppercase",
          }}>Needs operator now</span>
        </div>
        <div style={{ fontSize: 12.5, color: "white", fontWeight: 600, lineHeight: 1.35, marginBottom: 8 }}>
          MC-T17 · payload schema rejected operatorLock
        </div>
        <div style={{ display: "flex", gap: 6 }}>
          <V3Btn primary tone="rose">Triage</V3Btn>
          <V3Btn>Logs</V3Btn>
        </div>
      </div>

      {/* lanes — vertical stack, dense-aware */}
      {[
        { id: "active", subset: V3_TASKS_BY_LANE("active") },
        { id: "review", subset: V3_TASKS_BY_LANE("review") },
        { id: "assigned", subset: V3_TASKS_BY_LANE("assigned") },
        { id: "ready", subset: V3_TASKS_BY_LANE("ready") },
      ].map(({ id, subset }) => (
        <React.Fragment key={id}>
          <div style={{ marginBottom: 7 }}>
            <V3LaneHeader lane={V3_LANES.find(l=>l.id===id)} count={subset.length}/>
          </div>
          <div style={{
            display: "flex", flexDirection: "column",
            gap: density === "dense" ? 5 : 7, marginBottom: 14,
          }}>
            {subset.map(t => <V3Card key={t.id} task={t} dense={density === "dense"}/>)}
          </div>
        </React.Fragment>
      ))}
      <div style={{ height: 60 }}/>
    </>
  );
}

function V3MobileTriageFeed({ density }) {
  const incidents = V3_TASKS.filter(t =>
    t.status === "failed" || t.status === "blocked" || t.status === "noheartbeat"
  );
  const review = V3_TASKS.filter(t => t.status === "review");
  return (
    <>
      <V3TriageBlock title="Incidents" tone="rose" count={incidents.length}>
        <div style={{ display: "flex", flexDirection: "column", gap: 7, marginBottom: 12 }}>
          {incidents.map(t => <V3Card key={t.id} task={t} dense={density === "dense"}/>)}
        </div>
      </V3TriageBlock>
      <V3TriageBlock title="Review needed" tone="violet" count={review.length}>
        <div style={{ display: "flex", flexDirection: "column", gap: 7, marginBottom: 12 }}>
          {review.map(t => <V3Card key={t.id} task={t} dense={density === "dense"}/>)}
        </div>
      </V3TriageBlock>
      <V3TriageBlock title="Quiet lanes" tone="zinc">
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 7, marginBottom: 12 }}>
          {[
            { id: "draft",    tasks: V3_TASKS_BY_LANE("draft") },
            { id: "ready",    tasks: V3_TASKS_BY_LANE("ready") },
            { id: "active",   tasks: V3_TASKS_BY_LANE("active") },
            { id: "done",     tasks: V3_TASKS_BY_LANE("done") },
          ].map(q => <V3QuietChip key={q.id} laneId={q.id} tasks={q.tasks}/>)}
        </div>
      </V3TriageBlock>
      <div style={{ height: 60 }}/>
    </>
  );
}

Object.assign(window, {
  V3FinalDesktop, V3MobileFinal,
  V3ControlBar, V3Seg, V3Toggle,
  useV3Health,
});
