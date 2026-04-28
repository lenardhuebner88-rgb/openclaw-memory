// V3 Canvas — finalized recommended hybrid + addendum (control bar) + states + handoff.
// V3A/V3B/V3C are kept as a small reference set, not the primary view.

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

/* ════════════════════════════════════════════════════════════════
   HANDOFF PANEL — updated with V3ControlBar contract + slice I.
   ════════════════════════════════════════════════════════════════ */

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
          Mission Control Taskboard V3 · finalized hybrid · Next.js + Tailwind
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
                ["<ControlBar>",         "Density · Mode · Truth-rail · single source"],
                ["<LaneHeader>",         "tone dot · name · count · hint"],
                ["<TaskCard>",           "slim card · 3 zones · density-aware"],
                ["<StatusBadge>",        "label + tone + intent dot · 11 canonical statuses"],
                ["<ReceiptStage>",       "4-dot progress · falseProgress flag for striped amber"],
                ["<PriorityBadge>",      "P0–P3 monospace badge"],
                ["<AgeTag>",             "stale-aware monospace age"],
                ["<MeaningRail>",        "left-edge color · meaning-driven, not decorative"],
                ["<IncidentStrip>",      "appears only when failed/stale/no-hb > 0"],
                ["<TriageView>",         "Mode=triage layout · incidents top, quiet bottom"],
                ["<DetailsDrawer>",      "right slide-over · hosts <DrawerContent>"],
                ["<DrawerSheet>",        "mobile bottom sheet variant"],
                ["<DrawerModal>",        "centered focused modal variant"],
                ["<TruthRail>",          "right rail · honest counters + atlas suggest · opt-in"],
                ["<EmptyLane>",          "lane-specific copy · dashed border"],
                ["<LoadingLane>",        "3 skeleton cards · shimmer"],
                ["<ErrorLane>",          "red surface · retry CTA"],
              ].map(([k,v]) => (
                <tr key={k}><td style={tdsty}><code>{k}</code></td><td style={tdsty}>{v}</td></tr>
              ))}
            </tbody>
          </table>

          <h3 style={{ ...hsty, marginTop: 20 }}>ControlBar contract</h3>
          <pre style={presty}>{`type ControlBarState = {
  density:   'comfy' | 'dense';     // card padding + lane gap
  mode:      'board' | 'triage';    // V3B layout vs V3C inversion
  truthRail: boolean;               // shows V3A right rail
};

type ControlBarProps = {
  state:    ControlBarState;
  set:      (patch: Partial<ControlBarState>) => void;
  compact?: boolean;                // mobile inline variant
};`}</pre>
          <ul style={{ paddingLeft: 18, margin: "8px 0 0", fontSize: 12.5 }}>
            <li>Single state object · all three knobs flip without page reload.</li>
            <li>Persist to <code>localStorage["mc.taskboard.controlBar"]</code> (per-operator).</li>
            <li>URL-syncable: <code>?density=dense&mode=triage&rail=on</code> for shareable views.</li>
            <li>Keyboard: <code>D</code> density, <code>M</code> mode, <code>T</code> truth rail · all when board has focus.</li>
            <li>Triage mode hides the IncidentStrip (incidents are first-class in that view).</li>
          </ul>
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
};

type Health = {           // single source — chrome + rail + dashboard agree
  active, review, stale, failed: number;
  incidentCount: number;  // failed + stale
  hasIncident:   boolean;
};`}</pre>

          <h3 style={{ ...hsty, marginTop: 20 }}>Status taxonomy</h3>
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

          <h3 style={{ ...hsty, marginTop: 20 }}>ControlBar safeguards</h3>
          <ul style={{ paddingLeft: 18, margin: 0 }}>
            <li>None of the three knobs are state-changing — they are <i>view</i> controls only. Safe to flip mid-session.</li>
            <li>Mode=triage <b>does not</b> filter the dataset; it re-arranges the same tasks. Counter parity preserved.</li>
            <li>Truth-rail toggling re-fits the grid (188px → 188+304px). No fetch, no cache invalidation.</li>
            <li>Density flip emits no telemetry or write — safe across all auth tiers.</li>
          </ul>
        </section>

        <section>
          <h3 style={hsty}>Implementation slices (Codex)</h3>
          <ol style={{ paddingLeft: 18, margin: 0 }}>
            <li><b>Slice A · primitives</b>: <code>StatusBadge</code>, <code>PriorityBadge</code>, <code>ReceiptStage</code>, <code>AgeTag</code>, <code>MeaningRail</code>. Pure presentational. Storybook + visual test.</li>
            <li><b>Slice B · TaskCard</b>: composes A. No data fetching. Click → <code>onOpen(taskId)</code> callback. Density prop passes through.</li>
            <li><b>Slice C · LaneHeader + EmptyLane + LoadingLane + ErrorLane</b>. Wired with React Query <code>useLane(laneId)</code> states.</li>
            <li><b>Slice D · TaskboardShell</b>: sidebar + top chrome + sub-bar + 5-lane grid + closed-lanes footer. Pure layout.</li>
            <li><b>Slice E · IncidentStrip</b>: hidden when no failed/stale/no-hb. Single fetch <code>useTaskboardHealth()</code>.</li>
            <li><b>Slice F · DetailsDrawer</b>: route-driven (<code>/taskboard/[id]</code>) so deep-links work · <code>&lt;DrawerContent&gt;</code> shared with sheet/modal.</li>
            <li><b>Slice G · State-changing actions</b> behind confirm dialogs. All write through MCP wrappers per MC-T11.</li>
            <li><b>Slice H · Mobile</b>: same TaskCard, vertically stacked lanes with sticky lane chips · <code>DrawerSheet</code> at <code>md:hidden</code>.</li>
            <li><b>Slice I · ControlBar</b>: 1 component, 1 state object, 3 knobs. Wires Density (CSS variable), Mode (layout switch), TruthRail (grid template). Persist to localStorage; URL-sync via <code>useSearchParams</code>.</li>
          </ol>

          <h3 style={{ ...hsty, marginTop: 18 }}>Next.js / Tailwind notes</h3>
          <ul style={{ paddingLeft: 18, margin: 0 }}>
            <li><b>Routing</b>: <code>/taskboard?status=…&amp;agent=…&amp;density=…&amp;mode=…&amp;rail=…</code>; <code>/taskboard/[id]</code> opens drawer (parallel route).</li>
            <li><b>Data</b>: React Query · per-lane <code>useLane(laneId)</code> · separate <code>useTaskDetails(id)</code> for drawer (lazy receipts/events).</li>
            <li><b>Realtime</b>: SSE/WebSocket on <code>/api/mc/stream</code>; receipts and heartbeat events patch React Query cache by id.</li>
            <li><b>False-progress detection</b>: server-derived. UI never invents status. <code>noheartbeat</code> set when <code>now − lastHeartbeat &gt; threshold</code>.</li>
            <li><b>Tokens</b>: extend <code>tailwind.config.ts</code> with <code>tone</code> color set ({"{teal, amber, rose, violet, emerald, sky, indigo, zinc}"}); use CSS vars for fg/bg/border alphas.</li>
            <li><b>Density</b>: drive via <code>data-density="comfy|dense"</code> on shell · Tailwind plugin reads <code>data-density</code> for variants.</li>
            <li><b>A11y</b>: cards are <code>&lt;button&gt;</code>, drawer trapped, status changes announce via aria-live, ControlBar is <code>radiogroup</code> + <code>switch</code>.</li>
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
          <li>Mobile: lanes stack vertically, incident strip pins on top, drawer becomes sheet, ControlBar collapses to compact variant.</li>
          <li>Desktop: 5 primary lanes side-by-side, done+failed compressed in footer, drawer slides over right; ControlBar lives in the sub-bar.</li>
          <li>State-changing actions confirm before firing and write a receipt.</li>
          <li>Loading/empty/error states for every lane and the drawer.</li>
          <li>Atlas suggestion never auto-fires; only the operator commits.</li>
          <li><b>ControlBar</b>: all three knobs flip without page reload, persist per-operator, are URL-shareable.</li>
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
      subtitle="Finalized hybrid · unified ControlBar · mobile + desktop · drawer · states · handoff"
    >
      {/* ──────────────────────────────────────────────────────────────
         FINALIZED HYBRID — primary section, 4 desktop states
         ────────────────────────────────────────────────────────────── */}
      <DCSection
        title="Finalized hybrid · desktop · 1440 × 900"
        subtitle="V3B chrome · V3C incident strip (only when needed) · V3A truth rail (opt-in). Density / Mode / Truth-rail flip in place via the ControlBar in the sub-bar."
      >
        <DCArtboard label="Default · Comfy · Board · Truth-rail off" width={V3B_W} height={V3B_H}>
          <V3FinalDesktop initial={{ density: "comfy", mode: "board", truthRail: false }}/>
        </DCArtboard>
        <DCArtboard label="Dense · Board · Truth-rail off" width={V3B_W} height={V3B_H}>
          <V3FinalDesktop initial={{ density: "dense", mode: "board", truthRail: false }}/>
        </DCArtboard>
        <DCArtboard label="Comfy · Board · Truth-rail ON" width={V3B_W} height={V3B_H}>
          <V3FinalDesktop initial={{ density: "comfy", mode: "board", truthRail: true }}/>
        </DCArtboard>
        <DCArtboard label="Comfy · Triage mode" width={V3B_W} height={V3B_H}>
          <V3FinalDesktop initial={{ density: "comfy", mode: "triage", truthRail: false }}/>
        </DCArtboard>
        <DCArtboard label="With drawer open" width={V3B_W} height={V3B_H}>
          <V3BDesktop/>
        </DCArtboard>

        <div style={{ width: 380, paddingTop: 56, display: "flex", flexDirection: "column", gap: 12 }}>
          <V3Note title="Why these are equivalent" tone="violet">
            All five artboards render the <b>same dataset</b> through the same shell. Only the ControlBar state changes. No fetch, no reload. Operators tune the surface to what they're doing — incidents, scan, deep-dive — without leaving the page.
          </V3Note>
          <V3Note title="Calm by default" tone="teal">
            Top chrome carries identity, search, "+ New task" and the operator avatar. The big rose health-pill is gone. Honest beats sit in the sub-bar; an incident strip pins above the lanes <i>only when something is actually wrong</i>.
          </V3Note>
          <V3Note title="What the ControlBar changes" tone="amber">
            <b>Density</b>: card padding + lane gap (Tailwind <code>data-density</code>).<br/>
            <b>Mode</b>: Board (5-lane grid) ↔ Triage (incidents-on-top, quiet at bottom).<br/>
            <b>Truth rail</b>: opens 304px right rail with honest counters + Atlas suggest + selected pre-detail.
          </V3Note>
        </div>
      </DCSection>

      {/* ──────────────────────────────────────────────────────────────
         ADDENDUM — ControlBar component spec
         ────────────────────────────────────────────────────────────── */}
      <DCSection
        title="Addendum · ControlBar"
        subtitle="One unified control bar. Three knobs. One state object. No reload."
      >
        <DCArtboard label="ControlBar · light-on-dark sub-bar (production)" width={780} height={120}>
          <V3ControlBarShowcase compact={false}/>
        </DCArtboard>
        <DCArtboard label="ControlBar · compact (mobile inline)" width={780} height={100}>
          <V3ControlBarShowcase compact/>
        </DCArtboard>
        <DCArtboard label="State permutations · what each knob does" width={780} height={520}>
          <V3ControlBarMatrix/>
        </DCArtboard>

        <div style={{ width: 380, paddingTop: 56, display: "flex", flexDirection: "column", gap: 12 }}>
          <V3Note title="Three knobs · one state" tone="violet">
            <code>{`{ density, mode, truthRail }`}</code>. All three live in the sub-bar. Density and Mode are radio segments; Truth-rail is a switch. Compact variant strips the labels for mobile.
          </V3Note>
          <V3Note title="Keyboard" tone="teal">
            <code>D</code> Density · <code>M</code> Mode · <code>T</code> Truth rail. All when the board has focus. Same operator who learned ⌘K stays in flow.
          </V3Note>
          <V3Note title="Persist + share" tone="amber">
            Persist to <code>localStorage["mc.taskboard.controlBar"]</code> per-operator. URL-sync via <code>?density=…&amp;mode=…&amp;rail=…</code> for shareable views ("triage with rail open").
          </V3Note>
        </div>
      </DCSection>

      {/* ──────────────────────────────────────────────────────────────
         MOBILE
         ────────────────────────────────────────────────────────────── */}
      <DCSection
        title="Mobile · 390 × 844"
        subtitle="Same atoms, vertical stack. Compact ControlBar in the sticky header. Drawer becomes a bottom sheet."
      >
        <DCArtboard label="Mobile · feed (board mode)" width={406} height={860} style={{ background: "transparent", boxShadow: "none" }}>
          <div style={{ padding: 8 }}><V3MobileFinal/></div>
        </DCArtboard>
        <DCArtboard label="Mobile · details bottom sheet" width={406} height={860} style={{ background: "transparent", boxShadow: "none" }}>
          <div style={{ padding: 8 }}><V3MobileSheet/></div>
        </DCArtboard>
        <div style={{ width: 360, paddingTop: 56, display: "flex", flexDirection: "column", gap: 12 }}>
          <V3Note title="Mobile rules" tone="teal">
            Sticky header: title · 13 · 6 agents · operator. Truth row matches desktop counters exactly. ControlBar (compact) sits below — Density and Mode only, no rail on mobile.
          </V3Note>
          <V3Note title="Information density" tone="violet">
            Slim card stays slim — same 3 rows. We trade horizontal density (5 lanes) for vertical stacking. Tap a card → bottom sheet (drawer content, unchanged).
          </V3Note>
        </div>
      </DCSection>

      {/* ──────────────────────────────────────────────────────────────
         DRAWER / MODAL / SHEET
         ────────────────────────────────────────────────────────────── */}
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
            Detail leads with what's true and what to do next. Long context is below the fold.
          </V3Note>
          <V3Note title="Receipt chain" tone="teal">
            Latest first, full chain. Failed result is the first thing you read.
          </V3Note>
          <V3Note title="Raw metadata" tone="zinc">
            Last section, collapsible. Power users get it; everyone else doesn't see noise.
          </V3Note>
        </div>
      </DCSection>

      {/* ──────────────────────────────────────────────────────────────
         STATES
         ────────────────────────────────────────────────────────────── */}
      <DCSection
        title="State examples"
        subtitle="Loading · empty · error · stale · blocked · failed · review · accepted-without-heartbeat (false progress) · active healthy · done · draft."
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

      {/* ──────────────────────────────────────────────────────────────
         REFERENCE — earlier directions, tucked at the end
         ────────────────────────────────────────────────────────────── */}
      <DCSection
        title="Reference · earlier directions"
        subtitle="V3A/V3B/V3C are the chassis options the finalized hybrid pulls from. Kept here for rationale only — not the primary view."
      >
        <DCArtboard label="V3A · Dense Operator Cockpit" width={V3A_W} height={V3A_H}>
          <V3ADesktop/>
        </DCArtboard>
        <DCArtboard label="V3B · Balanced Kanban + Drawer" width={V3B_W} height={V3B_H}>
          <V3BDesktop/>
        </DCArtboard>
        <DCArtboard label="V3C · Incident-First Triage" width={V3C_W} height={V3C_H}>
          <V3CDesktop/>
        </DCArtboard>
      </DCSection>

      {/* ──────────────────────────────────────────────────────────────
         HANDOFF
         ────────────────────────────────────────────────────────────── */}
      <DCSection title="Handoff" subtitle="Component structure · ControlBar contract · safeguards · slices · acceptance">
        <DCArtboard label="Codex / Frontend-Guru spec" width={1260} height={1380}
          style={{ background: "#fffaf0" }}
        >
          <V3HandoffPanel/>
        </DCArtboard>
      </DCSection>
    </DesignCanvas>
  );
}

/* ════════════════════════════════════════════════════════════════
   CONTROL BAR SHOWCASE — addendum artboards
   ════════════════════════════════════════════════════════════════ */

function V3ControlBarShowcase({ compact }) {
  const [s1, setS1] = useStateCanvas({ density: "comfy",  mode: "board",  truthRail: false });
  const [s2, setS2] = useStateCanvas({ density: "dense",  mode: "board",  truthRail: true  });
  const [s3, setS3] = useStateCanvas({ density: "comfy",  mode: "triage", truthRail: false });
  const rows = [
    { label: "Default",          state: s1, set: (p) => setS1({ ...s1, ...p }) },
    { label: "Dense + rail on",  state: s2, set: (p) => setS2({ ...s2, ...p }) },
    { label: "Triage mode",      state: s3, set: (p) => setS3({ ...s3, ...p }) },
  ];
  return (
    <div style={{
      width: 780,
      height: compact ? 100 : 120,
      padding: "16px 18px",
      background: "#08080a",
      color: "white", fontFamily: "var(--font-sans)",
      display: "flex", flexDirection: "column", gap: compact ? 8 : 10,
      boxSizing: "border-box",
    }}>
      {rows.map((r) => (
        <div key={r.label} style={{
          display: "flex", alignItems: "center", gap: 14,
        }}>
          <span style={{
            width: 110, fontSize: 10.5, fontWeight: 700, color: "var(--text-soft)",
            letterSpacing: ".18em", textTransform: "uppercase",
          }}>{r.label}</span>
          <V3ControlBar state={r.state} set={r.set} compact={compact}/>
        </div>
      ))}
    </div>
  );
}

function V3ControlBarMatrix() {
  return (
    <div style={{
      width: 780, height: 520, padding: "20px 24px",
      background: "#08080a",
      color: "white", fontFamily: "var(--font-sans)",
      boxSizing: "border-box", overflow: "hidden",
    }}>
      <div style={{
        fontSize: 11, fontWeight: 700, color: "var(--text-soft)",
        letterSpacing: ".22em", textTransform: "uppercase", marginBottom: 14,
      }}>What each knob does</div>

      <div style={{ display: "grid", gridTemplateColumns: "120px 1fr 1fr", gap: 12 }}>
        <div/>
        <Hd>Off / Left</Hd>
        <Hd>On / Right</Hd>

        <Lbl>Density</Lbl>
        <Cell title="Comfy" body="13.5px title · 12px signal · 10px lane gap · 7px card gap. Default for cross-team operators."/>
        <Cell title="Dense" body="12.5px title · 11.5px signal · 8px lane gap · 5px card gap. Power-user scan mode."/>

        <Lbl>Mode</Lbl>
        <Cell title="Board" body="5 primary lanes side-by-side. Done + Failed compressed in footer. Incident strip pins on top when health is non-green."/>
        <Cell title="Triage" body="Incident cards on top (3-col). Review-needed + healthy active in 2-col below. Quiet lanes compressed to chip cards. Same dataset; rearranged."  tone="rose"/>

        <Lbl>Truth rail</Lbl>
        <Cell title="Off (default)" body="Grid is sidebar + main. Counters live in the sub-bar."/>
        <Cell title="On" body="Adds 304px right rail: honest counters · Atlas suggest · selected pre-detail · worker session strip. Keyboard-friendly companion."/>
      </div>

      <div style={{
        marginTop: 18, padding: "10px 12px", borderRadius: 6,
        background: "rgba(124,58,237,.08)", border: "1px solid rgba(124,58,237,.24)",
        color: "white", fontSize: 12, lineHeight: 1.5,
      }}>
        <b style={{ color: "#c4b5fd" }}>None of these knobs change data.</b> They are pure view controls — safe to flip mid-session, safe to URL-share, safe across all auth tiers.
      </div>
    </div>
  );

  function Hd({ children }) {
    return (
      <div style={{
        fontSize: 10, fontWeight: 700, color: "var(--text-dim)",
        letterSpacing: ".18em", textTransform: "uppercase",
        paddingBottom: 6, borderBottom: "1px solid rgba(255,255,255,.06)",
      }}>{children}</div>
    );
  }
  function Lbl({ children }) {
    return (
      <div style={{
        fontSize: 11, fontWeight: 700, color: "white",
        letterSpacing: ".06em", textTransform: "uppercase",
        paddingTop: 8,
      }}>{children}</div>
    );
  }
  function Cell({ title, body, tone }) {
    const t = tone ? V3_TONE[tone] : null;
    return (
      <div style={{
        padding: 10, borderRadius: 6,
        background: t ? t.bg : "rgba(255,255,255,.02)",
        border: `1px solid ${t ? t.border : "rgba(255,255,255,.06)"}`,
      }}>
        <div style={{
          fontSize: 12, fontWeight: 700, color: t ? t.fg : "white",
          marginBottom: 4,
        }}>{title}</div>
        <div style={{ fontSize: 11.5, color: "var(--text-soft)", lineHeight: 1.5 }}>{body}</div>
      </div>
    );
  }
}

Object.assign(window, { V3Canvas, V3HandoffPanel, V3ControlBarShowcase, V3ControlBarMatrix });
