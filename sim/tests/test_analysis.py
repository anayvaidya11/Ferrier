"""T12 gate: golden mini-dataset → known curve values; #63 pinned
cross-check; pooling guard refuses mixed curve sets."""

import json

import pytest

from wyzantium_sim import scenarios
from wyzantium_sim.analysis import (
    MixedCurveSetsError, TrialRow, attempt_splits, feasibility,
    load_dataset, outcome_census, refusal_damage, sensitivity,
)
from wyzantium_sim.analysis.feasibility import window
from wyzantium_sim.doe import tiers

NOMINAL = tiers.load_nominal()["sweep_point"]


def row(outcome="success", first=None, false_capture=None, **axes):
    sp = scenarios.build_sweep_point(**{**NOMINAL, **axes})
    return TrialRow(
        trial_id="t", seed=1, engine="mujoco", curve_set=sp["curve_set"],
        sweep_point=sp, outcome=outcome,
        first_attempt_success=(outcome == "success" if first is None
                               else first),
        attempts_used=1, t_total=1.0,
        handoff_reached=outcome == "success", false_capture=false_capture)


class TestSensitivity:
    def test_golden_marginal_values(self):
        rows = ([row()] * 4
                + [row(outcome="IS8-1", outer_occlusion=0.3)] * 1
                + [row(outer_occlusion=0.3)] * 3)
        curve = sensitivity(rows, NOMINAL)["outer_occlusion"]
        by_value = {s.value: s for s in curve}
        assert by_value[0.0].success == 1.0 and by_value[0.0].n == 4
        assert by_value[0.3].success == 0.75 and by_value[0.3].n == 4
        assert by_value[0.3].ci_lo < 0.75 < by_value[0.3].ci_hi

    def test_multi_axis_rows_excluded(self):
        rows = [row(), row(outer_occlusion=0.3, rain=0.2)]
        curve = sensitivity(rows, NOMINAL)
        assert all(len([s for s in stats if s.value != NOMINAL[axis]]) == 0
                   for axis, stats in curve.items())


class TestRefusalDamage:
    def test_golden_tradeoff_values(self):
        rows = (
            [row()] * 3 + [row(outcome="IS8-1")] * 1          # 0.85 nominal
            + [row(conf_min_attempt=0.5)] * 2                  # committed…
            + [row(outcome="IS8-16", conf_min_attempt=0.5,
                   false_capture=1)] * 2)                      # …and damaged
        curve = refusal_damage(rows, NOMINAL)
        by_t = {s.threshold: s for s in curve}
        assert by_t[0.85].refusal == 0.25
        assert by_t[0.85].success == 0.75
        assert by_t[0.85].contact_failure == 0.0
        assert by_t[0.5].contact_failure == 0.5
        assert by_t[0.5].false_capture_rate == 0.5
        assert by_t[0.5].refusal == 0.0


class TestSplitsAndCensus:
    def test_first_vs_overall(self):
        rows = [row(), row(first=False), row(outcome="IS8-1")]
        s = attempt_splits(rows)
        assert s.n == 3
        assert s.first_attempt_success == pytest.approx(1 / 3)
        assert s.overall_success == pytest.approx(2 / 3)

    def test_census(self):
        rows = [row(), row(outcome="IS8-1"), row(outcome="IS8-1")]
        assert outcome_census(rows) == {"success": 1, "IS8-1": 2}


class TestFeasibility:
    def test_63_pinned_cross_check(self):
        # studies/H04 Addendum A1: (0.2, 300 kg) → k_max ≈ 17 N/mm
        k_min, k_max = window(0.2, 300.0)
        assert k_max == pytest.approx(16.82, abs=0.02)
        rows = [row(stiffness_k_n_mm=k)
                for k in (1.0, 3.0, 10.0, 30.0, 70.0)]
        out = feasibility(rows, NOMINAL)
        cls = next(c for c in out["classes"]
                   if c["mu_trac"] == 0.2 and c["m_rv_kg"] == 300.0)
        assert cls["mask"]["30.0"] is False
        assert cls["mask"]["70.0"] is False
        assert cls["mask"]["1.0"] and cls["mask"]["3.0"] and cls["mask"]["10.0"]

    def test_band_and_intersection(self):
        rows = ([row(stiffness_k_n_mm=1.0, outcome="IS8-17")] * 2
                + [row(stiffness_k_n_mm=3.0)] * 2
                + [row(stiffness_k_n_mm=10.0)] * 2
                + [row(stiffness_k_n_mm=30.0)] * 2
                + [row(stiffness_k_n_mm=70.0, outcome="IS8-17")] * 2)
        out = feasibility(rows, NOMINAL)
        assert out["required_band_n_mm"] == (3.0, 30.0)
        cls = next(c for c in out["classes"]
                   if c["mu_trac"] == 0.2 and c["m_rv_kg"] == 300.0)
        lo, hi = cls["intersection_n_mm"]
        assert lo == 3.0 and hi == pytest.approx(16.82, abs=0.02)


class TestPoolingGuard:
    def _write(self, path, curve_set, code_git_sha="s"):
        sp = scenarios.build_sweep_point(**{**NOMINAL,
                                            "curve_set": curve_set})
        header = {"v": 1, "type": "trial_header", "trial_id": "x",
                  "seed": 1, "code_git_sha": code_git_sha,
                  "engine": {"name": "mujoco", "version": "0"},
                  "sweep_point": sp, "params_ref": "p"}
        result = {"v": 1, "type": "trial_result", "outcome": "success",
                  "first_attempt_success": True, "attempts_used": 1,
                  "t_total": 1.0, "handoff_reached": True}
        path.write_text(json.dumps(header) + "\n" + json.dumps(result)
                        + "\n", encoding="utf-8")

    def test_mixed_curve_sets_refused(self, tmp_path):
        self._write(tmp_path / "a.ndjson", "prior_v1")
        self._write(tmp_path / "b.ndjson", "mr_v1")
        with pytest.raises(MixedCurveSetsError):
            load_dataset(tmp_path)

    def test_single_curve_set_loads(self, tmp_path):
        self._write(tmp_path / "a.ndjson", "prior_v1")
        rows = load_dataset(tmp_path, expect_curve_set="prior_v1")
        assert len(rows) == 1 and rows[0].curve_set == "prior_v1"

    def test_mixed_code_shas_refused(self, tmp_path):
        # R01 S-05: same curve set, different code freezes — pre- and
        # post-fix prior_v1 records must never pool silently.
        self._write(tmp_path / "a.ndjson", "prior_v1", code_git_sha="aaa")
        self._write(tmp_path / "b.ndjson", "prior_v1", code_git_sha="bbb")
        with pytest.raises(MixedCurveSetsError):
            load_dataset(tmp_path)


class TestCharts:
    def test_render_all_writes_figures_and_index(self, tmp_path):
        from wyzantium_sim.analysis.charts import render_all
        rows = ([row()] * 3 + [row(outcome="IS8-1")]
                + [row(outer_occlusion=0.3)] * 2
                + [row(outcome="IS8-1", outer_occlusion=0.3)] * 2
                + [row(conf_min_attempt=0.5)]
                + [row(outcome="IS8-16", conf_min_attempt=0.5)])
        index = render_all(rows, NOMINAL, tmp_path)
        assert (tmp_path / "index.json").is_file()
        assert (tmp_path / "d017_tradeoff.png").is_file()
        assert (tmp_path / "failure_distribution.png").is_file()
        assert any(name.startswith("d014_outer_occlusion")
                   for name in index["figures"])
        for name in index["figures"].values():
            assert (tmp_path / name).stat().st_size > 0
