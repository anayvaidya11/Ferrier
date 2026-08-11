# How far along

<!-- Keep this to ONE short paragraph, high-school reading level.
     Update it whenever a T-task, phase, or gate changes state.
     Sources of truth: ROADMAP.md (phases), PHASE1_PLAN.md §4 (T0–T13 build order), git log. -->

_Last updated: 2026-08-11 (R01 surgical review complete; ratification packet P-08 waiting)_

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
points the gate score well below the 30% stop line. Since then the loop was
closed for real (holds now physically stop the vehicle, a human-approved
fix), the replay and analysis tools were built (T11–T12), and the full
formal experiment ran and was frozen: 13,400 trials, verifiable by
regeneration, about 25 cents of compute total. The frozen pre-measurement
number: under moderate degradation the robot refuses every attempt (0% of
5,000 gate trials, all safe refusals — it never risks the asset), while
clean-condition success sits near 89%. That number is built on stand-in
perception curves; the one thing that can move it honestly is the late-
August measurement window (about 3 days of human time — the approval packet
is written and waiting). Since the freeze, a full surgical review swept all
~9,000 lines of harness code against every committed contract clause (225
of 225 checked, two independent agents per finding): it confirmed 24 issues,
including a real orientation bug — every frozen trial ran with the target
flipped the wrong way, making the cameras' view of the tags much worse than
the specs intend — plus a handful of sweep axes that were promised but never
actually varied. None of it was patched silently: the fixes wait as one
written approval packet (P-08), then one cheap batched re-run replaces the
frozen numbers before the measurement swap. After that: the curve swap, the
final gate number reported before-and-after, and the T13 report. Phases 2
through 5 haven't started yet.
