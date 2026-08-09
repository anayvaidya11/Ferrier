"""T6 — confidence gate + guidance state machine.

Gate (PHASE1_PLAN §4): table-driven — commit predicate exact; IS §8 rows 1-5
stream patterns → specified responses; retry geometry; budget → escalate;
heading ∈ ±20°.

Double-entry transcription of the committed rules:
  #30 commit ⟺ pose_source = multi_tag_fused ∧ stage = inner_servo ∧
      conf ≥ conf_min_attempt (#29 default 0.85; sweep is the deliverable,
      D-017). The gate enforces the strict H-08/IS §10 reading: ≥2 INNER
      tags (id != 0) — the injector emits multi_tag_fused for any ≥2 tags,
      a flagged inconsistency.
  D-018 (#24): heading within a ±20° cone of the stud +X axis, computed
      from T_head_stud alone (anti-parallel nominal = 0°).
  D-005 (#28): back out 300 mm, apply last_contact_offset, attempt.n + 1.
  #27 attempts default 3; #55 time budget default 15 min → escalate.
  IS §8 rows 1-5 responses as quoted in INTERFACE_SPEC §8.
"""

import math

import pytest

from wyzantium_sim import frames
from wyzantium_sim.guidance import gate, machine

CONF_MIN = 0.85          # #29 default
SECTOR_DEG = 20.0        # #24 / D-018
BACKOUT_MM = 300.0       # #28 / D-005
ATTEMPTS_MAX = 3         # #27 default
TIME_BUDGET_S = 15 * 60  # #55 default

Q_NOMINAL = (0.0, 0.0, 1.0, 0.0)


def q_about_y(deg):
    h = math.radians(deg) / 2.0
    qy = (math.cos(h), 0.0, math.sin(h), 0.0)
    return frames.Pose(t=(0, 0, 0), q=qy).compose(
        frames.Pose(t=(0, 0, 0), q=Q_NOMINAL)).q


def line(**overrides):
    """A commit-eligible target_state line (WIRE_FORMAT example shape)."""
    base = {
        "v": 1, "type": "target_state", "t_capture": 10.0, "t_emit": 10.01,
        "pose": {"t": [0.12, 0.0, 0.0], "q": list(Q_NOMINAL)},
        "pose_cov": [1e-6] * 21,
        "pose_source": "multi_tag_fused", "conf": 0.90,
        "tags": [{"id": 1, "reproj_err": 0.4, "ambiguity_flag": False,
                  "ambiguity_ratio": 1.0},
                 {"id": 2, "reproj_err": 0.5, "ambiguity_flag": False,
                  "ambiguity_ratio": 1.0}],
        "stage": "inner_servo",
    }
    base.update(overrides)
    return base


class TestCommitPredicate:
    def test_nominal_line_commits(self):
        ok, _ = gate.commit_allowed(line(), conf_min=CONF_MIN)
        assert ok

    @pytest.mark.parametrize("field,value,why", [
        ("pose_source", "inner_ring", "pose_source"),
        ("pose_source", "outer_tag", "pose_source"),
        ("pose_source", "contact_force", "pose_source"),
        ("stage", "outer_servo", "stage"),
        ("conf", 0.84, "conf"),
    ], ids=["src-inner", "src-outer", "src-contact", "stage", "conf"])
    def test_each_conjunct_is_necessary(self, field, value, why):
        ok, reason = gate.commit_allowed(line(**{field: value}),
                                         conf_min=CONF_MIN)
        assert not ok
        assert why in reason

    def test_conf_exactly_at_threshold_commits(self):
        ok, _ = gate.commit_allowed(line(conf=0.85), conf_min=CONF_MIN)
        assert ok

    def test_two_inner_tags_required_not_just_any_two(self):
        # H-08/IS §10: outer (id 0) + one inner must NOT satisfy the gate
        # even though the injector labels it multi_tag_fused
        tags = [{"id": 0, "reproj_err": 0.4, "ambiguity_flag": False,
                 "ambiguity_ratio": 1.0},
                {"id": 3, "reproj_err": 0.5, "ambiguity_flag": False,
                 "ambiguity_ratio": 1.0}]
        ok, reason = gate.commit_allowed(line(tags=tags), conf_min=CONF_MIN)
        assert not ok
        assert "inner" in reason

    def test_missing_required_field_rejects(self):
        bad = line()
        del bad["conf"]
        ok, reason = gate.commit_allowed(bad, conf_min=CONF_MIN)
        assert not ok

    def test_pose_absent_cannot_commit(self):
        # WIRE_FORMAT: absent pose = "guidance must not act on position"
        no_pose = line()
        del no_pose["pose"]
        ok, reason = gate.commit_allowed(no_pose, conf_min=CONF_MIN)
        assert not ok
        assert "pose" in reason


class TestHeadingSector:
    def test_nominal_antiparallel_is_zero(self):
        assert gate.heading_misalign_deg(Q_NOMINAL) == pytest.approx(0.0,
                                                                     abs=1e-9)

    @pytest.mark.parametrize("deg,ok", [(15.0, True), (19.9, True),
                                        (20.1, False), (25.0, False)],
                             ids=["15", "19.9", "20.1", "25"])
    def test_sector_boundary(self, deg, ok):
        q = q_about_y(deg)
        assert gate.heading_misalign_deg(q) == pytest.approx(deg, abs=1e-6)
        allowed, reason = gate.commit_allowed(
            line(pose={"t": [0.12, 0.0, 0.0], "q": list(q)}),
            conf_min=CONF_MIN)
        assert allowed == ok
        if not ok:
            assert "heading" in reason


def make_machine(**overrides):
    defaults = dict(conf_min=CONF_MIN, attempts_max=ATTEMPTS_MAX,
                    time_budget_s=TIME_BUDGET_S)
    defaults.update(overrides)
    return machine.GuidanceMachine(**defaults)


class TestRow1OuterOcclusion:
    def test_above_threshold_continues(self):
        m = make_machine()
        d = m.observe(line(stage="outer_servo", pose_source="outer_tag",
                           conf=0.90), range_mm=1500.0, t_s=1.0)
        assert d.action == "continue"

    def test_outer_low_conf_detection_continues(self):
        # D-035: at outer range a detected frame is tracking evidence —
        # the commit-grade wall does not pre-empt a reversible approach.
        m = make_machine()
        d = m.observe(line(stage="outer_servo", pose_source="outer_tag",
                           conf=0.40,
                           degradation={"occlusion_est": 0.6}),
                      range_mm=1500.0, t_s=1.0)
        assert d.action == "continue"

    def test_inner_below_threshold_holds_and_reacquires(self):
        m = make_machine()
        d = m.observe(line(conf=0.40), range_mm=250.0, t_s=1.0)
        assert d.action == "hold"

    def test_inner_hold_timeout_escalates(self):
        m = make_machine()
        t = 1.0
        d = m.observe(line(conf=0.40), range_mm=250.0, t_s=t)
        while d.action == "hold":
            t += 0.1
            d = m.observe(line(conf=0.40), range_mm=250.0, t_s=t)
        assert d.action == "escalate"
        assert d.abort_reason == "low_confidence"
        assert t - 1.0 <= machine.HOLD_TIMEOUT_S + 0.2


class TestRow2OuterDestroyed:
    """D-034: row 2 shares row 1's hold wall — a single no-detection frame
    holds (a #43 blip is not a destroyed tag); sustained darkness past
    HOLD_TIMEOUT_S escalates. Policy default still forbids closing without
    the outer tag."""

    def _dark(self):
        return dict(stage="outer_servo", pose_source="none", conf=0.0,
                    pose=None, tags=None)

    def test_single_dark_frame_holds_not_escalates(self):
        m = make_machine()
        d = m.observe(line(**self._dark()), range_mm=2500.0, t_s=1.0)
        assert d.action == "hold"

    def test_sustained_darkness_escalates_with_imagery(self):
        m = make_machine()
        t = 1.0
        d = m.observe(line(**self._dark()), range_mm=2500.0, t_s=t)
        while d.action == "hold":
            t += 1.0 / 30.0
            d = m.observe(line(**self._dark()), range_mm=2500.0, t_s=t)
        assert d.action == "escalate"
        assert d.abort_reason == "low_confidence"
        assert d.escalation["recommend"] == "human_decision"
        assert t - 1.0 <= machine.HOLD_TIMEOUT_S + 0.2

    def test_detection_resets_dark_window(self):
        m = make_machine()
        t = 1.0
        for _ in range(60):  # 2 s dark — inside the wall throughout
            d = m.observe(line(**self._dark()), range_mm=2500.0, t_s=t)
            assert d.action == "hold"
            t += 1.0 / 30.0
        d = m.observe(line(stage="outer_servo", pose_source="outer_tag",
                           conf=0.95), range_mm=2500.0, t_s=t)
        assert d.action == "continue"  # detection resets the window
        t += 1.0 / 30.0
        for _ in range(120):  # 4 s dark after reset — still inside the wall
            d = m.observe(line(**self._dark()), range_mm=2500.0, t_s=t)
            assert d.action == "hold"
            t += 1.0 / 30.0


class TestRow3InnerOccluded:
    def _one_inner(self):
        return line(stage="inner_servo", pose_source="inner_ring",
                    conf=0.90,
                    tags=[{"id": 2, "reproj_err": 0.5,
                           "ambiguity_flag": False, "ambiguity_ratio": 1.0}])

    def test_single_marginal_ring_frame_only_rejects(self):
        # Per-frame tag detection is stochastic; one 33 ms frame below the
        # two-tag minimum is not an occluded ring. Like rows 1/5, the
        # row-3 response requires persistence (T8 composition finding,
        # 2026-08-04).
        m = make_machine()
        d = m.observe(self._one_inner(), range_mm=250.0, t_s=5.0)
        assert d.action == "reject_frame"
        assert m.attempt_n == 1

    def test_sustained_ring_absence_aborts_and_retries(self):
        # D-036: absence is a time window on the shared wall, not a
        # frame count.
        m = make_machine()
        t = 5.0
        d = m.observe(self._one_inner(), range_mm=250.0, t_s=t)
        while d.action == "reject_frame":
            t += 1.0 / 30.0
            d = m.observe(self._one_inner(), range_mm=250.0, t_s=t)
        assert d.action == "abort_retry"
        assert d.abort_reason == "inner_ring_absent"
        assert m.attempt_n == 2
        assert t - 5.0 <= machine.HOLD_TIMEOUT_S + 0.2

    def test_good_ring_frame_resets_the_window(self):
        m = make_machine()
        t = 5.0
        for _ in range(120):   # 4 s of ring gaps — inside the wall
            d = m.observe(self._one_inner(), range_mm=250.0, t_s=t)
            assert d.action == "reject_frame"
            t += 1.0 / 30.0
        m.observe(line(), range_mm=250.0, t_s=t)   # two inner tags reset
        t += 1.0 / 30.0
        for _ in range(120):   # 4 s more after reset — still inside
            d = m.observe(self._one_inner(), range_mm=250.0, t_s=t)
            assert d.action == "reject_frame"
            t += 1.0 / 30.0
        assert m.attempt_n == 1

    def test_budget_exhaustion_escalates(self):
        m = make_machine()
        t = 5.0
        d = m.observe(self._one_inner(), range_mm=250.0, t_s=t)
        for _ in range(int(30 * machine.HOLD_TIMEOUT_S * (ATTEMPTS_MAX + 2))):
            if d.action == "escalate":
                break
            t += 1.0 / 30.0
            d = m.observe(self._one_inner(), range_mm=250.0, t_s=t)
        assert d.action == "escalate"
        assert d.abort_reason == "attempt_budget_exhausted"

    def test_below_handoff_boundary_ring_jitter_never_aborts(self):
        # D-004 stage 3 is force-guided (pose_source contact_force):
        # below the handoff boundary, terminal foreshortening starving
        # the ring count is not an occluded ring — frames are rejected,
        # the insertion is not aborted, even past the wall (T8
        # composition finding, 2026-08-04). Row 4 (ring dead + outer
        # pose OK) still escalates.
        m = make_machine()
        t = 8.0
        for _ in range(int(3 * 30 * machine.HOLD_TIMEOUT_S)):
            d = m.observe(self._one_inner(), range_mm=60.0, t_s=t)
            assert d.action == "reject_frame"
            t += 1.0 / 30.0
        assert m.attempt_n == 1


class TestRow4InnerDestroyed:
    def test_zero_inner_at_handoff_range_never_attempts(self):
        m = make_machine()
        t = 8.0
        d = m.observe(line(stage="inner_servo", pose_source="outer_tag",
                           conf=0.92,
                           tags=[{"id": 0, "reproj_err": 0.3,
                                  "ambiguity_flag": False,
                                  "ambiguity_ratio": 1.0}]),
                      range_mm=60.0, t_s=t)
        while d.action == "reject_frame":
            t += 1.0 / 30.0
            d = m.observe(line(stage="inner_servo", pose_source="outer_tag",
                               conf=0.92,
                               tags=[{"id": 0, "reproj_err": 0.3,
                                      "ambiguity_flag": False,
                                      "ambiguity_ratio": 1.0}]),
                          range_mm=60.0, t_s=t)
        assert d.action == "escalate"
        assert d.abort_reason == "inner_ring_absent"
        assert m.attempt_n == 1, "D-013: no insertion attempt is consumed"
        assert t - 8.0 <= machine.HOLD_TIMEOUT_S + 0.2


class TestRow5AmbiguityFlip:
    def _flagged(self):
        return line(tags=[{"id": 1, "reproj_err": 0.6,
                           "ambiguity_flag": True, "ambiguity_ratio": 0.6},
                          {"id": 2, "reproj_err": 0.5,
                           "ambiguity_flag": False, "ambiguity_ratio": 1.0}])

    def test_flagged_frame_is_rejected(self):
        m = make_machine()
        d = m.observe(self._flagged(), range_mm=150.0, t_s=5.0)
        assert d.action == "reject_frame"

    def test_persistent_ambiguity_aborts(self):
        m = make_machine()
        d = None
        for _ in range(machine.AMBIGUITY_PERSIST_FRAMES):
            d = m.observe(self._flagged(), range_mm=150.0, t_s=5.0)
        assert d.action == "abort_retry"
        assert d.abort_reason == "ambiguity_persistent"

    def test_clean_frame_resets_the_streak(self):
        m = make_machine()
        for _ in range(machine.AMBIGUITY_PERSIST_FRAMES - 1):
            m.observe(self._flagged(), range_mm=150.0, t_s=5.0)
        m.observe(line(), range_mm=150.0, t_s=5.1)
        d = m.observe(self._flagged(), range_mm=150.0, t_s=5.2)
        assert d.action == "reject_frame"

    def test_outer_range_ambiguity_rejects_but_never_aborts(self):
        # Row 5's remedy is "require multi-tag or oblique confirmation" —
        # impossible beyond inner range with one coplanar tag, where the
        # H08 model makes face-on ambiguity structural (ratio < 1 beyond
        # ~1.2 m). The streak-abort is therefore scoped to inner range;
        # far-field flagged frames are rejected, never aborted (T8
        # composition finding, 2026-08-04).
        m = make_machine()
        for _ in range(3 * machine.AMBIGUITY_PERSIST_FRAMES):
            d = m.observe(self._flagged(), range_mm=2000.0, t_s=5.0)
            assert d.action == "reject_frame"
        assert m.attempt_n == 1


class TestBudgets:
    def test_time_budget_escalates(self):
        m = make_machine()
        d = m.observe(line(), range_mm=1500.0, t_s=TIME_BUDGET_S + 1.0)
        assert d.action == "escalate"
        assert d.abort_reason == "attempt_budget_exhausted"


class TestRetryGeometry:
    def test_backout_and_offset_applied(self):
        # WIRE_FORMAT example: measured contact offset 19 mm y, 8 mm z
        plan = machine.retry_plan(
            abort_head_center_mm=(20.0, 15.0, -4.0),
            last_contact_offset_mm=(19.0, 8.0),
            attempt_n=1)
        assert plan.attempt == 2
        assert plan.start_mm[0] == pytest.approx(20.0 + BACKOUT_MM)
        assert plan.start_mm[1:] == pytest.approx((15.0, -4.0))
        # aim corrected against the measured offset
        assert plan.aim_mm[1] == pytest.approx(-19.0)
        assert plan.aim_mm[2] == pytest.approx(-8.0)

    def test_offset_from_contacts_is_force_weighted(self):
        from wyzantium_sim.contact.engine import ContactPoint
        cps = (ContactPoint(pos_head_mm=(-10.0, 30.0, 0.0),
                            normal=(1.0, 0.0, 0.0),
                            force_n=(30.0, 0.0, 0.0)),
               ContactPoint(pos_head_mm=(-10.0, 0.0, 10.0),
                            normal=(1.0, 0.0, 0.0),
                            force_n=(10.0, 0.0, 0.0)))
        off = machine.contact_offset_mm(cps)
        assert off[0] == pytest.approx(22.5)  # (30*30 + 0*10) / 40
        assert off[1] == pytest.approx(2.5)   # (0*30 + 10*10) / 40


class TestUnderlyingAbort:
    # T9 review fix: _abort_retry on the final allowed attempt escalates
    # attempt_budget_exhausted, but the proximate perception abort must
    # survive on Decision.underlying_abort — otherwise the classifier
    # never sees the reason and misfiles the trial (clean_miss or a
    # stale row instead of IS8-5/IS8-3)

    def _flagged(self):
        return line(tags=[{"id": 1, "reproj_err": 0.4,
                           "ambiguity_flag": True, "ambiguity_ratio": 1.0},
                          {"id": 2, "reproj_err": 0.5,
                           "ambiguity_flag": False,
                           "ambiguity_ratio": 1.0}])

    def test_final_attempt_abort_reason_rides_the_escalation(self):
        m = make_machine(attempts_max=1)
        d = None
        for _ in range(machine.AMBIGUITY_PERSIST_FRAMES):
            d = m.observe(self._flagged(), range_mm=150.0, t_s=5.0)
        assert d.action == "escalate"
        assert d.abort_reason == "attempt_budget_exhausted"
        assert d.underlying_abort == "ambiguity_persistent"

    def test_time_budget_escalation_has_no_underlying_abort(self):
        m = make_machine()
        d = m.observe(line(), range_mm=400.0, t_s=TIME_BUDGET_S + 1.0)
        assert d.action == "escalate"
        assert d.underlying_abort is None

    def test_non_final_abort_retry_is_unchanged(self):
        m = make_machine(attempts_max=3)
        d = None
        for _ in range(machine.AMBIGUITY_PERSIST_FRAMES):
            d = m.observe(self._flagged(), range_mm=150.0, t_s=5.0)
        assert d.action == "abort_retry"
        assert d.abort_reason == "ambiguity_persistent"
        assert d.underlying_abort is None
