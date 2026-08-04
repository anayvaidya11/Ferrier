# How far along

<!-- Keep this to ONE short paragraph, high-school reading level.
     Update it whenever a T-task, phase, or gate changes state.
     Sources of truth: ROADMAP.md (phases), PHASE1_PLAN.md §4 (T0–T13 build order), git log. -->

_Last updated: 2026-08-04 (after T8)_

WyZantium is working toward a February submission in six phases, and right now
we're in Phase 1: a simulated docking experiment that must hit its kill-gate
number by September 30. The design groundwork (Phase 0 — all the specs and
contracts) is signed and closed. Of Phase 1's 14 build tasks (T0–T13), the
first 9 are done, and the big one just landed: the simulator now runs complete
start-to-finish docking trials — approach, camera-based guidance, the go/no-go
gate, physical contact, retries — and writes each one to a replayable record
file that comes out byte-for-byte identical when re-run from the same seed.
Wiring it together also uncovered and fixed real gaps in how the earlier
pieces compose. What's left is classifying the outcomes (T9), running the big
parameter sweeps (T10), and turning the results into the charts and report
the gate decision needs. Phases 2 through 5 — real physics proof, real
perception, integration, and customers — haven't started yet.
