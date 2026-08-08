# How far along

<!-- Keep this to ONE short paragraph, high-school reading level.
     Update it whenever a T-task, phase, or gate changes state.
     Sources of truth: ROADMAP.md (phases), PHASE1_PLAN.md §4 (T0–T13 build order), git log. -->

_Last updated: 2026-08-08 (after T10)_

WyZantium is working toward a February submission in six phases, and right now
we're in Phase 1: a simulated docking experiment that must hit its kill-gate
number by September 30. The design groundwork (Phase 0 — all the specs and
contracts) is signed and closed. Of Phase 1's 14 build tasks (T0–T13), the
first 11 are done: the simulator runs complete start-to-finish docking
trials, writes each one to a replay file that comes out byte-for-byte
identical from the same seed, labels every trial with exactly one honest
outcome under a written tie-breaking order, and now has the machinery to run
the big experiment itself — the full sweep plans are committed as data, a
runner works through them in parallel, survives being killed and picks up
exactly where it left off, meters spending against the ratified $100 cloud
ceiling, and ships the probes that pick the physics step size and measure
cost per thousand trials. What's left is actually running the sweeps, then
packaging replayable demo artifacts (T11) and turning the results into the
charts and report the gate decision needs (T12–T13). Phases 2 through 5 —
real physics proof, real perception, integration, and customers — haven't
started yet.
