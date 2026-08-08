"""T7 — contact stage runner (D-020 latch + IS8-17 jam, per step).

Gate (PHASE1_PLAN §4): centered handoff latches (D-020); offset handoff →
wrench sign matches; symmetric wedge fires IS8-17; lip strike radius ∈
[110,125] mm.

Double-entry transcription:
  D-020 / #54: latched ⟺ stud-head center within 3 mm radial of the throat
      axis at engagement depth, closing speed ≤ 0.1 m/s, condition held
      100 ms.
  IS8-17 / #62: axial contact force > F_ax_jam ∧ |lateral| < F_lat_jam ∧
      no latch confirm within t_jam → jam (abort_reason jam_detected);
      thresholds swept, tests use mid-grid (100 N, 25 N, 1.0 s).
  IS8-16 / #12: contact wrench in the lip band [110, 125] mm before
      capture-plane crossing → lip strike, its own outcome signal.

Scenario driver: axis-vertical gravity (-x) stands in for the commanded
insertion push (labeled arbitrary in the runner; no actuator model exists
pre-T8), same as the T4c conformance suite.
"""

import math

import pytest

from wyzantium_sim import frames
from wyzantium_sim.contact import engine, runner
from wyzantium_sim.contact.mujoco_engine import MuJoCoEngine
from wyzantium_sim.kinematic.handoff import HandoffState

COV0 = tuple(tuple(0.0 for _ in range(6)) for _ in range(6))
Q_NOMINAL = (0.0, 0.0, 1.0, 0.0)
G_AXIAL = (-9.81, 0.0, 0.0)
JAM_MID = runner.JamThresholds(f_ax_n=100.0, f_lat_n=25.0, t_s=1.0)


def handoff_at(head_center_mm, v_ms=(-0.05, 0.0, 0.0)):
    t = (head_center_mm[0] + 70.0, head_center_mm[1], head_center_mm[2])
    return HandoffState(T_head_stud=frames.Pose(t=t, q=Q_NOMINAL),
                        v_ms=v_ms, omega_rads=(0.0, 0.0, 0.0), pose_cov=COV0,
                        attempt=1, t_sim_s=0.0)


def make_engine(dt=0.001, **spec_overrides):
    defaults = dict(stiffness_k_n_mm=70.0, head_mass_kg=15.0,
                    stud_mass_kg=20.0, gravity_head_ms2=G_AXIAL)
    defaults.update(spec_overrides)
    eng = MuJoCoEngine()
    eng.load(engine.T1ModelSpec(**defaults),
             engine.SolverSettings(timestep_s=dt))
    return eng


class TestCenteredHandoffLatches:
    def test_latches_within_budget(self):
        eng = make_engine()
        out = runner.run_contact(eng, handoff_at((50.0, 0.0, 0.0)),
                                 jam=JAM_MID, max_time_s=8.0)
        assert out.latched
        assert not out.jam
        assert out.abort_reason is None
        assert out.latch_time_s is not None and out.latch_time_s < 8.0

    def test_latch_requires_the_hold(self):
        # a max_time shorter than any plausible settle+hold cannot latch
        eng = make_engine()
        out = runner.run_contact(eng, handoff_at((50.0, 0.0, 0.0)),
                                 jam=JAM_MID, max_time_s=0.05)
        assert not out.latched
        assert out.timed_out


class TestOffsetHandoffWrenchSign:
    @pytest.mark.parametrize("offset", [60.0, -60.0], ids=["+y", "-y"])
    def test_wall_pushes_back_toward_axis(self, offset):
        # sign is judged over the first-impact window (as in the T4c
        # conformance suite) — the later slide/rattle down the throat
        # contacts both sides of the axis and washes the sum out
        eng = make_engine()
        results = []
        runner.run_contact(
            eng, handoff_at((30.0, offset, 0.0), v_ms=(-0.05, 0.0, 0.0)),
            jam=JAM_MID, max_time_s=1.5,
            on_step=results.append)
        first = next((i for i, r in enumerate(results) if r.contacts), None)
        assert first is not None, "offset drop must contact the wall"
        burst = []
        for r in results[first:]:
            if not r.contacts:
                break
            burst.append(r.wall_wrench[1])
        f_y = sum(burst)
        assert math.copysign(1.0, f_y) == -math.copysign(1.0, offset)


class TestSymmetricWedgeJam:
    def test_wedge_fires_is8_17(self):
        # constructed wedge: throat narrowed below head diameter
        eng = make_engine(dt=2.0e-4, throat_d_mm=38.0)
        out = runner.run_contact(eng, handoff_at((-160.0, 0.0, 0.0)),
                                 jam=JAM_MID, max_time_s=4.0, dt=2.0e-4)
        assert out.jam
        assert out.abort_reason == "jam_detected"
        assert not out.latched
        assert out.jam_time_s is not None


class TestFullStroke:
    # full_stroke = the at-depth predicate ever held — the "full stroke"
    # half of IS8-10's "full stroke, no confirm" signature (T9 input)

    def test_latched_run_reports_full_stroke(self):
        eng = make_engine()
        out = runner.run_contact(eng, handoff_at((50.0, 0.0, 0.0)),
                                 jam=JAM_MID, max_time_s=8.0)
        assert out.latched
        assert out.full_stroke

    def test_short_timeout_never_reaches_depth(self):
        eng = make_engine()
        out = runner.run_contact(eng, handoff_at((50.0, 0.0, 0.0)),
                                 jam=JAM_MID, max_time_s=0.05)
        assert not out.latched
        assert not out.full_stroke


class TestLipStrike:
    def test_lip_band_contact_flagged_before_crossing(self):
        eng = make_engine()
        out = runner.run_contact(eng, handoff_at((50.0, 117.5, 0.0)),
                                 jam=JAM_MID, max_time_s=1.5)
        assert out.lip_strike
        assert out.lip_radii_mm
        for rho in out.lip_radii_mm:
            assert 110.0 - 3.0 <= rho <= 125.0 + 3.0

    def test_centered_run_has_no_lip_strike(self):
        eng = make_engine()
        out = runner.run_contact(eng, handoff_at((50.0, 0.0, 0.0)),
                                 jam=JAM_MID, max_time_s=8.0)
        assert not out.lip_strike

    def test_soft_base_lip_strike_measured_about_displaced_axis(self):
        # At k = 3 N/mm the axial dead load sags the compliant base by
        # tens of mm, so the head meets the lip after crossing the fixed
        # x = 0 plane but before the displaced mouth (probed: base_x ≈
        # -25 mm at first lip contact, in-band radii 111.7..124.8 mm about
        # the displaced axis). IS §6 defines the band about the funnel
        # axis, so this is a lip strike; a fixed-frame formula misses it.
        eng = make_engine(stiffness_k_n_mm=3.0)
        out = runner.run_contact(eng, handoff_at((50.0, 117.5, 0.0)),
                                 jam=JAM_MID, max_time_s=1.5)
        assert out.lip_strike
        assert out.lip_radii_mm
        for rho in out.lip_radii_mm:
            assert 110.0 - 3.0 <= rho <= 125.0 + 3.0
