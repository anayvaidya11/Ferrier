"""Golden and negative fixture corpus — the executable form of WIRE_FORMAT.

The golden trial exercises every line type and every omission semantic; the
negative corpus has one file per contract rule with its expected rejection
reason. Phase 3 firmware must pass this same corpus.
"""
import json
from pathlib import Path

import pytest

from wirefmt import records, validator

FIXTURES = Path(__file__).resolve().parent.parent / "wirefmt" / "fixtures"
GOLDEN = FIXTURES / "golden_trial.ndjson"


def test_golden_trial_validates_clean():
    assert validator.validate_trial_file(GOLDEN) == []


def test_golden_trial_round_trips_byte_identically():
    raw = GOLDEN.read_bytes()
    lines = records.read_ndjson(GOLDEN)
    rebuilt = "".join(records.dumps_line(obj) + "\n" for obj in lines)
    assert rebuilt.encode("utf-8") == raw


def test_golden_trial_exercises_the_contract():
    lines = records.read_ndjson(GOLDEN)
    states = [l for l in lines if l["type"] == "target_state"]
    truths = [l for l in lines if l["type"] == "sim_truth"]
    result = lines[-1]
    # Every line type present.
    assert lines[0]["type"] == "trial_header" and states and truths
    # Omission semantics: at least one pose-absent perception line.
    assert any("pose" not in s and s["pose_source"] == "none" for s in states)
    # The commit-relevant source appears fused in inner_servo.
    assert any(s["pose_source"] == "multi_tag_fused"
               and s["stage"] == "inner_servo" for s in states)
    # Abort and escalate lines carry their conditional-required fields.
    assert any(s["stage"] == "abort" and "abort_reason" in s for s in states)
    assert any(s["stage"] == "escalate" and "escalation" in s for s in states)
    # contact_wrench omitted before contact, present after.
    assert any("contact_wrench" not in t for t in truths)
    assert any("contact_wrench" in t for t in truths)
    # Result exercises the H-16 sub-path counter.
    assert result["outcome"] == "IS8-16" and result["false_capture"] is True


def load_manifest():
    return json.loads((FIXTURES / "negative" / "manifest.json").read_text())


def test_negative_manifest_covers_all_files():
    files = {p.name for p in (FIXTURES / "negative").glob("*.ndjson")}
    assert files == {entry["file"] for entry in load_manifest()}


@pytest.mark.parametrize("entry", load_manifest(),
                         ids=lambda e: e["file"] if isinstance(e, dict) else e)
def test_negative_fixture_rejected_for_stated_reason(entry):
    path = FIXTURES / "negative" / entry["file"]
    if entry["mode"] == "line":
        lines = records.read_ndjson(path)
        assert len(lines) == 1
        errors = validator.validate_line(lines[0])
    else:
        errors = validator.validate_trial_file(path)
    assert errors, f"{entry['file']} unexpectedly valid"
    assert any(entry["expect"] in e for e in errors), \
        f"{entry['file']}: no error contained {entry['expect']!r}: {errors}"
