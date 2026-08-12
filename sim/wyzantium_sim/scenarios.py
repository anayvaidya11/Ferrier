"""Scenario loading and sweep_point construction.

trial_header.sweep_point must carry every settable INTERFACE_SPEC §9
degradation axis and every §9.1 swept system parameter (WIRE_FORMAT). View
angle and range are trajectory-induced per §9's own coverage rows — they
emerge from the approach and are recorded in sim_truth, not set here.

The D-029 kill-gate cell is read from sim/scenarios/gate_moderate.json and
only from there; no module hardcodes the band.
"""
import json
from pathlib import Path

SCENARIO_DIR = Path(__file__).resolve().parent.parent / "scenarios"

SWEEP_AXES = (
    # IS §9 degradation axes (settable)
    "outer_occlusion", "inner_occlusion", "illuminance_lux", "rain",
    "dropout_p", "lens_contamination", "host_pitch_deg", "host_roll_deg",
    "tag_knockout_mask",
    # IS §9.1 swept system parameters
    "attempts_per_encounter", "speed_outer_ms", "speed_inner_ms",
    "speed_insertion_ms", "mu_contact", "restitution_e",
    "perception_rate_hz", "perception_latency_ms", "chassis_error_scale",
    "conf_min_attempt", "time_budget_min", "mud_f_c", "flip_kappa",
    "sigma_px",   # #40 committed sweep, realized by D-046(a) (R01 F-009)
    "stiffness_k_n_mm", "head_mass_kg",
    # Curve-swap seam: which perception curve set generated this trial
    "curve_set",
)


class SweepPointError(ValueError):
    pass


def build_sweep_point(**axes):
    """Build a complete sweep_point dict. Every axis exactly once."""
    missing = [a for a in SWEEP_AXES if a not in axes]
    if missing:
        raise SweepPointError(f"missing axes: {', '.join(missing)}")
    unknown = [a for a in axes if a not in SWEEP_AXES]
    if unknown:
        raise SweepPointError(f"unknown axes: {', '.join(unknown)}")
    return {a: axes[a] for a in SWEEP_AXES}


def load_scenario(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_gate_moderate():
    return load_scenario(SCENARIO_DIR / "gate_moderate.json")
