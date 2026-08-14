"""Wider #62 probe: does the sustained jam signature ever complete on
successful insertions, and with how much margin? (D-040's open hook.)

The week-one probe (sim/results/probe62_check.json) measured
*instantaneous* wrench percentiles on ONE nominal record. The committed
IS8-17 criterion is *sustained*: axial > F_ax_jam ∧ |lateral| < F_lat_jam
continuously for ≥ t_jam, pre-latch (contact/runner.py, D-040 semantics:
force cells are entry conditions; the persistence window discriminates).
This probe regenerates every contact-dynamics Tier-1 cell locally from
the committed plans and computes, per trial and per (F_ax, F_lat) pair,
the maximum sustained-window duration over the logged
sim_truth.contact_wrench series — deciding all 18 committed grid cells
offline at once.

Criterion transcription (runner.py run_contact, verbatim semantics):
  f_ax = abs(wrench[0]); f_lat = hypot(wrench[1], wrench[2])  # head_frame
  condition holds -> timer += dt; else timer = 0; fires at timer >= t_jam.
Absent contact_wrench (pre-contact, omitted-not-zeroed) = condition
false = reset, exactly as a zero wall wrench resets in the runner. The
logged series of a success ends at latch, so full-series evaluation is
the pre-latch evaluation plus the latch hold — conservative in the safe
direction.

No threshold changes here: any would-fire finding is evidence for the
recorded-revision decision D-040 left open, which is the human's.

Usage: sim/.venv/bin/python tools/probe62_wide.py [--workers 8]
"""
import argparse
import json
import math
import platform
import shutil
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
sys.path.insert(0, str(REPO / "sim"))

from wyzantium_sim.doe import runner, tiers  # noqa: E402

SWEEP_ROOT = 20260808
OUT = REPO / "sim" / "results" / "probe62_wide.json"

# Committed grid (#62; probe62_check.json committed_grid)
F_AX = (50.0, 100.0, 200.0)
F_LAT = (10.0, 25.0)
T_JAM = (0.5, 1.0, 2.0)
DEFAULTS = (100.0, 25.0, 1.0)

CONTACT_AXES = ("nominal", "stiffness_k_n_mm", "head_mass_kg",
                "mu_contact", "restitution_e", "speed_insertion_ms")


def wrench_series(record_path):
    """(t, fx, fy, fz) per sim_truth line; wrench absent -> None entry."""
    out = []
    for line in record_path.read_text().splitlines():
        obj = json.loads(line)
        if obj.get("type") != "sim_truth":
            continue
        w = obj.get("contact_wrench")
        out.append((obj["t"], w))
    return out


def max_sustained(series, f_ax_thr, f_lat_thr):
    """Longest contiguous duration with |fx| > f_ax ∧ hypot(fy,fz) < f_lat,
    resets mirroring the runner; returns seconds."""
    best = run = 0.0
    prev_t = None
    for t, w in series:
        dt = 0.0 if prev_t is None else max(0.0, t - prev_t)
        prev_t = t
        holds = False
        if w is not None:
            holds = (abs(w[0]) > f_ax_thr
                     and math.hypot(w[1], w[2]) < f_lat_thr)
        run = run + dt if holds else 0.0
        best = max(best, run)
    return best


def pct(sorted_vals, q):
    if not sorted_vals:
        return 0.0
    i = min(len(sorted_vals) - 1, int(round(q * (len(sorted_vals) - 1))))
    return sorted_vals[i]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--scratch", default=str(TOOLS / "mr_kit" / "build"
                                             / "probe62_records"))
    args = ap.parse_args()
    scratch = Path(args.scratch)
    scratch.mkdir(parents=True, exist_ok=True)

    t1 = tiers.tier1_plan(SWEEP_ROOT)
    plan = tuple(p for p in t1
                 if p.tag.split(":")[1].rsplit("=", 1)[0] in CONTACT_AXES)
    cells = sorted({p.tag.rsplit(":", 1)[0] for p in plan})
    print(f"[probe62] {len(plan)} trials across {len(cells)} cells",
          flush=True)
    result = runner.run_sweep(plan, scratch, workers=args.workers)

    outcomes = {}
    durations = {(fa, fl): [] for fa in F_AX for fl in F_LAT}
    inst_max_ax = []
    for path in result.paths:
        last = json.loads(path.read_text().splitlines()[-1])
        assert last["type"] == "trial_result", path.name
        outcomes[last["outcome"]] = outcomes.get(last["outcome"], 0) + 1
        if last["outcome"] != "success":
            continue  # census reported; only successes probe the margin
        series = wrench_series(path)
        inst_max_ax.append(max((abs(w[0]) for _, w in series
                                if w is not None), default=0.0))
        for pair in durations:
            durations[pair].append(max_sustained(series, *pair))

    n_success = outcomes.get("success", 0)
    grid = {}
    for (fa, fl), vals in durations.items():
        s = sorted(vals)
        stats = {"max_sustained_s": {"p50": pct(s, 0.50),
                                     "p90": pct(s, 0.90),
                                     "p99": pct(s, 0.99),
                                     "max": s[-1] if s else 0.0}}
        for t in T_JAM:
            stats[f"would_fire_t{t}"] = sum(v >= t for v in vals)
        grid[f"F_ax={fa:g},F_lat={fl:g}"] = stats

    d_ax, d_lat, d_t = DEFAULTS
    default_max = max(durations[(d_ax, d_lat)], default=0.0)
    default_fires = sum(v >= d_t for v in durations[(d_ax, d_lat)])
    verdict = (
        f"zero would-fires at the committed default "
        f"(F_ax={d_ax:g} N, F_lat={d_lat:g} N, t={d_t:g} s) across "
        f"{n_success} successful insertions; max sustained signature "
        f"{default_max:.4f} s = {default_max / d_t:.1%} of the window — "
        "D-040's persistence-window discrimination confirmed with margin"
        if default_fires == 0 else
        f"{default_fires}/{n_success} successful insertions WOULD have "
        f"fired IS8-17 at the committed default — evidence for the open "
        "D-040 recorded-revision decision (human's call; no change made)")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                         capture_output=True, text=True).stdout.strip()
    with open(OUT, "w") as fh:
        json.dump({
            "source": ("#62 wide probe (item 5, pre-window work): sustained "
                       "IS8-17 signature vs the committed grid over every "
                       "contact-dynamics Tier-1 cell, regenerated locally "
                       "from the committed plans (records not retained; "
                       "per-instance-class caveat, R01 F-018). Criterion "
                       "transcribed from contact/runner.py run_contact; "
                       "full-series evaluation = pre-latch + hold, "
                       "conservative. D-040 stands; no thresholds changed."),
            "code_git_sha": sha,
            "regenerated_on": platform.platform(),
            "cells": cells,
            "n_trials": len(plan),
            "outcome_census": outcomes,
            "instantaneous_axial_max_N": {
                "p90": pct(sorted(inst_max_ax), 0.90),
                "max": max(inst_max_ax, default=0.0)},
            "committed_grid": {"F_ax_N": list(F_AX), "F_lat_N": list(F_LAT),
                               "t_s": list(T_JAM)},
            "sustained_by_pair": grid,
            "default_cell": {"F_ax_N": d_ax, "F_lat_N": d_lat, "t_s": d_t,
                             "would_fire": default_fires,
                             "max_sustained_s": default_max},
            "finding": verdict,
        }, fh, indent=1)

    shutil.rmtree(scratch)
    print(f"[probe62] {verdict}", flush=True)
    print(f"[probe62] census: {outcomes} -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
