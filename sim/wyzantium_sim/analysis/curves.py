"""T12 — D-014 sensitivity curves, D-017 refusal/damage tradeoff, D-005
attempt splits, failure distributions. Data only (ARCH §6 interprets).

Outcome binning follows FAILURE_TAXONOMY §"Classifier precedence" row
semantics: REFUSAL_CLASSES are the perception/gate refusal rows (the
system declined; the asset was never touched); CONTACT_FAILURE_CLASSES are
the committed-and-failed rows (an insertion was attempted — the D-017
"damage-risk" side, together with the false_capture count).
"""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass

REFUSAL_CLASSES = frozenset(
    {"IS8-1", "IS8-2", "IS8-3", "IS8-4", "IS8-5", "IS8-14"})
CONTACT_FAILURE_CLASSES = frozenset(
    {"IS8-6", "IS8-7", "IS8-8", "IS8-9", "IS8-10", "IS8-11", "IS8-12",
     "IS8-13", "IS8-16", "IS8-17", "IS8-18"})


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple:
    """95% Wilson score interval — behaved at 0/n and n/n, unlike normal."""
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1.0 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


@dataclass(frozen=True)
class CellStat:
    value: object
    n: int
    success: float
    ci_lo: float
    ci_hi: float


def marginal_cells(rows, nominal) -> dict:
    """Group rows by single-axis deviation from the nominal sweep point —
    the Tier-1 structure. Key "nominal" holds exact-nominal rows;
    multi-axis rows are excluded (they belong to Tier-2 analyses)."""
    cells = defaultdict(list)
    for r in rows:
        diff = [(k, r.sweep_point[k]) for k, v in nominal.items()
                if k in r.sweep_point and r.sweep_point[k] != v
                and k != "curve_set"]
        if not diff:
            cells["nominal"].append(r)
        elif len(diff) == 1:
            cells[diff[0]].append(r)
    return dict(cells)


def sensitivity(rows, nominal) -> dict:
    """D-014: per-axis success curves with Wilson CIs. The nominal cell is
    included in every axis's curve at its nominal value."""
    cells = marginal_cells(rows, nominal)
    nominal_rows = cells.get("nominal", [])
    axes = defaultdict(dict)
    for key, cell_rows in cells.items():
        if key == "nominal":
            continue
        axis, value = key
        axes[axis][value] = cell_rows
    out = {}
    for axis, by_value in axes.items():
        if nominal_rows:
            by_value.setdefault(nominal[axis], nominal_rows)
        stats = []
        for value, cell_rows in by_value.items():
            n = len(cell_rows)
            k = sum(r.outcome == "success" for r in cell_rows)
            lo, hi = wilson_ci(k, n)
            stats.append(CellStat(value, n, k / n, lo, hi))
        out[axis] = sorted(stats, key=lambda s: s.value)
    return out


@dataclass(frozen=True)
class ThresholdStat:
    threshold: float
    n: int
    success: float
    refusal: float
    contact_failure: float
    miss: float
    false_capture_rate: float
    # R01 S-08: per-point Wilson CIs on the two headline series
    success_ci_lo: float = 0.0
    success_ci_hi: float = 1.0
    refusal_ci_lo: float = 0.0
    refusal_ci_hi: float = 1.0


def refusal_damage(rows, nominal) -> tuple:
    """D-017: the refusal-rate vs damage-risk tradeoff over the
    conf_min_attempt marginal (nominal cell included at its threshold)."""
    curve = []
    for stat_value, cell_rows in sorted(
            ((v, rs) for (v, rs) in _axis_cells(
                rows, nominal, "conf_min_attempt").items())):
        n = len(cell_rows)
        census = Counter(r.outcome for r in cell_rows)
        refusals = sum(census[c] for c in REFUSAL_CLASSES)
        contact = sum(census[c] for c in CONTACT_FAILURE_CLASSES)
        fc = sum(1 for r in cell_rows
                 if r.false_capture not in (None, 0))
        s_lo, s_hi = wilson_ci(census["success"], n)
        r_lo, r_hi = wilson_ci(refusals, n)
        curve.append(ThresholdStat(
            threshold=float(stat_value), n=n,
            success=census["success"] / n,
            refusal=refusals / n, contact_failure=contact / n,
            miss=census["clean_miss"] / n, false_capture_rate=fc / n,
            success_ci_lo=s_lo, success_ci_hi=s_hi,
            refusal_ci_lo=r_lo, refusal_ci_hi=r_hi))
    return tuple(curve)


def _axis_cells(rows, nominal, axis) -> dict:
    cells = marginal_cells(rows, nominal)
    by_value = {v: rs for (key, rs) in cells.items()
                if key != "nominal"
                for (a, v) in [key] if a == axis}
    if cells.get("nominal"):
        by_value.setdefault(nominal[axis], cells["nominal"])
    return by_value


@dataclass(frozen=True)
class SplitStat:
    n: int
    first_attempt_success: float
    overall_success: float


def attempt_splits(rows) -> SplitStat:
    """D-005: first-attempt vs multi-attempt success, reported separately."""
    n = len(rows)
    if n == 0:
        return SplitStat(0, 0.0, 0.0)
    first = sum(r.first_attempt_success for r in rows)
    overall = sum(r.outcome == "success" for r in rows)
    return SplitStat(n, first / n, overall / n)


def outcome_census(rows) -> dict:
    return dict(Counter(r.outcome for r in rows))
