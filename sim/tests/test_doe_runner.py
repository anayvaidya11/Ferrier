"""T10 — resumable sweep runner + spend meter (D-032 (c)/(d)).

Gate (PHASE1_PLAN §4 row T10): spend meter trips on synthetic overrun;
resume machinery (the kill/resume half of the gate lives in
test_doe_kill_resume.py — this file covers the per-trial oracle and the
in-process resume path).

Double-entry transcription:
  D-032 (c): ceiling read from spend_p02.json only; cumulative spend
      persists in a ledger; two trips, both hard stops — projected
      (plan × rate + spent crosses the ceiling → refuse to start) and
      imminent (the next trial would cross → stop before dispatching).
  D-032 (d): resume is per-trial; the completeness oracle is
      validate_trial_file == [], never bare existence; valid records are
      skipped, anything else re-runs and is overwritten.
"""
import json

import pytest

from wyzantium_sim.doe import runner as doe_runner
from wyzantium_sim.doe.tiers import PlannedTrial, derive_seed

# A cheap sweep point: the committed nominal with a tiny time budget —
# trials end as clean_miss mid-approach in well under a second. Values are
# overrides on the committed nominal, which the runner takes as given
# (plans commit values; the runner does not judge them).
CHEAP = {
    "outer_occlusion": 0.0, "inner_occlusion": 0.0,
    "illuminance_lux": 41000, "rain": 0.0, "dropout_p": 0.0,
    "lens_contamination": 0.0, "host_pitch_deg": 0.0, "host_roll_deg": 0.0,
    "tag_knockout_mask": 0, "attempts_per_encounter": 3,
    "speed_outer_ms": 1.0, "speed_inner_ms": 0.2, "speed_insertion_ms": 0.05,
    "mu_contact": 0.4, "restitution_e": 0.2, "perception_rate_hz": 30,
    "perception_latency_ms": 30, "chassis_error_scale": 1.0,
    "conf_min_attempt": 0.85, "time_budget_min": 0.05, "mud_f_c": 0.8,
    "flip_kappa": 1.0, "stiffness_k_n_mm": 10.0, "head_mass_kg": 15.0,
    "curve_set": "prior_v1",
}


def cheap_plan(n, root=20260808):
    return tuple(
        PlannedTrial(f"test:{i:03d}", derive_seed(root, f"test:{i:03d}"),
                     dict(CHEAP))
        for i in range(n))


def meter(tmp_path, *, ceiling=100.0, rate=0.0, name="ledger.json"):
    return doe_runner.SpendMeter(tmp_path / name, ceiling_usd=ceiling,
                                 usd_per_trial=rate)


class TestSpendMeter:
    def test_projected_overrun_trips_before_anything_runs(self, tmp_path):
        m = meter(tmp_path, rate=30.0)
        with pytest.raises(doe_runner.SpendCeilingError):
            m.check_projected(4)          # 4 × $30 = $120 > $100
        m.check_projected(3)              # $90 fits

    def test_imminent_overrun_trips_before_the_crossing_trial(self,
                                                              tmp_path):
        m = meter(tmp_path, rate=30.0)
        for _ in range(3):
            m.charge_before()
            m.record("t")
        assert m.spent_usd == pytest.approx(90.0)
        with pytest.raises(doe_runner.SpendCeilingError):
            m.charge_before()             # $90 + $30 crosses $100

    def test_ledger_persists_across_instances(self, tmp_path):
        m = meter(tmp_path, rate=25.0)
        m.charge_before()
        m.record("t0")
        again = meter(tmp_path, rate=25.0)
        assert again.spent_usd == pytest.approx(25.0)
        assert again.trials_recorded == 1

    def test_zero_rate_local_runs_never_trip(self, tmp_path):
        m = meter(tmp_path, rate=0.0)
        m.check_projected(10 ** 6)
        m.charge_before()
        m.record("t")
        assert m.spent_usd == 0.0

    def test_default_ceiling_comes_from_the_committed_file(self, tmp_path):
        m = doe_runner.SpendMeter(tmp_path / "ledger.json",
                                  usd_per_trial=60.0)
        m.charge_before()
        m.record("t")
        with pytest.raises(doe_runner.SpendCeilingError):
            m.charge_before()             # $60 + $60 crosses the P-02 $100


class TestRecordComplete:
    def test_missing_file_is_incomplete(self, tmp_path):
        assert not doe_runner.record_complete(tmp_path / "absent.ndjson")

    def test_valid_record_is_complete(self, tmp_path):
        result = doe_runner.run_sweep(cheap_plan(1), tmp_path)
        assert doe_runner.record_complete(result.paths[0])

    def test_truncated_record_is_incomplete(self, tmp_path):
        result = doe_runner.run_sweep(cheap_plan(1), tmp_path)
        path = result.paths[0]
        lines = path.read_bytes().splitlines(keepends=True)
        path.write_bytes(b"".join(lines[:-1]))   # drop trial_result
        assert not doe_runner.record_complete(path)


class TestRunSweepResume:
    def test_fresh_sweep_runs_everything_and_validates(self, tmp_path):
        result = doe_runner.run_sweep(cheap_plan(3), tmp_path)
        assert result.ran == 3 and result.skipped == 0
        assert len(result.paths) == 3
        for p in result.paths:
            assert doe_runner.record_complete(p)

    def test_second_pass_skips_everything(self, tmp_path):
        doe_runner.run_sweep(cheap_plan(3), tmp_path)
        result = doe_runner.run_sweep(cheap_plan(3), tmp_path)
        assert result.ran == 0 and result.skipped == 3

    def test_damaged_record_is_rerun_byte_identically(self, tmp_path):
        first = doe_runner.run_sweep(cheap_plan(3), tmp_path)
        target = first.paths[1]
        control = target.read_bytes()
        target.write_bytes(control[: len(control) // 2])
        result = doe_runner.run_sweep(cheap_plan(3), tmp_path)
        assert result.ran == 1 and result.skipped == 2
        assert target.read_bytes() == control

    def test_distinct_replicate_seeds_mean_distinct_files(self, tmp_path):
        # the D-032 seed rule: same sweep point, different tags → different
        # seeds → different trial_ids; nothing overwrites anything
        result = doe_runner.run_sweep(cheap_plan(3), tmp_path)
        assert len({p.name for p in result.paths}) == 3

    def test_projected_overrun_refuses_the_whole_sweep(self, tmp_path):
        m = meter(tmp_path, rate=60.0)
        with pytest.raises(doe_runner.SpendCeilingError):
            doe_runner.run_sweep(cheap_plan(3), tmp_path, spend=m)
        assert not list(tmp_path.glob("*.ndjson"))

    # NOTE: with a constant rate and an exclusive ledger, a passing
    # projected check implies every imminent check passes — the imminent
    # trip (TestSpendMeter) is defense-in-depth for a ledger that grows
    # concurrently (another process on the same ledger).

    def test_spend_is_recorded_per_completed_trial(self, tmp_path):
        m = meter(tmp_path, rate=10.0)
        doe_runner.run_sweep(cheap_plan(2), tmp_path, spend=m)
        assert m.spent_usd == pytest.approx(20.0)
        assert m.trials_recorded == 2
        ledger = json.loads((tmp_path / "ledger.json").read_text())
        assert ledger["spent_usd"] == pytest.approx(20.0)

    def test_skipped_trials_cost_nothing(self, tmp_path):
        doe_runner.run_sweep(cheap_plan(2), tmp_path)
        m = meter(tmp_path, rate=10.0)
        result = doe_runner.run_sweep(cheap_plan(2), tmp_path, spend=m)
        assert result.skipped == 2
        assert m.spent_usd == 0.0


class TestWorkers:
    def test_two_workers_produce_the_same_bytes_as_one(self, tmp_path):
        a = doe_runner.run_sweep(cheap_plan(4), tmp_path / "serial")
        b = doe_runner.run_sweep(cheap_plan(4), tmp_path / "pool",
                                 workers=2)
        assert sorted(p.name for p in a.paths) \
            == sorted(p.name for p in b.paths)
        for pa in a.paths:
            pb = (tmp_path / "pool") / pa.name
            assert pa.read_bytes() == pb.read_bytes()
