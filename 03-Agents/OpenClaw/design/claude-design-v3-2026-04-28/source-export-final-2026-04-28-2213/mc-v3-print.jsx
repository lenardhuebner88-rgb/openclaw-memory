// V3 Print layout — static, paged, no pan/zoom canvas.
// Each "page" is a fixed-size container that fits within a 1600×1000 print frame.

function PrintPage({ title, subtitle, children, padded = true }) {
  return (
    <section className="print-page" style={{
      width: 1600,
      minHeight: 1000,
      padding: padded ? "40px 48px" : 0,
      background: "#0a0a0d",
      color: "white",
      fontFamily: "var(--font-sans)",
      boxSizing: "border-box",
      breakAfter: "page",
      breakInside: "avoid",
      pageBreakAfter: "always",
      display: "flex", flexDirection: "column",
    }}>
      {(title || subtitle) && (
        <div style={{ marginBottom: 22 }}>
          {title && (
            <div style={{ fontSize: 22, fontWeight: 700, letterSpacing: -0.3, color: "white" }}>
              {title}
            </div>
          )}
          {subtitle && (
            <div style={{ fontSize: 13, color: "var(--text-soft)", marginTop: 4, lineHeight: 1.5 }}>
              {subtitle}
            </div>
          )}
        </div>
      )}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 24 }}>
        {children}
      </div>
    </section>
  );
}

function PrintLabel({ children }) {
  return (
    <div style={{
      fontSize: 11, fontWeight: 600, color: "var(--text-soft)",
      letterSpacing: ".18em", textTransform: "uppercase", marginBottom: 8,
    }}>{children}</div>
  );
}

function V3Print() {
  return (
    <div style={{ background: "#0a0a0d" }}>
      {/* COVER */}
      <PrintPage padded>
        <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center" }}>
          <div style={{
            fontSize: 11, fontWeight: 700, color: "#c4b5fd",
            letterSpacing: ".28em", textTransform: "uppercase", marginBottom: 18,
          }}>Mission Control · Taskboard V3</div>
          <div style={{ fontSize: 64, fontWeight: 700, lineHeight: 1.05, letterSpacing: -1.2, marginBottom: 14 }}>
            Market-ready<br/>operations UI.
          </div>
          <div style={{ fontSize: 18, color: "var(--text-soft)", lineHeight: 1.5, maxWidth: 880 }}>
            Three V3 directions, a recommended hybrid, drawer/modal/sheet, full state taxonomy, and a Codex handoff spec.
          </div>
          <div style={{ marginTop: 36, display: "flex", gap: 32, flexWrap: "wrap" }}>
            {[
              ["Lanes",     "7"],
              ["Statuses",  "11"],
              ["States",    "9"],
              ["Variants",  "3"],
              ["Surfaces",  "Mobile · Desktop"],
            ].map(([k, v]) => (
              <div key={k}>
                <div style={{ fontSize: 11, color: "var(--text-dim)", letterSpacing: ".18em",
                  textTransform: "uppercase", fontWeight: 600,
                }}>{k}</div>
                <div style={{ fontSize: 28, fontWeight: 600, fontFamily: "var(--font-mono)" }}>{v}</div>
              </div>
            ))}
          </div>
        </div>
      </PrintPage>

      {/* V3A */}
      <PrintPage title="V3A · Dense Operator Cockpit"
        subtitle="Maximum signal density. All 7 lanes side-by-side. Persistent right-rail Truth panel. ⌘K-driven. Best for power users.">
        <div style={{ transform: "scale(0.82)", transformOrigin: "top left", width: 1440, height: 900 }}>
          <V3ADesktop/>
        </div>
      </PrintPage>

      {/* V3B */}
      <PrintPage title="V3B · Balanced Kanban + Drawer"
        subtitle="5 primary lanes. Done + Failed compressed in footer. Drawer-driven detail. The recommended chassis.">
        <div style={{ transform: "scale(0.82)", transformOrigin: "top left", width: 1440, height: 900 }}>
          <V3BDesktop/>
        </div>
      </PrintPage>

      {/* V3C */}
      <PrintPage title="V3C · Incident-First Triage"
        subtitle="Inverts the kanban: failures, stale, review on TOP. Healthy work compressed. Use as a mode on top of V3B.">
        <div style={{ transform: "scale(0.82)", transformOrigin: "top left", width: 1440, height: 900 }}>
          <V3CDesktop/>
        </div>
      </PrintPage>

      {/* RECOMMENDED */}
      <PrintPage title="Recommended hybrid"
        subtitle="V3B chrome + V3C incident strip (only when something is wrong) + V3A right-rail as opt-in. Slim card universal.">
        <div style={{ transform: "scale(0.82)", transformOrigin: "top left", width: 1440, height: 900 }}>
          <V3RecommendedDesktop/>
        </div>
      </PrintPage>

      {/* MOBILE */}
      <PrintPage title="Mobile · 390 × 844"
        subtitle="Same atoms, vertical stack. Incident card pins. Drawer becomes a bottom sheet.">
        <div style={{ display: "flex", gap: 56, alignItems: "flex-start", justifyContent: "center" }}>
          <div>
            <PrintLabel>Primary feed</PrintLabel>
            <V3Mobile/>
          </div>
          <div>
            <PrintLabel>Details bottom sheet</PrintLabel>
            <V3MobileSheet/>
          </div>
        </div>
      </PrintPage>

      {/* DRAWER */}
      <PrintPage title="Details drawer (desktop · 460 wide)"
        subtitle="Truth → Lifecycle → Receipts → Session → Acceptance → Events → Relations → Result → Raw. Same content powers modal + mobile sheet.">
        <div style={{ display: "flex", gap: 28, alignItems: "flex-start" }}>
          <div style={{
            width: 460, height: 900,
            background: "#0a0a0d",
            border: "1px solid rgba(255,255,255,.10)",
            flexShrink: 0,
          }}>
            <V3DrawerContent task={V3_DETAIL_TASK} variant="drawer"/>
          </div>
          <div style={{ flex: 1, paddingTop: 8 }}>
            <PrintLabel>Why truth-first</PrintLabel>
            <p style={pSty}>The current detail leads with prompt and summary text. V3 leads with what's true and what to do next. Long context is below the fold.</p>
            <PrintLabel>Receipt chain</PrintLabel>
            <p style={pSty}>Latest first, full chain. The failed result is the first thing you read. Operator can scroll to draft if archaeology is needed.</p>
            <PrintLabel>Raw metadata</PrintLabel>
            <p style={pSty}>Last section, collapsible. Power users get it; everyone else doesn't see noise.</p>
            <PrintLabel>Three host shells, one body</PrintLabel>
            <p style={pSty}>Drawer (desktop right-side, 460px), Modal (centered focused, 720px), Sheet (mobile bottom). Body content is the same component — host shell varies.</p>
          </div>
        </div>
      </PrintPage>

      {/* STATES PAGE 1 */}
      <PrintPage title="States · 1 of 2"
        subtitle="Loading · empty · error · active healthy · stale-no-heartbeat (false progress)">
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 18 }}>
          <div><PrintLabel>Loading</PrintLabel>
            <StateLane kind={{ lane: "active", count: 0, render: () => <StateLoading/> }}/></div>
          <div><PrintLabel>Empty (review)</PrintLabel>
            <StateLane kind={{ lane: "review", count: 0,
              render: () => <StateEmpty lane={V3_LANES.find(l=>l.id==="review")}/> }}/></div>
          <div><PrintLabel>Error · fetch failed</PrintLabel>
            <StateLane kind={{ lane: "active", count: 0, render: () => <StateError/> }}/></div>
          <div><PrintLabel>Active · healthy</PrintLabel>
            <StateLane kind={{ lane: "active", count: 2,
              render: () => V3_TASKS_BY_LANE("active").map(t => <V3Card key={t.id} task={t}/>) }}/></div>
          <div><PrintLabel>No heartbeat (false progress)</PrintLabel>
            <StateLane kind={{ lane: "assigned", count: 1,
              render: () => V3_TASKS.filter(t=>t.status==="noheartbeat").map(t => <V3Card key={t.id} task={t}/>) }}/></div>
          <div><PrintLabel>Failed · needs review</PrintLabel>
            <StateLane kind={{ lane: "failed", count: 2,
              render: () => V3_TASKS_BY_LANE("failed").map(t => <V3Card key={t.id} task={t}/>) }}/></div>
        </div>
      </PrintPage>

      {/* STATES PAGE 2 */}
      <PrintPage title="States · 2 of 2"
        subtitle="Review · draft · done">
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 18 }}>
          <div><PrintLabel>Review needed</PrintLabel>
            <StateLane kind={{ lane: "review", count: 1,
              render: () => V3_TASKS_BY_LANE("review").map(t => <V3Card key={t.id} task={t}/>) }}/></div>
          <div><PrintLabel>Draft · waiting dispatch</PrintLabel>
            <StateLane kind={{ lane: "draft", count: 2,
              render: () => V3_TASKS_BY_LANE("draft").map(t => <V3Card key={t.id} task={t}/>) }}/></div>
          <div><PrintLabel>Done · with result</PrintLabel>
            <StateLane kind={{ lane: "done", count: 3,
              render: () => V3_TASKS_BY_LANE("done").map(t => <V3Card key={t.id} task={t}/>) }}/></div>
        </div>
      </PrintPage>

      {/* HANDOFF */}
      <PrintPage padded={false}>
        <div style={{
          padding: 40,
          background: "#fffaf0",
          color: "#1a1410",
          minHeight: 1000,
          boxSizing: "border-box",
        }}>
          <V3HandoffPanel/>
        </div>
      </PrintPage>
    </div>
  );
}

const pSty = {
  fontSize: 13, color: "var(--text-soft)", lineHeight: 1.55, marginTop: 0, marginBottom: 18,
};

Object.assign(window, { V3Print, PrintPage, PrintLabel });
