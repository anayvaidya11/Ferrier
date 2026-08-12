"""T12 — REPORT figures from analysis outputs (static matplotlib PNGs).

Design rules applied (dataviz reference instance, validated palette):
categorical hues in fixed slot order, one axis per chart, single-series
charts carry no legend (the title names them), text wears ink tokens never
series color, recessive grid, thin marks. The feasibility emission is a
table, not a chart — its job is lookup, not magnitude.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

from wyzantium_sim.analysis import curves as _curves  # noqa: E402

# Reference-instance palette (light mode), fixed slot order.
SERIES = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100")
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"

_LOG_AXES = {"illuminance_lux", "stiffness_k_n_mm"}


def _fig(w=6.4, h=4.0):
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    ax.grid(True, color="#e8e7e3", lw=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)
    ax.tick_params(colors=INK_2, labelsize=8)
    return fig, ax


def _save(fig, out_dir, name):
    out = Path(out_dir) / name
    fig.savefig(out, dpi=150, bbox_inches="tight", facecolor=SURFACE)
    plt.close(fig)
    return out


def sensitivity_chart(axis, stats, out_dir, *, curve_set):
    """D-014: one axis, one series — success rate with Wilson CI band."""
    fig, ax = _fig()
    xs = [s.value for s in stats]
    ax.fill_between(xs, [s.ci_lo for s in stats], [s.ci_hi for s in stats],
                    color=SERIES[0], alpha=0.15, lw=0)
    ax.plot(xs, [s.success for s in stats], color=SERIES[0], lw=2,
            marker="o", ms=5)
    if axis in _LOG_AXES:
        ax.set_xscale("log")
    ax.set_ylim(-0.03, 1.03)
    ax.set_xlabel(axis, color=INK_2, fontsize=9)
    ax.set_ylabel("success rate", color=INK_2, fontsize=9)
    ax.set_title(f"D-014 sensitivity — {axis}  [{curve_set}, simulated]",
                 color=INK, fontsize=10, loc="left")
    return _save(fig, out_dir, f"d014_{axis}.png")


def refusal_damage_chart(curve, out_dir, *, curve_set):
    """D-017: rates vs commit threshold — ≤4 series, fixed slot order,
    legend + direct end labels."""
    fig, ax = _fig()
    xs = [s.threshold for s in curve]
    # R01 S-08: Wilson bands on the two headline series
    ax.fill_between(xs, [s.success_ci_lo for s in curve],
                    [s.success_ci_hi for s in curve],
                    color=SERIES[0], alpha=0.12, lw=0)
    ax.fill_between(xs, [s.refusal_ci_lo for s in curve],
                    [s.refusal_ci_hi for s in curve],
                    color=SERIES[1], alpha=0.12, lw=0)
    series = [("success", [s.success for s in curve]),
              ("refusal", [s.refusal for s in curve]),
              ("contact failure", [s.contact_failure for s in curve]),
              ("false capture", [s.false_capture_rate for s in curve])]
    for (name, ys), color in zip(series, SERIES):
        ax.plot(xs, ys, color=color, lw=2, marker="o", ms=5, label=name)
        ax.annotate(name, (xs[-1], ys[-1]), textcoords="offset points",
                    xytext=(6, 0), fontsize=7, color=INK_2)
    ax.set_ylim(-0.03, 1.03)
    ax.set_xlabel("conf_min_attempt (D-017 sweep)", color=INK_2, fontsize=9)
    ax.set_ylabel("rate", color=INK_2, fontsize=9)
    ax.legend(frameon=False, fontsize=8, labelcolor=INK_2)
    ax.set_title(f"D-017 refusal / damage tradeoff  [{curve_set}, simulated]",
                 color=INK, fontsize=10, loc="left")
    return _save(fig, out_dir, "d017_tradeoff.png")


def census_chart(census, out_dir, *, curve_set, title="failure distribution"):
    """Outcome census: horizontal bars, one hue, direct value labels."""
    items = sorted(census.items(), key=lambda kv: kv[1])
    fig, ax = _fig(h=max(2.2, 0.34 * len(items) + 1.2))
    names = [k for k, _ in items]
    vals = [v for _, v in items]
    ax.barh(names, vals, color=SERIES[0], height=0.62)
    for i, v in enumerate(vals):
        ax.annotate(str(v), (v, i), textcoords="offset points",
                    xytext=(4, -3), fontsize=7, color=INK_2)
    ax.set_xlabel("trials", color=INK_2, fontsize=9)
    ax.set_title(f"{title}  [{curve_set}, simulated]", color=INK,
                 fontsize=10, loc="left")
    return _save(fig, out_dir, "failure_distribution.png")


def render_all(rows, nominal, out_dir) -> dict:
    """Every REPORT figure + a JSON index mapping figure → source data."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    curve_set = rows[0].curve_set if rows else "?"
    index = {"curve_set": curve_set, "n_trials": len(rows), "figures": {}}

    sens = _curves.sensitivity(rows, nominal)
    for axis, stats in sorted(sens.items()):
        p = sensitivity_chart(axis, stats, out_dir, curve_set=curve_set)
        index["figures"][f"d014_{axis}"] = p.name
    # R01 S-08: per-point data committed beside the figures
    index["d014_points"] = {
        axis: [vars(s) for s in stats] for axis, stats in sorted(sens.items())}

    d017 = _curves.refusal_damage(rows, nominal)
    if d017:
        p = refusal_damage_chart(d017, out_dir, curve_set=curve_set)
        index["figures"]["d017_tradeoff"] = p.name
        index["d017_points"] = [vars(s) for s in d017]

    census = _curves.outcome_census(rows)
    p = census_chart(census, out_dir, curve_set=curve_set)
    index["figures"]["failure_distribution"] = p.name

    splits = _curves.attempt_splits(rows)
    index["d005_splits"] = {"n": splits.n,
                            "first_attempt": splits.first_attempt_success,
                            "overall": splits.overall_success}
    with open(out_dir / "index.json", "w", encoding="utf-8") as f:
        json.dump(index, f, indent=1)
    return index
