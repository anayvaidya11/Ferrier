"""T9 — outcome classifier (table-driven trace→outcome, documented precedence).

Gate (PHASE1_PLAN §4): one constructed trace per class (success, IS8-1..17,
clean_miss) → exactly that class; precedence pairs tested; unmatched raises.
Risk 5 strengthens: overlapping signatures need a documented order with a
test per pair. IS8-15 is nominal per IS §8 row 15 / REQ-005 / D-030, so the
gate is read per the specs-win rule (PHASE1_PLAN header): one trace per
*classifiable* class, plus a test that IS8-15 is unreachable while staying
in the wire enum (see the PHASE1_PLAN §4 gate note).

Double-entry transcription:
  D-030: clean_miss ⟺ (a) fails D-022 ∧ (b) no contact ever ∧ (c) every
      attempt missed at r > 160 mm / never crossed, or ended on budget
      without reaching the plane ∧ (d) no §8 signature matches under the
      documented precedence order; the refusal path is never clean_miss;
      a trace matching no rule raises, never guesses.
  D-022 / D-020: success ⟺ latch within the attempt budget (t ≤ T is
      structural — the trial loop never runs past budget).
  H-16 / IS §8 row 16: lip strike is its own outcome class, never capture
      or clean miss; false-capture sub-path (a striking leg's own latch)
      counted separately via trial_result.false_capture.
  FAILURE_TAXONOMY §"Classifier precedence": the committed order; the
      transcription test below pins TABLE to it row-for-row.
"""

import re
from pathlib import Path

import pytest

from wirefmt import validator
from wyzantium_sim.classify import outcomes

TAXONOMY_MD = Path(__file__).resolve().parents[2] / "FAILURE_TAXONOMY.md"


def attempt(**kw):
    return outcomes.AttemptEnd(**kw)


def trace(*attempts_, **kw):
    return outcomes.Trace(attempts=tuple(attempts_), **kw)


def row_index(outcome):
    return [r.outcome for r in outcomes.TABLE].index(outcome)


# One canonical constructed trace per classifiable class (the T9 gate).
# Values chosen to satisfy exactly the class's signature and no earlier row.
CANONICAL = {
    "IS8-16": trace(attempt(handoff_reached=True, contact=True,
                            lip_strike=True)),
    "IS8-11": trace(attempt(handoff_reached=True, contact=True,
                            full_stroke=True, latched=True),
                    latch_confirm_intermittent=True),
    "IS8-12": trace(attempt(handoff_reached=True, contact=True,
                            full_stroke=True, latched=True),
                    release_failed=True),
    "success": trace(attempt(handoff_reached=True, contact=True,
                             full_stroke=True, latched=True)),
    "IS8-17": trace(attempt(handoff_reached=True, contact=True, jam=True,
                            abort_reason="jam_detected")),
    "IS8-13": trace(attempt(handoff_reached=True, contact=True),
                    plate_skew_exceeded=True),
    "IS8-8": trace(attempt(handoff_reached=True, contact=True),
                   constellation_violated=True),
    "IS8-6": trace(attempt(handoff_reached=True, contact=True),
                   stud_wrench_inconsistent=True),
    "IS8-9": trace(attempt(handoff_reached=True, contact=True),
                   insertion_force_spike_blunt=True),
    "IS8-7": trace(attempt(handoff_reached=True),
                   no_contact_at_expected_depth=True),
    "IS8-10": trace(attempt(handoff_reached=True, contact=True,
                            full_stroke=True, timed_out=True),
                    escalation_reason="attempt_budget_exhausted"),
    "IS8-2": trace(attempt(refused=True, abort_reason="low_confidence"),
                   escalation_reason="low_confidence", outer_tag_seen=False),
    "IS8-4": trace(attempt(), escalation_reason="inner_ring_absent"),
    "IS8-14": trace(attempt(), wrong_id_persistent=True),
    "IS8-5": trace(attempt(abort_reason="ambiguity_persistent"),
                   escalation_reason="ambiguity_persistent"),
    "IS8-3": trace(attempt(abort_reason="inner_ring_absent"),
                   attempt(abort_reason="inner_ring_absent"),
                   escalation_reason="attempt_budget_exhausted"),
    "IS8-1": trace(attempt(refused=True, abort_reason="low_confidence"),
                   escalation_reason="attempt_budget_exhausted"),
    "clean_miss": trace(attempt(miss_reason="r_gt_annulus"),
                        attempt(miss_reason="no_crossing"),
                        escalation_reason="attempt_budget_exhausted"),
}


class TestOneTracePerClass:
    @pytest.mark.parametrize("outcome", sorted(CANONICAL))
    def test_canonical_trace_maps_to_its_class(self, outcome):
        got, _ = outcomes.classify(CANONICAL[outcome])
        assert got == outcome

    @pytest.mark.parametrize("outcome", sorted(CANONICAL))
    def test_no_earlier_row_matches_the_canonical_trace(self, outcome):
        # minimality: each canonical trace reaches its row, not an earlier one
        tr = CANONICAL[outcome]
        for r in outcomes.TABLE[:row_index(outcome)]:
            assert not r.match(tr), f"{r.outcome} fires on canonical {outcome}"

    def test_empty_trace_is_clean_miss(self):
        # budget expired before any attempt ran: nominal stream, target
        # never touched — the D-030 residual
        assert outcomes.classify(trace()) == ("clean_miss", None)


# Risk-5 mandate: a test per overlapping pair. Each trace satisfies both
# rows' signatures; the earlier (listed first) must win.
PAIRS = [
    ("IS8-16", "success",
     trace(attempt(handoff_reached=True, contact=True, lip_strike=True,
                   full_stroke=True, latched=True))),
    ("IS8-16", "IS8-17",
     trace(attempt(handoff_reached=True, contact=True, lip_strike=True,
                   jam=True))),
    ("IS8-16", "IS8-1",
     trace(attempt(handoff_reached=True, contact=True, lip_strike=True),
           attempt(refused=True, abort_reason="low_confidence"),
           escalation_reason="attempt_budget_exhausted")),
    ("IS8-11", "IS8-12",
     trace(attempt(handoff_reached=True, contact=True, full_stroke=True,
                   latched=True),
           latch_confirm_intermittent=True, release_failed=True)),
    ("IS8-11", "success", CANONICAL["IS8-11"]),
    ("IS8-12", "success", CANONICAL["IS8-12"]),
    ("success", "IS8-17",  # jam then recovered latch is a success (D-005)
     trace(attempt(handoff_reached=True, contact=True, jam=True,
                   abort_reason="jam_detected"),
           attempt(handoff_reached=True, contact=True, full_stroke=True,
                   latched=True))),
    ("success", "IS8-3",  # ring aborts then recovered latch
     trace(attempt(abort_reason="inner_ring_absent"),
           attempt(handoff_reached=True, contact=True, full_stroke=True,
                   latched=True))),
    ("IS8-17", "IS8-5",
     trace(attempt(handoff_reached=True, contact=True, jam=True),
           attempt(abort_reason="ambiguity_persistent"),
           escalation_reason="attempt_budget_exhausted")),
    ("IS8-17", "IS8-1",
     trace(attempt(handoff_reached=True, contact=True, jam=True),
           attempt(refused=True, abort_reason="low_confidence"),
           escalation_reason="attempt_budget_exhausted")),
    ("IS8-17", "IS8-10",  # jam at depth is a jam, not "no confirm"
     trace(attempt(handoff_reached=True, contact=True, jam=True,
                   full_stroke=True))),
    ("IS8-13", "IS8-8",
     trace(attempt(handoff_reached=True, contact=True),
           plate_skew_exceeded=True, constellation_violated=True)),
    ("IS8-8", "IS8-6",
     trace(attempt(handoff_reached=True, contact=True),
           constellation_violated=True, stud_wrench_inconsistent=True)),
    ("IS8-6", "IS8-9",
     trace(attempt(handoff_reached=True, contact=True),
           stud_wrench_inconsistent=True, insertion_force_spike_blunt=True)),
    ("IS8-9", "IS8-7",
     trace(attempt(handoff_reached=True, contact=True),
           insertion_force_spike_blunt=True,
           no_contact_at_expected_depth=True)),
    ("IS8-10", "IS8-1",
     trace(attempt(handoff_reached=True, contact=True, full_stroke=True,
                   timed_out=True),
           attempt(refused=True, abort_reason="low_confidence"),
           escalation_reason="attempt_budget_exhausted")),
    ("IS8-2", "IS8-1",  # total outer loss outranks partial degradation
     trace(attempt(refused=True, abort_reason="low_confidence"),
           escalation_reason="low_confidence", outer_tag_seen=False)),
    ("IS8-4", "IS8-3",
     trace(attempt(abort_reason="inner_ring_absent"),
           escalation_reason="inner_ring_absent")),
    ("IS8-5", "IS8-3",
     trace(attempt(abort_reason="inner_ring_absent"),
           escalation_reason="ambiguity_persistent")),
    ("IS8-14", "IS8-5",
     trace(attempt(abort_reason="ambiguity_persistent"),
           escalation_reason="ambiguity_persistent",
           wrong_id_persistent=True)),
    ("IS8-1", "clean_miss",  # D-030: the refusal path is never clean_miss
     trace(attempt(miss_reason="r_gt_annulus"),
           attempt(refused=True, abort_reason="low_confidence"),
           escalation_reason="attempt_budget_exhausted")),
]


class TestPrecedencePairs:
    @pytest.mark.parametrize(
        "winner,loser,tr", PAIRS,
        ids=[f"{w}-over-{l}" for w, l, _ in PAIRS])
    def test_earlier_row_wins(self, winner, loser, tr):
        assert row_index(winner) < row_index(loser)
        got, _ = outcomes.classify(tr)
        assert got == winner

    @pytest.mark.parametrize(
        "winner,loser,tr", PAIRS,
        ids=[f"{w}-vs-{l}-overlaps" for w, l, _ in PAIRS])
    def test_pair_genuinely_overlaps_or_is_the_exclusion_case(
            self, winner, loser, tr):
        # each listed trace must satisfy the winner; it satisfies the loser
        # too unless the pair documents a designed exclusion (IS8-1 vs
        # clean_miss: D-030 makes them disjoint — the trace shows the
        # refusal keeps an otherwise-clean miss out of clean_miss)
        assert outcomes.TABLE[row_index(winner)].match(tr)
        if (winner, loser) != ("IS8-1", "clean_miss"):
            assert outcomes.TABLE[row_index(loser)].match(tr)
        else:
            assert not outcomes.TABLE[row_index(loser)].match(tr)


class TestFalseCapture:
    def test_striking_leg_latch_is_false_capture(self):
        got = outcomes.classify(
            trace(attempt(handoff_reached=True, contact=True, lip_strike=True,
                          full_stroke=True, latched=True)))
        assert got == ("IS8-16", True)

    def test_lip_then_clean_later_latch_is_not_false_capture(self):
        # the strike happened, so the trial scores IS8-16 (IS §8 row 16:
        # never capture) — but the recovery leg's latch is not the
        # false-capture sub-path
        got = outcomes.classify(
            trace(attempt(handoff_reached=True, contact=True,
                          lip_strike=True),
                  attempt(handoff_reached=True, contact=True,
                          full_stroke=True, latched=True)))
        assert got == ("IS8-16", False)

    @pytest.mark.parametrize(
        "outcome", sorted(set(CANONICAL) - {"IS8-16"}))
    def test_false_capture_absent_off_row_16(self, outcome):
        assert outcomes.classify(CANONICAL[outcome])[1] is None


class TestIS815Excluded:
    def test_table_covers_every_wire_outcome_except_comms(self):
        assert ({r.outcome for r in outcomes.TABLE}
                == validator.OUTCOMES - {"IS8-15"})

    def test_wire_enum_still_carries_is8_15(self):
        assert "IS8-15" in validator.OUTCOMES

    def test_comms_lost_trial_classifies_by_its_attempt(self):
        # IS §8 row 15 / REQ-005: comms loss is nominal, out-of-band, with
        # no trace representation — a latch under comms loss is a success
        got = outcomes.classify(
            trace(attempt(handoff_reached=True, contact=True,
                          full_stroke=True, latched=True)))
        assert got == ("success", None)


class TestUnclassifiedRaises:
    def test_contact_timeout_without_full_stroke_raises(self):
        # the interim map guessed IS8-10 here; D-030 says never guess —
        # contact without full stroke matches no signature
        with pytest.raises(outcomes.UnclassifiedFailure):
            outcomes.classify(
                trace(attempt(handoff_reached=True, contact=True,
                              timed_out=True),
                      escalation_reason="attempt_budget_exhausted"))

    def test_unknown_escalation_reason_raises(self):
        with pytest.raises(outcomes.UnclassifiedFailure):
            outcomes.classify(trace(attempt(),
                                    escalation_reason="not_a_reason"))

    def test_command_abort_raises(self):
        # abort_reason "command" names no §8 row
        with pytest.raises(outcomes.UnclassifiedFailure):
            outcomes.classify(
                trace(attempt(abort_reason="command"),
                      escalation_reason="attempt_budget_exhausted"))

    def test_raise_carries_the_trace_as_amendment_evidence(self):
        tr = trace(attempt(), escalation_reason="not_a_reason")
        with pytest.raises(outcomes.UnclassifiedFailure) as exc:
            outcomes.classify(tr)
        assert repr(tr) in str(exc.value)


class TestTableShape:
    def test_one_row_per_outcome(self):
        names = [r.outcome for r in outcomes.TABLE]
        assert len(names) == len(set(names)) == 18

    def test_clean_miss_is_the_residual_row(self):
        assert outcomes.TABLE[-1].outcome == "clean_miss"

    def test_every_row_documents_itself(self):
        assert all(r.doc.strip() for r in outcomes.TABLE)


class TestDocTranscription:
    def section(self):
        text = TAXONOMY_MD.read_text()
        m = re.search(r"^## Classifier precedence.*$", text, re.M)
        assert m, "FAILURE_TAXONOMY.md lacks the precedence section"
        return text[m.start():]

    def test_doc_order_equals_table_order(self):
        listed = re.findall(
            r"^\s*\d+\.\s+\*\*(success|clean_miss|IS8-\d+)\*\*",
            self.section(), re.M)
        assert listed == [r.outcome for r in outcomes.TABLE]

    def test_doc_states_the_is8_15_exclusion(self):
        assert "IS8-15 (comms loss) is not a classifier output" \
            in self.section()
