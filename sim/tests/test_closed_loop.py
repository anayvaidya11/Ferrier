"""D-037 closed-loop walker: holds freeze traversal, resume continues,
aborts end the attempt at the held position, ties go to grid arrivals."""

from dataclasses import dataclass

from wyzantium_sim.kinematic import closed_loop


@dataclass(frozen=True)
class FakePoint:
    name: str
    seg_dt_s: float


@dataclass(frozen=True)
class FakeDecision:
    action: str


def make_frame_cb(decisions):
    seen = []
    remaining = list(decisions)

    def on_frame(t, point):
        seen.append((round(t, 6), point.name))
        action = remaining.pop(0) if remaining else "continue"
        return FakeDecision(action)

    return on_frame, seen


def make_truth_cb():
    seen = []

    def on_truth(t, point):
        seen.append((round(t, 6), point.name))

    return on_truth, seen


def path(n=4, seg=1.0):
    return tuple(FakePoint(f"p{k}", 0.0 if k == 0 else seg)
                 for k in range(n))


class TestAllContinue:
    def test_arrivals_at_plain_cumulative_times(self):
        on_frame, frames = make_frame_cb([])
        on_truth, truths = make_truth_cb()
        res = closed_loop.walk(path(4), t0_s=10.0, rate_hz=2.0,
                               on_truth=on_truth, on_frame=on_frame)
        assert res.ended == "path_end"
        assert res.t_end_s == 13.0
        assert truths == [(10.0, "p0"), (11.0, "p1"),
                          (12.0, "p2"), (13.0, "p3")]
        # frames at 10.0/10.5/11.0(tie→after p1 arrival)/11.5/12.0/12.5;
        # ZOH point is the last arrival at each frame time
        assert frames[0] == (10.0, "p0")
        assert (11.0, "p1") in frames and (12.5, "p2") in frames

    def test_tie_goes_to_grid_arrival_first(self):
        # frame and arrival both at t=11.0: the frame must see p1, not p0
        on_frame, frames = make_frame_cb([])
        on_truth, _ = make_truth_cb()
        closed_loop.walk(path(3), t0_s=10.0, rate_hz=1.0,
                         on_truth=on_truth, on_frame=on_frame)
        assert (11.0, "p1") in frames
        assert (11.0, "p0") not in frames


class TestHold:
    def test_hold_freezes_position_and_shifts_arrivals(self):
        # rate 2 Hz; hold at the first frame (t=10.0) for 3 frames (1.5 s),
        # then continue. p1's arrival shifts from 11.0 to 12.5.
        on_frame, frames = make_frame_cb(["hold", "hold", "hold"])
        on_truth, truths = make_truth_cb()
        res = closed_loop.walk(path(2), t0_s=10.0, rate_hz=2.0,
                               on_truth=on_truth, on_frame=on_frame)
        assert res.ended == "path_end"
        assert truths == [(10.0, "p0"), (12.5, "p1")]
        # every frame during the hold saw the frozen position p0
        held = [name for t, name in frames if t < 12.5]
        assert set(held) == {"p0"}

    def test_resume_consumes_remaining_segment_only(self):
        # traversal up to the first frame consumed 0.0 s (frame at t0);
        # hold 1 frame at t=10.5 after 0.5 s of travel: remaining 0.5 s
        # completes at 11.5 (10.5 hold-frame → resume at 11.0 frame → +0.5)
        on_frame, _ = make_frame_cb(["continue", "hold"])
        on_truth, truths = make_truth_cb()
        closed_loop.walk(path(2), t0_s=10.0, rate_hz=2.0,
                         on_truth=on_truth, on_frame=on_frame)
        assert truths == [(10.0, "p0"), (11.5, "p1")]


class TestAbort:
    def test_abort_ends_at_held_position_and_time(self):
        on_frame, _ = make_frame_cb(["hold", "abort_retry"])
        on_truth, _ = make_truth_cb()
        res = closed_loop.walk(path(4), t0_s=0.0, rate_hz=2.0,
                               on_truth=on_truth, on_frame=on_frame)
        assert res.ended == "aborted"
        assert res.decision.action == "abort_retry"
        assert res.t_end_s == 0.5
        assert res.end_point.name == "p0"

    def test_escalate_ends_walk(self):
        on_frame, _ = make_frame_cb(["continue", "escalate"])
        on_truth, _ = make_truth_cb()
        res = closed_loop.walk(path(4), t0_s=0.0, rate_hz=2.0,
                               on_truth=on_truth, on_frame=on_frame)
        assert res.ended == "aborted"
        assert res.decision.action == "escalate"
