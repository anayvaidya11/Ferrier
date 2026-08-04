# WyZantium Industries — Master Context
### Autonomous recovery and servicing for unmanned ground fleets
**Version 1.0 · 31 July 2026 · Target: YC Spring 2027, projected mid-February 2027**

> **Read this first, every session.** This is the canonical description of what WyZantium is, what is being built, in what order, and under what rules. If any other document, prompt, or memory conflicts with this file, this file wins. If reality conflicts with this file, update this file.

---

## PART I — THE COMPANY

### 1.1 One sentence

WyZantium builds the autonomous hand that keeps unmanned fleets in the fight: a robot that goes forward when another robot goes down, and does the physical work a human would otherwise walk into the kill zone to do.

### 1.2 The claim everything rests on

> **A standardized attachment interface turns autonomous battlefield recovery from a research problem into an engineering problem.**

Every task in this agenda serves that sentence. If a task does not serve it, cut the task.

### 1.3 Why this exists

Militaries are buying unmanned ground vehicles at scale. Ukraine contracted 25,000 UGVs in the first half of 2026 and ran 16,676 missions in June alone. The U.S. Army's S-MET acquisition objective runs to 2,195 systems, and Project Sustainment selected five vendors in July 2026 for a medium logistics robot.

When one of those robots gets mired, runs out of charge, or throws a track a kilometre forward of friendly lines, the only remedy today is to send three or four soldiers into a drone-saturated zone to retrieve a machine. Ukrainian commanders describe this as unacceptable and do it anyway. Ukraine's UGV sector nearly collapsed in 2025 for exactly this reason: manufacturers never built the support layer, so a robot that broke down stayed broken.

The U.S. Army asked industry about this directly. Army Contracting Command at Aberdeen Proving Ground issued an RFI on 17 June 2026 seeking unmanned systems able to autonomously locate, rig, and recover disabled or destroyed vehicles in contested environments, explicitly under denied, degraded, intermittent, and limited (DDIL) network conditions. Responses were due 31 July 2026.

**Fleets are growing faster than the ability to keep them running. That gap is the company.**

### 1.4 What the machine does

Four functions, ordered by increasing difficulty:

| # | Function | Description | Hard part | Ours? |
|---|---|---|---|---|
| 1 | **Find** | Navigate to a disabled asset's last known position, off-road, GPS-denied | Off-road autonomy under DDIL | No — commodity (Overland, Forterra, Scout) |
| 2 | **Assess** | Classify why it stopped: mired / out of charge / mechanically damaged / destroyed | CV on a damaged, mud-covered, arbitrarily-oriented object | **Yes** |
| 3 | **Rig** | Physically attach: tow line, charge connector, battery bay | **The crux. This is the hand.** | **Yes** |
| 4 | **Resolve** | Restart in place, recharge, or extract to a rear point | Traction and power | No — mostly solved engineering |

**Functions 2 and 3 are the company.** Everything defensible lives there. 1 and 4 are purchased or integrated.

### 1.5 The strategic properties that make this fundable

**Useful before it's perfect.** A failed docking attempt costs a wasted trip. The fallback is exactly the status quo — send humans. A mission-level trade model (studies/C09_VALUE_THRESHOLD.md; A-010) shows robot-first recovery beats sending soldiers whenever docking success exceeds the robot-to-human sortie risk ratio — of order 10–35% across the swept parameter region; a 40% rate clears it with margin in most of that region, and Phase 1 measures whether the system does. Almost no autonomy product has this property; most require >95% because failure is catastrophic. This is the single strongest engineering argument in the thesis and it leads every pitch.

**Never pitch as cost savings.** The materiel argument inverts if UGVs get cheap enough, and Ukrainian doctrine explicitly treats them as expendable. The casualty argument does not invert and is worth roughly 15× more. Pitch casualty avoidance with a cost benefit attached.

**Interface, not platform.** The chassis is a purchased component. Armored recovery vehicles already exist. The gap is doing recovery without a human in the loop when the link is jammed.

### 1.6 What killed the previous project, and why this is different

Ghost Medic (offline AI first-aid assistant) was screened against five failure modes and failed all five. WyZantium passes all five.

| # | Test | Ghost Medic | WyZantium |
|---|---|---|---|
| 1 | Funded buyer exists | ✗ No medical UGV program of record | ✓ *weaker (A-008)* — AAL market-research RFI, 17 Jun 2026; no funded program yet |
| 2 | Not already solved by a trained human | ✗ Medics are trained; edge case only | ✓ Current answer is four soldiers forward |
| 3 | Not a commodity feature | ✗ Fall detection ships in every smartwatch | ✓ Autonomous rigging under DDIL |
| 4 | Payload arithmetic closes | ✗ Quadruped: 10–14 kg, 3 hours | ✓ Tow force is gearing, not payload |
| 5 | No regulatory/legal fork | ✗ FDA + Geneva Convention exclusivity | ✓ Materiel function; ITAR is a cost |

**This does not mean WyZantium works.** It means WyZantium does not fail for the reasons Ghost Medic failed. Its own distinct failure mode is §1.7.

### 1.7 The real risk, stated plainly

*Science Robotics* (2026) states that the reliability of robotic manipulation in unstructured environments is unknown. Published grasp success on unknown objects in cluttered scenes runs roughly 75–87% — indoors, well-lit, clean point clouds, human-hand-sized objects.

WyZantium attaches to a mud-covered 500 kg vehicle, at night, at an arbitrary angle, possibly damaged, possibly under observation.

**The mitigation is the thesis.** You do not have to grasp an unknown object. Require a standardized recovery interface on the target — tow eye, fiducial, defined attachment geometry — and an open-ended grasping problem becomes a constrained docking problem. Docking is dramatically more tractable. Every drone dock on earth relies on this.

That converts a physics risk into a standards-adoption risk, which is a business problem a founder can attack.

**Phase 1 exists to measure whether that conversion actually works.**

---

## PART II — THE APPROACH

### 2.1 Build strategy: simulate the risk, model the rest

WyZantium is not building a vehicle in the next six months. It is building **evidence that the vehicle would work**, at near-zero capital cost.

The distinction matters because of what kind of risk this is. Ghost Medic carried *market* risk, which no demo can retire. WyZantium carries *technical* risk, which simulation genuinely can. NVIDIA released Newton 1.0 in April 2026 as a physics foundation purpose-built for contact-rich manipulation, and synthetic grasp training now transfers zero-shot to real hardware. A docking success distribution measured across ten thousand simulated approaches is real, falsifiable evidence produced on a laptop.

Three tiers, applied per subsystem:

| Tier | Method | Applies to |
|---|---|---|
| **Built** | Real, working, tested code | Perception, embedded, wire contracts, abort logic, sim harness |
| **Derived** | Closed-form physics with sourced numbers | Tow forces, power budget, thermal, mechanical envelope |
| **Modeled** | CAD and concept renders, labeled as such | Chassis integration, docking head geometry, vehicle concept |

**Nothing is presented as more real than it is.** Ghost Medic's governing rule carries over verbatim: *simulated = labeled simulated, raw = labeled raw, stub = labeled stub.* Every claim on the site maps to a file in the repo.

**Compute rule — online-first (added 2026-08-01; SUPERSEDED by A-004 — compute is chosen on measured cost per trial; see AMENDMENTS).** Everything designed at first runs on cloud compute. Phase 1 simulation and any training run on rented cloud GPUs; the local machine (MacBook Air M4 — Metal only, no CUDA, 16 GB unified memory) is a terminal, not a compute ceiling. Spec parameters (trial budgets, timesteps, degradation sweep resolution) are sized to cloud GPU capability, not local hardware. Cloud spend is budgeted before Phase 1 starts.

### 2.2 The one thing physics cannot prove

Tow forces, power budgets, and thermal envelopes are closed-form. Docking reliability is not. It is empirical, and it must come from a simulation that is an honest experiment rather than a demonstration.

**If the degradation model is not adversarial, the result is decoration.** A beautiful 95% that a technical reviewer breaks in diligence is worse than an ugly 55% that survives it. The sim must try to break the system.

### 2.3 Architecture pattern (inherited from Ghost Medic)

Contract-first. One wire format between every stage, so any producer can be swapped for any other without touching consumers.

```
GHOST MEDIC                          WyZantium
sensor stream (NDJSON)          →    target-state stream (pose, fault, confidence)
one wire contract               →    one wire contract
parse, gate on ok flag          →    parse, gate on perception confidence
anomaly detected (fall)         →    fault classified (mired/dead/destroyed)
local model, no connectivity    →    local model, DDIL by requirement
guidance to a non-expert        →    rigging plan to an actuator
debounce: when NOT to fire      →    abort logic: when NOT to attempt
```

The last row carries the most weight. The reasoning about *when not to invoke the model* is the seed of abort-and-escalate logic, which in a recovery robot separates a useful machine from one that destroys the asset it was sent to save.

**The confidence-gated abort is the product's honesty discipline in steel:** when pose confidence falls below threshold, the system refuses to attempt, sends imagery, and recommends a human decision. That is Ghost Medic's `ok:false → "unavailable"` rule, applied to actuators.

### 2.4 The interface design rule

**Mechanical universality, electrical specificity.**

The Army has published MIL-STD-3078 (battery interoperability), and the C5ISR Center's Small Tactical Universal Battery provides eight sizes sharing a common mechanical and electrical interface. But different chemistries have different charging profiles and contact locations, which the standards literature states makes interoperable charging genuinely difficult.

So: one tow interface and one manipulator handling a bounded set of standardized attachment geometries, plus a software layer that knows each platform's electrical profile. **The hand is universal. The handshake is per-platform, and it is a config file, not a redesign.**

This makes WyZantium more valuable as MIL-STD-3078 adoption grows. You become the company that services the standard.

### 2.5 Repository structure

```
anayvaidya11/Ferrier/
├── MASTER_CONTEXT.md        # this document, committed
├── INTERFACE_SPEC.md        # the docking interface (Phase 0)
├── ARCHITECTURE.md          # system topology, real-vs-simulated table
├── WIRE_FORMAT.md           # target-state stream contract
├── ROADMAP.md               # phase status, 🟢/🟡/⬜/🧊
├── PHYSICS.md               # derived numbers, sourced (Phase 2)
├── sim/                     # docking simulation harness (Phase 1)
│   ├── scenarios/           # parameterized degradation cases
│   ├── results/             # committed datasets, reproducible
│   └── REPORT.md            # honest writeup + failure taxonomy
├── perception/              # fiducial detection, 6-DoF pose, fault classification
├── firmware/                # embedded C, sensor path
├── control/                 # approach planner, abort logic
├── cad/                     # docking head, interface adapter, concept
├── site/                    # the proof website
└── tools/                   # chart generation, render verification
```

**Docs committed and canonical.** Any Claude Code session orients by reading the repo. When prompt instructions conflict with the repo, the repo wins.

### 2.6 Operational notes (updated 2026-08-01; originally carried from Ghost Medic)

- **Pushes:** Claude Code commits and pushes to GitHub directly in the local macOS environment (verified 2026-08-01, first push of this repo). The Ghost Medic 403 was observed in a *sandboxed* environment and may still apply there. If a push fails: do not retry blindly — commit locally and fall back to the archived recipe: a human runs `git push origin main` manually, or a `deploy.sh` heredoc script is run outside the sandbox. See A-005/A-006.
- **Branches:** sessions in this repo work directly on `main` (verified 2026-08-01). If a session finds itself on a side branch, merge or fast-forward `main` deliberately. **Never force-push `main`.** (The Ghost Medic-era recipe — `git checkout -b main origin/[branch]` then force push — is retired: it errors when a local `main` exists and can overwrite remote history.)
- Prompts should be concise, target autonomous multi-step execution, and include built-in verification gates rather than back-and-forth debugging.

---

## PART III — THE SIX-MONTH PLAN

| Phase | Window | Objective | Gate |
|---|---|---|---|
| 0 | Aug 1–14 | Orient. Read the customer's words. Define the interface. | Interface spec written |
| 1 | Aug 15 – Sep 30 | **The docking experiment.** | **KILL GATE** |
| 2 | October | Physics proof | Closed-form numbers, sourced |
| 3 | November | Perception + embedded on real data | Working stack, measured accuracy |
| 4 | December | Integration, CAD, proof site, cofounder | End-to-end demo runs |
| 5 | January | Customer contact, application | Named human who wants this |
| — | February | Submit | — |

---

### PHASE 0 — Orient (Aug 1–14)

Two weeks. Cheap, and it aims everything that follows.

**Week 1 — Read the customer**
- Locate the RFI on SAM.gov: ACC-APG Durham, posted 17 June 2026. Read every question the Army asked. Their questions are a requirements document written by the customer, for free.
- Search for follow-on signal: resulting solicitations, sources-sought notices, NAMC announcements referencing recovery.
- Read MIL-STD-3078 and the STUB documentation. Know what standard exists before proposing one.
- Study the five Project Sustainment vendors (AM General, American Rheinmetall, Carnegie Robotics, HDT/BLADE, Stratom). These are prospective partners, not just competitors.

**Week 2 — Define the interface**
- `INTERFACE_SPEC.md`: fiducial pattern, mechanical envelope, tolerance budget, load path, failure modes, degradation assumptions.
- `ARCHITECTURE.md`: contract-first topology, real-vs-simulated table.
- `WIRE_FORMAT.md`: the target-state stream — pose, fault class, confidence, timestamps. Field-by-field, with the omitted-not-zeroed rule stated explicitly.
- Stand up the repo with all docs committed.

**Deliverable:** three specification documents. **No implementation code.**

**Gate:** the interface spec is precise enough that Phase 1 can be built directly against it without further design decisions.

---

### PHASE 1 — The docking experiment (Aug 15 – Sep 30) ⚠️ KILL GATE

Six weeks. **The most important work in the agenda.**

One question, answered with a number: *given a standardized target interface, what fraction of autonomous approach-and-latch attempts succeed under realistic field degradation?*

**Build**
- Simulation environment. Isaac Sim or Newton for contact fidelity; Gazebo or MuJoCo if lighter weight is needed. Choose on contact fidelity, not familiarity. **Verify GPU capability in week one, not week five.**
- Parameterized target: interface geometry on a host vehicle at randomized attitude, partial burial, arbitrary heading.
- Parameterized approach: docking head with simulated depth camera and IMU.
- **The degradation model is the actual product.** Mud occlusion percentage, low light, rain, partial sensor dropout, lens contamination, vehicle pitch/roll, partially destroyed fiducial.

**Run**
- 10,000+ randomized trials across the degradation space.
- Report as a **distribution, not a headline.** "94% clean, 61% at 40% fiducial occlusion, 23% below 10 lux without active illumination" is far more credible than "our system achieves 90%."
- Classify every failure mode. The taxonomy of *how* it fails is what tells a mechanical cofounder what to design.

**Gate criteria**

| Result | Meaning | Action |
|---|---|---|
| **>60%** in moderate degradation *(defined numerically in DECISIONS D-029, per A-011)* | Thesis holds | Proceed to Phase 2 |
| **30–60%** | Holds conditionally | Iterate interface / add active illumination or tactile feedback. Two weeks, re-run. |
| **<30%** | Interface does not sufficiently constrain the problem | **Stop.** Revisit whether the wedge is assessment-and-triage rather than physical rigging. |

A bad number here is the experiment working, not the company failing. Finding out in September with five months of runway is the entire point of front-loading it.

**Deliverable:** reproducible harness, committed results dataset, honest writeup with failure taxonomy. This artifact alone outperforms most hardware demos.

---

### PHASE 2 — Physics proof (October)

Four weeks. Mostly closed-form. This is what makes "we can build this" a claim rather than a hope.

- **Tow and extraction forces.** Rolling resistance and mired-vehicle breakout force for a 300–500 kg UGV in mud. Winch line tension, gearing ratios, anchor reaction loads. Show the derivation.
- **Power budget.** Locomotion + compute + winch + illumination against a realistic pack. Endurance under a defined mission profile.
- **Thermal.** Edge compute under continuous inference in an enclosed housing at 45 °C ambient.
- **Mechanical envelope.** Reach, degrees of freedom, payload at extension for the docking head.
- **Chassis selection.** Do **not** design a chassis. Select a commercially available platform, document why, treat it as a purchased component. Write it as a tradeoff study.

**Deliverable:** `PHYSICS.md`, every number derived and sourced.

**Anti-goal:** designing the vehicle. This is the most tempting and least valuable work available.

---

### PHASE 3 — Perception + embedded (November)

Four weeks. Existing skills carry directly.

- **Fiducial detection and 6-DoF pose estimation on real camera data.** Print the target, mount it, cover it in actual mud, shoot it in the dark. Real data, not sim.
- **Fault classification.** From imagery, distinguish mired / out of charge / mechanically damaged / destroyed. Small model, runs local, quantized.
- **Confidence-gated abort.** Below-threshold pose confidence → refuse, send imagery, escalate. Ported directly from Ghost Medic's `ok:false` discipline.
- **Embedded layer.** Sensor stream over the Phase 0 wire contract, same NDJSON-style pattern that already worked.

**Deliverable:** perception stack on real degraded imagery with measured accuracy, plus sensor-path firmware.

**Cross-check:** sim-measured performance vs. real-data performance. Where they diverge, that divergence is itself a finding worth publishing.

---

### PHASE 4 — Integration, proof, cofounder (December)

Four weeks.

- **End-to-end demo.** Simulated approach → real perception on real imagery → docking decision → abort-or-commit. Runs on command, reproducibly.
- **CAD.** Docking head, interface adapter, integrated vehicle concept. Labeled as concept where it is concept.
- **The proof site.** Same four-page structure that worked: overview, how it works, the physics, the evidence. Every claim traceable to a repo file. Real-vs-simulated table front and centre.
- **Recruit the mechanical cofounder.**

**On the cofounder.** You are the CTO — embedded C, CV, models, boards. The gap is mechanical: manipulator design, tow interface, structures, actuator selection, ruggedization. By December you hold a sim result, a physics document, a working perception stack, and a specific well-defined mechanical problem with a failure taxonomy attached. That is a genuinely attractive thing to hand someone.

Targets: robotics/ME people at universities with field robotics programs, FIRST and Formula SAE alumni, anyone in the SF network who builds actuators. **Conversations start 1 November 2026 (A-009; the earlier "no later than early December" was the deadline dressed as a plan).** A cofounder who appears three weeks before the deadline reads to YC exactly like what it is.

---

### PHASE 5 — Customer and application (January)

Four weeks. The YC screener's live objection is here: *procurement is not customers.*

**Get to a human.** Priority order:
1. A UGV manufacturer wanting recovery as a differentiator — HDT/BLADE, Stratom, Carnegie Robotics are all Project Sustainment participants and all smaller than the primes.
2. A NAMC member.
3. An Army unit doing robotics experimentation.
4. Anyone in the SF network with a line into either.

One conversation with a real operator improves the application more than another month of code.

**Also:**
- Cofounder locked, or a documented credible plan.
- Application draft, four full rewrites minimum. Open with *useful before it's perfect.*
- Two-minute video: you, the sim result, the honest number, the failure modes.

**Deliverable:** submitted application citing at least one customer conversation.

---

## PART IV — OPERATING RULES

### 4.1 Weekly cadence

| Day | Activity |
|---|---|
| Monday | Define the week's single deliverable. One. Not three. |
| Wed/Thu | Claude Code executes autonomously against a concise prompt with verification gates |
| Friday | Commit, update ROADMAP status, log real vs. simulated |
| Sunday | 30 minutes: did this week move the load-bearing claim, or just feel productive? |

### 4.2 Anti-rathole rules

1. Never work on a later-phase item while an earlier-phase gate is open.
2. Every claim on the site must map to a completed, evidenced item in the repo.
3. When unsure whether something is real or simulated, the answer goes in the label, not the code.
4. Do not design the chassis.
5. Do not build a medical variant. That was the last company.

### 4.3 Honesty discipline

Carried verbatim from Ghost Medic, because it is the most differentiated asset the founder has:

- Simulated is labeled simulated. Raw is labeled raw. Stub is labeled stub.
- Publish the failure taxonomy alongside the success rate.
- If the repository and the site ever disagree, the repository is right.
- Defense sales pressure runs against this. Hold the line anyway — it is the reason a technical reviewer will trust the number.

### 4.4 Vocabulary constraints

- **Never use the word "lattice."** Anduril's Lattice was selected as the Army's NGC2 common data layer baseline in June 2026.
- Never describe WyZantium as a cost-savings product.
- Never claim autonomy the system does not have; say "under DDIL" only where it is demonstrated.

---

## PART V — HONEST RISKS IN THIS PLAN

**The sim could be decorative.** An insufficiently adversarial degradation model yields a meaningless high number that diligence will break. Make the sim try to break the system.

**Phase 1 is genuinely uncertain.** Nobody knows whether the number comes back good. That is why it is a gate and not a milestone.

**Solo through December is a real cost.** YC accepts solo founders but the bar is higher. Every week past November without a cofounder conversation makes December harder.

**Scope creep toward the chassis.** Persistent temptation. The vehicle is a purchased component; the company is the stack that rides on it.

**Manipulation reliability may simply be hard.** If the standardized interface does not sufficiently constrain the problem, the honest answer is to change the wedge, not to fudge the number.

**Procurement timelines are long.** Fewer than 1% of SBIR Phase I awardees reach a program of record. The realistic first revenue path is riding in as a subcontractor to a prime — which is exactly what Forterra and Primordial Labs did under American Rheinmetall.

**Procurement-stage risk (added by A-008).** Week 1 research established the honest
reading of the demand signal: the recovery RFI is Army Applications Laboratory *market
research* run through ACC-APG Durham; no follow-on solicitation exists as of 2026-07-31,
and recovery is not among CPE Mission Autonomy's three named prototype mission sets
(breaching, sustainment, fires). §1.6 Test 1 remains a pass and a weaker one: **a
customer is asking questions in writing; no funded program yet exists.** If the RFI
matures, the demonstrated pipeline (NAMC RPP → selection in ~one quarter → 18-month OTA)
says the artifact to watch for is a NAMC RPP or AAL solicitation, not a FAR RFP
(research/FOLLOW_ON.md).

---

## PART VI — GLOSSARY

| Term | Meaning |
|---|---|
| **DDIL** | Denied, Degraded, Intermittent, Limited network conditions |
| **UGV** | Unmanned Ground Vehicle |
| **RFI** | Request for Information — market research, precedes a solicitation by 6–18 months |
| **NAMC** | National Advanced Mobility Consortium — OTA vehicle used by Project Sustainment |
| **OTA** | Other Transaction Agreement — faster contracting mechanism than traditional FAR |
| **S-MET** | Small Multipurpose Equipment Transport — the Army's squad robotic mule |
| **MIL-STD-3078** | Army battery interoperability standard |
| **STUB** | Small Tactical Universal Battery — eight sizes, common interface |
| **Rigging** | Physically attaching a recovery line or connector to a disabled asset |
| **Docking** | Constrained attachment to a *known* interface geometry (tractable) |
| **Grasping** | Unconstrained attachment to an *unknown* object (unsolved) |

---

*This document is the single source of truth for WyZantium. Update it when reality changes. Commit every update.*

---

## AMENDMENTS

*Precedence rule (restated by A-006): amendments are authoritative — where an amendment
and the body conflict, the amendment wins. From A-003 onward, substantive changes are
recorded here; the body is touched only to apply a recorded amendment or to add a
one-line supersession marker pointing at the governing amendment. Two earlier amendments
were applied in-body before this mechanism existed: **A-001** (2026-08-01, commit
`00b3c6a`) — §2.5 repository is `anayvaidya11/Ferrier`, not
`wyzantium-industries/recovery-stack`; **A-002** (2026-08-01, commit `2227701`) — §2.1
compute rule, online-first.*

### A-003 (2026-08-01) — Procurement policy narrowed: instruments, not artifacts

`NO_HARDWARE.md` revision 2 supersedes its 1 August 2026 original. The original
prohibited all physical purchase to prevent drifting into building a robot with no team,
no time, and no capital — and accidentally forbade a second, much cheaper activity:
pointing a camera at a muddy tag to collect data. Those are different activities with
different risk profiles, and collapsing them cost the program its measured perception
model.

The governing distinction from here forward is **instrument vs. artifact**. Product
artifacts (any part of the machine, any powered rig, any integration) remain absolutely
prohibited; measurement instruments (camera, lenses, printed targets, lighting,
tripod-class furniture, consumables) are permitted only where a committed decision
depends on a number that cannot be honestly derived or sourced, gated by the
three-question test in `NO_HARDWARE.md`, and channeled exclusively through
`MEASUREMENT_REQUESTS.md`. When an honest number is unavailable, the correct action is
to file a measurement request and stop — never to invent, estimate, or plausibly
interpolate. Consequence for the plan: perception curves become measured-where-
measurable (DECISIONS.md D-008-R); the measurement window is late August, bounded at
three working days of human time, per ROADMAP.md.

### A-004 (2026-08-01) — §2.1 compute rule superseded: cost per trial, not cloud GPU

The online-first compute rule (A-002) was written when Isaac Sim and rendering were in
the plan and a GPU was a hard requirement. D-007 (perception injected, not rendered)
removed the renderer, and with it the constraint that motivated the rule — so the rule
is superseded by its own reasoning, not by preference. The compute target is now chosen
on **measured cost per trial, verified before provisioning**: contact trials run
headless and are expected to run on parallel CPU; cloud GPU remains permitted (a
software purchase under NO_HARDWARE.md rev 2) and is rented only if it beats parallel
CPU on measured cost per trial — the retry loop multiplies trial count, and hourly
billing punishes exactly that workload. The local machine remains a terminal for
anything at experimental scale. This resolves the A-002-vs-spec-plan conflict flagged
during Week 2.

### A-005 (2026-08-01) — §2.6 push workaround obsolete

§2.6's first bullet claimed Claude Code cannot push to GitHub (persistent 403, carried
from Ghost Medic). Reality: the first push of this repo succeeded directly from a
Claude Code session on 2026-08-01. The §2.6 bullet is corrected in-body per this
amendment; the `deploy.sh` heredoc workaround is retired.

### A-006 (2026-08-01) — Documentation-integrity repairs from high-effort review

A review of A-005 found the amendment mechanism internally inconsistent. Repairs, all
applied in-body per the precedence rule now stated in this section's preamble:
(a) the preamble states the rule — amendments win over conflicting body text, and body
edits are limited to applying a recorded amendment or adding a supersession marker;
(b) §2.1's superseded compute-rule paragraph carries an in-body marker pointing at
A-004, so no un-annotated body text silently states retired policy;
(c) §2.6's push note is scoped to the environment where it was verified (local macOS) —
the Ghost Medic 403 was observed in a sandboxed environment and may recur there — and
the fallback recipe (manual push / `deploy.sh` heredoc outside the sandbox) is archived
in-body instead of deleted;
(d) §2.6's branch-recovery recipe (`git checkout -b main origin/[branch]` + force push)
is retired: it errors when a local `main` exists and risks overwriting remote history.
Sessions never force-push `main`;
(e) §2.6 retitled to "Operational notes" — its contents are now verified in this repo,
not Ghost Medic carryover.

### A-007 (2026-08-01) — Pitch-facing deliverables: replay artifacts, cost of the gap, claims register

The end state of this program is a YC demo plus the ask "the gap is capital" — evidence
that the machine would work, and a priced plan for the money to build it. Three
deliverable additions design backwards from that pitch:

(a) **Phase 1 produces replayable trial artifacts**, not only statistics: recorded,
re-runnable visualizations of at least one successful dock and one trial per failure
class, labeled *simulated* per §4.3. The harness logs full trial state from day one —
reproducibility requires it anyway; a partner watching a dock attempt fail honestly is
the demo. A replay of a real trial is evidence made legible; a rendered animation of no
trial would be the §2.2 decorative failure — the distinction is that every replay maps
to a committed trial record.

(b) **Phase 2 produces a "cost of the gap" deliverable**: order-of-magnitude prototype
cost (chassis as purchased component, actuators, sensors, fabrication), team, and a
12-month build plan — what the capital buys. Extends work already scheduled (chassis
tradeoff study, mechanical envelope). Without it "the gap is capital" is a slogan; with
it, an invoice.

(c) **`CLAIMS.md` is the claims register** — every external claim (site, deck, video,
application) maps to claim → evidence file → §4.3 label. Seeded in Phase 1, mandatory
gate for Phase 4's site. This makes §2.1's "every claim maps to a file" rule mechanical
instead of aspirational.

Also noted for Phase 5: the AAL contact channel (unmanned-ground-recovery@aal.army,
Week 1 research) is the warmest named door for the customer conversation.

### A-008 (2026-08-01) — §1.6 Test 1 downgraded to honest strength; procurement-stage risk added to Part V

Week 1 research (research/FOLLOW_ON.md, research/RFI_ACC-APG.md) established that the
recovery RFI is AAL market research, that no follow-on solicitation exists, and that
recovery is not among the three named NAMC prototype mission sets. §1.6 Test 1's row is
annotated in-body: still a pass — a customer asking questions in writing — and a weaker
one than the original text implied. Part V gains a procurement-stage risk entry. Note:
the Week 2 specification prompt also instructed recording "the bench-measurement
pull-forward is cancelled"; that instruction predates NO_HARDWARE rev 2 and is
superseded by A-003/D-008-R (the measurement path now runs through
MEASUREMENT_REQUESTS.md) — recorded here as a prompt-vs-document conflict resolved in
the documents' favor.

### A-009 (2026-08-01) — Cofounder outreach moved to 1 November

The Phase 4 body text said conversations start "no later than early December" — a
deadline dressed as a plan. First outreach now begins **1 November 2026**, as a dated
Phase 3 milestone in ROADMAP.md. Rationale: every artifact this program produces
doubles as recruiting material only if someone actually sees it, and by 1 November the
Phase 1 kill-gate result and the tradeoff curves exist to show. Body edited in-place
per the precedence rule (applying a recorded amendment).

### A-010 (2026-08-02) — §1.5's "40%" sentence replaced by the derived value threshold

The claim "Simulation shows meaningful value at a 40% autonomous success rate" was
circular (CLAIMS C-09): Phase 1's simulation is what would show it, and it led every
pitch while resting on nothing. It is retired. Replacement: the derived mission-level
trade model (studies/C09_VALUE_THRESHOLD.md) — robot-first beats humans-first when
docking success exceeds the robot-to-human sortie risk ratio, P\* = (ρ + h)/(1 + h),
of order 10–35% across the swept region. The new sentence is derived arithmetic with
swept class parameters and no empirical inputs; the old sentence may not be used
externally in any form.

### A-011 (2026-08-02) — Phase 1 early start; post-assessment gate repairs; P-02 ratified

Three records from the Phase 1 planning session, all human-decided or human-reviewed:

(a) **Phase 1 build begins on P-05 sign-off, not on 15 August** (human decision,
2026-08-02). Phase 0 finished ~12 days early; the window end (30 September) is
unchanged, so the early start becomes schedule margin on the kill gate. The Part III
"Aug 15" remains as the no-later-than bound. `PHASE1_PLAN.md` is the committed
execution map (build order, verification gates, week-by-week schedule).

(b) **Four gaps survived the gate self-assessment and were found during planning**,
recorded as HOLES H-13..H-16 and closed through sanctioned doors — most seriously,
the kill-gate criterion "moderate degradation" was never defined numerically anywhere
in the repo; left undefined, the gate cell could be chosen after seeing results.
Now D-029, defined before any trial runs, applied in-body as a marker on both gate
tables. Also: `clean_miss` defined (D-030); PHASE1_PARAMETERS #57 and INTERFACE_SPEC
§8 row 3 consistency repairs; `trial_result.false_capture` additive schema revision
(WIRE_FORMAT).

(c) **P-02 ratified: $100 hard cloud ceiling** for Phase 1 compute, expected spend
$20–60; exceeding it requires a recorded amendment. The A-004 measured-cost test
stands; the DOE runner meters cumulative spend against the ceiling.
