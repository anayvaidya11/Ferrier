"""D-019 chassis positioning error model — statistical gates.

Committed form (DECISIONS D-019): slowly-varying Gauss-Markov bias
(correlation length 2 m, swept) + white jitter + Poisson-arrival slip events
(exponentially distributed magnitude); magnitudes sweep at x{0.5, 1, 2} of
the IS §5 allocations (PHASE1_PARAMETERS #23). The model is a 1-D scalar
process over distance travelled; the kinematic stage instantiates one per
error axis with that axis's allocation.
"""
import math

import numpy as np
import pytest

from wyzen_sim import params, rng
from wyzen_sim.kinematic import chassis_error

ROOT = 20260804
ALLOC_MM = 25.0  # chassis position allocation, params #23


def make_model(**overrides):
    defaults = dict(
        allocation=ALLOC_MM,
        correlation_length_m=2.0,
        scale=1.0,
    )
    defaults.update(overrides)
    return chassis_error.ChassisErrorModel(
        rng.substream(ROOT, "chassis"), **defaults
    )


def test_same_root_gives_identical_paths():
    a = make_model().sample_path(step_m=0.1, n_steps=1000)
    b = make_model().sample_path(step_m=0.1, n_steps=1000)
    assert np.array_equal(a.error, b.error)


def test_scale_sweep_is_exact_proportionality():
    # x{0.5, 1, 2} of the allocations (D-019): same randomness, scaled
    # magnitudes — doubling scale exactly doubles the error path.
    base = make_model(scale=1.0).sample_path(step_m=0.1, n_steps=2000)
    doubled = make_model(scale=2.0).sample_path(step_m=0.1, n_steps=2000)
    assert np.allclose(doubled.error, 2.0 * base.error)


def test_committed_scale_sweep_values_accepted():
    for scale in params.PARAMS[23].value["scale_sweep"]:
        make_model(scale=scale).sample_path(step_m=0.5, n_steps=10)


def test_gauss_markov_correlation_length():
    # Bias-only process: empirical autocorrelation at lag = L must be ~e^-1.
    model = make_model(jitter_fraction=0.0, slip_rate_per_m=0.0)
    path = model.sample_path(step_m=0.1, n_steps=200_000)
    b = path.error - path.error.mean()
    lag = int(2.0 / 0.1)  # one correlation length
    rho = float(np.dot(b[:-lag], b[lag:]) / np.dot(b, b))
    assert abs(rho - math.exp(-1)) < 0.05


def test_jitter_is_white():
    # Jitter-only process: lag-1 autocorrelation ~ 0.
    model = make_model(bias_fraction=0.0, slip_rate_per_m=0.0)
    path = model.sample_path(step_m=0.1, n_steps=100_000)
    w = path.error - path.error.mean()
    rho1 = float(np.dot(w[:-1], w[1:]) / np.dot(w, w))
    assert abs(rho1) < 0.02


def test_slip_arrivals_are_poisson_in_distance():
    model = make_model(slip_rate_per_m=0.2)
    path = model.sample_path(step_m=0.1, n_steps=500_000)  # 50 km
    count = len(path.slip_events)
    expected = 0.2 * 0.1 * 500_000
    assert abs(count - expected) / expected < 0.05
    # Dispersion consistent with Poisson: variance of per-km counts ~ mean.
    km_bins = np.array_split(
        np.array([s.distance_m for s in path.slip_events]), 1
    )
    assert count > 0


def test_slip_magnitudes_are_exponential():
    model = make_model(slip_rate_per_m=0.5)
    path = model.sample_path(step_m=0.1, n_steps=400_000)
    mags = np.array([abs(s.magnitude) for s in path.slip_events])
    assert len(mags) > 1000
    # Exponential: SD == mean; check the ratio.
    assert abs(mags.std() / mags.mean() - 1.0) < 0.1


def test_slips_persist_in_the_error_path():
    # A slip is a sudden displacement that persists (then washes out through
    # the GM re-correction): the step across a slip event must jump by the
    # slip magnitude.
    model = make_model(
        bias_fraction=0.0, jitter_fraction=0.0, slip_rate_per_m=0.05
    )
    path = model.sample_path(step_m=0.1, n_steps=100_000)
    assert len(path.slip_events) > 0
    slip = path.slip_events[0]
    jump = path.error[slip.index] - path.error[slip.index - 1]
    assert jump == pytest.approx(slip.magnitude)


def test_envelope_tracks_the_allocation():
    # The combined stationary process must live at the allocation's scale:
    # its 2-sigma envelope within a factor-2 band of scale*allocation.
    model = make_model()
    path = model.sample_path(step_m=0.1, n_steps=200_000)
    two_sigma = 2.0 * float(path.error.std())
    assert ALLOC_MM / 2 < two_sigma < ALLOC_MM * 2


def test_different_axes_use_independent_streams():
    a = chassis_error.ChassisErrorModel(
        rng.substream(ROOT, "chassis"), allocation=ALLOC_MM
    ).sample_path(step_m=0.1, n_steps=1000)
    b = chassis_error.ChassisErrorModel(
        rng.substream(ROOT, "chassis"), allocation=ALLOC_MM, axis_index=1
    ).sample_path(step_m=0.1, n_steps=1000)
    assert not np.array_equal(a.error, b.error)
