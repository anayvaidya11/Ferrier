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
    # NOTE: translation is mm (repo convention); the WIRE_FORMAT pose is
    # METRES — T8's trial composition owns the /1000 conversion before any
    # pose reaches the perception injector or a wire line.
    T_head_stud: object   # frames.Pose, translation in mm
    v_ms: tuple           # closing velocity, head_frame, m/s
    omega_rads: tuple     # angular rate, rad/s
    pose_cov: tuple       # 6x6, row-major nested tuples, SI (m², m·rad,
                          # rad²) — same units as the wire pose_cov upper
                          # triangle it is rebuilt from (T8 decision)
    attempt: int
    t_sim_s: float
