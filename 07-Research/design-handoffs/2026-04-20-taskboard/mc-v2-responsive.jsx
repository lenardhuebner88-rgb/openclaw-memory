// V2 responsive — Tablet (768×1024) + Desktop (1440×900) breakpoints.
// Same tokens, same AgentBadge, same hero/sparkline/urgent card.
// Chip-swap disappears ≥768px; right rail appears ≥1024px.

/* ── Compressed horizontal hero strip for desktop ───────────── */
function V2HeroStrip({ stalled = 3, compact = false }) {
  const urgencyTone = stalled >= 3 ? "#f43f5e" : "#f59e0b";
  const urgencyGlow = stalled >= 3 ? "rgba(244,63,94,.35)" : "rgba(245,158,11,.35)";
  const isActivelyStale = stalled >= 1;
  const ok = stalled === 0;
  return (
    <div style={{
      border: ok ? "1px solid rgba(34,197,94,.25)" : "1px solid rgba(244,63,94,.25)",
      background: ok
        ? "linear-gradient(90deg, rgba(34,197,94,.05), #111111 40%)"
        : "linear-gradient(90deg, rgba(244,63,94,.07), #111111 40%)",
      borderRadius: 14, padding: "14px 16px",
      boxShadow: "0 4px 24px rgba(0,0,0,.35)",
      display: "grid",
      gridTemplateColumns: "auto 1fr auto",
      alignItems: "center",
      gap: 24, position: "relative", overflow: "hidden",
    }}>
      {/* Number + label block */}
      <div style={{ display: "flex", alignItems: "center", gap: 14, position: "relative" }}>
        <div style={{
          position: "absolute", left: -12, top: -8,
          width: 100, height: 100, pointerEvents: "none",
          background: "radial-gradient(circle, rgba(124,58,237,0.08), transparent 60%)",
          filter: "blur(8px)",
        }}/>
        <div style={{ position: "relative" }}>
          <Eyebrow style={{ marginBottom: 4, fontSize: 9 }}>MORNING STATUS</Eyebrow>
          <div style={{ display: "flex", alignItems: "baseline", gap: 10 }}>
            <div className="mc-num" style={{
              fontSize: 48, fontWeight: 600,
              color: ok ? "#bbf7d0" : "#fecdd3",
              letterSpacing: "-0.04em", lineHeight: 0.9,
              fontVariantNumeric: "tabular-nums",
            }}>{stalled}</div>
            <div style={{ lineHeight: 1.15 }}>
              <div style={{ fontSize: 14, fontWeight: 600, color: "white", letterSpacing: "-0.01em" }}>
                {ok ? "All clear" : `stalled`}
              </div>
              <MicroMeta style={{ fontSize: 10.5, marginTop: 2 }}>
                19 active · 117 dispatched
              </MicroMeta>
            </div>
          </div>
        </div>
      </div>

      {/* Inline sparkline */}
      <div style={{ minWidth: 0, paddingLeft: 8 }}>
        <Eyebrow style={{ marginBottom: 4, fontSize: 9 }}>PULSE · 2h</Eyebrow>
        <HeartbeatStrip/>
      </div>

      {/* Inline most-urgent CTA */}
      {!ok && (
        <button style={{
          all: "unset", cursor: "pointer",
          padding: "10px 14px 10px 14px",
          borderRadius: 10,
          border: "1px solid var(--accent-border)",
          borderLeft: `3px solid ${urgencyTone}`,
          background: "linear-gradient(90deg, rgba(124,58,237,.12), rgba(124,58,237,.06))",
          boxShadow: `0 0 12px rgba(124,58,237,.25), -1px 0 8px ${urgencyGlow}`,
          minWidth: 260, position: "relative",
        }}>
          {isActivelyStale && (
            <span style={{
              position: "absolute", top: 6, right: 8,
              width: 6, height: 6, borderRadius: 999,
              background: urgencyTone,
              boxShadow: `0 0 6px ${urgencyTone}`,
              animation: "mc-pulse-dot 2s ease-in-out infinite",
            }}/>
          )}
          <div style={{ fontSize: 9, letterSpacing: ".22em", textTransform: "uppercase", fontWeight: 600, color: "#c4b5fd", opacity: .8 }}>
            MOST URGENT
          </div>
          <div style={{
            fontSize: 14, fontWeight: 600, color: "white",
            marginTop: 2, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
            maxWidth: 260, letterSpacing: "-0.01em",
          }}>
            Retry ready: nightly research crawl
          </div>
        </button>
      )}
    </div>
  );
}

/* ── Desktop hover-action card — no swipe, reveals actions on hover ── */
function V2HoverCard({ task, selected = false, showKbd = false }) {
  const [hover, setHover] = useState(false);
  const es = MC.execState[task.state] || MC.execState.queued;
  const pr = MC.priority[task.priority] || MC.priority.medium;
  const live = task.state === "dispatched-active";
  const isDone = task.state === "done";
  const needsRetry = task.state === "blocked" || task.callout;

  return (
    <div
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{
        position: "relative",
        border: selected ? "1px solid var(--accent-border)" : "1px solid rgba(255,255,255,.08)",
        background: selected ? "rgba(124,58,237,.06)" : "#141414",
        borderRadius: 12, padding: 12,
        boxShadow: selected ? "0 0 0 2px rgba(124,58,237,.20), 0 4px 24px rgba(0,0,0,.35)" : "0 4px 24px rgba(0,0,0,.35)",
        cursor: "pointer",
        transition: "all 150ms ease",
      }}>
      {/* title + agent */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 8 }}>
        <h3 style={{
          margin: 0, fontSize: 13, fontWeight: 600, color: "white",
          lineHeight: 1.3, letterSpacing: "-0.005em", textWrap: "pretty", flex: 1,
        }}>{task.title}</h3>
        <AgentBadge name={task.agent} size="sm"/>
      </div>

      {/* pills */}
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
        <MicroMeta style={{ marginTop: 6, color: "#fecdd3", fontSize: 10.5 }}>
          ⛔ {task.callout}
        </MicroMeta>
      )}

      {/* hover action row */}
      <div style={{
        display: "flex", gap: 6, marginTop: 10,
        opacity: hover || selected ? 1 : 0,
        transform: hover || selected ? "translateY(0)" : "translateY(4px)",
        transition: "all 180ms ease",
        height: hover || selected ? "auto" : 0,
        overflow: "hidden",
      }}>
        <button style={{
          all: "unset", cursor: "pointer", flex: 1, textAlign: "center",
          fontSize: 11, fontWeight: 500, minHeight: 30,
          display: "inline-flex", alignItems: "center", justifyContent: "center",
          borderRadius: 8, border: "1px solid rgba(255,255,255,.10)",
          background: "rgba(255,255,255,.04)", color: "var(--text)",
        }}>Details</button>
        <button style={{
          all: "unset", cursor: "pointer", flex: 1, textAlign: "center",
          fontSize: 11, fontWeight: 500, minHeight: 30,
          display: "inline-flex", alignItems: "center", justifyContent: "center",
          borderRadius: 8, border: "1px solid rgba(245,158,11,.3)",
          background: "rgba(245,158,11,.10)", color: "#fde68a",
        }}>Admin</button>
        <button style={{
          all: "unset", cursor: "pointer", flex: 1, textAlign: "center",
          fontSize: 11, fontWeight: 500, minHeight: 30,
          display: "inline-flex", alignItems: "center", justifyContent: "center",
          borderRadius: 8, border: "1px solid var(--accent-border)",
          background: "var(--accent-wash)", color: "var(--accent-text)",
        }}>◆ {needsRetry ? "Retry" : "Dispatch"}</button>
      </div>

      {showKbd && selected && (
        <div style={{
          position: "absolute", top: 8, right: 8,
          display: "flex", gap: 3,
        }}>
          <Kbd>x</Kbd><Kbd>d</Kbd>
        </div>
      )}
    </div>
  );
}

function Kbd({ children }) {
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", justifyContent: "center",
      minWidth: 18, height: 18, padding: "0 5px",
      background: "rgba(0,0,0,.4)", border: "1px solid rgba(255,255,255,.10)",
      borderRadius: 4, fontSize: 10, fontFamily: "var(--font-mono)",
      color: "var(--text-soft)", fontWeight: 600,
    }}>{children}</span>
  );
}

/* ── Lane column (desktop/tablet) ───────────────────────────── */
function V2LaneColumn({ lane, tasks, selected, selectedIdx, showKbd = false }) {
  const dotColor = LANE_DOT[lane.tone] || "#52525b";
  const toneText = {
    rose: "#fecdd3", cyan: "#a5f3fc", sky: "#bae6fd", indigo: "#c7d2fe", emerald: "#bbf7d0",
  }[lane.tone];
  return (
    <div style={{
      background: "#111111",
      border: "1px solid rgba(255,255,255,.06)",
      borderRadius: 14, padding: 12,
      minWidth: 0,
      display: "flex", flexDirection: "column", gap: 8,
    }}>
      {/* lane header */}
      <div style={{
        display: "flex", alignItems: "center", justifyContent: "space-between",
        paddingBottom: 8, borderBottom: "1px solid rgba(255,255,255,.06)",
      }}>
        <div style={{ display: "inline-flex", alignItems: "center", gap: 7 }}>
          <span style={{
            width: 8, height: 8, borderRadius: 999, background: dotColor,
            boxShadow: `0 0 6px ${dotColor}`,
          }}/>
          <span style={{
            fontSize: 10, letterSpacing: ".22em", textTransform: "uppercase",
            fontWeight: 600, color: toneText,
          }}>{lane.name}</span>
        </div>
        <span className="mc-num" style={{
          fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--text-soft)",
          fontWeight: 600,
        }}>{String(tasks.length).padStart(2, "0")}</span>
      </div>
      {/* cards */}
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {tasks.map((t, i) => (
          <V2HoverCard
            key={t.id} task={t}
            selected={selected === lane.id && selectedIdx === i}
            showKbd={showKbd}
          />
        ))}
        {tasks.length === 0 && (
          <div style={{
            border: "1px dashed rgba(255,255,255,.08)", borderRadius: 10,
            padding: "18px 12px", textAlign: "center",
          }}>
            <MicroMeta style={{ fontSize: 11 }}>Empty</MicroMeta>
          </div>
        )}
      </div>
    </div>
  );
}

/* ── Right rail panels for desktop ──────────────────────────── */
function AgentLoadPanel() {
  const rows = [
    { name: "Pixel", load: 4, cap: 5, state: "busy" },
    { name: "Spark", load: 3, cap: 5, state: "busy" },
    { name: "James", load: 2, cap: 5, state: "busy" },
    { name: "Atlas", load: 1, cap: 5, state: "idle" },
    { name: "Forge", load: 1, cap: 5, state: "idle" },
    { name: "Lens",  load: 0, cap: 5, state: "idle" },
  ];
  return (
    <div style={{
      background: "#111111", border: "1px solid var(--border)",
      borderRadius: 12, padding: 14,
    }}>
      <Eyebrow style={{ marginBottom: 10 }}>AGENT LOAD</Eyebrow>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {rows.map(r => (
          <div key={r.name} style={{ display: "flex", alignItems: "center", gap: 9 }}>
            <AgentBadge name={r.name} size="sm"/>
            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "var(--text)" }}>
                <span>{r.name}</span>
                <span className="mc-num" style={{ fontFamily: "var(--font-mono)", color: "var(--text-soft)" }}>
                  {r.load}/{r.cap}
                </span>
              </div>
              <div style={{
                height: 4, background: "rgba(255,255,255,.05)",
                borderRadius: 2, marginTop: 3, overflow: "hidden",
              }}>
                <div style={{
                  width: `${(r.load/r.cap)*100}%`, height: "100%",
                  background: r.state === "busy"
                    ? "linear-gradient(90deg, #7c3aed, #a78bfa)"
                    : "rgba(255,255,255,.15)",
                  boxShadow: r.state === "busy" ? "0 0 6px rgba(124,58,237,.45)" : "none",
                }}/>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ActivityFeed() {
  const items = [
    { ago: "just now", color: "#22c55e", text: "Lens dispatched analytics report" },
    { ago: "2m",  color: "#f43f5e", text: "Pixel blocked · lock #4821" },
    { ago: "4m",  color: "#7c3aed", text: "Forge rotated vault scratch keys" },
    { ago: "12m", color: "#f59e0b", text: "James retry ready · research crawl" },
    { ago: "22m", color: "#22c55e", text: "Atlas closed daily budget review" },
    { ago: "1h",  color: "#38bdf8", text: "Spark drafted incident comms" },
  ];
  return (
    <div style={{
      background: "#111111", border: "1px solid var(--border)",
      borderRadius: 12, padding: 14,
    }}>
      <Eyebrow style={{ marginBottom: 10 }}>ACTIVITY</Eyebrow>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {items.map((it, i) => (
          <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 8 }}>
            <span style={{
              marginTop: 6, width: 6, height: 6, borderRadius: 999,
              background: it.color, boxShadow: `0 0 4px ${it.color}`,
              flexShrink: 0,
            }}/>
            <div style={{ flex: 1, minWidth: 0, lineHeight: 1.35 }}>
              <div style={{ fontSize: 11.5, color: "var(--text)" }}>{it.text}</div>
              <MicroMeta style={{ fontSize: 10, marginTop: 1 }}>{it.ago} ago</MicroMeta>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function QuickActions() {
  const actions = [
    { key: "⌘K", label: "Command palette" },
    { key: "N",  label: "New task" },
    { key: "X",  label: "Dispatch selected" },
    { key: "D",  label: "Admin cleanup" },
    { key: "J / K",  label: "Navigate" },
  ];
  return (
    <div style={{
      background: "#111111", border: "1px solid var(--border)",
      borderRadius: 12, padding: 14,
    }}>
      <Eyebrow style={{ marginBottom: 10 }}>QUICK ACTIONS</Eyebrow>
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        {actions.map(a => (
          <div key={a.key} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "4px 0" }}>
            <span style={{ fontSize: 11.5, color: "var(--text)" }}>{a.label}</span>
            <Kbd>{a.key}</Kbd>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ── Tablet screen 768×1024 ─────────────────────────────────── */
function V2TabletScreen({ stalled = 3 }) {
  const [selectedLane, setSelectedLane] = useState("needs");
  // split lanes into 2 columns (2-col lane view)
  const left  = ["needs", "active"].map(id => MOBILE_LANES.find(l => l.id === id));
  const right = ["ready", "waiting", "done"].map(id => MOBILE_LANES.find(l => l.id === id));
  return (
    <div style={{
      width: "100%", height: "100%", overflow: "hidden",
      display: "flex", flexDirection: "column",
      background: "#0a0a0d",
      backgroundImage: `
        radial-gradient(ellipse 800px 300px at 0% 0%, rgba(124,58,237,0.05), transparent 60%),
        radial-gradient(ellipse 800px 300px at 100% 0%, rgba(124,58,237,0.05), transparent 60%),
        linear-gradient(180deg, #0a0a0d 0%, #08080b 100%)
      `,
    }}>
      {/* header */}
      <div style={{
        padding: "14px 20px", borderBottom: "1px solid var(--border)",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        background: "rgba(15,15,15,.92)", backdropFilter: "blur(6px)",
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{
            width: 30, height: 30, borderRadius: 8,
            border: "1px solid var(--accent-border)", background: "var(--accent-wash)",
            color: "#c4b5fd", display: "inline-flex", alignItems: "center", justifyContent: "center",
            fontSize: 15,
          }}>⚙</div>
          <span style={{ fontSize: 10, letterSpacing: ".24em", color: "var(--text)", fontWeight: 600 }}>
            MISSION CONTROL · TASKBOARD
          </span>
        </div>
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 4,
            padding: "3px 8px", borderRadius: 999,
            border: "1px solid rgba(34,197,94,.20)", background: "rgba(34,197,94,.10)",
            color: "#bbf7d0", fontSize: 9, letterSpacing: ".14em", fontWeight: 700, textTransform: "uppercase",
          }}>
            <span style={{ width: 5, height: 5, borderRadius: 999, background: "#22c55e", boxShadow: "0 0 6px #22c55e" }}/>
            LIVE
          </div>
          <AgentBadge name="pieter_pan" size="sm"/>
        </div>
      </div>

      {/* body */}
      <div style={{ flex: 1, overflowY: "auto", padding: "18px 20px 96px" }}>
        {/* full-width hero */}
        <V2HeroMorning stalled={stalled}/>

        {/* 2-col lanes, no chip-swap */}
        <div style={{ marginTop: 20 }}>
          <Eyebrow style={{ marginBottom: 10 }}>LANES · 2-COL VIEW</Eyebrow>
          <div style={{
            display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14,
          }}>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {left.map(l => (
                <V2LaneColumn key={l.id} lane={l}
                  tasks={MOBILE_TASKS.filter(t => t.lane === l.id)}
                  selected={selectedLane} selectedIdx={-1}
                />
              ))}
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {right.map(l => (
                <V2LaneColumn key={l.id} lane={l}
                  tasks={MOBILE_TASKS.filter(t => t.lane === l.id)}
                  selected={selectedLane} selectedIdx={-1}
                />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* bottom tab bar stays on tablet */}
      <BottomTabBar active="tasks"/>
    </div>
  );
}

/* ── Desktop screen 1440×900 ────────────────────────────────── */
function V2DesktopScreen({ stalled = 3 }) {
  const [selIdx, setSelIdx] = useState(0);
  const [selLane, setSelLane] = useState("needs");
  const [kbdToast, setKbdToast] = useState(null);

  // fake keyboard nav
  useEffect(() => {
    const onKey = (e) => {
      if (e.target.tagName === "INPUT") return;
      if (e.key === "j") { setSelIdx(i => i + 1); setKbdToast("↓ next"); }
      if (e.key === "k") { setSelIdx(i => Math.max(0, i - 1)); setKbdToast("↑ prev"); }
      if (e.key === "x") { setKbdToast("◆ Dispatched"); }
      if (e.key === "d") { setKbdToast("Admin cleanup"); }
      if (kbdToast) setTimeout(() => setKbdToast(null), 1200);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [kbdToast]);

  return (
    <div style={{
      width: "100%", height: "100%", overflow: "hidden",
      display: "flex", flexDirection: "column",
      background: "#0a0a0d",
      backgroundImage: `
        radial-gradient(ellipse 800px 300px at 0% 0%, rgba(124,58,237,0.05), transparent 60%),
        radial-gradient(ellipse 800px 300px at 100% 0%, rgba(124,58,237,0.05), transparent 60%),
        linear-gradient(180deg, #0a0a0d 0%, #08080b 100%)
      `,
      position: "relative",
    }}>
      {/* top bar */}
      <div style={{
        padding: "12px 24px", borderBottom: "1px solid var(--border)",
        display: "flex", alignItems: "center", justifyContent: "space-between",
        background: "rgba(15,15,15,.92)", backdropFilter: "blur(6px)",
        flexShrink: 0,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{
              width: 28, height: 28, borderRadius: 7,
              border: "1px solid var(--accent-border)", background: "var(--accent-wash)",
              color: "#c4b5fd", display: "inline-flex", alignItems: "center", justifyContent: "center",
              fontSize: 14,
            }}>⚙</div>
            <span style={{ fontSize: 10, letterSpacing: ".24em", color: "var(--text)", fontWeight: 600 }}>
              MISSION CONTROL
            </span>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 4 }}>
            {["Taskboard", "Agents", "Vault", "Incidents"].map((n, i) => (
              <span key={n} style={{
                padding: "5px 10px", borderRadius: 8,
                fontSize: 11.5, fontWeight: 500,
                color: i === 0 ? "#c4b5fd" : "var(--text-soft)",
                background: i === 0 ? "var(--accent-wash)" : "transparent",
                border: i === 0 ? "1px solid var(--accent-border)" : "1px solid transparent",
              }}>{n}</span>
            ))}
          </div>
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <div style={{
            display: "flex", alignItems: "center", gap: 6,
            padding: "5px 10px", borderRadius: 8,
            border: "1px solid var(--border)", background: "#141414",
            fontSize: 11, color: "var(--text-soft)",
            minWidth: 220,
          }}>
            <span style={{ opacity: .5 }}>⌕</span>
            Search tasks, agents…
            <Kbd>⌘K</Kbd>
          </div>
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 4,
            padding: "4px 9px", borderRadius: 999,
            border: "1px solid rgba(34,197,94,.20)", background: "rgba(34,197,94,.10)",
            color: "#bbf7d0", fontSize: 9, letterSpacing: ".14em", fontWeight: 700, textTransform: "uppercase",
          }}>
            <span style={{ width: 5, height: 5, borderRadius: 999, background: "#22c55e", boxShadow: "0 0 6px #22c55e" }}/>
            LIVE
          </div>
          <AgentBadge name="pieter_pan" size="sm"/>
        </div>
      </div>

      {/* main grid: content + right rail */}
      <div style={{
        flex: 1, display: "grid",
        gridTemplateColumns: "1fr 280px",
        gap: 16, padding: 16,
        overflow: "hidden", minHeight: 0,
      }}>
        {/* left: hero strip + 5-lane grid */}
        <div style={{ display: "flex", flexDirection: "column", gap: 14, minWidth: 0 }}>
          <V2HeroStrip stalled={stalled}/>

          {/* page title row */}
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div>
              <Eyebrow style={{ marginBottom: 2 }}>TASK OPERATIONS · 5-LANE GRID</Eyebrow>
              <h1 style={{ margin: 0, fontSize: 22, fontWeight: 600, color: "white", letterSpacing: "-0.02em" }}>
                Taskboard
              </h1>
            </div>
            <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
              <span style={{ fontSize: 11, color: "var(--text-soft)" }}>Nav</span>
              <Kbd>j</Kbd><Kbd>k</Kbd>
              <span style={{ fontSize: 11, color: "var(--text-soft)", marginLeft: 6 }}>Action</span>
              <Kbd>x</Kbd><Kbd>d</Kbd>
            </div>
          </div>

          {/* 5-lane grid */}
          <div style={{
            flex: 1, minHeight: 0, overflow: "auto",
            display: "grid",
            gridTemplateColumns: "repeat(5, minmax(0, 1fr))",
            gap: 12,
          }}>
            {MOBILE_LANES.map((l, li) => (
              <V2LaneColumn key={l.id} lane={l}
                tasks={MOBILE_TASKS.filter(t => t.lane === l.id)}
                selected={selLane}
                selectedIdx={selLane === l.id ? selIdx : -1}
                showKbd
              />
            ))}
          </div>
        </div>

        {/* right rail */}
        <div style={{ display: "flex", flexDirection: "column", gap: 12, minHeight: 0, overflowY: "auto" }}>
          <AgentLoadPanel/>
          <ActivityFeed/>
          <QuickActions/>
        </div>
      </div>

      {/* keyboard toast */}
      {kbdToast && (
        <div style={{
          position: "absolute", bottom: 24, left: "50%", transform: "translateX(-50%)",
          padding: "8px 14px", borderRadius: 10,
          background: "rgba(17,17,17,.95)", border: "1px solid var(--accent-border)",
          color: "#c4b5fd", fontSize: 12, fontWeight: 600,
          boxShadow: "0 8px 32px rgba(0,0,0,.4), 0 0 12px rgba(124,58,237,.25)",
          zIndex: 60,
        }}>{kbdToast}</div>
      )}
    </div>
  );
}

/* ── Bezels ─────────────────────────────────────────────────── */
function TabletBezel({ children, width = 768, height = 1024, label }) {
  return (
    <div style={{ position: "relative" }}>
      {label && (
        <div style={{
          position: "absolute", bottom: "100%", left: 0, paddingBottom: 10,
          fontSize: 12, fontWeight: 500, color: "rgba(60,50,40,.7)", whiteSpace: "nowrap",
        }}>{label}</div>
      )}
      <div style={{
        width: width + 24, height: height + 24, padding: 12,
        borderRadius: 40, background: "#1a1a1c",
        boxShadow: "0 1px 3px rgba(0,0,0,.15), 0 12px 40px rgba(0,0,0,.25), inset 0 0 0 2px #000",
      }}>
        <div style={{
          position: "relative", width, height,
          borderRadius: 28, overflow: "hidden",
        }}>{children}</div>
      </div>
    </div>
  );
}

function DesktopBezel({ children, width = 1440, height = 900, label }) {
  return (
    <div style={{ position: "relative" }}>
      {label && (
        <div style={{
          position: "absolute", bottom: "100%", left: 0, paddingBottom: 10,
          fontSize: 12, fontWeight: 500, color: "rgba(60,50,40,.7)", whiteSpace: "nowrap",
        }}>{label}</div>
      )}
      <div style={{
        width: width + 20, height: height + 38, padding: "28px 10px 10px",
        borderRadius: 14, background: "#1a1a1c",
        boxShadow: "0 1px 3px rgba(0,0,0,.15), 0 12px 40px rgba(0,0,0,.25), inset 0 0 0 1px #000",
        position: "relative",
      }}>
        {/* traffic lights */}
        <div style={{
          position: "absolute", top: 11, left: 14, display: "flex", gap: 6,
        }}>
          {["#ff5f57","#febc2e","#28c840"].map(c => (
            <span key={c} style={{ width: 10, height: 10, borderRadius: 999, background: c }}/>
          ))}
        </div>
        <div style={{
          position: "relative", width, height,
          borderRadius: 6, overflow: "hidden",
        }}>{children}</div>
      </div>
    </div>
  );
}

Object.assign(window, {
  V2HeroStrip, V2HoverCard, V2LaneColumn, AgentLoadPanel, ActivityFeed, QuickActions,
  V2TabletScreen, V2DesktopScreen, TabletBezel, DesktopBezel, Kbd,
});
