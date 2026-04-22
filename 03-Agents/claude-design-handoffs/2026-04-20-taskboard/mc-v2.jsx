// V2 — Radical mobile-only. Polished visual presence.

function V2SwipeCard({ task, showGhostHint = false }) {
  const [dx, setDx] = useState(0);
  const [animating, setAnimating] = useState(false);
  const [hasSwipedOnce, setHasSwipedOnce] = useState(!showGhostHint);
  const startX = useRef(0);
  const dragging = useRef(false);
  const es = MC.execState[task.state] || MC.execState.queued;
  const pr = MC.priority[task.priority] || MC.priority.medium;
  const live = task.state === "dispatched-active";
  const isDone = task.state === "done";
  const needsRetry = task.state === "blocked" || task.callout;

  const onDown = (e) => {
    dragging.current = true;
    startX.current = (e.touches?.[0] || e).clientX;
    setAnimating(false);
  };
  const onMove = (e) => {
    if (!dragging.current) return;
    const x = (e.touches?.[0] || e).clientX;
    setDx(x - startX.current);
  };
  const onUp = () => {
    if (!dragging.current) return;
    dragging.current = false;
    setAnimating(true);
    if (Math.abs(dx) > 90) setHasSwipedOnce(true);
    if (dx > 90)       { setDx(360); setTimeout(() => setDx(0), 250); }
    else if (dx < -90) { setDx(-360); setTimeout(() => setDx(0), 250); }
    else setDx(0);
  };

  const rightReveal = Math.max(0, Math.min(120, dx));
  const leftReveal  = Math.max(0, Math.min(120, -dx));

  return (
    <div style={{ position: "relative", borderRadius: 14, overflow: "hidden", padding: "0 4px" }}>
      {/* right swipe action */}
      <div style={{
        position: "absolute", inset: "0 4px", borderRadius: 14,
        display: "flex", alignItems: "center", justifyContent: "flex-start",
        padding: "0 18px",
        background: "linear-gradient(90deg, rgba(124,58,237,.28), rgba(124,58,237,.05))",
        border: "1px solid var(--accent-border)",
        color: "#e9d5ff", opacity: rightReveal > 8 ? 1 : 0,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 18 }}>◆</span>
          <span style={{ fontSize: 13, fontWeight: 600, letterSpacing: ".06em", textTransform: "uppercase" }}>
            {needsRetry ? "Retry" : "Dispatch"}
          </span>
        </div>
      </div>
      {/* left swipe action */}
      <div style={{
        position: "absolute", inset: "0 4px", borderRadius: 14,
        display: "flex", alignItems: "center", justifyContent: "flex-end",
        padding: "0 18px",
        background: "linear-gradient(270deg, rgba(245,158,11,.22), rgba(245,158,11,.04))",
        border: "1px solid rgba(245,158,11,.3)",
        color: "#fde68a", opacity: leftReveal > 8 ? 1 : 0,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ fontSize: 13, fontWeight: 600, letterSpacing: ".06em", textTransform: "uppercase" }}>
            Admin cleanup
          </span>
          <span style={{ fontSize: 16 }}>✕</span>
        </div>
      </div>

      {/* the card */}
      <div
        onTouchStart={onDown} onTouchMove={onMove} onTouchEnd={onUp}
        onMouseDown={onDown} onMouseMove={onMove} onMouseUp={onUp} onMouseLeave={onUp}
        style={{
          position: "relative", zIndex: 2,
          border: "1px solid rgba(255,255,255,.08)", background: "#141414",
          borderRadius: 14, padding: 12,
          boxShadow: "0 4px 24px rgba(0,0,0,.35)",
          transform: `translateX(${dx}px)`,
          transition: animating ? "transform 250ms ease-out" : "none",
          touchAction: "pan-y",
          userSelect: "none",
        }}>
        {/* ghost-chevron hints — first view only */}
        {!hasSwipedOnce && dx === 0 && (
          <>
            <span style={{
              position: "absolute", left: 6, top: "50%", transform: "translateY(-50%)",
              fontSize: 16, color: "rgba(253,230,138,0.55)",
              animation: "v2-ghost-breathe 3s ease-in-out infinite",
              pointerEvents: "none",
            }}>‹</span>
            <span style={{
              position: "absolute", right: 6, top: "50%", transform: "translateY(-50%)",
              fontSize: 16, color: "rgba(196,181,253,0.55)",
              animation: "v2-ghost-breathe 3s ease-in-out infinite",
              animationDelay: "1.5s",
              pointerEvents: "none",
            }}>›</span>
          </>
        )}

        {/* title + agent */}
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 8 }}>
          <h3 style={{
            margin: 0, fontSize: 14, fontWeight: 600, color: "white",
            lineHeight: 1.3, letterSpacing: "-0.005em", textWrap: "pretty", flex: 1,
          }}>{task.title}</h3>
          <AgentBadge name={task.agent} size="sm"/>
        </div>

        {/* 3 pills max */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: 5, marginTop: 8 }}>
          <Pill tone={es.tone} size="sm" dot live={live}>{es.icon} {es.label}</Pill>
          {!isDone && <Pill tone={pr.tone} size="sm">{pr.label}</Pill>}
          {task.age !== "—" && (
            <Pill tone="zinc" size="sm" style={{ fontFamily: "var(--font-mono)", letterSpacing: 0, textTransform: "none" }}>
              ⏱{task.age}
            </Pill>
          )}
        </div>

        {task.callout && (
          <MicroMeta style={{ marginTop: 8, color: "#fecdd3", fontSize: 11 }}>
            ⛔ {task.callout}
          </MicroMeta>
        )}

        {/* swipe hint row — only after first swipe */}
        {hasSwipedOnce && (
          <div style={{
            display: "flex", alignItems: "center", justifyContent: "space-between",
            marginTop: 8, paddingTop: 7, borderTop: "1px dashed rgba(255,255,255,.06)",
          }}>
            <MicroMeta style={{ fontSize: 10, color: "var(--text-dim)" }}>
              ← Admin · swipe · {needsRetry ? "Retry" : "Dispatch"} →
            </MicroMeta>
            <MicroMeta style={{ fontSize: 10, color: "var(--text-dim)" }}>hold ⋯</MicroMeta>
          </div>
        )}
      </div>
    </div>
  );
}

/* lane tone → dominant dot color */
const LANE_DOT = {
  rose:    "#f43f5e",
  cyan:    "#22d3ee",
  sky:     "#38bdf8",
  indigo:  "#818cf8",
  emerald: "#22c55e",
};

function V2SwipeChip({ lane, active, onClick }) {
  const toneBg = {
    rose:    ["rgba(244,63,94,.15)",  "rgba(244,63,94,.35)",  "#fecdd3"],
    cyan:    ["rgba(34,211,238,.12)", "rgba(34,211,238,.3)",  "#a5f3fc"],
    sky:     ["rgba(56,189,248,.12)", "rgba(56,189,248,.3)",  "#bae6fd"],
    indigo:  ["rgba(129,140,248,.12)","rgba(129,140,248,.3)", "#c7d2fe"],
    emerald: ["rgba(34,197,94,.12)",  "rgba(34,197,94,.3)",   "#bbf7d0"],
  }[lane.tone] || ["rgba(255,255,255,.06)", "rgba(255,255,255,.12)", "#f0f0f0"];
  const dotColor = LANE_DOT[lane.tone] || "#52525b";
  return (
    <button onClick={onClick} style={{
      all: "unset", cursor: "pointer", flexShrink: 0,
      display: "inline-flex", flexDirection: "column", alignItems: "flex-start", gap: 3,
      padding: active ? "12px 14px" : "8px 14px",
      borderRadius: 14,
      border: `1px solid ${active ? toneBg[1] : "var(--border)"}`,
      background: active ? toneBg[0] : "#141414",
      minHeight: active ? 60 : 52, minWidth: 92,
      scrollSnapAlign: "start",
      boxShadow: active
        ? `inset 0 1px 0 rgba(255,255,255,.05), inset 0 -1px 0 rgba(0,0,0,.3)`
        : "none",
      transition: "all 200ms ease",
    }}>
      <span style={{
        display: "inline-flex", alignItems: "center", gap: 5,
        fontSize: 9.5, letterSpacing: ".18em", textTransform: "uppercase", fontWeight: 600,
        color: active ? toneBg[2] : "var(--text-soft)",
      }}>
        <span style={{
          width: 6, height: 6, borderRadius: 999,
          background: dotColor,
          boxShadow: active ? `0 0 6px ${dotColor}` : "none",
        }}/>
        {lane.name}
      </span>
      <span className="mc-num" style={{
        fontFamily: "var(--font-mono)", fontSize: 18, fontWeight: 600,
        color: active ? "white" : "var(--text)",
        letterSpacing: "-0.01em", lineHeight: 1,
      }}>{String(lane.count).padStart(2, "0")}</span>
    </button>
  );
}

/* Procedurally-generated 2h sparkline driven by 19 active / 117 dispatched ratio. */
function buildPulse(total = 48) {
  // each bucket ≈ 2.5 min. Amplitude seeded by dispatch rate (117/2h ≈ ~1/min).
  const out = [];
  let stallMinutes = new Set([36, 41]); // recent stalls
  let incidentMinutes = new Set([44]);   // rose incident
  for (let i = 0; i < total; i++) {
    // base: sinusoidal + noise, peaks cluster around "dispatch surges"
    const surge1 = Math.exp(-Math.pow((i - 12) / 5, 2)) * 7;
    const surge2 = Math.exp(-Math.pow((i - 28) / 4, 2)) * 9;
    const baseline = 2 + Math.sin(i / 3) * 1.2 + Math.sin(i / 7) * 0.8;
    const noise = ((i * 2654435761) % 97) / 97 * 2.2;
    let v = baseline + surge1 + surge2 + noise;
    let kind = "ok";
    if (stallMinutes.has(i)) { v = Math.max(v, 10); kind = "stall"; }
    if (incidentMinutes.has(i)) { v = Math.max(v, 12); kind = "incident"; }
    out.push({ v: Math.max(1.5, v), kind });
  }
  return out;
}

function HeartbeatStrip() {
  const data = useMemo(() => buildPulse(48), []);
  const max = Math.max(...data.map(d => d.v));
  return (
    <div>
      <div style={{ display: "flex", alignItems: "flex-end", gap: 2, height: 26, marginTop: 10 }}>
        {data.map((d, i) => {
          const color = d.kind === "incident" ? "#f43f5e"
                      : d.kind === "stall" ? "#f59e0b"
                      : "#22c55e";
          const opacity = d.kind === "ok" ? 0.42 : 1;
          const glow = d.kind !== "ok" ? `0 0 4px ${color}` : "none";
          return (
            <div key={i} style={{
              flex: 1, minWidth: 0,
              height: `${Math.max(3, (d.v / max) * 26)}px`,
              background: color, opacity,
              borderRadius: 1.5,
              boxShadow: glow,
            }}/>
          );
        })}
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 4 }}>
        <MicroMeta style={{ fontSize: 9.5, color: "var(--text-dim)" }}>2h ago</MicroMeta>
        <MicroMeta style={{ fontSize: 9.5, color: "var(--text-dim)" }}>now</MicroMeta>
      </div>
    </div>
  );
}

function V2HeroMorning({ stalled = 3 }) {
  const ok = stalled === 0;
  // urgency tone for left-border on most-urgent card
  const urgencyTone = stalled >= 3 ? "#f43f5e" : "#f59e0b";
  const urgencyGlow = stalled >= 3 ? "rgba(244,63,94,.35)" : "rgba(245,158,11,.35)";
  const isActivelyStale = stalled >= 1;

  return (
    <div style={{
      position: "relative",
      border: ok ? "1px solid rgba(34,197,94,.25)" : "1px solid rgba(244,63,94,.25)",
      background: ok
        ? "linear-gradient(180deg, rgba(34,197,94,.06), rgba(34,197,94,.01) 50%, #111111 100%)"
        : "linear-gradient(180deg, rgba(244,63,94,.08), rgba(244,63,94,.02) 50%, #111111 100%)",
      borderRadius: 18, padding: 14,
      boxShadow: "0 4px 24px rgba(0,0,0,.35)",
      overflow: "hidden",
    }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <Eyebrow>OPERATOR · MORNING STATUS</Eyebrow>
        <MicroMeta style={{ fontSize: 10, color: "var(--text-dim)" }}>20/04/2026 · 06:47</MicroMeta>
      </div>

      {/* confidence readout — the answer, not the caption */}
      <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginTop: 8, position: "relative" }}>
        {/* violet glow behind the number */}
        <div style={{
          position: "absolute", left: -16, top: -12,
          width: 140, height: 140, pointerEvents: "none",
          background: "radial-gradient(circle, rgba(124,58,237,0.08), transparent 60%)",
          filter: "blur(8px)",
        }}/>
        <div className="mc-num" style={{
          position: "relative",
          fontSize: "clamp(56px, 12vw, 88px)",
          fontWeight: 600,
          color: ok ? "#bbf7d0" : "#fecdd3",
          letterSpacing: "-0.04em", lineHeight: 0.9,
          fontVariantNumeric: "tabular-nums",
          fontFeatureSettings: '"tnum" 1, "ss01" 1',
          textShadow: ok ? "0 0 40px rgba(34,197,94,.15)" : "0 0 40px rgba(244,63,94,.15)",
        }}>{stalled}</div>
        <div style={{ flex: 1, lineHeight: 1.2, paddingBottom: 4, position: "relative" }}>
          <div style={{ fontSize: 18, fontWeight: 600, color: "white", letterSpacing: "-0.015em" }}>
            {ok ? "All clear" : `stalled · ${stalled > 1 ? "needs a look" : "needs you"}`}
          </div>
          <MicroMeta style={{ fontSize: 11, marginTop: 4 }}>
            19 active · 117 dispatched · confidence 0%
          </MicroMeta>
        </div>
      </div>

      {/* pulse */}
      <HeartbeatStrip/>

      {/* most urgent — distinguished from lane cards */}
      {!ok && (
        <button style={{
          all: "unset", cursor: "pointer", display: "block", marginTop: 14,
          position: "relative",
          width: "100%", boxSizing: "border-box",
          padding: "12px 14px 12px 17px",
          borderRadius: 12,
          border: "1px solid var(--accent-border)",
          borderLeft: `3px solid ${urgencyTone}`,
          background: "linear-gradient(90deg, rgba(124,58,237,.12), rgba(124,58,237,.06))",
          boxShadow: `0 0 12px rgba(124,58,237,.25), -1px 0 8px ${urgencyGlow}`,
        }}>
          {/* pulse-dot when actively stale */}
          {isActivelyStale && (
            <span style={{
              position: "absolute", top: 8, right: 10,
              width: 6, height: 6, borderRadius: 999,
              background: urgencyTone,
              boxShadow: `0 0 6px ${urgencyTone}`,
              animation: "mc-pulse-dot 2s ease-in-out infinite",
            }}/>
          )}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10 }}>
            <div style={{ minWidth: 0, flex: 1 }}>
              <div style={{ fontSize: 10, letterSpacing: ".22em", textTransform: "uppercase", fontWeight: 600, color: "#c4b5fd", opacity: .8 }}>
                Most urgent
              </div>
              <div style={{
                fontSize: 18, fontWeight: 600, color: "white", marginTop: 4,
                whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
                letterSpacing: "-0.01em", lineHeight: 1.2,
              }}>
                Retry ready: nightly research crawl
              </div>
              <MicroMeta style={{ fontSize: 11, marginTop: 3, color: "#c4b5fd", opacity: .7 }}>
                2/3 retries used · preserved for triage
              </MicroMeta>
            </div>
            <div style={{ fontSize: 18, flexShrink: 0, color: "#c4b5fd" }}>→</div>
          </div>
        </button>
      )}
    </div>
  );
}

function V2LongPressSheet({ task, onClose }) {
  if (!task) return null;
  return (
    <>
      <div onClick={onClose} style={{
        position: "absolute", inset: 0, background: "rgba(0,0,0,.6)",
        backdropFilter: "blur(4px)", zIndex: 60,
      }}/>
      <div style={{
        position: "absolute", left: 8, right: 8, bottom: 82, zIndex: 70,
        border: "1px solid var(--border)", background: "rgba(17,17,17,.98)",
        borderRadius: 22, padding: 14,
        backdropFilter: "blur(12px)",
        boxShadow: "0 -10px 40px rgba(0,0,0,.5)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
          <AgentBadge name={task.agent} size="md"/>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontSize: 13, fontWeight: 600, color: "white", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
              {task.title}
            </div>
            <MicroMeta style={{ fontSize: 10.5 }}>{task.meta}</MicroMeta>
          </div>
        </div>
        {["Details", "Retry", "Cancel"].map((label, i) => (
          <button key={label} style={{
            all: "unset", cursor: "pointer", display: "flex", alignItems: "center", gap: 12,
            width: "100%", boxSizing: "border-box",
            minHeight: 48, padding: "0 14px",
            borderRadius: 12, marginTop: i ? 2 : 0,
            color: i === 2 ? "#fca5a5" : "var(--text)", fontSize: 14, fontWeight: 500,
            background: "transparent",
            borderTop: i ? "1px solid rgba(255,255,255,.05)" : "none",
          }}>
            <span style={{ fontSize: 14, opacity: .6 }}>
              {i === 0 ? "ⓘ" : i === 1 ? "↻" : "✕"}
            </span>
            {label}
          </button>
        ))}
      </div>
    </>
  );
}

function V2Screen() {
  const [active, setActive] = useState("needs");
  const [nav, setNav] = useState("tasks");
  const [sheet, setSheet] = useState(null);
  const pressTimer = useRef(null);
  const tasks = MOBILE_TASKS.filter(t => t.lane === active);

  const holdBind = (task) => ({
    onTouchStart: () => { pressTimer.current = setTimeout(() => setSheet(task), 500); },
    onTouchEnd:   () => clearTimeout(pressTimer.current),
    onMouseDown:  () => { pressTimer.current = setTimeout(() => setSheet(task), 500); },
    onMouseUp:    () => clearTimeout(pressTimer.current),
    onMouseLeave: () => clearTimeout(pressTimer.current),
  });

  return (
    <div style={{
      position: "absolute", inset: 0, paddingTop: 47,
      overflow: "hidden", display: "flex", flexDirection: "column",
    }}>
      <div style={{
        padding: "8px 16px 6px",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        background: "rgba(15,15,15,.95)", backdropFilter: "blur(6px)",
        flexShrink: 0,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{
            width: 24, height: 24, borderRadius: 6,
            border: "1px solid var(--accent-border)", background: "var(--accent-wash)",
            color: "#c4b5fd", display: "inline-flex", alignItems: "center", justifyContent: "center",
            fontSize: 13,
          }}>⚙</div>
          <span style={{ fontSize: 9.5, letterSpacing: ".22em", color: "var(--text)", fontWeight: 600 }}>TASKBOARD</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 4,
            padding: "2px 7px", borderRadius: 999,
            border: "1px solid rgba(34,197,94,.20)", background: "rgba(34,197,94,.10)",
            color: "#bbf7d0", fontSize: 9, letterSpacing: ".14em", fontWeight: 700, textTransform: "uppercase",
          }}>
            <span style={{ width: 5, height: 5, borderRadius: 999, background: "#22c55e", boxShadow: "0 0 6px #22c55e", animation: "mc-live-glow 2s ease-in-out infinite" }}/>
            LIVE
          </div>
          <AgentBadge name="pieter_pan" size="sm"/>
        </div>
      </div>

      <div style={{ flex: 1, overflowY: "auto", padding: "12px 12px 120px" }}>
        <V2HeroMorning stalled={MOBILE_TASKS.filter(t => t.lane === "needs").length}/>

        <div style={{ marginTop: 16, marginBottom: 12 }}>
          <Eyebrow style={{ padding: "0 4px", marginBottom: 8 }}>LANES</Eyebrow>
          <div style={{
            display: "flex", gap: 6, overflowX: "auto",
            scrollSnapType: "x mandatory",
            margin: "0 -12px", padding: "0 12px 4px",
            scrollbarWidth: "none",
          }}>
            {MOBILE_LANES.map(l => (
              <V2SwipeChip key={l.id} lane={l} active={active === l.id} onClick={() => setActive(l.id)}/>
            ))}
          </div>
        </div>

        <div style={{
          display: "flex", alignItems: "center", justifyContent: "space-between",
          padding: "0 2px", marginBottom: 8,
        }}>
          <div style={{ fontSize: 11, letterSpacing: ".22em", textTransform: "uppercase", fontWeight: 600, color: "var(--text)" }}>
            {MOBILE_LANES.find(l => l.id === active)?.name}
            <span className="mc-num" style={{
              marginLeft: 8, fontFamily: "var(--font-mono)", color: "var(--text-soft)",
              fontWeight: 500, letterSpacing: 0,
            }}>{String(tasks.length).padStart(2, "0")}</span>
          </div>
          <button style={{
            all: "unset", cursor: "pointer", fontSize: 10, letterSpacing: ".18em",
            textTransform: "uppercase", fontWeight: 600, color: "var(--text-soft)",
            padding: "4px 8px",
          }}>Sort ↓</button>
        </div>

        <div className="mc-stagger" style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {tasks.map((t, i) => (
            <div key={t.id} {...holdBind(t)}>
              <V2SwipeCard task={t} showGhostHint={i === 0}/>
            </div>
          ))}
          {tasks.length === 0 && (
            <div style={{
              border: "1px dashed rgba(255,255,255,.10)", borderRadius: 14,
              padding: "28px 16px", textAlign: "center",
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
      </div>

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
      <V2LongPressSheet task={sheet} onClose={() => setSheet(null)}/>
    </div>
  );
}

/* inject ghost-breathe keyframes once */
if (!document.getElementById("v2-polish-style")) {
  const s = document.createElement("style");
  s.id = "v2-polish-style";
  s.textContent = `
    @keyframes v2-ghost-breathe {
      0%, 100% { opacity: 0.3; transform: translateY(-50%) translateX(0); }
      50%      { opacity: 0.6; transform: translateY(-50%) translateX(2px); }
    }
    @keyframes mc-pulse-dot {
      0%, 100% { opacity: 1; transform: scale(1); }
      50%      { opacity: 0.5; transform: scale(0.85); }
    }
  `;
  document.head.appendChild(s);
}

Object.assign(window, { V2SwipeCard, V2SwipeChip, V2HeroMorning, V2LongPressSheet, V2Screen, HeartbeatStrip });
