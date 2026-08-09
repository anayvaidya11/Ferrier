#!/usr/bin/env python3
"""tools/charts.py — REPORT charts from a record dataset (PHASE1_PLAN §2).

Thin CLI over wyzantium_sim.analysis (the logic lives, tested, in the
package). Run from the sim venv:

    sim/.venv/bin/python tools/charts.py <dataset-dir> --out <fig-dir>
        [--feasibility out.json] [--band-threshold 0.60]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from wyzantium_sim.analysis import feasibility, load_dataset
from wyzantium_sim.analysis.charts import render_all
from wyzantium_sim.doe import tiers


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dataset", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--feasibility", type=Path, default=None)
    ap.add_argument("--band-threshold", type=float, default=0.60)
    args = ap.parse_args(argv)

    nominal = tiers.load_nominal()["sweep_point"]
    rows = load_dataset(args.dataset)
    index = render_all(rows, nominal, args.out)
    print(f"{len(index['figures'])} figures → {args.out} "
          f"({index['n_trials']} trials, {index['curve_set']})")

    if args.feasibility is not None:
        out = feasibility(rows, nominal, threshold=args.band_threshold)
        args.feasibility.parent.mkdir(parents=True, exist_ok=True)
        with open(args.feasibility, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)
        print(f"#63 emission → {args.feasibility}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
