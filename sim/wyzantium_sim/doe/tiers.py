"""T10 — tier generators: committed grids → deterministic trial plans.

Tier definitions are data (sim/scenarios/{nominal,tier1,tier2}.json, plus
gate_moderate.json for the D-029 band and spend_p02.json for the ceiling),
transcription-tested and never hardcoded here — the gate_moderate.json
discipline (D-029) extended to the whole DOE (D-032). This module turns
them into PlannedTrial tuples; doe/runner.py executes plans.

Seed rule (D-032): a trial's root seed is the top 63 bits of
sha1("{sweep_root}|{tag}"), where the tag is unique within the sweep
("tier1:{axis}={value}:r{i}", "tier2:{i}", "gate:{i}"). Pure function of
(sweep_root, tag): order-independent, resume-stable, and replicates at the
same sweep point get distinct seeds — so trial_ids (engine-seed-sweephash)
never collide and nothing is silently overwritten.

Samplers draw from per-plan generator streams derived the same way
(derive_seed(root, "sampler:<plan>") → the reserved "doe" substream), so
tier2 and gate sampling are deterministic and mutually independent.

Tier-1 dedupe (D-032): grid points equal to the nominal value collapse
into one shared nominal cell — the marginal curves join on it instead of
re-running identical points once per axis.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from wyzantium_sim import rng, scenarios


def _load(name):
    with open(scenarios.SCENARIO_DIR / name, "r", encoding="utf-8") as f:
        return json.load(f)


def load_nominal():
    return _load("nominal.json")


def load_tier1():
    return _load("tier1.json")


def load_tier2():
    return _load("tier2.json")


def load_spend():
    return _load("spend_p02.json")


def derive_seed(sweep_root, tag: str) -> int:
    digest = hashlib.sha1(f"{int(sweep_root)}|{tag}".encode()).digest()
    return int.from_bytes(digest[:8], "big") >> 1


def _sampler(sweep_root, plan_name: str):
    return rng.substream(derive_seed(sweep_root, f"sampler:{plan_name}"),
                         "doe")


@dataclass(frozen=True)
class Tier1Cell:
    axis: str | None      # None → the shared nominal cell
    value: object
    sweep_point: dict


@dataclass(frozen=True)
class PlannedTrial:
    tag: str
    seed: int
    sweep_point: dict


def tier1_cells() -> tuple[Tier1Cell, ...]:
    nominal = load_nominal()["sweep_point"]
    grids = load_tier1()["grids"]
    cells = [Tier1Cell(None, None, dict(nominal))]
    for axis, grid in grids.items():
        for value in grid["cells"]:
            if value == nominal[axis]:
                continue  # collapses into the shared nominal cell
            cells.append(Tier1Cell(
                axis, value,
                scenarios.build_sweep_point(**{**nominal, axis: value})))
    return tuple(cells)


def _replicated(cells_with_names, sweep_root, replicates):
    plan = []
    for name, sweep_point in cells_with_names:
        for i in range(replicates):
            tag = f"{name}:r{i:03d}"
            plan.append(PlannedTrial(tag, derive_seed(sweep_root, tag),
                                     sweep_point))
    return tuple(plan)


def tier1_plan(sweep_root, replicates=None) -> tuple[PlannedTrial, ...]:
    if replicates is None:
        replicates = int(load_tier1()["replicates_default"])
    named = [("tier1:nominal" if c.axis is None
              else f"tier1:{c.axis}={json.dumps(c.value)}", c.sweep_point)
             for c in tier1_cells()]
    return _replicated(named, sweep_root, replicates)


def _lhs_u(gen, n):
    """One LHS column: a permuted stratum index plus in-stratum jitter."""
    return (gen.permutation(n) + gen.random(n)) / n


def _lhs_column(gen, dom, n):
    u = _lhs_u(gen, n)
    if "cells" in dom:
        cells = dom["cells"]
        return [cells[min(int(x * len(cells)), len(cells) - 1)] for x in u]
    if "int_lo" in dom:
        span = dom["int_hi"] - dom["int_lo"] + 1
        return [int(dom["int_lo"] + min(int(x * span), span - 1)) for x in u]
    return [float(dom["lo"] + x * (dom["hi"] - dom["lo"])) for x in u]


def tier2_plan(sweep_root, n=None) -> tuple[PlannedTrial, ...]:
    t2 = load_tier2()
    n = int(t2["n_min"] if n is None else n)
    nominal = load_nominal()["sweep_point"]
    gen = _sampler(sweep_root, "tier2")
    columns = {axis: _lhs_column(gen, dom, n)
               for axis, dom in t2["domains"].items()}
    plan = []
    for i in range(n):
        point = {**nominal,
                 **{axis: columns[axis][i] for axis in columns}}
        tag = f"tier2:{i:05d}"
        plan.append(PlannedTrial(tag, derive_seed(sweep_root, tag),
                                 scenarios.build_sweep_point(**point)))
    return tuple(plan)


def _band_value(gen, spec):
    if "cells" in spec:
        return spec["cells"][int(gen.integers(len(spec["cells"])))]
    if "value" in spec:
        return spec["value"]
    return float(gen.uniform(spec["lo"], spec["hi"]))


def gate_plan(sweep_root, n) -> tuple[PlannedTrial, ...]:
    """Uniform samples over the D-029 moderate band (read from
    gate_moderate.json only), system parameters at nominal. D-046(b): the
    gate's encounter-geometry marginalization is real — host pitch/roll
    sample the committed D-024 envelope per trial (the JSON's additive
    encounter_geometry_realization block; the band block stays verbatim)."""
    gate = scenarios.load_gate_moderate()
    band = gate["band"]
    geometry = {axis: spec for axis, spec
                in gate.get("encounter_geometry_realization", {}).items()
                if isinstance(spec, dict)}
    nominal = load_nominal()["sweep_point"]
    gen = _sampler(sweep_root, "gate")
    plan = []
    for i in range(int(n)):
        point = {**nominal,
                 **{axis: _band_value(gen, spec)
                    for axis, spec in band.items()},
                 **{axis: _band_value(gen, spec)
                    for axis, spec in geometry.items()}}
        tag = f"gate:{i:05d}"
        plan.append(PlannedTrial(tag, derive_seed(sweep_root, tag),
                                 scenarios.build_sweep_point(**point)))
    return tuple(plan)
