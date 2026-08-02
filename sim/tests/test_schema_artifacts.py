"""Schema JSON artifacts — the cross-language contract surface.

Phase 3 firmware implements against wirefmt/schema/*.v1.schema.json and the
fixture corpus, not against the Python validator. These tests pin the two
representations together so they cannot drift.
"""
import json
from pathlib import Path

import pytest

from wirefmt import validator

SCHEMA_DIR = Path(__file__).resolve().parent.parent / "wirefmt" / "schema"
TYPES = ["target_state", "trial_header", "sim_truth", "trial_result"]


@pytest.mark.parametrize("line_type", TYPES)
def test_schema_file_exists_and_parses(line_type):
    path = SCHEMA_DIR / f"{line_type}.v1.schema.json"
    schema = json.loads(path.read_text())
    assert schema["properties"]["type"]["const"] == line_type


def load(line_type):
    return json.loads((SCHEMA_DIR / f"{line_type}.v1.schema.json").read_text())


def test_target_state_enums_match_validator():
    props = load("target_state")["properties"]
    assert set(props["pose_source"]["enum"]) == validator.POSE_SOURCES
    assert set(props["stage"]["enum"]) == validator.STAGES
    assert set(props["abort_reason"]["enum"]) == validator.ABORT_REASONS
    assert set(props["fault"]["properties"]["class"]["enum"]) == \
        validator.FAULT_CLASSES


def test_trial_result_outcomes_match_validator():
    props = load("trial_result")["properties"]
    assert set(props["outcome"]["enum"]) == validator.OUTCOMES


def test_required_lists_match_wire_format():
    # WIRE_FORMAT required sets, per line type.
    assert set(load("target_state")["required"]) == {
        "v", "type", "t_capture", "t_emit", "pose_source", "conf", "stage"}
    assert set(load("trial_header")["required"]) == {
        "v", "type", "trial_id", "seed", "code_git_sha", "engine",
        "sweep_point", "params_ref"}
    assert set(load("sim_truth")["required"]) == {
        "v", "type", "t", "T_world_head", "T_world_stud", "actuator_cmd"}
    assert set(load("trial_result")["required"]) == {
        "v", "type", "outcome", "first_attempt_success", "attempts_used",
        "t_total", "handoff_reached"}
