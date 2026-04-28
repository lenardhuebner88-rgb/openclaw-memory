// V3C — Incident-first Triage Board (DESKTOP)
// Inverts the kanban: failures, stale, review on TOP. Healthy active/done compressed below.
// Designed for: incident commander / on-call. Maximize signal for what is broken.
// Frame: 1440 × 900.

const V3C_W = 1440, V3C_H = 900;

function V3CDesktop() {
  return (
    <div style={{
      width: V3C_W, height: V3C_H,
      background: "#08080a", color: "white",
      fontFamily: "var(--font-sans)",
      display: "flex", flexDirection: "column",
      overflow: "hidden",
    }}>
      {/* compact ribbon */}
      <div style={{
        height: 44, padding: "0 18px",
        display: "flex", alignItems: "center", gap: 12,
        borderBottom: "1px solid rgba(255,255,255,.06)",
        background: "rgba(0,0,0,.45)",
        flexShrink: 0,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{
            width: 22, height: 22, borderRadius: 5,
            background: "linear-gradient(135deg,#f43f5e,#f59e0b)",
            display: "grid", placeItems: "center",
            fontFamily: "var(--font-mono)", fontSize: 11, fontWeight: 700, color: "#0a0a0d",
          }}>!</div>
          <div style={{ fontSize: 13, fontWeight: 600 }}>Mission Control · Triage</div>
        </div>
        <span style={{
          fontSize: 11, color: "var(--text-dim)", fontFamily: "var(--font-mono)",
          marginLeft: 6,
        }}>live · 2026-04-28 06:18</span>

        <div style={{ flex: 1 }}/>

        <div style={{ display: "flex", gap: 6 }}>
          <V3CMode label="Triage" active/>
          <V3CMode label="Board"/>
          <V3CMode label="Pipeline"/>
        </div>

        <div style={{ flex: 1 }}/>

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{
            padding: "4px 10px", borderRadius: 999,
            background: "rgba(244,63,94,.16)", border: "1px solid rgba(244,63,94,.32)",
            color: "#fda4af", fontSize: 10.5, fontWeight: 700,
            letterSpacing: ".12em", textTransform: "uppercase",
          }}>3 incidents</span>
          <span style={{
            padding: "4px 10px", borderRadius: 999,
            background: "rgba(245,158,11,.10)", border: "1px solid rgba(245,158,11,.30)",
            color: "#fcd34d", fontSize: 10.5, fontWeight: 700,
            letterSpacing: ".12em", textTransform: "uppercase",
          }}>1 stale</span>
        </div>
      </div>

      <div style={{ flex: 1, padding: 16, display: "flex", flexDirection: "column", gap: 14, overflow: "hidden" }}>
        {/* incident row — 3 large incident cards */}
        <V3CIncidentRow/>
        {/* triage groups: review · stale · accepted-no-progress */}
        <V3CTriageGroups/>
        {/* compressed healthy strip at bottom */}
        <V3CHealthyStrip/>
      </div>
    </div>
  );
}

function V3CMode({ label, active }) {
  return (
    <div style={{
      padding: "5px 12px", borderRadius: 5,
      fontSize: 11.5, fontWeight: 600,
      color: active ? "white" : "var(--text-soft)",
      background: active ? "rgba(244,63,94,.12)" : "rgba(255,255,255,.03)",
      border: `1px solid ${active ? "rgba(244,63,94,.32)" : "rgba(255,255,255,.06)"}`,
      cursor: "pointer",
    }}>{label}</div>
  );
}

function V3CIncidentRow() {
  const incidents = V3_TASKS.filter(t => t.lane === "failed" || t.id === "v3_5");
  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
        <span style={{ width: 6, height: 6, borderRadius: 1, background: "#f43f5e",
          boxShadow: "0 0 6px #f43f5e",
          animation: "mc-live-glow 2s ease-in-out infinite",
        }}/>
        <span style={{ fontSize: 10.5, fontWeight: 700, color: "#fda4af",
          letterSpacing: ".18em", textTransform: "uppercase",
        }}>Incidents · needs operator</span>
        <span style={{ fontSize: 11, color: "var(--text-dim)", marginLeft: 4 }}>
          high-signal, ordered by risk · oldest first
        </span>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 10 }}>
        {incidents.map(t => <V3CIncidentCard key={t.id} task={t}/>)}
      </div>
    </div>
  );
}

function V3CIncidentCard({ task }) {
  const s = V3_STATUS[task.status];
  const tone = s.intent === "danger" ? V3_TONE.rose : V3_TONE.amber;
  return (
    <div style={{
      padding: 12,
      borderRadius: 10,
      background: `linear-gradient(180deg, ${tone.bg} 0%, rgba(255,255,255,.02) 100%)`,
      border: `1px solid ${tone.border}`,
      display: "flex", flexDirection: "column", gap: 8,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <StatusBadge status={task.status} showIntent/>
        <PriorityBadge priority={task.priority}/>
        <span style={{ flex: 1 }}/>
        <AgentBadge name={task.agent} size="xs"/>
        <AgeTag age={task.age} stale={!!task.stale}/>
      </div>
      <div style={{
        fontSize: 14, fontWeight: 600, lineHeight: 1.35,
        color: "white",
        display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical",
        overflow: "hidden",
      }}>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 11.5,
          color: "var(--text-dim)", marginRight: 6,
        }}>{task.code}</span>
        {task.title}
      </div>
      <ReceiptDots/>
      <div style={{ fontSize: 12, lineHeight: 1.45, color: tone.fg, fontWeight: 500 }}>
        {s.intent === "danger" ? "⛔ " : "⚠ "}{task.signal}
      </div>
      <div style={{ display: "flex", gap: 6, marginTop: 2 }}>
        <V3Btn primary tone={s.intent === "danger" ? "rose" : "amber"}>Triage</V3Btn>
        <V3Btn>Logs</V3Btn>
        <V3Btn>Reassign</V3Btn>
      </div>
    </div>
  );
}

function V3CTriageGroups() {
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
      <V3CGroup title="Review needed" tone="violet" tasks={V3_TASKS.filter(t => t.status === "review")}/>
      <V3CGroup title="In progress · healthy" tone="teal"
        tasks={V3_TASKS.filter(t => t.status === "active")}/>
    </div>
  );
}

function V3CGroup({ title, tone, tasks }) {
  const t = V3_TONE[tone];
  return (
    <div style={{
      padding: 12, borderRadius: 10,
      background: "rgba(255,255,255,.02)",
      border: "1px solid rgba(255,255,255,.06)",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
        <span style={{ width: 6, height: 6, borderRadius: 1, background: t.solid,
          boxShadow: `0 0 6px ${t.solid}`,
        }}/>
        <span style={{ fontSize: 10.5, fontWeight: 700, color: t.fg,
          letterSpacing: ".18em", textTransform: "uppercase",
        }}>{title}</span>
        <span style={{
          fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-soft)",
        }}>{String(tasks.length).padStart(2,"0")}</span>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {tasks.map(task => <V3Card key={task.id} task={task} dense/>)}
      </div>
    </div>
  );
}

function V3CHealthyStrip() {
  // compress draft + ready + assigned + done into chips
  const groups = [
    { id: "draft", name: "Draft" },
    { id: "ready", name: "Ready" },
    { id: "assigned", name: "Assigned" },
    { id: "done", name: "Done today" },
  ];
  return (
    <div style={{
      padding: 12, borderRadius: 10,
      background: "rgba(255,255,255,.02)",
      border: "1px solid rgba(255,255,255,.06)",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
        <span style={{ width: 6, height: 6, borderRadius: 1, background: "#a1a1aa" }}/>
        <span style={{ fontSize: 10.5, fontWeight: 700, color: "var(--text-soft)",
          letterSpacing: ".18em", textTransform: "uppercase",
        }}>Quiet lanes · click to expand</span>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 10 }}>
        {groups.map(g => {
          const lane = V3_LANES.find(l => l.id === g.id);
          const tasks = V3_TASKS_BY_LANE(g.id);
          const t = V3_TONE[lane.tone];
          return (
            <div key={g.id} style={{
              padding: 10, borderRadius: 8,
              background: "rgba(0,0,0,.25)",
              border: `1px solid ${t.border}`,
              cursor: "pointer",
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8 }}>
                <span style={{ width: 5, height: 5, borderRadius: 1, background: t.solid }}/>
                <span style={{ fontSize: 10, fontWeight: 600, color: t.fg,
                  letterSpacing: ".16em", textTransform: "uppercase",
                }}>{g.name}</span>
                <span style={{ flex: 1 }}/>
                <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "white", fontWeight: 600 }}>
                  {String(tasks.length).padStart(2,"0")}
                </span>
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 3 }}>
                {tasks.slice(0,4).map(task => (
                  <span key={task.id} style={{
                    fontFamily: "var(--font-mono)", fontSize: 10,
                    padding: "2px 5px", borderRadius: 3,
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
            </div>
          );
        })}
      </div>
    </div>
  );
}

Object.assign(window, { V3CDesktop, V3C_W, V3C_H });
