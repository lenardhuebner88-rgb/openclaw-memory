// V3 — Details Drawer / Modal / Sheet
// Single content component <V3DrawerContent>, three host shells:
//  - <V3Drawer>      desktop right-side overlay (460px)
//  - <V3Modal>       desktop center modal (720px)
//  - <V3Sheet>       mobile bottom sheet (full-height, 390 wide)
//
// Order of information matters. Truth first. Raw last.
//   1. header (code/title/status/age/actions)
//   2. truth & next safe action      ← FIRST. Operator-decision surface.
//   3. lifecycle stages (4 dots, with timestamps)
//   4. receipt chain (latest first)
//   5. worker session + dispatch token
//   6. acceptance criteria
//   7. events / history (collapsible)
//   8. parent / follow-ups
//   9. result detail / blocker
//  10. raw metadata (collapsed advanced)

function V3DrawerContent({ task = V3_DETAIL_TASK, variant = "drawer" }) {
  const s = V3_STATUS[task.status];
  const next = suggestedNext(task);
  const isCompact = variant === "compact" || variant === "sheet";

  return (
    <div style={{
      display: "flex", flexDirection: "column",
      height: "100%",
      fontFamily: "var(--font-sans)",
    }}>
      <V3DrawerHeader task={task} variant={variant}/>
      <div style={{
        flex: 1, overflow: "auto",
        padding: isCompact ? "14px 16px 24px" : "16px 22px 28px",
        display: "flex", flexDirection: "column", gap: 16,
      }}>
        <V3SecTruth task={task} next={next}/>
        <V3SecLifecycle task={task}/>
        <V3SecReceipts task={task}/>
        <V3SecSession task={task}/>
        <V3SecAcceptance task={task}/>
        <V3SecEvents task={task}/>
        <V3SecRelations task={task}/>
        <V3SecResult task={task}/>
        <V3SecRaw task={task}/>
      </div>
    </div>
  );
}

function V3DrawerHeader({ task, variant }) {
  const s = V3_STATUS[task.status];
  return (
    <div style={{
      padding: "14px 18px 12px",
      borderBottom: "1px solid rgba(255,255,255,.08)",
      background: "rgba(0,0,0,.4)",
      flexShrink: 0,
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
        <span style={{
          fontFamily: "var(--font-mono)", fontSize: 11.5, fontWeight: 600,
          color: "var(--text-dim)",
        }}>{task.code}</span>
        <span style={{ flex: 1 }}/>
        <button style={{
          all: "unset", cursor: "pointer",
          width: 24, height: 24, borderRadius: 5,
          display: "grid", placeItems: "center",
          color: "var(--text-soft)",
          border: "1px solid rgba(255,255,255,.08)",
          fontSize: 12,
        }}>↗</button>
        <button style={{
          all: "unset", cursor: "pointer",
          width: 24, height: 24, borderRadius: 5,
          display: "grid", placeItems: "center",
          color: "var(--text-soft)",
          border: "1px solid rgba(255,255,255,.08)",
          fontSize: 12,
        }}>×</button>
      </div>
      <div style={{
        fontSize: 17, fontWeight: 600, lineHeight: 1.3, color: "white",
        letterSpacing: "-0.005em",
      }}>{task.title}</div>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 10 }}>
        <StatusBadge status={task.status} showIntent/>
        <PriorityBadge priority={task.priority}/>
        <AgentBadge name={task.agent} size="xs"/>
        <span style={{ fontSize: 11.5, color: "var(--text-soft)" }}>{task.agent}</span>
        <span style={{ flex: 1 }}/>
        <AgeTag age={task.age} stale={!!task.stale}/>
      </div>
    </div>
  );
}

/* ── SECTIONS ─────────────────────────────────────────────────── */

function SecHeader({ children, hint }) {
  return (
    <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginBottom: 8 }}>
      <div style={{
        fontSize: 10, fontWeight: 700, color: "var(--text-soft)",
        letterSpacing: ".22em", textTransform: "uppercase",
      }}>{children}</div>
      {hint && <div style={{ fontSize: 11, color: "var(--text-dim)" }}>{hint}</div>}
    </div>
  );
}

/* TRUTH — operator's #1 question: what is true and what should I do next? */
function V3SecTruth({ task, next }) {
  const s = V3_STATUS[task.status];
  const tone = V3_TONE[next.tone];
  return (
    <section>
      <SecHeader>Current truth · suggested next</SecHeader>
      <div style={{
        padding: 12, borderRadius: 10,
        background: tone.bg, border: `1px solid ${tone.border}`,
      }}>
        <div style={{ fontSize: 13, lineHeight: 1.5, color: "white" }}>
          {task.status === "failed" && (
            <>Run failed at <b style={{ fontFamily: "var(--font-mono)" }}>result</b> stage.
              Schema validation rejected the payload — operatorLock field is missing. Two follow-up tasks have already been drafted; do not retry until <b>MC-T17b</b> lands.</>
          )}
        </div>
        <div style={{ display: "flex", gap: 8, marginTop: 10 }}>
          <V3Btn primary tone={next.tone}>{next.label}</V3Btn>
          <V3Btn>Reassign to operator</V3Btn>
          <V3Btn>Cancel run</V3Btn>
        </div>
      </div>
    </section>
  );
}

/* LIFECYCLE — 4 stages with absolute timestamps */
function V3SecLifecycle({ task }) {
  const stages = [
    { id: "draft",      label: "Draft",       t: "06:12:00", state: "ok"   },
    { id: "dispatched", label: "Dispatched",  t: "06:14:38", state: "ok"   },
    { id: "accepted",   label: "Accepted",    t: "06:14:41", state: "ok"   },
    { id: "result",     label: "Result",      t: "06:18:04", state: "fail" },
  ];
  return (
    <section>
      <SecHeader hint="actual receipt-stage truth">Lifecycle</SecHeader>
      <div style={{
        padding: "10px 12px", borderRadius: 8,
        background: "rgba(255,255,255,.02)",
        border: "1px solid rgba(255,255,255,.06)",
        display: "flex", alignItems: "stretch", gap: 0,
      }}>
        {stages.map((s, i) => {
          const ok = s.state === "ok", fail = s.state === "fail";
          const color = fail ? "#f43f5e" : ok ? "#5eead4" : "rgba(255,255,255,.10)";
          return (
            <React.Fragment key={s.id}>
              <div style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: 5 }}>
                <span style={{
                  width: 11, height: 11, borderRadius: 2,
                  background: color,
                  boxShadow: ok || fail ? `0 0 8px ${color}` : undefined,
                }}/>
                <div style={{ fontSize: 10.5, fontWeight: 700, color: "white",
                  letterSpacing: ".12em", textTransform: "uppercase",
                }}>{s.label}</div>
                <div style={{ fontFamily: "var(--font-mono)", fontSize: 10.5,
                  color: fail ? "#fda4af" : ok ? "var(--text-soft)" : "var(--text-dim)",
                }}>{s.t}</div>
              </div>
              {i < stages.length - 1 && (
                <div style={{
                  width: 1, alignSelf: "center", height: 28,
                  background: ok ? "rgba(94,234,212,.30)" : "rgba(255,255,255,.06)",
                }}/>
              )}
            </React.Fragment>
          );
        })}
      </div>
    </section>
  );
}

/* RECEIPTS — latest first, full chain */
function V3SecReceipts({ task }) {
  return (
    <section>
      <SecHeader hint="latest first · full chain">Receipt chain</SecHeader>
      <div style={{
        borderRadius: 8, overflow: "hidden",
        border: "1px solid rgba(255,255,255,.06)",
        background: "rgba(0,0,0,.2)",
      }}>
        {task.receipts.map((r, i) => {
          const fail = r.outcome === "fail";
          const color = fail ? "#f43f5e" : "#5eead4";
          return (
            <div key={i} style={{
              display: "grid",
              gridTemplateColumns: "12px 92px 1fr 70px",
              gap: 10, alignItems: "center",
              padding: "8px 12px",
              borderBottom: i < task.receipts.length - 1 ? "1px solid rgba(255,255,255,.05)" : "none",
              background: fail ? "rgba(244,63,94,.06)" : "transparent",
            }}>
              <span style={{
                width: 7, height: 7, borderRadius: 1, background: color,
                justifySelf: "center",
              }}/>
              <span style={{
                fontSize: 10.5, fontWeight: 700,
                color: fail ? "#fda4af" : "var(--text-soft)",
                letterSpacing: ".14em", textTransform: "uppercase",
              }}>{r.stage}</span>
              <span style={{ fontSize: 12, color: fail ? "#fecdd3" : "white", lineHeight: 1.4 }}>
                <b style={{ fontWeight: 600 }}>{r.who}</b> · {r.text}
              </span>
              <span style={{
                fontFamily: "var(--font-mono)", fontSize: 10.5,
                color: "var(--text-dim)", textAlign: "right",
              }}>{r.t}</span>
            </div>
          );
        })}
      </div>
    </section>
  );
}

/* SESSION — dispatch + worker + run ids */
function V3SecSession({ task }) {
  return (
    <section>
      <SecHeader>Session · identity</SecHeader>
      <div style={{
        display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6,
      }}>
        <KVMono label="Dispatch token"  value={task.raw.dispatchToken}/>
        <KVMono label="Worker session"  value={task.raw.workerSession}/>
        <KVMono label="Parent run id"   value={task.raw.parentRunId}/>
        <KVMono label="Region"          value={task.raw.region}/>
      </div>
    </section>
  );
}

function KVMono({ label, value }) {
  return (
    <div style={{
      padding: "8px 10px", borderRadius: 6,
      background: "rgba(255,255,255,.02)",
      border: "1px solid rgba(255,255,255,.06)",
    }}>
      <div style={{
        fontSize: 9.5, fontWeight: 700, color: "var(--text-dim)",
        letterSpacing: ".18em", textTransform: "uppercase",
      }}>{label}</div>
      <div style={{
        fontFamily: "var(--font-mono)", fontSize: 11, color: "white", marginTop: 2,
      }}>{value}</div>
    </div>
  );
}

function V3SecAcceptance({ task }) {
  return (
    <section>
      <SecHeader hint={`${task.acceptance.filter(a=>a.ok).length}/${task.acceptance.length} passing`}>
        Acceptance criteria
      </SecHeader>
      <div style={{
        borderRadius: 8, overflow: "hidden",
        border: "1px solid rgba(255,255,255,.06)",
      }}>
        {task.acceptance.map((a, i) => (
          <div key={i} style={{
            display: "flex", alignItems: "center", gap: 10,
            padding: "8px 12px",
            borderBottom: i < task.acceptance.length - 1 ? "1px solid rgba(255,255,255,.05)" : "none",
            background: a.ok ? "rgba(34,197,94,.04)" : "rgba(244,63,94,.06)",
          }}>
            <span style={{
              width: 14, height: 14, borderRadius: 3,
              display: "grid", placeItems: "center",
              background: a.ok ? "rgba(34,197,94,.20)" : "rgba(244,63,94,.20)",
              color: a.ok ? "#86efac" : "#fda4af",
              fontSize: 10, fontWeight: 700,
            }}>{a.ok ? "✓" : "×"}</span>
            <span style={{ fontSize: 12.5, color: a.ok ? "white" : "#fecdd3" }}>{a.label}</span>
          </div>
        ))}
      </div>
    </section>
  );
}

function V3SecEvents({ task }) {
  return (
    <section>
      <SecHeader hint="ordered by time · most recent first">Events</SecHeader>
      <div style={{
        borderRadius: 8, overflow: "hidden",
        border: "1px solid rgba(255,255,255,.06)",
        background: "rgba(0,0,0,.2)",
      }}>
        {task.events.map((e, i) => {
          const t = V3_TONE[e.tone];
          return (
            <div key={i} style={{
              display: "grid",
              gridTemplateColumns: "70px 1fr",
              gap: 10, alignItems: "center",
              padding: "6px 12px",
              borderBottom: i < task.events.length - 1 ? "1px solid rgba(255,255,255,.05)" : "none",
            }}>
              <span style={{
                fontFamily: "var(--font-mono)", fontSize: 10.5, color: "var(--text-dim)",
              }}>{e.t}</span>
              <span style={{ display: "flex", alignItems: "center", gap: 7 }}>
                <span style={{ width: 5, height: 5, borderRadius: 1, background: t.solid }}/>
                <span style={{ fontSize: 12, color: "white" }}>{e.text}</span>
              </span>
            </div>
          );
        })}
      </div>
    </section>
  );
}

function V3SecRelations({ task }) {
  return (
    <section>
      <SecHeader>Parent · follow-ups</SecHeader>
      <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
        <RelationRow icon="↑" label="Parent" code={task.parent.code} title={task.parent.title}/>
        {task.followUps.map(fu => (
          <RelationRow key={fu.code} icon="↳" label="Follow-up" code={fu.code} title={fu.title}
            badge={<StatusBadge status={fu.status}/>}
          />
        ))}
        <button style={{
          all: "unset", cursor: "pointer",
          padding: "7px 10px", borderRadius: 6,
          background: "rgba(124,58,237,.10)", border: "1px dashed rgba(124,58,237,.30)",
          color: "#c4b5fd", fontSize: 11.5, fontWeight: 600,
          display: "flex", alignItems: "center", gap: 6,
        }}>+ Create follow-up task from this</button>
      </div>
    </section>
  );
}

function RelationRow({ icon, label, code, title, badge }) {
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 10,
      padding: "7px 10px", borderRadius: 6,
      background: "rgba(255,255,255,.02)",
      border: "1px solid rgba(255,255,255,.06)",
    }}>
      <span style={{
        fontSize: 11, color: "var(--text-dim)",
        width: 56, fontWeight: 600, letterSpacing: ".08em", textTransform: "uppercase",
      }}>{icon} {label}</span>
      <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--text-soft)" }}>{code}</span>
      <span style={{ fontSize: 12, color: "white", flex: 1 }}>{title}</span>
      {badge}
    </div>
  );
}

function V3SecResult({ task }) {
  return (
    <section>
      <SecHeader>Result · blocker detail</SecHeader>
      <div style={{
        padding: 12, borderRadius: 8,
        background: "rgba(244,63,94,.06)",
        border: "1px solid rgba(244,63,94,.22)",
        fontSize: 12.5, lineHeight: 1.55, color: "#fecdd3",
      }}>
        <b style={{ color: "#fda4af", fontWeight: 700 }}>Schema rejection · payload validation</b><br/>
        <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "#fda4af" }}>
          schema=v2025.04.21 missing field "operatorLock" at $.payload.operator
        </span>
        <br/><br/>
        Failure preserved in receipt chain. No retry attempted (operator-gate rule). Drafted
        follow-ups MC-T17b (schema fix) and MC-T17c (pre-flight validation test) before
        marking failed.
      </div>
    </section>
  );
}

function V3SecRaw({ task }) {
  return (
    <section>
      <SecHeader hint="advanced · click to expand">Raw metadata</SecHeader>
      <div style={{
        padding: "10px 12px", borderRadius: 8,
        background: "rgba(0,0,0,.4)",
        border: "1px solid rgba(255,255,255,.06)",
        fontFamily: "var(--font-mono)", fontSize: 10.5,
        color: "var(--text-soft)", lineHeight: 1.6,
        whiteSpace: "pre-wrap",
      }}>
{`{
  "dispatchToken":  "${task.raw.dispatchToken}",
  "workerSession":  "${task.raw.workerSession}",
  "parentRunId":    "${task.raw.parentRunId}",
  "region":         "${task.raw.region}",
  "schemaVersion":  "${task.raw.schemaVersion}"
}`}
      </div>
    </section>
  );
}

Object.assign(window, { V3DrawerContent });
