# WyZen — Roadmap

Status per phase. Canonical plan lives in [MASTER_CONTEXT.md](MASTER_CONTEXT.md) Part III; this file tracks state only. Updated every Friday per §4.1.

**Legend:** 🟢 complete · 🟡 in progress · ⬜ not started · 🧊 frozen (blocked or deliberately iced)

| Phase | Window | Objective | Gate | Status |
|---|---|---|---|---|
| 0 | Aug 1–14 | Orient. Read the customer's words. Define the interface. | Interface spec written | 🟡 |
| 1 | Aug 15 – Sep 30 | The docking experiment | ⚠️ **KILL GATE** — see criteria below | ⬜ |
| 2 | October | Physics proof | Closed-form numbers, sourced | ⬜ |
| 3 | November | Perception + embedded on real data | Working stack, measured accuracy | ⬜ |
| 4 | December | Integration, CAD, proof site, cofounder | End-to-end demo runs | ⬜ |
| 5 | January | Customer contact, application | Named human who wants this | ⬜ |
| — | February | Submit to YC | — | ⬜ |

---

## Phase 0 — Orient (Aug 1–14) 🟡

### Week 1 — Read the customer 🟢 (completed 2026-07-31)

- 🟢 Locate the ACC-APG Durham RFI (posted 17 Jun 2026) on SAM.gov; capture every Army question → `research/RFI_ACC-APG.md` (full notice text retrieved verbatim via SAM.gov API)
- 🟢 Convert Army questions into numbered requirements, [DIRECT] vs [INFERRED] → `research/REQUIREMENTS.md` (16 requirements: 10 direct, 6 inferred)
- 🟢 Search for follow-on signal: solicitations, sources-sought, NAMC announcements → `research/FOLLOW_ON.md` (17 dated signals; no follow-on solicitation exists yet as of 2026-07-31)
- 🟢 Read MIL-STD-3078 and STUB documentation; know what each does and does not standardize → `research/STANDARDS.md` (full MIL-STD-3078 PDF retrieved and read; MIL-PRF-32383/7 needs human ASSIST retrieval)
- 🟢 Study the five Project Sustainment vendors (AM General, American Rheinmetall, Carnegie Robotics, HDT/BLADE, Stratom) → `research/VENDORS.md` (selection confirmed from three independent sources)

### Week 2 — Define the interface ⬜

- 🟢 `INTERFACE_SPEC.md` v1.0 (2026-08-01) — fiducial pattern, mechanical envelope, tolerance budget, load path, failure modes, degradation assumptions
- 🟢 `ARCHITECTURE.md` v1.0 (2026-08-01) — contract-first topology, real-vs-simulated table, sim architecture, compute plan, Phase 1 output spec
- 🟢 `WIRE_FORMAT.md` v1.0 (2026-08-01) — target-state stream field-by-field; omitted-not-zeroed rule with worked example; consumer checklist; annotated reference lines
- 🟢 Stand up the repo with all docs committed (2026-07-31)
- 🟡 **Gate: OPEN — two items remain** (`HOLES.md`, 2026-08-02): H-04 narrowed to the topology ratification (P-01, human) and H-07 literature-curve extraction (half-day work session). `PHASE1_PARAMETERS.md`: 58/61 filled. Both closable well before Aug 14.

**Deliverable:** three specification documents. No implementation code.
**Gate:** interface spec precise enough that Phase 1 builds directly against it with no further design decisions.

---

### Measurement window (late August, alongside Phase 1 stand-up)

Physical measurements run per `MEASUREMENT_REQUESTS.md` (MR-001 mud, MR-002 low-lux,
MR-003 layout flip rate; MR-004 deferred), under `NO_HARDWARE.md` rev 2
(instruments-not-artifacts). **Hard bound: measurement is three working days of the
human's time. A request that cannot be executed in that budget is deferred, not
extended.** Phase 1 may begin with literature-derived perception curves and swap in
measured curves when they land, provided the swap is recorded and the before/after
results are both reported — silently improving an input mid-experiment is the same
failure as refitting a model after seeing the answer.

## Phase 1 — The docking experiment (Aug 15 – Sep 30) ⬜ ⚠️ KILL GATE

One question, one number: given a standardized target interface, what fraction of autonomous approach-and-latch attempts succeed under realistic field degradation?

**Gate criteria:**

| Result | Meaning | Action |
|---|---|---|
| >60% in moderate degradation | Thesis holds | Proceed to Phase 2 |
| 30–60% | Holds conditionally | Iterate interface / active illumination / tactile feedback; two weeks, re-run |
| <30% | Interface does not sufficiently constrain the problem | **Stop.** Revisit wedge: assessment-and-triage instead of physical rigging |

**Deliverables (per MASTER_CONTEXT Phase 1 + A-007):** reproducible harness, committed
results dataset, honest writeup with failure taxonomy, sensitivity curve (D-014),
first/multi-attempt distributions (D-005), and **replayable trial artifacts** (≥1
successful dock + 1 per failure class, labeled simulated, each mapping to a committed
trial record). First `CLAIMS.md` entries land with these results.

---

## Phase 2 — Physics proof (October) ⬜

Tow/extraction forces, power budget, thermal, mechanical envelope, chassis selection (tradeoff study — do **not** design a chassis). Deliverable: `PHYSICS.md`, every number derived and sourced, **plus the "cost of the gap"** — order-of-magnitude prototype cost, team, and 12-month build plan: what the capital buys (A-007).

## Phase 3 — Perception + embedded (November) ⬜

Fiducial detection + 6-DoF pose on real degraded imagery, fault classification, confidence-gated abort, sensor-path firmware on the Phase 0 wire contract. Cross-check sim vs real performance.

**Milestone — 1 Nov 2026: first cofounder outreach conversations begin (A-009).** Materials in hand by then: the Phase 1 kill-gate number, the D-014 sensitivity curve, the D-017 refusal/damage tradeoff curve, the failure taxonomy, and the H-04 study — a specific, well-defined mechanical problem with evidence attached.

## Phase 4 — Integration, proof, cofounder (December) ⬜

End-to-end demo, CAD (labeled as concept), proof site, mechanical cofounder — conversations start no later than early December. **Site gate: `CLAIMS.md` complete — no external claim without a register row (A-007).**

## Phase 5 — Customer and application (January) ⬜

Get to a human (UGV manufacturer → NAMC member → Army robotics unit → SF network; warmest named door: unmanned-ground-recovery@aal.army from the Week 1 RFI research). Application: four full rewrites minimum, opens with *useful before it's perfect*. Two-minute video.

## Submit (February) ⬜

Application citing at least one customer conversation.
