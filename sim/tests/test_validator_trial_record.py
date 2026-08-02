"""trial_header / sim_truth / trial_result rules + whole-file validation.

WIRE_FORMAT trial record schema: one NDJSON file per trial — header line,
interleaved state sequence, result line. "A trial whose header cannot name
its seed, SHA, and sweep point is not a result; it is an anecdote."
"""
import pytest

from wirefmt import records, validator

HEADER = {
    "v": 1,
    "type": "trial_header",
    "trial_id": "t2-000001",
    "seed": 20260802,
    "code_git_sha": "beb8b24aa0000000000000000000000000000000",
    "engine": {"name": "mujoco", "version": "3.2.0"},
    "sweep_point": {"outer_occlusion": 0.3, "illuminance_lux": 50},
    "params_ref": "PHASE1_PARAMETERS.md",
}

SIM_TRUTH = {
    "v": 1,
    "type": "sim_truth",
    "t": 142.030,
    "T_world_head": {"t": [12.0, 4.1, 0.4], "q": [1.0, 0.0, 0.0, 0.0]},
    "T_world_stud": {"t": [14.4, 4.2, 0.5], "q": [1.0, 0.0, 0.0, 0.0]},
    "actuator_cmd": {"vx": 0.2},
}

RESULT = {
    "v": 1,
    "type": "trial_result",
    "outcome": "success",
    "first_attempt_success": True,
    "attempts_used": 1,
    "t_total": 311.2,
    "handoff_reached": True,
}

TARGET_STATE = {
    "v": 1, "type": "target_state", "t_capture": 142.031, "t_emit": 142.043,
    "pose_source": "none", "conf": 0.1, "stage": "acquire",
}


def errs(base, overrides=None, drop=()):
    obj = {**base, **(overrides or {})}
    for key in drop:
        obj.pop(key, None)
    return validator.validate_line(obj)


# --- trial_header ---

def test_nominal_header_valid():
    assert errs(HEADER) == []


@pytest.mark.parametrize("field", ["trial_id", "seed", "code_git_sha",
                                   "engine", "sweep_point", "params_ref"])
def test_header_missing_required_field(field):
    assert any(field in e for e in errs(HEADER, drop=[field]))


def test_header_engine_needs_name_and_version():
    assert any("engine" in e
               for e in errs(HEADER, {"engine": {"name": "mujoco"}}))


def test_header_seed_must_be_int():
    assert any("seed" in e for e in errs(HEADER, {"seed": "42"}))


# --- sim_truth ---

def test_nominal_sim_truth_valid_without_wrench():
    # contact_wrench omitted before contact — omission is meaningful.
    assert errs(SIM_TRUTH) == []


def test_sim_truth_with_wrench_valid():
    assert errs(SIM_TRUTH,
                {"contact_wrench": [0.0, 4.1, -2.2, 0.0, 0.1, 0.0]}) == []


def test_sim_truth_wrench_needs_six_components():
    assert any("contact_wrench" in e
               for e in errs(SIM_TRUTH, {"contact_wrench": [1.0] * 5}))


@pytest.mark.parametrize("field", ["t", "T_world_head", "T_world_stud",
                                   "actuator_cmd"])
def test_sim_truth_missing_required_field(field):
    assert any(field in e for e in errs(SIM_TRUTH, drop=[field]))


def test_sim_truth_world_pose_may_exceed_10m():
    # The 10 m bound is for T_head_stud on the target-state stream; world
    # frames are unbounded.
    far = {"t": [120.0, 0.0, 0.0], "q": [1.0, 0.0, 0.0, 0.0]}
    assert errs(SIM_TRUTH, {"T_world_head": far}) == []


# --- trial_result ---

def test_nominal_result_valid():
    assert errs(RESULT) == []


@pytest.mark.parametrize("outcome", ["clean_miss", "IS8-1", "IS8-16", "IS8-17"])
def test_valid_outcomes_accepted(outcome):
    assert errs(RESULT, {"outcome": outcome}) == []


@pytest.mark.parametrize("outcome", ["IS8-0", "IS8-18", "latched", ""])
def test_invalid_outcomes_rejected(outcome):
    assert any("outcome" in e for e in errs(RESULT, {"outcome": outcome}))


@pytest.mark.parametrize("field", ["outcome", "first_attempt_success",
                                   "attempts_used", "t_total",
                                   "handoff_reached"])
def test_result_missing_required_field(field):
    assert any(field in e for e in errs(RESULT, drop=[field]))


def test_false_capture_only_with_lip_strike():
    # H-16 revision: false_capture is the IS8-16 sub-path counter.
    assert errs(RESULT, {"outcome": "IS8-16", "false_capture": True}) == []
    assert any("false_capture" in e
               for e in errs(RESULT, {"false_capture": True}))


# --- whole file ---

def write_trial(tmp_path, lines):
    path = tmp_path / "trial.ndjson"
    records.write_ndjson(path, lines)
    return path


def test_wellformed_trial_file_valid(tmp_path):
    path = write_trial(tmp_path, [HEADER, TARGET_STATE, SIM_TRUTH, RESULT])
    assert validator.validate_trial_file(path) == []


def test_file_must_start_with_header(tmp_path):
    path = write_trial(tmp_path, [TARGET_STATE, SIM_TRUTH, RESULT])
    assert any("header" in e for e in validator.validate_trial_file(path))


def test_file_must_end_with_result(tmp_path):
    path = write_trial(tmp_path, [HEADER, TARGET_STATE, SIM_TRUTH])
    assert any("result" in e for e in validator.validate_trial_file(path))


def test_duplicate_header_rejected(tmp_path):
    path = write_trial(tmp_path, [HEADER, HEADER, RESULT])
    assert any("header" in e for e in validator.validate_trial_file(path))


def test_line_errors_carry_line_numbers(tmp_path):
    bad_state = {**TARGET_STATE, "conf": 1.5}
    path = write_trial(tmp_path, [HEADER, bad_state, RESULT])
    assert any(e.startswith("line 2:")
               for e in validator.validate_trial_file(path))
