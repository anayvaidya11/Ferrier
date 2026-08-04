"""T4b orchestrator gates — wirefmt-valid emission with honest omission.

The injector consumes ground truth plus a per-frame scene description (which
tags could geometrically be seen, at what range/angle/camera) and emits
target_state lines. Every line must pass the producer-strict validator;
non-detections omit pose/tags rather than zeroing; the curve-swap seam
changes behavior only through the registry.
"""
import copy

import pytest

from wirefmt import validator
from wyzen_sim.frames import Pose
from wyzen_sim.perception import curves, inject

ROOT = 20260804

TRUTH = Pose((2.412, 0.113, -0.071), (1.0, 0.0, 0.0, 0.0))

CLEAN_OUTER = [inject.TagSighting(
    tag_id=0, camera="A", dist_m=2.4, view_angle_rad=0.2, span_m=0.15,
)]

TWO_INNER = [
    inject.TagSighting(tag_id=1, camera="B", dist_m=0.25,
                       view_angle_rad=0.5, span_m=0.11),
    inject.TagSighting(tag_id=4, camera="B", dist_m=0.25,
                       view_angle_rad=0.5, span_m=0.11),
]

NOMINAL_SWEEP = {
    "outer_occlusion": 0.0, "inner_occlusion": 0.0,
    "illuminance_lux": 41000, "rain": 0.0, "dropout_p": 0.0,
    "lens_contamination": 0.0, "mud_f_c": 0.8, "flip_kappa": 1.0,
    "sigma_px": 0.5, "perception_rate_hz": 30, "perception_latency_ms": 30,
    "curve_set": "prior_v1",
}


def make_injector(**overrides):
    sweep = {**NOMINAL_SWEEP, **overrides}
    return inject.PerceptionInjector(root_seed=ROOT, config=sweep)


def test_nominal_outer_line_is_valid_and_sourced():
    line = make_injector().observe(
        t=142.031, truth=TRUTH, sightings=CLEAN_OUTER, stage="outer_servo"
    )
    assert validator.validate_line(line) == []
    assert line["pose_source"] == "outer_tag"
    assert "pose" in line and "pose_cov" in line
    assert line["tags"][0]["id"] == 0
    assert line["t_emit"] == pytest.approx(line["t_capture"] + 0.030)


def test_no_detection_omits_pose_and_tags():
    # Full mud on every tag → nothing detected; omission, never zeroing.
    line = make_injector(outer_occlusion=1.0, inner_occlusion=1.0).observe(
        t=143.1, truth=TRUTH, sightings=CLEAN_OUTER, stage="outer_servo"
    )
    assert validator.validate_line(line) == []
    assert line["pose_source"] == "none"
    assert "pose" not in line and "pose_cov" not in line and "tags" not in line


def test_two_inner_tags_fuse():
    line = make_injector().observe(
        t=214.5, truth=Pose((0.182, 0.004, -0.009), (1.0, 0.0, 0.0, 0.0)),
        sightings=TWO_INNER, stage="inner_servo",
    )
    assert validator.validate_line(line) == []
    assert line["pose_source"] == "multi_tag_fused"
    assert len(line["tags"]) == 2


def test_same_root_is_deterministic():
    a = make_injector().observe(142.0, TRUTH, CLEAN_OUTER, "outer_servo")
    b = make_injector().observe(142.0, TRUTH, CLEAN_OUTER, "outer_servo")
    assert a == b


def test_noisy_pose_differs_from_truth_but_stays_close():
    line = make_injector().observe(142.0, TRUTH, CLEAN_OUTER, "outer_servo")
    t = line["pose"]["t"]
    assert t != list(TRUTH.t)
    assert all(abs(a - b) < 0.05 for a, b in zip(t, TRUTH.t))


def test_dropout_frame_reports_degradation():
    line = make_injector(dropout_p=1.0).observe(
        142.0, TRUTH, CLEAN_OUTER, "outer_servo"
    )
    assert validator.validate_line(line) == []
    assert line["pose_source"] == "none"
    assert line["degradation"]["dropout"] is True


def test_curve_swap_changes_output_only_via_registry():
    # A synthetic set with the decode floor above the outer tag's px size
    # kills detection; identical config otherwise.
    base = curves.get("prior_v1")
    synthetic = curves.CurveSet(
        name="synthetic_kill", detection_onset_px=200.0,
        detection_onset_width_px=base.detection_onset_width_px,
        angle_falloff_exponent=base.angle_falloff_exponent,
        lux_knee=base.lux_knee, lux_floor_p=base.lux_floor_p,
        fp_rate_per_image=base.fp_rate_per_image,
    )
    curves.register(synthetic)
    try:
        with_prior = make_injector().observe(
            142.0, TRUTH, CLEAN_OUTER, "outer_servo")
        with_kill = make_injector(curve_set="synthetic_kill").observe(
            142.0, TRUTH, CLEAN_OUTER, "outer_servo")
    finally:
        curves.unregister("synthetic_kill")
    assert with_prior["pose_source"] == "outer_tag"
    assert with_kill["pose_source"] == "none"


def test_config_must_carry_every_required_key():
    broken = {k: v for k, v in NOMINAL_SWEEP.items() if k != "flip_kappa"}
    with pytest.raises(inject.ConfigError, match="flip_kappa"):
        inject.PerceptionInjector(root_seed=ROOT, config=broken)
