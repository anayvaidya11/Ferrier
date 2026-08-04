# Design Decisions — Record of Authority

Every spec statement in `INTERFACE_SPEC.md`, `ARCHITECTURE.md`, and `WIRE_FORMAT.md`
must trace to a REQ-xxx in `research/REQUIREMENTS.md` or a D-xxx here. A spec statement
with no traceable parent is a hole and must be flagged, not quietly asserted.

Superseded decisions are struck through, never deleted — the reasoning chain stays
auditable. Revisions carry an `-R` suffix.

---

### D-001 — Mating principle is split
Compliant funnel + active latch live on the WyZantium recovery head. A hardened male capture
stud + rigidly co-located fiducial live on the target vehicle.
**Consequence:** capture and load transfer are separate mechanisms with opposite
requirements. Adoption cost collapses to a machined stud and a plate. Mud accumulates on
the serviceable side of the interface.

### D-002 — Heritage is claimed through the mounting boss and load path only
Bolts to the existing lunette pattern, reacts into the same frame member. Never through
mating geometry.
**Consequence:** the capture feature is a **stud**, not a lunette and not a pintle. No
inherited qualification is claimed for the mating geometry. Using "pintle" for the
target-side feature inverts standard usage and will be caught.

### ~~D-003 — Preliminary latch load rating: 15 kN design~~ — superseded by D-003-R, 2026-08-01
~~≈10 kN breakout for a mired 500 kg UGV × 1.5 safety factor. Stated as an assumption,
unverified until Phase 2.~~
**Why superseded:** the INTERFACE_SPEC §2.1 derivation showed the stud has a different
governing load case than the latch — bending at the neck, not tension — so a single
tension rating conflated two structures.

### D-003-R — Two load ratings: latch tension and stud neck bending
**(a) Latch tension rating: 15 kN axial** — ≈10 kN mired-breakout for a 500 kg-class
UGV (§1.7) × 1.5. **(b) Stud neck bending rating: 462 N·m design moment** — the
transverse component of a 15 kN tow at the D-018 sector edge (15·sin 20° ≈ 5.13 kN) on
the 90 mm exposed length (D-016); SF ≈ 2.2 against class-typical 4140 QT yield
(655 MPa — a material-class value; Phase 2 sources the actual certificate).
**Both are static ratings, unverified until Phase 2; dynamic/snatch tow loads are
excluded and flagged as a Phase 2 item.**
**Consequence:** under tow the funnel carries zero load; the latch is the entire
primary structure and a single point of failure (unchanged). The stud's governing case
constrains approach/tow geometry — see D-018.

### D-017 — Confidence threshold is a swept parameter, and its sweep is a deliverable
`conf_min_attempt` is **not a constant**: it is the single parameter trading refusal
rate against the risk of committing to an insertion that should have been refused, and
§1.5's asymmetry (a refusal costs a wasted trip; a wrong insertion risks the asset) —
not a round number — is what sets it. Sweep {0.50, 0.60, 0.70, 0.80, 0.85, 0.90,
0.95}; default 0.85 is **arbitrary and labeled so**.
**Consequence:** Phase 1 outputs a **refusal-rate vs. damage-risk tradeoff curve** — a
second deliverable of D-014's class (ARCHITECTURE §6).

### D-018 — Approach and tow sector: ±20° about the stud axis (normative)
Final approach heading and applied tow direction shall lie within a ±20° cone of the
stud +X axis. Basis: the D-003-R(b) bending arithmetic — SF erodes from ≈2.2 at 20° to
≈1.5 at 30° (INTERFACE_SPEC §2.1, derivation shown there).
**What would make it wrong:** material below class-typical yield, dynamic amplification
beyond the static margin, or a Phase 2 neck redesign.
**Consequence:** propagates into the approach planner (ARCHITECTURE §2/§4) and the
resolver stage; Phase 2 verification item in ROADMAP.

### D-019 — Chassis positioning error model (form decided; magnitudes swept)
Error = slowly-varying Gauss-Markov bias (correlation length 2 m, swept) + white
jitter + Poisson-arrival slip events (exponentially distributed magnitude). Magnitudes
sweep at ×{0.5, 1, 2} of the §5 allocations. Rationale: captures mud-slip
phenomenology with few parameters.
**What would make it wrong:** a real platform dominated by oscillatory control
coupling rather than slip — Phase 3+ data would show it.

### D-020 — Latch success predicate (sim)
`latched` ⟺ stud-head center within 3 mm radial of throat axis at engagement depth,
closing speed ≤ 0.1 m/s, condition held 100 ms. Basis: §5 latch tolerance class;
speed bound tied to the insertion-speed sweep ceiling.
**What would make it wrong:** the Phase 4 latch CAD defining a mechanism with a
different engagement condition — restate then.

### D-021 — Phase 1 sweep design (DOE)
Three tiers: **Tier 1** one-factor marginal grids at nominal elsewhere (produces the
per-axis curves and the D-014/D-017 deliverables); **Tier 2** Latin Hypercube, N ≥
4,000 over the joint degradation space (interaction discovery); **Tier 3**
failure-replay set (A-007 artifacts). Total ≥ 10,000 trials (MASTER_CONTEXT Phase 1).
Full factorial (~10⁷ cells) is infeasible and unnecessary for the deliverables.
**What would make it wrong:** Tier 2 revealing interactions strong enough that Tier 1
marginals mislead — redesign the DOE then, as a recorded revision.

### D-022 — Success definition
Trial success ⟺ D-020 latch within the attempt budget (D-005/H-01) and total encounter
time ≤ T. **T swept {5, 15, 30} min, default 15 — arbitrary, labeled so** (mission
exposure time is a casualty-logic input, §1.3, with no sourced value yet).
First-attempt and multi-attempt distributions stay separate (D-005).

### D-023 — Interim mud-degradation model (until MR-001)
P(detect | mud fraction f) = P_mask(f) · C(f), where P_mask is the clean-mask
literature curve and C(f) = max(0, 1 − f/f_c) with f_c swept {0.6, 0.8, 1.0}
(f_c = 1.0 degenerates to the literature mask model). Direction is conservative — mud
strictly worse than clean masking. **The functional form is an assumption, labeled;
MR-001 replaces it.**
**What would make it wrong:** wet-mud specularity locally *raising* contrast, breaking
monotonicity — MR-001 would show it.

### D-024 — Host integration envelope (requirements WyZantium levies, not facts)
Free cylinder Ø270 × 400 mm forward of the plate (funnel outer Ø250 + 20 mm clearance;
depth 180 mm + drawbar + approach margin); stud axis height 400–800 mm; host resting
attitude within ±20°. These are interface *requirements* on integrators, derived from
the funnel envelope and §9's terrain sweep — renegotiated when real platform data
lands (Phase 2 / vendor engagement; none is published today, VENDORS.md).

### D-031 — Open-access literature substitution for the two paywalled dependencies (re-scopes P-06, P-07)
The program's evidence base had exactly two paywalled-paper dependencies, both
parked as .edu favors in PENDING_HUMAN. Decision, executed in two stages
(`research/OA_SUBSTITUTION.md` is the work-order): **Stage A** (2026-08-04) commits
the decision and candidate tables with every caveat left standing; **Stage B**
page-verifies the substitutes per the source-integrity rule and only then revises
caveats, per their written terms.
**Kallwies 2020 (P-07): replaced; the obtain-the-PDF ask is dropped.** Grounds:
nine dead retrieval routes (a settled negative); a public, unresolved ~40×
reproduction failure of its headline figure (github.com/UniBwTAS/apriltags_tas
issue #4 — caution-grade, not peer-reviewed); and the abstract's figures measure
the authors' improved method and OpenCV cornerSubPix, not stock-detector corner σ —
so the paper would not have anchored #40 even if obtained. Replacement path:
Adámek 2023 (Sensors, CC BY — closed-form pose-variance models; ArUco basis, so
candidate form-anchor with magnitudes staying swept/MR-measured) first, ranked
alternates behind it.
**Whitney 1982 (P-06): supplemented, not replaced.** An OA pair (Whitney's own MIT
OCW 2.875 "Rigid Part Mating" lecture + the CJME 2025 OA review, with Simunovic
1979 and R. Soc. Open Sci. 2019 as reinforcement) covers the theory components
(force equilibrium, wedging/jamming conditions, RCC parameter selection). The 1982
paper's **experimental validation has no OA substitute** — P-06 narrows to that one
component, optional, needed only if IS8-17 promotes T5 (D-027). The C-12 prior-art
DOI citation stands regardless.
**Consequence:** #40's sweep and the params/test transcriptions are untouched by
this decision; any future anchoring runs through the ROADMAP curve-swap protocol as
a recorded revision. No caveat is struck in Stage A; MR-004's fallback paragraph is
repaired (it named Kallwies as usable, contradicting its own UNAVAILABLE status).
**What would make it wrong:** Stage B failing to page-verify the candidates — then
the ranked backups are walked in order, and if all fail, the original paywalled
asks are reinstated in PENDING_HUMAN as written before this decision.

### D-030 — `clean_miss` outcome predicate (closes H-14)
`clean_miss` ⟺ all four hold: **(a)** the trial fails D-022; **(b)** no contact ever
occurred — no `sim_truth.contact_wrench` line exists in the record (no annulus
contact, no lip-band event); **(c)** every attempt either crossed the capture plane at
r > 160 mm (the D-006 kinematic-miss path) or ended on the attempt/time budget without
reaching it; **(d)** no INTERFACE_SPEC §8 row's wire signature matches under the
classifier's documented precedence order — the perception stream stayed nominal and
the miss is attributable to accumulated guidance/chassis error alone.
**The refusal path is not a clean miss:** a trial whose attempts were refused by the
gate (`abort_reason: low_confidence`, `ambiguity_persistent`, `inner_ring_absent`, …)
classifies to the §8 row named by that signature. IS8-15 (comms) remains nominal per
§8.
**Consequence:** `clean_miss` is the residual class — target never touched, nothing
classifiable explains why — so its fraction indicts the D-019 error budget against the
§5/§6 envelope arithmetic, not perception. The Phase 1 classifier implements a
documented precedence order (exactly one row per trial, FAILURE_TAXONOMY rule); a
trace matching no rule raises for a recorded amendment, never guesses (WIRE_FORMAT).

### D-029 — "Moderate degradation" defined numerically — the kill-gate cell (closes H-13)
The gate criterion (MASTER_CONTEXT Phase 1; ROADMAP) reads ">60% in moderate
degradation" but no committed definition of *moderate* existed anywhere in the repo —
found 2026-08-02 during Phase 1 planning, after the gate self-assessment. Left
undefined, the cell could be chosen after seeing results, which is refitting. Defined
now, before any trial runs:

**The moderate band** (degradation axes only, §9 grids; sampled uniformly over the
listed cells/ranges):

| Axis | Moderate band | Basis |
|---|---|---|
| Outer-tag occlusion | {30, 40}% | mid-grid; MASTER_CONTEXT's reporting example treats 40% occlusion as the mid-severity exemplar |
| Inner-ring occlusion | {30, 40, 50}% | mid-grid of the 0–90% axis (arbitrary, labeled) |
| Illuminance | {50, 100} lux | dim-but-lit band; the same example treats sub-10 lux as the severe regime |
| Rain | 10–20% | mid-grid (arbitrary) |
| Sensor dropout | p = 0.05, bursts on | second grid point (arbitrary) |
| Lens contamination | 10–25% aperture | mid-range (arbitrary) |
| Fiducial destruction | none | per-tag knockout is target damage, not environmental severity |

Host pitch/roll, view angle, and range are encounter geometry, not degradation dials —
they marginalize over their full committed distributions. All swept *system*
parameters sit at their labeled defaults (§9.1). The gate number is the success rate
over this band (D-022 success definition; first-attempt and multi-attempt reported
separately per D-005), with its confidence interval.
**Band edges are arbitrary-labeled mid-grid choices except where anchored above.**
Transcribed verbatim into `sim/scenarios/gate_moderate.json` before the first DOE run;
harness code never hardcodes it. Changing the band after any results exist is a
recorded revision reporting both numbers — the same discipline as the ROADMAP curve
swap.
**What would make it wrong:** MR-001/002 data placing a detection cliff at a band
edge, making the gate number knife-edge sensitive to the choice — then the gate is
reported as a curve across the band with the committed cell number alongside.

### D-028 — Feasibility-window semantics: intersection, not verdict (repairs the #63 mandate)
The original #63 mandate was doubly wrong: its trigger fired on *partial* band
exceedance ("required-k exceeds k_max"), and it hard-coded a verbatim conclusion into a
parameter row. Corrected semantics, two-sided:
**A vehicle class can dock iff [k_lo_req, k_hi_req] ∩ [k_min, k_max] ≠ ∅** — where
k_max = μ_trac·m_rv·g/35 mm is the derived static traction ceiling and k_min = n_F/δ_work
is the noise-floor bound (also class-dependent through n_F, a named Phase 2 unknown).
**Infeasible only on empty intersection. Partial overlap means a narrower usable band —
a tuning finding, not an elimination.** (As originally written, Phase 2 could have
deleted viable vehicle classes.)
**Reporting split:** PHASE1_PARAMETERS #63 **emits data only** — the per-class window,
the required band, their intersection, and the mask, tuple order (μ_trac, m_rv)
everywhere. **ARCHITECTURE §6.7 owns the interpretation, once, normatively**, with the
CLAIMS C-13 static-only caveat attached (Phase 2's dynamic analysis may lower k_max;
the window recomputes, these semantics don't change).
**Symbols:** μ_trac (recovery-vehicle traction) and μ_contact (stud/funnel interface,
PHASE1_PARAMETERS #31) are different physical quantities and never share a symbol.
**Provenance label:** the intersection is *simulated required band ∩ derived static
bounds* — not a pure simulation result; labeling it "derived from simulation" was the
§4.3 failure.

### D-027 — Funnel compliance topology RATIFIED: T1 — rigid steel funnel on a compliant instrumented base mount (closes H-04)
Ratified by the human 2026-08-02 (PENDING_HUMAN P-01), from
`studies/H04_FUNNEL_COMPLIANCE.md`. **Rationale:** T1 maximizes R6 simulatability —
rigid bodies + one 6-DOF spring-damper + hard stops is the only uncontroversial
Phase 1 contact model among the candidates, which protects the falsifiability of the
kill-gate number; best debris behavior under R5; benign, designable overload via hard
stops; high retry endurance under R3; and a clean single-interface net wrench for the
stage-3 direction signal under R2.
**Fallbacks (distinct, not interchangeable — they answer different failures):**
- **T4a deflection sensing** if stage-3 lateral-error *direction recovery* proves
  marginal in early Phase 1 trials. T4a does **not** address jamming: a symmetric jam
  produces near-zero net deflection just as it produces near-zero net wrench —
  deflection sensing is blind to it too.
- **T5 RCC geometry** if *throat jamming* dominates the failure taxonomy. Without the
  IS8-17 jam-detection outcome class (added with this ratification), that trigger
  would be **unobservable in Phase 1** — the study's own escalation path was
  unreachable as written; only the axial/lateral force criterion or T5's geometry
  addresses the jam failure.
The two reversal conditions of the study's §5 carry into this decision unchanged —
cited, not restated.
**R4 as ratified (revised — the original was wrong for angled tow):** *"Carries no
axial tow load; reacts lateral and moment components within the D-018 tow-angle
envelope."* Under tow at the D-018 sector edge the stud bears laterally against the
throat rim, which reacts directly into the compliant base — the mount sees tow-class
loads, not only capture impacts. Consequences: hard stops (or a lockout) sized against
D-003-R's structural load cases, bottoming before the elastomer carries tow-class
lateral load; Phase 2 verification item (ROADMAP).

### D-026 — Stiffness and head mass are swept; Phase 1 outputs a required-stiffness band
Parameters #35/#36 do not wait on Phase 2 chassis selection: compliance stiffness k
sweeps the derived envelope as a log grid {1, 3, 10, 30, 70} N/mm (studies/H04 §4) and
head effective mass M_eff sweeps a class range {8, 15, 30} kg. **The Phase 1
deliverable is a required-stiffness band** — "capture succeeds above the gate
threshold only for k within [X, Y] at M_eff = Z" — D-014's logic applied to
mechanics: a specification handed to the mechanical cofounder instead of a value
guessed today. The two-order-wide envelope stops being an embarrassment and becomes
the sweep axis.
**What would make it wrong:** a ratified H-04 topology whose compliance is not
representable as a single lumped k (e.g., T5's coupled off-diagonal terms) — then the
sweep re-parameterizes to that topology's stiffness description, as a recorded
revision. Only #34 (topology) remains a true H-04 blocker.

### D-025 — Cam B obliquity: 30°, justified band [15°, 45°]
Lower bound: constellation discriminability must survive partial occlusion down to an
adjacent two-tag baseline (studies/H08_AMBIGUITY_MODEL.md arithmetic). Upper bound:
far-side tag foreshortening and full-ring frame coverage through insertion. The
extrinsic translation stays [ASSUMED] within the band (D-012); **MR-003's oblique arm
uses 30°.**

### D-004 — Three-stage terminal guidance
3 m → 200 mm: outer fiducial visual servo. 200 mm → contact: inner-ring servo on an
off-axis camera. Contact → latch: contact-force-guided insertion, where the funnel wall
reaction force is the sensor.
**Consequence:** open-loop dead-reckoning is **rejected** — drift over mud with slip and
chassis compliance is the least honestly-modelable quantity in the simulation, and an
unfalsifiable assumption under the headline number is the decorative failure §2.2
forbids.

### D-005 — Retry loop
On failed insertion: back out 300 mm, apply the measured contact offset, re-approach.
**Consequence:** `attempts-per-encounter` is an explicit Phase 1 parameter.
First-attempt success and multi-attempt success are **reported as separate
distributions**.

### D-006 — Two-stage simulation
Approach and acquisition run in cheap kinematic sim; full contact physics runs only on
the last 50 mm, and only for trials that reach it. Contact physics runs on an **annulus
around the funnel mouth**, not only inside it.
**Consequence:** geometric near-misses must score as misses. If the annulus is omitted,
near-misses are silently scored as captures and the headline number is manufactured. The
**capture plane** and the **handoff state vector** must be specified in Phase 0 or
Phase 1 inherits a design decision.

### D-007 — Perception is injected, not rendered
Phase 1 never generates imagery. The perception stage is a stochastic model.
**Consequence:** the physics engine needs no renderer. Isaac Sim exits the plan. Newton
primary, MuJoCo/MJX fallback, with a predefined fallback trigger (see
`ARCHITECTURE.md` §4).

### ~~D-008 — Perception curves are literature-derived (B′)~~ — superseded by D-008-R, 2026-08-01
~~Published AprilTag characterization supplies detection probability and pose error as
functions of occlusion, illuminance, view angle, and range. Label: perception model
derived from published characterization, not measured on this system. Mud response is an
extrapolation and must be flagged as such per §4.3. Synthetic rendering (B‴) is a
Phase 1 stretch item, not a dependency.~~
**Why superseded:** D-008 was written under the 1 August NO_HARDWARE.md total-purchase
prohibition, which collapsed two different activities — building product hardware and
pointing a camera at a muddy tag — into one prohibition, and cost the program its
measured perception model. NO_HARDWARE.md rev 2 (instruments-not-artifacts) restores the
cheaper activity under the measurement-request protocol.

### D-008-R — Perception curves are measured where measurable, literature-derived where not
Detection probability as a function of occlusion, illuminance, and view angle is
measured on real printed tags with a real imaging instrument, per `MEASUREMENT_REQUESTS.md`
MR-001/002/003. Pose error covariance remains literature-derived and labeled (MR-004
DEFERRED). Mud response moves from *extrapolated* to *measured, consumer-grade
instrument, relative trend only* if MR-001 is collected; if it is not, it stays
extrapolated and the label says so.
**Consequence:** `ARCHITECTURE.md`'s real-vs-simulated table moves the perception rows
from Derived toward Built **conditional on collection** — rows stay marked *pending
MR-001/002/003* until data lands, and no row is marked Built on the strength of an
unfulfilled request. `INTERFACE_SPEC.md` §9–§10 describe the measurement plan and state
plainly what remains unmeasured after it completes. Phase 1 may open on
literature-derived curves and swap in measured curves when they land, with the swap
recorded and before/after results both reported (ROADMAP.md).

### ~~D-009 — No hardware purchases, binding, per NO_HARDWARE.md~~ — superseded by D-009-R, 2026-08-01
~~Supersedes any prior amendment authorizing hardware spend. The bench-measurement path
is cancelled. Camera parameters are assumed simulated values.~~
**Why superseded:** same narrowing as D-008 → D-008-R. The 1 August version of
NO_HARDWARE.md this decision cited has itself been superseded by revision 2.

### D-009-R — No product hardware; instruments via measurement requests only
No part of the product is purchased, fabricated, or assembled — binding per
NO_HARDWARE.md rev 2. Measurement instruments are permitted only through
`MEASUREMENT_REQUESTS.md` under the three-question test. The recovery head's camera
parameters (D-012) remain **assumed simulated values** — the measurement instrument is
not the product camera and its absolute values are non-transferable.

### D-010 — Fiducial family: AprilTag 36h11, reference C implementation
Chosen because the published characterization is the richest of any fiducial family (so
the literature-derived fallback under D-008-R is strongest), and the reference
implementation means a bench measurement characterizes the tag and detector, not our
integration.

### D-011 — Nested two-scale constellation
Outer: 150 mm tag on a 200 mm plate, sized for 3 m acquisition. Inner: ring of ~10 mm
tags readable to contact. Every tag ID maps to a known rigid offset from the stud frame,
so **any single visible tag yields full 6-DoF pose**.
**Qualification (added 2026-08-01, from studies/H08_AMBIGUITY_MODEL.md):** the
single-tag pose is position-reliable but **orientation is flip-prone for single small
tags** — a lone 10 mm tag cannot self-disambiguate the two-solution ambiguity at any
view angle at inner-servo ranges (discriminability ≈1.4 px, below the noise floor).
The 6-DoF claim stands as a positioning statement; **insertion commit requires ≥2
fused tags** (`pose_source: multi_tag_fused`, WIRE_FORMAT).
**Consequence:** two candidate layouts specified to fabrication precision — coplanar
cluster vs. inner ring raised on a collar — with the selection rule stated explicitly.
**Selection rule (rev 2026-08-01, propagated from D-008-R):** the layout is selected by
**MR-003's measured flip rate** across both candidate layouts. Note the original
formulation ("Phase 1 decision rule (measured flip rate)") was circular under D-007 +
old D-009: with no renderer and no bench, Phase 1's injected model would contain an
*assumed* flip parameter, and "measuring" it in sim measures the assumption back.
MR-003 breaks the circle with a physical measurement. **Fallback if MR-003 is never
collected:** a derived observability analysis — IPPE two-solution ambiguity separation
as a function of collar standoff and camera obliquity — selects the layout, labeled
derived.
**Scope consequence for Week 2 (rev 2026-08-01):** because selection now happens in
late August — before Phase 1 — `INTERFACE_SPEC.md` §3 carries **both candidate layouts
plus the MR-003 selection rule**, and **Phase 1 builds against whichever layout won,
only**. The candidates do not travel into Phase 1 as live alternatives; specifying both
to full fabrication depth as if Phase 1 must sweep them is over-specification. The
collar standoff is a **swept measurement parameter in MR-003, not a specified
dimension** — the shipped standoff is set by the selection analysis, and no spacer is
ever fabricated to a spec value (NO_HARDWARE.md rev 2).

### D-012 — Simulated sensor parameters, assumed
Cam A: 1920×1200 global shutter monochrome, ~70° HFOV, on funnel axis. Cam B: same
sensor, ~90–100° HFOV, mounted oblique off the funnel axis.
**Consequence:** labeled assumed and unvalidated against hardware. Cam B's oblique
mounting is load-bearing: it breaks the coplanar pose ambiguity by construction, because
the two-solution flip is worst near head-on and Cam B is never head-on.

### D-013 — No non-visual fallback that produces metric pose
Fiducial gone → degraded pose class → escalate with imagery. Never authorizes an
insertion attempt.
**Consequence:** consistency with D-004. A silhouette-fit fallback would produce a pose
confident enough to act on and wrong enough to damage the asset.

### D-014 — Headline Phase 1 output is a sensitivity curve
Docking success as a function of assumed detection rate — not a single success rate.
**Consequence:** survives uncertainty in the perception model because it does not depend
on any single perception value being correct. Produces a requirement handed to a
mechanical cofounder rather than a claim to defend.

### D-015 — Capture envelope at the capture plane: ±35 mm positional, ±10° angular
**Assumption, unverified until Phase 2.** The envelope the funnel must swallow,
referenced to the capture plane, not the latch. Added 2026-08-01 so the tolerance budget
in `INTERFACE_SPEC.md` §5 traces to a recorded decision rather than exempting itself
from the traceability rule.
**Consequence:** funnel mouth size is derived from this envelope plus stud head radius;
every budget allocation in §5 decomposes against these two numbers.

### D-016 — Provisional interface dimension set (assumed, Phase 2 verifies)
One named set of dimensions so the simulation and the spec share exact geometry. All
values **[ASSUMED]** pending Phase 2 structural work; sources of each are shown in
`INTERFACE_SPEC.md`: stud neck Ø25 mm, head Ø40 mm spherical-capped, exposed length
90 mm; funnel mouth Ø220 mm (derived from D-015 + head radius, arithmetic in §5–§6),
throat Ø42 mm, depth 180 mm (half-angle ≈26°, derived); target plate 200 × 200 mm;
outer tag 150 mm at +185 mm above stud axis; inner ring 8 × 10 mm tags at radius 55 mm;
collar standoff swept 10–40 mm (MR-003 measures at shop-bought heights; shipped value
set by the selection analysis, never fabricated to spec — NO_HARDWARE rev 2).
**Consequence:** Phase 1 builds against exactly these numbers; changing any of them is a
recorded decision revision, not a code edit.
