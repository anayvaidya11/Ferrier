# WyZen Docking Interface Specification

**Status:** Phase 0 deliverable, v1.0, 2026-08-01. Every normative statement traces to a
REQ-xxx (`research/REQUIREMENTS.md`) or D-xxx (`DECISIONS.md`); untraceable statements
are holes and live in `HOLES.md`, not here. Labels per MASTER_CONTEXT §4.3.
All dimensions are the D-016 provisional set — **[ASSUMED], Phase 2 verifies** — unless
individually marked derived.

## 1. Scope and non-scope

**Covers:** the physical and perceptual interface for autonomous tow/recovery attachment
— the target-side stud-and-fiducial assembly, the head-side funnel/latch envelope it
mates with, coordinate frames, tolerance budget, capture-plane handoff, failure modes,
and the degradation axes Phase 1 parameterizes (REQ-003, D-001, D-004).

**Does not cover:** battery swap, electrical handshake, or charging. Battery swap is a
**labeled future variant of the same head with zero Phase 1 scope** — different
geometry plus an electrical handshake, and admitting it would double the Phase 1
problem. The MIL-STD-3078 white-space argument (`research/STANDARDS.md`) belongs in the
pitch and in `ARCHITECTURE.md` as a future direction, not here. The ID allocation
scheme (§3.4) reserves fiducial space for that variant so nothing here forecloses it.

## 2. Target-side assembly

The target vehicle carries the passive half: a machined stud and a fiducial plate. All
active mechanism (funnel, latch, cameras, illumination) lives on the WyZen head — mud
accumulates on the serviceable side (D-001).

### 2.1 The stud [ASSUMED dimensions per D-016]

- Geometry: hardened male capture stud, neck Ø25 mm, spherical-capped head Ø40 mm,
  exposed length 90 mm from plate front face, axis normal to the plate (D-001, D-016).
- Engagement: the latch engages **behind the head** — the 7.5 mm radial shoulder where
  head (Ø40) meets neck (Ø25). Under tow the load path is head shoulder → latch →
  head structure. The funnel carries zero tow load; tension would pull the stud
  straight out of the mouth. **The latch is the entire primary structure and a single
  point of failure** (D-003, stated per its consequence).
- Material class: through-hardened quenched-and-tempered alloy steel (4140 QT class),
  zinc-nickel surface treatment for corrosion [ASSUMED — Phase 2 selects].
- Load rating: **15 kN axial design** (≈10 kN mired-breakout for a 500 kg UGV × 1.5) —
  an assumption, unverified until Phase 2 (D-003).
- Off-axis load sensitivity [derived, shown]: at tow angle θ off the stud axis,
  transverse component 15 kN·sin θ bends the neck about the plate face (moment arm
  90 mm, section modulus πd³/32 = 1.53×10⁻⁶ m³). At θ = 20°: σ ≈ 5.13 kN × 0.09 m /
  1.53×10⁻⁶ ≈ 300 MPa — safety factor ≈ 2.2 against 4140 QT yield (~655 MPa). At
  θ = 30°: σ ≈ 440 MPa, SF ≈ 1.5. **Provisional off-axis tow limit: ±20° [ASSUMED].
  Bending, not shear, sizes the neck — Phase 2 must verify this, and the tow-angle
  limit becomes an operational constraint the resolver stage must respect** (flagged
  in §10 and HOLES.md).

### 2.2 The mounting boss (D-002)

- Bolts to the host's **existing lunette bolt pattern** and reacts into the same frame
  member the lunette loads — heritage is claimed through the mounting boss and load
  path **only**, never through mating geometry. The capture feature is a **stud** — not
  a lunette, not a pintle; no inherited qualification is claimed for the mating
  geometry (D-002).
- Per-unit cost class (qualitative): a machined pin and a plate — no moving parts,
  nothing to maintain, nothing to certify. §1.7's mitigation is adoption; **every gram
  of complexity added to the target side is thesis risk** (D-001 consequence).

## 3. Fiducial specification (D-010, D-011)

### 3.1 Family

AprilTag **36h11**, reference C implementation (D-010). 36h11 tag geometry: 6×6 data
modules inside a 1-module black border; stated tag dimension = black-border outer edge
(8×8 modules); a ≥1-module white quiet zone surrounds it.

### 3.2 Outer tag [D-016]

- Dimension: **150 mm** black-edge (module = 18.75 mm), printed matte, on the
  200 × 200 mm plate — quiet zone 25 mm ≥ 1 module ✓.
- Sizing arithmetic [derived]: Cam A spans 70° over 1920 px → 6.4×10⁻⁴ rad/px; robust
  decode floor ~20 px across the tag → 38 mm at 3 m on clean imagery; ×4 margin for
  mud, obliquity, motion blur, low light → 150 mm (D-011, D-012, REQ-004).
- Position: tag center at (0, 0, +185 mm) in `stud_frame` (§4) — plate bottom edge
  +85 mm above the stud axis, clear of the funnel envelope at full engagement (§6).

### 3.3 Inner ring [D-016]

- **8 tags × 10 mm** black-edge, centers on a 55 mm-radius circle about the stud axis,
  45° angular pitch, first tag at 12 o'clock (+Z), all tags upright (identical
  orientation; position alone distinguishes them).
- Readability [derived]: Cam B spans ~95° over 1920 px → 8.6×10⁻⁴ rad/px; a 10 mm tag
  subtends 39 px at 300 mm and 116 px at 100 mm — above the 20 px floor with ≥2×
  margin across the inner-servo range (D-004, D-012).
- The ring sits at the stud base — **the most mud- and impact-vulnerable point on the
  assembly**. Its occlusion axis is swept independently in Phase 1 (§9); if inner-ring
  survival dominates the failure taxonomy, that is a finding handed to the mechanical
  cofounder (D-014 consequence).

### 3.4 Candidate layouts and selection (D-011)

Two candidates, both fully defined by this section plus one parameter:

- **L-A coplanar:** ring in the plate front-face plane (standoff h = 0).
- **L-B collar:** ring raised on a collar, standoff **h_c ∈ [10, 40] mm** — a swept
  parameter, not a dimension. MR-003 measures flip rate at shop-bought spacer heights;
  the shipped h_c comes from the selection analysis and is **never fabricated to spec
  during this program** (NO_HARDWARE rev 2, D-011).

**Selection rule:** MR-003's measured wrong-solution rate across both layouts selects;
fallback if never collected: derived IPPE ambiguity-separation analysis, labeled
derived (D-011). Phase 1 builds against the winner only — the loser does not travel
into Phase 1 as a live alternative (D-011 scope consequence).

### 3.5 Tag ID → rigid transform table

Every tag ID maps to a fixed transform to `stud_frame`, so **any single visible tag
yields full 6-DoF pose** (D-011). Poses `T_stud_tag` (tag frame expressed in
stud_frame; tag frame: origin tag center, +Z out of tag face, +X tag-right, +Y tag-up):

| ID | Role | Center in stud_frame (x, y, z) mm | Orientation |
|---|---|---|---|
| 0 | Outer | (0, 0, +185) | +Z_tag ∥ +X_stud; +Y_tag ∥ +Z_stud |
| 1–8 | Inner ring, k = 1..8 | (h, 55·sin(45°·(k−1))·(−1)... see rule | as ID 0 |

Rule for IDs 1–8: center = (h, −55·sin α_k, +55·cos α_k) with α_k = 45°·(k−1) measured
clockwise from +Z viewed from the approach direction (+X looking at the plate); h = 0
(L-A) or h_c (L-B). All tag faces normal +X_stud, upright.

**ID allocation scheme:** family 36h11 (587 usable IDs) is allocated in blocks of 16
per interface variant: IDs 0–15 = variant 0, the base recovery plate (0 outer, 1–8
inner, 9–15 reserved); IDs 16–31 reserved for the battery-swap variant (§1); IDs 32+
unallocated. A decoded ID outside the expected variant block is a rejection, not a
pose (§8 row 14).

## 4. Coordinate frames

Notation: `T_A_B` is the pose of frame B expressed in frame A; p_A = T_A_B · p_B.
Rotations are unit quaternions (w, x, y, z). Every pose in `WIRE_FORMAT.md` names its
frame explicitly (WIRE_FORMAT consumer checklist enforces this).

| Frame | Origin | Axes |
|---|---|---|
| `stud_frame` | Intersection of stud axis with plate front face | +X along stud axis away from plate (toward approach); +Z toward outer tag ("plate up"); +Y = Z × X (right-handed) |
| `plate_frame` | Plate geometric center, front face | Parallel to stud_frame; T_stud_plate = translation (0, 0, +185 mm) [D-016] |
| `head_frame` | Funnel mouth center | +X along funnel axis **into** the funnel (insertion direction); +Z head-up; +Y = Z × X |
| `capture_plane_frame` | Alias of head_frame | The capture plane is head_frame's YZ plane (x = 0); named separately because §5 and §6 reference it |
| `cam_a_frame` | Cam A optical center | Camera convention: +Z optical axis, +X image-right, +Y image-down. Boresight ∥ head +X. Extrinsic T_head_camA = ((−50, 0, +140) mm, boresight-parallel) [ASSUMED, D-012] |
| `cam_b_frame` | Cam B optical center | Same convention. Mounted off-axis: T_head_camB = ((+100, −250, 0) mm, yawed +30° toward funnel axis) [ASSUMED, D-012 — obliqueness is load-bearing: Cam B is never head-on, breaking the coplanar flip by construction] |

At nominal full engagement, head +X and stud +X are anti-parallel (the head faces the
plate). The perception deliverable is `T_head_stud`; guidance consumes only that
transform and the frame declarations above.

## 5. Tolerance budget (D-015)

Referenced to the **capture plane**, not the latch: the funnel must swallow
**±35 mm positional, ±10° angular** error at the capture plane (D-015).

**Why latch tolerance is irrelevant to perception:** the latch needs the stud head
within ~±3 mm at the throat — an order of magnitude tighter — but by the time the stud
reaches the throat, position error has been mechanically collapsed by the funnel wall:
contact geometry, not vision, resolves the final millimeters (D-004 stage 3, D-001).
Perception only has to hit a 220 mm mouth; steel does the rest.

**Decomposition [allocations ASSUMED, arithmetic derived]:**

| Contributor | Allocation (position) | Allocation (angle) |
|---|---|---|
| Perception error at outer→inner handoff | ±15 mm | ±3° |
| Chassis positioning error (slip, compliance, control) | ±25 mm | ±6° |
| Target plate mounting tolerance (§7) | ±3 mm | ±1° |
| RSS total | **29.6 mm** | **6.8°** |
| Envelope (D-015) | 35 mm | 10° |
| Margin | 15% | 32% |

The funnel absorbs everything inside the envelope by design; the allocations above are
Phase 1 sweep centers, not guarantees — Phase 1's sensitivity curve (D-014) reports
what happens as each contributor grows past its allocation.

## 6. Capture plane and handoff state vector (D-006)

- **Capture plane:** head_frame YZ plane at the funnel mouth (x = 0).
- **Handoff:** kinematic simulation hands off to contact physics when the predicted
  stud-head center crosses x = +50 mm in head_frame (50 mm before the mouth), and only
  for trials that reach it (D-006).
- **Handoff state vector** (complete, passed across the boundary):
  `T_head_stud` (pose, 7), closing velocity v ∈ ℝ³ (head frame, m/s), angular rate
  ω ∈ ℝ³ (rad/s), pose covariance 6×6, attempt index, sim time. Nothing else crosses;
  if contact physics needs a quantity not listed here, that is a spec bug, not a code
  decision (D-006 consequence).
- **Annulus rule:** contact physics runs on a disc of radius **160 mm** about the
  funnel axis at the capture plane — mouth radius 110 mm + funnel lip 25 mm + 25 mm
  margin [ASSUMED] — not only inside the mouth. Trajectories crossing the capture
  plane inside r ≤ 160 mm get full contact simulation (lip strikes score as the misses
  they are); r > 160 mm scores as a kinematic clean miss. Omitting the annulus would
  silently score near-misses as captures and manufacture the headline number (D-006).
- Funnel geometry closing the arithmetic [D-016; derived]: mouth Ø220 = 2 × (35 mm
  envelope + 20 mm head radius + 55 mm margin-to-wall-angle); throat Ø42 = head Ø40
  + 2 mm; depth 180 mm → wall half-angle atan((110 − 21)/180) ≈ **26°**. At full
  engagement the funnel face stands ~70 mm off the plate (exposed stud 90 mm + latch
  pocket − depth 180 mm), clearing the fiducial plate (§3.2) with no interference.

## 7. Mounting assumptions on host platforms

All **[ASSUMED — unvalidated]**: no fetched source publishes dimensions for any
Project Sustainment platform (`research/VENDORS.md`, program-wide UNVERIFIED: no
weight/payload class published; Dire WOLF only "thousands of pounds" cargo).

- A frame member exists at the host rear capable of reacting 15 kN, accessed via an
  existing lunette bolt pattern (D-002; S-MET-class vehicles tow, so a rated rear
  structure is plausible — plausibility is not validation).
- Stud axis height above ground: 400–800 mm; orientation rearward, level with chassis.
- Obstruction cone: a free cylinder Ø270 mm × 400 mm forward of the plate (funnel
  envelope + margin), no host structure inside it.
- Host attitude at rest: pitch/roll within ±20° (matches §9 sweep; REQ-004 terrain).

## 8. Failure modes, enumerated

Seed of the Phase 1 failure taxonomy — Phase 1 classifies against these rows directly
(D-006, D-014). "Escalate" always means: refuse further attempts, send imagery,
recommend a human decision — never a metric pose from a non-visual source (D-013,
§2.3 confidence-gated abort).

| # | Failure | Detection means | System response |
|---|---|---|---|
| 1 | Outer tag partially occluded | Detection dropout / reprojection error rise; `degradation.occlusion_est` | Continue if pose confidence ≥ threshold; else hold, reacquire; escalate on timeout |
| 2 | Outer tag destroyed | No ID-0 detection at expected range while mission context confirms target | Close to inner-ring range only if commanded policy allows; else escalate with imagery (D-013) |
| 3 | Inner ring occluded | < 1 inner tag decoded inside 300 mm | Abort insertion, back out 300 mm (D-005), reacquire; escalate after attempt budget |
| 4 | Inner ring destroyed | Outer pose OK; zero inner detections at handoff range | **No insertion attempt** (D-013); escalate |
| 5 | Pose ambiguity flip | `tags[].ambiguity_flag`; inter-tag or Cam A/B pose disagreement | Reject frame; require multi-tag or oblique confirmation; persistent → abort stage |
| 6 | Stud bent | Vision pose nominal but contact wrench profile inconsistent with funnel model (D-004 stage 3) | Back out after N anomalous contacts; escalate with imagery |
| 7 | Stud sheared / missing | Inner-ring pose OK; no contact where stud expected | Abort; escalate |
| 8 | Plate detached / shifted | Inter-tag transforms violate §3.5 calibration beyond mount tolerance | Pose invalid; escalate (D-013) |
| 9 | Funnel packed with debris | Insertion force spike without latch confirm | Back out, retry per D-005; escalate. (Debris lives on the serviceable side — D-001) |
| 10 | Latch fails to engage | No latch-confirm after full insertion stroke | Retry per D-005; escalate |
| 11 | Latch engages, does not lock | Intermittent confirm signal | **Do not apply tow load**; re-seat; escalate |
| 12 | Latch locks, will not release | Post-mission release fails | Human procedure via manual release on the head (head = serviceable side, D-001) |
| 13 | Host frame member deformed | Plate pose skewed beyond §7 mounting assumptions; contact/vision mismatch | Abort; escalate |
| 14 | Wrong-ID decode | Decoded ID outside expected variant block (§3.4) | Reject frame; persistent → escalate |
| 15 | Comms loss mid-attempt | Link monitor | **Nominal, not a failure of the attempt**: continue autonomously (REQ-005, Q4); telemetry and any escalation queue store-and-forward |

## 9. Degradation assumptions Phase 1 will parameterize

Each axis with sweep range, distribution, and honest coverage status. **Coverage
legend:** LIT = literature-derived; MR-x = measured if that request is collected,
else extrapolated; EXT = extrapolated, no supporting data (the honest weakness of
D-008-R's fallback tier — in the document, not a footnote).

| Axis | Sweep | Distribution | Coverage |
|---|---|---|---|
| Mud occlusion, outer tag | 0–70%, 10% steps | uniform grid | **MR-001** (else EXT — clean-mask studies only) |
| Mud occlusion, inner ring — swept independently (§3.3) | 0–90%, 10% steps | uniform grid | **MR-001** (else EXT) |
| Illuminance | {1, 2, 5, 10, 50, 100, 10³, 10⁴} lux | log grid | LIT trend; sub-10 lux **MR-002** (else EXT); absolutes non-transferable |
| Rain | contrast reduction + droplet occlusion 0–30% | uniform | EXT — no literature found |
| Sensor dropout | per-frame Bernoulli p ∈ {0, .05, .1, .2, .3} + burst (geometric, mean 5 frames) | as stated | ASSUMED model |
| Lens contamination (Cam B dominant at insertion) | contrast/blur field over 0–50% aperture area | uniform | EXT |
| Host pitch/roll | ±20° each | uniform | terrain input (REQ-004) |
| Partial fiducial destruction | per-tag knockout, sampled over 2⁹ combinations | uniform over sampled set | ASSUMED model |
| View angle | 0–60° from approach geometry | trajectory-induced | LIT to ~60°; near-head-on flip **MR-003** (else derived IPPE fallback) |
| Range | 5 m → contact | trajectory-induced | LIT (detection vs range) |

Perception enters Phase 1 as the injected model (D-007) parameterized by these axes
(D-008-R). Which cells are measured vs extrapolated at run time is recorded in
`ARCHITECTURE.md`'s real-vs-simulated table and updated when MR data lands.

## 10. Known weaknesses

Stated as a section, not buried:

1. The **15 kN rating is unverified** (D-003); Phase 2 owns it.
2. The **funnel carries no tow load; the latch is a single point of failure** (D-003).
3. **Bending sizes the stud neck**, not shear — the ±20° off-axis tow limit is assumed
   and materially constrains the resolver stage (§2.1 derivation; Phase 2 verifies).
4. The **inner ring sits at the most vulnerable point** on the assembly (§3.3).
5. The **perception model is not measured on this system**; detection curves are
   literature-derived until MR-001/002/003 land, and **mud response is extrapolated**
   until MR-001 (D-008-R).
6. **Camera parameters are assumed** (D-012), including both extrinsics in §4.
7. The **tolerance-budget allocations are assumed** sweep centers, not measurements
   (§5).
8. **Host mounting assumptions are unvalidated** — no platform data is published (§7).
9. The capture envelope itself (±35 mm/±10°) is an assumption Phase 2 must confirm
   against real chassis-positioning data (D-015).
