// V3 Canvas — composes all V3 artboards with annotations + handoff spec.

const { useState: useStateCanvas } = React;

/* small annotation primitives */
function V3Note({ children, tone = "violet", title }) {
  const t = V3_TONE[tone];
  return (
    <div style={{
      padding: "10px 12px",
      background: t.bg, border: `1px solid ${t.border}`,
      borderRadius: 8, color: "white",
      fontFamily: "var(--font-sans)",
      fontSize: 12, lineHeight: 1.5,
      maxWidth: 360,
    }}>
      {title && (
        <div style={{
          fontSize: 10, fontWeight: 700, color: t.fg,
          letterSpacing: ".18em", textTransform: "uppercase", marginBottom: 4,
        }}>{title}</div>
      )}
      {children}
    </div>
  );
}

function V3HandoffPanel() {
  return (
    <div style={{
      width: 1200, padding: 28,
      background: "#fff",
      border: "1px solid #e5e2dc",
      borderRadius: 8,
      fontFamily: "ui-sans-serif, system-ui, -apple-system, sans-serif",
      color: "#1a1410",
      lineHeight: 1.55, fontSize: 13.5,
    }}>
      <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginBottom: 18 }}>
        <div style={{ fontSize: 22, fontWeight: 700, letterSpacing: -0.3 }}>
          Codex / Frontend-Guru Handoff
        </div>
        <div style={{ fontSize: 12, color: "#6b5d4a" }}>
          Mission Control Taskboard V3 · market-ready · Next.js + Tailwind
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 32 }}>
        {/* COMPONENT STRUCTURE */}
        <section>
          <h3 style={hsty}>Component structure</h3>
          <table style={tsty}>
            <thead><tr><th style={thsty}>Component</th><th style={thsty}>Owns</th></tr></thead>
            <tbody>
              {[
                ["<TaskboardShell>",     "page chrome · search · health beats · sidebar"],
                ["<LaneHeader>",         "tone dot · name · count · hint"],
                ["<TaskCard>",           "slim card · 3 zones (identity, status row, signal)"],
                ["<StatusBadge>",        "label + tone + intent dot · 11 canonical statuses"],
                ["<ReceiptStage>",       "4-dot progress (draft/dispatch/accept/result)"],
                ["<PriorityBadge>",      "P0–P3 monospace badge"],
                ["<AgeTag>",             "stale-aware monospace age"],
                ["<MeaningRail>",        "left edge of card · color = meaning"],
                ["<IncidentStrip>",      "appears only when failed/stale/no-hb > 0"],
                ["<DetailsDrawer>",      "right slide-over · hosts <DrawerContent>"],
                ["<DrawerSheet>",        "mobile bottom sheet variant"],
                ["<DrawerModal>",        "centered focused modal variant"],
                ["<TruthPanel>",         "right rail · honest counters + atlas suggest"],
                ["<EmptyLane>",          "lane-specific copy · dashed border"],
                ["<LoadingLane>",        "3 skeleton cards · shimmer"],
                ["<ErrorLane>",          "red surface · retry CTA"],
              ].map(([k,v]) => (
                <tr key={k}><td style={tdsty}><code>{k}</code></td><td style={tdsty}>{v}</td></tr>
              ))}
            </tbody>
          </table>
        </section>

        {/* DATA SHAPE */}
        <section>
          <h3 style={hsty}>Data each component needs</h3>
          <pre style={presty}>{`type Task = {
  id, code, title, project,
  agent: AgentName,            // 6 canonical
  priority: 'P0'|'P1'|'P2'|'P3',
  lane: LaneId,                // 7 canonical
  status: Status,              // 11 canonical
  age: string, stale: boolean,
  signal: string,              // 1 line, ≤90 chars
  workerSession?: string,
  retries?: '0/3'|'1/3'|'2/3'|'3/3',
};

type DetailTask = Task & {
  acceptance: { label, ok }[];
  receipts:   { stage, t, outcome, who, text }[];
  events:     { t, text, tone }[];
  parent?:    { code, title };
  followUps:  { code, title, status }[];
  raw: {
    dispatchToken, workerSession,
    parentRunId, region, schemaVersion
  };
};`}</pre>

          <h3 style={{ ...hsty, marginTop: 24 }}>Status taxonomy</h3>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8 }}>
            {[
              ["draft",       "neutral"],
              ["queued",      "neutral · sky"],
              ["dispatched",  "neutral · indigo"],
              ["assigned",    "neutral · indigo"],
              ["accepted",    "ok · teal"],
              ["active",      "ok · teal · heartbeat green"],
              ["noheartbeat", "warn · STRIPED amber · false-progress"],
              ["stale",       "warn · amber"],
              ["blocked",     "danger · rose"],
              ["failed",      "danger · rose"],
              ["review",      "review · violet"],
              ["done",        "ok · emerald"],
            ].map(([s, m]) => (
              <div key={s} style={{
                display: "flex", alignItems: "center", gap: 8,
                padding: "5px 8px", borderRadius: 5,
                background: "#faf6ee",
                border: "1px solid #ece4d2",
                fontFamily: "ui-monospace, SF Mono, Menlo, monospace",
                fontSize: 11.5,
              }}>
                <code style={{ fontWeight: 600 }}>{s}</code>
                <span style={{ flex: 1 }}/>
                <span style={{ color: "#6b5d4a", fontSize: 10.5 }}>{m}</span>
              </div>
            ))}
          </div>
        </section>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 32, marginTop: 28 }}>
        <section>
          <h3 style={hsty}>State-changing controls · need safeguards</h3>
          <ul style={{ paddingLeft: 18, margin: 0 }}>
            <li><b>Dispatch</b> (draft → dispatched): confirm modal · idempotency token · operator session check.</li>
            <li><b>Cancel run</b> (active → cancelled): confirm modal · cannot fire if accepted-no-heartbeat is in degraded grace window.</li>
            <li><b>Force resync</b> (noheartbeat): no-op if heartbeat resumes mid-flight · operator-gated.</li>
            <li><b>Retry failed</b> (failed → ready): blocked when retries == 3/3 or operator-block flag set.</li>
            <li><b>Approve & close</b> (review → done): writes acceptance signature receipt · cannot fire if any acceptance criteria failing.</li>
            <li><b>Reassign</b> (any active worker change): writes <code>reassign</code> receipt · drops old worker session cleanly.</li>
            <li><b>Create follow-up from this</b>: pre-fills parent · operator decides dispatch separately.</li>
          </ul>
        </section>

        <section>
          <h3 style={hsty}>Implementation slices (Codex)</h3>
          <ol style={{ paddingLeft: 18, margin: 0 }}>
            <li><b>Slice A · primitives</b>: <code>StatusBadge</code>, <code>PriorityBadge</code>, <code>ReceiptStage</code>, <code>AgeTag</code>, <code>MeaningRail</code>. Pure presentational. Storybook + visual test.</li>
            <li><b>Slice B · TaskCard</b>: composes A. No data fetching. Click → <code>onOpen(taskId)</code> callback.</li>
            <li><b>Slice C · LaneHeader + EmptyLane + LoadingLane + ErrorLane</b>. Wired with React Query <code>useLane(laneId)</code> states.</li>
            <li><b>Slice D · TaskboardShell</b>: sidebar + top chrome + 5-lane grid + closed-lanes footer. Pure layout · grid uses <code>grid-cols-5</code>.</li>
            <li><b>Slice E · IncidentStrip</b>: hidden when no failed/stale/no-hb. Single fetch <code>useTaskboardHealth()</code>.</li>
            <li><b>Slice F · DetailsDrawer</b>: route-driven (<code>/taskboard/[id]</code>) so deep-links work · <code>&lt;DrawerContent&gt;</code> shared with sheet/modal.</li>
            <li><b>Slice G · State-changing actions</b> behind confirm dialogs. All write through MCP wrappers per MC-T11.</li>
            <li><b>Slice H · Mobile</b>: same TaskCard, vertically stacked lanes with sticky lane chips · <code>DrawerSheet</code> at <code>md:hidden</code>.</li>
          </ol>

          <h3 style={{ ...hsty, marginTop: 18 }}>Next.js / Tailwind notes</h3>
          <ul style={{ paddingLeft: 18, margin: 0 }}>
            <li><b>Routing</b>: <code>/taskboard?status=…&amp;agent=…</code> for filters, <code>/taskboard/[id]</code> opens drawer (parallel route or modal route).</li>
            <li><b>Data</b>: React Query · per-lane <code>useLane(laneId)</code> · separate <code>useTaskDetails(id)</code> for drawer (fetches receipts, events lazily).</li>
            <li><b>Realtime</b>: SSE/WebSocket on <code>/api/mc/stream</code>; receipts and heartbeat events patch React Query cache by id.</li>
            <li><b>False-progress detection</b>: server-derived. UI never invents status. <code>status: noheartbeat</code> flag is set when <code>now - lastHeartbeat &gt; threshold</code>.</li>
            <li><b>Tokens</b>: extend <code>tailwind.config.ts</code> with <code>tone</code> color set ({"{teal, amber, rose, violet, emerald, sky, indigo, zinc}"}); use CSS vars for fg/bg/border alphas.</li>
            <li><b>A11y</b>: cards are <code>&lt;button&gt;</code>, drawer trapped, status changes announce via aria-live.</li>
            <li><b>Print</b>: drawer prints linearly (lifecycle, receipts, raw); skip nav.</li>
          </ul>
        </section>
      </div>

      <div style={{ marginTop: 28 }}>
        <h3 style={hsty}>Acceptance criteria — definition of "market-ready"</h3>
        <ol style={{ paddingLeft: 18, margin: 0, columns: 2, columnGap: 32 }}>
          <li>Operator identifies <b>active</b>, <b>blocked</b>, <b>stale</b>, <b>failed</b>, <b>review-needed</b> tasks within <b>10s</b> on first load.</li>
          <li>Cards show only: code, title, agent, priority, status, receipt-stage, age, 1 signal line.</li>
          <li>No card exposes raw metadata (dispatch token, worker session, run id, schema version).</li>
          <li>Drawer contains: truth+next, lifecycle, receipts, session, acceptance, events, parent/follow-ups, result detail, raw metadata (collapsed).</li>
          <li>Accepted-without-heartbeat is <b>visually distinct</b> from healthy active (striped amber rail, "no heartbeat" status).</li>
          <li>Failed and blocked use <b>rose</b>; review uses <b>violet</b>; healthy active uses <b>teal</b> — colors never overload.</li>
          <li>Dashboard counters (active/review/stale/failed) are derived from the same source as Taskboard — they cannot disagree.</li>
          <li>Mobile: 7 lanes stack vertically, incident strip pins on top, drawer becomes sheet.</li>
          <li>Desktop: 5 primary lanes side-by-side, done+failed compressed in footer, drawer slides over right.</li>
          <li>State-changing actions confirm before firing and write a receipt.</li>
          <li>Loading/empty/error states for every lane and the drawer.</li>
          <li>Atlas suggestion never auto-fires; only the operator commits.</li>
        </ol>
      </div>
    </div>
  );
}

const hsty = { fontSize: 14, fontWeight: 700, margin: "0 0 10px", letterSpacing: -0.2 };
const tsty = { width: "100%", borderCollapse: "collapse" };
const thsty = { textAlign: "left", fontSize: 11, fontWeight: 700, color: "#6b5d4a",
  letterSpacing: ".12em", textTransform: "uppercase", borderBottom: "1px solid #ece4d2",
  padding: "6px 8px",
};
const tdsty = { padding: "5px 8px", borderBottom: "1px solid #f5efe2", fontSize: 12 };
const presty = { background: "#faf6ee", border: "1px solid #ece4d2",
  borderRadius: 6, padding: 12, fontSize: 11, lineHeight: 1.55,
  fontFamily: "ui-monospace, SF Mono, Menlo, monospace",
  color: "#1a1410", whiteSpace: "pre-wrap", margin: 0,
};

/* ════════════════════════════════════════════════════════════════
   MAIN CANVAS
   ════════════════════════════════════════════════════════════════ */

function V3Canvas() {
  return (
    <DesignCanvas
      title="Mission Control Taskboard V3"
      subtitle="Market-ready operations UI · 3 directions · recommended hybrid · drawer · states · handoff"
    >
      {/* directions */}
      <DCSection
        title="Three V3 directions — pick a chassis"
        subtitle="All share slim card, status taxonomy, 7-lane model, receipt-stage indicator. They differ in how the chrome is organized."
      >
        <DCArtboard label="V3A · Dense Operator Cockpit (1440×900)" width={V3A_W} height={V3A_H}>
          <V3ADesktop/>
        </DCArtboard>
        <DCArtboard label="V3B · Balanced Kanban + Drawer (1440×900)" width={V3B_W} height={V3B_H}>
          <V3BDesktop/>
        </DCArtboard>
        <DCArtboard label="V3C · Incident-First Triage (1440×900)" width={V3C_W} height={V3C_H}>
          <V3CDesktop/>
        </DCArtboard>
        <div style={{ width: 360, paddingTop: 56, display: "flex", flexDirection: "column", gap: 12 }}>
          <V3Note title="V3A — when to pick" tone="teal">
            Experienced operators on widescreens. Maximum signal density: all 7 lanes side-by-side, persistent right-rail Truth panel, ⌘K-driven. Best for power users.
          </V3Note>
          <V3Note title="V3B — when to pick" tone="violet">
            Mixed audience. 5 primary lanes side-by-side, done+failed compressed in footer, drawer-driven detail. The most "professional SaaS" feel and the recommended chassis.
          </V3Note>
          <V3Note title="V3C — when to pick" tone="rose">
            Incident commander / on-call. Inverts kanban: failures, stale, review on TOP. Healthy work compressed to chips. Use as a <i>mode</i> on top of V3B.
          </V3Note>
        </div>
      </DCSection>

      {/* recommendation */}
      <DCSection
        title="Recommended hybrid"
        subtitle="V3B chrome (calm, drawer-driven) + V3C incident strip (only when something is wrong) + V3A right-rail Truth panel as an opt-in mode. Slim card is universal."
      >
        <DCArtboard label="Desktop · 1440×900 · primary view" width={V3B_W} height={V3B_H}>
          <V3RecommendedDesktop/>
        </DCArtboard>
        <DCArtboard label="Desktop · drawer open · 1440×900" width={V3B_W} height={V3B_H}>
          <V3BDesktop/>
        </DCArtboard>
        <div style={{ width: 380, paddingTop: 56, display: "flex", flexDirection: "column", gap: 12 }}>
          <V3Note title="Why this hybrid" tone="violet">
            <b>Calm by default.</b> When health is green, no alarming red surfaces. When something fails, the incident strip pins on top with one-click triage.
            <br/><br/>
            <b>Drawer over modal.</b> Operators stay in context — board never disappears. Modal reserved for state-changing confirms.
          </V3Note>
          <V3Note title="What we kept from V2" tone="teal">
            Token system, agent palette, mobile bottom-tab, density philosophy. V3 refines them — does not replace them.
          </V3Note>
          <V3Note title="What changed materially" tone="amber">
            7 canonical lanes (was 5). Receipt-stage shipped on every card. Striped amber rail for accepted-no-heartbeat. Card content cut by 60%.
          </V3Note>
        </div>
      </DCSection>

      {/* mobile */}
      <DCSection
        title="Mobile · 390 × 844"
        subtitle="Same atoms, vertical stack. Incident card pins, drawer becomes a bottom sheet."
      >
        <DCArtboard label="Mobile · primary feed" width={406} height={860} style={{ background: "transparent", boxShadow: "none" }}>
          <div style={{ padding: 8 }}><V3Mobile/></div>
        </DCArtboard>
        <DCArtboard label="Mobile · details bottom sheet" width={406} height={860} style={{ background: "transparent", boxShadow: "none" }}>
          <div style={{ padding: 8 }}><V3MobileSheet/></div>
        </DCArtboard>
        <div style={{ width: 360, paddingTop: 56, display: "flex", flexDirection: "column", gap: 12 }}>
          <V3Note title="Mobile rules" tone="teal">
            Header truth row matches desktop counters exactly. Lane chips replace 7-column board. Tap a card → bottom sheet (drawer content, unchanged).
          </V3Note>
          <V3Note title="Information density" tone="violet">
            Slim card stays slim on mobile — same 3 rows. We trade horizontal density (7 lanes) for vertical stacking. Truth panel collapses into the sticky header.
          </V3Note>
        </div>
      </DCSection>

      {/* drawer */}
      <DCSection
        title="Details drawer / modal / sheet"
        subtitle="One content component, three host shells. Order: truth → lifecycle → receipts → session → acceptance → events → relations → result → raw."
      >
        <DCArtboard label="Drawer (desktop) · 460 × 900" width={460} height={900}>
          <div style={{ width: 460, height: 900, background: "#0a0a0d" }}>
            <V3DrawerContent task={V3_DETAIL_TASK} variant="drawer"/>
          </div>
        </DCArtboard>
        <DCArtboard label="Modal (desktop) · 720 × 760" width={720} height={760}>
          <div style={{
            width: 720, height: 760,
            background: "#0a0a0d",
            border: "1px solid rgba(255,255,255,.10)",
            boxShadow: "0 24px 64px rgba(0,0,0,.5)",
          }}>
            <V3DrawerContent task={V3_DETAIL_TASK} variant="modal"/>
          </div>
        </DCArtboard>
        <div style={{ width: 360, paddingTop: 56, display: "flex", flexDirection: "column", gap: 12 }}>
          <V3Note title="Why truth-first" tone="rose">
            The current detail leads with prompt + summary text. V3 leads with what's true and what to do next. Long context is below the fold.
          </V3Note>
          <V3Note title="Receipt chain" tone="teal">
            Latest first, full chain. The failed result is the first thing you read. Operator can scroll to draft if archaeology is needed.
          </V3Note>
          <V3Note title="Raw metadata" tone="zinc">
            Last section, collapsible. Power users get it; everyone else doesn't see noise.
          </V3Note>
        </div>
      </DCSection>

      {/* states */}
      <DCSection
        title="State examples"
        subtitle="Every lane and every card has a deliberate visual for: loading, empty, error, stale, blocked, failed, review-needed, accepted-without-heartbeat (false progress), active healthy, done, draft."
      >
        <DCArtboard label="Loading · skeleton" width={STATES_W} height={STATES_H} style={{ background: "transparent", boxShadow: "none" }}>
          <StateLane kind={{ lane: "active", count: 0, render: () => <StateLoading/> }}/>
        </DCArtboard>
        <DCArtboard label="Empty · review" width={STATES_W} height={STATES_H} style={{ background: "transparent", boxShadow: "none" }}>
          <StateLane kind={{ lane: "review", count: 0,
            render: () => <StateEmpty lane={V3_LANES.find(l=>l.id==="review")}/> }}/>
        </DCArtboard>
        <DCArtboard label="Error · fetch failed" width={STATES_W} height={STATES_H} style={{ background: "transparent", boxShadow: "none" }}>
          <StateLane kind={{ lane: "active", count: 0, render: () => <StateError/> }}/>
        </DCArtboard>
        <DCArtboard label="Active · healthy" width={STATES_W} height={STATES_H} style={{ background: "transparent", boxShadow: "none" }}>
          <StateLane kind={{ lane: "active", count: 2,
            render: () => V3_TASKS_BY_LANE("active").map(t => <V3Card key={t.id} task={t}/>) }}/>
        </DCArtboard>
        <DCArtboard label="Stale · no heartbeat (false progress)" width={STATES_W} height={STATES_H} style={{ background: "transparent", boxShadow: "none" }}>
          <StateLane kind={{ lane: "assigned", count: 1,
            render: () => V3_TASKS.filter(t=>t.status==="noheartbeat").map(t => <V3Card key={t.id} task={t}/>) }}/>
        </DCArtboard>
        <DCArtboard label="Failed · needs review" width={STATES_W} height={STATES_H} style={{ background: "transparent", boxShadow: "none" }}>
          <StateLane kind={{ lane: "failed", count: 2,
            render: () => V3_TASKS_BY_LANE("failed").map(t => <V3Card key={t.id} task={t}/>) }}/>
        </DCArtboard>
        <DCArtboard label="Review needed" width={STATES_W} height={STATES_H} style={{ background: "transparent", boxShadow: "none" }}>
          <StateLane kind={{ lane: "review", count: 1,
            render: () => V3_TASKS_BY_LANE("review").map(t => <V3Card key={t.id} task={t}/>) }}/>
        </DCArtboard>
        <DCArtboard label="Draft · waiting dispatch" width={STATES_W} height={STATES_H} style={{ background: "transparent", boxShadow: "none" }}>
          <StateLane kind={{ lane: "draft", count: 2,
            render: () => V3_TASKS_BY_LANE("draft").map(t => <V3Card key={t.id} task={t}/>) }}/>
        </DCArtboard>
        <DCArtboard label="Done · with result" width={STATES_W} height={STATES_H} style={{ background: "transparent", boxShadow: "none" }}>
          <StateLane kind={{ lane: "done", count: 3,
            render: () => V3_TASKS_BY_LANE("done").map(t => <V3Card key={t.id} task={t}/>) }}/>
        </DCArtboard>
      </DCSection>

      {/* handoff */}
      <DCSection title="Handoff" subtitle="Component structure · data shape · safeguards · slices · acceptance">
        <DCArtboard label="Codex / Frontend-Guru spec" width={1260} height={1260}
          style={{ background: "#fffaf0" }}
        >
          <V3HandoffPanel/>
        </DCArtboard>
      </DCSection>
    </DesignCanvas>
  );
}

Object.assign(window, { V3Canvas, V3HandoffPanel });
