// Canvas section for interaction-state artboards.
// Renders 5 frame-groups (Details / Admin / Retry / Command / All-Clear).

function StatesSection({ showAnnotations = true }) {
  return (
    <>
      {/* ─── intro divider ─────────────────────────────────── */}
      <div style={{ padding: "40px 60px 32px", maxWidth: 920 }}>
        <div style={{
          fontSize: 11, fontWeight: 600, letterSpacing: ".22em", textTransform: "uppercase",
          color: "#7c3aed", marginBottom: 8,
        }}>
          INTERACTION STATES · CLICK-THRU MOCKUPS
        </div>
        <h1 style={{
          margin: 0, fontSize: 36, fontWeight: 600, color: "#2a1f14",
          letterSpacing: "-0.02em", lineHeight: 1.1,
        }}>
          What happens when you tap.
        </h1>
        <p style={{ fontSize: 15, color: "#5a4a2a", lineHeight: 1.5, marginTop: 12, maxWidth: 720 }}>
          Every core CTA shown in its activated state. Details uses a full-screen bottom sheet on mobile
          and a 640px centered modal on desktop. Admin cleanup is the only rose-filled destructive;
          Retry owns the violet brand glow; ⌘K is always reachable. All-clear is the only time we break
          the rose urgency tone.
        </p>
      </div>

      {/* 1. DETAILS MODAL ──────────────────────────────── */}
      <DCSection
        title="1 · Details modal"
        subtitle="Mobile = full-screen sheet slides up from bottom (88% height, drag-handle). Desktop = 640px centered modal with scrim + blur."
        gap={60}
      >
        <div style={{ position: "relative", paddingRight: 260 }}>
          <PhoneFrame label="V2 Mobile · Details sheet open" width={390} height={844}>
            {/* background layer — the screen you came from, dimmed by scrim */}
            <V2ScreenLaneLocked lane="waiting" stalled={3}/>
            <DetailsSheetMobile/>
          </PhoneFrame>

          {showAnnotations && (
            <>
              <Pin n={1} x={20 + 195} y={20 + 110}/>
              <Pin n={2} x={20 + 195} y={20 + 380}/>
              <Pin n={3} x={20 + 195} y={20 + 780}/>
              <Callout n={1} x={420} y={70} width={220}
                title="Drag-handle sheet"
                body="Slides from bottom. 88% viewport height keeps the task context (1-tap-dismiss) visible behind the scrim."
              />
              <Callout n={2} x={420} y={300} width={220}
                title="Receipt timeline"
                body="4-step vertical timeline with tone-colored dots + connecting rail. Accepted → progress → progress → result, most-recent-first, mono timestamps right-aligned."
              />
              <Callout n={3} x={420} y={700} width={220}
                title="Sticky action row"
                body="Close · Cancel · Dispatch. Sits at 40px each, thumb-reach. Dispatch gets the primary violet wash."
              />
            </>
          )}
        </div>

        <div style={{ position: "relative", paddingRight: 300 }}>
          <DesktopBezel label="V2 Desktop · Details modal open · 1440×900" width={1440} height={900}>
            <V2DesktopScreen stalled={3}/>
            <DetailsModalDesktop/>
          </DesktopBezel>

          {showAnnotations && (
            <>
              <Pin n={1} x={10 + 720} y={38 + 180}/>
              <Pin n={2} x={10 + 720} y={38 + 600}/>
              <Callout n={1} x={1480} y={140} width={260}
                title="640px centered modal"
                body="Scrim dims + blurs the board behind. Violet inner glow on the border hints it's a primary-action surface, not destructive."
              />
              <Callout n={2} x={1480} y={560} width={260}
                title="Right-justified action row"
                body="Desktop convention — Close · Cancel · Dispatch rightward. Escape closes. Keyboard-triggerable throughout."
              />
            </>
          )}
        </div>
      </DCSection>

      {/* 2. ADMIN CLEANUP CONFIRM ──────────────────────── */}
      <DCSection
        title="2 · Admin cleanup · destructive confirm"
        subtitle="Rose-tinted. The only dialog where brand violet is absent. Preserves the failure-reason so triage context survives the cancellation."
        gap={60}
      >
        <div style={{ position: "relative", paddingRight: 260 }}>
          <PhoneFrame label="V2 Mobile · Admin cleanup confirm" width={390} height={844}>
            <V2ScreenLaneLocked lane="needs" stalled={3}/>
            <AdminConfirmDialog width={340}/>
          </PhoneFrame>

          {showAnnotations && (
            <>
              <Pin n={1} x={20 + 195} y={20 + 290}/>
              <Pin n={2} x={20 + 195} y={20 + 500}/>
              <Callout n={1} x={420} y={240} width={220}
                title="Destructive header"
                body="⚠ chip + rose gradient. 'Cancel this task?' as the H1; 'This cannot be undone' in body. No brand violet anywhere."
              />
              <Callout n={2} x={420} y={470} width={220}
                title="Failure reason preserved"
                body="Panel explicitly labelled WILL BE PRESERVED. The triage context survives the cleanup — cancelled ≠ forgotten."
              />
            </>
          )}
        </div>

        <div style={{ position: "relative", paddingRight: 300 }}>
          <DesktopBezel label="V2 Desktop · Admin cleanup confirm · 1440×900" width={1440} height={900}>
            <V2DesktopScreen stalled={3}/>
            <AdminConfirmDialog/>
          </DesktopBezel>

          {showAnnotations && (
            <>
              <Pin n={1} x={10 + 720} y={38 + 410}/>
              <Callout n={1} x={1480} y={380} width={260}
                title="Right-justified · rose-filled confirm"
                body="Cancel (ghost) left, Confirm cleanup (rose-filled) right. Full-bleed rose glow on border + 'DESTRUCTIVE' eyebrow in rose."
              />
              <DCPostIt top={680} left={1480} rotate={-2} width={240}>
                Only place we use rose-filled buttons. Everywhere else rose is chip-only.
              </DCPostIt>
            </>
          )}
        </div>
      </DCSection>

      {/* 3. RETRY CONFIRM ──────────────────────────────── */}
      <DCSection
        title="3 · Retry confirm · violet brand action"
        subtitle="Slot-indicator for retry budget. Failure-reason visible to confirm triage intent. The only dialog that owns violet glow."
        gap={60}
      >
        <div style={{ position: "relative", paddingRight: 260 }}>
          <PhoneFrame label="V2 Mobile · Retry confirm (2/3 used)" width={390} height={844}>
            <V2ScreenLaneLocked lane="waiting" stalled={3}/>
            <RetryConfirmDialog width={340}/>
          </PhoneFrame>

          {showAnnotations && (
            <>
              <Pin n={1} x={20 + 195} y={20 + 295}/>
              <Pin n={2} x={20 + 195} y={20 + 430}/>
              <Callout n={1} x={420} y={250} width={220}
                title="2/3 retries used"
                body="Eyebrow shows budget at a glance. Slot pills below are rose-on-used / dim-on-free — matches the pulse-bar's bar metaphor."
              />
              <Callout n={2} x={420} y={400} width={220}
                title="Failure reason inline"
                body="Rose panel below still shows the reason — confirmation that you saw what broke before re-dispatching."
              />
            </>
          )}
        </div>

        <div style={{ position: "relative", paddingRight: 300 }}>
          <DesktopBezel label="V2 Desktop · Retry confirm · 1440×900" width={1440} height={900}>
            <V2DesktopScreen stalled={3}/>
            <RetryConfirmDialog/>
          </DesktopBezel>

          {showAnnotations && (
            <>
              <Pin n={1} x={10 + 720} y={38 + 180}/>
              <Callout n={1} x={1480} y={140} width={260}
                title="Violet brand glow"
                body="Outer shadow picks up #7c3aed. ◆ glyph reinforces brand. Slot pills double as a budget visualisation users can read at a glance."
              />
            </>
          )}
        </div>
      </DCSection>

      {/* 4. COMMAND PALETTE ────────────────────────────── */}
      <DCSection
        title="4 · Command palette · ⌘K"
        subtitle="Same surface on both breakpoints. Desktop centered; mobile docks just above the tab bar so results + keyboard can coexist. Fuzzy-filtering as you type."
        gap={60}
      >
        <div style={{ position: "relative", paddingRight: 260 }}>
          <PhoneFrame label="V2 Mobile · ⌘K palette open" width={390} height={844}>
            <V2ScreenLaneLocked lane="needs" stalled={3}/>
            <CommandPalette mobile selectedIdx={1}/>
          </PhoneFrame>

          {showAnnotations && (
            <>
              <Pin n={1} x={20 + 195} y={20 + 430}/>
              <Pin n={2} x={20 + 195} y={20 + 760}/>
              <Callout n={1} x={420} y={400} width={220}
                title="Docked above tab bar"
                body="On mobile, the palette sheets up from the FAB. Input at top, results scroll; the FAB cursor becomes part of the search pattern."
              />
              <Callout n={2} x={420} y={730} width={220}
                title="Touch-friendly kbd footer"
                body="↑↓ ⏎ ESC legend stays visible — reassurance that the same palette drives keyboard flow on bigger screens."
              />
            </>
          )}
        </div>

        <div style={{ position: "relative", paddingRight: 300 }}>
          <DesktopBezel label="V2 Desktop · ⌘K palette open · 1440×900" width={1440} height={900}>
            <V2DesktopScreen stalled={3}/>
            <CommandPalette selectedIdx={1}/>
          </DesktopBezel>

          {showAnnotations && (
            <>
              <Pin n={1} x={10 + 720} y={38 + 210}/>
              <Pin n={2} x={10 + 720} y={38 + 380}/>
              <Callout n={1} x={1480} y={170} width={260}
                title="560px centered"
                body="Search input + ⌕ glyph, ESC chip on the right. Same cursor animation as the mobile version. Violet wash reminds it's a command, not a data surface."
              />
              <Callout n={2} x={1480} y={350} width={260}
                title="Selected row = violet wash + ⏎"
                body="Selected row gets the violet-washed border + enter-key hint. Icons colored by kind: violet primary, rose danger, soft neutral nav."
              />
            </>
          )}
        </div>
      </DCSection>

      {/* 5. ALL-CLEAR EMPTY ────────────────────────────── */}
      <DCSection
        title="5 · All-clear · 0 incidents"
        subtitle="Emerald replaces rose only when stalled = 0. Morning status number drops to 0; lanes show quiet empty-state prompts, not disabled buttons."
        gap={60}
      >
        <div style={{ position: "relative", paddingRight: 260 }}>
          <PhoneFrame label="V2 Mobile · all-clear morning status" width={390} height={844}>
            <AllClearScreen/>
          </PhoneFrame>

          {showAnnotations && (
            <>
              <Pin n={1} x={20 + 195} y={20 + 180}/>
              <Pin n={2} x={20 + 195} y={20 + 470}/>
              <Callout n={1} x={420} y={130} width={220}
                title="0 · All clear · steady"
                body="Number stays large — same typographic weight as the urgent state. Color shifts to emerald; 'steady' chip replaces the stalled-count. No CTA — nothing to dispatch."
              />
              <Callout n={2} x={420} y={430} width={220}
                title="Quiet empty lanes"
                body="Dashed border + emerald check + 'Nothing waiting'. 'Pull the next ready task or create a new one' is the only instruction. No disabled-looking buttons."
              />
            </>
          )}
        </div>

        <div style={{ position: "relative", paddingRight: 300 }}>
          <DesktopBezel label="V2 Desktop · all-clear · 1440×900" width={1440} height={900}>
            <V2DesktopScreen stalled={0}/>
          </DesktopBezel>

          {showAnnotations && (
            <>
              <Pin n={1} x={10 + 400} y={38 + 110}/>
              <Callout n={1} x={1480} y={80} width={260}
                title="Hero strip compresses to emerald"
                body="Same horizontal strip geometry, emerald border + 0 in emerald. 'All clear' label replaces 'stalled'. Pulse bar flattens."
              />
              <DCPostIt top={300} left={1480} rotate={2} width={240}>
                Emerald is the only non-rose success tone. It should feel rare + earned.
              </DCPostIt>
            </>
          )}
        </div>
      </DCSection>

      {/* Summary grid */}
      <DCSection title="Dialog system summary" subtitle="One row per confirm surface." gap={32}>
        <div style={{
          width: 1100, padding: 28, background: "#fff", borderRadius: 6,
          boxShadow: "0 1px 3px rgba(0,0,0,.08), 0 4px 16px rgba(0,0,0,.06)",
          fontSize: 13, lineHeight: 1.6, color: "#2a1f14",
        }}>
          <div style={{ display: "grid", gridTemplateColumns: "180px 1fr 1fr 1fr", gap: 20, alignItems: "start" }}>
            <div></div>
            <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: ".18em", textTransform: "uppercase", color: "#7c3aed" }}>Tone</div>
            <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: ".18em", textTransform: "uppercase", color: "#7c3aed" }}>Surface</div>
            <div style={{ fontSize: 11, fontWeight: 600, letterSpacing: ".18em", textTransform: "uppercase", color: "#7c3aed" }}>Primary CTA</div>
            {[
              ["Details", "Neutral · violet accents", "Sheet (mobile) · 640px modal (desktop)", "◆ Dispatch (violet)"],
              ["Admin cleanup", "Rose-tinted, destructive", "440px dialog, scrim + blur", "Confirm cleanup (rose-filled)"],
              ["Retry", "Violet-tinted, brand", "440px dialog, violet glow", "◆ Dispatch retry (violet)"],
              ["⌘K palette", "Neutral · violet hint", "Centered 560px · docked on mobile", "⏎ Run selected"],
              ["All clear", "Emerald", "Inline hero + empty lanes", "— (no action)"],
            ].map((row, i) => (
              <React.Fragment key={i}>
                <div style={{ fontWeight: 600, color: "#2a1f14", borderTop: "1px solid #eadfce", paddingTop: 12 }}>{row[0]}</div>
                <div style={{ color: "#5a4a2a", borderTop: "1px solid #eadfce", paddingTop: 12 }}>{row[1]}</div>
                <div style={{ color: "#5a4a2a", borderTop: "1px solid #eadfce", paddingTop: 12 }}>{row[2]}</div>
                <div style={{ color: "#5a4a2a", borderTop: "1px solid #eadfce", paddingTop: 12 }}>{row[3]}</div>
              </React.Fragment>
            ))}
          </div>
        </div>
      </DCSection>
    </>
  );
}

/* ── All-Clear mobile screen (reuses shared primitives + AllClearHero) ── */
function AllClearScreen() {
  return (
    <div style={{ position: "absolute", inset: 0, paddingTop: 47, overflow: "hidden", display: "flex", flexDirection: "column" }}>
      {/* header */}
      <div style={{ padding: "8px 16px 6px", display: "flex", alignItems: "center", justifyContent: "space-between", background: "rgba(15,15,15,.95)", backdropFilter: "blur(6px)", flexShrink: 0 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ width: 24, height: 24, borderRadius: 6, border: "1px solid var(--accent-border)", background: "var(--accent-wash)", color: "#c4b5fd", display: "inline-flex", alignItems: "center", justifyContent: "center", fontSize: 13 }}>⚙</div>
          <span style={{ fontSize: 9.5, letterSpacing: ".22em", color: "var(--text)", fontWeight: 600 }}>TASKBOARD</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <div style={{ display: "inline-flex", alignItems: "center", gap: 4, padding: "2px 7px", borderRadius: 999, border: "1px solid rgba(34,197,94,.20)", background: "rgba(34,197,94,.10)", color: "#bbf7d0", fontSize: 9, letterSpacing: ".14em", fontWeight: 700, textTransform: "uppercase" }}>
            <span style={{ width: 5, height: 5, borderRadius: 999, background: "#22c55e", boxShadow: "0 0 6px #22c55e" }}/>LIVE
          </div>
          <AgentBadge name="pieter_pan" size="sm"/>
        </div>
      </div>
      <div style={{ flex: 1, overflowY: "auto", padding: "12px 12px 120px" }}>
        <AllClearHero/>
        <div style={{ marginTop: 16, marginBottom: 12 }}>
          <Eyebrow style={{ padding: "0 4px", marginBottom: 8 }}>LANES</Eyebrow>
          <div style={{ display: "flex", gap: 6, overflowX: "auto", margin: "0 -12px", padding: "0 12px 4px", scrollbarWidth: "none" }}>
            {MOBILE_LANES.map(l => (
              <V2SwipeChip key={l.id} lane={{...l, count: 0}} active={l.id === "needs"} onClick={() => {}}/>
            ))}
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 2px", marginBottom: 8 }}>
          <div style={{ fontSize: 11, letterSpacing: ".22em", textTransform: "uppercase", fontWeight: 600, color: "var(--text)" }}>
            Needs attention
            <span className="mc-num" style={{ marginLeft: 8, fontFamily: "var(--font-mono)", color: "var(--text-soft)", fontWeight: 500, letterSpacing: 0 }}>00</span>
          </div>
        </div>
        <QuietEmptyLane message="Nothing waiting"/>
      </div>
      <BottomTabBar active="tasks"/>
    </div>
  );
}

Object.assign(window, { StatesSection, AllClearScreen });
