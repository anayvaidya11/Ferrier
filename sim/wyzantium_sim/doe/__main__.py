"""T10 — DOE sweep CLI: `python -m wyzantium_sim.doe`.

Plans come from the committed tier generators (D-021/D-032) or a plan
file; execution, resume, and spend metering are doe/runner.py. The mini
plan is the smoke-sweep unit (PHASE1_PLAN §5 week 3 / risk #8: small-N,
local, MuJoCo): the first 50 Tier-1 cells at one replicate.

Spend: --usd-per-trial engages the meter (ceiling from spend_p02.json,
never a flag — changing the ceiling is a recorded amendment, not a CLI
option). The ledger defaults to <out>/spend_ledger.json.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from wyzantium_sim.doe import tiers
from wyzantium_sim.doe.runner import SpendMeter, run_sweep


def load_plan_file(path) -> tuple:
    data = json.loads(Path(path).read_text())
    return tuple(tiers.PlannedTrial(t["tag"], int(t["seed"]),
                                    dict(t["sweep_point"]))
                 for t in data["trials"])


def build_plan(args) -> tuple:
    if args.plan_file is not None:
        return load_plan_file(args.plan_file)
    if args.plan == "tier1":
        return tiers.tier1_plan(args.sweep_root, replicates=args.replicates)
    if args.plan == "tier2":
        return tiers.tier2_plan(args.sweep_root, n=args.n)
    if args.plan == "gate":
        if args.n is None:
            raise SystemExit("--plan gate requires --n")
        return tiers.gate_plan(args.sweep_root, n=args.n)
    if args.plan == "mini":
        return tiers.tier1_plan(args.sweep_root, replicates=1)[:50]
    raise SystemExit(f"unknown plan {args.plan!r}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wyzantium_sim.doe")
    ap.add_argument("--plan", choices=("tier1", "tier2", "gate", "mini"))
    ap.add_argument("--plan-file", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--sweep-root", type=int, default=20260808,
                    help="D-032 sweep root seed (default: the committed "
                         "Phase 1 root)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--replicates", type=int, default=None,
                    help="tier1 only; default from tier1.json")
    ap.add_argument("--n", type=int, default=None,
                    help="tier2 (default n_min) / gate (required)")
    ap.add_argument("--usd-per-trial", type=float, default=0.0,
                    help="committed $/trial rate (A-004); 0 = local, "
                         "meter off")
    ap.add_argument("--ledger", type=Path, default=None)
    args = ap.parse_args(argv)
    if (args.plan is None) == (args.plan_file is None):
        raise SystemExit("exactly one of --plan / --plan-file")

    plan = build_plan(args)
    spend = None
    if args.usd_per_trial > 0.0:
        ledger = args.ledger or args.out / "spend_ledger.json"
        spend = SpendMeter(ledger, usd_per_trial=args.usd_per_trial)

    result = run_sweep(plan, args.out, workers=args.workers, spend=spend)
    print(f"ran={result.ran} skipped={result.skipped} total={len(plan)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
