# Pending Human Actions

Single ledger of everything owed by the human, so nothing is scattered. Dated when
added; struck through when done.

| # | Action | Needed by | Context |
|---|---|---|---|
| ~~P-01~~ | ~~Ratify the funnel compliance topology (H-04)~~ **DONE 2026-08-02 — T1 ratified as D-027**, with revised R4, refined k bounds, and the IS8-17 jam class | — | studies/H04 header + Addendum |
| ~~P-02~~ | ~~Set the cloud dollar ceiling for Phase 1 compute~~ **DONE 2026-08-02 — $100 hard ceiling ratified by the human** (recorded answer, planning session); expected spend $20–60; exceeding it requires a recorded amendment, not a quiet overrun (A-011) | — | A-004 test decides CPU vs GPU by measured cost; the DOE runner meters cumulative spend against the ceiling |
| P-03 | **Approve MR-001 / MR-002 / MR-003 procedures and purchase instruments** — procedures are now execution-ready; total human time budgeted at the 3-working-day bound. **Execution kit committed 2026-08-14: `research/mr_kit/`** — print sheets S1–S4 (machine-verified scale + decode), per-day checklists (incl. the derived MR-002 exposure ceiling), shopping list, CSV templates, and `tools/mr_kit/detect_frames.py` (frames → loader-valid rows) | late August measurement window | `MEASUREMENT_REQUESTS.md`; NO_HARDWARE rev 2 three-question test answered per item |
| P-04 | **ASSIST registration** (https://assist.dla.mil) and retrieval of MIL-PRF-32383/7 (STUB slash sheet) | Phase 2 latest | Top UNVERIFIED item from `research/STANDARDS.md` |
| ~~P-05~~ | ~~Phase 0 gate sign-off~~ **DONE 2026-08-02 — signed by the human** (recorded answer, planning session), after the H-13..H-16 post-assessment closures. **Phase 0 is formally closed; the Phase 1 build is open** (A-011). Review packet kept below for reference | — | `HOLES.md` read 0 open (sixteen holes, all doors named); `PHASE1_PARAMETERS.md` 65/65 at signature |
| P-06 | **Re-scoped by D-031; Stage B COMPLETE 2026-08-04.** The OA theory pair is page-verified — Whitney's own MIT OCW 2.875 lecture (51 slides read; wedging θ > c/μ, jamming parallelogram, RCC, and theory-vs-data validation figures slides 35–38) + CJME 2025 review (CC BY; Whitney-model equations and jamming diagram, pp. 8–12). Caveats in C-12, INTERFACE_SPEC §2.3, and H04 (Addendum A5) are revised per their written terms. **Residual (email route REMOVED at the human's direction, 2026-08-04 — no favor-asks):** if a T5-promotion argument ever needs experimental grounding beyond the OCW validation figures, the path is (1) page-read **Simunovic 1979** (MIT DSpace 1721.1/16229, open PDF verified downloadable — Claude's task, zero cost) and only then (2) a **self-serve ASME PDF purchase** of the 1982 paper (~US$38, a checkout page; a document purchase per NO_HARDWARE rev 2) | only if a T5-promotion argument needs it AND Simunovic proves insufficient (Phase 1/2) | Struck entirely only if the 1982 full text itself lands |
| ~~P-07~~ | ~~Obtain Kallwies 2020~~ **CLOSED per D-031; Stage B COMPLETE 2026-08-04.** Ask dropped (nine dead routes; public unresolved ~40× reproduction caution; abstract figures aren't stock-detector corner σ). Replacement page-verified: **Adámek 2023 (Sensors, CC BY, all 20 pages read) added as perception_prior Paper 5 — FORM anchor for #40** (variance-vs-area/angle functional forms; ArUco basis, so magnitudes stay swept/MR-measured). No human action remains | — | #40's sweep unchanged; any future magnitude anchoring arrives via MR `reproj_rms_px` under the curve-swap protocol |

| ~~P-08~~ | ~~Ratification sitting: Phase-1 closeout decisions~~ **DONE 2026-08-11 — "I ratify P-08" (recorded answer, in-session). Recorded as D-039..D-046**; #62 took Option 1 (grid stands, persistence-window semantics — the no-behavior-change default under the blanket ratification; recalibration stays open as a future revision); F-013/F-014 exited as recorded exclusions in D-046(d). Fixes + freeze_prior_v2 re-run authorized in the same answer | — | Packet kept below for reference |

*Note: the hole-closure prompt's Part E-5 asked for a "rename repo to recovery-stack"
action here. That premise conflicts with committed A-001 (§2.5 says the repository IS
`anayvaidya11/Ferrier`, by explicit prior decision), so per the documents-win rule the
action was not added — recorded in the session report.*

---

## P-03 execution packet (added 2026-08-09 — read on a phone in ~5 minutes)

**What P-03 is:** the only remaining human lever on the Phase 1 gate number.
The simulation currently runs on literature-derived perception curves
(`prior_v1`); the entire moderate-band result is dominated by how mud degrades
tag detection — a number the literature honestly cannot supply. Three
measurements, three working days, replace the stand-ins with reality
(`mr_v1`), and the gate is evaluated only after that swap, reporting before
and after.

**What signing costs:** ≤ 3 working days + instrument-class purchases
(NO_HARDWARE rev 2 compliant, three-question test already answered per item in
`MEASUREMENT_REQUESTS.md`): a manually-exposable camera + lens, two tripods, a
dimmable lamp, printed AprilTags on matte paper, shop-bought spacers (arbitrary
heights, never machined to spec), soil/water/board consumables. Order of
magnitude $10¹–10² total.

**The three days:**
1. **MR-001 (~1.5 days)** — tag detection vs. mud: 14 camera/tag geometries ×
   8 mud levels × 100 frames. This is the axis your entire gate band hangs on.
2. **MR-002 (~0.5 day)** — detection below 10 lux: 20 dark-room conditions.
   Camera-specific, carries the non-transferable label.
3. **MR-003 (~1 day)** — pose-flip rate vs. view angle, both candidate tag
   layouts. Highest-value entry: it also decides the D-011 layout selection.

Hard bound: any overrun defers remaining cells, never extends the budget.

**What happens with the data:** three CSVs (+ the `reproj_rms_px` column that
replaces the swept σ_px) commit under `research/data/`; Claude registers the
`mr_v1` curve set, re-runs every affected axis, reports before/after both
(ROADMAP protocol), and only then computes the gate number against
`gate_moderate.json`.

**To approve:** say so in a session (it gets recorded here with the date), buy
the list, and schedule the days — the procedures in `MEASUREMENT_REQUESTS.md`
§"Execution grids" are written to need zero design decisions from you.

---

## P-08 ratification packet (added 2026-08-11 — grows as R01 findings land; one sitting ratifies all)

### (a) D-039 draft — MuJoCo is the Phase-1 engine of record; A-004 GPU leg waived as moot

**What it records:** ARCH §4's day-one Newton conformance run never happened —
Newton was never provisioned (GPU quota; the credits landed after the CPU path
was already proven). The entire frozen experiment (13,400 trials) ran on
MuJoCo 3.11.0, which passed the conformance suite and the bit-identical
replay contract. PHASE1_PLAN §3 requires "both measurements committed" for
A-004; only the CPU leg exists ($0.0095/1k trials, `sim/results/a004/`).

**The waiver argument:** the full DOE cost ~$0.25 of compute. Even a GPU rate
10× better than CPU could save at most ~$0.22 across all of Phase 1 — while
running the GPU leg itself (quota request, provisioning, spot time) costs more
than it could ever recover. The comparison A-004 exists to decide is moot at
this workload scale. Recording the waiver keeps the obligation visible instead
of silently unmet; the Newton adapter stays in-tree as a labeled stub.

**What would make it wrong:** Phase 2+ contact workloads at a scale where the
$/trial comparison stops being moot — re-open with a fresh cost test then.

**To ratify:** say so in a session (recorded here with the date); DECISIONS.md
gains D-039 and PHASE1_PLAN §3/ARCH §4 get supersession markers pointing at it.

### (b) #62 jam-threshold force grid — recalibrate or keep (finding from `sim/results/probe62_check.json`)

**The finding (2026-08-10):** the committed IS8-17 jam grid (F_ax {50,100,200} N,
F_lat {10,25} N, t {0.5,1,2} s) stands *operationally* — IS8-17 fired 0× in the
freeze — but the discrimination is carried almost entirely by the 1.0 s
persistence window, not the force cells: a *successful* nominal insertion
exceeds F_ax_jam at its p90 (272 N vs 100 N) and F_lat_jam at its p99
(6.4 kN vs 25 N) on contact transients. The force cells as committed do not
separate jam from normal contact; the time window does.

**Option 1 — keep the grid, record the semantics:** IS8-17 is a
*sustained*-wrench criterion; the force cells are entry conditions only. Zero
behavioral change, no re-run; REPORT documents that discrimination lives in
the persistence window. Honest, cheap, and consistent with how the freeze
actually scored.

**Option 2 — recalibrate force cells to measured scales** (e.g., anchor
F_ax_jam above the successful-insertion p99): behavioral change → Class B →
joins the batched re-run/re-freeze. Sharper physical meaning, costs a
recalibration decision now on one probe record's evidence.

**To ratify:** pick one (or ask for a wider probe first — more records, both
outcomes, cheap and local).

### (c) R01 review findings — Class B set (added 2026-08-11 after the 8-lane surgical review; details in `studies/R01_PHASE1_REVIEW/FINDINGS.md`)

225/225 contract clauses verdicted; 24 findings survived adversarial
prosecution, 0 rejected. Eight are behavioral and need your ratification
before the single batched re-run that replaces `freeze_prior_v1`:

1. **F-012 (high) — every frozen trial ran with the target orientation
   inverted**: nominal engagement was realized as Ry(180°) instead of
   Rz(180°), so "plate up" mapped to head-*down* — the outer tag sits at
   z=−185 mm instead of +185, and camera view angles run 4–48° worse than
   the committed nominal (62° vs 15° at handoff, at the literature model's
   validity edge). Every frozen detection/confidence/refusal number
   inherits this. Two independent agents reproduced the numbers exactly.
2. **F-004 (high)** — hold/absence timers persist across D-005 retry
   attempts: a fresh attempt's first gap frame can instantly abort with the
   previous attempt's clock (violates D-034/D-036's own blip-vs-condition
   rule at the attempt seam).
3. **F-007 + F-008 (high)** — inner tags use the 110 mm constellation span
   instead of their own 10 mm size for both decode extent and flip
   discriminability: 10 mm tags "decode" at 3 m (IS §3.3 says ~3 px there)
   and lone tags become flip-immune (H08/D-011 say the opposite).
4. **F-016 (high)** — the latency sweep axis is behaviorally inert (no
   consumer reads t_emit; no staleness bound) — the frozen latency marginal
   is fake-flat, the exact hazard D-032(e) named.
5. **F-009 (med)** — σ_px's committed sweep {0.3, 0.5, 1.0} px is
   unrealizable (pinned at 0.5; not a sweep axis; the amendment trial.py's
   docstring promises was never recorded). Found independently by 3 lanes.
6. **F-005 (med)** — ambiguity-rejected frames still authorize commit at
   the trial seam (gate never reads ambiguity_flag).
7. **F-017 (med)** — trial_header lacks the compute-instance identity ARCH
   §5 commits (additive schema revision; pairs with the F-018 finding that
   regeneration only verifies on the freeze instance class).

Plus at the same sitting: H-17 host-attitude realization (your earlier
"batch with review fixes" answer), the F-013/F-014 realize-or-exclude
calls, the E-class doc repairs, and the #62/D-039 items above.
**Consequence of ratifying:** one batched fix set → local verification →
one cloud re-run (~$0.15–0.30, P-02-metered, your explicit go at launch) →
`freeze_prior_v2` with the gate restated pre-swap. `freeze_prior_v1`
stays committed as evidence.

What to read before signing, in order. The signature asserts one sentence: *"The
interface spec is precise enough that Phase 1 builds directly against it with no
further design decisions"* (the MASTER_CONTEXT Phase 0 gate condition).

1. **`HOLES.md`** (~10 min) — the whole ledger. Check that every hole names its door
   and that no closure reads like invention. Pay attention to the post-assessment
   section (H-13..H-16): the self-assessment passed and then planning found four more;
   the two new decisions below are what closed the substantive ones.
2. **`DECISIONS.md` D-029 and D-030** (~10 min) — the only *new* decisions since the
   self-assessment. D-029 defines "moderate degradation" — the cell your kill-gate
   number is computed over. **This is the most consequential thing you are signing**:
   if the band feels wrong (too easy, too harsh), say so now, not after 10,000 trials.
   D-030 defines `clean_miss`.
3. **`PHASE1_PARAMETERS.md`** (~15 min) — read the header, then spot-check any five
   rows: follow each row's Source column to the committed document and confirm the
   value is actually there. The gate claim is that all 65 rows survive this check.
4. **`ROADMAP.md` Phase 0 §Week 2 + `studies/H04` header and Addendum** (~10 min) —
   confirm the T1 ratification you made (D-027) is recorded the way you meant it.

**To sign:** say so in a session (it gets recorded here with the date), or commit an
edit striking P-05 yourself. On signature: Phase 0 closes, Phase 1 build opens
(`PHASE1_PLAN.md`).
