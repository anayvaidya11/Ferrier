"""T10 — probes: #33 convergence (halts on <1% delta) + A-004 cost.

Gate (PHASE1_PLAN §4 row T10): convergence probe halts on <1% delta.
#33 (HOLES H-03): halve timestep until success-rate delta < 1% over a
500-trial probe; D-032 (f) reads the delta as absolute percentage
points. The batch runner and the clock are injected, so the probe logic
is exercised synthetically; real batches run the DOE runner.
"""
import pytest

from wyzantium_sim.doe import probes


def synthetic_rates(rates_by_dt, calls=None):
    def run_batch(timestep_s, n):
        if calls is not None:
            calls.append((timestep_s, n))
        return rates_by_dt[timestep_s]
    return run_batch


class TestConvergenceProbe:
    def test_halts_when_the_halving_moves_the_rate_less_than_1pp(self):
        calls = []
        result = probes.convergence_probe(
            synthetic_rates({1e-3: 0.50, 5e-4: 0.60, 2.5e-4: 0.605},
                            calls),
            timestep0_s=1e-3)
        assert result.halted
        # 0.50→0.60 is 10 pp (continue); 0.60→0.605 is 0.5 pp (halt);
        # the coarser of the converged pair is the chosen timestep
        assert result.timestep_s == 5e-4
        assert [s.timestep_s for s in result.steps] == [1e-3, 5e-4, 2.5e-4]
        assert calls == [(1e-3, 500), (5e-4, 500), (2.5e-4, 500)]

    def test_exactly_1pp_does_not_halt(self):
        result = probes.convergence_probe(
            synthetic_rates({1e-3: 0.50, 5e-4: 0.51, 2.5e-4: 0.52,
                             1.25e-4: 0.53, 6.25e-5: 0.54}),
            timestep0_s=1e-3, max_halvings=4)
        assert not result.halted          # every delta is exactly 1.0 pp

    def test_max_halvings_exhausts_without_convergence(self):
        rates = {1e-3 / 2 ** k: 0.1 * k for k in range(9)}
        result = probes.convergence_probe(
            synthetic_rates(rates), timestep0_s=1e-3, max_halvings=3)
        assert not result.halted
        assert len(result.steps) == 4     # dt0 + 3 halvings

    def test_probe_n_is_passed_through(self):
        calls = []
        probes.convergence_probe(
            synthetic_rates({1e-3: 0.5, 5e-4: 0.5}, calls),
            timestep0_s=1e-3, probe_n=17)
        assert calls == [(1e-3, 17), (5e-4, 17)]


class TestCostProbe:
    def test_usd_per_1k_from_wall_time_and_hourly_price(self):
        ticks = iter([100.0, 100.0 + 7200.0])   # two hours of wall time
        result = probes.cost_probe(lambda n: None, n_trials=1000,
                                   usd_per_hour=3.0,
                                   clock=lambda: next(ticks))
        assert result["n_trials"] == 1000
        assert result["wall_s"] == pytest.approx(7200.0)
        assert result["usd_per_1k_trials"] == pytest.approx(6.0)

    def test_batch_receives_the_trial_count(self):
        seen = []
        ticks = iter([0.0, 60.0])
        probes.cost_probe(seen.append, n_trials=250, usd_per_hour=1.0,
                          clock=lambda: next(ticks))
        assert seen == [250]

    def test_commit_a004_writes_the_instance_artifact(self, tmp_path):
        ticks = iter([0.0, 3600.0])
        result = probes.cost_probe(lambda n: None, n_trials=500,
                                   usd_per_hour=2.0,
                                   clock=lambda: next(ticks))
        path = probes.commit_a004(
            result, {"name": "cpu-c7a-8xl", "provider": "retail"},
            tmp_path)
        assert path == tmp_path / "cpu-c7a-8xl.json"
        import json
        data = json.loads(path.read_text())
        assert data["instance"]["provider"] == "retail"
        assert data["usd_per_1k_trials"] == pytest.approx(4.0)
        assert "A-004" in data["source"]
