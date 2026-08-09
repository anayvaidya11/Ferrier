# HOLES — Phase 0 Gate Ledger

Updated 2026-08-08 (H-17 opened during T10 — host attitude unrealized; previously
2026-08-02: H-04/H-07 closures; D-028 reconciliation; post-assessment holes
H-13..H-16). Four sanctioned doors: **DERIVED** (Door 1),
**SOURCED** (Door 2), **DECIDED** (Door 3, promoted to a D-xxx), **SWEPT** (Door 4,
declared Phase 1 parameter with range + arbitrary-labeled default). No fifth door;
nothing below was closed by invention.

## Closed

| # | Hole | Door | Resolution lives at |
|---|---|---|---|
| H-01 | attempts-per-encounter | 4 SWEPT | INTERFACE_SPEC §9.1 ({1,2,3,5}, default 3 arbitrary) |
| H-02 | Approach/insertion speed profile | 4 SWEPT | §9.1 (three stage speeds; insertion ceiling tied to D-020; coupling to H-04 noted) |
| H-03 | Contact μ, e | 4 SWEPT | §9.1 (μ 0.1–0.8, e 0.1–0.4 — contamination state spans the range; sweeping IS the honest treatment). Solver stiffness/damping: 3 DECIDED — numerical artifacts set by the recorded convergence procedure in PHASE1_PARAMETERS §Contact, logged per-run in `trial_header` |
| H-05 | Chassis error model | 3 DECIDED (form, D-019) + magnitudes swept ×{0.5,1,2} | DECISIONS D-019; §9.1 |
| H-06 | Perception rate/latency | 4 SWEPT | §9.1 ({10,30,60} Hz; {10,30,100} ms; class-value defaults labeled) |
| H-08 | Flip injection pre-MR-003 | 1 DERIVED | studies/H08_AMBIGUITY_MODEL.md — discriminability scaling, collar observability bound (h_c ≥ ~8 mm), interim model with its one shape parameter κ declared swept in §9.1. Residual: MR-003 validates. **Consequence propagated: single-tag orientation caveat (D-011 qualification); insertion requires ≥2 fused tags (WIRE_FORMAT)** |
| H-09 | Latch predicate | 3 DECIDED | D-020 |
| H-10 | Sweep design | 3 DECIDED | D-021 (3-tier DOE, ≥10k trials) |
| H-11 | Success definition + T | 3 DECIDED (predicate, D-022) + T swept | D-022; §9.1 |
| H-12 | Mud extrapolation form | 3 DECIDED (form, D-023) + f_c swept | D-023; §9.1 |

**Former ratification placeholders:**

| Item | Door | Resolution |
|---|---|---|
| conf_min_attempt = 0.85 | 4 SWEPT | D-017 — reclassified per Part B: the sweep's refusal-vs-damage tradeoff curve is a Phase 1 deliverable (ARCHITECTURE §6.6) |
| Tow-angle limit ±20° | 3 DECIDED (on a shown derivation) | D-018 normative sector; D-003-R split; Phase 2 verifies incl. dynamic loads |
| Annulus margin | 1 DERIVED | INTERFACE_SPEC §6 — 160 mm from lip band + head radius + drift + reserve; too-small hides lip strikes (incl. the false-capture path) |
| Tolerance-budget allocations | 4 SWEPT | §5 — declared sweep centers, ×{0.5,1,2} via D-019 |
| Obstruction cone / stud height / host attitude | 3 DECIDED | D-024 — requirements WyZantium levies on integrators; renegotiated when platform data exists |
| Camera extrinsics (Cam B obliquity) | 3 DECIDED (bounds derived) | D-025 — β = 30°, band [15°, 45°] from studies/H08 §5; translations stay [ASSUMED] within band |

## Open (and recently closed from this list)

| # | Hole | Status | What closes it |
|---|---|---|---|
| H-17 | **Host pitch/roll are swept axes (IS §9, D-024 attitude envelope, D-029 marginalization) but realized nowhere in the harness** — the sweep_point carries them, the kinematic/contact stages ignore them (recorded in `trial_logger.py`'s docstring since T8; surfaced as a hole at T10, 2026-08-08). D-032 excludes them from Tier-1/Tier-2 rather than emitting fake-flat curves; the D-029 gate's "marginalize over their full committed distributions" is currently a no-op | **OPEN** | Realize host attitude in the harness (target-frame tilt through kinematic truth, sightings, and the contact model), then add their grids/domains by recorded revision — or a recorded D-029 revision re-scoping the gate's marginalization claim |
| H-18 | **Outer-stage approach gating reuses the D-017 commit threshold, structurally refusing the whole D-029 moderate band** — `guidance/machine.py` realizes IS §8 row 1 as: hold whenever conf < conf_min (default 0.85) at *any* stage, escalate `low_confidence` after 5 s. But `inject.py`'s evidence-mass confidence for the single outer tag is numerically capped at that tag's per-frame p_detect — ≈0.44 at 30% occlusion (D-023 mud factor), below 0.85 whenever occlusion ≳ 0.1 — so every moderate-band trial dies IS8-1/IS8-2 before contact physics runs. Probe evidence: `sim/results/probe33_gate/conv33.json` (0.0 success, 500 trials × 2 timesteps, vs 1.0 nominal; outcome census 139× IS8-1, 61× IS8-2 per 200 records). D-013/#30 tie conf_min to the *commit* predicate (inner_servo ∧ multi_tag_fused); reusing it for outer-stage approach-holds is code-level glue — the same composition class as the two T8 findings flagged in `machine.py`'s own comments. Found 2026-08-09, first provisioned probe session. *Evidence update (same day, Tier-1 marginals, 4,400 trials, `sim/results/tier1_prior_v1_summary.json`): the conf-cap attribution above was WRONG for single axes — outer_occlusion alone is benign to 0.7 (detected-frame confidence clears the threshold and resets the row-1 hold timer). The gate-cell zero decomposes as: (1) **dominant — IS §8 row 2 realized per-frame with no persistence** (`machine.py` ~line 176, POLICY_CLOSE_WITHOUT_OUTER=False): the first #43 dropout frame (Bernoulli 0.05 burst starts, geometric mean-5 ≈ 0.17 s blips at 30 Hz) escalates IS8-1 within seconds; row 2 is the only §8 row that never received the T8 persistence treatment (rows 1/3/4/5 all hold/streak for exactly this reason); dropout_p = 0.05 alone → 0/50. (2) inner_occlusion ≥ 0.3 → ring starvation (0.10 → 0.00 success, IS8-3/IS8-1). Lux benign at 5+; rain/contamination bite only at their sweep extremes; the conf_min sweep behaves per D-017 (0.5 admits IS8-4 damage — the tradeoff working)* | **CLOSED 2026-08-09 — Door 3 (DECIDED ×3): D-034 (row-2 dark window), D-035 (conf_min commit-scoped), D-036 (ring absence as time window)**, each human-ratified in-session with before/after probe artifacts committed. All three were the same composition disease: per-frame or frame-count readings of §8 rows against stochastic 30 Hz detection. Residual behavior ratified as the honest machine: at the gate cell, fused commit confidence clears the 0.85 default on 0.5% of ring-fused frames (vs 33.9% nominal), so moderate-band trials end overwhelmingly in *refusal* — measured, not patched, per D-017 (the threshold sweep is the deliverable). Post-fix evidence: `sim/results/tier1_prior_v1_summary.json` (dropout cells pass; inner_occlusion 0.3/0.4 → 0.28/0.00), `tier2_prior_v1_summary.json` (LHS success 0.0045, refusal-dominated), `probe33_gate/conv33.json` | — |
| H-04 | Funnel compliance architecture | **CLOSED 2026-08-02 — Door 3 (DECIDED): D-027, T1 ratified by the human** (studies/H04, header + Addendum). Stiffness/mass swept per D-026 with the A1 feasibility mask; revised R4 and the IS8-17 jam class landed with the ratification | — |
| H-07 | Literature perception curves | **CLOSED 2026-08-02 — Door 2** (`research/data/perception_prior.md`: Olson 2011, Wang & Olson 2016, Krogius 2019 fetched and page-verified; 34 extraction rows, text/table-sourced only; a fabricated fetch summary was caught and discarded). Kallwies 2020 UNAVAILABLE (P-07; settled negative per D-031). Regions the corpus honestly cannot anchor (view-angle shape, covariance magnitudes) exited as declared sweeps in #39/#40 — Door 4 residuals, replaced by MR bench data. *2026-08-04, D-031 Stage B: Paper 5 (Adámek 2023) page-verified and added as the covariance model's FORM anchor; magnitudes stay swept/MR* | — |

## Post-assessment holes (found 2026-08-02, Phase 1 planning session)

The gate self-assessment passed, and a Phase 1 planning pass then found four more.
Recorded here as holes — not silently patched — and closed through the same doors.

| # | Hole | Door | Resolution lives at |
|---|---|---|---|
| H-13 | **"Moderate degradation" — the kill-gate criterion itself — was never defined numerically anywhere in the repo.** Undefined, the gate cell could be chosen after seeing results (refitting) | 3 DECIDED | D-029; transcribed verbatim to `sim/scenarios/gate_moderate.json` before the first DOE run |
| H-14 | `clean_miss` outcome had no committed definition — only §8 row 16's negative constraint ("never scored as capture or clean miss") | 3 DECIDED | D-030 (four-condition predicate; refusal path excluded) |
| H-15 | PHASE1_PARAMETERS #57 omitted IS8-17 (added by D-027 but never propagated); INTERFACE_SPEC §8 row 3 said "< 1 inner tag" against the ≥2-tag commit rule | consistency repair — applies committed D-027 / D-011, no new decision | #57 revised in place; IS §8 row 3 corrected |
| H-16 | `trial_result` had no field for §8 row 16's mandated false-capture sub-path count; #63's required-band citation pointed at the wrong §6 item | 3 DECIDED (additive schema revision) | WIRE_FORMAT `trial_result.false_capture` (optional, v1 additive); ARCHITECTURE §6.7 |

**Open count: 1** (H-17, found 2026-08-08 during T10 — a build-phase hole, not a
Phase 0 gate condition; H-18, found and closed 2026-08-09 through D-034/035/036; the gate's sixteen holes and every ratification placeholder
exited through a sanctioned door — twelve from the original ledger, four found
post-assessment (a passed self-assessment is evidence, not immunity).
`PHASE1_PARAMETERS.md` reads 65/65 (post-D-028). The gate's technical condition is
met; formal sign-off was PENDING_HUMAN P-05 (done).
