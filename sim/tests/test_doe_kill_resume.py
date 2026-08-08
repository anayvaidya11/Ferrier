"""T10 — the kill/resume half of the gate: a 50-trial mini-sweep survives
SIGKILL and resumes to a dataset byte-identical to an uninterrupted run.

The machinery under test is the whole chain: CLI entry (subprocess),
process-pool workers, the atomic record writer (a killed writer leaves
either nothing or a complete file — never a truncated one), and the D-032
resume oracle. The sweep point is the committed nominal with a small time
budget so the 50 trials stay cheap — the cell choice is irrelevant to the
machinery (the committed mini/smoke sweeps run in ops with real cells).
"""
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

from wyzantium_sim.doe import __main__ as doe_cli
from wyzantium_sim.doe import runner as doe_runner
from wyzantium_sim.doe.tiers import derive_seed

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
# NOTE on the budget values: 0.05 min ends as a fast clean_miss before
# handoff; 0.2 min latches; in between (≈0.1) the budget truncates the
# insertion itself — originally an UnclassifiedFailure, now IS8-18 per
# D-033 (the recorded amendment this exact shape forced).

N = 50


def write_plan_file(path: Path, n=N):
    # every 5th trial is a slower latching cell: keeps the kill window
    # wide and exercises heterogeneous outcomes through the runner
    trials = []
    for i in range(n):
        point = dict(CHEAP)
        if i % 5 == 0:
            point["time_budget_min"] = 0.2
        trials.append({"tag": f"mini:{i:03d}",
                       "seed": derive_seed(20260808, f"mini:{i:03d}"),
                       "sweep_point": point})
    path.write_text(json.dumps({"trials": trials}))
    return path


def test_mini_sweep_survives_kill_and_resumes_byte_identically(tmp_path):
    plan_file = write_plan_file(tmp_path / "plan.json")
    plan = doe_cli.load_plan_file(plan_file)
    assert len(plan) == N

    # the uninterrupted control
    control_dir = tmp_path / "control"
    control = doe_runner.run_sweep(plan, control_dir)
    assert control.ran == N

    # the killed run: CLI subprocess, its own session so SIGKILL takes the
    # pool workers down with it
    kill_dir = tmp_path / "killed"
    stderr_log = (tmp_path / "stderr.log").open("wb")
    proc = subprocess.Popen(
        [sys.executable, "-m", "wyzantium_sim.doe",
         "--plan-file", str(plan_file), "--out", str(kill_dir),
         "--workers", "2"],
        stdout=subprocess.DEVNULL, stderr=stderr_log,
        start_new_session=True)
    try:
        deadline = time.monotonic() + 120.0
        while time.monotonic() < deadline:
            if len(list(kill_dir.glob("*.ndjson"))) >= 3:
                break
            if proc.poll() is not None:
                raise AssertionError(
                    "CLI exited before the kill window: "
                    + (tmp_path / "stderr.log").read_text())
            time.sleep(0.01)
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        proc.wait(timeout=30)
    finally:
        stderr_log.close()
        if proc.poll() is None:
            os.killpg(os.getpgid(proc.pid), signal.SIGKILL)

    survivors = sorted(kill_dir.glob("*.ndjson"))
    assert survivors, "kill landed before any record was written"
    assert len(survivors) < N, \
        "kill landed after completion — widen the kill window"
    # the atomic-writer guarantee: every surviving file is complete
    for f in survivors:
        assert doe_runner.record_complete(f), f.name

    # resume in-process; only the missing trials run
    resumed = doe_runner.run_sweep(plan, kill_dir)
    assert resumed.skipped == len(survivors)
    assert resumed.ran == N - len(survivors)

    # the resumed dataset is byte-identical to the uninterrupted control
    control_files = {p.name: p for p in control_dir.glob("*.ndjson")}
    resumed_files = {p.name: p for p in kill_dir.glob("*.ndjson")}
    assert control_files.keys() == resumed_files.keys()
    for name, cp in control_files.items():
        assert cp.read_bytes() == resumed_files[name].read_bytes(), name


def test_cli_reports_and_second_run_skips(tmp_path):
    plan_file = write_plan_file(tmp_path / "plan.json", n=4)
    out_dir = tmp_path / "out"
    cmd = [sys.executable, "-m", "wyzantium_sim.doe",
           "--plan-file", str(plan_file), "--out", str(out_dir)]
    first = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "ran=4 skipped=0" in first.stdout
    second = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "ran=0 skipped=4" in second.stdout
