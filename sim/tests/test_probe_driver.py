"""Probe driver (doe/probe_driver.py): plan determinism, solver passthrough,
success-rate parsing, per-dt directory isolation."""

import json

from wyzantium_sim.contact.engine import SolverSettings
from wyzantium_sim.doe import probe_driver, runner


class TestNominalPlan:
    def test_deterministic_and_distinct_seeds(self):
        a = probe_driver.nominal_plan(20260808, 8, "probe33")
        b = probe_driver.nominal_plan(20260808, 8, "probe33")
        assert a == b
        assert len({p.seed for p in a}) == 8

    def test_prefix_scopes_seeds(self):
        a = probe_driver.nominal_plan(20260808, 4, "probe33")
        b = probe_driver.nominal_plan(20260808, 4, "a004")
        assert {p.seed for p in a}.isdisjoint({p.seed for p in b})

    def test_gate_probe_plan_has_n_distinct_seeds(self):
        plan = probe_driver.probe_plan("gate", 33, 8)
        assert len(plan) == 8
        assert len({p.seed for p in plan}) == 8


class TestSolverPassthrough:
    def test_header_carries_injected_timestep(self, tmp_path):
        plan = probe_driver.nominal_plan(20260808, 1, "probe33")
        result = runner.run_sweep(plan, tmp_path,
                                  solver=SolverSettings(timestep_s=1e-4))
        header = json.loads(
            result.paths[0].read_text(encoding="utf-8").splitlines()[0])
        assert header["solver"]["timestep_s"] == 1e-4

    def test_default_solver_unchanged(self, tmp_path):
        from wyzantium_sim.trial import TRIAL_TIMESTEP_S
        plan = probe_driver.nominal_plan(20260808, 1, "probe33")
        result = runner.run_sweep(plan, tmp_path)
        header = json.loads(
            result.paths[0].read_text(encoding="utf-8").splitlines()[0])
        assert header["solver"]["timestep_s"] == TRIAL_TIMESTEP_S


class TestBatchSuccessRate:
    def test_counts_success_outcomes(self, tmp_path):
        for i, outcome in enumerate(["success", "IS8-2", "success"]):
            p = tmp_path / f"t{i}.ndjson"
            p.write_text('{"kind":"header"}\n'
                         f'{{"outcome":"{outcome}"}}\n', encoding="utf-8")
        rate = probe_driver.batch_success_rate(sorted(tmp_path.glob("*.ndjson")))
        assert rate == 2 / 3
