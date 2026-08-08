"""T10 — resumable sweep runner + spend meter (D-032 (c)/(d)).

Execution: a plan (tuple of tiers.PlannedTrial) maps to one record path
per trial — precomputed from the D-032 seed rule and the trial-id scheme,
so resume never depends on execution order. A trial whose record already
validates on disk is skipped (the D-032 resume oracle:
validate_trial_file == [], never bare existence — sound because the
record writer is atomic); anything else runs and overwrites.

Spend (D-032 (c)): the ceiling defaults from sim/scenarios/spend_p02.json
(P-02/A-011(c)) and is never hardcoded; cumulative spend persists in a
JSON ledger (atomic tmp+replace). Two hard stops, both raising
SpendCeilingError — the recorded-amendment path, never a quiet overrun:
check_projected() before a sweep starts (risk #3's "projected overrun"),
charge_before() ahead of each dispatch (defense-in-depth: with a constant
rate and an exclusive ledger the projected check subsumes it; it exists
for a ledger shared across processes).

Workers: workers=1 runs inline on one engine (the byte-identity contract
holds for reused engines — run_trial loads per call); workers>1 uses a
process pool with one engine per worker. Records are deterministic per
trial, so worker scheduling cannot change any byte.
"""

from __future__ import annotations

import json
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path

from wirefmt import validator
from wyzantium_sim import scenarios, trial
from wyzantium_sim.contact.mujoco_engine import MuJoCoEngine
from wyzantium_sim.doe import tiers


class SpendCeilingError(RuntimeError):
    """The P-02 ceiling would be crossed — recorded amendment, never a
    quiet overrun (A-011 (c))."""


class SpendMeter:
    def __init__(self, ledger_path, *, usd_per_trial, ceiling_usd=None):
        self.ledger_path = Path(ledger_path)
        self.usd_per_trial = float(usd_per_trial)
        self.ceiling_usd = float(
            tiers.load_spend()["ceiling_usd"]
            if ceiling_usd is None else ceiling_usd)
        if self.ledger_path.is_file():
            ledger = json.loads(self.ledger_path.read_text())
            self.spent_usd = float(ledger["spent_usd"])
            self.trials_recorded = int(ledger["trials"])
        else:
            self.spent_usd = 0.0
            self.trials_recorded = 0

    def check_projected(self, n_trials: int) -> None:
        projected = self.spent_usd + n_trials * self.usd_per_trial
        if projected > self.ceiling_usd:
            raise SpendCeilingError(
                f"projected ${projected:.2f} for {n_trials} trials crosses "
                f"the ${self.ceiling_usd:.2f} ceiling "
                f"(spent ${self.spent_usd:.2f}) — recorded amendment "
                "required (P-02/A-011)")

    def charge_before(self) -> None:
        if self.spent_usd + self.usd_per_trial > self.ceiling_usd:
            raise SpendCeilingError(
                f"next trial would cross the ${self.ceiling_usd:.2f} "
                f"ceiling (spent ${self.spent_usd:.2f}) — recorded "
                "amendment required (P-02/A-011)")

    def record(self, tag: str) -> None:
        self.spent_usd += self.usd_per_trial
        self.trials_recorded += 1
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = f"{self.ledger_path}.tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump({"source": "D-032 (c); P-02/A-011",
                       "spent_usd": self.spent_usd,
                       "trials": self.trials_recorded,
                       "last_tag": tag}, f)
        os.replace(tmp, self.ledger_path)


def record_complete(path) -> bool:
    """The D-032 resume oracle. Malformed files count as incomplete."""
    path = Path(path)
    if not path.is_file():
        return False
    try:
        return validator.validate_trial_file(path) == []
    except Exception:
        return False


@dataclass(frozen=True)
class SweepResult:
    ran: int
    skipped: int
    paths: tuple  # tuple[Path, ...] in plan order


_WORKER_ENGINE = None


def _init_worker(engine_factory):
    global _WORKER_ENGINE
    _WORKER_ENGINE = engine_factory()


def _run_planned(seed, sweep_point, out_dir):
    return trial.run_trial(seed, sweep_point, _WORKER_ENGINE,
                           sweep_point["curve_set"], out_dir=Path(out_dir))


def run_sweep(plan, out_dir, *, workers=1, engine_factory=MuJoCoEngine,
              spend=None) -> SweepResult:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    engine = engine_factory()
    engine_name = engine.engine_id["name"]

    paths, pending = [], []
    for p in plan:
        built = scenarios.build_sweep_point(**p.sweep_point)
        path = out_dir / f"{trial._trial_id(p.seed, built, engine_name)}.ndjson"
        paths.append(path)
        if not record_complete(path):
            pending.append(p)

    if spend is not None:
        spend.check_projected(len(pending))

    if workers <= 1:
        for p in pending:
            if spend is not None:
                spend.charge_before()
            trial.run_trial(p.seed, p.sweep_point, engine,
                            p.sweep_point["curve_set"], out_dir=out_dir)
            if spend is not None:
                spend.record(p.tag)
    else:
        with ProcessPoolExecutor(
                max_workers=workers, initializer=_init_worker,
                initargs=(engine_factory,)) as pool:
            futures = {}
            for p in pending:
                if spend is not None:
                    spend.charge_before()
                futures[pool.submit(_run_planned, p.seed, p.sweep_point,
                                    str(out_dir))] = p
            for fut in as_completed(futures):
                fut.result()  # surface worker exceptions
                if spend is not None:
                    spend.record(futures[fut].tag)

    return SweepResult(ran=len(pending), skipped=len(plan) - len(pending),
                       paths=tuple(paths))
