"""D-019 chassis positioning error model.

Committed form (DECISIONS D-019): slowly-varying Gauss-Markov bias with a
2 m correlation length (swept), plus white jitter, plus Poisson-arrival slip
events with exponentially distributed magnitude; magnitudes scale at
x{0.5, 1, 2} of the IS §5 allocations (PHASE1_PARAMETERS #23). The process
is 1-D over distance travelled; the kinematic stage instantiates one model
per error axis with that axis's allocation.

Slips feed the bias state: a slip is a sudden persistent displacement that
the Gauss-Markov re-correction then washes out — the mud-slip phenomenology
D-019 names. The allocation is read as the ~2-sigma envelope of the combined
process; how it splits across bias/jitter/slip components is NOT committed
anywhere, so the split lives here as visible, arbitrary-labeled constants —
changing the committed envelope or correlation length is a decision
revision, changing a fraction below is a code-level tuning choice.
"""
from dataclasses import dataclass

import math

import numpy as np

# Arbitrary code-level proportions of the allocation's sigma (labeled).
DEFAULT_BIAS_FRACTION = 0.6
DEFAULT_JITTER_FRACTION = 0.3
DEFAULT_SLIP_RATE_PER_M = 0.05
DEFAULT_SLIP_MEAN_FRACTION = 0.5


@dataclass(frozen=True)
class SlipEvent:
    index: int
    distance_m: float
    magnitude: float


@dataclass(frozen=True)
class ErrorPath:
    error: np.ndarray
    slip_events: tuple


class ChassisErrorModel:
    def __init__(self, generator, allocation, correlation_length_m=2.0,
                 scale=1.0, bias_fraction=DEFAULT_BIAS_FRACTION,
                 jitter_fraction=DEFAULT_JITTER_FRACTION,
                 slip_rate_per_m=DEFAULT_SLIP_RATE_PER_M,
                 slip_mean_fraction=DEFAULT_SLIP_MEAN_FRACTION,
                 axis_index=0):
        if axis_index:
            generator = np.random.Generator(
                generator.bit_generator.jumped(axis_index)
            )
        self._gen = generator
        self.allocation = float(allocation)
        self.correlation_length_m = float(correlation_length_m)
        self.scale = float(scale)
        self.bias_fraction = float(bias_fraction)
        self.jitter_fraction = float(jitter_fraction)
        self.slip_rate_per_m = float(slip_rate_per_m)
        self.slip_mean_fraction = float(slip_mean_fraction)

    def sample_path(self, step_m, n_steps):
        """Sample the error process over a path of n_steps * step_m metres.

        All random draws are scale-independent; magnitudes are linear in
        `scale`, so the same RNG root at a different scale yields an exactly
        proportional path (the x{0.5, 1, 2} sweep semantics).
        """
        sigma_env = self.scale * self.allocation / 2.0
        sigma_b = self.bias_fraction * sigma_env
        sigma_w = self.jitter_fraction * sigma_env
        slip_mean = self.slip_mean_fraction * sigma_env

        a = math.exp(-step_m / self.correlation_length_m)
        innov_scale = sigma_b * math.sqrt(1.0 - a * a)

        # Draw everything up front, scale-independently.
        n_bias = self._gen.standard_normal(n_steps)
        n_jitter = self._gen.standard_normal(n_steps)
        u_arrival = self._gen.random(n_steps)
        unit_mags = self._gen.exponential(1.0, n_steps)
        signs = np.where(self._gen.random(n_steps) < 0.5, -1.0, 1.0)

        p_slip = self.slip_rate_per_m * step_m
        slip_here = u_arrival < p_slip

        error = np.empty(n_steps)
        slips = []
        b = 0.0
        for k in range(n_steps):
            b = a * b + innov_scale * n_bias[k]
            if slip_here[k]:
                magnitude = signs[k] * unit_mags[k] * slip_mean
                b += magnitude
                slips.append(
                    SlipEvent(index=k, distance_m=k * step_m,
                              magnitude=magnitude)
                )
            error[k] = b + sigma_w * n_jitter[k]
        return ErrorPath(error=error, slip_events=tuple(slips))
