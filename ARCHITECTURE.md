# WyZen System Architecture

**Status:** Phase 0 deliverable, v1.0, 2026-08-01. Traceability and labeling rules as in
`INTERFACE_SPEC.md`. Contract-first per MASTER_CONTEXT §2.3.

## 1. The four functions (§1.4)

| # | Function | Ours? | Why |
|---|---|---|---|
| 1 | **Find** — navigate to last known position, off-road, GPS-denied | Integrated | Off-road DDIL autonomy is commodity; named providers in the ecosystem: Forterra (autonomy prime on American Rheinmetall's team), Overland AI (EABC selectee) — `research/VENDORS.md`, `research/FOLLOW_ON.md`. Building it would be competing with our integration partners (REQ-001, REQ-002). |
| 2 | **Assess** — classify why it stopped | **Ours** | CV on a damaged, mud-covered, arbitrarily-oriented object is the defensible perception problem (REQ-012; fault classes in `WIRE_FORMAT.md`). |
| 3 | **Rig** — physically attach | **Ours** | The crux; the entire interface spec exists for this (REQ-003, D-001, D-004). |
| 4 | **Resolve** — restart, recharge, or extract | Integrated | Winch/traction/power are solved engineering purchased with the chassis; the §2.1-derived tow-angle limit (INTERFACE_SPEC §2.1) is the one constraint we impose on it (D-003). |

## 2. Contract-first data flow (§2.3)

One wire contract between every stage; any producer swaps for any other without
touching consumers (REQ-011: everything below the link runs onboard).

```
sensors (Cam A, Cam B, IMU, contact wrench)          [Phase 1: injected models, D-007]
   │
   ▼
perception  ──────────►  TARGET-STATE STREAM  (WIRE_FORMAT.md, NDJSON, versioned)
(detect, pose, fault,          │
 degradation estimates)        ▼
                        ┌─ CONFIDENCE GATE ─┐   gates: stage transitions, attempt
                        │  conf < threshold │   authorization, insertion commit
                        └───────┬───────────┘   (D-013; §2.3 abort discipline)
                        pass ▼         ▼ fail
                     guidance        abort/escalate path
                 (3-stage, D-004;    (refuse, send imagery,
                  approach planner    recommend human — D-013)
                  constrained to the
                  ±20° D-018 sector)
                        ▼
                actuator commands    telemetry/escalation stream
                (approach, insert,   (store-and-forward under DDIL,
                 back-out D-005)      REQ-005; INTERFACE_SPEC §8 row 15)
```

**Where the gate sits and what it gates:** between the stream and every consumer that
can move steel. Below-threshold pose confidence → the system refuses the attempt,
sends imagery, recommends a human decision (§2.3). `pose_source` (WIRE_FORMAT) makes
D-013 enforceable: guidance may only act on enumerated visual/contact sources — there
is no non-visual metric-pose source to act on.

## 3. Real-vs-simulated table (§2.1 tiers + what stands in for what)

If a reader cannot tell from this table alone what is real, the table has failed.

| Subsystem | Tier | Status | What stands in for what |
|---|---|---|---|
| Wire contract + parsers/validators | Built | Phase 1 | Real schema, real validation — nothing stands in |
| Abort / confidence-gate logic | Built | Phase 1 | Real code under test — nothing stands in |
| Sim harness + trial logging/replay (A-007) | Built | Phase 1 | Real code; its *inputs* are simulated and labeled below |
| Contact physics (funnel/stud, last 50 mm + annulus) | Simulated | Phase 1 | Newton solver stands in for hardware docking trials |
| Approach/chassis kinematics | Simulated | Phase 1 | Kinematic model + error injection stands in for a real vehicle on terrain |
| Perception: detection probability | Derived → pending MR-001/002/003 | Phase 1 | Literature-derived curves stand in for bench measurement; **rows move toward Built only when MR data lands — never on the strength of an unfulfilled request** (D-008-R) |
| Perception: mud response | Extrapolated → pending MR-001 | Phase 1 | Clean-occlusion literature extrapolated — **no supporting data** until MR-001 |
| Perception: pose covariance | Derived (literature) | Phase 1 | Published accuracy figures stand in; MR-004 DEFERRED |
| Cameras (both) | Modeled | Phase 0–1 | Assumed parameters (D-012) stand in for hardware |
| Fiducial plate / stud / funnel geometry | Modeled | Phase 0 | D-016 parametric CAD-level definition stands in for fabricated parts (NO_HARDWARE) |
| Tow/extraction physics, power, thermal | Derived | Phase 2 | Closed-form with sourced numbers stands in for testing |
| Fault classification (mired/depleted/damaged/destroyed) | Modeled → Built in Phase 3 | Phase 3 | Until Phase 3, an assumed classifier stub; Phase 3 measures on real imagery |
| Cost of the gap | Derived | Phase 2 | Sourced estimates stand in for quotes (A-007) |

## 4. Simulation architecture (D-006, D-007)

- **Two-stage split:** approach + acquisition in cheap kinematic sim; full contact
  physics only on the last 50 mm, only for trials that reach it, on the 160 mm annulus
  disc — lip strikes score as misses; the capture plane and complete handoff state
  vector are fixed in `INTERFACE_SPEC.md` §6 (D-006).
- **No renderer exists anywhere in Phase 1** (D-007): perception is the injected
  stochastic model over INTERFACE_SPEC §9's axes (D-008-R).
- **Engine: Newton primary, MuJoCo/MJX fallback.** Fallback trigger, testable, no
  re-litigation: *if, within the first provisioning day, Newton cannot report the
  funnel-wall contact wrench per timestep with spatial resolution sufficient to
  recover the lateral error direction (sign and magnitude of the contact-normal offset
  at the wall), switch to MuJoCo.* The wall-reaction force is the stage-3 sensor
  (D-004); an engine that cannot report it cannot run the experiment.
- Isaac Sim exited the plan with the renderer (D-007). Its RTX/no-macOS constraint is
  therefore irrelevant — noted only so nobody reintroduces it for rendering Phase 1
  never does.

## 5. Compute plan (A-004)

Contact trials run headless; **CPU-first is the expectation**. Cloud GPU is a software
purchase and permitted (NO_HARDWARE rev 2), but nothing in Phase 1 requires it under
D-007/D-008-R. The retry loop (D-005) multiplies trial count, and hourly billing
punishes exactly that workload — so the answer is not assumed in either direction.
**The deciding test (A-004), run in Phase 1 week one before provisioning anything:**
implement one representative contact workload (1,000 nominal-parameter trials through
the full capture-plane + annulus pipeline), run it on a cloud CPU instance and a cloud
GPU spot instance, and compare **measured dollars per 1,000 trials**. The winner is
provisioned; the loser is not; both measurements are committed alongside the trial
records (engine and instance identity land in every `trial_header`). The local machine
is a terminal at experimental scale.

## 6. Phase 1 output specification

What the experiment produces, in full (D-005, D-006, D-014, A-007):

1. **The sensitivity curve** — docking success as a function of assumed detection
   rate, the headline that survives perception-model uncertainty (D-014).
2. **Failure taxonomy** keyed row-for-row to `INTERFACE_SPEC.md` §8 — every failed
   trial classified against that table; unclassifiable failures extend the table by
   recorded amendment, not ad-hoc labels.
3. **First-attempt and multi-attempt distributions, reported separately**, with
   `attempts-per-encounter` an explicit swept parameter (D-005).
4. **Committed, reproducible dataset** — seeds, parameters, and results sufficient to
   re-run any trial bit-identically.
5. **Replayable trial artifacts** — ≥1 successful dock + ≥1 per failure class,
   each generated from and mapping to a committed trial record, labeled *simulated*
   (A-007). First `CLAIMS.md` entries land with these.
6. **The refusal-rate vs. damage-risk tradeoff curve** (D-017) — docking outcomes as
   `conf_min_attempt` sweeps {0.50–0.95}: how often the machine refuses versus how
   often it commits to an insertion it should not have attempted. A second deliverable
   of D-014's class, and §1.5's asymmetry made quantitative — arguably the more
   interesting curve to a defense reviewer, because it prices the abort discipline.
