"""#37/#38: perception rate and latency → t_capture / t_emit."""
import numpy as np


def frame_times(rate_hz, t0, n):
    return t0 + np.arange(n) / float(rate_hz)


def emit_time(t_capture, latency_ms):
    return t_capture + latency_ms / 1000.0
