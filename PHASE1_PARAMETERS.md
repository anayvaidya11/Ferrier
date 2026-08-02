# Phase 1 Simulation Parameter Set — the Gate Made Literal

Every constant, sweep, distribution, threshold, transform, and criterion Phase 1
needs, each citing the committed source it came from. **An entry that cannot be filled
from the specs points at its open hole instead of a value. When this document has no
UNFILLED entries, Phase 0 is done; until then it is the precise map of what remains.**
Status: 2026-08-02 (post-D-027) — **63 entries, 61 filled, 2 UNFILLED** (#39/#40
perception curves — H-07 extraction; the last items between this document and a
closed Phase 0 gate).

## Geometry (all from D-016 / INTERFACE_SPEC)

| # | Parameter | Value | Source |
|---|---|---|---|
| 1 | Stud neck diameter | 25 mm [ASSUMED] | D-016 |
| 2 | Stud head diameter | 40 mm [ASSUMED] | D-016 |
| 3 | Stud exposed length | 90 mm [ASSUMED] | D-016 |
| 4 | Funnel mouth diameter | 220 mm [derived] | IS §6 |
| 5 | Funnel throat diameter | 42 mm | D-016 |
| 6 | Funnel depth | 180 mm | D-016 |
| 7 | Funnel wall half-angle | ≈26° [derived] | IS §6 |
| 8 | Plate envelope | 200 × 200 mm | D-016 |
| 9 | Outer tag: size, center | 150 mm at (0, 0, +185) mm stud_frame | IS §3.2, §3.5 |
| 10 | Inner ring | 8 × 10 mm tags, r = 55 mm, 45° pitch | IS §3.3, §3.5 |
| 11 | Collar standoff h_c (layout L-B) | swept [10, 40] mm; observability floor ~8 mm [derived] | D-016; studies/H08 §3 |
| 12 | Funnel lip band | radial [110, 125] mm | IS §6 |
| 13 | Contact-physics annulus radius | 160 mm [derived] | IS §6 |
| 14 | Capture plane | head_frame YZ at x = 0 | IS §6 |
| 15 | Kinematic→contact handoff trigger | stud-head center at x = +50 mm | IS §6, D-006 |

## Frames and cameras

| # | Parameter | Value | Source |
|---|---|---|---|
| 16 | T_stud_plate | (0, 0, +185) mm, identity rotation | IS §4 |
| 17 | Cam A extrinsic | (−50, 0, +140) mm, boresight ∥ +X [ASSUMED] | IS §4, D-012 |
| 18 | Cam B extrinsic | (+100, −250, 0) mm, yaw 30° [translations ASSUMED; angle D-025, band 15–45°] | IS §4, D-025 |
| 19 | f_A (focal, px) | ≈1371 px [derived: 1920/(2·tan 35°)] | D-012 |
| 20 | f_B (focal, px) | ≈880 px [derived: 1920/(2·tan 47.5°)] | D-012 |

## Envelope and error budget

| # | Parameter | Value | Source |
|---|---|---|---|
| 21 | Capture envelope, position | ±35 mm [ASSUMED] | D-015 |
| 22 | Capture envelope, angle | ±10° [ASSUMED] | D-015 |
| 23 | Budget allocations (percep/chassis/mount) | 15/25/3 mm, 3/6/1° — sweep centers ×{0.5, 1, 2} | IS §5, D-019 |

## Guidance

| # | Parameter | Value | Source |
|---|---|---|---|
| 24 | Approach/tow sector | ±20° cone about stud +X, normative | D-018 |
| 25 | Stage boundaries | outer servo 3 m → 200 mm; inner servo 200 mm → contact | D-004 |
| 26 | Stage speeds | swept: 0.5–2.0 / 0.1–0.3 / 0.02–0.15 m/s (defaults 1.0/0.2/0.05, arbitrary) | IS §9.1 |
| 27 | attempts-per-encounter | {1, 2, 3, 5}, default 3 (arbitrary) | IS §9.1, D-005 |
| 28 | Retry back-out distance | 300 mm | D-005 |
| 29 | conf_min_attempt | swept {0.50–0.95}, default 0.85 (arbitrary); tradeoff curve is a deliverable | D-017 |
| 30 | Insertion commit rule | pose_source = multi_tag_fused (≥2 tags) ∧ stage = inner_servo ∧ conf ≥ threshold | WIRE_FORMAT; studies/H08 |

## Contact

| # | Parameter | Value | Source |
|---|---|---|---|
| 31 | Friction μ | swept 0.1–0.8, default 0.4 (arbitrary) | IS §9.1 |
| 32 | Restitution e | swept 0.1–0.4, default 0.2 (arbitrary) | IS §9.1 |
| 33 | Solver timestep/stiffness (numerical) | set by recorded convergence procedure: halve timestep until success-rate delta < 1% over a 500-trial probe; values logged per run in `trial_header` | HOLES H-03 |
| 34 | Compliance topology | **T1 — rigid steel funnel on compliant instrumented base; rigid bodies + one 6-DOF spring-damper + hard stops** (RATIFIED 2026-08-02) | D-027 |
| 35 | Compliance stiffness k | swept log grid {1, 3, 10, 30, 70} N/mm over the derived envelope; **Phase 1 outputs the required-stiffness band** | D-026; studies/H04 §4 |
| 36 | Head effective mass M_eff | swept {8, 15, 30} kg class range | D-026 |

## Perception injection (D-007, D-008-R)

| # | Parameter | Value | Source |
|---|---|---|---|
| 37 | Perception rate | {10, 30, 60} Hz, default 30 | IS §9.1 |
| 38 | Perception latency | {10, 30, 100} ms, default 30 | IS §9.1 |
| 39 | **Detection-probability curves P(range, angle, illuminance)** | **UNFILLED — H-07 extraction pending; MR-001/002 replace/refine** | — |
| 40 | **Pose covariance magnitudes** | **UNFILLED — H-07 extraction (literature); MR-004 DEFERRED** | — |
| 41 | Mud model | P_mask(f)·max(0, 1−f/f_c), f_c ∈ {0.6, 0.8, 1.0} | D-023 |
| 42 | Flip model | studies/H08 §4; κ ∈ {0.5, 1, 2} | studies/H08 |
| 43 | Dropout | Bernoulli p ∈ {0, .05, .1, .2, .3} + burst (geometric, mean 5) | IS §9 |
| 44 | Lens contamination (Cam B) | 0–50% aperture area | IS §9 |
| 45 | Rain proxy | contrast + droplet occlusion 0–30% | IS §9 |
| 46 | Partial destruction | per-tag knockout over sampled 2⁹ | IS §9 |
| 47 | Illuminance grid | {1, 2, 5, 10, 50, 100, 10³, 10⁴} lux | IS §9 |
| 48 | Occlusion grids | outer 0–70%, inner 0–90%, 10% steps, independent | IS §9 |

## Environment, DOE, outcomes, logging, compute

| # | Parameter | Value | Source |
|---|---|---|---|
| 49 | Host pitch/roll | ±20° uniform | IS §9, D-024 |
| 50 | DOE Tier 1 | one-factor marginal grids at nominal elsewhere | D-021 |
| 51 | DOE Tier 2 | LHS, N ≥ 4,000 joint | D-021 |
| 52 | DOE Tier 3 | failure-replay set (A-007 artifacts) | D-021 |
| 53 | Total trials | ≥ 10,000 | MASTER_CONTEXT Phase 1, D-021 |
| 54 | Latch predicate | 3 mm radial @ engagement depth, ≤0.1 m/s, 100 ms | D-020 |
| 55 | Encounter time budget T | {5, 15, 30} min, default 15 (arbitrary) | D-022 |
| 56 | Success definition | D-020 within attempts ∧ t ≤ T; first/multi-attempt reported separately | D-022, D-005 |
| 57 | Outcome classes | success \| IS8-1…IS8-16 \| clean_miss | IS §8; FAILURE_TAXONOMY.md |
| 58 | Trial record schema | header/state/result per WIRE_FORMAT | WIRE_FORMAT |
| 59 | sim_truth logging rate | every physics step post-handoff; every kinematic step pre-handoff | WIRE_FORMAT |
| 60 | Seed policy | single RNG root per trial in `trial_header`; all streams derive | WIRE_FORMAT |
| 61 | Compute decision test | 1,000-trial representative workload, cloud CPU vs GPU spot, $/1k trials, winner provisioned, both measurements committed | ARCHITECTURE §5, A-004 |
| 62 | Jam-detection thresholds (IS8-17) | swept, defaults arbitrary: F_ax_jam {50, 100, 200} N; F_lat_jam {10, 25} N; t_jam {0.5, 1, 2} s — recalibrated against simulated force scales in Phase 1 week one, as a recorded revision | IS §8 row 17, D-027 |
| 63 | k feasibility mask — **a reported finding, not bookkeeping** | ceiling k_max = μ·m_rv·g/35 mm per (μ, m_rv) cell (17–112 N/mm across classes). **Required Phase 1 report line:** intersect the required-stiffness band (deliverable 7) with each class's ceiling — wherever required-k exceeds k_max, report it as *"a recovery vehicle of class (m_rv, μ) cannot dock in that condition regardless of autonomy quality"* — a chassis-selection requirement consumed directly by Phase 2's tradeoff study | studies/H04 A1; ARCHITECTURE §6.7 |

**UNFILLED: #39, #40 (H-07 — one extraction session).** #34 filled by D-027
ratification (T1); #35/#36 are sweeps per D-026 with #63's feasibility mask; the
required-stiffness band is a Phase 1 deliverable, not a Phase 0 guess.
