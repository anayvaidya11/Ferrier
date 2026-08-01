# Procurement Policy — Instruments, Not Artifacts

**Status:** binding. Supersedes the 1 August 2026 version of this file, which prohibited
all physical purchase and is hereby narrowed. The prior version is preserved in git
history (commit `bef4a85`).
**Date:** 1 August 2026, revision 2.

## The rule

**WyZen will not purchase, fabricate, or assemble any part of the product.** No chassis,
no recovery head, no funnel, no latch, no stud, no actuators, no mounting hardware, no
powered rigs, no integration of any kind. The deliverable for YC Spring 2027 is a
demonstrated and simulated design, and buildability is proven through physics,
simulation, CAD, and software, per MASTER_CONTEXT §2.1. **Nothing in this program gets
built.**

The failure mode this policy actively resists is a bench that grows into a prototype. A
tripod and a printed plate is a measurement setup. The same plate on a linear slide with
a servo and a mock funnel is the beginning of a robot nobody has time to finish. Any
powered motion, any mock of product geometry, any assembly that resembles the machine is
an artifact and is prohibited — regardless of how cheap it is.

## The distinction

- An **instrument** is a tool used to produce evidence and then set down. A camera on a
  tripod photographing a printed tag under mud is an instrument. It is consumed by the
  experiment, appears in no design, and is never integrated into anything.
- An **artifact** is a piece of the product. A recovery head, a funnel, a latch, a stud,
  a chassis, a mounting bracket, an actuator, a wiring harness, a powered test rig that
  resembles the machine. These remain absolutely prohibited.

## The carve-out

Measurement instruments are permitted where a program decision depends on a number that
cannot be honestly derived or sourced. Permitted instruments are limited to:

- imaging sensors and lenses
- printed fiducial targets
- lighting
- mounting furniture of the tripod-and-clamp class
- consumable materials such as paper, soil, and water

## The test — applied before any purchase

Three questions. **All three must pass:**

1. Does a committed decision or spec statement depend on a number this produces?
2. Is the item consumed by the experiment rather than incorporated into a design?
3. Would the item be discarded, returned, or repurposed after data collection ends?

Any "no" makes it an artifact, and it is prohibited.

## The escalation rule

**When an honest number is unavailable and the analysis is blocked, the correct action is
never to invent, estimate, or plausibly interpolate. It is to file a measurement request
in `MEASUREMENT_REQUESTS.md` and stop.** The human will evaluate the request, purchase
what is needed, collect the data, and return it.

A blocked analysis that names its blocker is a success. A completed analysis resting on a
fabricated number is a failure that poisons every downstream phase.

## Labeling

Per MASTER_CONTEXT §4.3:

- **Measured** is labeled measured, with the instrument named.
- **Derived** is labeled derived.
- **Literature-sourced** is labeled with its citation.
- **Extrapolated** is labeled extrapolated.
- Absolute values from consumer-grade instruments are labeled **non-transferable**, and
  only relative trends are carried forward.
