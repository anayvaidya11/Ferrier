"""T8 — trial logger: canonical NDJSON emission via wirefmt.

The logger owns the wire seams the stage code refuses to own: the mm→m
pose conversion (handoff.py / inject.py docstrings assign it to T8), the
world-frame convention (world ≡ stud frame: T_world_stud is identity on
every line, T_world_head recovers T_head_stud exactly), the 21-element
upper-triangle ↔ 6×6 covariance shape, and the sticky contact_wrench
omission (omitted-not-zeroed until first contact, a measurement after).
Every buffered line is validated at buffer time (producer-strict).
"""
import math

import pytest

from wirefmt import records, validator
from wyzantium_sim import frames
from wyzantium_sim.contact import engine
from wyzantium_sim.logging import trial_logger
from wyzantium_sim.perception import noise

Q_NOMINAL = (0.0, 0.0, 1.0, 0.0)
T_MM = frames.Pose(t=(120.0, 117.5, -30.0), q=Q_NOMINAL)


def step_at(t_s, contacts=(), wrench=(0.0,) * 6):
    return engine.StepResult(
        t_sim_s=t_s, T_head_stud=T_MM, stud_v_ms=(-0.05, 0.0, 0.0),
        stud_omega_rads=(0.0, 0.0, 0.0), contacts=tuple(contacts),
        wall_wrench=tuple(wrench), funnel_t_mm=(0.0, 0.0, 0.0))


CONTACT = engine.ContactPoint(pos_head_mm=(0.0, 117.5, 0.0),
                              normal=(-1.0, 0.0, 0.0), force_n=12.0)


def target_state_line(**overrides):
    line = {"v": 1, "type": "target_state", "t_capture": 1.0, "t_emit": 1.012,
            "pose_source": "none", "conf": 0.0, "stage": "outer_servo"}
    line.update(overrides)
    return line


def make_logger(tmp_path, name="t.ndjson"):
    return trial_logger.TrialLogger(tmp_path / name)


def log_minimal_record(log):
    log.header(trial_id="mujoco-7-abc12345", seed=7,
               code_git_sha="deadbeef", engine={"name": "mujoco", "version": "3.2"},
               sweep_point={"curve_set": "prior_v1"},
               params_ref="PHASE1_PARAMETERS.md")
    log.sim_truth_kinematic(0.5, T_MM, {"mode": "velocity", "v_cmd_ms": 0.5})
    log.target_state(target_state_line())
    log.sim_truth_contact(step_at(1.4, contacts=[CONTACT],
                                  wrench=(30.0, 1.0, 0.0, 0.0, 0.0, 0.0)),
                          {"mode": "gravity_insert"})
    log.result(outcome="success", first_attempt_success=True,
               attempts_used=1, t_total=1.4, handoff_reached=True)


class TestUnitSeams:
    def test_pose_mm_to_m_divides_translation_only(self):
        m = trial_logger.pose_mm_to_m(T_MM)
        assert m.t == pytest.approx((0.120, 0.1175, -0.030))
        assert m.q == pytest.approx(T_MM.q)

    def test_upper21_round_trips_through_6x6(self):
        cov21 = noise.pose_cov_upper21(0.5, 1371.0, 2.4, 0.15)
        m = trial_logger.upper21_to_6x6(cov21)
        assert all(m[i][j] == m[j][i] for i in range(6) for j in range(6))
        flat = [m[i][j] for i in range(6) for j in range(i, 6)]
        assert flat == pytest.approx(cov21)


class TestWorldConvention:
    def test_stud_frame_is_world(self, tmp_path):
        log = make_logger(tmp_path)
        log.sim_truth_kinematic(0.5, T_MM, {"mode": "velocity",
                                            "v_cmd_ms": 0.5})
        line = log.lines[-1]
        assert line["T_world_stud"] == {"t": [0.0, 0.0, 0.0],
                                        "q": [1.0, 0.0, 0.0, 0.0]}
        # T_head_stud (m) is exactly recoverable: T_world_head⁻¹ ∘ T_world_stud
        world_head = frames.Pose.from_wire(line["T_world_head"])
        recovered = world_head.inverse()
        expected = trial_logger.pose_mm_to_m(T_MM)
        assert recovered.t == pytest.approx(expected.t)
        assert tuple(abs(a) for a in recovered.q) == pytest.approx(
            tuple(abs(b) for b in expected.q))


class TestStickyWrench:
    def test_wrench_omitted_before_first_contact_present_after(self, tmp_path):
        log = make_logger(tmp_path)
        cmd = {"mode": "gravity_insert"}
        log.sim_truth_contact(step_at(0.1), cmd)
        log.sim_truth_contact(step_at(0.2, contacts=[CONTACT],
                                      wrench=(30.0, 0.0, 0.0, 0.0, 0.0, 0.0)),
                              cmd)
        log.sim_truth_contact(step_at(0.3), cmd)  # zeros, but post-contact
        assert "contact_wrench" not in log.lines[0]
        assert log.lines[1]["contact_wrench"] == [30.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        assert log.lines[2]["contact_wrench"] == [0.0] * 6

    def test_kinematic_lines_never_carry_wrench(self, tmp_path):
        log = make_logger(tmp_path)
        log.sim_truth_kinematic(0.5, T_MM, {"mode": "velocity",
                                            "v_cmd_ms": 0.5})
        assert "contact_wrench" not in log.lines[-1]


class TestProducerStrict:
    def test_every_buffered_line_validates(self, tmp_path):
        log = make_logger(tmp_path)
        log_minimal_record(log)
        for line in log.lines:
            assert validator.validate_line(line) == []

    def test_invalid_target_state_raises(self, tmp_path):
        log = make_logger(tmp_path)
        bad = target_state_line()
        del bad["conf"]
        with pytest.raises(trial_logger.TrialLogError):
            log.target_state(bad)

    def test_invalid_outcome_raises(self, tmp_path):
        log = make_logger(tmp_path)
        with pytest.raises(trial_logger.TrialLogError):
            log.result(outcome="bogus", first_attempt_success=False,
                       attempts_used=1, t_total=1.0, handoff_reached=False)

    def test_result_omits_false_capture_when_none(self, tmp_path):
        log = make_logger(tmp_path)
        log.result(outcome="success", first_attempt_success=True,
                   attempts_used=1, t_total=1.0, handoff_reached=True)
        assert "false_capture" not in log.lines[-1]


class TestWrittenFile:
    def test_file_validates_and_reserializes_byte_identically(self, tmp_path):
        log = make_logger(tmp_path)
        log_minimal_record(log)
        path = log.write()
        assert validator.validate_trial_file(path) == []
        raw = path.read_bytes()
        rebuilt = b"".join(
            (records.dumps_line(obj) + "\n").encode("utf-8")
            for obj in records.read_ndjson(path))
        assert raw == rebuilt
