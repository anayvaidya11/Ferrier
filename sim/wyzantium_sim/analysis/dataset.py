"""T12 — dataset loading with the curve-set pooling guard.

Reads only the header and result lines of each record (fast at 10⁴ scale).
The guard is the ROADMAP curve-swap discipline made mechanical: analysis
refuses to pool rows across curve-set IDs — pre- and post-MR datasets are
reported side by side, never averaged (PHASE1_PLAN §2 analysis/ row).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


class MixedCurveSetsError(ValueError):
    """Rows span more than one curve_set — pooling refused."""


@dataclass(frozen=True)
class TrialRow:
    trial_id: str
    seed: int
    engine: str
    curve_set: str
    sweep_point: dict
    outcome: str
    first_attempt_success: bool
    attempts_used: int
    t_total: float
    handoff_reached: bool
    false_capture: object   # int | None


def _row(path: Path) -> TrialRow:
    lines = path.read_text(encoding="utf-8").splitlines()
    header, result = json.loads(lines[0]), json.loads(lines[-1])
    sp = header["sweep_point"]
    return TrialRow(
        trial_id=header["trial_id"], seed=header["seed"],
        engine=header["engine"]["name"], curve_set=sp["curve_set"],
        sweep_point=sp, outcome=result["outcome"],
        first_attempt_success=result["first_attempt_success"],
        attempts_used=result["attempts_used"], t_total=result["t_total"],
        handoff_reached=result["handoff_reached"],
        false_capture=result.get("false_capture"))


def load_dataset(source, *, expect_curve_set=None) -> tuple:
    """source: a directory of .ndjson records, or an iterable of paths."""
    source = Path(source) if isinstance(source, (str, Path)) else source
    paths = (sorted(Path(source).glob("*.ndjson"))
             if isinstance(source, Path) else [Path(p) for p in source])
    rows = tuple(_row(p) for p in paths)
    seen = sorted({r.curve_set for r in rows})
    if len(seen) > 1:
        raise MixedCurveSetsError(
            f"dataset spans curve sets {seen} — pooling across the swap "
            "seam is refused (ROADMAP protocol); load each set separately")
    if expect_curve_set is not None and seen and seen != [expect_curve_set]:
        raise MixedCurveSetsError(
            f"dataset is {seen[0]!r}, expected {expect_curve_set!r}")
    return rows
