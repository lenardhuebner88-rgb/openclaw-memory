// V3A — Dense Operator Cockpit (DESKTOP)
// Maximum signal density. 7-lane single-screen kanban with right rail "Truth" panel.
// Designed for: experienced operator, rapid scan, keyboard-driven, status-first.
// Frame: 1440 × 900.

const V3A_W = 1440, V3A_H = 900;

function V3ADesktop() {
  return (
    <div style={{
      width: V3A_W, height: V3A_H,
      background: "#08080a", color: "white",
      fontFamily: "var(--font-sans)",
      display: "flex", flexDirection: "column",
      overflow: "hidden",
    }}>
      <V3ATopChrome/>
      <div style={{
        flex: 1, display: "grid",
        gridTemplateColumns: "1fr 320px",
        minHeight: 0,
      }}>
        <V3ABoard/>
        <V3ARightRail/>
      </div>
    </div>
  );
}

/* ── top chrome: workspace · search · health · operator ───────── */
function V3ATopChrome() {
  return (
    <div style={{
      height: 48, padding: "0 14px",
      display: "flex", alignItems: "center", gap: 12,
      borderBottom: "1px solid rgba(255,255,255,.06)",
      background: "rgba(0,0,0,.4)",
      flexShrink: 0,
    }}>
      {/* identity */}
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <div style={{
          width: 22, height: 22, borderRadius: 5,
          background: "linear-gradient(135deg,#7c3aed,#22d3ee)",
          display: "grid", placeItems: "center",
          fontFamily: "var(--font-mono)", fontSize: 11, fontWeight: 700, color: "#0a0a0d",
        }}>MC</div>
        <div style={{ fontSize: 12, fontWeight: 600, letterSpacing: ".01em" }}>Mission Control</div>
        <span style={{ color: "var(--text-dim)" }}>/</span>
        <div style={{ fontSize: 12, color: "var(--text-soft)" }}>Taskboard</div>
      </div>

      {/* tabs */}
      <div style={{ display: "flex", gap: 2, marginLeft: 16 }}>
        {[
          ["Taskboard", true],
          ["Pipeline", false],
          ["Workers", false],
          ["Alerts", false, 4],
        ].map(([label, on, badge]) => (
          <div key={label} style={{
            padding: "6px 11px", borderRadius: 6,
            fontSize: 12, fontWeight: 500,
            color: on ? "white" : "var(--text-soft)",
            background: on ? "rgba(255,255,255,.06)" : "transparent",
            border: `1px solid ${on ? "rgba(255,255,255,.10)" : "transparent"}`,
            display: "inline-flex", alignItems: "center", gap: 6,
            cursor: "pointer",
          }}>
            {label}
            {badge && (
              <span style={{
                fontFamily: "var(--font-mono)", fontSize: 10, fontWeight: 700,
                background: "rgba(244,63,94,.18)", color: "#fda4af",
                padding: "1px 5px", borderRadius: 3,
              }}>{badge}</span>
            )}
          </div>
        ))}
      </div>

      <div style={{ flex: 1 }}/>

      {/* search */}
      <div style={{
        display: "flex", alignItems: "center", gap: 6,
        padding: "5px 9px", borderRadius: 6,
        background: "rgba(255,255,255,.04)", border: "1px solid rgba(255,255,255,.06)",
        width: 280,
      }}>
        <span style={{ color: "var(--text-dim)", fontSize: 11 }}>⌕</span>
        <span style={{ fontSize: 11.5, color: "var(--text-dim)", flex: 1 }}>
          Search · jump to task, agent, run id…
        </span>
        <span style={{
          fontFamily: "var(--font-mono)", fontSize: 9.5, fontWeight: 600,
          color: "var(--text-dim)",
          padding: "1px 5px", borderRadius: 3,
          border: "1px solid rgba(255,255,255,.10)",
        }}>⌘K</span>
      </div>

      {/* health pill */}
      <div style={{
        display: "flex", alignItems: "center", gap: 6,
        padding: "4px 9px", borderRadius: 999,
        background: "rgba(245,158,11,.10)", border: "1px solid rgba(245,158,11,.28)",
        color: "#fcd34d",
      }}>
        <span style={{
          width: 6, height: 6, borderRadius: 999, background: "#f59e0b",
          boxShadow: "0 0 6px #f59e0b",
          animation: "mc-live-glow 2s ease-in-out infinite",
        }}/>
        <span style={{ fontSize: 10.5, fontWeight: 600, letterSpacing: ".06em", textTransform: "uppercase" }}>
          1 stale · 2 failed
        </span>
      </div>

      <div style={{
        width: 26, height: 26, borderRadius: 999,
        background: "linear-gradient(135deg,#3b82f6,#7c3aed)",
        display: "grid", placeItems: "center",
        fontFamily: "var(--font-mono)", fontSize: 10, fontWeight: 700,
      }}>PP</div>
    </div>
  );
}

/* ── board: 7 lanes wide ──────────────────────────────────────── */
function V3ABoard() {
  return (
    <div style={{
      display: "flex", flexDirection: "column", minHeight: 0,
      background: "#08080a",
    }}>
      {/* board sub-toolbar */}
      <div style={{
        height: 38, padding: "0 14px",
        display: "flex", alignItems: "center", gap: 10,
        borderBottom: "1px solid rgba(255,255,255,.06)",
        flexShrink: 0,
      }}>
        <div style={{ display: "flex", gap: 1, padding: 2,
          background: "rgba(255,255,255,.04)", borderRadius: 6,
          border: "1px solid rgba(255,255,255,.06)",
        }}>
          {["All", "Mine", "Failing", "Stale", "Review"].map((l, i) => (
            <div key={l} style={{
              padding: "3px 9px", borderRadius: 4, fontSize: 11, fontWeight: 500,
              color: i === 0 ? "white" : "var(--text-soft)",
              background: i === 0 ? "rgba(255,255,255,.08)" : "transparent",
              cursor: "pointer",
            }}>{l}</div>
          ))}
        </div>
        <div style={{
          fontSize: 11, color: "var(--text-dim)", letterSpacing: ".02em",
          fontFamily: "var(--font-mono)",
        }}>13 tasks · 6 agents · last sync 4s ago</div>

        <div style={{ flex: 1 }}/>

        {/* density toggle */}
        <div style={{ display: "flex", gap: 1, padding: 2,
          background: "rgba(255,255,255,.04)", borderRadius: 6,
          border: "1px solid rgba(255,255,255,.06)",
        }}>
          {["Dense", "Comfy"].map((l, i) => (
            <div key={l} style={{
              padding: "3px 9px", borderRadius: 4, fontSize: 11, fontWeight: 500,
              color: i === 0 ? "white" : "var(--text-soft)",
              background: i === 0 ? "rgba(255,255,255,.08)" : "transparent",
              cursor: "pointer",
            }}>{l}</div>
          ))}
        </div>
        <div style={{
          fontSize: 11, color: "var(--text-soft)",
          padding: "4px 9px", borderRadius: 6,
          border: "1px solid rgba(255,255,255,.10)",
          cursor: "pointer",
        }}>+ New task</div>
      </div>

      {/* 7-lane grid */}
      <div style={{
        flex: 1, padding: "10px 12px 14px",
        display: "grid",
        gridTemplateColumns: "repeat(7, 1fr)",
        gap: 8,
        minHeight: 0,
      }}>
        {V3_LANES.map(lane => (
          <V3ALane key={lane.id} lane={lane}/>
        ))}
      </div>
    </div>
  );
}

function V3ALane({ lane }) {
  const tasks = V3_TASKS_BY_LANE(lane.id);
  const t = V3_TONE[lane.tone];

  return (
    <div style={{
      display: "flex", flexDirection: "column", minHeight: 0,
      borderRadius: 8,
      background: "rgba(255,255,255,.015)",
    }}>
      <div style={{ padding: "10px 8px 0" }}>
        <V3LaneHeader lane={lane} count={tasks.length} dense/>
      </div>
      <div style={{
        flex: 1, padding: "8px 6px 10px",
        display: "flex", flexDirection: "column", gap: 6,
        overflow: "hidden",
      }}>
        {tasks.length === 0 ? (
          <div style={{
            margin: 8, padding: "16px 10px",
            border: `1px dashed ${t.border}`, borderRadius: 6,
            fontSize: 10.5, color: "var(--text-dim)",
            textAlign: "center", lineHeight: 1.5,
          }}>
            <div style={{ fontSize: 14, marginBottom: 4, opacity: .5 }}>—</div>
            no {lane.name.toLowerCase()}
          </div>
        ) : tasks.map(task => (
          <V3Card key={task.id} task={task} dense
            selected={task.id === "v3_4"}
          />
        ))}
      </div>
    </div>
  );
}

/* ── right rail: Truth panel + suggested next + Atlas steer ───── */
function V3ARightRail() {
  return (
    <div style={{
      borderLeft: "1px solid rgba(255,255,255,.06)",
      background: "rgba(0,0,0,.3)",
      display: "flex", flexDirection: "column",
      overflow: "hidden",
    }}>
      <div style={{ padding: "12px 14px 8px",
        borderBottom: "1px solid rgba(255,255,255,.06)",
      }}>
        <Eyebrow>Truth · System state</Eyebrow>
      </div>

      <div style={{ padding: 14, display: "flex", flexDirection: "column", gap: 10 }}>
        {/* Honest counters: dashboard truth must match taskboard */}
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
          <TruthChip label="Active" value="2" tone="teal"  detail="hb green"/>
          <TruthChip label="Review" value="1" tone="violet" detail="awaits operator"/>
          <TruthChip label="Stale"  value="1" tone="amber"  detail="no heartbeat"/>
          <TruthChip label="Failed" value="2" tone="rose"   detail="needs review"/>
        </div>

        {/* Atlas operator suggestion */}
        <div style={{
          marginTop: 4, padding: 10, borderRadius: 8,
          background: "rgba(124,58,237,.08)", border: "1px solid rgba(124,58,237,.28)",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
            <span style={{
              width: 16, height: 16, borderRadius: 3,
              background: "rgba(124,58,237,.20)", color: "#c4b5fd",
              display: "grid", placeItems: "center",
              fontFamily: "var(--font-mono)", fontSize: 9, fontWeight: 700,
            }}>AT</span>
            <div style={{ fontSize: 10.5, fontWeight: 600, color: "#c4b5fd",
              letterSpacing: ".14em", textTransform: "uppercase",
            }}>Atlas · suggests next</div>
          </div>
          <div style={{ fontSize: 12.5, lineHeight: 1.45, color: "white" }}>
            Review <span style={{ fontFamily: "var(--font-mono)", color: "#fda4af" }}>MC-T17</span> failure: payload schema rejected operatorLock. Two follow-ups already drafted.
          </div>
          <div style={{ display: "flex", gap: 6, marginTop: 8 }}>
            <V3Btn primary>Open MC-T17</V3Btn>
            <V3Btn>Dismiss</V3Btn>
          </div>
        </div>

        {/* selected task pre-detail */}
        <div style={{ marginTop: 4 }}>
          <Eyebrow>Selected · MC-T17</Eyebrow>
          <div style={{ marginTop: 6, padding: 10, borderRadius: 8,
            background: "rgba(244,63,94,.06)", border: "1px solid rgba(244,63,94,.20)",
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
              <StatusBadge status="failed" showIntent/>
              <PriorityBadge priority="P2"/>
              <span style={{ flex: 1 }}/>
              <AgeTag age="12m" stale/>
            </div>
            <div style={{ fontSize: 12.5, fontWeight: 600, lineHeight: 1.35, marginBottom: 6 }}>
              mc-pending-pickup-smoke.sh · operatorLock missing in payload
            </div>
            <ReceiptDots/>
            <div style={{ marginTop: 8, fontSize: 11.5, lineHeight: 1.45, color: "#fda4af" }}>
              ⛔ Result · failed · payload schema rejected
            </div>
            <div style={{ display: "flex", gap: 6, marginTop: 9 }}>
              <V3Btn primary tone="rose">Review failure</V3Btn>
              <V3Btn>Open drawer</V3Btn>
            </div>
          </div>
        </div>

        {/* worker session strip */}
        <div style={{
          marginTop: 4,
          padding: "8px 10px", borderRadius: 6,
          background: "rgba(255,255,255,.02)", border: "1px solid rgba(255,255,255,.06)",
          display: "flex", flexDirection: "column", gap: 4,
        }}>
          <Eyebrow>Worker session</Eyebrow>
          <div style={{ fontFamily: "var(--font-mono)", fontSize: 10.5, color: "var(--text-soft)" }}>
            ws_01HX7N4C7E2K5J · Forge · region us-east-1
          </div>
          <div style={{ fontFamily: "var(--font-mono)", fontSize: 10.5, color: "var(--text-soft)" }}>
            dt_2K9P7M · run_4K2P9M7B
          </div>
        </div>
      </div>
    </div>
  );
}

/* helpers */
function TruthChip({ label, value, tone, detail }) {
  const t = V3_TONE[tone];
  return (
    <div style={{
      padding: "8px 10px", borderRadius: 6,
      background: t.bg, border: `1px solid ${t.border}`,
    }}>
      <div style={{
        fontSize: 9.5, color: t.fg, fontWeight: 600,
        letterSpacing: ".18em", textTransform: "uppercase",
      }}>{label}</div>
      <div style={{
        fontSize: 22, fontWeight: 600, color: "white",
        fontFamily: "var(--font-mono)", letterSpacing: "-0.02em",
      }}>{value}</div>
      <div style={{ fontSize: 10, color: "var(--text-dim)" }}>{detail}</div>
    </div>
  );
}

function ReceiptDots() {
  // Failed: stages 0,1,2 ok, stage 3 = fail (rose)
  const stages = [
    { label: "draft",      ok: true },
    { label: "dispatched", ok: true },
    { label: "accepted",   ok: true },
    { label: "result",     ok: false, fail: true },
  ];
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 0,
      padding: "5px 8px", borderRadius: 6,
      background: "rgba(0,0,0,.3)",
      border: "1px solid rgba(255,255,255,.04)",
    }}>
      {stages.map((s, i) => (
        <React.Fragment key={s.label}>
          <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
            <span style={{
              width: 7, height: 7, borderRadius: 1,
              background: s.fail ? "#f43f5e" : s.ok ? "#5eead4" : "rgba(255,255,255,.10)",
              boxShadow: s.fail ? "0 0 6px #f43f5e" : s.ok ? "0 0 4px #5eead4" : undefined,
            }}/>
            <span style={{
              fontSize: 9.5, color: s.fail ? "#fda4af" : s.ok ? "var(--text-soft)" : "var(--text-dim)",
              letterSpacing: ".06em", textTransform: "uppercase", fontWeight: 600,
            }}>{s.label}</span>
          </div>
          {i < stages.length - 1 && (
            <span style={{
              flex: 1, height: 1, margin: "0 6px",
              background: s.ok ? "rgba(94,234,212,.30)" : "rgba(255,255,255,.06)",
            }}/>
          )}
        </React.Fragment>
      ))}
    </div>
  );
}

function V3Btn({ children, primary, tone = "violet" }) {
  const t = V3_TONE[tone];
  if (primary) return (
    <button style={{
      all: "unset", cursor: "pointer",
      padding: "5px 10px", borderRadius: 5,
      background: t.solid, color: tone === "rose" ? "white" : "white",
      fontSize: 11.5, fontWeight: 600, letterSpacing: ".01em",
      boxShadow: `0 0 12px ${t.solid}40`,
    }}>{children}</button>
  );
  return (
    <button style={{
      all: "unset", cursor: "pointer",
      padding: "5px 10px", borderRadius: 5,
      background: "rgba(255,255,255,.04)",
      border: "1px solid rgba(255,255,255,.10)",
      color: "var(--text-soft)",
      fontSize: 11.5, fontWeight: 500,
    }}>{children}</button>
  );
}

Object.assign(window, { V3ADesktop, V3A_W, V3A_H, TruthChip, ReceiptDots, V3Btn });
