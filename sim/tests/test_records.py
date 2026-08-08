"""Canonical NDJSON writer — WIRE_FORMAT encoding rules.

Byte-identical replay (WIRE_FORMAT trial record schema) requires a canonical
serialization: fixed key order for known fields, shortest round-trip floats,
LF line endings, and the omitted-not-zeroed rule enforced at the writer.
"""
import json

import pytest

from wirefmt import records

NOMINAL = {
    "v": 1,
    "type": "target_state",
    "t_capture": 142.031,
    "t_emit": 142.043,
    "pose": {"t": [2.412, 0.113, -0.071], "q": [0.008, 0.002, 0.9999, 0.011]},
    "pose_cov": [0.0009, 0, 0, 0, 0, 0, 0.0016, 0, 0, 0, 0, 0.0016,
                 0, 0, 0, 0.0007, 0, 0, 0.0011, 0, 0.0011],
    "pose_source": "outer_tag",
    "conf": 0.96,
    "stage": "outer_servo",
}


def test_round_trip_is_byte_identical():
    line = records.dumps_line(NOMINAL)
    assert records.dumps_line(json.loads(line)) == line


def test_key_order_is_canonical_regardless_of_input_order():
    shuffled = dict(reversed(list(NOMINAL.items())))
    assert records.dumps_line(shuffled) == records.dumps_line(NOMINAL)


def test_unknown_fields_are_preserved_and_stable():
    # WIRE_FORMAT: unknown fields MUST be ignored and preserved on relay.
    with_unknown = {**NOMINAL, "future_field": {"a": 1}}
    line = records.dumps_line(with_unknown)
    assert '"future_field":{"a":1}' in line
    assert records.dumps_line(json.loads(line)) == line


def test_null_value_is_rejected():
    # Omitted-not-zeroed: a field that could not be determined is omitted,
    # never emitted as zero, null, or a default.
    with pytest.raises(records.EncodingError, match="null"):
        records.dumps_line({**NOMINAL, "fault": None})


def test_floats_keep_shortest_round_trip_repr():
    line = records.dumps_line(NOMINAL)
    assert '"t_capture":142.031' in line
    assert '"conf":0.96' in line


def test_write_and_read_ndjson_lf_terminated(tmp_path):
    path = tmp_path / "trial.ndjson"
    second = {**NOMINAL, "t_capture": 142.064, "t_emit": 142.076}
    records.write_ndjson(path, [NOMINAL, second])
    raw = path.read_bytes()
    assert raw.endswith(b"\n") and b"\r" not in raw
    assert raw.count(b"\n") == 2
    assert records.read_ndjson(path) == [NOMINAL, second]


class TestAtomicWrite:
    # T10 resume treats an on-disk record as evidence, which is only sound
    # if the writer is atomic: a failure mid-write must never leave a
    # truncated or partial file at the destination.

    def test_failed_serialization_leaves_existing_file_untouched(self,
                                                                 tmp_path):
        path = tmp_path / "trial.ndjson"
        second = {**NOMINAL, "t_capture": 142.064, "t_emit": 142.076}
        records.write_ndjson(path, [second, second])
        before = path.read_bytes()
        with pytest.raises(records.EncodingError):
            # line 1 serializes fine, line 2 raises — a non-atomic writer
            # leaves line 1 alone at the destination
            records.write_ndjson(path, [NOMINAL,
                                        {**NOMINAL, "fault": None}])
        assert path.read_bytes() == before

    def test_no_tmp_sibling_survives_a_successful_write(self, tmp_path):
        path = tmp_path / "trial.ndjson"
        records.write_ndjson(path, [NOMINAL])
        assert [p.name for p in tmp_path.iterdir()] == ["trial.ndjson"]
