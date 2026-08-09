# Phase 1 Execution Map — The Docking Experiment

Committed 2026-08-02 (A-011). **Authority: the specs win.** This file sequences the
build; every behavioral rule it references lives in `INTERFACE_SPEC.md`,
`WIRE_FORMAT.md`, `ARCHITECTURE.md`, `PHASE1_PARAMETERS.md`, and `DECISIONS.md`. Where
this file and a spec disagree, the spec is right and this file has a bug (MASTER_CONTEXT
§2.5 documents-win rule). Build opened 2026-08-02 on the P-05 signature; window ends
30 September.

One question, one number: given a standardized target interface, what fraction of
autonomous approach-and-latch attempts succeed under realistic field degradation?
Gate: >60% over the D-029 moderate band → Phase 2; 30–60% → iterate two weeks, re-run;
<30% → stop, revisit the wedge.

## 1. Shape of the experiment

Two-stage sim (D-006): cheap kinematic approach/acquisition; full contact physics only
on the last 50 mm, only for trials whose predicted stud-head center crosses x = +50 mm
(head_frame), on the 160 mm annulus disc — r > 160 mm at the capture plane is a
kinematic `clean_miss` (D-030). Perception is an **injected stochastic model** (D-007);
no renderer exists anywhere in Phase 1. Contact model is the ratified T1 (D-027): rigid
funnel + stud, one 6-DOF spring-damper at the base + hard stops. Engine: Newton
primary, MuJoCo fallback on the ARCHITECTURE §4 day-one trigger. ≥10,000 trials across
the D-021 three-tier DOE. Every trial writes one WIRE_FORMAT NDJSON record, replayable
bit-identically from its header (seed, SHA, engine, sweep_point).

## 2. Code structure

Language: Python 3.11+ (no committed constraint found; Phase 3 firmware is embedded C
against the same wire contract, which is why the contract package below is
language-neutral at its boundary). Two installable packages under `sim/`:

### `sim/wirefmt/` — the contract package (ARCHITECTURE §3 "Built" tier)

Dependency-free (stdlib only). The cross-language artifacts are JSON Schema files and
golden fixtures; Phase 3's C firmware implements against the same schemas and must pass
the same fixture corpus.

| File | Responsibility | Binds to |
|---|---|---|
| `schema/*.v1.schema.json` | target_state, trial_header (incl. #33 solver block + compute-instance identity), sim_truth, trial_result (incl. `false_capture`) | WIRE_FORMAT; PHASE1_PARAMETERS #33, #58 |
| `validator.py` | Line- and file-level validation implementing the consumer checklist in order, incl. omitted-not-zeroed (pose without pose_cov ⇒ pose-absent) | WIRE_FORMAT §Consumer checklist |
| `records.py` | Typed constructors + canonical NDJSON writer (shortest round-trip floats, fixed key order, LF) — required for bit-identical replay | WIRE_FORMAT; #60 |
| `fixtures/` | Golden trial record + one negative fixture per rule (incl. the zeroed-pose anti-example from WIRE_FORMAT's worked failure) | WIRE_FORMAT |

### `sim/wyzantium_sim/` — the harness

| Module | Responsibility | Binds to |
|---|---|---|
| `params.py` | All 65 entries as typed constants/sweeps; transcription test asserts each equals the committed doc value | PHASE1_PARAMETERS |
| `frames.py`, `geometry.py` | Frame algebra (quaternion w,x,y,z); D-016 dimensions + §3.5 tag-ID→transform table | IS §3.5, §4, §6 |
| `rng.py` | Single root seed → named substreams (chassis, perception.*, contact, doe) via `SeedSequence.spawn` | #60 |
| `kinematic/` | Approach integrator; handoff trigger at x = +50 mm; annulus test; D-019 chassis error (Gauss-Markov 2 m + jitter + Poisson slip, ×{0.5,1,2}); frozen `HandoffState` dataclass — field list tested equal to IS §6's | D-006, D-019; IS §5–6 |
| `perception/` | Injection orchestrator: detection model (#39), mud (D-023), flip (H08 §4, κ), σ_px→pose_cov (#40 via #19/#20 camera models), dropout/contamination/rain (#43–45), rate/latency (#37–38). **Curve-swap seam** (`curves.py`): registry {`prior_v1`, `mr_v1`}; active set ID stamped into every `trial_header.sweep_point` | D-007, D-008-R; studies/H08 |
| `guidance/` | Confidence gate (D-013/D-017; commit ⟺ multi_tag_fused ∧ inner_servo ∧ conf ≥ threshold); D-004 3-stage state machine; D-005 retry (back out 300 mm, apply `last_contact_offset`); D-018 ±20° sector constraint; stage-3 contact guidance consuming the wall-reaction wrench | D-004/005/013/017/018 |
| `contact/` | `ContactEngine` protocol (§3 below); engine-neutral T1 model builder; `newton_engine.py` + `mujoco_engine.py` adapters; contact-stage runner evaluating D-020 latch predicate and the IS8-17 jam criterion (#62) per step | D-027, D-020; IS §8 rows 16–17 |
| `classify/outcomes.py` | Table-driven trace→outcome mapping: success \| IS8-1..17 \| clean_miss (D-030), documented precedence order, one row per trial; unmatchable trace raises `UnclassifiedFailure` (recorded-amendment path, never a guess) | FAILURE_TAXONOMY; D-030; #57 |
| `logging/trial_logger.py` | Header/state/result NDJSON via `wirefmt`; sim_truth every physics step post-handoff, every kinematic step pre-handoff; contact_wrench omitted pre-contact | WIRE_FORMAT; #59 |
| `trial.py` | `run_trial(seed, sweep_point, engine, curve_set) → record path` — composition root, the unit of replay | all above |
| `doe/` | Tier generators (Tier 1 marginals; Tier 2 LHS N ≥ 4,000; Tier 3 replay set); resumable multiprocess runner with **cumulative spend metering against the $100 ceiling (P-02)**; #33 convergence probe; A-004 cost probe | D-021; A-004; #33, #50–53, #61 |
| `replay/` | Re-run any committed record, diff byte-for-byte; A-007 artifacts rendered from logged state (trajectory/wrench animation — not imagery; D-007 untouched), labeled *simulated* | A-007 |
| `analysis/` | D-014 sensitivity curve; D-017 refusal/damage curve; first/multi-attempt splits; failure distribution; #63 feasibility windows + intersections (data only — interpretation stays in ARCHITECTURE §6.7); refuses to pool across curve-set IDs | D-014/017/028; ARCH §6 |
| `sim/scenarios/` | Committed sweep-point definitions per tier + `gate_moderate.json` (verbatim transcription of D-029 — code never hardcodes the gate cell) | D-029, D-021 |
| `tools/charts.py` | Charts for `sim/REPORT.md` from `analysis/` outputs | ARCH §6; §2.5 |

Local dev: **MuJoCo is the dev/test engine regardless of the production winner** — the
M4 Mac has no CUDA and cannot run Newton (Warp). Test suite is engine-parameterized;
Newton cases skip locally, run on the provisioned instance.

## 3. Engine abstraction and the two week-one tests

**`ContactEngine` protocol:** `load(T1ModelSpec, SolverSettings)` /
`set_state(HandoffState)` / `step(dt) → StepResult` / `state()`. `StepResult` carries
body states plus **per-contact-point reports** (position in head_frame, normal, force)
and the aggregated wall wrench. Per-point data is deliberate: the fallback trigger
demands spatial resolution sufficient to recover lateral-error direction (ARCH §4),
IS8-16 needs contact radius in the lip band, IS8-17 needs the axial/lateral split.
Everything downstream consumes `StepResult` only — engine swap is a constructor
argument recorded in `trial_header.engine`.

**Day-one engine conformance suite** (= the ARCH §4 fallback test, run on the first
provisioned instance): (1) stud dropped onto the wall at known lateral offsets — wrench
must recover sign and magnitude-ordering of the offset; (2) symmetric throat wedge —
high-axial/near-zero-lateral signature observable; (3) lip-band strike — contact radius
within [110, 125] mm; (4) determinism — same seed twice → identical trajectories
(bit-identical replay is a WIRE_FORMAT contract; an engine/instance that cannot run
deterministically fails provisioning even if it wins on cost, recorded with the A-004
result); (5) spring/restitution/friction sanity vs closed-form single-contact cases.
Newton failing any of 1–4 ⇒ MuJoCo, zero harness rework, decision recorded.

**A-004 cost test** (week one, before provisioning anything): 1,000 nominal trials
through the full capture-plane + annulus pipeline on a cloud CPU instance and a GPU
spot instance; measured $/1k trials; winner provisioned, **both measurements
committed** to `sim/results/a004/`. Representative means: handoff states sampled from
the §5 tolerance budget under D-019 at ×1 (not idealized centers — the outcome mix
sets per-trial step counts); D-005 retry loop on at default 3 (retries multiply contact
invocations; hourly billing punishes exactly that, ARCH §5); full trial logging on;
solver settings from a first-pass #33 probe. The kinematic stage stays off the cost
path by design (that is the point of D-006).

## 4. Build order (TDD; each task's definition of done is its verification gate)

| # | Task | Verification gate |
|---|---|---|
| T0 | Scaffolding: pyproject, pytest, lint | suite green empty; packages import |
| T1 | **`wirefmt`: schemas + golden fixture + validator + writer** — first code in the repo | golden validates; each negative fixture rejected for its stated reason; write→parse→write byte-identical |
| T2 | `params.py` + scenario loader | transcription test: 65/65 equal to doc values; `sweep_point` serializer covers every §9/§9.1 axis against a literal list |
| T3 [P] | frames/geometry/rng | transform property tests; tag table == IS §3.5; substream independence |
| T4a [P] | D-019 chassis error | statistical gates: GM correlation ≈2 m, Poisson arrivals, exponential slip, ×{0.5,1,2} scaling |
| T4b [P] | Perception injection (all models + seam) | each model vs its committed formula; every emitted line passes `wirefmt`; non-detections omit `pose`/`tags`; latency/rate honored |
| T4c [P, critical path] | Engine adapters + conformance suite | suite passes on chosen engine; Newton-vs-MuJoCo decision committed with suite output |
| T5 | Kinematic stage + handoff | nominal run hands off at x=+50 mm; synthetic r>160 mm → clean_miss; `HandoffState` fields == IS §6 list |
| T6 | Gate + guidance state machine | table-driven: commit predicate exact; §8 rows 1–5 stream patterns → specified responses; retry geometry; budget → escalate; heading ∈ ±20° |
| T7 | Contact stage | centered handoff latches (D-020); offset handoff → wrench sign matches; symmetric wedge fires IS8-17; lip strike radius ∈ [110,125] mm |
| T8 | `trial.py` + logger end-to-end | full record validates line-by-line; #59 cadence asserted; **same seed twice → byte-identical files** |
| T9 [P] | Outcome classifier | one constructed trace per class (success, IS8-1..17, clean_miss) → exactly that class; precedence pairs tested; unmatched raises |
| T10 | DOE runner + probes | 50-trial mini-sweep survives kill/resume; tier cell counts correct; convergence probe halts on <1% delta; spend meter trips on synthetic overrun |
| T11 [P] | Replay + A-007 artifacts | replay bit-identical; artifact generated from a record, labeled *simulated*, carries trial_id |
| T12 [P] | Analysis + charts | golden mini-dataset → known curve values; **#63 pinned cross-check reproduced: (μ_trac, m_rv) = (0.2, 300 kg) → k_max ≈ 17 N/mm → k ∈ {30, 70} masked infeasible** |
| T13 | REPORT assembly + CLAIMS rows | every ARCH §6.1–6.7 output present, traceable to committed files |

T4a/T4b/T4c parallel after T0–T3; T9/T11/T12 parallel with DOE runs after T8.

*Gate note (2026-08-08, T9): the T9 gate reads "one constructed trace per class
(success, IS8-1..17, clean_miss)" — but IS8-15 is nominal, not a failure (IS §8 row 15
/ REQ-005 / D-030), so per this file's header (the specs win) the gate is read as: one
trace per classifiable class (success, IS8-1..14, 16, 17, clean_miss), plus a test
asserting IS8-15 is unreachable as a classifier output while remaining in the wire
enum. The committed precedence order lives in FAILURE_TAXONOMY.md §"Classifier
precedence", transcription-tested against the code table.*

## 5. Week-by-week (build start ≈ Aug 4, on P-05 sign-off)

*Schedule note (2026-08-04): the week-1 provisioning day (Day 2–3) slides to after T8
lands and cloud credits arrive (~1 week out). No committed decision fixes a provisioning
date, and A-004's own definition of a representative workload (§3) requires T4c, T6, T7,
and T8 to exist first — so the local build queue (T4c MuJoCo half → T5 → T6 → T7 → T8)
proceeds in the interim on the M4. A-004 content unchanged; this is a sequencing note,
not an amendment. 2026-08-08 update: cloud credits are abandoned (human decision —
the application process is not worth a $20–60 expected spend); provisioning waits
only on T8 (done) and pays retail under the P-02 ceiling. Still a sequencing note.
Same-day reversal, 2026-08-08 late: the abandoned path was a paperwork application;
AWS's console offered $20/activity credits for five one-click activities, all five
driven in-session at near-zero cost (budget alarm, EC2 launch/terminate, Lambda,
RDS create/delete, Bedrock invoke); Billing shows $180 credit remaining vs $0 used.
Provisioning now draws on credits; the P-02 $100 ceiling and the runner's spend
meter are unchanged, and an AWS Budgets alarm (`wyzantium-p02-ceiling`, alerts at
50/80/100% of $100/mo) now backs the meter externally. Still a sequencing note.*

| Week | Work | Must land |
|---|---|---|
| 1 (Aug 4–10) | T0–T3 + T4c. Day 2–3 = first provisioning day: **engine conformance suite → fallback decision recorded**. Day 5–7: #33 first-pass probe → **A-004 cost test, both $/1k committed, winner provisioned**. From measured force scales: **#62 jam thresholds recalibrated, recorded revision** | All three week-one obligations (ARCH §4, §5; #62) |
| 2 (Aug 11–17) | T4a, T4b complete; T5; T6 begun | D-019 statistical gates; handoff spec-equality |
| 3 (Aug 18–24) | T6 done; T8 end-to-end; T9, T11; ~200-trial smoke sweep committed; curve-swap seam tested on synthetic MR-format CSV | First full records validate + replay |
| 4 (Aug 25–31) | T10 hardened; **Tier 1 marginal grids** → draft D-014/D-017 curves. Human's 3-day **measurement window** ≈ here: freeze tagged pre-swap Tier-1 dataset on `prior_v1`; when MR CSVs commit, register `mr_v1`, re-run affected axes, **report before/after both** (ROADMAP protocol) | Curve-set ID in every header; analysis pooling guard on |
| 5 (Sep 1–7) | **Tier 2 LHS N ≥ 4,000**; interim analysis — do Tier 2 interactions invalidate Tier 1 marginals (D-021's failure mode → recorded DOE revision)? Watch IS8-17 dominance (D-027 T5-promotion trigger; P-06 Whitney becomes load-bearing) | Trial count tracking to ≥10,000 |
| 6 (Sep 8–14) | Complete ≥10,000 incl. post-swap re-runs; **Tier 3 replay artifacts** (≥1 per failure class + ≥1 success); #63 windows; **gate evaluated against `gate_moderate.json`** | The kill-gate number exists |
| 7–8 (Sep 15–28) | **Reserved: the 30–60% iterate branch ("two weeks, re-run")**. If >60% first pass: analysis depth, REPORT drafting, CLAIMS rows | — |
| Sep 29–30 | Final `sim/REPORT.md` (ARCH §6.1–6.7), dataset audit, ROADMAP/CLAIMS updates | Phase 1 closes on schedule |

## 6. Risks / watch-items

1. **Newton 1.0 maturity** — per-contact-point reporting and determinism unverified;
   both adapters built together, day-one gate, fallback costs zero rework.
2. **GPU nondeterminism vs the replay contract** — determinism is a provisioning
   criterion recorded with A-004, not a week-5 discovery.
3. **Throughput unknown until A-004** — runner meters spend against the $100 ceiling;
   projected overrun forces a recorded amendment (P-02), never a silent quality cut.
4. **Curve-swap discipline** — the exact ROADMAP-named failure; enforced mechanically
   (header stamping + analysis pooling guard + tagged pre-swap dataset).
5. **Classifier precedence** — overlapping signatures (lip strike → jam → budget
   exhaustion) need a documented order with a test per pair; novel patterns raise for
   recorded amendment.
6. **Week-one overload** — three obligations in seven days; A-004 scoped to the
   contact pipeline (honest per ARCH §5), kinematic stage off the critical path.
7. **Retry × time-budget cost interaction** — cap per-trial wall time; log `t_total`
   vs T so runaway trials surface in the manifest, not the bill.
8. **Local ceiling** — 16 GB, no CUDA: full suite must stay runnable locally on MuJoCo
   (small-N smoke sweep); development never requires the provisioned instance.

## 7. Exit criteria

≥10,000 committed trials; ARCH §6.1–6.7 outputs present; gate number computed only
against the pre-committed `gate_moderate.json` (D-029); every REPORT claim traceable
to a committed file; CLAIMS rows landed with the replay artifacts (A-007). The three
load-bearing tests — golden-fixture round-trip, same-seed byte-identical trial, #63
pinned cross-check — pass before any DOE run is committed.
