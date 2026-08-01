# HOLES — Phase 0 Gate Self-Test Results

**Method (2026-08-01):** attempted to draft the complete Phase 1 simulation parameter
set — every constant, sweep range, distribution, threshold, and frame transform —
using only `INTERFACE_SPEC.md`, `ARCHITECTURE.md`, `WIRE_FORMAT.md` (plus the
committed `DECISIONS.md` and `MEASUREMENT_REQUESTS.md` they cite) and nothing else.
The probe draft is not committed; it was a probe. Every value that could not be filled
from the specs alone is a hole, listed here with the section that should have
contained it and the decision still required. **None are resolved by invented values**
(NO_HARDWARE rev 2 escalation rule; Week 2 prompt gate rule).

**Gate verdict is at the bottom, and it is plain.**

## Holes

| # | Missing value | Should live in | Decision required |
|---|---|---|---|
| H-01 | `attempts-per-encounter` default and sweep set (D-005 names the parameter, no value exists) | INTERFACE_SPEC §9 / ARCHITECTURE §6 | Pick default + sweep (e.g., {1, 2, 3, 5}) and record as a decision |
| H-02 | Approach speed profile: outer-servo speed, inner-servo creep speed, insertion speed, and the design closing velocity at the capture plane | INTERFACE_SPEC §6 | Set the three stage speeds + v_insert with rationale (chassis class, contact energy) |
| H-03 | Contact material parameters: friction (clean and mud-contaminated steel), restitution, contact stiffness/damping for the funnel-wall model | ARCHITECTURE §4 | Nominal + sweep ranges, sourced (Phase 2 literature) or declared sensitivity axes |
| H-04 | **Funnel compliance architecture** — D-001 says "compliant funnel"; nothing defines whether compliance is a mounted-spring stage or structural, in which DOFs, at what stiffness. The sim cannot model the crux mechanism without it. **Largest hole in the set.** | INTERFACE_SPEC §2 / §6 | Design decision: compliance topology + stiffness/damping ranges to sweep |
| H-05 | Chassis positioning error *model* (§5 allocates ±25 mm but not the form: bias vs. random walk vs. slip events, correlation time) | ARCHITECTURE §4 | Pick the error model and its parameters |
| H-06 | Perception frame rate and latency distribution for the injected model (WIRE_FORMAT carries the timestamps; no values set) | ARCHITECTURE §4 | Set rate (e.g., 30 Hz) + latency distribution, labeled assumed |
| H-07 | Numeric literature-derived detection curves — D-008-R's fallback tier names the sources; nobody has digitized the actual curves with figure-level citations | new: `research/data/perception_prior.md` | Extraction task (no hardware needed) — Phase 1 week-one work item |
| H-08 | Flip-probability-vs-angle injection values pre-MR-003 — the derived IPPE fallback analysis (D-011) has not actually been performed | `research/data/` + INTERFACE_SPEC §9 | Run the derived analysis, or hold the axis until MR-003 lands |
| H-09 | Latch success criterion in sim: what geometric/kinematic state counts as "latched" (head-center offset bound at throat depth, max closing v at confirm) | INTERFACE_SPEC §6 | Define the latch-confirm predicate |
| H-10 | Sweep design over §9's axes — full factorial is ~10⁷ cells; 10,000+ trials (MASTER_CONTEXT Phase 1) needs a sampling strategy (LHS, stratified, staged) | ARCHITECTURE §6 | Choose the DOE and its per-axis stratification |
| H-11 | Formal success definition + per-encounter time budget ("docking success" = latched within attempts budget within T seconds; T unset) | ARCHITECTURE §6 | Set T and ratify the success predicate |
| H-12 | Mud-extrapolation functional form pre-MR-001 (how the clean-mask literature curve is degraded to stand in for mud: scale, contrast-model, threshold shift) | INTERFACE_SPEC §9 | Pick the extrapolation form and label it — it is the number most likely to be wrong, per D-008-R |

## Placeholder values requiring ratification

These appear in the specs as **[ASSUMED]**-labeled values that trace to a decision's
*mechanism* but whose *magnitudes* were set editorially. They are disclosed here so
none ride into Phase 1 unratified (Week 2 prompt, verification item 6):

- `conf_min_attempt` = 0.85 (WIRE_FORMAT) — placeholder; Phase 1 sweeps it, but the
  default should be ratified or replaced.
- Annulus margin 25 mm beyond lip (INTERFACE_SPEC §6).
- Tolerance-budget allocations 15/25/3 mm and 3/6/1° (§5) — sweep centers.
- Obstruction cone Ø270 × 400 mm; mounting height 400–800 mm; host attitude ±20° (§7).
- Off-axis tow limit ±20° (§2.1) — Phase 2 owns the real number; flagged in §10.
- Camera extrinsics in §4 (D-012 covers the sensors; the mounting offsets are
  editorial).

## Gate verdict

**No — Phase 0 does not pass yet.** The gate requires that Phase 1 build against the
specs with **no further design decisions**; twelve holes and six unratified
placeholders remain. Honest status of each class: H-01, H-02, H-05, H-06, H-09, H-10,
H-11, H-12 are one-session decisions; H-07 and H-08 are small derivation/extraction
tasks doable without hardware; H-03 is a sourcing task; **H-04 (funnel compliance) is
a genuine design decision and the critical path** — it defines the crux mechanism the
whole experiment measures. The gate window runs to Aug 14; a single decisions session
closing H-01–H-12, plus committing the two derivation artifacts, closes the gate.
A hole honestly reported closes the gate *correctly*; these are reported, not filled.
