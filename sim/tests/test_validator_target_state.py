"""target_state line validation — WIRE_FORMAT field table, producer-strict.

Producer-strict means the harness's own output must satisfy every rule; the
consumer-side downgrade semantics (e.g. pose-without-cov treated as
pose-absent) are a separate concern for the guidance gate, not for what we
are allowed to write.
"""
import pytest

from wirefmt import validator

NOMINAL = {
    "v": 1,
    "type": "target_state",
    "t_capture": 142.031,
    "t_emit": 142.043,
    "pose": {"t": [2.412, 0.113, -0.071], "q": [1.0, 0.0, 0.0, 0.0]},
    "pose_cov": [0.0009, 0, 0, 0, 0, 0, 0.0016, 0, 0, 0, 0, 0.0016,
                 0, 0, 0, 0.0007, 0, 0, 0.0011, 0, 0.0011],
    "pose_source": "outer_tag",
    "conf": 0.96,
    "stage": "outer_servo",
}


def errs(overrides=None, drop=()):
    obj = {**NOMINAL, **(overrides or {})}
    for key in drop:
        obj.pop(key, None)
    return validator.validate_line(obj)


def test_nominal_line_is_valid():
    assert errs() == []


@pytest.mark.parametrize(
    "field", ["v", "type", "t_capture", "t_emit", "pose_source", "conf", "stage"]
)
def test_missing_required_field_named_in_error(field):
    result = errs(drop=[field])
    assert any(field in e for e in result)


def test_unknown_version_rejected():
    assert any("v" in e for e in errs({"v": 0}))


def test_unknown_type_rejected():
    assert any("type" in e for e in errs({"type": "target_st8"}))


def test_emit_before_capture_rejected():
    assert any("t_emit" in e for e in errs({"t_emit": 142.0}))


def test_zeroed_pose_placeholder_rejected_via_unit_quaternion():
    # The WIRE_FORMAT worked failure: a placeholder pose of zeros. The zero
    # quaternion is not a rotation; the unit-norm rule is what catches it.
    bad = {"t": [0.0, 0.0, 0.0], "q": [0.0, 0.0, 0.0, 0.0]}
    assert any("unit" in e for e in errs({"pose": bad}))


def test_translation_beyond_10m_rejected():
    bad = {"t": [11.0, 0.0, 0.0], "q": [1.0, 0.0, 0.0, 0.0]}
    assert any("10" in e for e in errs({"pose": bad}))


def test_pose_without_pose_cov_rejected():
    # Pose without stated uncertainty is pose-absent by contract; a producer
    # emitting one has a bug.
    assert any("pose_cov" in e for e in errs(drop=["pose_cov"]))


def test_pose_cov_wrong_length_rejected():
    assert any("21" in e for e in errs({"pose_cov": [0.1] * 20}))


def test_pose_cov_must_be_psd():
    cov = [0.0] * 21
    cov[0] = -1.0  # negative x-variance
    assert any("PSD" in e for e in errs({"pose_cov": cov}))


@pytest.mark.parametrize("conf", [-0.1, 1.1])
def test_conf_out_of_range_rejected(conf):
    assert any("conf" in e for e in errs({"conf": conf}))


def test_pose_source_has_no_guessed_value():
    assert any("pose_source" in e for e in errs({"pose_source": "guessed"}))


def test_stage_enum_enforced():
    assert any("stage" in e for e in errs({"stage": "cruising"}))


def test_abort_stage_requires_abort_reason():
    assert any("abort_reason" in e for e in errs({"stage": "abort"}))


def test_escalate_requires_abort_reason_and_escalation():
    result = errs({"stage": "escalate"})
    assert any("abort_reason" in e for e in result)
    assert any("escalation" in e for e in result)


def test_escalate_fully_formed_is_valid():
    assert errs({
        "stage": "escalate",
        "abort_reason": "low_confidence",
        "escalation": {"imagery_ref": "frame_0142.png",
                       "recommend": "human_decision"},
    }) == []


def test_abort_reason_enum_enforced():
    assert any("abort_reason" in e
               for e in errs({"stage": "abort", "abort_reason": "gave_up"}))


def test_fault_class_enum_enforced():
    assert any("fault" in e
               for e in errs({"fault": {"class": "sleepy", "conf": 0.5}}))


def test_zero_lux_rejected():
    # "0 lux is a measurement, not a default" — the field is > 0 by spec;
    # an unavailable observation is omitted.
    assert any("illuminance" in e
               for e in errs({"degradation": {"illuminance_lux": 0}}))


def test_tag_entries_require_documented_keys():
    assert any("tags" in e
               for e in errs({"tags": [{"id": 0, "reproj_err": 0.4}]}))


def test_attempt_n_must_be_at_least_1():
    assert any("attempt" in e for e in errs({"attempt": {"n": 0}}))


def test_unknown_top_level_field_is_not_an_error():
    assert errs({"future_field": 42}) == []


def test_relayed_null_rejected_by_validator_too():
    # The writer refuses to emit nulls; a relayed line containing one must be
    # caught at validation as well (omitted-not-zeroed, both directions).
    assert any("null" in e for e in errs({"fault": None}))
