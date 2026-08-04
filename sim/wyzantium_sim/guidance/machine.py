"""Guidance state machine: IS §8 rows 1-5 responses, budgets, D-005 retry.

Table-driven in precedence order (documented at observe()); fully
deterministic — T6 has no RNG stream (#60) by design. Stage vocabulary is
the wire enum (D-004): acquire, outer_servo, inner_servo, contact_insert,
latched, abort, escalate.

Committed: the §8 row responses, #27/#28/#29/#55 values, the escalate
semantics ("refuse further attempts, send imagery, recommend a human
decision", IS §8 preamble), the abort_reason enum (WIRE_FORMAT).

Arbitrary code-level choices (spec gaps recorded 2026-08-04, chassis_error
precedent):
- HOLD_TIMEOUT_S: row 1's "escalate on timeout" has no committed number.
- AMBIGUITY_PERSIST_FRAMES: row 5's "persistent" has no committed count.
- POLICY_CLOSE_WITHOUT_OUTER = False: row 2's "if commanded policy allows"
  has no committed policy; conservative default.
- HANDOFF_RANGE_MM: row 4's "at handoff range" boundary.
- Time-budget exhaustion (#55/D-022) reuses abort_reason
  "attempt_budget_exhausted" — the enum has no time value; noted for a
  possible amendment.
- escalation.imagery_ref is a synthetic reference: Phase 1 renders no
  imagery (D-007), but the field is schema-required on escalate.
- retry aim correction subtracts last_contact_offset (sign convention);
  contact_offset_mm is the force-magnitude-weighted mean of contact-point
  lateral positions (ARCH §4 requires direction recovery; no committed
  formula).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

HOLD_TIMEOUT_S = 5.0
AMBIGUITY_PERSIST_FRAMES = 5
POLICY_CLOSE_WITHOUT_OUTER = False
INNER_RANGE_MM = 300.0    # IS §8 row 3: "inside 300 mm"
HANDOFF_RANGE_MM = 100.0
BACKOUT_MM = 300.0        # #28, D-005

_ESCALATION = {"imagery_ref": "sim://no-imagery-rendered-D007",
               "recommend": "human_decision"}


@dataclass(frozen=True)
class Decision:
    action: str               # continue|hold|reject_frame|abort_retry|escalate
    stage: str
    abort_reason: str = None
    escalation: dict = None


@dataclass(frozen=True)
class RetryPlan:
    start_mm: tuple
    aim_mm: tuple
    attempt: int


def contact_offset_mm(contacts) -> tuple:
    """Force-weighted mean lateral (y, z) of contact points — the D-005
    measured contact offset (direction recovery per ARCH §4)."""
    weights = [math.sqrt(sum(f * f for f in c.force_n)) for c in contacts]
    total = sum(weights)
    y = sum(w * c.pos_head_mm[1] for w, c in zip(weights, contacts)) / total
    z = sum(w * c.pos_head_mm[2] for w, c in zip(weights, contacts)) / total
    return (y, z)


def retry_plan(abort_head_center_mm, last_contact_offset_mm,
               attempt_n: int) -> RetryPlan:
    """D-005: back out 300 mm (+x, toward approach), correct the aim against
    the measured offset, increment the attempt index."""
    x, y, z = abort_head_center_mm
    off_y, off_z = last_contact_offset_mm
    return RetryPlan(
        start_mm=(x + BACKOUT_MM, y, z),
        aim_mm=(0.0, -off_y, -off_z),
        attempt=attempt_n + 1)


class GuidanceMachine:
    """One encounter's decision layer. Consumes target_state lines plus the
    caller's range/clock; emits Decisions. Attempt re-approaches themselves
    are kinematic runs (T5) parameterized by retry_plan()."""

    def __init__(self, conf_min: float = 0.85, attempts_max: int = 3,
                 time_budget_s: float = 900.0):
        self.conf_min = conf_min
        self.attempts_max = attempts_max
        self.time_budget_s = time_budget_s
        self.attempt_n = 1
        self.stage = "acquire"
        self._ambiguity_streak = 0
        self._hold_since = None

    def _escalate(self, reason: str) -> Decision:
        self.stage = "escalate"
        return Decision(action="escalate", stage=self.stage,
                        abort_reason=reason, escalation=dict(_ESCALATION))

    def _abort_retry(self, reason: str) -> Decision:
        self.attempt_n += 1
        if self.attempt_n > self.attempts_max:
            return self._escalate("attempt_budget_exhausted")
        self.stage = "abort"
        return Decision(action="abort_retry", stage=self.stage,
                        abort_reason=reason)

    def observe(self, line: dict, range_mm: float, t_s: float) -> Decision:
        # Precedence: budgets → row 5 → rows 3/4 → row 2 → row 1 → continue.
        if t_s > self.time_budget_s:
            return self._escalate("attempt_budget_exhausted")
        if self.attempt_n > self.attempts_max:
            return self._escalate("attempt_budget_exhausted")

        tags = line.get("tags") or []
        conf = line.get("conf", 0.0)

        # IS §8 row 5: ambiguity flip
        if any(t.get("ambiguity_flag") for t in tags):
            self._ambiguity_streak += 1
            if self._ambiguity_streak >= AMBIGUITY_PERSIST_FRAMES:
                self._ambiguity_streak = 0
                return self._abort_retry("ambiguity_persistent")
            return Decision(action="reject_frame", stage=self.stage)
        self._ambiguity_streak = 0

        # IS §8 rows 3/4: inner ring below the commit minimum
        if range_mm <= INNER_RANGE_MM:
            inner = [t for t in tags if t.get("id") != 0]
            if len(inner) < 2:
                if (not inner and range_mm <= HANDOFF_RANGE_MM
                        and line.get("pose_source") in ("outer_tag",
                                                        "multi_tag_fused")
                        and conf >= self.conf_min):
                    # row 4: outer pose OK, ring dead — never attempt (D-013)
                    return self._escalate("inner_ring_absent")
                return self._abort_retry("inner_ring_absent")

        # IS §8 row 2: no outer detection at expected range
        if line.get("pose_source") == "none" and not tags:
            if not POLICY_CLOSE_WITHOUT_OUTER:
                return self._escalate("low_confidence")

        # IS §8 row 1: degraded confidence — hold, reacquire, timeout
        if conf < self.conf_min:
            if self._hold_since is None:
                self._hold_since = t_s
            if t_s - self._hold_since > HOLD_TIMEOUT_S:
                return self._escalate("low_confidence")
            return Decision(action="hold", stage=self.stage)
        self._hold_since = None

        self.stage = "outer_servo" if range_mm > 200.0 else "inner_servo"
        return Decision(action="continue", stage=self.stage)
