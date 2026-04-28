// V3 — Mission Control Taskboard, market-ready operations UI.
// Foundation: lane model, status taxonomy, slim card, receipt-stage indicator,
// stale/blocked/review cues, agent badge reuse.

const { useState: useStateV3, useEffect: useEffectV3, useRef: useRefV3, useMemo: useMemoV3 } = React;

/* ════════════════════════════════════════════════════════════════
   STATUS TAXONOMY — every color must mean something specific.
   ════════════════════════════════════════════════════════════════ */

// Canonical lane model — 7 lanes
const V3_LANES = [
  { id: "draft",    name: "Draft",     hint: "waiting dispatch",  tone: "zinc"    },
  { id: "ready",    name: "Ready",     hint: "queued",            tone: "sky"     },
  { id: "assigned", name: "Assigned",  hint: "not yet accepted",  tone: "indigo"  },
  { id: "active",   name: "Active",    hint: "heartbeat OK",      tone: "teal"    },
  { id: "review",   name: "Review",    hint: "awaits operator",   tone: "violet"  },
  { id: "done",     name: "Done",      hint: "result delivered",  tone: "emerald" },
  { id: "failed",   name: "Failed",    hint: "blocked / errored", tone: "rose"    },
];

// Canonical receipt-stage. 4 dots, lit per progress.
const V3_STAGES = ["draft", "dispatched", "accepted", "result"];

// Status semantics. tone+intent never lie.
const V3_STATUS = {
  // healthy paths
  draft:           { label: "Draft",        tone: "zinc",   intent: "neutral",  stage: 0 },
  queued:          { label: "Queued",       tone: "sky",    intent: "neutral",  stage: 1 },
  dispatched:      { label: "Dispatched",   tone: "indigo", intent: "neutral",  stage: 1 },
  assigned:        { label: "Assigned",     tone: "indigo", intent: "neutral",  stage: 1 },
  accepted:        { label: "Accepted",     tone: "teal",   intent: "ok",       stage: 2 },
  active:          { label: "Active",       tone: "teal",   intent: "ok",       stage: 2 },
  // danger paths — distinct visual taxonomy per type
  noheartbeat:     { label: "No heartbeat", tone: "amber",  intent: "warn",     stage: 2, falseProgress: true },
  stale:           { label: "Stale",        tone: "amber",  intent: "warn",     stage: 2 },
  blocked:         { label: "Blocked",      tone: "rose",   intent: "danger",   stage: 2 },
  failed:          { label: "Failed",       tone: "rose",   intent: "danger",   stage: 3 },
  review:          { label: "Review needed",tone: "violet", intent: "review",   stage: 3 },
  done:            { label: "Done",         tone: "emerald",intent: "ok",       stage: 3 },
};

// Priority, restrained
const V3_PRIORITY = {
  P0: { label: "P0", tone: "rose"  },
  P1: { label: "P1", tone: "amber" },
  P2: { label: "P2", tone: "zinc"  },
  P3: { label: "P3", tone: "zinc"  },
};

/* Tone palette — single source of truth for V3 */
const V3_TONE = {
  zinc:    { fg: "#a1a1aa", bg: "rgba(161,161,170,0.10)", border: "rgba(161,161,170,0.22)", solid: "#71717a" },
  sky:     { fg: "#7dd3fc", bg: "rgba(56,189,248,0.10)",  border: "rgba(56,189,248,0.25)",  solid: "#38bdf8" },
  indigo:  { fg: "#a5b4fc", bg: "rgba(99,102,241,0.10)",  border: "rgba(99,102,241,0.28)",  solid: "#6366f1" },
  teal:    { fg: "#5eead4", bg: "rgba(20,184,166,0.10)",  border: "rgba(20,184,166,0.28)",  solid: "#14b8a6" },
  violet:  { fg: "#c4b5fd", bg: "rgba(124,58,237,0.10)",  border: "rgba(124,58,237,0.30)",  solid: "#7c3aed" },
  emerald: { fg: "#86efac", bg: "rgba(34,197,94,0.10)",   border: "rgba(34,197,94,0.28)",   solid: "#22c55e" },
  amber:   { fg: "#fcd34d", bg: "rgba(245,158,11,0.10)",  border: "rgba(245,158,11,0.30)",  solid: "#f59e0b" },
  rose:    { fg: "#fda4af", bg: "rgba(244,63,94,0.10)",   border: "rgba(244,63,94,0.30)",   solid: "#f43f5e" },
};

/* ════════════════════════════════════════════════════════════════
   ATOMS — labeled, restrained, monochrome surfaces.
   ════════════════════════════════════════════════════════════════ */

function StatusBadge({ status, size = "sm", showIntent = false }) {
  const s = V3_STATUS[status] || V3_STATUS.draft;
  const t = V3_TONE[s.tone];
  const px = size === "sm" ? { padding: "2px 7px", fontSize: 10.5 } : { padding: "3px 9px", fontSize: 11.5 };
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 5,
      borderRadius: 4,
      background: t.bg, border: `1px solid ${t.border}`, color: t.fg,
      fontWeight: 600, letterSpacing: ".01em",
      fontFamily: "var(--font-sans)",
      ...px,
    }}>
      {showIntent && (
        <span style={{
          width: 5, height: 5, borderRadius: 1, background: t.solid,
          boxShadow: s.intent === "ok" ? `0 0 4px ${t.solid}` : undefined,
        }}/>
      )}
      {s.label}
    </span>
  );
}

function PriorityBadge({ priority, size = "sm" }) {
  const p = V3_PRIORITY[priority];
  if (!p) return null;
  const t = V3_TONE[p.tone];
  const px = size === "sm" ? { padding: "1px 5px", fontSize: 10 } : { padding: "2px 7px", fontSize: 11 };
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 0,
      borderRadius: 3,
      background: t.bg, border: `1px solid ${t.border}`, color: t.fg,
      fontWeight: 700, fontFamily: "var(--font-mono)",
      letterSpacing: 0,
      ...px,
    }}>
      {p.label}
    </span>
  );
}

/* Receipt-stage micro indicator — 4 dots */
function ReceiptStage({ stage = 0, falseProgress = false, size = "sm" }) {
  const dot = size === "sm" ? 5 : 6;
  return (
    <div style={{ display: "inline-flex", alignItems: "center", gap: 3 }}>
      {V3_STAGES.map((label, i) => {
        const lit = i <= stage;
        const fp = falseProgress && i === 2;
        const color = fp ? "#f59e0b" : lit ? "#5eead4" : "rgba(255,255,255,.10)";
        return (
          <span
            key={label}
            title={label}
            style={{
              width: dot, height: dot, borderRadius: 1,
              background: color,
              boxShadow: lit && !fp ? `0 0 4px ${color}` : undefined,
              border: fp ? "1px solid #f59e0b" : "none",
              backgroundImage: fp
                ? "repeating-linear-gradient(45deg, #f59e0b 0 2px, transparent 2px 4px)"
                : undefined,
            }}
          />
        );
      })}
    </div>
  );
}

/* Age tag — monospace + auto-color when stale */
function AgeTag({ age, stale = false, size = "sm" }) {
  const fontSize = size === "sm" ? 10.5 : 11.5;
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 3,
      fontFamily: "var(--font-mono)",
      fontSize,
      color: stale ? "#fcd34d" : "var(--text-soft)",
      letterSpacing: 0,
    }}>
      <span style={{ opacity: .7 }}>⏱</span>{age}
    </span>
  );
}

/* Stripe pattern utility — for false-progress / no-heartbeat strip */
function StripeStrip({ color = "#f59e0b", height = 2 }) {
  return (
    <div style={{
      height,
      backgroundImage: `repeating-linear-gradient(45deg, ${color} 0 4px, transparent 4px 8px)`,
      opacity: .55,
    }}/>
  );
}

/* ════════════════════════════════════════════════════════════════
   SLIM CARD — V3's card primitive.
   3 zones max:
     1. identity row (title + agent + priority)
     2. status row (status badge + receipt stage + age)
     3. signal line (1 line, ≤90c, role-colored)
   No description. No project chip. No 'next action' button on card.
   Click → drawer.
   ════════════════════════════════════════════════════════════════ */

function V3Card({ task, dense = false, selected = false, onClick }) {
  const s = V3_STATUS[task.status] || V3_STATUS.draft;
  const tone = V3_TONE[s.tone];
  const isFalse = !!s.falseProgress;
  const isDanger = s.intent === "danger";
  const isReview = s.intent === "review";

  // Left rail color — MEANING, not decoration:
  // danger → rose, review → violet, no-heartbeat → striped amber, ok → teal, neutral → invisible
  const railColor =
    isDanger ? V3_TONE.rose.solid :
    isReview ? V3_TONE.violet.solid :
    isFalse  ? V3_TONE.amber.solid :
    s.intent === "ok" ? V3_TONE.teal.solid :
    "transparent";

  const railStyle = isFalse
    ? { backgroundImage: `repeating-linear-gradient(180deg, ${railColor} 0 6px, transparent 6px 10px)` }
    : { background: railColor };

  const padY = dense ? 8 : 10;
  const padX = dense ? 10 : 12;

  return (
    <button
      onClick={onClick}
      style={{
        all: "unset", cursor: "pointer", display: "block", textAlign: "left",
        position: "relative",
        width: "100%", boxSizing: "border-box",
        background: selected ? "rgba(255,255,255,.04)" : "#0f0f10",
        border: `1px solid ${selected ? "rgba(255,255,255,.14)" : "rgba(255,255,255,.06)"}`,
        borderRadius: 8,
        padding: `${padY}px ${padX}px ${padY}px ${padX + 6}px`,
        boxShadow: selected ? "0 0 0 2px rgba(124,58,237,.18)" : undefined,
      }}
    >
      {/* meaning rail */}
      <span style={{
        position: "absolute", left: 0, top: 4, bottom: 4, width: 3,
        borderRadius: "2px 0 0 2px",
        ...railStyle,
      }}/>

      {/* row 1: title + agent + priority */}
      <div style={{ display: "flex", alignItems: "flex-start", gap: 8 }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{
            fontSize: dense ? 12.5 : 13.5, fontWeight: 600, color: "white",
            letterSpacing: "-0.005em", lineHeight: 1.3,
            display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical",
            overflow: "hidden", textOverflow: "ellipsis",
          }}>
            <span style={{
              fontFamily: "var(--font-mono)", fontSize: dense ? 10.5 : 11,
              color: "var(--text-dim)", fontWeight: 500,
              marginRight: 6, letterSpacing: 0,
            }}>
              {task.code}
            </span>
            {task.title}
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 5, flexShrink: 0 }}>
          {task.priority && <PriorityBadge priority={task.priority}/>}
          <AgentBadge name={task.agent} size="xs"/>
        </div>
      </div>

      {/* row 2: status + receipt-stage + age */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 8 }}>
        <StatusBadge status={task.status} showIntent/>
        <ReceiptStage stage={s.stage} falseProgress={isFalse}/>
        <span style={{ flex: 1 }}/>
        {task.age && <AgeTag age={task.age} stale={!!task.stale}/>}
      </div>

      {/* row 3: 1 signal line, role-colored */}
      {task.signal && (
        <div style={{
          marginTop: 7, paddingTop: 7,
          borderTop: "1px dashed rgba(255,255,255,.06)",
          fontSize: dense ? 11.5 : 12, lineHeight: 1.4,
          color: isDanger ? V3_TONE.rose.fg
               : isReview ? V3_TONE.violet.fg
               : isFalse  ? V3_TONE.amber.fg
               : "var(--text-soft)",
          whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
        }}>
          {isDanger ? "⛔ " : isReview ? "◆ " : isFalse ? "⚠ " : ""}
          {task.signal}
        </div>
      )}
    </button>
  );
}

/* ════════════════════════════════════════════════════════════════
   LANE HEADER — single line. Tone dot + name + count + hint.
   ════════════════════════════════════════════════════════════════ */

function V3LaneHeader({ lane, count, dense = false }) {
  const t = V3_TONE[lane.tone];
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 8,
      padding: dense ? "0 0 6px" : "0 4px 8px",
      borderBottom: "1px solid rgba(255,255,255,.06)",
    }}>
      <span style={{
        width: 6, height: 6, borderRadius: 1, background: t.solid,
        boxShadow: `0 0 6px ${t.solid}`,
      }}/>
      <span style={{
        fontSize: 10.5, fontWeight: 600, color: t.fg,
        letterSpacing: ".18em", textTransform: "uppercase",
      }}>{lane.name}</span>
      <span style={{
        fontFamily: "var(--font-mono)", fontSize: 11,
        color: "var(--text-dim)", fontWeight: 600,
      }}>
        {String(count).padStart(2, "0")}
      </span>
      <span style={{ flex: 1 }}/>
      <span style={{
        fontSize: 10, color: "var(--text-dim)",
        fontStyle: "italic", letterSpacing: ".02em",
      }}>{lane.hint}</span>
    </div>
  );
}

/* ════════════════════════════════════════════════════════════════
   V3 SAMPLE TASKS — realistic, from prompt.
   ════════════════════════════════════════════════════════════════ */

const V3_TASKS = [
  // 1 — done with result
  { id: "v3_1", code: "MC-T03", title: "Alerts · Group-Collapse UI for cost-spam fatigue",
    lane: "done", agent: "Pixel", priority: "P2", status: "done", age: "32m",
    signal: "Result available · UI grouped alert noise",
    project: "alerts", workerSession: "ws_01HX7K9P3M2T1V" },

  // 2 — done foundations
  { id: "v3_2", code: "MC-T02", title: "Foundations · Dashboard signal cleanup",
    lane: "done", agent: "Pixel", priority: "P2", status: "done", age: "1h",
    signal: "Completed after accepted receipt + build verification",
    project: "foundations", workerSession: "ws_01HX7G2A8B4F9R" },

  // 3 — draft, waiting dispatch
  { id: "v3_3", code: "MC-T11", title: "Add Taskboard MCP wrappers for receipt/finalize/move",
    lane: "draft", agent: "Forge", priority: "P1", status: "draft", age: "—",
    signal: "Draft waiting for safe dispatch decision",
    project: "mcp", workerSession: null },

  // 4 — failed, needs review
  { id: "v3_4", code: "MC-T17", title: "mc-pending-pickup-smoke.sh · operatorLock missing in payload",
    lane: "failed", agent: "Forge", priority: "P2", status: "failed", age: "12m",
    signal: "Failed · needs blocker/root-cause review before retry",
    project: "smoke", workerSession: "ws_01HX7N4C7E2K5J", retries: "2/3" },

  // 5 — assigned/queued, accepted-no-progress (FALSE-PROGRESS state)
  { id: "v3_5", code: "MC-T18", title: "mc-pending-pickup-smoke.sh · retry",
    lane: "assigned", agent: "Forge", priority: "P2", status: "noheartbeat", age: "8m",
    stale: true,
    signal: "Accepted 8m ago · no heartbeat since pickup",
    project: "smoke", workerSession: "ws_01HX7N9R2D8K1J" },

  // 6 — failed/stale, high-risk
  { id: "v3_6", code: "MC-T22", title: "403 Auto-Pickup Bug · Ingress/Receipt Validation",
    lane: "failed", agent: "Forge", priority: "P1", status: "blocked", age: "2d",
    stale: true,
    signal: "High-risk failed autonomy path · explicit review required",
    project: "ingress", workerSession: "ws_01HX5L1F4P9V2N", retries: "3/3" },

  // Filler tasks for shape
  { id: "v3_7", code: "MC-T05", title: "Compile weekly ops digest",
    lane: "active", agent: "Atlas", priority: "P2", status: "active", age: "6m",
    signal: "Heartbeat green · 78% complete",
    project: "ops", workerSession: "ws_01HX7P0Q5K7M3R" },

  { id: "v3_8", code: "MC-T08", title: "Dispatch new analytics report",
    lane: "active", agent: "Lens", priority: "P2", status: "active", age: "2m",
    signal: "Heartbeat green · 30% complete",
    project: "analytics", workerSession: "ws_01HX7P5W2N1H8B" },

  { id: "v3_9", code: "MC-T12", title: "Summarize competitor launch threads",
    lane: "ready", agent: "James", priority: "P3", status: "queued", age: "—",
    signal: "Queued 20m · awaiting James pickup",
    project: "research" },

  { id: "v3_10", code: "MC-T13", title: "Rotate scratch vault keys",
    lane: "ready", agent: "Forge", priority: "P2", status: "queued", age: "—",
    signal: "Dispatched 4m · pending Forge pickup",
    project: "vault" },

  { id: "v3_11", code: "MC-T19", title: "Review taskboard audit summary before publishing",
    lane: "review", agent: "Pixel", priority: "P1", status: "review", age: "18m",
    signal: "Awaits operator approval · 3 acceptance criteria checked",
    project: "audit", workerSession: "ws_01HX7L8R4M9P3K" },

  { id: "v3_12", code: "MC-T20", title: "Patch Forge rate-limit regression",
    lane: "done", agent: "Forge", priority: "P1", status: "done", age: "2h",
    signal: "Closed 06:18 · regression patched + tests added",
    project: "forge" },

  { id: "v3_13", code: "MC-T21", title: "Draft incident comms for auth flake",
    lane: "draft", agent: "Spark", priority: "P0", status: "draft", age: "—",
    signal: "Draft · 2 days idle · blocking incident close",
    project: "incident" },
];

const V3_TASKS_BY_LANE = (lane) => V3_TASKS.filter(t => t.lane === lane);

/* Sample drawer task with full receipt chain */
const V3_DETAIL_TASK = {
  ...V3_TASKS[3], // failed forge smoke
  description: "Smoke test for the pending-pickup contract on Forge auto-pickup. Verifies operatorLock claim + handshake response + 403 fallback. Last run failed during payload validation: operatorLock field missing.",
  acceptance: [
    { label: "operatorLock field included in payload", ok: false },
    { label: "Handshake response < 2s", ok: true },
    { label: "403 fallback re-emits dispatch token", ok: true },
  ],
  receipts: [
    { stage: "result",     t: "06:18:04", outcome: "fail",     who: "Forge", text: "operatorLock missing · payload schema rejected" },
    { stage: "accepted",   t: "06:14:41", outcome: "ok",       who: "Forge", text: "Worker session acquired · ws_01HX7N4C7E2K5J" },
    { stage: "dispatched", t: "06:14:38", outcome: "ok",       who: "Atlas", text: "Dispatch token issued · dt_2K9P7M" },
    { stage: "draft",      t: "06:12:00", outcome: "ok",       who: "operator", text: "Created from MC-T17 retry queue" },
  ],
  events: [
    { t: "06:18:04", text: "Result · failed", tone: "rose" },
    { t: "06:18:04", text: "Failure reason preserved · op_id=op_8K2P", tone: "rose" },
    { t: "06:14:41", text: "Heartbeat: ok", tone: "teal" },
    { t: "06:14:38", text: "Dispatch accepted", tone: "indigo" },
    { t: "06:12:00", text: "Created from queue", tone: "zinc" },
  ],
  parent: { code: "MC-T16", title: "Auto-pickup pipeline reliability sprint" },
  followUps: [
    { code: "MC-T17b", title: "Add operatorLock to payload schema", status: "draft" },
    { code: "MC-T17c", title: "Add schema-validation pre-flight test", status: "draft" },
  ],
  raw: {
    dispatchToken: "dt_2K9P7M",
    workerSession: "ws_01HX7N4C7E2K5J",
    parentRunId: "run_4K2P9M7B",
    region: "us-east-1",
    schemaVersion: "v2025.04.21",
  },
};

/* Suggested next action — derived per-task */
function suggestedNext(task) {
  const s = V3_STATUS[task.status];
  if (s.intent === "danger" && task.status === "failed") return { label: "Review failure", tone: "rose", primary: false };
  if (s.intent === "danger" && task.status === "blocked") return { label: "Escalate or unblock", tone: "rose", primary: false };
  if (s.falseProgress) return { label: "Force resync or cancel", tone: "amber", primary: false };
  if (task.status === "review") return { label: "Approve & close", tone: "violet", primary: true };
  if (task.status === "draft") return { label: "Dispatch", tone: "violet", primary: true };
  if (task.status === "queued") return { label: "Pause queue", tone: "zinc", primary: false };
  return { label: "Open details", tone: "zinc", primary: false };
}

/* ════════════════════════════════════════════════════════════════
   EXPORT
   ════════════════════════════════════════════════════════════════ */

Object.assign(window, {
  V3_LANES, V3_STAGES, V3_STATUS, V3_PRIORITY, V3_TONE,
  V3_TASKS, V3_TASKS_BY_LANE, V3_DETAIL_TASK,
  StatusBadge, PriorityBadge, ReceiptStage, AgeTag, StripeStrip,
  V3Card, V3LaneHeader, suggestedNext,
});
