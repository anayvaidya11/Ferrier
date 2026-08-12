"""Build freeze_prior_v2: the post-R01-fix pre-swap freeze (D-041..D-046).

Runs the three committed plans (tiers.tier1_plan / tier2_plan / gate_plan at
the committed sweep root), writes per-record sha256 lists, summaries,
feasibility, figures, and MANIFEST.json — all via json.dump (the v1 manifest
was assembled through an unquoted shell heredoc; that is how R01 F-002
happened, and this script is the fix's structural half).

Usage (full freeze, on the provisioned instance):
  WYZ_INSTANCE_CLASS=c7i.8xlarge python tools/freeze_v2.py \
      --out /home/ubuntu/runs/freeze_prior_v2 --workers 32 \
      --usd-per-1k 0.009502167853532263
Miniature local validation:
  python tools/freeze_v2.py --out /tmp/fv2 --replicates 1 --tier2-n 8 \
      --gate-n 8 --workers 8 --usd-per-1k 0
"""
import argparse
import hashlib
import json
import platform
import shutil
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "sim"))

from wyzantium_sim import scenarios, trial  # noqa: E402
from wyzantium_sim.analysis import charts, curves, dataset, feasibility  # noqa: E402
from wyzantium_sim.doe import runner, tiers  # noqa: E402

SWEEP_ROOT = 20260808   # the committed Phase 1 root (D-032; freeze v1)


def run_plan(plan, out_dir, workers, usd_per_1k, ledger):
    out_dir.mkdir(parents=True, exist_ok=True)
    spend = (runner.SpendMeter(ledger, usd_per_trial=usd_per_1k / 1000.0)
             if usd_per_1k > 0 else None)
    return runner.run_sweep(plan, out_dir, workers=workers, spend=spend)


def sha_list(records_dir, out_file):
    lines = []
    for p in sorted(records_dir.glob("*.ndjson")):
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        lines.append(f"{h}  {p.name}")
    out_file.write_text("\n".join(lines) + "\n")
    return len(lines)


def census_and_ci(rows):
    n = len(rows)
    k = sum(r.outcome == "success" for r in rows)
    lo, hi = curves.wilson_ci(k, n)
    return {"n": n, "success": k, "rate": (k / n if n else 0.0),
            "ci95_wilson": [lo, hi],
            "census": dict(Counter(r.outcome for r in rows))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--replicates", type=int, default=None)
    ap.add_argument("--tier2-n", type=int, default=None)
    ap.add_argument("--gate-n", type=int, default=5000)   # D-038
    ap.add_argument("--usd-per-1k", type=float, default=0.0)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    ledger = out / "spend_ledger_v2.json"

    plans = {
        "tier1": tiers.tier1_plan(SWEEP_ROOT, replicates=args.replicates),
        "tier2": tiers.tier2_plan(SWEEP_ROOT, n=args.tier2_n),
        "gate": tiers.gate_plan(SWEEP_ROOT, n=args.gate_n),
    }
    counts, digests = {}, []
    rows_by_plan = {}
    for name, plan in plans.items():
        rec_dir = out / f"records_{name}"
        print(f"[freeze_v2] {name}: {len(plan)} trials", flush=True)
        run_plan(plan, rec_dir, args.workers, args.usd_per_1k, ledger)
        counts[name] = sha_list(rec_dir, out / f"{name}.sha256")
        digests.append((name, hashlib.sha256(
            (out / f"{name}.sha256").read_bytes()).hexdigest()))
        rows_by_plan[name] = dataset.load_dataset(rec_dir)
        # Records are not retained (manifest records_storage) — hash, load
        # the analysis rows, then free the disk before the next plan (full
        # contact records total tens of GB across the three plans).
        shutil.rmtree(rec_dir)
        print(f"[freeze_v2] {name}: hashed {counts[name]}, records freed",
              flush=True)

    nominal = tiers.load_nominal()["sweep_point"]
    summary = {
        "source": ("post-R01 pre-swap prior_v2 freeze (P-08 sitting, "
                   "D-039..D-046; PHASE1_PLAN week-4 step; ROADMAP "
                   "curve-swap protocol)"),
        "tier1": census_and_ci(rows_by_plan["tier1"]),
        "tier2": census_and_ci(rows_by_plan["tier2"]),
        "gate": census_and_ci(rows_by_plan["gate"]),
    }
    with open(out / "freeze_summary.json", "w") as fh:
        json.dump(summary, fh, indent=1)

    with open(out / "feasibility_63.json", "w") as fh:
        json.dump(feasibility(rows_by_plan["tier1"], nominal), fh, indent=1)

    charts.render_all(rows_by_plan["tier1"], nominal, out / "figures")

    total = sum(counts.values())
    manifest = {
        "source": summary["source"],
        "code_git_sha": trial._git_sha(),
        "engine": "mujoco (engine of record, D-039)",
        "instance": trial._instance_id() | {
            "platform": platform.platform(), "python": platform.python_version()},
        "curve_set": "prior_v1",
        "decisions_applied": ["D-039", "D-040", "D-041", "D-042", "D-043",
                              "D-044", "D-045", "D-046"],
        "plans": {"tier1": f"tiers.tier1_plan({SWEEP_ROOT})",
                  "tier2": f"tiers.tier2_plan({SWEEP_ROOT})",
                  "gate": f"tiers.gate_plan({SWEEP_ROOT}, {args.gate_n})"},
        "counts": counts,
        "dataset_digest": {name: d for name, d in digests},
        "records_storage": (
            "not retained — records regenerate deterministically from this "
            "manifest (code sha + committed plans + seed rule); the "
            "per-record sha256 lists verify regeneration ON THIS INSTANCE "
            "CLASS ONLY (byte-identity is per-instance-class, R01 F-018; "
            "off-platform auditors verify trial_id reproduction and "
            "on-platform digests). Regeneration cost at the committed "
            f"A-004 rate: ~${total * args.usd_per_1k / 1000.0:.2f}."),
    }
    with open(out / "MANIFEST.json", "w") as fh:
        json.dump(manifest, fh, indent=1)
    print(f"[freeze_v2] done: {counts} -> {out}", flush=True)


if __name__ == "__main__":
    main()
