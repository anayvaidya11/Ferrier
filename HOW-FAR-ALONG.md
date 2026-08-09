# How far along

<!-- Keep this to ONE short paragraph, high-school reading level.
     Update it whenever a T-task, phase, or gate changes state.
     Sources of truth: ROADMAP.md (phases), PHASE1_PLAN.md §4 (T0–T13 build order), git log. -->

_Last updated: 2026-08-09 (first cloud runs; D-034/035/036)_

WyZantium is working toward a February submission in six phases, and right now
we're in Phase 1: a simulated docking experiment that must hit its kill-gate
number by September 30. The design groundwork (Phase 0) is signed and closed,
and the experiment machine (build tasks T0–T10) is built and proven. This week
the experiment actually started running on rented cloud computers: the physics
step size was confirmed, the cost came in at about a penny per thousand trials
(the whole experiment fits in roughly a dollar against $180 of credits), and
the first 13,000 trials ran. Those first runs caught three real bugs — the
robot's decision logic was giving up on a whole mission over fraction-of-a-
second sensor blips — each fixed as a written, human-approved decision
(D-034/035/036). With the bugs gone, an honest early picture emerged: in clean
conditions docking succeeds almost always, but under the moderate mud and
darkness the kill gate is scored on, the robot usually *refuses* to attempt
(it can't get confident enough in what its cameras show), which currently
points the gate score well below the 30% stop line. Two things could move
that number honestly: the real mud-on-camera measurements happening in late
August, and the already-planned tradeoff study of how cautious the robot
should be. What's left: the full formal sweeps, replayable demo artifacts
(T11), and the charts and report the gate decision needs (T12–T13). Phases
2 through 5 haven't started yet.
