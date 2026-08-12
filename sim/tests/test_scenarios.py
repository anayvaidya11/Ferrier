"""Scenario loading, sweep_point axis coverage, and the D-029 gate cell.

WIRE_FORMAT requires trial_header.sweep_point to carry every degradation axis
(INTERFACE_SPEC §9) and every swept system parameter (§9.1) for the trial.
View angle and range are excluded by the spec's own words: their §9 rows read
"trajectory-induced" — they emerge from the approach, they are not set points;
they appear in sim_truth, not sweep_point.

The kill-gate cell (D-029) lives in sim/scenarios/gate_moderate.json and only
there — code never hardcodes the band.
"""
import json
from pathlib import Path

import pytest

from wyzantium_sim import scenarios

SCENARIO_DIR = Path(__file__).resolve().parent.parent / "scenarios"

# Literal, independently-transcribed axis list (double-entry with
# scenarios.SWEEP_AXES). Degradation axes from IS §9; system parameters
# from IS §9.1; curve_set per PHASE1_PLAN's curve-swap seam.
AXES = (
    # IS §9 degradation axes (settable)
    "outer_occlusion", "inner_occlusion", "illuminance_lux", "rain",
    "dropout_p", "lens_contamination", "host_pitch_deg", "host_roll_deg",
    "tag_knockout_mask",
    # IS §9.1 swept system parameters
    "attempts_per_encounter", "speed_outer_ms", "speed_inner_ms",
    "speed_insertion_ms", "mu_contact", "restitution_e",
    "perception_rate_hz", "perception_latency_ms", "chassis_error_scale",
    "conf_min_attempt", "time_budget_min", "mud_f_c", "flip_kappa",
    "stiffness_k_n_mm", "head_mass_kg",
    # Curve-swap seam
    "curve_set",
)

NOMINAL = {
    "outer_occlusion": 0.0, "inner_occlusion": 0.0,
    "illuminance_lux": 41000, "rain": 0.0, "dropout_p": 0.0,
    "lens_contamination": 0.0, "host_pitch_deg": 0.0, "host_roll_deg": 0.0,
    "tag_knockout_mask": 0, "attempts_per_encounter": 3,
    "speed_outer_ms": 1.0, "speed_inner_ms": 0.2, "speed_insertion_ms": 0.05,
    "mu_contact": 0.4, "restitution_e": 0.2, "perception_rate_hz": 30,
    "perception_latency_ms": 30, "chassis_error_scale": 1.0,
    "conf_min_attempt": 0.85, "time_budget_min": 15, "mud_f_c": 0.8,
    "flip_kappa": 1.0, "stiffness_k_n_mm": 10.0, "head_mass_kg": 15.0,
    "curve_set": "prior_v1",
}


def test_axis_list_matches_literal_transcription():
    assert scenarios.SWEEP_AXES == AXES


def test_build_sweep_point_accepts_full_axis_set():
    point = scenarios.build_sweep_point(**NOMINAL)
    assert set(point.keys()) == set(AXES)


def test_build_sweep_point_rejects_missing_axis():
    partial = {k: v for k, v in NOMINAL.items() if k != "mud_f_c"}
    with pytest.raises(scenarios.SweepPointError, match="mud_f_c"):
        scenarios.build_sweep_point(**partial)


def test_build_sweep_point_rejects_unknown_axis():
    with pytest.raises(scenarios.SweepPointError, match="fog"):
        scenarios.build_sweep_point(**NOMINAL, fog=0.5)


def test_load_scenario_reads_json(tmp_path):
    path = tmp_path / "case.json"
    path.write_text(json.dumps({"name": "smoke", "sweep_point": NOMINAL}))
    assert scenarios.load_scenario(path)["name"] == "smoke"


# --- The D-029 gate cell ---

def test_gate_moderate_file_exists_in_scenarios_dir():
    assert (SCENARIO_DIR / "gate_moderate.json").is_file()


def test_gate_moderate_matches_d029_committed_band():
    gate = scenarios.load_gate_moderate()
    band = gate["band"]
    # Independently transcribed from DECISIONS.md D-029.
    assert band["outer_occlusion"] == {"cells": [0.3, 0.4]}
    assert band["inner_occlusion"] == {"cells": [0.3, 0.4, 0.5]}
    assert band["illuminance_lux"] == {"cells": [50, 100]}
    assert band["rain"] == {"lo": 0.10, "hi": 0.20}
    assert band["dropout_p"] == {"value": 0.05, "bursts": True}
    assert band["lens_contamination"] == {"lo": 0.10, "hi": 0.25}
    assert band["tag_knockout_mask"] == {"value": 0}
    assert gate["source"] == "DECISIONS.md D-029"
    # Encounter geometry marginalizes; system parameters at labeled defaults.
    assert "marginalize" in gate["encounter_geometry"]
    assert "defaults" in gate["system_parameters"]


def test_gate_band_is_not_hardcoded_anywhere_in_wyzantium_sim():
    # D-029: code reads the band from the JSON only. The distinctive band
    # values must not appear as literals in any wyzantium_sim module.
    package_dir = Path(scenarios.__file__).parent
    # R01 F-019: rglob, not glob — doe/tiers.py (the sole band consumer)
    # and every other subpackage must be scanned too. The sanctioned path
    # is scenarios.load_gate_moderate(); the guarded string is the QUOTED
    # filename (an actual path resolution) — loader calls and docstring
    # prose mentioning the file are fine.
    for py in package_dir.rglob("*.py"):
        text = py.read_text()
        if py.name != "scenarios.py":
            for quoted in ('"gate_moderate.json"', "'gate_moderate.json'"):
                assert quoted not in text, (
                    f"{py.name} resolves the gate JSON directly — the "
                    "loader in scenarios.py is the only sanctioned path")
        for marker in ("0.3, 0.4", "[50, 100]"):
            assert marker not in text, f"{py.name} hardcodes the gate band"
