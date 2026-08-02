"""Single-root seed policy (PHASE1_PARAMETERS #60, WIRE_FORMAT).

One integer root per trial, recorded in trial_header.seed; every stream the
trial consumes derives from it by name. Derivation is order-independent —
each stream's seed sequence is keyed by (root, crc32(name)), so requesting
streams in a different order can never change any stream's values.
"""
import zlib

import numpy as np

STREAM_NAMES = ("chassis", "perception.detection", "perception.noise",
                "perception.flip", "perception.dropout", "contact", "doe")


def substream(root, name):
    """Deterministic, independent generator for one named stream."""
    if name not in STREAM_NAMES:
        raise ValueError(f"unknown stream {name!r}; "
                         f"streams are {STREAM_NAMES}")
    key = zlib.crc32(name.encode("utf-8"))
    seq = np.random.SeedSequence([int(root), key])
    return np.random.Generator(np.random.PCG64(seq))


def streams(root):
    """All named generators for one trial root."""
    return {name: substream(root, name) for name in STREAM_NAMES}
