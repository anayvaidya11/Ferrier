"""T4b perception injection — per-model gates against committed formulas.

Sources: #39 (detection anchors), D-023 (mud form), studies/H08 §2/§4 (flip
model, k = 3, class σ_px), #40/#19/#20 (noise propagation), #43–#45
(dropout/contamination/rain), #37–#38 (rate/latency), IS §3.2 (20 px decode
floor). Arbitrary internals (ramp widths, lux floor, conf blend) live in the
curve set / module constants, labeled — these tests pin the committed parts.
"""
import math

import numpy as np
import pytest

from wyzantium_sim import rng
from wyzantium_sim.perception import (
    curves, detection, dropout, flip, mud, noise, timing,
)

ROOT = 20260804


# --- curves: the swap seam ---

def test_prior_v1_is_registered():
    cs = curves.get("prior_v1")
    assert cs.name == "prior_v1"
    assert cs.detection_onset_px == 20.0  # IS §3.2 decode floor
    assert cs.fp_rate_per_image == pytest.approx(1.4e-5)  # #39 anchor


def test_unknown_curve_set_rejected():
    with pytest.raises(KeyError):
        curves.get("mr_v1")  # registered only when MR data lands


def test_register_new_set():
    synthetic = curves.CurveSet(
        name="synthetic_test", detection_onset_px=40.0,
        detection_onset_width_px=10.0, angle_falloff_exponent=2.0,
        lux_knee=10.0, lux_floor_p=0.2, fp_rate_per_image=1.4e-5,
    )
    curves.register(synthetic)
    try:
        assert curves.get("synthetic_test").detection_onset_px == 40.0
    finally:
        curves.unregister("synthetic_test")


# --- mud: D-023, exact form ---

def test_mud_formula_is_d023():
    # P_mask(f) * max(0, 1 - f/f_c) with P_mask = 1 - f (EXT, labeled).
    assert mud.detection_factor(0.0, f_c=0.8) == 1.0
    f, f_c = 0.3, 0.8
    assert mud.detection_factor(f, f_c) == pytest.approx(
        (1 - f) * max(0.0, 1 - f / f_c)
    )


@pytest.mark.parametrize("f_c", [0.6, 0.8, 1.0])
def test_mud_zero_at_and_beyond_f_c(f_c):
    assert mud.detection_factor(f_c, f_c) == 0.0
    assert mud.detection_factor(min(1.0, f_c + 0.1), f_c) == 0.0


def test_mud_is_monotonically_nonincreasing():
    vals = [mud.detection_factor(f, 0.8) for f in np.linspace(0, 1, 21)]
    assert all(a >= b for a, b in zip(vals, vals[1:]))


# --- flip: H08 §2/§4 ---

def test_discriminability_matches_h08_table():
    # Outer tag, Cam A, 3 m: f*S^2/d^2 = 1371 * 0.15^2 / 9 ≈ 3.4 px.
    d_px = flip.discriminability(
        f_px=1371.0, span_m=0.15, dist_m=3.0, tilt_rad=math.pi / 2
    )
    assert d_px == pytest.approx(1371.0 * 0.15**2 / 9.0, rel=1e-6)


def test_theta_min_outer_tag_at_3m_is_26_degrees():
    # H08 §2 table: asin(1.5 * d^2 / (f * S^2)) ≈ 26°.
    theta = math.degrees(math.asin(1.5 * 9.0 / (1371.0 * 0.15**2)))
    assert theta == pytest.approx(26.0, abs=0.5)
    # And the model agrees: at that tilt, D == k*sigma → p_flip == 0.
    d_px = flip.discriminability(1371.0, 0.15, 3.0, math.radians(theta))
    assert flip.p_flip(d_px, sigma_px=0.5, kappa=1.0) == pytest.approx(
        0.0, abs=1e-9
    )


def test_p_flip_formula_and_ceiling():
    # p = 0.5 * max(0, 1 - D/(k*sigma)) * kappa, clamped at the principled
    # 0.5 coin-flip ceiling (H08 §4).
    assert flip.p_flip(0.0, sigma_px=0.5, kappa=1.0) == 0.5
    assert flip.p_flip(0.0, sigma_px=0.5, kappa=2.0) == 0.5  # clamped
    assert flip.p_flip(0.75, sigma_px=0.5, kappa=1.0) == pytest.approx(
        0.5 * (1 - 0.75 / 1.5)
    )
    assert flip.p_flip(0.75, sigma_px=0.5, kappa=0.5) == pytest.approx(
        0.25 * (1 - 0.75 / 1.5)
    )


def test_collar_rule_suppresses_flip():
    # H08 §4: collar layout, >=2 tags visible, observable standoff → no flip.
    assert flip.p_flip_for_layout(
        d_px=0.0, sigma_px=0.5, kappa=1.0, layout="collar",
        n_tags_visible=2, standoff_observable=True,
    ) == 0.0
    # Single-tag frames fall back to the coplanar rule.
    assert flip.p_flip_for_layout(
        d_px=0.0, sigma_px=0.5, kappa=1.0, layout="collar",
        n_tags_visible=1, standoff_observable=True,
    ) == 0.5


def test_reflect_about_boresight_flips_tilt():
    # The wrong branch reflects the rotation about the line of sight
    # (boresight = +x): q = (w, x, y, z) → (w, x, -y, -z).
    q = (0.9689124217106447, 0.1, 0.15, 0.2)  # unit-ish; normalized inside
    flipped = flip.reflect_about_boresight(q)
    assert flipped[0] == pytest.approx(q[0])
    assert flipped[1] == pytest.approx(q[1])
    assert flipped[2] == pytest.approx(-q[2])
    assert flipped[3] == pytest.approx(-q[3])


# --- noise: sigma_px → pose covariance via #19/#20 camera models ---

def test_covariance_scales_follow_first_order_propagation():
    # Lateral sigma = sigma_px*d/f; depth = sigma_px*d^2/(f*S);
    # rotation = sigma_px*d/(f*S) — the same first-order pattern as H08 §3's
    # delta_z ≈ sigma_px*d^2/(f*r).
    cov = noise.pose_cov_upper21(
        sigma_px=0.5, f_px=880.0, dist_m=0.25, span_m=0.11
    )
    lat = 0.5 * 0.25 / 880.0
    depth = 0.5 * 0.25**2 / (880.0 * 0.11)
    rot = 0.5 * 0.25 / (880.0 * 0.11)
    # Order [x y z rx ry rz]; head_frame +x is the boresight/depth axis.
    assert cov[0] == pytest.approx(depth**2)    # var(x) = depth
    assert cov[6] == pytest.approx(lat**2)      # var(y)
    assert cov[11] == pytest.approx(lat**2)     # var(z)
    assert cov[15] == pytest.approx(rot**2)     # var(rx)
    assert len(cov) == 21


def test_covariance_passes_wirefmt_psd_check():
    from wirefmt import validator
    line = {
        "v": 1, "type": "target_state", "t_capture": 1.0, "t_emit": 1.01,
        "pose": {"t": [0.25, 0.0, 0.0], "q": [1.0, 0.0, 0.0, 0.0]},
        "pose_cov": noise.pose_cov_upper21(0.5, 880.0, 0.25, 0.11),
        "pose_source": "inner_ring", "conf": 0.9, "stage": "inner_servo",
    }
    assert validator.validate_line(line) == []


def test_covariance_grows_with_distance():
    near = noise.pose_cov_upper21(0.5, 1371.0, 1.0, 0.15)
    far = noise.pose_cov_upper21(0.5, 1371.0, 3.0, 0.15)
    assert far[0] > near[0] and far[6] > near[6] and far[15] > near[15]


# --- dropout: #43 Bernoulli + geometric bursts ---

def test_dropout_never_when_p_zero():
    model = dropout.FrameDropout(rng.substream(ROOT, "perception.dropout"),
                                 p=0.0, burst_mean=5.0)
    assert not any(model.sample() for _ in range(1000))


def test_dropout_long_run_fraction_and_burst_mean():
    model = dropout.FrameDropout(rng.substream(ROOT, "perception.dropout"),
                                 p=0.05, burst_mean=5.0)
    dropped = np.array([model.sample() for _ in range(200_000)])
    # Burst-length accounting: entries are Bernoulli(p) *starts*, each
    # dropping ~burst_mean frames → long-run fraction ≈ p*burst/(1+p*burst).
    frac = dropped.mean()
    expected = 0.05 * 5.0 / (1 + 0.05 * 5.0)
    assert abs(frac - expected) < 0.03
    # Measured mean burst length ≈ 5 frames (geometric).
    runs, run = [], 0
    for d in dropped:
        if d:
            run += 1
        elif run:
            runs.append(run)
            run = 0
    assert abs(np.mean(runs) - 5.0) < 0.5


def test_contamination_and_rain_factors():
    assert dropout.contamination_factor(0.0) == 1.0
    assert dropout.contamination_factor(0.5) == pytest.approx(0.5)
    assert dropout.rain_factor(0.0) == 1.0
    assert dropout.rain_factor(0.3) == pytest.approx(0.7)


# --- timing: #37/#38 ---

def test_frame_times_and_latency():
    t = timing.frame_times(rate_hz=30, t0=100.0, n=4)
    assert np.allclose(t, [100.0, 100.0 + 1 / 30, 100.0 + 2 / 30,
                           100.0 + 3 / 30])
    assert timing.emit_time(100.0, latency_ms=30) == pytest.approx(100.030)


# --- detection: composite of committed factors ---

def test_detection_plateau_when_clean_and_large():
    cs = curves.get("prior_v1")
    p = detection.p_detect(
        px_size=100.0, view_angle_rad=0.0, mud_fraction=0.0, f_c=0.8,
        illuminance_lux=41000, curve=cs,
    )
    assert p == pytest.approx(1.0)  # #39: near-field plateau ~1.0


def test_detection_zero_below_decode_floor():
    cs = curves.get("prior_v1")
    assert detection.p_detect(5.0, 0.0, 0.0, 0.8, 41000, cs) == 0.0


def test_detection_factors_compose_multiplicatively():
    cs = curves.get("prior_v1")
    p = detection.p_detect(
        px_size=100.0, view_angle_rad=math.radians(60), mud_fraction=0.3,
        f_c=0.8, illuminance_lux=41000, curve=cs,
    )
    expected = (math.cos(math.radians(60)) ** cs.angle_falloff_exponent
                * mud.detection_factor(0.3, 0.8))
    assert p == pytest.approx(expected)


def test_detection_low_lux_degrades():
    cs = curves.get("prior_v1")
    bright = detection.p_detect(100.0, 0.0, 0.0, 0.8, 50, cs)
    dim = detection.p_detect(100.0, 0.0, 0.0, 0.8, 2, cs)
    assert bright == pytest.approx(1.0)  # at/above the 10-lux knee... 50 lux
    assert dim < bright
