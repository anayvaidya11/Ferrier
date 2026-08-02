# HOLES — Phase 0 Gate Ledger

Updated 2026-08-01 (hole-closure session). Four sanctioned doors: **DERIVED** (Door 1),
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
| Obstruction cone / stud height / host attitude | 3 DECIDED | D-024 — requirements WyZen levies on integrators; renegotiated when platform data exists |
| Camera extrinsics (Cam B obliquity) | 3 DECIDED (bounds derived) | D-025 — β = 30°, band [15°, 45°] from studies/H08 §5; translations stay [ASSUMED] within band |

## Open

| # | Hole | Status | What closes it |
|---|---|---|---|
| H-04 | Funnel compliance architecture | **OPEN — narrowed to topology only** (study complete, UNRATIFIED). Stiffness and head mass exited via Door 4 (D-026, 2026-08-02): swept, with the **required-stiffness band** now a Phase 1 deliverable | **Human ratifies a topology** (PENDING_HUMAN.md P-01) — the single remaining H-04 decision |
| H-07 | Literature perception curves, digitized | **OPEN — task specified, not performed** | A reading/extraction session: digitize detection-vs-range/angle/lighting curves and pose covariance from the named sources (Olson 2011; Wang & Olson 2016; Kallwies 2020) into `research/data/perception_prior.md` with figure-level citations. No hardware needed; Door 2 on completion. Estimated half a day. **Not closable by citation-from-memory — that is the Door 2 correctness failure** |

**Open count: 2.** Both have named closure paths; H-04's is a human decision, H-07's is
a bounded work session. The Phase 0 gate remains open on exactly these two plus the
resulting unfilled entries in `PHASE1_PARAMETERS.md`.
