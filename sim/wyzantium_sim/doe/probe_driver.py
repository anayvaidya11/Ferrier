"""Probe driver — wires the T10 probes to the real batch (PHASE1_PLAN §3).

The probes in doe/probes.py are pure (injected run_batch); this module
supplies the real batch: the committed nominal cell (D-032 (a)) replicated
with distinct seeds under the D-032 (b) seed rule — "handoff states sampled
from the §5 tolerance budget under D-019 at ×1, not idealized centers"
(PHASE1_PLAN §3): the per-trial chassis-error and perception substreams
spread the handoff states; nothing here idealizes them.

Subcommands:

  conv33  — #33 convergence probe (H-03; D-032 (f) absolute-pp reading).
            Each timestep batch runs in its own subdirectory: trial_id does
            not encode solver settings, so sharing a directory would let the
            resume oracle skip re-runs at a finer dt.
  a004    — A-004 cost measurement: wall-clock a fresh N-trial nominal batch,
            convert with the instance's committed hourly price, write the
            artifact via commit_a004 (both instances committed, ARCH §5).

Success rate: a trial's outcome is the trial_result line's "outcome"
(classify/outcomes.py, T9); success ⇔ outcome == "success".
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from wyzantium_sim import scenarios
from wyzantium_sim.contact.engine import SolverSettings
from wyzantium_sim.doe import probes, runner, tiers
from wyzantium_sim.trial import TRIAL_TIMESTEP_S


def nominal_plan(sweep_root, n, prefix) -> tuple:
    """n distinct-seed replicates of the committed nominal cell.

    Tags follow the D-032 (b) scheme ("{prefix}:{i:05d}", unique within the
    probe); seeds are the pure function of (sweep_root, tag), so probe plans
    are order-independent and resume-stable like every other plan.
    """
    nominal = scenarios.build_sweep_point(
        **tiers.load_nominal()["sweep_point"])
    return tuple(
        tiers.PlannedTrial(f"{prefix}:{i:05d}",
                           tiers.derive_seed(sweep_root, f"{prefix}:{i:05d}"),
                           nominal)
        for i in range(n))


def batch_success_rate(paths) -> float:
    """Fraction of records whose trial_result outcome is "success"."""
    n_success = 0
    for path in paths:
        last = Path(path).read_text(encoding="utf-8").rstrip("\n")
        last = last[last.rfind("\n") + 1:]
        if json.loads(last)["outcome"] == "success":
            n_success += 1
    return n_success / len(paths)


def conv33(out_dir, *, sweep_root, probe_n=500, timestep0_s=TRIAL_TIMESTEP_S,
           workers=1) -> probes.ConvergenceResult:
    out_dir = Path(out_dir)

    def run_batch(dt, n):
        batch_dir = out_dir / f"dt_{dt:.1e}"
        plan = nominal_plan(sweep_root, n, "probe33")
        result = runner.run_sweep(plan, batch_dir, workers=workers,
                                  solver=SolverSettings(timestep_s=dt))
        return batch_success_rate(result.paths)

    result = probes.convergence_probe(run_batch, timestep0_s=timestep0_s,
                                      probe_n=probe_n)
    artifact = {
        "source": "#33 (H-03); D-032 (f) absolute-pp reading; probe_driver",
        "sweep_root": sweep_root,
        "probe_n": probe_n,
        "chosen_timestep_s": result.timestep_s,
        "halted": result.halted,
        "steps": [{"timestep_s": s.timestep_s, "success_rate": s.success_rate}
                  for s in result.steps],
    }
    with open(out_dir / "conv33.json", "w", encoding="utf-8") as f:
        json.dump(artifact, f, indent=2)
    return result


def a004(out_dir, *, sweep_root, n_trials, usd_per_hour, instance,
         workers=1, timestep_s=TRIAL_TIMESTEP_S) -> Path:
    """Fresh-directory cost measurement — resume skips would corrupt the
    wall-clock, so any prior batch directory is removed first."""
    out_dir = Path(out_dir)
    batch_dir = out_dir / "batch"
    if batch_dir.exists():
        shutil.rmtree(batch_dir)
    plan = nominal_plan(sweep_root, n_trials, "a004")

    def run_batch(n):
        assert n == len(plan)
        runner.run_sweep(plan, batch_dir, workers=workers,
                         solver=SolverSettings(timestep_s=timestep_s))

    result = probes.cost_probe(run_batch, n_trials=n_trials,
                               usd_per_hour=usd_per_hour)
    result["success_rate"] = batch_success_rate(
        sorted(batch_dir.glob("*.ndjson")))
    result["workers"] = workers
    result["timestep_s"] = timestep_s
    return probes.commit_a004(result, instance, out_dir)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wyzantium_sim.doe.probe_driver")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p33 = sub.add_parser("conv33")
    p33.add_argument("--out", type=Path, required=True)
    p33.add_argument("--sweep-root", type=int, default=20260808)
    p33.add_argument("--probe-n", type=int, default=500)
    p33.add_argument("--timestep0", type=float, default=TRIAL_TIMESTEP_S)
    p33.add_argument("--workers", type=int, default=1)

    pa = sub.add_parser("a004")
    pa.add_argument("--out", type=Path, required=True)
    pa.add_argument("--sweep-root", type=int, default=20260808)
    pa.add_argument("--n", type=int, default=1000)
    pa.add_argument("--usd-per-hour", type=float, required=True)
    pa.add_argument("--instance-json", type=str, required=True,
                    help='e.g. \'{"type":"c7i.8xlarge","market":"spot"}\'')
    pa.add_argument("--workers", type=int, default=1)
    pa.add_argument("--timestep", type=float, default=TRIAL_TIMESTEP_S)

    args = ap.parse_args(argv)
    if args.cmd == "conv33":
        result = conv33(args.out, sweep_root=args.sweep_root,
                        probe_n=args.probe_n, timestep0_s=args.timestep0,
                        workers=args.workers)
        print(f"chosen_timestep_s={result.timestep_s} halted={result.halted}")
        return 0
    if args.cmd == "a004":
        path = a004(args.out, sweep_root=args.sweep_root, n_trials=args.n,
                    usd_per_hour=args.usd_per_hour,
                    instance=json.loads(args.instance_json),
                    workers=args.workers, timestep_s=args.timestep)
        print(f"a004 artifact: {path}")
        return 0
    raise SystemExit(f"unknown cmd {args.cmd!r}")


if __name__ == "__main__":
    raise SystemExit(main())
