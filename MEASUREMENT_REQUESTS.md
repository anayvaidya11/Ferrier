# Measurement Requests

The standing channel between analysis and the physical world, per `NO_HARDWARE.md` rev 2.
When a committed decision or spec statement depends on a number that cannot be honestly
derived or sourced, the analysis **files a request here and stops** — it never invents,
estimates, or plausibly interpolates. The human evaluates the request, purchases what the
three-question test permits, collects the data, and returns it in the stated format. Most
requests should die at the "why it cannot be derived or sourced" field; the protocol
exists to make measurement the last resort, not the first.

**Statuses:** OPEN / APPROVED / COLLECTED / REJECTED / BLOCKED / DEFERRED.
**Hard bound (ROADMAP.md):** total measurement effort is three working days of human
time. Requests that do not fit are deferred, not extended.

## Request template

Every entry carries:

- **ID and status**
- **The number needed** — a specific quantity with units, not a topic
- **What depends on it** — the D-xxx / REQ-xxx / spec section blocked, and what exactly cannot be written without it
- **Why it cannot be derived or sourced** — the derivation attempted, the literature searched, and why each fell short. Mandatory; a request that skips it is rejected.
- **Procedure** — enough detail that the human executes it with zero design decisions
- **Instruments required** — with the three-question test answered per item and an order-of-magnitude cost
- **Output format** — exact file, schema, units, so the data drops into the repo as committed data
- **If never collected** — the fallback value or assumption and the label it carries. Every request must survive rejection.

---

## MR-001 — AprilTag 36h11 detection rate vs. mud occlusion fraction — **OPEN**

**The number needed:** P(detection) for AprilTag 36h11 as a function of mud occlusion
fraction, in increments {0, 10, 20, 30, 40, 50, 60, 70}% of tag area, at both tag scales
(150 mm and 10 mm edge), at view angles {0°, 20°, 40°, 60°} spanning the approach cone,
at representative ranges (150 mm tag: 3 m, 1.5 m, 0.5 m; 10 mm tag: 300 mm, 200 mm,
100 mm). Dimensionless probability per condition, N ≥ 100 frames each.

**What depends on it:** D-008-R (the mud axis is the one published characterization does
not cover); `INTERFACE_SPEC.md` §9 (mud occlusion sweep range and distribution, inner
ring swept independently from outer); the Phase 1 degradation model's most-cited axis.
Without it the mud curve entering Phase 1 is an extrapolation from clean-occlusion
studies.

**Why it cannot be derived or sourced:** Derivation: the detector is an algorithmic
pipeline (adaptive threshold → segmentation → quad extraction → homography + decode);
it has no closed-form failure model, so P(detect) under contamination is not derivable.
Literature searched: Olson (ICRA 2011) and Wang & Olson (IROS 2016) characterize
detection vs. distance, angle, and lighting but not surface contamination; Krogius et
al. (IROS 2019) characterize layout flexibility and decode robustness; comparative
fiducial studies (e.g., Sagitov et al. 2017) test occlusion with clean synthetic masks
or hard occluders. Mud is adherent, textured, partial-transparency contamination — it
degrades local contrast and gradient structure across the whole tag rather than cleanly
masking modules, so quad extraction typically fails before bit decode. That is a
different failure mechanism from masking, and no published mud/soil-contamination curve
for AprilTag was found in Week 1 research or since.

**Procedure:** Print both tag scales (36h11, known IDs, matte paper, quiet zone per
spec) and mount flat on a rigid board. Board on one tripod; camera on a second at the
sweep geometry (range and angle per grid above, measured with a tape and protractor —
consumer precision is acceptable, this measures detection, not pose truth). Fixed
exposure; record ambient illuminance with a lux-meter app per condition. Apply a
soil-and-water mixture in visually estimated area increments; photograph the tag state
before each condition (the occlusion fraction is later estimated from these stills —
estimation method noted in the data file). N ≥ 100 frames per grid point, camera
untouched during capture. Run the reference C detector offline over each frame set.

**Instruments** (three-question test: 1 = decision depends on it, 2 = consumed by
experiment, 3 = discarded/repurposed after):
- Camera + lens (any manually-exposable consumer camera qualifies) — 1: yes (D-008-R);
  2: yes; 3: yes (repurposed). Cost: order $10²  (zero if an owned device serves)
- Tripods ×2 + clamps — yes/yes/yes. Order $10¹
- Printed tags, soil, water, board — consumables — yes/yes/yes. Order $10⁰–10¹

**Output format:** `research/data/mr001_mud_detection.csv`, one row per condition:
`tag_scale_mm, range_m, view_angle_deg, occlusion_frac_est, illuminance_lux, n_frames,
n_detected, detector_version, notes`. Raw frames archived under
`research/data/mr001_frames/` (or a linked archive if too large to commit). Occlusion
estimation method documented in a header comment.

**If never collected:** mud response stays **extrapolated** from clean-occlusion
literature, labeled exactly that per §4.3, and D-014's sensitivity-curve headline is the
mechanism that keeps Phase 1 honest despite it.

---

## MR-002 — Detection rate vs. illuminance below 10 lux — **OPEN**

**The number needed:** P(detection) for 36h11 at illuminance {50, 10, 5, 2, 1} lux,
both tag scales, frontal and 40° view, fixed exposure ceiling (shutter bounded at the
value the spec assumes for a moving platform, so the low-light penalty appears as
sensor noise, not as unbounded exposure time). N ≥ 100 frames per condition.

**What depends on it:** the sub-10-lux sweep axis named in MASTER_CONTEXT Phase 1
("23% below 10 lux without active illumination" is the style of claim the program
expects to make); `INTERFACE_SPEC.md` §9 illuminance axis; D-008-R.

**Why it cannot be derived or sourced:** Derivation: low-light failure couples detector
thresholds to sensor exposure, gain, and noise — camera-dependent, not derivable.
Literature: published AprilTag characterizations (Olson 2011; Wang & Olson 2016) vary
lighting qualitatively but do not publish calibrated sub-10-lux detection curves; what
exists covers office-to-outdoor illuminance. What the literature does cover: relative
degradation trends with reduced contrast. What it does not: absolute detection
probability at single-digit lux for a stated exposure bound. Because absolutes here are
instrument-specific, this measurement carries the **non-transferable** label from the
start and only its relative trend is carried forward.

**Procedure:** darkened room, single dimmable source, lux measured at the tag plane per
condition. Same rig as MR-001, clean tags. Sweep the illuminance grid at fixed exposure
ceiling; N ≥ 100 frames per point; detector offline as MR-001.

**Instruments:** shared with MR-001 (no additional purchase beyond a dimmable lamp —
yes/yes/yes, order $10¹).

**Output format:** `research/data/mr002_lowlux_detection.csv`: `tag_scale_mm,
view_angle_deg, illuminance_lux, exposure_ms, gain_setting, n_frames, n_detected,
detector_version, notes`.

**If never collected:** the low-light curve stays **literature-derived trend +
extrapolation below 10 lux**, labeled as such, and the active-illumination iteration
path in the Phase 1 gate table is the design response if the gate lands in the 30–60%
band.

---

## MR-003 — Detection and pose-flip rate vs. view angle, both candidate layouts — **OPEN** — highest-value entry

**The number needed:** for each candidate layout from D-011 — (a) coplanar cluster,
(b) inner ring raised on a collar (standoff swept, see procedure) — P(detection) and
**flip incidence** (fraction of frames in which the detector-plus-pose-estimator selects
the wrong branch of the two-solution planar ambiguity, judged against the known rig
geometry) as a function of view angle: {0°–10° in 2° steps} (the near-head-on region
where the flip is worst), then {15°–75° in 15° steps}. Both from an on-axis camera
position and an oblique one (~30° off-axis, standing in for Cam B). N ≥ 100 frames per
point.

**What this measures, precisely:** the wrong-solution *selection rate under real corner
noise and real optics*. It does not re-measure the two-solution geometric structure or
the ambiguity separation angle — those are derivable (Collins & Bartoli, IPPE) and any
version of this request that only reproduces the derivable geometry dies at the field
below. The purchase buys the noise behavior, nothing else.

**What depends on it:** D-011's layout selection rule — this request is what converts
the redundancy scheme from an assertion into a measurement; D-012's load-bearing claim
that Cam B's obliqueness breaks the ambiguity by construction; `INTERFACE_SPEC.md` §3
(which layout ships) and §8 (pose-ambiguity-flip failure mode detection means).

**Why it cannot be derived or sourced:** Derivation: the two-solution structure of
planar pose is analytic (Collins & Bartoli, IPPE, IJCV 2014), and the ambiguity
*separation* can be derived for ideal noise — that derivation is exactly the fallback
below. But the actual flip *rate* depends on corner-noise statistics under real optics,
which are not derivable. Literature: Kallwies et al. (ICRA 2020) measure pose accuracy
and flip mitigation for single planar tags; no published characterization exists for
multi-tag constellations with deliberate depth separation, and none compares coplanar
vs. collar layouts — the comparison is the whole question. Simulating it is circular
under D-007: the injected model's flip parameter would be assumed, and measuring it in
sim measures the assumption.

**Procedure:** print both layouts on rigid board; the collar variant is raised on a
**shop-bought spacer of arbitrary height — never machined or cut to a spec dimension**.
The spacer is the seam where this instrument could quietly become product geometry: a
spacer made to the spec standoff is an artifact and fails the three-question test.
Instead, **sweep at least two arbitrary shop-bought heights and record them**; the
selection analysis interpolates across the swept heights, and the shipped standoff is
set by that analysis, not by the rig. Protractor-set view angles; for each layout ×
spacer height × camera position × angle: N ≥ 100 frames, offline detection + pose
estimation with the reference implementation, flip judged against rig geometry (sign of
the recovered normal). Consumer angular precision (±2°) is acceptable — the deliverable
is a rate difference between layouts, not absolute pose truth.

**Instruments:** shared with MR-001; shop-bought spacers of arbitrary height (≥2) —
yes/yes/yes, order $10⁰.

**Output format:** `research/data/mr003_flip_rate.csv`: `layout {coplanar|collar},
collar_standoff_mm, cam_position {axial|oblique}, view_angle_deg, n_frames, n_detected,
n_flipped, detector_version, notes`.

**If never collected:** the layout is selected by the **derived** IPPE
ambiguity-separation analysis (as a function of collar standoff and camera obliquity),
labeled derived; the flip *rate* under degradation stays uncharacterized and
`INTERFACE_SPEC.md` §10 says so.

---

## Execution grids and time budget (added 2026-08-01 — makes each request executable with zero design decisions)

**MR-001 grid (trimmed to fit the time bound; trim recorded):** outer tag at
{3.0, 1.0} m × {0°, 20°, 40°, 60°}; inner tag at {0.30, 0.15} m × {0°, 20°, 40°} —
14 geometry setups × 8 mud levels (0–70%, 10% steps, applied cumulatively so the tag
is mudded once per level, geometry cycled within each level) = 112 conditions ×
N = 100 frames (~4 s at 30 fps each; repositioning dominates at ~4 min/setup).
Randomize geometry order within each mud level; photograph tag state before every
condition. **Estimated human time: 1.5 days.** (The full 768-condition grid from the
original filing would blow the 3-day bound; the trim drops redundant mid-range points,
not axes.)

**MR-002 grid:** {50, 10, 5, 2, 1} lux × both scales × {0°, 40°} at one range per
scale (1.0 m outer / 0.20 m inner), fixed exposure ceiling, N = 100 —
20 conditions, dark-room setup dominates. **Estimated human time: 0.5 day.**

**MR-003 grid:** 2 layouts (coplanar; collar) × 2 shop-bought spacer heights
(arbitrary, recorded — **never machined to a spec dimension**) × 2 camera positions
(axial; 30° oblique per D-025) × view angles {0°, 2°, 4°, 6°, 8°, 10°} ∪ {15°, 30°,
45°, 60°, 75°} × N = 100. Collar cells: 2 heights; coplanar cells: height n/a →
(1 + 2) × 2 × 11 = 66 conditions. Flip judged against rig geometry (recovered-normal
sign). **Estimated human time: 1.0 day.** Standing cautions restated: the spacer is
tripod-class furniture at arbitrary heights, and the request measures **wrong-branch
selection under real noise** — the two-solution geometry itself is derivable
(studies/H08) and is not what this purchase buys.

**Total: 3.0 days — exactly at the ROADMAP hard bound. Any overrun defers the
remaining cells, never extends the budget.** Data lands in the schemas already
specified per request; all three CSVs commit under `research/data/`.

**Schema addition (2026-08-02, from the H-07 finding):** all three CSVs additionally
carry a **`reproj_rms_px`** column — mean RMS corner reprojection residual per
condition, computed offline from the same frames. The literature corpus cannot anchor
corner noise (its only quantifying source is paywalled — `perception_prior.md`), so
this column is what replaces the swept σ_px class value in PHASE1_PARAMETERS #40. It
costs nothing at collection time and converts MR-001/002/003 into the covariance
measurement MR-004 deferred.

## MR-004 — Pose error covariance — **DEFERRED**

**The number needed:** 6-DoF pose error covariance for 36h11 vs. range and view angle.

**What depends on it:** `WIRE_FORMAT.md` pose-covariance field semantics; the injected
perception model's error magnitude.

**Why deferred rather than open:** honest covariance measurement requires
metrology-grade ground truth — a jig with repeatable, measured camera-to-tag placement —
which costs more in setup time than the cameras cost in dollars, and violates the
three-working-day bound on its own. Under D-014 the headline sensitivity axis is
**detection rate**, not pose error, so the program's exposure to this number is second
order.

**Fallback (in effect now):** PHASE1_PARAMETERS #40's swept corner-noise class value
σ_px ∈ {0.3, 0.5, 1.0} px propagated through the committed camera models, labeled
*swept class value; not measured, not literature-anchored*. Recorded here so the gap
is visible rather than forgotten. *(Repaired 2026-08-04 per D-031: the previous text
named "Kallwies et al. 2020 accuracy figures" as a usable fallback — contradicting
`perception_prior.md`'s UNAVAILABLE status — and Olson 2011, whose only
corner-accuracy statement is qualitative. Literature anchoring, if it lands, arrives
via `research/OA_SUBSTITUTION.md` §2 under the ROADMAP curve-swap protocol.)*
