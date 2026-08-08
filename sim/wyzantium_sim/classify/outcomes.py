"""T9 — table-driven trace→outcome mapping under the committed precedence.

Contract (PHASE1_PLAN §2): success | IS8-1..18 | clean_miss (D-030, D-033),
documented precedence order, one row per trial; an unmatchable trace raises
UnclassifiedFailure — the recorded-amendment path, never a guess.

The order of TABLE transcribes FAILURE_TAXONOMY.md §"Classifier precedence"
row-for-row (test-enforced). First match wins, which is what makes the
outcome unique per trial (FAILURE_TAXONOMY: exactly one row). IS8-15
(comms loss) is nominal per IS §8 row 15 / REQ-005 / D-030 and is
deliberately absent from the table; it stays in the wire enum for schema
stability.

Never-a-guess is enforced up front as well as by fall-through: classify()
refuses any escalation reason or abort reason outside the sets the table
was written against, even when the attempt history would otherwise fit a
shape row — a future GuidanceMachine reason lands on the amendment path,
not on a plausible row.

Double-entry transcription:
  D-022 / D-020: success ⟺ any latch within the attempt budget; t ≤ T is
      structural (the trial loop never runs past budget).
  D-030: clean_miss is the residual — (a) holds because the success row
      failed, (d) holds by table position; (b) and (c) are checked here.
      Clause (c)'s two arms (crossed at r > 160 mm; ended on budget before
      the plane) both leave handoff_reached False, which is the check.
      The refusal path is never clean_miss (it classifies IS8-1).
  D-033: IS8-18 ⟺ a contact-stage timeout (AttemptEnd.timed_out) — the
      attempt crossed the plane and the budget, not the mechanism, ended
      the insertion.
  H-16 / IS §8 row 16: false_capture = a striking leg's own latch, emitted
      only with IS8-16.

Everything here is pure and RNG-free: same trace, same outcome, so replay
classification is byte-stable. Fields marked "no Phase 1 producer" exist so
the table is total before their producers arrive; today's sim never sets
them (no fault injection, wrench profiling, constellation check, ID-block
check, or post-tow model).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

# The reasons the table was written against. Anything else raises — the
# never-a-guess rule made mechanical (a new machine reason or abort enum
# value must extend the taxonomy before it gets an outcome).
_KNOWN_ESCALATIONS = (None, "attempt_budget_exhausted",
                      "ambiguity_persistent", "inner_ring_absent",
                      "low_confidence")
_KNOWN_ABORTS = (None, "low_confidence", "ambiguity_persistent",
                 "inner_ring_absent", "jam_detected")


@dataclass(frozen=True)
class AttemptEnd:
    """How one attempt ended, in the order the trial ran them.

    Per-attempt (not aggregate) because D-030 clause (c) quantifies over
    every attempt.
    """
    handoff_reached: bool = False
    miss_reason: str | None = None   # KinematicResult: r_gt_annulus | no_crossing
    refused: bool = False            # gate refusal by insertion onset (D-013)
    abort_reason: str | None = None  # this attempt's abort, if any (WIRE_FORMAT)
    contact: bool = False            # any contact point this attempt
    lip_strike: bool = False         # lip-band contact pre-capture-plane (#12)
    latched: bool = False            # D-020 predicate confirmed (#54)
    jam: bool = False                # #62 criterion fired
    full_stroke: bool = False        # D-020 position (depth ∧ radial) ever held
    timed_out: bool = False          # contact budget expired (IS8-18, D-033)


@dataclass(frozen=True)
class Trace:
    """What the classifier consumes: one per trial.

    outer_tag_seen has no default on purpose: defaulting it to the nominal
    value would let a constructor that forgets the field silently make
    IS8-2 unreachable — every caller decides explicitly.
    """
    outer_tag_seen: bool             # any ID-0 detection (IS8-2 vs IS8-1)
    attempts: tuple = ()             # tuple[AttemptEnd, ...]
    escalation_reason: str | None = None
    # no Phase 1 producer:
    stud_wrench_inconsistent: bool = False    # IS8-6
    no_contact_at_expected_depth: bool = False  # IS8-7
    constellation_violated: bool = False      # IS8-8
    insertion_force_spike_blunt: bool = False  # IS8-9
    latch_confirm_intermittent: bool = False  # IS8-11
    release_failed: bool = False              # IS8-12
    plate_skew_exceeded: bool = False         # IS8-13
    wrong_id_persistent: bool = False         # IS8-14


class UnclassifiedFailure(ValueError):
    """A trace no precedence row names — extend §8 by recorded amendment."""


def _last_abort(tr: Trace) -> str | None:
    """The proximate cause when the budget exhausts: the last abort seen."""
    for a in reversed(tr.attempts):
        if a.abort_reason is not None:
            return a.abort_reason
    return None


def _low_confidence_shape(tr: Trace) -> bool:
    # the two producible IS8-1 signals: terminal low-confidence escalation
    # or a gate refusal (refusal attempts also carry abort_reason
    # "low_confidence", so a last-abort disjunct would be dead code)
    return (tr.escalation_reason == "low_confidence"
            or any(a.refused for a in tr.attempts))


def _clean_miss(tr: Trace) -> bool:
    # (a) holds: the success row failed. (d) holds: rows 1-18 failed.
    if tr.escalation_reason not in (None, "attempt_budget_exhausted"):
        return False
    if any(a.contact or a.refused or a.abort_reason is not None
           for a in tr.attempts):
        return False  # stream was not nominal / target was touched
    # (c): both arms — crossed at r > 160 mm (miss_reason), or ended on
    # the budget before the plane — leave handoff_reached False
    return all(not a.handoff_reached for a in tr.attempts)


@dataclass(frozen=True)
class Row:
    outcome: str
    doc: str
    match: Callable[[Trace], bool]


TABLE: tuple[Row, ...] = (
    Row("IS8-16", "lip-band contact pre-capture-plane; own class, never "
        "capture or clean miss (IS §8 row 16)",
        lambda tr: any(a.lip_strike for a in tr.attempts)),
    Row("IS8-11", "latch confirm intermittent; pre-success or unreachable; "
        "no-lock forbids tow, so before IS8-12 [no Phase 1 producer]",
        lambda tr: tr.latch_confirm_intermittent),
    Row("IS8-12", "post-tow release fails on an otherwise-good latch; "
        "pre-success or unreachable [no Phase 1 producer]",
        lambda tr: tr.release_failed),
    Row("success", "any D-020 latch within the attempt budget (D-022); a "
        "retry that recovers is a success (D-005)",
        lambda tr: any(a.latched for a in tr.attempts)),
    Row("IS8-17", "#62 jam criterion fired; never folded into generic "
        "insertion failure; a jam at depth is a jam, not 'no confirm'",
        lambda tr: any(a.jam for a in tr.attempts)),
    Row("IS8-13", "plate skew beyond D-024; global anomaly explains every "
        "residual downstream [no Phase 1 producer]",
        lambda tr: tr.plate_skew_exceeded),
    Row("IS8-8", "constellation residuals violate §3.5; global plate fault "
        "before local wrench reads [no Phase 1 producer]",
        lambda tr: tr.constellation_violated),
    Row("IS8-6", "wrench profile inconsistent with the funnel model "
        "[no Phase 1 producer]",
        lambda tr: tr.stud_wrench_inconsistent),
    Row("IS8-9", "insertion force spike, blunt profile, no confirm; most "
        "local contact anomaly [no Phase 1 producer]",
        lambda tr: tr.insertion_force_spike_blunt),
    Row("IS8-7", "no contact at expected depth; absence-of-evidence after "
        "every presence-of-evidence row [no Phase 1 producer]",
        lambda tr: tr.no_contact_at_expected_depth),
    Row("IS8-10", "full stroke, no confirm — requires the runner's "
        "full_stroke observable (D-020 position: depth AND radial), not "
        "mere contact",
        lambda tr: any(a.full_stroke and not a.latched for a in tr.attempts)),
    Row("IS8-18", "insertion incomplete at budget (D-033): a contact-stage "
        "timeout — the budget, not the mechanism, ended it; after IS8-10 "
        "(a completed stroke is more specific), before the perception "
        "rows (contact evidence outranks stream-shape inference)",
        lambda tr: any(a.timed_out and not a.latched for a in tr.attempts)),
    Row("IS8-2", "zero ID-0 across the approach with the low-confidence "
        "shape; total outer loss outranks partial degradation",
        lambda tr: not tr.outer_tag_seen and _low_confidence_shape(tr)),
    Row("IS8-4", "terminal escalation inner_ring_absent: outer OK, zero "
        "inner at handoff",
        lambda tr: tr.escalation_reason == "inner_ring_absent"),
    Row("IS8-14", "persistent out-of-block ID decode (§3.4); would corrupt "
        "the statistics rows 5/3/1 read [no Phase 1 producer]",
        lambda tr: tr.wrong_id_persistent),
    Row("IS8-5", "ambiguity: terminal escalation, or exhaustion whose "
        "proximate abort was ambiguity_persistent (a final-attempt abort "
        "rides Decision.underlying_abort into the trace)",
        lambda tr: (tr.escalation_reason == "ambiguity_persistent"
                    or _last_abort(tr) == "ambiguity_persistent")),
    Row("IS8-3", "exhaustion whose proximate abort was inner_ring_absent "
        "(the commit rule never satisfied)",
        lambda tr: _last_abort(tr) == "inner_ring_absent"),
    Row("IS8-1", "outer degradation: low_confidence escalation or any gate "
        "refusal; D-030's refusal path lands here, never clean_miss",
        _low_confidence_shape),
    Row("clean_miss", "D-030 residual: no contact ever, every attempt "
        "ended short of the capture plane with a nominal stream",
        _clean_miss),
)


def classify(trace: Trace) -> tuple[str, bool | None]:
    """One outcome per trial; (outcome, false_capture).

    false_capture is emitted only with IS8-16 (H-16): whether a striking
    leg itself latched — the deflected-into-the-mouth sub-path §8 row 16
    counts separately.
    """
    if trace.escalation_reason not in _KNOWN_ESCALATIONS:
        raise UnclassifiedFailure(
            f"escalation reason {trace.escalation_reason!r} is outside the "
            "committed table — extend §8 by recorded amendment, never a "
            f"guess (D-030): {trace!r}")
    for a in trace.attempts:
        if a.abort_reason not in _KNOWN_ABORTS:
            raise UnclassifiedFailure(
                f"abort reason {a.abort_reason!r} is outside the committed "
                "table — extend §8 by recorded amendment, never a guess "
                f"(D-030): {trace!r}")
    for row in TABLE:
        if row.match(trace):
            if row.outcome == "IS8-16":
                return row.outcome, any(a.lip_strike and a.latched
                                        for a in trace.attempts)
            return row.outcome, None
    raise UnclassifiedFailure(
        "no precedence row matches — extend §8 by recorded amendment, "
        f"never a guess (D-030): {trace!r}")
