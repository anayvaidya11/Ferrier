"""D-037 — closed-loop attempt walker: holds are physically real.
D-045 — frames are consumed at ARRIVAL: capture at the camera cadence,
delivery latency_s later, so the swept #38 latency axis is behaviorally
live (the vehicle covers ground during the delay; walls, holds, and
budgets run on the delayed clock).

Walks a SpatialPath against sim time. The vehicle traverses segments at
their commanded speeds; a "hold" decision freezes traversal (v = 0) while
frames keep being captured and delivered — stop, stare, reacquire; a
"continue" (or "reject_frame") resumes; "abort_retry"/"escalate" end the
attempt at the position held at DELIVERY time. Truth is zero-order-held at
the last grid point (pre-existing T8 behavior); a frame's CONTENT snapshots
the capture-time held point (the evidence describes capture geometry;
code-level choice, labeled in D-045), and its decision applies at capture +
latency_s. With latency above the frame period several frames are in
flight at once (FIFO). Event order on ties: grid arrival, then capture,
then delivery — so latency_s = 0 reproduces the former capture-time
semantics exactly. Frames still in flight when the path ends are dropped
(the handoff transitions the stage; labeled).

Determinism: everything here is a pure function of the path, t0, the rate,
latency, and the callbacks' decisions — no clocks, no RNG. Pauses shift
delivery-driven traversal; they never change the spatial realization
(D-019 error is indexed by arc length — D-037).
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class WalkResult:
    ended: str            # "path_end" | "aborted"
    t_end_s: float
    decision: object      # the terminal Decision when aborted, else None
    end_point: object     # PathPoint the vehicle was at when the walk ended


def walk(points, *, t0_s, rate_hz, on_truth, on_frame,
         latency_s: float = 0.0) -> WalkResult:
    """on_truth(t_s, point) fires at every grid arrival (sim_truth cadence,
    #59); on_frame(t_capture_s, point, t_deliver_s) fires when a frame is
    DELIVERED (capture + latency_s), with the point zero-order-held at its
    capture instant, and returns the guidance Decision."""
    t = float(t0_s)
    on_truth(t, points[0])
    last = points[0]

    j = 0                       # next capture index
    i = 1
    rem = points[i].seg_dt_s if i < len(points) else None
    holding = False
    pending = deque()           # (t_capture, capture-held point) FIFO

    while True:
        next_capture = t0_s + j / rate_hz
        next_delivery = pending[0][0] + latency_s if pending else None
        arrival = (t + rem) if (rem is not None and not holding) else None

        # Earliest event wins; ties resolve arrival → capture → delivery
        # (the T8 strict-< rule generalized; latency 0 ⇒ old semantics).
        candidates = [c for c in (arrival, next_capture, next_delivery)
                      if c is not None]
        t_next = min(candidates)

        if arrival is not None and arrival == t_next:
            t = arrival
            on_truth(t, points[i])
            last = points[i]
            i += 1
            if i >= len(points):
                return WalkResult("path_end", t, None, last)
            rem = points[i].seg_dt_s
            continue

        if arrival is not None:
            rem -= t_next - t       # traversal consumed up to this event
        t = t_next

        if t == next_capture and (next_delivery is None
                                  or next_capture <= next_delivery):
            pending.append((next_capture, last))
            j += 1
            continue

        t_capture, cap_point = pending.popleft()
        d = on_frame(t_capture, cap_point, t)
        if d.action in ("abort_retry", "escalate"):
            return WalkResult("aborted", t, d, last)
        holding = d.action == "hold"
