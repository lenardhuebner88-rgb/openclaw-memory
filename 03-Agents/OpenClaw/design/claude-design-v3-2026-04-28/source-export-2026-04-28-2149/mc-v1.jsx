// V1 — Evolutionary refinement. Same mental model as current taskboard,
// re-organized for thumb reach: sticky hero strip, horizontal lane chips,
// denser cards with tone-washed action row, FAB + bottom tab bar.

function V1TaskCard({ task }) {
  const es = MC.execState[task.state] || MC.execState.queued;
  const pr = MC.priority[task.priority] || MC.priority.medium;
  const isDone = task.state === "done";
  const live = task.state === "dispatched-active";
  const agent = MC.agents[task.agent];
  const needsRetry = task.state === "blocked" || task.callout;

  return (
    <div style={{
      border: "1px solid rgba(255,255,255,.08)", background: "var(--panel-card)",
      borderRadius: 14, padding: 12, boxShadow: "0 4px 24px rgba(0,0,0,.35)",
    }}>
      {/* top row: title + agent */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 8 }}>
        <h3 style={{
          margin: 0, fontSize: 13.5, fontWeight: 600, color: "white",
          lineHeight: 1.3, letterSpacing: "-0.005em", textWrap: "pretty",
        }}>{task.title}</h3>
        <AgentBadge name={task.agent} size="sm"/>
      </div>

      {/* pills row */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: 5, marginTop: 8 }}>
        {task.age !== "—" && (
          <Pill tone="zinc" size="sm" style={{ fontFamily: "var(--font-mono)", letterSpacing: 0, textTransform: "none" }}>
            <span style={{ fontSize: 9 }}>⏱</span>{task.age}
          </Pill>
        )}
        <Pill tone={es.tone} size="sm" dot live={live}>{es.icon} {es.label}</Pill>
        {!isDone && <Pill tone={pr.tone} size="sm">{pr.label}</Pill>}
      </div>

      {/* meta row (middot separators, tabular nums) */}
      {task.meta && (
        <MicroMeta style={{ marginTop: 8 }}>{task.meta}</MicroMeta>
      )}

      {/* callout */}
      {task.callout && (
        <div style={{
          marginTop: 8, borderRadius: 8, padding: "7px 9px",
          border: "1px solid rgba(244,63,94,.20)", background: "rgba(244,63,94,.10)",
          color: "#fecdd3", fontSize: 11.5, lineHeight: 1.4,
          display: "flex", alignItems: "center", gap: 8,
        }}>
          <span style={{ fontSize: 12 }}>⛔</span>
          <span style={{ flex: 1 }}>{task.callout}</span>
        </div>
      )}
      {task.ruleId && (
        <MicroMeta style={{ marginTop: 4, fontSize: 10, color: "var(--text-dim)" }}>
          {task.ruleId}
        </MicroMeta>
      )}

      {/* action row — tone-washed pill buttons, 44px+ tap targets */}
      {!isDone && (
        <div style={{ display: "flex", gap: 6, marginTop: 10 }}>
          <button style={actBtn(false)}>Details</button>
          <button style={actBtn(true, needsRetry ? "retry" : "dispatch")}>
            {needsRetry ? "◆ Retry" : "◆ Dispatch"}
          </button>
        </div>
      )}
    </div>
  );
}

function actBtn(primary, kind) {
  const base = {
    all: "unset", cursor: "pointer", flex: 1, textAlign: "center",
    fontSize: 12.5, fontWeight: 500, minHeight: 44,
    display: "inline-flex", alignItems: "center", justifyContent: "center",
    borderRadius: 999, border: "1px solid",
    letterSpacing: ".02em",
  };
  if (primary) {
    return {
      ...base,
      borderColor: "var(--accent-border)",
      background: "var(--accent-wash)",
      color: "var(--accent-text)",
      boxShadow: "0 0 12px rgba(124,58,237,.25)",
    };
  }
  return { ...base, borderColor: "rgba(255,255,255,.10)", background: "rgba(255,255,255,.04)", color: "var(--text)" };
}

function V1LaneChip({ lane, active, onClick }) {
  return (
    <button onClick={onClick} style={{
      all: "unset", cursor: "pointer", flexShrink: 0,
      display: "inline-flex", alignItems: "center", gap: 6,
      padding: "8px 12px", borderRadius: 999,
      border: active ? "1px solid var(--accent-border)" : "1px solid var(--border)",
      background: active ? "var(--accent-wash)" : "var(--panel)",
      color: active ? "var(--accent-text)" : "var(--text-soft)",
      fontSize: 10.5, letterSpacing: ".18em", textTransform: "uppercase", fontWeight: 600,
      minHeight: 36,
      boxShadow: active ? "0 0 12px rgba(124,58,237,.25)" : undefined,
      scrollSnapAlign: "start",
    }}>
      {lane.name}
      <span className="mc-num" style={{
        fontFamily: "var(--font-mono)", fontSize: 10, letterSpacing: 0, fontWeight: 700,
        padding: "1px 5px", borderRadius: 5,
        background: active ? "rgba(124,58,237,.25)" : "rgba(255,255,255,.06)",
        color: active ? "#e9d5ff" : "var(--text)",
      }}>{String(lane.count).padStart(2,"0")}</span>
    </button>
  );
}

function V1Screen() {
  const [active, setActive] = useState("needs");
  const [nav, setNav] = useState("tasks");
  const tasks = MOBILE_TASKS.filter(t => t.lane === active);

  return (
    <div style={{
      position: "absolute", inset: 0, paddingTop: 47,
      overflow: "hidden", display: "flex", flexDirection: "column",
    }}>
      {/* sticky top: brand + title + hero strip */}
      <div style={{
        padding: "10px 16px 0",
        background: "rgba(15,15,15,.95)", backdropFilter: "blur(6px)",
        borderBottom: "1px solid var(--border)",
        flexShrink: 0,
      }}>
        {/* brand row */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{
              width: 30, height: 30, borderRadius: 8,
              border: "1px solid var(--accent-border)", background: "var(--accent-wash)",
              color: "#c4b5fd", display: "inline-flex", alignItems: "center", justifyContent: "center",
              fontSize: 16, boxShadow: "0 0 12px rgba(124,58,237,.25)",
            }}>⚙</div>
            <div style={{ lineHeight: 1.05 }}>
              <div style={{ fontSize: 9.5, letterSpacing: ".26em", color: "var(--text)", fontWeight: 500 }}>MISSION<br/>CONTROL</div>
            </div>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{
              display: "inline-flex", alignItems: "center", gap: 5,
              padding: "3px 8px", borderRadius: 999,
              border: "1px solid rgba(34,197,94,.20)", background: "rgba(34,197,94,.10)",
              color: "#bbf7d0", fontSize: 9, letterSpacing: ".14em", fontWeight: 700, textTransform: "uppercase",
            }}>
              <span style={{ width: 6, height: 6, borderRadius: 999, background: "#22c55e", boxShadow: "0 0 6px #22c55e", animation: "mc-live-glow 2s ease-in-out infinite" }}/>
              LIVE
            </div>
            <AgentBadge name="pieter_pan" size="sm"/>
          </div>
        </div>

        {/* title */}
        <div style={{ marginTop: 12 }}>
          <Eyebrow style={{ marginBottom: 4 }}>TASK OPERATIONS</Eyebrow>
          <h1 style={{
            margin: 0, fontSize: 22, fontWeight: 600, color: "white",
            letterSpacing: "-0.02em", lineHeight: 1.15,
          }}>Taskboard</h1>
        </div>

        {/* HERO GLANCE STRIP — the "is everything ok" answer */}
        <div style={{
          marginTop: 10, marginBottom: 10,
          border: "1px solid rgba(244,63,94,.25)",
          background: "linear-gradient(180deg, rgba(244,63,94,.06), rgba(244,63,94,.02))",
          borderRadius: 12, padding: "10px 12px",
          display: "grid", gridTemplateColumns: "auto 1fr auto", gap: 10, alignItems: "center",
        }}>
          <div style={{
            width: 38, height: 38, borderRadius: 10,
            border: "1px solid rgba(244,63,94,.3)", background: "rgba(244,63,94,.1)",
            color: "#fecdd3", display: "inline-flex", alignItems: "center", justifyContent: "center",
            fontSize: 18, fontWeight: 700, fontFamily: "var(--font-mono)",
          }}>3</div>
          <div style={{ minWidth: 0 }}>
            <div style={{ fontSize: 13, color: "white", fontWeight: 600, lineHeight: 1.25 }}>
              3 stalled · 1 retry ready
            </div>
            <MicroMeta style={{ fontSize: 10.5, marginTop: 1 }}>
              19 active · 117 dispatched · confidence 0%
            </MicroMeta>
          </div>
          <button style={{
            all: "unset", cursor: "pointer", minHeight: 32, padding: "0 10px",
            borderRadius: 999, fontSize: 11, fontWeight: 600,
            border: "1px solid var(--accent-border)", background: "var(--accent-wash)", color: "var(--accent-text)",
            boxShadow: "0 0 12px rgba(124,58,237,.25)",
            letterSpacing: ".04em",
          }}>Open →</button>
        </div>

        {/* lane chip rail */}
        <div style={{
          display: "flex", gap: 6, overflowX: "auto", scrollSnapType: "x mandatory",
          margin: "0 -16px", padding: "0 16px 12px",
          scrollbarWidth: "none",
        }}>
          {MOBILE_LANES.map(l => (
            <V1LaneChip key={l.id} lane={l} active={active === l.id} onClick={() => setActive(l.id)}/>
          ))}
        </div>
      </div>

      {/* scrolling lane body */}
      <div style={{
        flex: 1, overflowY: "auto", padding: "12px 12px 120px",
        display: "flex", flexDirection: "column", gap: 10,
      }} className="mc-stagger">
        {tasks.map(t => <V1TaskCard key={t.id} task={t}/>)}
        {tasks.length === 0 && (
          <div style={{
            border: "1px dashed rgba(255,255,255,.10)", borderRadius: 14,
            padding: "28px 16px", textAlign: "center", marginTop: 24,
          }}>
            <div style={{
              width: 32, height: 32, borderRadius: 10, margin: "0 auto 8px",
              border: "1px solid var(--accent-border)", background: "var(--accent-wash)",
              color: "#c4b5fd", display: "inline-flex", alignItems: "center", justifyContent: "center",
            }}>✓</div>
            <div style={{ fontSize: 13, color: "white", marginBottom: 4 }}>Nothing urgent is stuck right now.</div>
            <MicroMeta>Pull the next ready task or create a new one.</MicroMeta>
          </div>
        )}
      </div>

      {/* FAB — command palette */}
      <button style={{
        all: "unset", cursor: "pointer",
        position: "absolute", right: 16, bottom: 96,
        width: 52, height: 52, borderRadius: 18,
        border: "1px solid var(--accent-border)",
        background: "linear-gradient(180deg, rgba(124,58,237,.35), rgba(124,58,237,.15))",
        color: "white",
        display: "inline-flex", alignItems: "center", justifyContent: "center",
        fontSize: 22, fontWeight: 300,
        boxShadow: "0 0 20px rgba(124,58,237,.45), 0 8px 24px rgba(0,0,0,.4)",
        zIndex: 25,
      }}>⌘</button>

      <BottomTabBar active={nav} onNav={setNav}/>
    </div>
  );
}

Object.assign(window, { V1TaskCard, V1LaneChip, V1Screen });
