"""#43–#45: sensor dropout, lens contamination, rain proxy.

Dropout (#43, ASSUMED model): per-frame Bernoulli(p) burst *starts*; each
start drops a run of frames with geometric length, mean 5. Contamination
(#44, EXT) and rain (#45, EXT — no literature found) are linear detection
multipliers over their committed sweep ranges.
"""


class FrameDropout:
    def __init__(self, generator, p, burst_mean=5.0):
        self._gen = generator
        self.p = float(p)
        self.burst_mean = float(burst_mean)
        self._remaining = 0

    def sample(self):
        """True if this frame is dropped."""
        if self._remaining > 0:
            self._remaining -= 1
            return True
        if self.p > 0.0 and self._gen.random() < self.p:
            # Geometric (support >= 1) with mean burst_mean.
            self._remaining = int(self._gen.geometric(1.0 / self.burst_mean))
            self._remaining -= 1  # this frame is the first of the burst
            return True
        return False


def contamination_factor(aperture_fraction):
    return 1.0 - float(aperture_fraction)


def rain_factor(rain_fraction):
    return 1.0 - float(rain_fraction)
