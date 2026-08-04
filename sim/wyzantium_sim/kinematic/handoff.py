"""Handoff state vector (IS §6, D-006).

Exactly six fields cross the kinematic→contact boundary: `T_head_stud` (pose),
closing velocity v (head_frame, m/s), angular rate ω (rad/s), pose covariance
6×6, attempt index, sim time. Nothing else crosses; if contact physics needs a
quantity not listed here, that is a spec bug, not a code decision.

Owned here per PHASE1_PLAN §2 (kinematic/ row); adopted by T5's handoff logic.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HandoffState:
    T_head_stud: object   # frames.Pose, translation in mm
    v_ms: tuple           # closing velocity, head_frame, m/s
    omega_rads: tuple     # angular rate, rad/s
    pose_cov: tuple       # 6x6, row-major nested tuples
    attempt: int
    t_sim_s: float
