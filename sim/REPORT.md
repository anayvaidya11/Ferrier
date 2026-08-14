# Phase 1 Report — The Docking Experiment (T13)

> **STATUS: DRAFT, PRE-SWAP.** Every number in this document was produced
> on the `prior_v1` **stand-in perception curves** (swept, literature-
> anchored where the corpus allows — the C-14 sanctioned phrasing; no
> "literature-derived curve" is claimed). The final gate evaluation
> happens only after the P-03 measurement window replaces the stand-ins
> with `mr_v1` bench data; both before/after numbers will be reported
> (ROADMAP curve-swap protocol). Sections that can only be written then
> are marked **[MR_V1 PENDING]**. Drafted 2026-08-14 against the frozen
> dataset `results/freeze_prior_v2/` (code `f6325bd`, 13,900 trials).
> *(History note preserved from the stub, R01 F-001: an earlier stub line
> "No simulation exists yet" predated the build and had become a false
> repo statement — corrected 2026-08-11. This draft is dated and
> commit-pinned so it cannot rot the same way.)*

Label discipline (MASTER_CONTEXT §4.3): **simulated** results throughout,
produced by real, tested harness code; inputs labeled per §9 below.

---

## 0. The experiment

**One question, one number:** given a standardized target interface, what
fraction of autonomous approach-and-latch attempts succeed under
realistic field degradation?

**The gate** (MASTER_CONTEXT Phase 1): success rate over the pre-committed
"moderate degradation" cell — defined numerically *before any trial ran*
(D-029, transcribed verbatim to `scenarios/gate_moderate.json`) at
N = 5,000 (D-038). >60% → Phase 2; 30–60% → iterate two weeks; <30% →
stop and revisit the wedge.

**Design, in one paragraph.** Two-stage simulation (D-006): approach and
acquisition in a cheap closed-loop kinematic stage (holds physically stop
the vehicle, D-037), full contact physics only on the last 50 mm and only
on the 160 mm annulus — near-misses score as misses (`clean_miss`,
D-030). Perception is an injected stochastic model (D-007; no renderer
exists), parameterized by INTERFACE_SPEC §9 axes and the curve-swap seam
(D-008-R). Contact model is the ratified T1 (D-027): rigid funnel + stud,
one 6-DOF spring-damper at the base + hard stops. Engine of record:
MuJoCo 3.11.0 (D-039). Three-tier DOE (D-021/D-032): one-axis marginals,
Tier-2 LHS over all axes jointly, and the D-029 gate cell. Every trial
writes one WIRE_FORMAT NDJSON record, replayable bit-identically from its
header within an instance class (F-018).

**Three acts to the frozen dataset:**

1. **freeze_prior_v1** (2026-08-09, 13,400 trials at `b493e7a`) — first
   full run after H-18's three composition bugs were found by probe and
   closed as human-ratified decisions (D-034/035/036: persistence
   semantics for dark windows, commit-scoped confidence, ring-absence
   time windows). Gate cell 0.0% (N = 5,000, CI [0, 0.08%]), all policy
   refusals.
2. **R01 surgical review + P-08** (2026-08-11) — 225/225 contract clauses
   verdicted by 16 agents with adversarial prosecution; 24 findings
   survived, 0 rejected; 8 behavioral, ratified in one sitting as
   D-039..D-046. Highest-impact: F-012 — every v1 trial viewed the
   target inverted (Ry(180°) for Rz(180°)).
3. **freeze_prior_v2** (2026-08-12, 13,900 trials at `f6325bd`,
   c7i.8xlarge, $0.132 metered) — the batched fix set re-run. The fixes
   are visible in composition (v1 Tier-1 carried 17 attempt-seam IS8-3
   artifacts; v2 carries none; ambiguity refusals now exist because
   D-043 made flip realism real) — and the verdict is unchanged.

**Headline pre-swap numbers** (`results/freeze_prior_v2/freeze_summary.json`):

| Dataset | N | Success | 95% CI (Wilson) | Census |
|---|---|---|---|---|
| Tier 1 (98 marginal cells) | 4,900 | **88.0%** | [87.1%, 88.9%] | 4,313 success · 537 IS8-1 · 50 IS8-2 |
| Tier 2 (LHS, joint) | 4,000 | **0.98%** | [0.71%, 1.33%] | 2,064 IS8-2 · 1,897 IS8-1 · 39 success |
| **Gate cell (D-029)** | 5,000 | **0.0%** | [0%, 0.077%] | 4,964 IS8-1 · 36 IS8-5 |

---

## 1. The sensitivity curves (ARCH §6.1 — D-014)

The headline output is deliberately **success as a function of each
degradation axis**, not a single rate — it survives uncertainty in the
perception stand-ins because it does not depend on any single perception
value being correct. 25 axes, one figure each, per-point Wilson CIs, in
[`results/freeze_prior_v2/figures/`](results/freeze_prior_v2/figures/)
with the numeric per-point data committed beside them
(`figures/index.json`, R01 S-08).

Load-bearing readings (each cell N = 50, all other axes nominal):

- **Outer-tag occlusion**
  ([figure](results/freeze_prior_v2/figures/d014_outer_occlusion.png)) —
  benign through 30% (0.88), **cliff at 40% (0.02), zero beyond**. This
  is the axis the whole D-029 gate band hangs on, and it is built on the
  D-023 mud model: an **extrapolation with no supporting data** until
  MR-001. The gate number inherits exactly this cliff's position.
- **Inner-ring occlusion**
  ([figure](results/freeze_prior_v2/figures/d014_inner_occlusion.png)) —
  holds through 50%, half-success at 60%, dead by 70–90% (ring
  starvation: the ≥2-fused-tag commit rule, D-011, becomes
  unsatisfiable). The ring sits at the mud line; see the taxonomy
  reading, §2.
- **Sensor dropout**
  ([figure](results/freeze_prior_v2/figures/d014_dropout_p.png)) —
  benign through p = 0.1, 0.68 at 0.2, 0.24 at 0.3. Fraction-of-a-second
  blips no longer kill missions (D-034's persistence window); sustained
  starvation honestly does.
- **Illuminance**
  ([figure](results/freeze_prior_v2/figures/d014_illuminance_lux.png)) —
  1.0 at 5 lux and above, **0.0 at 1–2 lux**: a hard cliff sitting
  squarely in the sub-10-lux region the prior_v1 lux floor
  extrapolates (MR-002's territory; absolutes there will carry the
  non-transferable label even after measurement).
- **Host attitude**
  ([pitch](results/freeze_prior_v2/figures/d014_host_pitch_deg.png) ·
  [roll](results/freeze_prior_v2/figures/d014_host_roll_deg.png)) —
  0.94–1.0 across the full ±20° envelope (D-024). These axes exist in
  the data because H-17/D-046(b) realized host tilt through
  truth/sightings/handoff/contact; they were silently absent before R01.
- **Compliance stiffness k**
  ([figure](results/freeze_prior_v2/figures/d014_stiffness_k_n_mm.png))
  — flat 1.0 across the {1..70} N/mm grid at nominal: capture is not
  stiffness-limited in clean conditions; stiffness earns its keep in §7's
  feasibility windows.

Marginal flatness is evidence about the *nominal* neighborhood only; the
Tier-2 joint sample is where interactions show, and its refusal-dominated
0.98% says degradations compound hard.

## 2. The failure taxonomy, measured (ARCH §6.2)

Every failed trial classifies against exactly one INTERFACE_SPEC §8 row
via the committed precedence order
([`FAILURE_TAXONOMY.md`](../FAILURE_TAXONOMY.md), transcription-tested);
unclassifiable traces raise rather than guess. Distribution figure:
[failure_distribution.png](results/freeze_prior_v2/figures/failure_distribution.png).

**Measured vs a-priori.** The taxonomy's frequency column was an a-priori
guess, and its own header says the measured delta is a finding:

- **IS8-1 (outer degradation / policy refusal) dominates everything** —
  537 of 587 Tier-1 failures, 4,964 of 5,000 gate outcomes. Guessed
  "Common"; measured *the* failure mode of the pre-swap system.
- **IS8-3 (inner ring below 2 tags) went from "Common" (a-priori) to
  zero** in v2 Tier-1. The 17 IS8-3s in v1 were attempt-seam timer
  artifacts (R01 F-004), not ring physics — D-042 removed them. The
  honest ring-starvation signal now lives inside the inner-occlusion
  cliff (§1), which classifies as refusal before the ring row is
  reached.
- **IS8-5 (ambiguity) exists only because the fixes made it possible** —
  36 gate-cell refusals; v1 had structurally flip-immune lone tags
  (F-007/F-008) and could not produce them.
- **Contact-side rows (IS8-9/10/16/17/18) fired zero times** in the
  frozen DOE: pre-swap, trials that reach contact latch, and trials that
  don't reach contact refuse. IS8-17 (jam) never fired — see the #62
  semantics note (D-040): discrimination is carried by the persistence
  window, and the force cells stand as entry conditions. The wide probe
  (`results/probe62_wide.json`, 850 successful insertions across all 17
  contact-dynamics Tier-1 cells) quantifies that: **zero would-fires at
  every one of the 18 committed grid cells**; the longest sustained jam
  signature on any successful insertion was 0.255 s — 25.5% of the
  default 1.0 s window and half of even the tightest 0.5 s cell — while
  instantaneous contact transients exceed every force cell by orders of
  magnitude (p90 max-axial ≈ 35 kN), confirming D-040's reading with
  measured margin.

**Reading it the way a cofounder would** (the taxonomy's purpose under
D-014): the mechanical agenda (rows 3, 9, 10, 16) has *not yet been
reached* by the experiment — the perception agenda (rows 1, 5) gates
everything in front of it. Pre-swap, the machine's problem is not
latching; it is **earning the confidence to try** under mud and dark.
Whether that remains true on measured curves is exactly what the swap
decides.

## 3. First-attempt vs multi-attempt (ARCH §6.3 — D-005)

Reported separately, always (`figures/index.json → d005_splits`):

| Dataset | First-attempt | Overall (≤3 attempts, §9.1 default) |
|---|---|---|
| Tier 1 (pre-swap) | **86.73%** | **88.02%** |
| Gate cell (pre-swap) | 0% | 0% (no attempts authorized) |
| Tier 1 **[MR_V1 PENDING]** | — | — |
| Gate cell **[MR_V1 PENDING]** | — | — |

The retry loop (back out 300 mm, apply measured contact offset) converts
~1.3 points of Tier-1 first-attempt failures — modest at nominal, where
most failures are refusals retries cannot cure. `attempts_per_encounter`
is itself a swept axis
([figure](results/freeze_prior_v2/figures/d014_attempts_per_encounter.png)).

## 4. The reproducible dataset (ARCH §6.4)

The committed deliverable is the **regeneration closure**, not retained
record bulk (`results/freeze_prior_v2/MANIFEST.json`):

- Committed plans (`tiers.tier1_plan/tier2_plan/gate_plan` at sweep root
  20260808) + the D-032 seed rule + code SHA `f6325bd` + per-record
  sha256 lists (`tier1.sha256`, `tier2.sha256`, `gate.sha256`).
- Byte-identity is a **per-instance-class contract** (R01 F-018; measured
  cross-platform float divergence recorded in
  `results/review_r01/F-018/`): the freeze ran on c7i.8xlarge / Linux /
  Python 3.12.3, stamped with compute-instance identity in every
  `trial_header` (D-046(f)). Off-platform auditors verify trial-id
  reproduction; on-platform, full digests.
- Cost: **$0.132 for 13,900 trials** (`spend_ledger_v2.json`), metered
  against the P-02 $100 ceiling; regeneration at the committed A-004
  rate ($0.0095/1k) costs about the same.

## 5. Replayable trial artifacts (ARCH §6.5 — A-007)

Committed: [`results/tier3_prior_v2/`](results/tier3_prior_v2/) — one
artifact per class the v2 DOE produced (success, IS8-1, IS8-2, IS8-5;
contact-failure classes produced zero trials to replay), each rendered
from logged state only (D-007 untouched), labeled *simulated*, sidecars
carrying the F-024 trial-id regeneration recipe. The class-set delta vs
the v1 set is itself R01-fix evidence (IS8-3 artifacts gone with D-042;
IS8-5 possible only after D-043). Regenerator: `../tools/tier3_v2.py`.
The v1 set stays committed. **[MR_V1 PENDING]** — the post-swap set,
same driver, both kept. First CLAIMS rows land with these artifacts
(Appendix A).

## 6. The refusal/damage tradeoff (ARCH §6.6 — D-017)

The curve that prices the abort discipline: outcomes as
`conf_min_attempt` sweeps {0.50–0.95}
([figure](results/freeze_prior_v2/figures/d017_tradeoff.png), 7 points,
per-point Wilson CIs in `figures/index.json → d017_points`).

**Pre-swap reading, stated plainly:** over the marginal sweep — every
other axis at nominal — the curve is **flat**: success 1.0 and refusal
0.0 at every threshold including 0.95. At nominal, perception is clean
enough that the gate never bites; lowering the bar to 0.5 admits no
damage because there is nothing marginal to admit. The tradeoff earns
its keep under degradation: at the gate cell, fused commit confidence
clears the 0.85 default on ~0.5% of ring-fused frames (H-18 closure
evidence), which is why the gate census is 100% refusal. **The
decision-relevant D-017 curve — thresholds swept *inside* the degraded
band on measured curves — is a [MR_V1 PENDING] output**; pre-swap it
would only re-measure the stand-in cliff positions. No false captures
were produced anywhere in the frozen DOE (`false_capture_rate` 0.0 at
every threshold).

## 7. Required-stiffness band ∩ feasible windows (ARCH §6.7 — D-026/D-028)

Pre-swap, capture succeeds across the entire committed k grid at nominal
(§1), so the **simulated required band is the full grid [1, 70] N/mm at
the 0.60 threshold** — the sim does not constrain stiffness before the
swap; the *derived static ceilings* do the constraining
(`results/freeze_prior_v2/feasibility_63.json`, k_max = μ_trac·m_rv·g/35 mm):

| Class (μ_trac, m_rv) | k_max [N/mm] | Grid cells masked infeasible | Intersection |
|---|---|---|---|
| (0.2, 300 kg) | 16.8 | {30, 70} | [1, 16.8] |
| (0.2, 500 kg) | 28.0 | {30, 70} | [1, 28.0] |
| (0.35, 500 kg) | 49.1 | {70} | [1, 49.1] |
| (0.35, 800 kg) | 78.5 | none | [1, 70] |

Semantics per D-028: **intersection, not verdict** — a partial overlap is
a narrower usable band, never an elimination. Provenance label exactly:
*simulated required band ∩ derived static bounds* — not a pure simulation
result. CLAIMS C-13 caveat attached: the ceiling is static-only;
dynamic/snatch loads are unmodeled and Phase 2's dynamic analysis may
lower k_max, shrinking every window above.

## 8. The gate statement

**Pre-swap (prior_v1, labeled stand-in): 0 successes in 5,000 gate-cell
trials, Wilson CI [0%, 0.077%].** Census: 4,964 low-confidence refusals
(IS8-1) + 36 ambiguity refusals (IS8-5). Zero contact failures, zero
false captures, zero damage — under the moderate band the machine
declines to move steel it cannot see well enough, exactly as D-013
requires. First-attempt/multi-attempt: no attempts were authorized.

**What this number is and is not.** It is the honest output of committed
code on committed stand-in curves, frozen and regenerable. It is **not**
the kill-gate evaluation: the mud axis dominating the band is an
extrapolation MR-001 exists to replace, and the program's own protocol
(ROADMAP; D-029) evaluates the gate after the swap, reporting both
numbers. Taken at face value it would read "<30% — stop"; the committed
reading is **evaluation pending the one honest lever, the P-03
measurement window** (~3 human days; kit and one-command swap are staged
— `../research/mr_kit/`, `../studies/SWAP_REHEARSAL.md`).

**[MR_V1 PENDING]** — final gate evaluation block: mr_v1 gate rate + CI,
before/after per plan, D-029 knife-edge check (if MR data places a
detection cliff at a band edge, the gate is reported as a curve across
the band with the committed cell number alongside).

## 9. What is real in this result (labels)

| Input | Label | Exit |
|---|---|---|
| Harness, wire contract, gate/guidance logic, classifier | **Built** (real code, 591 tests) | — |
| Contact physics (T1 model, MuJoCo) | **Simulated** | Phase 2+ hardware |
| Chassis/approach kinematics | **Simulated** (D-019 error model, magnitudes swept) | Phase 2 platform data |
| Perception: detection vs occlusion/mud | **Swept stand-in; mud response EXTRAPOLATED, no supporting data** | **MR-001** |
| Perception: sub-10-lux | **Extrapolated trend** | **MR-002** (non-transferable absolutes) |
| Perception: flip rate | **Derived form (H08), κ swept** | **MR-003** (also selects D-011 layout) |
| Perception: σ_px | **Swept class value** | MR `reproj_rms_px` column |
| Camera parameters | **Assumed** (D-012) | Phase 3 hardware |
| Interface geometry | **Assumed** (D-016) | Phase 2 verifies |
| Traction ceilings (§7) | **Derived, static-only** | Phase 2 dynamic analysis |

## Appendix A — CLAIMS rows staged for T13 close (NOT yet in CLAIMS.md)

Landed only post-swap, with the replay artifacts (A-007); drafted here so
the close is mechanical:

1. *"Under the pre-committed moderate-degradation cell, the system
   refused every attempt rather than risk the asset (0/5,000, all policy
   refusals, zero damage)"* — evidence: freeze summary + this report §8;
   label: simulated, pre-swap stand-in curves; status at landing:
   EVIDENCED for the pre-swap claim as phrased, never quotable without
   the stand-in qualifier.
2. *"Docking success ~88% [87.1, 88.9] across clean/near-nominal
   conditions (Tier-1)"* — same labels and qualifier.
3. *"Failure taxonomy measured; refusal-dominated; contact rows
   unreached pre-swap"* — evidence: §2 + failure_distribution.
4. *"Every trial regenerable: plans + seed rule + code SHA + per-record
   hashes; $0.0095/1k trials measured"* — evidence: MANIFEST + A-004.
5. **[MR_V1 PENDING]** the gate-number claim itself.

## Appendix B — artifact index

- Frozen dataset: `results/freeze_prior_v2/` (summary, manifest, sha256
  lists, feasibility, spend ledger, 27 figures + `index.json` per-point
  data). Prior freeze kept as evidence: `results/freeze_prior_v1/`.
- Gate cell definition: `scenarios/gate_moderate.json` (D-029 verbatim).
- Swap machinery: `../tools/swap_mr_v1.py` (one command;
  rehearsed 2026-08-14 — `../studies/SWAP_REHEARSAL.md`;
  `results/swap_rehearsal/`, synthetic, labeled).
- Measurement kit: `../research/mr_kit/` (sheets, checklists, shopping
  list, `detect_frames.py`).
- Review provenance: `../studies/R01_PHASE1_REVIEW/` (225-row matrix,
  findings, probes); `results/review_r01/` (probe artifacts).
