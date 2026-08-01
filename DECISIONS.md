# Design Decisions — Record of Authority

Every spec statement in `INTERFACE_SPEC.md`, `ARCHITECTURE.md`, and `WIRE_FORMAT.md`
must trace to a REQ-xxx in `research/REQUIREMENTS.md` or a D-xxx here. A spec statement
with no traceable parent is a hole and must be flagged, not quietly asserted.

Superseded decisions are struck through, never deleted — the reasoning chain stays
auditable. Revisions carry an `-R` suffix.

---

### D-001 — Mating principle is split
Compliant funnel + active latch live on the WyZen recovery head. A hardened male capture
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

### D-003 — Preliminary latch load rating: 15 kN design
≈10 kN breakout for a mired 500 kg UGV × 1.5 safety factor. Stated as an **assumption,
unverified until Phase 2**.
**Consequence:** under tow the funnel carries zero load — tension pulls the stud straight
out of the mouth. The latch is the entire primary structure and a single point of
failure. Said plainly wherever the rating appears.

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
