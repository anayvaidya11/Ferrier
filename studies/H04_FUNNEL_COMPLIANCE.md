# H-04 — Funnel Compliance Architecture: Tradeoff Study

# **RATIFIED 2026-08-02 — T1, per D-027 (PENDING_HUMAN P-01).** The body below is the record of how the decision was made; its caveats and unfetched-prior-art disclosure stand as written. Post-ratification refinements are in the Addendum only.

D-001 asserted a compliant funnel; no committed document defines where the compliance
lives, in which degrees of freedom, or at what stiffness. This omission is load-bearing
in more directions than anything else in the spec: the compliance *is* the tolerance
budget's absorber (D-015), it determines whether contact-force guidance can recover
lateral error direction at all (D-004 stage 3), it sets the contact model Phase 1 must
resolve (D-006, D-007), and it decides whether the handoff state vector is well-posed.
This study informs the decision; it does not make it.

## 1. Requirements the compliance must satisfy (cited)

| # | Requirement | Source |
|---|---|---|
| R1 | Absorb ±35 mm / ±10° at the capture plane | D-015; INTERFACE_SPEC §5 |
| R2 | Produce a wall-reaction force whose **direction** is recoverable — it is the stage-3 guidance signal | D-004 |
| R3 | Survive repeated contact across the retry loop | D-005 |
| R4 | *(revised at ratification, D-027 — original text was wrong for angled tow)* **Carries no axial tow load; reacts lateral and moment components within the D-018 tow-angle envelope.** Under angled tow the stud bears laterally on the throat rim, which reacts into the compliant base — the mount sees tow-class loads, not only capture impacts | D-003-R, D-018, D-027 |
| R5 | Tolerate debris/mud ingress on the head side | D-001 rationale |
| R6 | **Simulatability** — honestly modelable in Newton/MuJoCo at the fidelity stage 3 consumes; a topology that cannot be simulated credibly is disqualified regardless of merit (unfalsifiable number = §2.2 failure) | §2.2, D-007 |

## 2. Candidate topologies

**T1 — Rigid steel funnel on a compliant base mount.** All compliance concentrated at
one 6-DOF elastomer/spring-cartridge interface between funnel and head structure; hard
stops bound travel. Funnel itself is dumb, washable steel.

**T2 — Compliant funnel wall, rigid mount.** The cone itself deflects (elastomer-lined
or segmented petals).

**T3 — Staged stiffness.** Soft elastomer outer lip for first contact, stiffening
toward a rigid steel throat; rigid mount.

**T4 — Series-elastic instrumented mount.** T1's topology with measured deflection
(spring + displacement sensing); passive variant T4a, actively backdriven variant T4b
where compliance is controlled impedance.

**T5 — Remote-center-compliance (RCC) mount.** Classic peg-in-hole assembly solution
(Whitney's RCC): compliance arranged so the effective compliance center projects to
the throat, converting contact moments into corrective translation — the anti-jamming
geometry. Prior art: RCC devices in robotic assembly; spacecraft soft-capture rings
(NASA/IDSS low-impact docking = actively controlled T4b-class); automated
fifth-wheel/trailer couplers (rigid funnels, compliance from vehicle suspension —
evidence that pure T1-class works at vehicle scale). *(Prior-art families named from
general engineering knowledge — no specific document was fetched for this study; a
literature pass is a cheap Phase 1 week-one add.)*

## 3. Evaluation

| Criterion | T1 rigid+base | T2 compliant wall | T3 staged | T4 series-elastic | T5 RCC |
|---|---|---|---|---|---|
| Tolerance absorbed (R1) | Good — travel sized at mount | Good | Good | Good | Good |
| Force-direction signal (R2) | **Good** — one interface, net wrench clean | Poor — distributed deformation smears direction | Fair — lip events ambiguous | **Best** — deflection directly measured | Good — but moment→translation coupling complicates readout |
| Contact-model complexity (R6) | **Low** — rigid bodies + one 6-DOF spring | **High — deformable contact; not credible in Newton/MuJoCo at Phase 1 fidelity → disqualified by R6** | Med-high — soft layer needs fine contact resolution | Low — same as T1 + sensor model | Low-med — rigid bodies + specific spring topology |
| Debris sensitivity (R5) | Low — smooth steel, hose it off | High — soft surfaces trap grit; wear | Med — lip wear | Low (mechanism sealed at base) | Low-med |
| Overload behavior | Bottoms on hard stops — benign, designable | Tears/permanent set | Lip tears | Stops + sensor saturation — benign, observable | Stops; off-nominal loads can excite the RCC geometry |
| Retry endurance (R3) | High | Low-med | Med | High | High |
| Cofounder design burden | Low | Med | Med | Med-high | Med |

**T2 is disqualified on R6.** T3 survives but buys little that T1+geometry doesn't.

## 4. Stiffness envelope [derived; inputs labeled]

For the concentrated-compliance candidates (T1/T4/T5), lateral stiffness k must sit
between two bounds:

- **Lower bound — signal above noise (R2):** wall reaction at a working deflection
  must exceed the force-estimate noise floor n_F. **n_F is a missing input** — no
  force-sensing spec exists (component selection is Phase 2/3 scope). At a
  load-cell-class placeholder n_F ≈ 5 N [class value, labeled] and working deflection
  δ ≈ 5 mm: **k ≥ ~1 N/mm**.
- **Upper bound — quasi-static push capability:** the chassis must be able to drive
  the funnel through full envelope deflection: k ≤ F_avail / 35 mm. With
  F_avail ≈ μ·m·g ≈ 0.5 · 500 kg · 9.8 ≈ 2.45 kN [both factors class assumptions —
  recovery-vehicle mass and mud traction coefficient are unsourced]: **k ≤ ~70 N/mm**.
- Impact-force bound (dynamic): F_peak ≈ v·√(k·M_eff) at v_insert ≤ 0.15 m/s and
  M_eff ≈ 15 kg [class assumption] stays below the D-003-R structural numbers across
  the whole band — not binding.

**Envelope: k ∈ [~1, ~70] N/mm — two orders of magnitude wide because two inputs are
honest unknowns (n_F, F_avail).** Phase 1 sweeps k across this band (log grid); the
sensitivity of docking success to k is itself a Phase 1 finding the cofounder needs.
Neither unknown is a measurement-request candidate — both are component/vehicle
selection facts, Phase 2 scope — so they are named here and carried, not assumed away.

## 5. Recommendation — explicitly a recommendation, not a decision

**T1 (rigid funnel, compliant instrumented base), with T5's RCC geometry studied as a
refinement of the mount, and T4a's deflection sensing adopted if stage-3 direction
recovery proves marginal in early Phase 1 trials.** Reasoning: T1 maximizes R6
(simulatability) and R5 (debris), gives a clean single-interface wrench signal (R2),
and its failure behavior is benign and designable. It is also the only candidate whose
Phase 1 contact model is uncontroversial — rigid bodies plus one spring — which
protects the kill-gate number's falsifiability.
**What would change my mind:** Phase 1 showing lateral-error direction is not
recoverable from the net base wrench under realistic noise (→ T4a's measured
deflection), or the cofounder demonstrating jamming modes at the throat that RCC
geometry eliminates (→ T5).

## 6. Consequences of each candidate

| | Phase 1 contact model | Phase 4 CAD | Mechanical cofounder designs |
|---|---|---|---|
| T1 | Rigid bodies + 6-DOF spring-damper at base + hard stops | Funnel weldment, elastomer mount cartridge | Mount stiffness/travel, seal, **and a stop stack (or lockout) sized against D-003-R's structural load cases — not the insertion-impact bound — bottoming hard before the elastomer carries tow-class lateral load** (revised R4, D-027) |
| T3 | + soft contact layer at lip (fine mesh/substep cost) | + bonded lip | Lip material, bond, replacement scheme |
| T4a | T1 + deflection sensor model | + sensor integration | Sensing, calibration, sealing |
| T4b | Impedance-controlled joint (adds control loop to sim) | Actuated mount | Actuator, drive, control — largest scope |
| T5 | T1 with off-diagonal spring coupling | RCC linkage | RCC geometry tuning to throat position |

**Until ratified:** `INTERFACE_SPEC.md` §2.3 carries a placeholder pointing here;
`PHASE1_PARAMETERS.md` carries the compliance entries UNFILLED; the Phase 0 gate is
open on exactly this decision.

---

## Addendum (2026-08-02, post-ratification — D-027 required actions; body above unchanged)

**A1. Upper stiffness bound refined.** §4's F_avail used m = 500 kg, numerically
identical to D-003's *target*-vehicle mass — a carried-over number, not a chosen one.
Refinement: recovery-vehicle mass is its own class parameter, **swept independently
m_rv ∈ {300, 500, 800} kg** (any overlap with the target's 500 kg is coincidental),
and **μ swept 0.2–0.5** (0.5 alone is optimistic for mud). The ceiling becomes a
function, k_max = μ·m_rv·g / 35 mm:

| | μ = 0.2 | μ = 0.35 | μ = 0.5 |
|---|---|---|---|
| m_rv = 300 kg | **17 N/mm** | 29 | 42 |
| m_rv = 500 kg | 28 | 49 | 70 |
| m_rv = 800 kg | 45 | 79 | **112 N/mm** |

The band **narrows conditionally**: at the low-traction/light end the ceiling falls to
~17 N/mm, making the committed sweep's k = 30 and k = 70 cells infeasible for that
vehicle class — Phase 1 records a per-(μ, m_rv) feasibility mask rather than one
number.

**A2. Stiffness–stud coupling cross-checked.** Full-envelope deflection at the ceiling
puts F_lat = k·35 mm into the stud: 2.45 kN at 70 N/mm → 220 N·m at the 90 mm worst
arm; 3.92 kN at 112 N/mm → 353 N·m. Both sit **below** D-003-R(b)'s 462 N·m design
moment. **Verdict: the traction limit sets the k ceiling, not the stud's governing
load case** — the coupling is real but not binding anywhere in the refined band.
(Tow-class lateral through the mount — 5.13 kN at the D-018 ±20° sector edge — is the
stop stack's load case, per revised R4, and is Phase 2's verification item.)

**A4-note (2026-08-02): the §2 prior-art disclosure is discharged.** The literature
pass ran same-day (not deferred to Phase 1): all three families verified against
fetched sources — Draper RCC patent US 4,098,001 + Whitney 1982 (DOI-verified
metadata; full text paywalled), IDSS IDD Rev E + NASA SSP 50920 Rev A (both read in
full), JOST KKS + SAF-Holland XL-FW20034SL (both read). Whitney & Nevins 1979
unretrievable → demoted to unverified analogy. Citations live in INTERFACE_SPEC §2.3;
the §2 parenthetical above stands unedited as the record of what was true at
recommendation time.

**A3. Jam observability (D-027).** §5's T5 trigger ("jamming dominates the taxonomy")
was unobservable under T1's net-wrench signal — a symmetric wedge reads as high axial,
near-zero lateral, no latch: indistinguishable from "seated and latching." IS8-17
(jam detection: axial force above threshold ∧ lateral below threshold ∧ no latch
confirm) makes it observable; thresholds are declared sweeps in PHASE1_PARAMETERS.
T4a is blind to the same failure (near-zero net deflection) — recorded in D-027.
