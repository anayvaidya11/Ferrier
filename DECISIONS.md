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
*(parenthetical repaired 2026-08-11, R01 F-010: the original "f_c = 1.0
degenerates to the literature mask model" was false under this decision's own
product form — at f_c = 1.0, P = (1−f)·P_mask, the mask model squared under
prior_v1's P_mask = 1−f; no f_c cell is a mask-only baseline)*. Direction is
conservative — mud strictly worse than clean masking. **The functional form is an assumption, labeled;
MR-001 replaces it.**
**What would make it wrong:** wet-mud specularity locally *raising* contrast, breaking
monotonicity — MR-001 would show it.

### D-024 — Host integration envelope (requirements WyZantium levies, not facts)
Free cylinder Ø270 × 400 mm forward of the plate (funnel outer Ø250 + 20 mm clearance;
depth 180 mm + drawbar + approach margin); stud axis height 400–800 mm; host resting
attitude within ±20°. These are interface *requirements* on integrators, derived from
the funnel envelope and §9's terrain sweep — renegotiated when real platform data
lands (Phase 2 / vendor engagement; none is published today, VENDORS.md).

### D-046 — Sweep-axes reconciliation + DOE revision for freeze_prior_v2 (R01 sitting; 2026-08-11)
The R01 review (studies/R01_PHASE1_REVIEW) found four committed sweep axes that
the frozen harness could not honestly produce. Reconciled here, all at once,
before the v2 re-run: **(a) σ_px joins SWEEP_AXES** with the #40 grid
{0.3, 0.5, 1.0} px and a Tier-1 marginal (F-009 — the pin at 0.5 was an
unrecorded exclusion; trial.py's promised amendment is this one).
**(b) Host pitch/roll are realized** (closes H-17): the sweep_point's
host_pitch_deg/host_roll_deg compose a tilt into the target pose ahead of
Q_NOMINAL, flowing through kinematic truth, sightings view angles, handoff,
and the contact model; Tier-1 marginals added over the D-024 ±20° envelope
and the D-029 gate cell marginalizes over the committed distributions as its
text always claimed. **(c) Latency is live** per D-045. **(d) Still
unrealized, now by recorded exclusion** (the H-17 lesson — exclusions are
written down, never silent): the IS §5 mount-tolerance contributor (F-013)
and the D-019 GM correlation-length sweep (F-014) — both stay fixed at their
committed defaults; realizing either is a future recorded revision. **(e) The
#62 jam force grid stays pinned at mid-grid** (per D-040 the discrimination
lives in the persistence window; joining the sweep axes is a future revision
if IS8-17 ever produces). **(f) trial_header gains compute-instance
identity** (F-017; ARCH §5's commitment, additive v1 schema revision like
H-16's false_capture) — engine AND instance now both land in every header.
Ratified by the human (R01 sitting, 2026-08-11, "I ratify P-08").
**What would make it wrong:** Tier-2 interactions invalidating the new
marginals (D-021's failure mode → recorded DOE revision), or Phase-3 real
data showing the tilt realization misses a dominant attitude effect.

### D-045 — Frames are consumed at arrival; staleness bound = the committed latency ceiling (R01 F-016; 2026-08-11)
The frozen harness consumed perception frames at capture time; t_emit was
written to the wire and read by nothing, so the swept latency axis {10, 30,
100} ms was behaviorally inert — a fake-flat marginal, the exact hazard
D-032(e) named (probe: sim/results/review_r01/F-016). Realization: the
closed-loop stage delivers each frame to guidance at **t_emit** (the vehicle
covers ground during the delay; walls and holds see delayed evidence), and
WIRE_FORMAT consumer-checklist item 4 is realized structurally — a frame
whose capture-age at consumption exceeds the **staleness bound** is treated
pose-absent. The bound is set to the #38 sweep ceiling (100 ms), **a labeled
class value taken from the committed sweep, not measured**: consumers
tolerate up to the swept latency ceiling; anything older (future queuing
paths) is pose-absent. Ratified by the human (R01 sitting, 2026-08-11).
**What would make it wrong:** a real perception stack whose queuing behavior
demands a tighter bound than its own latency ceiling — a Phase 3 observable.

### D-044 — Ambiguity-flagged frames are not commit evidence (R01 F-005; 2026-08-11)
IS §8 row 5 ("reject frame") and the WIRE_FORMAT worked flip example were
honored by the guidance machine but not by the commit path: trial.py latched
commit_line from gate.commit_allowed alone, and the gate never read
tags[].ambiguity_flag — a machine-rejected frame could authorize insertion
(dual reproduction in raw_lanes.json; fix-time probe under
sim/results/review_r01/F-005). Fix: the commit predicate gains an ambiguity
conjunct — a line carrying any flagged tag, or rejected by the machine, is
not commit evidence. D-013/#30 semantics otherwise unchanged.
Ratified by the human (R01 sitting, 2026-08-11).

### D-043 — Per-tag decode extent; flip discriminability from the visible span (R01 F-007/F-008; 2026-08-11)
sightings_for() hard-coded span_m = 0.11 (the full inner-ring constellation
span) for every inner tag, so (a) decode probability used a 34 px extent at
2.9 m where the per-tag truth is ~3 px — 10 mm tags "decoded" at 3 m against
IS §3.3's own arithmetic, bypassing IS8-2 semantics in outer-destroyed
cells; and (b) flip discriminability made lone tags flip-immune, inverting
D-011's qualification and H08's committed model (probes:
sim/results/review_r01/F-007, F-008). Fix per the committed sources: decode
pixel extent uses the **per-tag size** (IS §3.2/§3.3); flip discriminability
and ambiguity ratio use the **visible-constellation span** (H08 §2: lone tag
= tag size; multi-tag = span of the tags actually detected this frame).
Ratified by the human (R01 sitting, 2026-08-11).
**What would make it wrong:** MR-003 measuring flip behavior the H08
visible-span model cannot reproduce — the curve-swap protocol owns that.

### D-042 — Guidance walls and streaks reset at attempt boundaries (R01 F-004; 2026-08-11)
_hold_since / _ring_absent_since / _ambiguity_streak survived D-005 retries:
a fresh attempt's first gap frame inherited the previous attempt's open
window and aborted at 0.000 s against D-036's 5 s wall (probe:
sim/results/review_r01/F-004, four variants, fresh-machine controls). Same
blip-vs-condition disease as D-034/035/036, at the attempt seam. Fix: the
trial's attempt transition resets the machine's evidence windows and
streaks; within-attempt semantics unchanged.
Ratified by the human (R01 sitting, 2026-08-11).

### D-041 — Nominal engagement orientation is Rz(180°) (R01 F-012; 2026-08-11)
Q_NOMINAL was realized as (0, 0, 1, 0) = Ry(180°), mapping stud +Z ("plate
up") to head −Z — every frozen trial rendered the outer tag at z = −185 mm
in head_frame with cam A view angles 37.7°/62.4° at 300 mm/handoff where the
IS §4 + §7 constraint set (anti-parallel +X, +Z∥+Z at level attitude,
right-handed) uniquely requires Rz(180°) = (0, 0, 0, 1) → +185 mm,
6.1°/14.8° (probe: sim/results/review_r01/F-012, N=50/arm; all 10 checks).
Nominal-cell outcomes were invariant (50/50 both arms) — the contamination
concentrates in the degraded bands, i.e. the D-029 gate cell. Fix:
Q_NOMINAL = (0, 0, 0, 1); the freeze regenerates as freeze_prior_v2.
Ratified by the human (R01 sitting, 2026-08-11).

### D-040 — #62 jam grid stands; discrimination is carried by the persistence window (R01 sitting; 2026-08-11)
The week-one #62 recalibration check (sim/results/probe62_check.json) found
successful-insertion transients exceed F_ax_jam at p90 and F_lat_jam at p99
— the force cells do not separate jam from normal contact; the 1.0 s
persistence window does. Decision (P-08(b) Option 1, the no-behavior-change
default under the blanket ratification): **the committed grid stands; IS8-17
is a sustained-wrench criterion; the force cells are entry conditions only.**
REPORT documents this semantics. Recalibrating the cells to measured scales
remains open as a future recorded revision if IS8-17 ever fires.
Ratified by the human (R01 sitting, 2026-08-11).

### D-039 — MuJoCo is the Phase-1 engine of record; A-004 GPU leg waived as moot (2026-08-11)
ARCH §4's day-one Newton conformance never ran — Newton was never
provisioned (GPU quota; credits landed after the CPU path was proven). The
entire experiment runs on MuJoCo 3.11.0, which passed the conformance suite
and the bit-identical replay contract. PHASE1_PLAN §3's "both measurements
committed" is waived by this record: the full DOE costs ~$0.25 of compute,
so no GPU measurement could change the winner while costing more than it
could recover. The Newton adapter stays in-tree as a labeled stub.
Ratified by the human (R01 sitting, 2026-08-11).
**What would make it wrong:** Phase 2+ contact workloads at a scale where
the $/trial comparison stops being moot — re-open with a fresh cost test.

### D-038 — Gate-cell trial count: N = 5,000 (DOE addendum to D-032; 2026-08-09)
D-021 fixed tier shapes and D-029 fixed the gate band, but no committed number set
the gate cell's own trial count (`gate_plan(n)` left n a CLI argument). Recorded
now, before the formal freeze: **N = 5,000**. Sizing: the D-029 gate number carries
a 95% CI; at worst-case p ≈ 0.3 the Wilson half-width at N = 5,000 is ≈ 1.3 pp (≈
0.6 pp at p ≈ 0.05) — comfortably inside the 1 pp reporting granularity of the gate
table's thresholds. Totals: 4,400 (Tier 1) + 4,000 (Tier 2, n_min) + 5,000 (gate) =
13,400 ≥ the committed 10,000 (D-021), before post-swap re-runs. Approved plan,
2026-08-09 ("Phase 1 completion plan", step 4).
**What would make it wrong:** a gate number landing within ~1 pp of a decision
boundary — then N grows by recorded revision until the CI excludes the boundary,
never silently.

### D-037 — Closed-loop kinematic stage: holds are physically real (retires the T5 open-loop limitation; 2026-08-09)
T5 was open-loop by design: perception frames were generated post-hoc along a
precomputed trajectory, so hold/reject decisions could not slow the vehicle —
a labeled limitation ("revisit at T10", trial.py docstring). Consequence: the
D-034/035/036 walls fired on a clock while the vehicle kept driving; refusal
timing and retry geometry were approximations a diligence reader would find in
one read. **Realization from here: the spatial path and its D-019 chassis-error
realization are unchanged (error is indexed by arc length — a stationary
vehicle does not accrue slip); what closes the loop is the time mapping. A
"hold" freezes position (v = 0) while frames keep arriving at the perception
cadence — stop, stare, reacquire; "continue" resumes along the same path;
abort/escalate end the attempt at the held position. Walls fire on sim time at
a fixed position. Frames zero-order-hold truth at the last grid point
(pre-existing behavior). The handoff state's time is the pause-aware crossing
time; the encounter budget therefore counts hold time, as it should.**
Ratified by the human (plan session, 2026-08-09, "Fix now"). Every pre-D-037
record regenerates; pre-D-037 summaries stay committed as historical evidence.
Retry noise realization (chassis substream restarting identically per attempt)
remains a separate labeled limitation — not expanded here.
**What would make it wrong:** a real platform whose hold behavior is not
station-keeping (e.g., drift under mud creep while "stopped") — an MR/Phase 3
observable; or doctrine forbidding stationary dwell in the open (would bound
HOLD_TIMEOUT_S, not the mechanism).

### D-036 — Rows 3/4 ring persistence is a time window on the shared wall (closes H-18's third cause; 2026-08-09)
Post-D-035 gate re-probe still returned 0.0: every attempt died `inner_ring_absent`
in the 300→200 mm band and no frame ever reached inner_servo. The instrumented
per-frame data (nominal vs gate, 50 records each) showed RING_PERSIST_FRAMES = 5
(0.17 s at 30 Hz) was mis-scaled on its own terms: **nominal** frames near handoff
carry < 2 inner tags up to 73% of the time (foreshortening alone — streaks fire at
zero degradation and nominal survives by stage timing), while at the gate cell the
ring is intermittently present (P(≥2 tags) ≈ 0.19–0.23 per frame ⇒ a genuine
confirmation about once per second) and the frame-scale streak reads that jitter as
absence. Same blip-vs-condition class as D-034/D-035, so the same instrument:
**ring absence is sustained time on the shared HOLD_TIMEOUT_S wall — < 2 inner tags
continuously for 5 s aborts (row 3) or, ring-dead at handoff range with outer pose
good, escalates without consuming an attempt (row 4, D-013 unchanged); stochastic
gaps reject frames and reset on any ≥ 2-tag frame. RING_PERSIST_FRAMES retired.**
Decided by the human (recorded answer, 2026-08-09 session, third H-18 brief, framed
as final: no further gate surgery — whatever the gate scores after D-036 is
reported as-is; fused-conf refusal at commit is characterized by the D-017 sweep,
not patched).
**What would make it wrong:** evidence that sustained-seconds absence windows mask
a real occluded-ring hazard on approach paths the sim's open-loop T5 cannot
represent (Phase 3 real-data check).

### D-035 — conf_min is commit-scoped: the row-1 hold wall applies at inner range only (closes H-18's second cause; 2026-08-09)
Post-D-034 gate re-probe still returned 0.0 over 500 trials: detected-frame
confidence at the D-029 cell medians 0.16 (p90 0.49, n=9,351 frames) against the
0.85 wall, because row 1 was realized as "hold whenever conf < conf_min at ANY
stage" — one muddy outer tag cannot sustain commit-grade evidence mass under
compound degradation, so approaches die before the commit gate ever operates
(census: 335× IS8-1, 165× IS8-3). D-013/#30 define the threshold at the **commit
predicate** (inner_servo ∧ multi_tag_fused ∧ conf ≥ threshold); §1.5's asymmetry
says approach is the reversible, cheap act and insertion is the guarded one.
**Realization from here: the row-1 conf wall holds only at inner range
(≤ INNER_RANGE_MM), where fused commit-grade confidence is the operative
question. At outer range a detected frame is tracking evidence and the approach
continues; absence of detections is governed by the D-034 dark wall; ambiguity
rejection (row 5) unchanged; the commit predicate itself unchanged.** Decided by
the human (recorded answer, 2026-08-09 session, second H-18 brief). The asset
remains protected where the product's honesty discipline lives: at commit —
refusal there is measured, not pre-empted at approach.
**Consequence:** gate-cell trials now reach inner range and the D-017
refusal/damage tradeoff is measured at its intended site. Pre-D-035 gate probes
stay committed as H-18 evidence, not poolable data.
**What would make it wrong:** doctrine requiring commit-grade confidence to even
maneuver near a casualty (would be an IS revision), or Phase 3 real-data evidence
that low-conf outer tracking correlates with approach-phase collisions the sim
cannot see.

### D-034 — IS §8 row 2 realized with persistence: sustained dark window, not single frame (closes H-18's dominant cause; 2026-08-09)
Row 2 ("no outer detection at expected range") was realized per-frame: one
no-detection line escalated `low_confidence` immediately. The #43 dropout model
produces ~0.17 s blips (Bernoulli 0.05 burst starts, geometric mean-5 at 30 Hz), so
the D-029 gate band scored ~0% for a sensor-blip artifact, not a docking result —
H-18's Tier-1 evidence: dropout_p = 0.05 *alone* → 0/50 success, IS8-1-dominated
(`sim/results/tier1_prior_v1_summary.json`). Rows 1/3/4/5 all received persistence
mechanisms for exactly this per-frame-jitter reason (T8 composition findings); row 2
was the only §8 row without one. **Realization from here: a no-detection frame
starts/continues a dark window; row 2 escalates only when the window exceeds
HOLD_TIMEOUT_S (the same 5.0 s wall as row 1's hold — one coherent semantics: outer
channel dark *or* degraded for 5 s ⇒ escalate; the constant remains code-level
arbitrary, labeled, uncommitted). Any detection resets the window; single blips are
held frames, not aborts. Routing clause: a fully-dark frame — no tags, pose_source
"none" — is row 2's domain at *any* range and never feeds rows 3/4's ring streak
(a blip is not an occluded ring); rows 3/4 act only on frames carrying detection
evidence, which preserves IS8-2 for whole-approach blindness (the committed
test's signature) instead of a blind dead-reckoning walk into a spurious IS8-3.
POLICY_CLOSE_WITHOUT_OUTER semantics unchanged.** Decided
by the human (recorded answer, 2026-08-09 session, "fix then re-probe"); all
pre-decision probe/Tier-1 artifacts stay committed as the before evidence.
**Consequence:** every record produced under the per-frame reading regenerates under
D-034 code; the pre-fix Tier-1/probe summaries are historical evidence for H-18, not
poolable data. IS8-2 (zero detections whole-approach) remains reachable — genuine
blindness still classifies.
**What would make it wrong:** a committed doctrine that any sensor dropout mandates
mission abort (would be an IS §8 revision, not a code default), or MR/field data
showing dropout episodes correlate with total perception loss ≫ 5 s.

### D-033 — IS8-18: insertion incomplete at encounter budget (extends §8; T9 review, 2026-08-08)
The T9 code review confirmed two trace shapes today's sim produces that no §8 row
names: a contact-stage timeout with contact but no full stroke (shallow stall below
the #62 jam thresholds — static stall force ~30 N against F_ax_jam = 100 N mid-grid),
and a budget-truncated insertion window (handoff lands with seconds of budget left;
the contact stage gets the sliver and times out). The classifier's contract raises
`UnclassifiedFailure` on both — correct discipline, but the raise fires inside
`run_trial`, so a T10 sweep would crash mid-batch on a physically ordinary outcome
and lose the trial record. FAILURE_TAXONOMY's own rule names the fix: *unclassifiable
failures extend §8 by recorded amendment first*. This is that amendment: **§8 row 18,
"insertion incomplete at encounter budget"** — the attempt crossed the capture plane
and the insertion window ended on the time/attempt budget with no latch confirm and
no other §8 signature. Never folded into IS8-10 (a latch-mechanism signature, not a
budget artifact; row 10 now also requires the D-020 positional predicate — depth AND
radial — so out-of-funnel trajectories cannot masquerade as full strokes) and never
clean_miss (the plane was crossed; D-030 (b)/(c)). Wire enum, schema, #57, taxonomy,
precedence order (position 12, after IS8-10, before the perception rows), and the
classifier table extend together; `AttemptEnd.timed_out` is the detection signature.
**Consequence:** if IS8-18 dominates a sweep, the finding indicts the encounter time
budget T (#55, arbitrary and unsourced) and the insertion speed class (H-02), not the
mechanism — the honest dial is mission-exposure sourcing. The #62 recalibration hook
(sub-threshold stalls reading as IS8-18 instead of IS8-17) is the recorded revision
path if week-one force scales show the jam thresholds miss real stalls.
**What would make it wrong:** #62 recalibration reclassifying most IS8-18 mass as
IS8-17 — then the row shrinks to true budget truncations, reported as the revision.

### D-032 — DOE execution semantics: committed grids, seed rule, spend metering, resume (T10, 2026-08-08)
D-021 fixed the tier *shapes* but left the runner's semantics open; T10 closes them,
committed here and as scenario data so "tier cell counts correct" has a referent.
**(a) Grids are data:** `sim/scenarios/nominal.json` (IS §9.1 defaults + zero
degradation), `tier1.json` (per-axis marginal grids; arbitrary steps labeled per axis
where §9/§9.1 gives only a range), `tier2.json` (LHS domains, degradation axes only) —
transcription-tested, never hardcoded (the D-029 gate_moderate.json discipline
extended). Tier-1 grid points equal to nominal collapse into one shared nominal cell.
**(b) Seed rule:** trial seed = top 63 bits of sha1("{sweep_root}|{tag}"), tag unique
within the sweep. Pure, order-independent, resume-stable; replicates at the same
sweep point get distinct seeds, so `trial_id` (engine-seed-sweephash) never collides —
closing the silent-overwrite hazard the pre-D-032 id scheme allowed. Samplers draw
from per-plan streams derived the same way (mutually independent, deterministic).
**(c) Spend metering:** the ceiling is read from `sim/scenarios/spend_p02.json`
(P-02/A-011(c)) only; cumulative spend persists in a ledger under `sim/results/`;
the $/trial rate is a committed input (from the A-004 measurements when they exist;
0 for local runs). Two trips, both hard stops raising for a recorded amendment:
*projected* (plan × rate + spent would cross the ceiling — refuse to start, risk #3's
wording) and *imminent* (the next trial would cross it — stop before dispatching).
**(d) Resume:** per-trial granularity; the completeness oracle is
`validator.validate_trial_file(path) == []`, never bare existence; sound because the
record writer is atomic (serialize-all, tmp + os.replace). A valid on-disk record is
skipped; anything else is re-run and overwritten.
**(e) Exclusions:** host pitch/roll are in the sweep_point but realized nowhere in
the harness — excluded from both tiers rather than emitting fake-flat curves,
recorded as **H-17** (open); their grids land with the realization. `curve_set` is
the swap seam, re-run under the ROADMAP protocol, not a marginal axis.
**(f) #33 probe reading:** "success-rate delta < 1%" is absolute percentage points.
**What would make it wrong:** H-17's realization shifting outcomes enough that
committed Tier-1/Tier-2 datasets need re-runs (a recorded revision reporting both);
or A-004 measuring a $/trial rate that makes the committed replicate counts cross
the P-02 ceiling — then the counts are revised by recorded amendment, never quietly.

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
