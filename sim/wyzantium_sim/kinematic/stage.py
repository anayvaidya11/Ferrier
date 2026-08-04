"""Kinematic approach stage + handoff (T5).

Simulates the cheap pre-contact approach (D-006 two-stage split): a commanded
trajectory toward the funnel mouth, perturbed by the D-019 chassis error
model, stepped on a fixed arc-length grid until the stud-head center crosses
the handoff plane at x = +50 mm (#15, IS §6 — official head_frame: approach
side +x, mouth x=0). At the crossing, r = √(y²+z²) against the 160 mm annulus
(#13): r ≤ 160 → HandoffState for the contact stage; r > 160 → the D-006
kinematic-miss path (final clean_miss classification is the T9 classifier's,
D-030). Stage speeds and boundaries are #26/#25; chassis allocations #23
(±25 mm, ±6°) sweep ×{0.5,1,2} via `scale`.

Committed: the numbers above. Arbitrary code-level choices (spec gaps
recorded 2026-08-04, chassis_error precedent): straight-line commanded
trajectory aimed at the mouth center; start at D-004's 3 m outer-stage start;
INSERTION_ONSET_RANGE_MM (the #26 insertion speed has no committed onset);
DS_MM sampling grid; chassis error applied to lateral y/z and rotations about
y/z (axis_index 1-4 on the "chassis" substream); zero angular rate at
handoff; pose_cov defaults to zeros (placeholder until T6 wires perception
into the loop — no current consumer reads it); r evaluated at the
handoff-plane crossing (IS §6's 160 mm derivation reserves 5 mm for the
remaining 50 mm of drift); commanded direction used for the handoff velocity.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from wyzantium_sim import frames, params, rng
from wyzantium_sim.kinematic.chassis_error import ChassisErrorModel
from wyzantium_sim.kinematic.handoff import HandoffState

HANDOFF_X_MM = 50.0            # #15
ANNULUS_R_MM = 160.0           # #13
START_MM = (3000.0, 0.0, 0.0)  # D-004 outer-stage start (3 m)
Q_NOMINAL = (0.0, 0.0, 1.0, 0.0)   # IS §4: anti-parallel, 180° about +Y
HEAD_CENTER_STUD_MM = (70.0, 0.0, 0.0)  # exposed 90 − head radius 20

INSERTION_ONSET_RANGE_MM = 100.0   # arbitrary: #26 insertion-speed onset
DS_MM = 10.0                       # arbitrary: arc-length sampling grid
ZERO_COV = tuple(tuple(0.0 for _ in range(6)) for _ in range(6))


@dataclass(frozen=True)
class KinematicStep:
    t_sim_s: float
    T_head_stud: frames.Pose
    range_mm: float
    stage: str
    v_cmd_ms: float


@dataclass(frozen=True)
class KinematicResult:
    handoff_reached: bool
    handoff: HandoffState | None
    r_mm: float | None
    miss_reason: str | None    # None | "r_gt_annulus" | "no_crossing"
    t_end_s: float
    steps: tuple


def _axis_quat(angle_rad: float, axis: int) -> tuple:
    h = 0.5 * angle_rad
    q = [math.cos(h), 0.0, 0.0, 0.0]
    q[1 + axis] = math.sin(h)
    return tuple(q)


def _rot(q: tuple) -> frames.Pose:
    return frames.Pose(t=(0.0, 0.0, 0.0), q=q)


def _nlerp(q1: tuple, q2: tuple, f: float) -> tuple:
    if sum(a * b for a, b in zip(q1, q2)) < 0.0:
        q2 = tuple(-v for v in q2)
    q = tuple((1.0 - f) * a + f * b for a, b in zip(q1, q2))
    n = math.sqrt(sum(v * v for v in q))
    return tuple(v / n for v in q)


class KinematicStage:
    """One attempt's approach; the D-005 retry loop (T6) re-runs it with a
    new attempt index and start state."""

    def __init__(self, root: int, scale: float = 1.0, start_mm=START_MM,
                 aim_mm=(0.0, 0.0, 0.0), attempt: int = 1, t0_s: float = 0.0,
                 pose_cov=None, ds_mm: float = DS_MM, speeds=None):
        self._start = tuple(float(v) for v in start_mm)
        self._aim = tuple(float(v) for v in aim_mm)
        self._attempt = attempt
        self._t0 = t0_s
        self._cov = ZERO_COV if pose_cov is None else pose_cov
        self._ds = ds_mm

        # (outer, inner, insertion); the T8 trial passes the speed_* sweep
        # axes here — defaults are the #26 committed values.
        sp = params.PARAMS[26].default if speeds is None else speeds
        self._speeds = tuple(float(v) for v in sp)
        self._outer_to_mm = params.PARAMS[25].value["outer_m"][1] * 1000.0
        alloc = params.PARAMS[23].value
        pos_mm = alloc["position_mm"][1]        # chassis contributor: 25 mm
        ang_deg = alloc["angle_deg"][1]         # chassis contributor: 6°
        self._err_models = [
            ChassisErrorModel(rng.substream(root, "chassis"),
                              allocation=a, scale=scale, axis_index=i)
            for i, a in ((1, pos_mm), (2, pos_mm), (3, ang_deg), (4, ang_deg))
        ]

    def _speed_stage(self, range_mm: float) -> tuple:
        if range_mm > self._outer_to_mm:
            return self._speeds[0], "outer"
        if range_mm > INSERTION_ONSET_RANGE_MM:
            return self._speeds[1], "inner"
        return self._speeds[2], "insertion"

    def _pose(self, center, q) -> frames.Pose:
        off = _rot(q).apply(HEAD_CENTER_STUD_MM)
        return frames.Pose(
            t=tuple(c - o for c, o in zip(center, off)), q=q)

    def run(self) -> KinematicResult:
        delta = tuple(a - s for a, s in zip(self._aim, self._start))
        length = math.sqrt(sum(v * v for v in delta))
        d = tuple(v / length for v in delta)
        self._dir = d
        n = int(length // self._ds)
        err_y, err_z, err_ry, err_rz = (
            m.sample_path(self._ds / 1000.0, n + 1).error
            for m in self._err_models)

        steps = []
        t = self._t0
        prev = None  # (center, q, t)
        for k in range(n + 1):
            s = k * self._ds
            center = (self._start[0] + d[0] * s,
                      self._start[1] + d[1] * s + float(err_y[k]),
                      self._start[2] + d[2] * s + float(err_z[k]))
            q_err = _rot(_axis_quat(math.radians(float(err_ry[k])), 1)).compose(
                _rot(_axis_quat(math.radians(float(err_rz[k])), 2))).q
            q = _rot(q_err).compose(_rot(Q_NOMINAL)).q
            rng_mm = math.sqrt(sum(v * v for v in center))
            v_cmd, stage_name = self._speed_stage(rng_mm)
            if k > 0:
                t += self._ds / 1000.0 / v_cmd

            if prev is not None and center[0] <= HANDOFF_X_MM < prev[0][0]:
                return self._cross(prev, (center, q, t), steps)

            steps.append(KinematicStep(
                t_sim_s=t, T_head_stud=self._pose(center, q),
                range_mm=rng_mm, stage=stage_name, v_cmd_ms=v_cmd))
            prev = (center, q, t)

        return KinematicResult(
            handoff_reached=False, handoff=None, r_mm=None,
            miss_reason="no_crossing", t_end_s=t, steps=tuple(steps))

    def _cross(self, prev, cur, steps) -> KinematicResult:
        (c0, q0, t0), (c1, q1, t1) = prev, cur
        f = (c0[0] - HANDOFF_X_MM) / (c0[0] - c1[0])
        center = tuple(a + f * (b - a) for a, b in zip(c0, c1))
        q = _nlerp(q0, q1, f)
        t = t0 + f * (t1 - t0)
        r = math.hypot(center[1], center[2])
        pose = self._pose(center, q)
        steps.append(KinematicStep(
            t_sim_s=t, T_head_stud=pose, range_mm=math.sqrt(
                sum(v * v for v in center)),
            stage="insertion", v_cmd_ms=self._speeds[2]))

        if r > ANNULUS_R_MM:
            return KinematicResult(
                handoff_reached=False, handoff=None, r_mm=r,
                miss_reason="r_gt_annulus", t_end_s=t, steps=tuple(steps))

        v_ms = tuple(self._speeds[2] * v for v in self._dir)
        handoff = HandoffState(
            T_head_stud=pose, v_ms=v_ms, omega_rads=(0.0, 0.0, 0.0),
            pose_cov=self._cov, attempt=self._attempt, t_sim_s=t)
        return KinematicResult(
            handoff_reached=True, handoff=handoff, r_mm=r, miss_reason=None,
            t_end_s=t, steps=tuple(steps))
