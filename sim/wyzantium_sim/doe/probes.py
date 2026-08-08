"""T10 — probes: #33 solver convergence + A-004 cost measurement.

Convergence (#33, HOLES H-03): "halve timestep until success-rate delta
< 1% over a 500-trial probe; values logged per run in trial_header."
D-032 (f) reads the delta as absolute percentage points; the halt keeps
the coarser timestep of the converged pair (the finer one demonstrably
adds nothing — arbitrary code-level choice, labeled). run_batch is
injected (timestep_s, n) → success rate: the logic stays pure; the real
batch drives the DOE runner over a committed probe plan.

A-004 (PHASE1_PLAN §3): measured dollars per 1,000 trials. cost_probe
times an injected batch on a wall clock — wall time is the measurement
here, not part of any wire record, so the replay contract is untouched —
and converts with the instance's committed hourly price. commit_a004
writes one artifact per instance under sim/results/a004/; both the
winner and the loser are committed (ARCH §5).
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ConvergenceStep:
    timestep_s: float
    success_rate: float


@dataclass(frozen=True)
class ConvergenceResult:
    timestep_s: float     # the chosen (coarser converged) timestep
    halted: bool
    steps: tuple          # tuple[ConvergenceStep, ...] in probe order


def convergence_probe(run_batch, *, timestep0_s, probe_n=500,
                      threshold_pp=1.0, max_halvings=8) -> ConvergenceResult:
    dt = float(timestep0_s)
    steps = [ConvergenceStep(dt, float(run_batch(dt, probe_n)))]
    for _ in range(max_halvings):
        half = dt / 2.0
        steps.append(ConvergenceStep(half, float(run_batch(half, probe_n))))
        delta_pp = abs(steps[-1].success_rate
                       - steps[-2].success_rate) * 100.0
        if delta_pp < threshold_pp:
            return ConvergenceResult(dt, True, tuple(steps))
        dt = half
    return ConvergenceResult(dt, False, tuple(steps))


def cost_probe(run_batch, *, n_trials, usd_per_hour,
               clock=time.monotonic) -> dict:
    t0 = clock()
    run_batch(n_trials)
    wall_s = clock() - t0
    return {
        "n_trials": int(n_trials),
        "wall_s": float(wall_s),
        "usd_per_hour": float(usd_per_hour),
        "usd_per_1k_trials":
            float(usd_per_hour) * (wall_s / 3600.0) / n_trials * 1000.0,
    }


def commit_a004(result: dict, instance: dict, out_dir) -> Path:
    """One committed artifact per measured instance (winner AND loser)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{instance['name']}.json"
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"source": "A-004 (ARCHITECTURE §5; PHASE1_PLAN §3); "
                             "PHASE1_PARAMETERS #61",
                   "instance": dict(instance), **result}, f, indent=1)
    os.replace(tmp, path)
    return path
