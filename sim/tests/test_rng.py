"""Single-root seed policy (PHASE1_PARAMETERS #60, WIRE_FORMAT).

One integer root per trial; every stream derives from it by name,
deterministically. Bit-identical replay depends on this.
"""
from wyzen_sim import rng

ROOT = 20260802


def test_stream_names_are_the_committed_set():
    assert rng.STREAM_NAMES == (
        "chassis", "perception.detection", "perception.noise",
        "perception.flip", "perception.dropout", "contact", "doe")


def test_same_root_and_name_reproduces_bit_identical_streams():
    a = rng.substream(ROOT, "chassis").random(64)
    b = rng.substream(ROOT, "chassis").random(64)
    assert (a == b).all()


def test_different_names_give_different_streams():
    a = rng.substream(ROOT, "chassis").random(64)
    b = rng.substream(ROOT, "contact").random(64)
    assert not (a == b).all()


def test_different_roots_give_different_streams():
    a = rng.substream(ROOT, "chassis").random(64)
    b = rng.substream(ROOT + 1, "chassis").random(64)
    assert not (a == b).all()


def test_request_order_does_not_change_any_stream():
    forward = {name: rng.substream(ROOT, name).random(16)
               for name in rng.STREAM_NAMES}
    backward = {name: rng.substream(ROOT, name).random(16)
                for name in reversed(rng.STREAM_NAMES)}
    for name in rng.STREAM_NAMES:
        assert (forward[name] == backward[name]).all(), name


def test_streams_helper_returns_all_named_generators():
    streams = rng.streams(ROOT)
    assert set(streams.keys()) == set(rng.STREAM_NAMES)
    check = rng.substream(ROOT, "doe").random(8)
    assert (streams["doe"].random(8) == check).all()


def test_unknown_stream_name_rejected():
    import pytest
    with pytest.raises(ValueError, match="unknown stream"):
        rng.substream(ROOT, "vibes")
