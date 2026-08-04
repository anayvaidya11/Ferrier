"""T4c cycle B / T5 frame pinning — MuJoCo adapter behind ContactEngine.

Official head_frame (pinned by T5 per IS §6's handoff arithmetic and §4's
anti-parallel engagement note; §4's "+X into the funnel" axis wording
contradicted both and carries a dated correction): origin at the funnel
mouth center; the APPROACH side is +x — the stud descends from x>0, handoff
fires at x=+50 mm ("50 mm before the mouth", IS §6), the mouth is x=0, the
funnel interior and throat are at x<0. At nominal engagement stud +X and head +X are
anti-parallel (IS §4); the nominal stud orientation is a 180° rotation about
+Y: q = (0, 0, 1, 0). The head-sphere center sits at T_head_stud · (70, 0, 0)
mm (exposed 90 − head radius 20, D-016).

The adapter may use any internal world; the boundary (set_state / StepResult)
speaks this official frame.

Units across the boundary: mm for poses, m/s velocities, N / N·m wrench
(WIRE_FORMAT). Gravity is a T1ModelSpec field (official head_frame, m/s²),
default mission convention (0,0,-9.81); conformance drops use axis-vertical
(-9.81, 0, 0) so "down" is the insertion direction (-x).
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
Q_NOMINAL = (0.0, 0.0, 1.0, 0.0)  # 180° about +Y: stud +X anti-parallel head +X


def make_spec(**overrides):
    defaults = dict(stiffness_k_n_mm=10.0, head_mass_kg=15.0)
    defaults.update(overrides)
    return engine.T1ModelSpec(**defaults)


def make_engine(**spec_overrides):
    eng = MuJoCoEngine()
    eng.load(make_spec(**spec_overrides), engine.SolverSettings(timestep_s=DT))
    return eng


def handoff_at(head_center_mm, v_ms=(0.0, 0.0, 0.0)):
    """HandoffState placing the head-sphere center at head_center_mm
    (official frame, nominal anti-parallel orientation)."""
    # R(Q_NOMINAL)·(70,0,0) = (-70,0,0), so t = center + (70,0,0)
    t = (head_center_mm[0] + 70.0, head_center_mm[1], head_center_mm[2])
    pose = frames.Pose(t=t, q=Q_NOMINAL)
    return HandoffState(T_head_stud=pose, v_ms=v_ms,
                        omega_rads=(0.0, 0.0, 0.0), pose_cov=COV0,
                        attempt=1, t_sim_s=0.0)


def head_center(result):
    return result.T_head_stud.apply((70.0, 0.0, 0.0))


class TestIdentity:
    def test_engine_identity_for_trial_header(self):
        import mujoco
        eng = make_engine()
        assert eng.engine_id == {"name": "mujoco", "version": mujoco.__version__}


class TestStateRoundTrip:
    def test_set_state_places_head_center(self):
        eng = make_engine()
        eng.set_state(handoff_at((300.0, 40.0, -25.0)))
        r = eng.state()
        assert head_center(r) == pytest.approx((300.0, 40.0, -25.0), abs=1e-6)

    def test_set_state_sets_velocity(self):
        eng = make_engine()
        eng.set_state(handoff_at((300.0, 0.0, 0.0), v_ms=(-0.2, 0.01, -0.02)))
        r = eng.state()
        assert r.stud_v_ms == pytest.approx((-0.2, 0.01, -0.02), abs=1e-9)

    def test_step_advances_sim_time(self):
        eng = make_engine(gravity_head_ms2=(0.0, 0.0, 0.0))
        eng.set_state(handoff_at((300.0, 0.0, 0.0)))
        for _ in range(10):
            r = eng.step(DT)
        assert r.t_sim_s == pytest.approx(10 * DT, rel=1e-9)


class TestUnits:
    def test_free_fall_matches_kinematics(self):
        # No contact possible from x=+500 falling -x; after t seconds
        # v_x ≈ -g t (m/s), displacement ≈ -½ g t² (reported in mm).
        g = 9.81
        eng = make_engine(gravity_head_ms2=(-g, 0.0, 0.0))
        eng.set_state(handoff_at((500.0, 0.0, 0.0)))
        n = 200
        for _ in range(n):
            r = eng.step(DT)
        t = n * DT
        assert r.stud_v_ms[0] == pytest.approx(-g * t, rel=0.02)
        assert head_center(r)[0] - 500.0 == pytest.approx(
            -0.5 * g * t * t * 1000.0, rel=0.03)


class TestContactReporting:
    def test_drop_on_wall_reports_contacts_and_wrench(self):
        # Head above the cone wall at lateral offset 60 mm, axis-vertical
        # gravity (-x): it must land on the wall; contacts are reported in
        # the official frame (funnel interior x<0) and the aggregated wall
        # wrench opposes the fall (+x push-back).
        eng = make_engine(gravity_head_ms2=(-9.81, 0.0, 0.0))
        eng.set_state(handoff_at((30.0, 60.0, 0.0)))
        hit = None
        for _ in range(2000):
            r = eng.step(DT)
            if r.contacts:
                hit = r
                break
        assert hit is not None, "stud never contacted the funnel wall"
        cp = hit.contacts[0]
        rho = math.hypot(cp.pos_head_mm[1], cp.pos_head_mm[2])
        assert -185.0 <= cp.pos_head_mm[0] <= 0.0
        assert 15.0 <= rho <= 130.0
        assert np.linalg.norm(cp.normal) == pytest.approx(1.0, rel=1e-6)
        # wall pushes back against the -x fall: net axial force on stud > 0
        assert hit.wall_wrench[0] > 0.0
