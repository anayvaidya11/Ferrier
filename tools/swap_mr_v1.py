"""The mr_v1 curve swap — one command, rehearsed before it matters.

Real mode (late August, after the P-03 bench days):
  python tools/swap_mr_v1.py --out <dir> --workers 32 \
      --usd-per-1k 0.009502167853532263
  Reads the three real CSVs from research/data/, fits mr_v1 with the
  pre-registered rules (mr_ingest.build_mr_curveset — zero remaining
  modeling freedom), registers it (the ROADMAP protocol's explicit act),
  re-runs the committed tier1/tier2/gate plans on mr_v1 (seed-paired with
  the freeze: same SWEEP_ROOT, same tags → same seeds; the only changed
  input is the curve set), and writes before_after.json against the
  committed freeze_prior_v2 summary. Spend-metered per P-02.

Rehearsal mode (item 2, 2026-08-14):
  python tools/swap_mr_v1.py --rehearse --out sim/results/swap_rehearsal
  Same code path on synthetic CSVs generated from the ground-truth
  builders in sim/tests/test_mr_ingest.py, at miniature plan sizes, local,
  $0. Additionally asserts the fits recover the generating parameters
  (the committed test tolerances) and demonstrates the analysis pooling
  guard (MixedCurveSetsError) on a deliberately mixed directory.

Everything JSON lands via json.dump (F-002 discipline). Records are
hashed and freed (freeze_v2 pattern); regeneration is the audit path.
"""
import argparse
import dataclasses
import json
import shutil
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
sys.path.insert(0, str(TOOLS))
sys.path.insert(0, str(REPO / "sim"))

import freeze_v2  # noqa: E402  (sha_list, census_and_ci, SWEEP_ROOT)
from wyzantium_sim.analysis import dataset  # noqa: E402
from wyzantium_sim.doe import runner, tiers  # noqa: E402
from wyzantium_sim.perception import curves, mr_ingest  # noqa: E402

REHEARSAL_LABEL = ("SYNTHETIC REHEARSAL — not bench data; generated from "
                   "sim/tests/test_mr_ingest.py ground truth by "
                   "tools/swap_mr_v1.py --rehearse")
REAL_CSVS = ("mr001_mud_detection.csv", "mr002_lowlux_detection.csv",
             "mr003_flip_rate.csv")


def synth_csvs(out_dir):
    from tests import test_mr_ingest as gt
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for name, cols, rows in (
            ("mr001_synthetic.csv", gt.MR001_COLS, gt._mr001_rows()),
            ("mr002_synthetic.csv", gt.MR002_COLS, gt._mr002_rows()),
            ("mr003_synthetic.csv", gt.MR003_COLS, gt._mr003_rows())):
        p = out_dir / name
        p.write_text(gt._csv_text(cols, rows, comment=REHEARSAL_LABEL))
        paths.append(p)
    return paths


def assert_fit_recovery(report):
    """Rehearsal-only: the fits must recover the synthetic ground truth
    within the committed test tolerances (test_mr_ingest.py)."""
    from tests import test_mr_ingest as gt
    checks = (
        ("angle_exponent", report.angle_exponent_hat, gt.N_TRUE, 0.05),
        ("mud_f_c", report.mud_f_c_hat, gt.F_C_TRUE, 0.02),
        ("lux_knee", report.lux_knee_hat, gt.KNEE_TRUE, 1e-9),
        ("lux_floor", report.lux_floor_hat, gt.FLOOR_TRUE, 0.02),
        ("sigma_px", report.sigma_px_hat, gt.SIGMA_TRUE, 1e-9),
        ("flip_kappa", report.flip_kappa_hat, gt.KAPPA_TRUE, 0.1),
    )
    for name, got, want, tol in checks:
        if abs(got - want) > tol:
            raise SystemExit(f"rehearsal fit recovery FAILED: {name} "
                             f"{got} vs truth {want} (tol {tol})")
    print("[swap] fit recovery: all fitted parameters within committed "
          "tolerances of ground truth")


def run_slice(name, plan, curve_label, out, workers, usd_per_1k, ledger,
              curve_sets, keep_one=None):
    """Run one plan on one curve set; hash, census, free. Returns census."""
    rec_dir = out / f"records_{name}_{curve_label}"
    rec_dir.mkdir(parents=True, exist_ok=True)
    spend = (runner.SpendMeter(ledger, usd_per_trial=usd_per_1k / 1000.0)
             if usd_per_1k > 0 else None)
    print(f"[swap] {name} on {curve_label}: {len(plan)} trials", flush=True)
    runner.run_sweep(plan, rec_dir, workers=workers, spend=spend,
                     curve_sets=curve_sets)
    freeze_v2.sha_list(rec_dir, out / f"{name}_{curve_label}.sha256")
    rows = dataset.load_dataset(rec_dir, expect_curve_set=curve_label)
    if keep_one is not None:
        keep_one.mkdir(parents=True, exist_ok=True)
        first = sorted(rec_dir.glob("*.ndjson"))[0]
        shutil.copy2(first, keep_one / first.name)
    shutil.rmtree(rec_dir)
    return freeze_v2.census_and_ci(rows)


def on_curve_set(plan, name):
    return tuple(dataclasses.replace(
        p, sweep_point={**p.sweep_point, "curve_set": name}) for p in plan)


def guard_demo(mixed_dir):
    """The pooling guard must fire on a prior_v1 + mr_v1 mixture."""
    try:
        dataset.load_dataset(mixed_dir)
    except dataset.MixedCurveSetsError as e:
        print("[swap] pooling guard fired on the mixed directory (good)")
        return {"raised": "MixedCurveSetsError", "message": str(e)}
    raise SystemExit("pooling guard did NOT fire on a mixed directory — "
                     "do not proceed to a real swap")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rehearse", action="store_true")
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--mr-dir", default=str(REPO / "research" / "data"))
    ap.add_argument("--replicates", type=int, default=None)
    ap.add_argument("--tier2-n", type=int, default=None)
    ap.add_argument("--gate-n", type=int, default=None)
    ap.add_argument("--usd-per-1k", type=float, default=0.0)
    ap.add_argument("--before",
                    default=str(REPO / "sim" / "results" / "freeze_prior_v2"
                                / "freeze_summary.json"))
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    ledger = out / "spend_ledger_swap.json"
    label = REHEARSAL_LABEL if args.rehearse else (
        "mr_v1 swap (ROADMAP curve-swap protocol; P-03 bench data; "
        "seed-paired with freeze_prior_v2)")

    if args.rehearse:
        csvs = synth_csvs(out / "synthetic_csvs")
        args.replicates = args.replicates or 1
        args.tier2_n = args.tier2_n or 30
        args.gate_n = args.gate_n or 50
    else:
        csvs = [Path(args.mr_dir) / n for n in REAL_CSVS]
        missing = [str(p) for p in csvs if not p.exists()]
        if missing:
            sys.exit("real MR CSVs not found: " + ", ".join(missing)
                     + " — collect the P-03 bench data first, or use "
                       "--rehearse")
        args.gate_n = args.gate_n or 5000   # D-038

    # 1. Fit with the pre-registered rules; 2. register (the explicit act).
    cs, report = mr_ingest.build_mr_curveset(*csvs)
    with open(out / "mr_v1_curveset.json", "w") as fh:
        json.dump({"source": label} | dataclasses.asdict(cs), fh, indent=1)
    with open(out / "mr_fit_report.json", "w") as fh:
        json.dump({"source": label} | dataclasses.asdict(report), fh,
                  indent=1)
    if args.rehearse:
        assert_fit_recovery(report)
    curves.register(cs)

    plans = {
        "tier1": tiers.tier1_plan(freeze_v2.SWEEP_ROOT,
                                  replicates=args.replicates),
        "tier2": tiers.tier2_plan(freeze_v2.SWEEP_ROOT, n=args.tier2_n),
        "gate": tiers.gate_plan(freeze_v2.SWEEP_ROOT, n=args.gate_n),
    }

    # 3. Re-run. Rehearsal runs BOTH sides seed-paired at miniature scale;
    # the real swap runs mr_v1 only (before = the committed freeze).
    mixed = out / "guard_demo_records"
    after = {}
    before = {}
    for name, plan in plans.items():
        if args.rehearse:
            before[name] = run_slice(
                name, plan, "prior_v1", out, args.workers, args.usd_per_1k,
                ledger, (), keep_one=mixed if name == "tier1" else None)
        after[name] = run_slice(
            name, on_curve_set(plan, cs.name), cs.name, out, args.workers,
            args.usd_per_1k, ledger, (cs,),
            keep_one=(mixed if args.rehearse and name == "tier1"
                      else None))
    if not args.rehearse:
        before = json.loads(Path(args.before).read_text())
        before = {k: before[k] for k in plans}

    # 4. Before/after — always both numbers, never a delta alone.
    with open(out / "before_after.json", "w") as fh:
        json.dump({
            "source": label,
            "curve_sets": {"before": "prior_v1", "after": cs.name},
            "seed_pairing": ("same SWEEP_ROOT + tags -> same seeds; the "
                             "curve set is the only changed input"),
            "plans": {n: {"before": before[n], "after": after[n]}
                      for n in plans},
        }, fh, indent=1)

    # 5. Pooling-guard demonstration (rehearsal only — real records from
    # the freeze are not retained).
    if args.rehearse:
        demo = guard_demo(mixed)
        with open(out / "guard_demo.json", "w") as fh:
            json.dump({"source": label} | demo, fh, indent=1)
        shutil.rmtree(mixed)

    print(f"[swap] done -> {out}", flush=True)


if __name__ == "__main__":
    main()
