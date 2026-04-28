// V3 — Recommended hybrid (Mobile + Desktop) + States gallery.
// The recommendation = V3B board chrome (calmer, drawer-driven) + V3C incident strip
// + V3A right-rail truth panel optional. Slim card is the universal atom.

/* ════════════════════════════════════════════════════════════════
   MOBILE — 390 × 844 phone frame
   ════════════════════════════════════════════════════════════════ */

function V3Mobile() {
  return (
    <PhoneFrame width={390} height={844} dark>
      <div style={{
        position: "absolute", inset: 0,
        paddingTop: 47,
        display: "flex", flexDirection: "column",
        background: "transparent", color: "white",
        fontFamily: "var(--font-sans)",
      }}>
        {/* sticky header */}
        <div style={{
          padding: "10px 16px 12px",
          borderBottom: "1px solid rgba(255,255,255,.06)",
          background: "rgba(0,0,0,.45)",
          backdropFilter: "blur(12px)",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
            <div style={{
              fontSize: 16, fontWeight: 700, letterSpacing: "-0.005em",
            }}>Taskboard</div>
            <span style={{ flex: 1 }}/>
            <span style={{
              padding: "3px 9px", borderRadius: 999,
              background: "rgba(244,63,94,.16)", border: "1px solid rgba(244,63,94,.32)",
              color: "#fda4af", fontSize: 9.5, fontWeight: 700,
              letterSpacing: ".14em", textTransform: "uppercase",
            }}>3 needs op</span>
            <div style={{
              width: 28, height: 28, borderRadius: 999,
              background: "linear-gradient(135deg,#3b82f6,#7c3aed)",
              display: "grid", placeItems: "center",
              fontFamily: "var(--font-mono)", fontSize: 10, fontWeight: 700,
            }}>PP</div>
          </div>

          {/* truth strip — same numbers as drawer/dashboard, no false healthy */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 5 }}>
            {[
              ["Active",  "2", "#5eead4"],
              ["Review",  "1", "#c4b5fd"],
              ["Stale",   "1", "#fcd34d"],
              ["Failed",  "2", "#fda4af"],
            ].map(([l, n, c]) => (
              <div key={l} style={{
                padding: "5px 7px", borderRadius: 6,
                background: "rgba(255,255,255,.03)",
                border: "1px solid rgba(255,255,255,.06)",
                display: "flex", alignItems: "center", gap: 5,
              }}>
                <span style={{ width: 5, height: 5, borderRadius: 1, background: c }}/>
                <span style={{ fontSize: 9, color: "var(--text-dim)",
                  letterSpacing: ".12em", textTransform: "uppercase", fontWeight: 600,
                }}>{l}</span>
                <span style={{ flex: 1 }}/>
                <span style={{
                  fontFamily: "var(--font-mono)", fontSize: 12, fontWeight: 700, color: "white",
                }}>{n}</span>
              </div>
            ))}
          </div>

          {/* lane chips */}
          <div style={{
            marginTop: 12, display: "flex", gap: 5, overflow: "hidden",
          }}>
            {V3_LANES.slice(0, 5).map((l, i) => {
              const t = V3_TONE[l.tone];
              const active = i === 3; // active lane focused
              return (
                <div key={l.id} style={{
                  padding: "5px 9px", borderRadius: 6,
                  background: active ? "rgba(255,255,255,.08)" : "transparent",
                  border: `1px solid ${active ? "rgba(255,255,255,.14)" : t.border}`,
                  display: "flex", alignItems: "center", gap: 5,
                  flexShrink: 0,
                }}>
                  <span style={{ width: 5, height: 5, borderRadius: 1, background: t.solid }}/>
                  <span style={{
                    fontSize: 10, fontWeight: 600,
                    color: active ? "white" : t.fg,
                    letterSpacing: ".10em", textTransform: "uppercase",
                  }}>{l.name}</span>
                  <span style={{
                    fontFamily: "var(--font-mono)", fontSize: 10, fontWeight: 700,
                    color: active ? "white" : "var(--text-dim)",
                  }}>{V3_TASKS_BY_LANE(l.id).length}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* incident card pinned at top of feed */}
        <div style={{ padding: "12px 14px 10px", overflow: "auto", flex: 1 }}>
          <div style={{
            padding: 10, borderRadius: 10,
            background: "linear-gradient(180deg, rgba(244,63,94,.12) 0%, rgba(244,63,94,.04) 100%)",
            border: "1px solid rgba(244,63,94,.30)",
            marginBottom: 12,
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
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

          <div style={{ marginBottom: 8 }}>
            <V3LaneHeader lane={V3_LANES.find(l=>l.id==="active")} count={2}/>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 7, marginBottom: 16 }}>
            {V3_TASKS_BY_LANE("active").map(t => <V3Card key={t.id} task={t}/>)}
          </div>

          <div style={{ marginBottom: 8 }}>
            <V3LaneHeader lane={V3_LANES.find(l=>l.id==="review")} count={1}/>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 7, marginBottom: 16 }}>
            {V3_TASKS_BY_LANE("review").map(t => <V3Card key={t.id} task={t}/>)}
          </div>

          <div style={{ marginBottom: 8 }}>
            <V3LaneHeader lane={V3_LANES.find(l=>l.id==="assigned")} count={1}/>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 7, marginBottom: 80 }}>
            {V3_TASKS_BY_LANE("assigned").map(t => <V3Card key={t.id} task={t}/>)}
          </div>
        </div>

        <BottomTabBar active="tasks"/>
      </div>
    </PhoneFrame>
  );
}

/* Mobile sheet (full-screen drawer) */
function V3MobileSheet() {
  return (
    <PhoneFrame width={390} height={844} dark>
      <div style={{
        position: "absolute", inset: 0, paddingTop: 47,
        display: "flex", flexDirection: "column", background: "transparent",
        color: "white", fontFamily: "var(--font-sans)",
      }}>
        {/* dimmed back */}
        <div style={{
          position: "absolute", inset: 0, top: 47,
          background: "rgba(0,0,0,.5)", backdropFilter: "blur(6px)",
        }}/>
        {/* sheet */}
        <div style={{
          position: "absolute", left: 0, right: 0, bottom: 0,
          height: 700,
          background: "#0a0a0d",
          borderTop: "1px solid rgba(255,255,255,.10)",
          borderRadius: "20px 20px 0 0",
          display: "flex", flexDirection: "column",
          boxShadow: "0 -24px 48px rgba(0,0,0,.6)",
        }}>
          <div style={{ display: "grid", placeItems: "center", padding: "10px 0 4px" }}>
            <span style={{ width: 36, height: 4, borderRadius: 2, background: "rgba(255,255,255,.18)" }}/>
          </div>
          <V3DrawerContent task={V3_DETAIL_TASK} variant="sheet"/>
        </div>
      </div>
    </PhoneFrame>
  );
}

/* ════════════════════════════════════════════════════════════════
   DESKTOP RECOMMENDED — V3B chrome with V3C incident strip
   ════════════════════════════════════════════════════════════════ */

function V3RecommendedDesktop() {
  // Same as V3B but without the open drawer — clean state
  return (
    <div style={{
      width: V3B_W, height: V3B_H,
      background: "#0a0a0d", color: "white",
      fontFamily: "var(--font-sans)",
      display: "flex", flexDirection: "column", overflow: "hidden",
    }}>
      <V3BTopChrome/>
      <div style={{ flex: 1, display: "grid", gridTemplateColumns: "188px 1fr", minHeight: 0 }}>
        <V3BSidebar/>
        <V3BMainNoDrawer/>
      </div>
    </div>
  );
}

function V3BMainNoDrawer() {
  const primary = V3_LANES.filter(l => ["draft","ready","assigned","active","review"].includes(l.id));
  const closed  = V3_LANES.filter(l => ["done","failed"].includes(l.id));
  return (
    <div style={{ display: "flex", flexDirection: "column", minHeight: 0, background: "#08080a" }}>
      <V3BIncidentStrip/>
      <div style={{
        flex: 1, padding: "12px 14px 14px",
        display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 10,
        minHeight: 0,
      }}>
        {primary.map(lane => <V3BLane key={lane.id} lane={lane}/>)}
      </div>
      <V3BClosedFooter lanes={closed}/>
    </div>
  );
}

/* ════════════════════════════════════════════════════════════════
   STATES GALLERY — 1 component, 9 states
   ════════════════════════════════════════════════════════════════ */

const STATES_W = 320, STATES_H = 360;

function StateLane({ kind }) {
  return (
    <div style={{
      width: STATES_W, height: STATES_H,
      padding: 14,
      background: "#0a0a0d",
      border: "1px solid rgba(255,255,255,.06)",
      borderRadius: 10,
      color: "white", fontFamily: "var(--font-sans)",
      display: "flex", flexDirection: "column",
      boxSizing: "border-box",
    }}>
      <V3LaneHeader
        lane={V3_LANES.find(l=>l.id===(kind.lane || "active")) || V3_LANES[0]}
        count={kind.count ?? 0}
      />
      <div style={{ flex: 1, marginTop: 10, minHeight: 0,
        display: "flex", flexDirection: "column", gap: 6,
      }}>
        {kind.render()}
      </div>
    </div>
  );
}

function StateLoading() {
  return [0,1,2].map(i => (
    <div key={i} style={{
      padding: 12,
      background: "#0f0f10",
      border: "1px solid rgba(255,255,255,.06)",
      borderRadius: 8,
      display: "flex", flexDirection: "column", gap: 8,
    }}>
      <Skel w="65%" h={11}/>
      <Skel w="38%" h={9}/>
      <Skel w="80%" h={9}/>
    </div>
  ));
}

function Skel({ w, h }) {
  return (
    <div style={{
      width: w, height: h, borderRadius: 3,
      background: "linear-gradient(90deg, rgba(255,255,255,.04) 0%, rgba(255,255,255,.10) 50%, rgba(255,255,255,.04) 100%)",
      backgroundSize: "200% 100%",
      animation: "mc-skel 1.4s linear infinite",
    }}/>
  );
}

function StateEmpty({ lane }) {
  const t = V3_TONE[lane.tone];
  return (
    <div style={{
      flex: 1, display: "grid", placeItems: "center",
      padding: 20, borderRadius: 8,
      border: `1px dashed ${t.border}`,
      textAlign: "center",
    }}>
      <div>
        <div style={{ fontSize: 22, color: t.fg, opacity: .6, marginBottom: 8 }}>—</div>
        <div style={{ fontSize: 12, color: "var(--text-soft)", fontWeight: 500, marginBottom: 4 }}>
          No tasks in {lane.name.toLowerCase()}
        </div>
        <div style={{ fontSize: 10.5, color: "var(--text-dim)", lineHeight: 1.5, maxWidth: 220 }}>
          {lane.id === "draft" && "When operator drafts a task, it'll wait here for safe dispatch."}
          {lane.id === "active" && "Nothing running. All accepted tasks have results or moved to review."}
          {lane.id === "review" && "All caught up. Review queue is clear."}
          {lane.id === "failed" && "Nothing has failed in the last 24h. ✓"}
          {!["draft","active","review","failed"].includes(lane.id) && "Lane is empty."}
        </div>
      </div>
    </div>
  );
}

function StateError() {
  return (
    <div style={{
      flex: 1, display: "grid", placeItems: "center",
      padding: 20, borderRadius: 8,
      background: "rgba(244,63,94,.06)",
      border: "1px solid rgba(244,63,94,.22)",
      textAlign: "center",
    }}>
      <div>
        <div style={{
          width: 30, height: 30, margin: "0 auto 10px",
          borderRadius: 6, background: "rgba(244,63,94,.16)",
          display: "grid", placeItems: "center",
          color: "#fda4af", fontSize: 16, fontWeight: 700,
        }}>!</div>
        <div style={{ fontSize: 12, color: "white", fontWeight: 600, marginBottom: 4 }}>
          Couldn't load lane
        </div>
        <div style={{ fontSize: 10.5, color: "#fda4af", lineHeight: 1.5,
          fontFamily: "var(--font-mono)", marginBottom: 10,
        }}>
          mc_taskboard_fetch · 503 · upstream timeout
        </div>
        <V3Btn primary tone="rose">Retry</V3Btn>
      </div>
    </div>
  );
}

/* ════════════════════════════════════════════════════════════════
   EXPORT
   ════════════════════════════════════════════════════════════════ */

Object.assign(window, {
  V3Mobile, V3MobileSheet,
  V3RecommendedDesktop,
  StateLane, StateLoading, StateEmpty, StateError, Skel,
  STATES_W, STATES_H,
});
