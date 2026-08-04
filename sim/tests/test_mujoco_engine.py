"""T4c cycle B — MuJoCo adapter behind the ContactEngine protocol.

World frame == head_frame: origin at funnel mouth center, +X along the funnel
axis toward the throat (mouth plane is x=0, throat at x=+180). The stud
approaches from x<0. Adapter placement convention (code-level, documented in
mujoco_engine.py): head-sphere center sits at T_head_stud · (70, 0, 0) mm
(exposed 90 − head radius 20); T5's handoff gate pins the full IS §4 pose
convention later.

Units across the boundary: mm for poses, m/s velocities, N / N·m wrench
(WIRE_FORMAT). Gravity is a T1ModelSpec field (head_frame, m/s²), default
mission convention (0,0,-9.81); conformance drops use axis-vertical
(+9.81,0,0) so "down" is the insertion direction.
"""

import math

import numpy as np
import pytest

from wyzantium_sim import frames
from wyzantium_sim.contact import engine
from wyzantium_sim.contact.mujoco_engine import MuJoCoEngine
from wyzantium_sim.kinematic.handoff import HandoffState

DT = 0.001
COV0 = tuple(tuple(0.0 for _ in range(6)) for _ in range(6))


def make_spec(**overrides):
    defaults = dict(stiffness_k_n_mm=10.0, head_mass_kg=15.0)
    defaults.update(overrides)
    return engine.T1ModelSpec(**defaults)


def make_engine(**spec_overrides):
    eng = MuJoCoEngine()
    eng.load(make_spec(**spec_overrides), engine.SolverSettings(timestep_s=DT))
    return eng


def handoff_at(head_center_mm, v_ms=(0.0, 0.0, 0.0)):
    """HandoffState placing the head-sphere center at head_center_mm."""
    t = tuple(head_center_mm[i] - 70.0 * (1 if i == 0 else 0) for i in range(3))
    pose = frames.Pose(t=t, q=(1.0, 0.0, 0.0, 0.0))
    return HandoffState(T_head_stud=pose, v_ms=v_ms,
                        omega_rads=(0.0, 0.0, 0.0), pose_cov=COV0,
                        attempt=1, t_sim_s=0.0)


class TestIdentity:
    def test_engine_identity_for_trial_header(self):
        import mujoco
        eng = make_engine()
        assert eng.engine_id == {"name": "mujoco", "version": mujoco.__version__}


class TestStateRoundTrip:
    def test_set_state_places_head_center(self):
        eng = make_engine()
        eng.set_state(handoff_at((-300.0, 40.0, -25.0)))
        r = eng.state()
        got = r.T_head_stud.apply((70.0, 0.0, 0.0))
        assert got == pytest.approx((-300.0, 40.0, -25.0), abs=1e-6)

    def test_set_state_sets_velocity(self):
        eng = make_engine()
        eng.set_state(handoff_at((-300.0, 0.0, 0.0), v_ms=(0.2, 0.01, -0.02)))
        r = eng.state()
        assert r.stud_v_ms == pytest.approx((0.2, 0.01, -0.02), abs=1e-9)

    def test_step_advances_sim_time(self):
        eng = make_engine(gravity_head_ms2=(0.0, 0.0, 0.0))
        eng.set_state(handoff_at((-300.0, 0.0, 0.0)))
        for _ in range(10):
            r = eng.step(DT)
        assert r.t_sim_s == pytest.approx(10 * DT, rel=1e-9)


class TestUnits:
    def test_free_fall_matches_kinematics(self):
        # No contact possible from x=-500; after t seconds v_x ≈ g t (m/s)
        # and displacement ≈ ½ g t² (reported in mm). Validates mm/m handling.
        g = 9.81
        eng = make_engine(gravity_head_ms2=(g, 0.0, 0.0))
        eng.set_state(handoff_at((-500.0, 0.0, 0.0)))
        n = 200
        for _ in range(n):
            r = eng.step(DT)
        t = n * DT
        assert r.stud_v_ms[0] == pytest.approx(g * t, rel=0.02)
        x_mm = r.T_head_stud.apply((70.0, 0.0, 0.0))[0]
        assert x_mm - (-500.0) == pytest.approx(0.5 * g * t * t * 1000.0, rel=0.03)


class TestContactReporting:
    def test_drop_on_wall_reports_contacts_and_wrench(self):
        # Head above the cone wall at lateral offset 60 mm, axis-vertical
        # gravity: it must land on the wall and the adapter must report
        # per-contact points (head_frame mm, inside the funnel region) and a
        # nonzero aggregated wall wrench opposing the fall.
        eng = make_engine(gravity_head_ms2=(9.81, 0.0, 0.0))
        eng.set_state(handoff_at((-30.0, 60.0, 0.0)))
        hit = None
        for _ in range(2000):
            r = eng.step(DT)
            if r.contacts:
                hit = r
                break
        assert hit is not None, "stud never contacted the funnel wall"
        cp = hit.contacts[0]
        rho = math.hypot(cp.pos_head_mm[1], cp.pos_head_mm[2])
        assert 0.0 <= cp.pos_head_mm[0] <= 185.0
        assert 15.0 <= rho <= 130.0
        assert np.linalg.norm(cp.normal) == pytest.approx(1.0, rel=1e-6)
        # wall pushes back against +x fall: net axial force on the stud < 0
        assert hit.wall_wrench[0] < 0.0
