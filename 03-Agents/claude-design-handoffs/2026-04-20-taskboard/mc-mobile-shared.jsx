// Shared mobile primitives, data, and mocks for V1 + V2.
const { useState, useEffect, useRef, useMemo } = React;

/* ── tiny primitives ─────────────────────────────────────────── */
function Pill({ tone = "zinc", dot = false, live = false, glow = false, size = "md", className = "", style = {}, children, ...rest }) {
  const sz = size === "sm"
    ? { padding: "2px 7px", fontSize: 9, letterSpacing: ".14em", minHeight: 18 }
    : { padding: "3px 9px", fontSize: 10, letterSpacing: ".16em", minHeight: 20 };
  return (
    <span
      className={`mc-pill tone-${tone} ${glow ? "mc-pill-glow" : ""} ${className}`}
      style={{
        display: "inline-flex", alignItems: "center", gap: 5,
        border: "1px solid transparent", borderRadius: 999,
        textTransform: "uppercase", fontWeight: 600,
        boxShadow: glow ? "0 0 12px rgba(245,158,11,0.25)" : undefined,
        ...sz, ...style,
      }}
      {...rest}
    >
      {dot && (
        <span
          style={{
            display: "inline-block", width: 6, height: 6, borderRadius: 999,
            background: "currentColor",
            boxShadow: live ? "0 0 6px currentColor" : undefined,
            animation: live ? "mc-live-glow 2s ease-in-out infinite" : undefined,
          }}
        />
      )}
      {children}
    </span>
  );
}

function AgentBadge({ name, size = "sm" }) {
  const meta = MC.agents[name] ?? { badge: "??", color: "#52525b" };
  // New contrast recipe: uniform card-corner anchor, tone-washed bg @0.20,
  // 13px semibold, letter-spacing 0.04em. Size just scales dims.
  const dims = size === "xs" ? { w: 22, h: 22, fs: 10, rad: 6 }
    : size === "sm" ? { w: 28, h: 28, fs: 13, rad: 8 }
    : { w: 34, h: 34, fs: 14, rad: 9 };
  // tone-washed background using agent color at 0.20, border at 0.40, text at full color
  const c = meta.color;
  const hexToRgb = (h) => {
    const v = h.replace("#","");
    const n = parseInt(v.length === 3 ? v.split("").map(c=>c+c).join("") : v, 16);
    return [n>>16 & 255, n>>8 & 255, n & 255];
  };
  const [r,g,b] = hexToRgb(c);
  const dark = c === "#eab308";
  return (
    <span style={{
      width: dims.w, height: dims.h, borderRadius: dims.rad, fontSize: dims.fs,
      background: `rgba(${r},${g},${b},0.20)`,
      color: dark ? "#fde047" : c,
      fontWeight: 600, letterSpacing: "0.04em",
      display: "inline-flex", alignItems: "center", justifyContent: "center",
      border: `1px solid rgba(${r},${g},${b},0.40)`, flexShrink: 0,
      fontFamily: "var(--font-mono)",
    }}>{meta.badge}</span>
  );
}

function Eyebrow({ children, style = {} }) {
  return (
    <div style={{
      fontSize: 10, letterSpacing: ".22em", textTransform: "uppercase",
      fontWeight: 500, color: "var(--text-dim)", lineHeight: 1.3, ...style,
    }}>{children}</div>
  );
}

function MicroMeta({ children, style = {} }) {
  return (
    <div style={{
      fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-soft)",
      lineHeight: 1.4, ...style,
    }}>{children}</div>
  );
}

/* ── bottom tab bar (5 slots, 60px cells) ────────────────────── */
const TABS = [
  { key: "dashboard", icon: "🏠", label: "Home" },
  { key: "tasks", icon: "☑️", label: "Tasks" },
  { key: "alerts", icon: "🚨", label: "Alerts", badge: 2 },
  { key: "team", icon: "👥", label: "Team" },
  { key: "more", icon: "➕", label: "More" },
];

function BottomTabBar({ active = "tasks", onNav }) {
  return (
    <div style={{
      position: "absolute", left: 8, right: 8, bottom: 8,
      display: "grid", gridTemplateColumns: "repeat(5,1fr)", gap: 2,
      border: "1px solid var(--border)",
      background: "rgba(15,15,15,.95)", backdropFilter: "blur(12px)",
      borderRadius: 20, padding: 5,
      boxShadow: "0 -8px 32px rgba(0,0,0,.28)",
      zIndex: 30,
    }}>
      {TABS.map(t => {
        const on = t.key === active;
        return (
          <button key={t.key} onClick={() => onNav?.(t.key)} style={{
            all: "unset", cursor: "pointer", position: "relative",
            display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
            gap: 3, minHeight: 60, borderRadius: 14,
            color: on ? "#c4b5fd" : "var(--text-soft)",
            background: on ? "var(--accent-wash)" : "transparent",
            border: `1px solid ${on ? "var(--accent-border)" : "transparent"}`,
            fontSize: 9.5, letterSpacing: ".14em", textTransform: "uppercase", fontWeight: 600,
            boxShadow: on ? "0 0 12px rgba(124,58,237,.25)" : undefined,
          }}>
            <span style={{ fontSize: 18, lineHeight: 1 }}>{t.icon}</span>
            {t.label}
            {t.badge && (
              <span style={{
                position: "absolute", top: 6, right: 14,
                minWidth: 16, height: 16, padding: "0 4px", borderRadius: 999,
                background: "var(--rose)", color: "white",
                fontFamily: "var(--font-mono)", fontSize: 9, fontWeight: 700,
                display: "inline-flex", alignItems: "center", justifyContent: "center",
                border: "1px solid #0f0f0f",
              }}>{t.badge}</span>
            )}
          </button>
        );
      })}
    </div>
  );
}

/* ── status bar (fake iOS) ───────────────────────────────────── */
function StatusBar({ dark = true }) {
  const color = dark ? "white" : "#111";
  return (
    <div style={{
      height: 47, padding: "0 24px",
      display: "flex", alignItems: "flex-end", justifyContent: "space-between",
      paddingBottom: 8,
      color, fontSize: 15, fontWeight: 600,
      fontFamily: "ui-rounded, -apple-system, system-ui, sans-serif",
      fontVariantNumeric: "tabular-nums",
    }}>
      <div>6:47</div>
      <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
        <svg width="18" height="11" viewBox="0 0 18 11" fill={color}>
          <rect x="0" y="6" width="3" height="5" rx="0.5"/>
          <rect x="5" y="4" width="3" height="7" rx="0.5"/>
          <rect x="10" y="2" width="3" height="9" rx="0.5"/>
          <rect x="15" y="0" width="3" height="11" rx="0.5"/>
        </svg>
        <svg width="16" height="12" viewBox="0 0 16 12" fill="none" stroke={color} strokeWidth="1.2">
          <path d="M1 4.5C3 2.5 5.5 1.5 8 1.5s5 1 7 3" />
          <path d="M3 7c1.5-1.2 3-1.8 5-1.8s3.5.6 5 1.8" />
          <path d="M5.5 9.2c.7-.6 1.5-.9 2.5-.9s1.8.3 2.5.9" />
          <circle cx="8" cy="10.5" r="0.7" fill={color} stroke="none"/>
        </svg>
        <svg width="27" height="12" viewBox="0 0 27 12" fill="none">
          <rect x="0.5" y="0.5" width="22" height="11" rx="2.5" stroke={color} opacity=".5"/>
          <rect x="2" y="2" width="17" height="8" rx="1.2" fill={color}/>
          <rect x="23.5" y="3.5" width="1.5" height="5" rx=".5" fill={color} opacity=".5"/>
        </svg>
      </div>
    </div>
  );
}

/* ── iPhone frame ─────────────────────────────────────────────── */
function PhoneFrame({ children, label = "", width = 390, height = 844, dark = true, chrome = true }) {
  return (
    <div style={{ position: "relative" }}>
      {label && (
        <div style={{
          position: "absolute", bottom: "100%", left: 0, paddingBottom: 10,
          fontSize: 12, fontWeight: 500, color: "rgba(60,50,40,.7)", whiteSpace: "nowrap",
        }}>{label}</div>
      )}
      <div style={{
        width: width + 16, height: height + 16, padding: 8,
        borderRadius: 56, background: "#1a1a1c",
        boxShadow: "0 1px 3px rgba(0,0,0,.15), 0 12px 40px rgba(0,0,0,.25), inset 0 0 0 2px #000",
      }}>
        <div style={{
          position: "relative", width, height,
          background: dark ? "#0a0a0d" : "#fff",
          borderRadius: 48, overflow: "hidden",
          backgroundImage: dark ? `
            radial-gradient(ellipse 800px 300px at 0% 0%, rgba(124,58,237,0.05), transparent 60%),
            radial-gradient(ellipse 800px 300px at 100% 0%, rgba(124,58,237,0.05), transparent 60%),
            linear-gradient(180deg, #0a0a0d 0%, #08080b 100%)
          ` : undefined,
        }}>
          {chrome && <StatusBar dark={dark}/>}
          {/* dynamic island */}
          <div style={{
            position: "absolute", top: 11, left: "50%", transform: "translateX(-50%)",
            width: 124, height: 36, borderRadius: 20, background: "#000", zIndex: 50,
          }}/>
          {children}
        </div>
      </div>
    </div>
  );
}

/* ── annotation pins (number + callout) ──────────────────────── */
function Pin({ n, x, y, side = "right" }) {
  return (
    <div style={{
      position: "absolute", left: x, top: y,
      width: 28, height: 28, borderRadius: 999,
      background: "#7c3aed", color: "white",
      display: "inline-flex", alignItems: "center", justifyContent: "center",
      fontFamily: "ui-sans-serif, system-ui", fontWeight: 700, fontSize: 13,
      boxShadow: "0 0 0 3px rgba(124,58,237,.25), 0 4px 12px rgba(0,0,0,.25)",
      zIndex: 20, transform: "translate(-50%, -50%)",
    }}>{n}</div>
  );
}

function Callout({ n, title, body, x, y, width = 220 }) {
  return (
    <div style={{
      position: "absolute", left: x, top: y, width,
      padding: "12px 14px", background: "#fff",
      borderRadius: 10, zIndex: 15,
      boxShadow: "0 1px 3px rgba(0,0,0,.10), 0 8px 24px rgba(0,0,0,.08)",
      fontFamily: '-apple-system, system-ui, sans-serif',
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
        <span style={{
          width: 20, height: 20, borderRadius: 999, background: "#7c3aed", color: "white",
          display: "inline-flex", alignItems: "center", justifyContent: "center",
          fontSize: 11, fontWeight: 700,
        }}>{n}</span>
        <div style={{ fontSize: 13, fontWeight: 600, color: "#2a1f14" }}>{title}</div>
      </div>
      <div style={{ fontSize: 12, lineHeight: 1.5, color: "#5a4a2a" }}>{body}</div>
    </div>
  );
}

/* ── data: mobile-optimized task list ────────────────────────── */
const MOBILE_TASKS = [
  { id: "m1", title: "Reconcile taskboard audit receipts", lane: "needs", agent: "Pixel", priority: "high", state: "blocked", age: "4m", meta: "Age 3h · mission-control · 2/3 retries", callout: "Blocked · waiting on lock #4821", ruleId: "candidate-for-operatorLock" },
  { id: "m2", title: "Retry ready — nightly research crawl", lane: "needs", agent: "James", priority: "medium", state: "waiting-result", age: "12m", meta: "Age 1d · james", callout: "2/3 retries used. Failure reason preserved for triage.", ruleId: "ready-for-retry" },
  { id: "m3", title: "Inspect stale receipt · auth flake", lane: "needs", agent: "Spark", priority: "urgent", state: "blocked", age: "22m", meta: "Age 2h · incident", callout: "Receipt older than contract window", ruleId: "needs-receipt" },
  { id: "m4", title: "Dispatch new analytics report", lane: "active", agent: "Lens", priority: "medium", state: "dispatched-active", age: "just now", meta: "Age 14m · analytics" },
  { id: "m5", title: "Kick off design review for taskboard v3", lane: "active", agent: "Pixel", priority: "high", state: "dispatched-active", age: "2m", meta: "Age 22m · mission-control" },
  { id: "m6", title: "Compile weekly ops digest", lane: "active", agent: "Atlas", priority: "low", state: "waiting-result", age: "8m", meta: "Age 1h · ops" },
  { id: "m7", title: "Summarize competitor launch threads", lane: "ready", agent: "James", priority: "low", state: "queued", age: "—", meta: "Queued 20m ago · research" },
  { id: "m8", title: "Rotate scratch vault keys", lane: "ready", agent: "Forge", priority: "medium", state: "pending-pickup", age: "—", meta: "Dispatched 4m ago · vault" },
  { id: "m9", title: "Draft incident comms for auth flake", lane: "waiting", agent: "Spark", priority: "urgent", state: "draft", age: "—", meta: "Created 2d ago · incident" },
  { id: "m10", title: "Port admin cleanup modal to shadcn dialog", lane: "waiting", agent: "Pixel", priority: "low", state: "draft", age: "—", meta: "Backlog · mission-control" },
  { id: "m11", title: "Close daily budget review", lane: "done", agent: "Atlas", priority: "low", state: "done", age: "1h", meta: "Closed 11/04 05:32" },
  { id: "m12", title: "Patch Forge rate-limit regression", lane: "done", agent: "Forge", priority: "high", state: "done", age: "2h", meta: "Closed 11/04 03:58" },
];

const MOBILE_LANES = [
  { id: "needs",   name: "Needs attention", count: 3, tone: "rose"    },
  { id: "active",  name: "Active",          count: 3, tone: "cyan"    },
  { id: "ready",   name: "Ready",           count: 2, tone: "sky"     },
  { id: "waiting", name: "Waiting",         count: 2, tone: "indigo"  },
  { id: "done",    name: "Done",            count: 2, tone: "emerald" },
];

Object.assign(window, {
  Pill, AgentBadge, Eyebrow, MicroMeta, BottomTabBar, StatusBar,
  PhoneFrame, Pin, Callout, TABS, MOBILE_TASKS, MOBILE_LANES,
});
