"""T5 — kinematic stage + handoff.

Gate (PHASE1_PLAN §4): nominal run hands off at x=+50 mm; synthetic
r>160 mm → clean_miss precondition; HandoffState fields == IS §6 list (the
field-list assert lives in test_contact_engine.py).

Double-entry transcription of the committed numbers:
  #15 handoff trigger: stud-head center crosses x = +50 mm (official frame,
      approach side +x, "50 mm before the mouth", IS §6);
  #13 annulus: r > 160 mm at the crossing → the D-006 kinematic-miss path
      (final clean_miss classification is T9's, D-030);
  #26 stage speeds, defaults (1.0, 0.2, 0.05) m/s (outer/inner/insertion);
  #25 stage boundaries: outer 3 m → 200 mm, inner 200 mm → contact;
  #23 chassis allocations: ±25 mm position, ±6° angle, sweep ×{0.5, 1, 2}
      via D-019.
"""

import math

import pytest

from wyzantium_sim.contact import engine
from wyzantium_sim.contact.mujoco_engine import MuJoCoEngine
from wyzantium_sim.kinematic import stage

ROOT = 20260804
HANDOFF_X_MM = 50.0
ANNULUS_R_MM = 160.0
SPEEDS = (1.0, 0.2, 0.05)


def make_stage(**overrides):
    defaults = dict(root=ROOT, scale=0.0)
    defaults.update(overrides)
    return stage.KinematicStage(**defaults)


def head_center(handoff):
    return handoff.T_head_stud.apply((70.0, 0.0, 0.0))


class TestNominalHandoff:
    def test_hands_off_exactly_at_x50(self):
        result = make_stage().run()
        assert result.handoff_reached
        c = head_center(result.handoff)
        assert c[0] == pytest.approx(HANDOFF_X_MM, abs=1e-6)

    def test_nominal_run_is_on_axis(self):
        result = make_stage().run()
        assert result.r_mm == pytest.approx(0.0, abs=1e-9)
        c = head_center(result.handoff)
        assert math.hypot(c[1], c[2]) == pytest.approx(result.r_mm, abs=1e-9)

    def test_handoff_velocity_is_insertion_speed_closing(self):
        result = make_stage().run()
        v = result.handoff.v_ms
        assert v[0] == pytest.approx(-SPEEDS[2], rel=1e-6)
        assert math.hypot(v[1], v[2]) == pytest.approx(0.0, abs=1e-9)

    def test_speeds_override_honored_default_unchanged(self):
        # T8: the speed_* sweep axes must reach the stage, or the trial
        # header would record a sweep_point the run never realized.
        slow = make_stage(speeds=(1.0, 0.2, 0.025)).run()
        assert slow.handoff.v_ms[0] == pytest.approx(-0.025, rel=1e-6)
        default = make_stage().run()
        assert default.handoff.v_ms[0] == pytest.approx(-SPEEDS[2], rel=1e-6)

    def test_nominal_orientation_is_anti_parallel(self):
        result = make_stage().run()
        assert result.handoff.T_head_stud.q == pytest.approx(
            (0.0, 0.0, 1.0, 0.0))

    def test_time_matches_piecewise_stage_speeds(self):
        # 3000→200 mm at 1.0 m/s, 200→onset at 0.2 m/s, onset→50 mm at
        # 0.05 m/s (onset is the stage's labeled-arbitrary constant)
        result = make_stage().run()
        onset = stage.INSERTION_ONSET_RANGE_MM
        expected = ((3000.0 - 200.0) / 1000.0 / SPEEDS[0]
                    + (200.0 - onset) / 1000.0 / SPEEDS[1]
                    + (onset - 50.0) / 1000.0 / SPEEDS[2])
        assert result.handoff.t_sim_s == pytest.approx(expected, rel=0.05)

    def test_attempt_and_t0_carried(self):
        result = make_stage(attempt=3, t0_s=12.5).run()
        assert result.handoff.attempt == 3
        assert result.handoff.t_sim_s > 12.5


class TestAnnulusMiss:
    def test_synthetic_r_gt_160_is_kinematic_miss(self):
        # aim the trajectory 200 mm off-axis: it crosses x=+50 far outside
        # the annulus → D-006 kinematic-miss path, no HandoffState
        result = make_stage(aim_mm=(0.0, 200.0, 0.0)).run()
        assert not result.handoff_reached
        assert result.handoff is None
        assert result.miss_reason == "r_gt_annulus"
        assert result.r_mm > ANNULUS_R_MM

    def test_never_crossing_is_a_miss_without_radius(self):
        result = make_stage(aim_mm=(2000.0, 500.0, 0.0)).run()
        assert not result.handoff_reached
        assert result.miss_reason == "no_crossing"


class TestChassisError:
    def test_same_root_is_deterministic(self):
        a = make_stage(scale=1.0).run()
        b = make_stage(scale=1.0).run()
        assert a.handoff.T_head_stud.t == b.handoff.T_head_stud.t
        assert a.handoff.T_head_stud.q == b.handoff.T_head_stud.q
        assert a.r_mm == b.r_mm

    def test_scale_1_perturbs_the_handoff(self):
        nominal = make_stage(scale=0.0).run()
        errored = make_stage(scale=1.0).run()
        assert errored.r_mm > 0.0
        assert errored.r_mm != pytest.approx(nominal.r_mm, abs=1e-9)
        assert errored.handoff.T_head_stud.q != nominal.handoff.T_head_stud.q

    def test_steps_are_recorded_per_kinematic_step(self):
        # T8 logs sim_truth every kinematic step pre-handoff (#59)
        result = make_stage().run()
        assert len(result.steps) > 100
        xs = [s.T_head_stud.apply((70.0, 0.0, 0.0))[0] for s in result.steps]
        assert xs == sorted(xs, reverse=True), "approach must descend in x"


class TestContactIntegration:
    def test_nominal_handoff_feeds_the_engine(self):
        result = make_stage().run()
        eng = MuJoCoEngine()
        eng.load(engine.T1ModelSpec(stiffness_k_n_mm=10.0, head_mass_kg=15.0),
                 engine.SolverSettings())
        eng.set_state(result.handoff)
        c = eng.state().T_head_stud.apply((70.0, 0.0, 0.0))
        assert c == pytest.approx((HANDOFF_X_MM, 0.0, 0.0), abs=1e-6)
