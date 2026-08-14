# How far along

<!-- Keep this to ONE short paragraph, high-school reading level.
     Update it whenever a T-task, phase, or gate changes state.
     Sources of truth: ROADMAP.md (phases), PHASE1_PLAN.md §4 (T0–T13 build order), git log. -->

_Last updated: 2026-08-14 (pre-window staging: measurement kit, swap rehearsed, T13 draft)_

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
is written and waiting). A full surgical review then swept all ~9,000 lines
of harness code against every committed contract clause (225 of 225
checked, two independent agents per finding) and confirmed 24 issues —
including a real orientation bug that had every trial viewing the target
the wrong way up. The human ratified the whole fix packet in one sitting
(P-08 → decisions D-039 through D-046), every fix landed with before-and-
after evidence, and the experiment re-ran clean: 13,900 new trials for
about 13 cents (freeze_prior_v2). The re-run says the fixes were real but
the verdict is unchanged — in clean conditions docking succeeds ~88% of
the time, and under the moderate mud-and-darkness gate band the robot
still refuses every single attempt rather than risk the asset. That
refusal is built on stand-in perception curves, so the one honest lever
on the gate number is still the measurement window — and that window is
now fully staged: printable tag sheets and day checklists are committed
(machine-verified before printing), the frame-processing script turns
captured clips into ready data rows, the swap itself was rehearsed
end-to-end on synthetic data (finding and fixing a bug that would have
crashed the real run), and the final report is drafted with the
post-measurement numbers left as labeled blanks. When the three CSVs
land, the swap is one command and the report fills in. Phases 2 through
5 haven't started yet.
