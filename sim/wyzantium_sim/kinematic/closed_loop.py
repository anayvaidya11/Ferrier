"""D-037 — closed-loop attempt walker: holds are physically real.

Walks a SpatialPath against sim time. The vehicle traverses segments at
their commanded speeds; a "hold" decision freezes traversal (v = 0) while
perception frames keep arriving at the cadence — stop, stare, reacquire; a
"continue" (or "reject_frame") resumes; "abort_retry"/"escalate" end the
attempt at the held position. Truth is zero-order-held at the last grid
point (pre-existing T8 behavior); frames strictly between grid arrivals see
that point, and a frame tying a grid arrival yields to the arrival (the T8
strict-< rule). Frame times are t0 + j/rate, matching timing.frame_times.

Determinism: everything here is a pure function of the path, t0, the rate,
and the callbacks' decisions — no clocks, no RNG. Pauses shift arrival
times; they never change the spatial realization (D-019 error is indexed by
arc length; a stationary vehicle does not accrue slip — D-037).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WalkResult:
    ended: str            # "path_end" | "aborted"
    t_end_s: float
    decision: object      # the terminal Decision when aborted, else None
    end_point: object     # PathPoint the vehicle was at when the walk ended


def walk(points, *, t0_s, rate_hz, on_truth, on_frame) -> WalkResult:
    """on_truth(t_s, point) fires at every grid arrival (sim_truth cadence,
    #59); on_frame(t_s, point) fires at every perception frame with the
    zero-order-held point and returns the guidance Decision."""
    t = float(t0_s)
    on_truth(t, points[0])
    last = points[0]

    j = 0
    next_frame_t = t0_s + j / rate_hz
    i = 1
    rem = points[i].seg_dt_s if i < len(points) else None
    holding = False

    while True:
        arrival = (t + rem) if (rem is not None and not holding) else None
        if arrival is not None and arrival <= next_frame_t:
            t = arrival
            on_truth(t, points[i])
            last = points[i]
            i += 1
            if i >= len(points):
                return WalkResult("path_end", t, None, last)
            rem = points[i].seg_dt_s
            continue

        if arrival is not None:
            rem -= next_frame_t - t     # traversal consumed up to the frame
        t = next_frame_t
        d = on_frame(t, last)
        j += 1
        next_frame_t = t0_s + j / rate_hz
        if d.action in ("abort_retry", "escalate"):
            return WalkResult("aborted", t, d, last)
        holding = d.action == "hold"
