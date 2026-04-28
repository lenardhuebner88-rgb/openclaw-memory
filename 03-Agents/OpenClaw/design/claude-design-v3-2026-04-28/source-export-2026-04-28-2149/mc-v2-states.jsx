// Interaction-state overlays for V2: Details / Admin / Retry / Command / All-Clear
// Each overlay is exported as a standalone component that gets composed
// into a screen + frame on the canvas.

/* ── sample task used across all confirm/detail dialogs ────── */
const SAMPLE_DETAIL_TASK = {
  id: "tsk_7f3a9c",
  title: "Retry ready — nightly research crawl",
  agent: "James",
  priority: "medium",
  state: "waiting-result",
  age: "12m",
  workerSession: "ws_01HX4P8K9Q2M7T",
  description: "Nightly re-index of competitor launch threads + weekly digest subscribers. Third attempt failed on upstream rate-limit at 06:18.",
  failureReason: "HTTP 429 from api.competitor-feed.com · upstream rate limit (rolling 1h). Retry recommended ≥30m after first 429 cleared.",
  dispatchHistory: [
    { when: "05:47", outcome: "fail", reason: "429" },
    { when: "06:02", outcome: "fail", reason: "429" },
    { when: "06:18", outcome: "fail", reason: "429" },
  ],
  timeline: [
    { t: "06:18:04", kind: "result", label: "Result · failed", tone: "rose" },
    { t: "06:18:03", kind: "progress", label: "Progress · upstream 429", tone: "amber" },
    { t: "06:15:00", kind: "progress", label: "Progress · fetched 12/200 pages", tone: "cyan" },
    { t: "06:12:41", kind: "accepted", label: "Accepted · session ws_01HX4…7T", tone: "violet" },
  ],
};

/* ── shared dialog chrome ──────────────────────────────────── */
function Scrim({ children, onClose }) {
  return (
    <div onClick={onClose} style={{
      position: "absolute", inset: 0, zIndex: 80,
      background: "rgba(0,0,0,.65)",
      backdropFilter: "blur(6px)",
      display: "flex", alignItems: "center", justifyContent: "center",
    }}>{children}</div>
  );
}

/* ── DETAILS — full-screen sheet (mobile) ──────────────────── */
function DetailsSheetMobile({ task = SAMPLE_DETAIL_TASK }) {
  const es = MC.execState[task.state] || MC.execState.queued;
  return (
    <div style={{
      position: "absolute", inset: 0, zIndex: 80,
      background: "rgba(0,0,0,.55)",
      backdropFilter: "blur(4px)",
    }}>
      <div style={{
        position: "absolute", left: 0, right: 0, bottom: 0,
        height: "88%", background: "#0f0f10",
        borderTopLeftRadius: 24, borderTopRightRadius: 24,
        border: "1px solid var(--border)",
        display: "flex", flexDirection: "column",
        overflow: "hidden",
        boxShadow: "0 -20px 60px rgba(0,0,0,.6)",
      }}>
        {/* drag handle */}
        <div style={{ padding: "10px 0 4px", display: "flex", justifyContent: "center" }}>
          <div style={{ width: 36, height: 4, borderRadius: 4, background: "rgba(255,255,255,.15)" }}/>
        </div>
        {/* header */}
        <div style={{ padding: "6px 18px 14px", borderBottom: "1px solid var(--border)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <AgentBadge name={task.agent} size="sm"/>
            <Eyebrow>TASK DETAIL</Eyebrow>
            <span style={{ marginLeft: "auto", fontFamily: "var(--font-mono)", fontSize: 10, color: "var(--text-dim)" }}>
              {task.id}
            </span>
          </div>
          <h2 style={{
            margin: "10px 0 0", fontSize: 18, fontWeight: 600, color: "white",
            letterSpacing: "-0.015em", lineHeight: 1.25,
          }}>{task.title}</h2>
          <div style={{ display: "flex", gap: 5, marginTop: 8, flexWrap: "wrap" }}>
            <Pill tone={es.tone} size="sm">{es.icon} {es.label}</Pill>
            <Pill tone="zinc" size="sm" style={{ fontFamily: "var(--font-mono)", letterSpacing: 0, textTransform: "none" }}>
              ⏱{task.age}
            </Pill>
          </div>
        </div>

        {/* scroll body */}
        <div style={{ flex: 1, overflowY: "auto", padding: "14px 18px 14px" }}>
          <DetailsBody task={task}/>
        </div>

        {/* sticky action row */}
        <div style={{
          padding: "10px 14px 14px",
          background: "rgba(15,15,15,.95)", backdropFilter: "blur(8px)",
          borderTop: "1px solid var(--border)",
          display: "flex", gap: 6,
        }}>
          <DialogBtn tone="ghost" style={{ flex: 1 }}>Close</DialogBtn>
          <DialogBtn tone="danger" style={{ flex: 1 }}>Cancel</DialogBtn>
          <DialogBtn tone="primary" style={{ flex: 1.2 }}>◆ Dispatch</DialogBtn>
        </div>
      </div>
    </div>
  );
}

/* ── DETAILS — centered modal (desktop) ────────────────────── */
function DetailsModalDesktop({ task = SAMPLE_DETAIL_TASK }) {
  const es = MC.execState[task.state] || MC.execState.queued;
  return (
    <Scrim>
      <div onClick={e => e.stopPropagation()} style={{
        width: 640, maxHeight: "80%",
        background: "#0f0f10", border: "1px solid var(--border)",
        borderRadius: 16, overflow: "hidden",
        display: "flex", flexDirection: "column",
        boxShadow: "0 30px 100px rgba(0,0,0,.6), 0 0 0 1px rgba(124,58,237,.08)",
      }}>
        {/* header */}
        <div style={{ padding: "18px 22px", borderBottom: "1px solid var(--border)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <AgentBadge name={task.agent} size="sm"/>
            <Eyebrow>TASK DETAIL</Eyebrow>
            <span style={{ marginLeft: "auto", fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-dim)" }}>
              {task.id}
            </span>
            <button style={{ all: "unset", cursor: "pointer", padding: 4, color: "var(--text-soft)", fontSize: 16 }}>✕</button>
          </div>
          <h2 style={{
            margin: "10px 0 0", fontSize: 20, fontWeight: 600, color: "white",
            letterSpacing: "-0.015em", lineHeight: 1.25,
          }}>{task.title}</h2>
          <div style={{ display: "flex", gap: 5, marginTop: 10, flexWrap: "wrap" }}>
            <Pill tone={es.tone} size="sm">{es.icon} {es.label}</Pill>
            <Pill tone="zinc" size="sm" style={{ fontFamily: "var(--font-mono)", letterSpacing: 0, textTransform: "none" }}>
              ⏱{task.age}
            </Pill>
          </div>
        </div>

        <div style={{ flex: 1, overflowY: "auto", padding: "18px 22px" }}>
          <DetailsBody task={task} wide/>
        </div>

        <div style={{
          padding: "12px 18px",
          background: "rgba(15,15,15,.95)",
          borderTop: "1px solid var(--border)",
          display: "flex", gap: 8, justifyContent: "flex-end",
        }}>
          <DialogBtn tone="ghost">Close</DialogBtn>
          <DialogBtn tone="danger">Cancel</DialogBtn>
          <DialogBtn tone="primary">◆ Dispatch</DialogBtn>
        </div>
      </div>
    </Scrim>
  );
}

/* ── shared details body (description, session, timeline, history) ── */
function DetailsBody({ task, wide = false }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
      {/* description */}
      <div>
        <Eyebrow style={{ marginBottom: 6 }}>DESCRIPTION</Eyebrow>
        <p style={{
          margin: 0, fontSize: 13.5, lineHeight: 1.55, color: "var(--text)",
          textWrap: "pretty",
        }}>{task.description}</p>
      </div>

      {/* worker session */}
      <div style={{
        padding: "10px 12px", borderRadius: 10,
        background: "#141414", border: "1px solid var(--border)",
        display: "flex", alignItems: "center", justifyContent: "space-between",
      }}>
        <div>
          <Eyebrow>WORKER SESSION</Eyebrow>
          <div style={{
            fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--text)",
            marginTop: 3, letterSpacing: 0,
          }}>{task.workerSession}</div>
        </div>
        <button style={{
          all: "unset", cursor: "pointer",
          padding: "5px 9px", borderRadius: 6,
          border: "1px solid var(--border)", background: "rgba(255,255,255,.03)",
          fontSize: 10, color: "var(--text-soft)", letterSpacing: ".12em",
          textTransform: "uppercase", fontWeight: 600,
        }}>Copy</button>
      </div>

      {/* failure reason */}
      {task.failureReason && (
        <div style={{
          padding: "10px 12px", borderRadius: 10,
          border: "1px solid rgba(244,63,94,.2)", background: "rgba(244,63,94,.06)",
        }}>
          <Eyebrow style={{ color: "#fecdd3", marginBottom: 4 }}>FAILURE REASON · PRESERVED</Eyebrow>
          <div style={{ fontSize: 12.5, color: "#fecdd3", lineHeight: 1.45 }}>
            {task.failureReason}
          </div>
        </div>
      )}

      {/* receipt timeline */}
      <div>
        <Eyebrow style={{ marginBottom: 8 }}>RECEIPT TIMELINE</Eyebrow>
        <div style={{ display: "flex", flexDirection: "column", gap: 6, position: "relative" }}>
          {task.timeline.map((t, i) => {
            const toneColor = {
              rose: "#f43f5e", amber: "#f59e0b", cyan: "#22d3ee", violet: "#a78bfa",
            }[t.tone] || "#52525b";
            return (
              <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 10 }}>
                <div style={{
                  width: 18, flexShrink: 0,
                  display: "flex", justifyContent: "center", position: "relative",
                  paddingTop: 5,
                }}>
                  <span style={{
                    width: 8, height: 8, borderRadius: 999,
                    background: toneColor, boxShadow: `0 0 6px ${toneColor}`, zIndex: 2,
                  }}/>
                  {i < task.timeline.length - 1 && (
                    <span style={{
                      position: "absolute", top: 12, left: "50%", transform: "translateX(-50%)",
                      width: 1, height: 22,
                      background: "rgba(255,255,255,.08)",
                    }}/>
                  )}
                </div>
                <div style={{ flex: 1, minWidth: 0, lineHeight: 1.3 }}>
                  <div style={{ fontSize: 12.5, color: "var(--text)", fontWeight: 500 }}>
                    {t.label}
                  </div>
                </div>
                <span style={{
                  fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-dim)",
                  flexShrink: 0, paddingTop: 1,
                }}>{t.t}</span>
              </div>
            );
          })}
        </div>
      </div>

      {/* dispatch history chips */}
      <div>
        <Eyebrow style={{ marginBottom: 6 }}>DISPATCH HISTORY · {task.dispatchHistory.length}/3</Eyebrow>
        <div style={{ display: "flex", gap: 5, flexWrap: "wrap" }}>
          {task.dispatchHistory.map((h, i) => (
            <span key={i} style={{
              display: "inline-flex", alignItems: "center", gap: 5,
              padding: "4px 9px", borderRadius: 8,
              border: h.outcome === "fail" ? "1px solid rgba(244,63,94,.25)" : "1px solid rgba(34,197,94,.25)",
              background: h.outcome === "fail" ? "rgba(244,63,94,.08)" : "rgba(34,197,94,.08)",
              color: h.outcome === "fail" ? "#fecdd3" : "#bbf7d0",
              fontSize: 11, fontFamily: "var(--font-mono)", letterSpacing: 0,
            }}>
              {h.outcome === "fail" ? "✕" : "✓"} {h.when} · {h.reason}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ── Destructive confirm — Admin cleanup ───────────────────── */
function AdminConfirmDialog({ width = 440, task = SAMPLE_DETAIL_TASK }) {
  return (
    <Scrim>
      <div onClick={e => e.stopPropagation()} style={{
        width, background: "#0f0f10",
        border: "1px solid rgba(244,63,94,.25)",
        borderRadius: 14, overflow: "hidden",
        boxShadow: "0 30px 80px rgba(0,0,0,.6), 0 0 0 1px rgba(244,63,94,.1)",
      }}>
        <div style={{
          padding: "20px 22px 18px",
          background: "linear-gradient(180deg, rgba(244,63,94,.08), rgba(244,63,94,.02))",
          borderBottom: "1px solid var(--border)",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{
              width: 36, height: 36, borderRadius: 10, flexShrink: 0,
              border: "1px solid rgba(244,63,94,.35)", background: "rgba(244,63,94,.12)",
              color: "#fecdd3", display: "inline-flex", alignItems: "center", justifyContent: "center",
              fontSize: 17,
            }}>⚠</div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <Eyebrow style={{ color: "#fecdd3", marginBottom: 3 }}>ADMIN CLEANUP · DESTRUCTIVE</Eyebrow>
              <h2 style={{
                margin: 0, fontSize: 16, fontWeight: 600, color: "white",
                letterSpacing: "-0.01em", lineHeight: 1.3,
              }}>Cancel this task?</h2>
            </div>
          </div>
        </div>

        <div style={{ padding: "16px 22px", display: "flex", flexDirection: "column", gap: 12 }}>
          <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.5, color: "var(--text)" }}>
            This cannot be undone. The worker session will be released and the task marked
            <span style={{ color: "#fecdd3", fontWeight: 600 }}> cancelled</span>.
          </p>

          {/* target */}
          <div style={{
            padding: "10px 12px", borderRadius: 10,
            background: "#141414", border: "1px solid var(--border)",
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <AgentBadge name={task.agent} size="sm"/>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  fontSize: 12.5, fontWeight: 500, color: "white",
                  whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
                }}>{task.title}</div>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: 10.5, color: "var(--text-dim)", marginTop: 2 }}>
                  {task.id} · session {task.workerSession}
                </div>
              </div>
            </div>
          </div>

          {task.failureReason && (
            <div style={{
              padding: "10px 12px", borderRadius: 10,
              border: "1px solid rgba(244,63,94,.2)", background: "rgba(244,63,94,.06)",
            }}>
              <Eyebrow style={{ color: "#fecdd3", marginBottom: 4 }}>WILL BE PRESERVED</Eyebrow>
              <div style={{ fontSize: 12, color: "#fecdd3", lineHeight: 1.45 }}>
                {task.failureReason}
              </div>
            </div>
          )}
        </div>

        <div style={{
          padding: "12px 18px",
          borderTop: "1px solid var(--border)",
          display: "flex", gap: 8, justifyContent: "flex-end",
          background: "rgba(15,15,15,.95)",
        }}>
          <DialogBtn tone="ghost">Cancel</DialogBtn>
          <DialogBtn tone="danger-filled">Confirm cleanup</DialogBtn>
        </div>
      </div>
    </Scrim>
  );
}

/* ── Retry confirm (violet brand action) ───────────────────── */
function RetryConfirmDialog({ width = 440, task = SAMPLE_DETAIL_TASK, used = 2, cap = 3 }) {
  return (
    <Scrim>
      <div onClick={e => e.stopPropagation()} style={{
        width, background: "#0f0f10",
        border: "1px solid var(--accent-border)",
        borderRadius: 14, overflow: "hidden",
        boxShadow: "0 30px 80px rgba(0,0,0,.6), 0 0 24px rgba(124,58,237,.25)",
      }}>
        <div style={{
          padding: "20px 22px 18px",
          background: "linear-gradient(180deg, rgba(124,58,237,.10), rgba(124,58,237,.03))",
          borderBottom: "1px solid var(--border)",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <div style={{
              width: 36, height: 36, borderRadius: 10, flexShrink: 0,
              border: "1px solid var(--accent-border)", background: "var(--accent-wash)",
              color: "#c4b5fd", display: "inline-flex", alignItems: "center", justifyContent: "center",
              fontSize: 17,
            }}>◆</div>
            <div style={{ flex: 1, minWidth: 0 }}>
              <Eyebrow style={{ color: "#c4b5fd", marginBottom: 3 }}>RETRY · {used}/{cap} USED</Eyebrow>
              <h2 style={{
                margin: 0, fontSize: 16, fontWeight: 600, color: "white",
                letterSpacing: "-0.01em", lineHeight: 1.3,
              }}>Dispatch retry?</h2>
            </div>
          </div>
        </div>

        <div style={{ padding: "16px 22px", display: "flex", flexDirection: "column", gap: 12 }}>
          <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.5, color: "var(--text)" }}>
            {used}/{cap} retries used. Failure reason preserved for triage.
            A new worker session will be acquired; previous session releases on pickup.
          </p>

          <div style={{
            padding: "10px 12px", borderRadius: 10,
            background: "#141414", border: "1px solid var(--border)",
          }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              <AgentBadge name={task.agent} size="sm"/>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{
                  fontSize: 12.5, fontWeight: 500, color: "white",
                  whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
                }}>{task.title}</div>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: 10.5, color: "var(--text-dim)", marginTop: 2 }}>
                  {task.id} · last failed {task.dispatchHistory.at(-1).when}
                </div>
              </div>
            </div>
          </div>

          {/* retry slots */}
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <Eyebrow>SLOTS</Eyebrow>
            <div style={{ display: "flex", gap: 4 }}>
              {Array.from({ length: cap }).map((_, i) => (
                <span key={i} style={{
                  width: 24, height: 8, borderRadius: 3,
                  background: i < used ? "#f43f5e" : "rgba(255,255,255,.08)",
                  boxShadow: i < used ? "0 0 4px rgba(244,63,94,.5)" : "none",
                }}/>
              ))}
            </div>
          </div>

          {task.failureReason && (
            <div style={{
              padding: "10px 12px", borderRadius: 10,
              border: "1px solid rgba(244,63,94,.2)", background: "rgba(244,63,94,.06)",
            }}>
              <Eyebrow style={{ color: "#fecdd3", marginBottom: 4 }}>FAILURE REASON</Eyebrow>
              <div style={{ fontSize: 12, color: "#fecdd3", lineHeight: 1.45 }}>
                {task.failureReason}
              </div>
            </div>
          )}
        </div>

        <div style={{
          padding: "12px 18px",
          borderTop: "1px solid var(--border)",
          display: "flex", gap: 8, justifyContent: "flex-end",
          background: "rgba(15,15,15,.95)",
        }}>
          <DialogBtn tone="ghost">Cancel</DialogBtn>
          <DialogBtn tone="primary">◆ Dispatch retry</DialogBtn>
        </div>
      </div>
    </Scrim>
  );
}

/* ── Dialog button primitive ──────────────────────────────── */
function DialogBtn({ tone = "ghost", children, style = {} }) {
  const styles = {
    ghost:   { border: "1px solid rgba(255,255,255,.10)", background: "rgba(255,255,255,.04)", color: "var(--text)" },
    primary: { border: "1px solid var(--accent-border)", background: "linear-gradient(180deg, rgba(124,58,237,.35), rgba(124,58,237,.15))", color: "white", boxShadow: "0 0 12px rgba(124,58,237,.3)" },
    danger:  { border: "1px solid rgba(244,63,94,.30)", background: "rgba(244,63,94,.10)", color: "#fecdd3" },
    "danger-filled": { border: "1px solid rgba(244,63,94,.5)", background: "linear-gradient(180deg, rgba(244,63,94,.35), rgba(244,63,94,.15))", color: "white", boxShadow: "0 0 12px rgba(244,63,94,.25)" },
  }[tone];
  return (
    <button style={{
      all: "unset", cursor: "pointer",
      padding: "0 16px", minHeight: 40,
      display: "inline-flex", alignItems: "center", justifyContent: "center",
      borderRadius: 10, fontSize: 13, fontWeight: 500, letterSpacing: "-0.005em",
      textAlign: "center", whiteSpace: "nowrap",
      ...styles, ...style,
    }}>{children}</button>
  );
}

/* ── Command Palette ──────────────────────────────────────── */
const CMD_ITEMS = [
  { icon: "→", label: "Go to Analytics",       hint: "Navigate",   kind: "nav" },
  { icon: "◆", label: "Dispatch selected",     hint: "Task action", kind: "primary" },
  { icon: "+", label: "New task",              hint: "Create",      kind: "nav" },
  { icon: "✕", label: "Admin cleanup…",        hint: "Destructive", kind: "danger" },
  { icon: "⟳", label: "Retry: research crawl", hint: "Task action", kind: "primary" },
  { icon: "◐", label: "Toggle agent panel",    hint: "Layout",      kind: "nav" },
  { icon: "⌕", label: "Search receipts…",      hint: "Vault",       kind: "nav" },
];

function CommandPalette({ mobile = false, selectedIdx = 1 }) {
  return (
    <Scrim>
      <div onClick={e => e.stopPropagation()} style={{
        width: mobile ? "calc(100% - 16px)" : 560,
        maxHeight: mobile ? "70%" : 440,
        marginTop: mobile ? "auto" : -60, // center-ish offset on desktop; bottom-dock on mobile
        marginBottom: mobile ? 100 : 0,
        background: "rgba(17,17,17,.98)",
        border: "1px solid var(--border)",
        borderRadius: 14, overflow: "hidden",
        boxShadow: "0 30px 80px rgba(0,0,0,.6), 0 0 24px rgba(124,58,237,.2)",
        display: "flex", flexDirection: "column",
      }}>
        {/* input */}
        <div style={{
          padding: "14px 16px", borderBottom: "1px solid var(--border)",
          display: "flex", alignItems: "center", gap: 10,
          background: "rgba(124,58,237,.04)",
        }}>
          <span style={{ color: "#c4b5fd", fontSize: 16 }}>⌕</span>
          <div style={{
            flex: 1, fontSize: 14.5, color: "white", letterSpacing: "-0.005em",
            fontWeight: 400,
          }}>
            dispatch<span style={{
              display: "inline-block", width: 2, height: 16, marginLeft: 1,
              background: "#c4b5fd", verticalAlign: "middle",
              animation: "mc-cursor 1s steps(2) infinite",
            }}/>
          </div>
          <Kbd>ESC</Kbd>
        </div>

        {/* results */}
        <div style={{ flex: 1, overflowY: "auto", padding: 4 }}>
          <div style={{ padding: "8px 12px 4px" }}>
            <Eyebrow>SUGGESTIONS</Eyebrow>
          </div>
          {CMD_ITEMS.map((it, i) => {
            const sel = i === selectedIdx;
            const iconColor = it.kind === "primary" ? "#c4b5fd"
              : it.kind === "danger" ? "#fecdd3"
              : "var(--text-soft)";
            return (
              <div key={i} style={{
                display: "flex", alignItems: "center", gap: 12,
                padding: "10px 12px", borderRadius: 10,
                background: sel ? "var(--accent-wash)" : "transparent",
                border: sel ? "1px solid var(--accent-border)" : "1px solid transparent",
              }}>
                <span style={{
                  width: 22, height: 22, borderRadius: 6,
                  display: "inline-flex", alignItems: "center", justifyContent: "center",
                  fontSize: 13, color: iconColor,
                  background: sel ? "rgba(124,58,237,.18)" : "rgba(255,255,255,.04)",
                }}>{it.icon}</span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{
                    fontSize: 13.5, color: sel ? "white" : "var(--text)",
                    fontWeight: sel ? 500 : 400, letterSpacing: "-0.005em",
                  }}>{it.label}</div>
                </div>
                <span style={{
                  fontSize: 10, letterSpacing: ".14em", textTransform: "uppercase",
                  color: "var(--text-dim)", fontWeight: 600,
                }}>{it.hint}</span>
                {sel && <Kbd>⏎</Kbd>}
              </div>
            );
          })}
        </div>

        {/* footer */}
        <div style={{
          padding: "10px 14px", borderTop: "1px solid var(--border)",
          display: "flex", alignItems: "center", gap: 14,
          background: "rgba(10,10,12,.9)",
        }}>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 5, fontSize: 10.5, color: "var(--text-soft)" }}>
            <Kbd>↑</Kbd><Kbd>↓</Kbd> navigate
          </span>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 5, fontSize: 10.5, color: "var(--text-soft)" }}>
            <Kbd>⏎</Kbd> run
          </span>
          <span style={{ display: "inline-flex", alignItems: "center", gap: 5, fontSize: 10.5, color: "var(--text-soft)" }}>
            <Kbd>ESC</Kbd> close
          </span>
          <span style={{ marginLeft: "auto", fontSize: 10.5, color: "var(--text-dim)", fontFamily: "var(--font-mono)" }}>
            7 commands
          </span>
        </div>
      </div>
    </Scrim>
  );
}

/* ── All-Clear empty state for Morning Status ──────────────── */
function AllClearHero() {
  return (
    <div style={{
      position: "relative",
      border: "1px solid rgba(34,197,94,.25)",
      background: "linear-gradient(180deg, rgba(34,197,94,.08), rgba(34,197,94,.01) 50%, #111111 100%)",
      borderRadius: 18, padding: 14,
      boxShadow: "0 4px 24px rgba(0,0,0,.35), 0 0 28px rgba(34,197,94,.06)",
      overflow: "hidden",
    }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
        <Eyebrow>OPERATOR · MORNING STATUS</Eyebrow>
        <MicroMeta style={{ fontSize: 10, color: "var(--text-dim)" }}>20/04/2026 · 06:47</MicroMeta>
      </div>

      <div style={{ display: "flex", alignItems: "baseline", gap: 12, marginTop: 8, position: "relative" }}>
        <div style={{
          position: "absolute", left: -16, top: -12,
          width: 140, height: 140, pointerEvents: "none",
          background: "radial-gradient(circle, rgba(34,197,94,0.10), transparent 60%)",
          filter: "blur(8px)",
        }}/>
        <div className="mc-num" style={{
          position: "relative",
          fontSize: "clamp(56px, 12vw, 88px)",
          fontWeight: 600, color: "#bbf7d0",
          letterSpacing: "-0.04em", lineHeight: 0.9,
          fontVariantNumeric: "tabular-nums",
          textShadow: "0 0 40px rgba(34,197,94,.25)",
        }}>0</div>
        <div style={{ flex: 1, lineHeight: 1.2, paddingBottom: 4, position: "relative" }}>
          <div style={{
            fontSize: 18, fontWeight: 600, color: "white", letterSpacing: "-0.015em",
            display: "inline-flex", alignItems: "center", gap: 6,
          }}>
            All clear
            <span style={{
              display: "inline-flex", alignItems: "center", gap: 5,
              padding: "1px 7px", borderRadius: 999,
              border: "1px solid rgba(34,197,94,.25)", background: "rgba(34,197,94,.12)",
              fontSize: 9, letterSpacing: ".14em", textTransform: "uppercase",
              fontWeight: 700, color: "#bbf7d0",
            }}>
              <span style={{ width: 5, height: 5, borderRadius: 999, background: "#22c55e", boxShadow: "0 0 6px #22c55e", animation: "mc-live-glow 2s ease-in-out infinite" }}/>
              steady
            </span>
          </div>
          <MicroMeta style={{ fontSize: 11, marginTop: 4 }}>
            19 active · 117 dispatched · confidence 100%
          </MicroMeta>
        </div>
      </div>

      <div style={{ marginTop: 6 }}><HeartbeatStrip allClear/></div>
    </div>
  );
}

/* ── Quiet empty-lane for lane-body ────────────────────────── */
function QuietEmptyLane({ message = "Nothing waiting" }) {
  return (
    <div style={{
      border: "1px dashed rgba(255,255,255,.08)", borderRadius: 14,
      padding: "28px 16px", textAlign: "center",
      background: "rgba(255,255,255,.01)",
    }}>
      <div style={{
        width: 32, height: 32, borderRadius: 10, margin: "0 auto 10px",
        border: "1px solid rgba(34,197,94,.25)", background: "rgba(34,197,94,.08)",
        color: "#bbf7d0", display: "inline-flex", alignItems: "center", justifyContent: "center",
        fontSize: 14,
      }}>✓</div>
      <div style={{ fontSize: 13, color: "var(--text)", marginBottom: 4, fontWeight: 500 }}>
        {message}
      </div>
      <MicroMeta>Pull the next ready task or create a new one.</MicroMeta>
    </div>
  );
}

/* inject cursor keyframe */
if (!document.getElementById("v2-states-style")) {
  const s = document.createElement("style");
  s.id = "v2-states-style";
  s.textContent = `
    @keyframes mc-cursor { 0%,100% { opacity: 1; } 50% { opacity: 0; } }
  `;
  document.head.appendChild(s);
}

Object.assign(window, {
  DetailsSheetMobile, DetailsModalDesktop, AdminConfirmDialog, RetryConfirmDialog,
  CommandPalette, AllClearHero, QuietEmptyLane, DialogBtn, SAMPLE_DETAIL_TASK,
});
