"""Double-entry transcription test for PHASE1_PARAMETERS.md.

EXPECTED below is transcribed directly from the committed document,
independently of wyzantium_sim/params.py — the two transcriptions must agree on
every load-bearing value. Encoding conventions (shared with params.py):
discrete sweeps are tuples, continuous ranges are {"lo": x, "hi": y},
structured values are dicts, recorded procedures are strings.
"""
import pytest

from wyzantium_sim import params

# {num: (value, default, unit, citation-substring-of-source)}
EXPECTED = {
    # Geometry (D-016 / INTERFACE_SPEC)
    1: (25.0, None, "mm", "D-016"),
    2: (40.0, None, "mm", "D-016"),
    3: (90.0, None, "mm", "D-016"),
    4: (220.0, None, "mm", "IS §6"),
    5: (42.0, None, "mm", "D-016"),
    6: (180.0, None, "mm", "D-016"),
    7: (26.0, None, "deg", "IS §6"),
    8: ((200.0, 200.0), None, "mm", "D-016"),
    9: ({"size_mm": 150.0, "center_stud_mm": (0.0, 0.0, 185.0)},
        None, "mm", "IS §3.2"),
    10: ({"count": 8, "tag_size_mm": 10.0, "radius_mm": 55.0,
          "pitch_deg": 45.0}, None, "", "IS §3.3"),
    11: ({"lo": 10.0, "hi": 40.0}, None, "mm", "D-016"),
    12: ({"lo": 110.0, "hi": 125.0}, None, "mm", "IS §6"),
    13: (160.0, None, "mm", "IS §6"),
    14: ("head_frame YZ plane at x = 0", None, "", "IS §6"),
    15: (50.0, None, "mm", "IS §6"),
    # Frames and cameras
    16: ({"t_mm": (0.0, 0.0, 185.0), "rotation": "identity"},
         None, "", "IS §4"),
    17: ({"t_mm": (-50.0, 0.0, 140.0), "boresight": "+X"},
         None, "", "D-012"),
    18: ({"t_mm": (100.0, -250.0, 0.0), "yaw_deg": 30.0,
          "band_deg": (15.0, 45.0)}, None, "", "D-025"),
    19: (1371.0, None, "px", "D-012"),
    20: (880.0, None, "px", "D-012"),
    # Envelope and error budget
    21: (35.0, None, "mm", "D-015"),
    22: (10.0, None, "deg", "D-015"),
    23: ({"position_mm": (15.0, 25.0, 3.0), "angle_deg": (3.0, 6.0, 1.0),
          "scale_sweep": (0.5, 1.0, 2.0)}, None, "", "D-019"),
    # Guidance
    24: (20.0, None, "deg", "D-018"),
    25: ({"outer_m": (3.0, 0.2), "inner_m": (0.2, 0.0)}, None, "m", "D-004"),
    26: ({"outer": {"lo": 0.5, "hi": 2.0}, "inner": {"lo": 0.1, "hi": 0.3},
          "insertion": {"lo": 0.02, "hi": 0.15}},
         (1.0, 0.2, 0.05), "m/s", "IS §9.1"),
    27: ((1, 2, 3, 5), 3, "", "D-005"),
    28: (300.0, None, "mm", "D-005"),
    29: ((0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95), 0.85, "", "D-017"),
    30: ("pose_source = multi_tag_fused (>=2 tags) AND stage = inner_servo "
         "AND conf >= threshold", None, "", "WIRE_FORMAT"),
    # Contact
    31: ({"lo": 0.1, "hi": 0.8}, 0.4, "", "IS §9.1"),
    32: ({"lo": 0.1, "hi": 0.4}, 0.2, "", "IS §9.1"),
    33: ("halve timestep until success-rate delta < 1% over a 500-trial "
         "probe; values logged per run in trial_header", None, "", "H-03"),
    34: ("T1: rigid steel funnel on compliant instrumented base; rigid "
         "bodies + one 6-DOF spring-damper + hard stops (RATIFIED "
         "2026-08-02)", None, "", "D-027"),
    35: ((1.0, 3.0, 10.0, 30.0, 70.0), None, "N/mm", "D-026"),
    36: ((8.0, 15.0, 30.0), 15.0, "kg", "D-026"),
    # Perception injection
    37: ((10, 30, 60), 30, "Hz", "IS §9.1"),
    38: ((10, 30, 100), 30, "ms", "IS §9.1"),
    39: ("literature anchors per research/data/perception_prior.md "
         "(near-field plateau, onset-of-failure falloff); view-angle "
         "falloff shape is a swept parameter until MR data lands",
         None, "", "perception_prior"),
    40: ((0.3, 0.5, 1.0), 0.5, "px", "perception_prior"),
    41: ({"form": "P_mask(f) * max(0, 1 - f/f_c)",
          "f_c": (0.6, 0.8, 1.0)}, 0.8, "", "D-023"),
    42: ((0.5, 1.0, 2.0), 1.0, "", "H08"),
    43: ({"bernoulli_p": (0.0, 0.05, 0.1, 0.2, 0.3),
          "burst": "geometric, mean 5"}, None, "", "IS §9"),
    44: ({"lo": 0.0, "hi": 0.5}, None, "", "IS §9"),
    45: ({"lo": 0.0, "hi": 0.3}, None, "", "IS §9"),
    46: ("per-tag knockout over sampled 2^9 combinations", None, "", "IS §9"),
    47: ((1, 2, 5, 10, 50, 100, 1000, 10000), None, "lux", "IS §9"),
    48: ({"outer": {"lo": 0.0, "hi": 0.7}, "inner": {"lo": 0.0, "hi": 0.9},
          "step": 0.1, "independent": True}, None, "", "IS §9"),
    # Environment, DOE, outcomes, logging, compute
    49: (20.0, None, "deg", "IS §9"),
    50: ("one-factor marginal grids at nominal elsewhere", None, "", "D-021"),
    51: (4000, None, "trials", "D-021"),
    52: ("failure-replay set (A-007 artifacts)", None, "", "D-021"),
    53: (10000, None, "trials", "D-021"),
    54: ({"radial_mm": 3.0, "speed_max_ms": 0.1, "hold_ms": 100.0},
         None, "", "D-020"),
    55: ((5, 15, 30), 15, "min", "D-022"),
    56: ("D-020 latch within attempt budget AND t <= T; first/multi-attempt "
         "reported separately", None, "", "D-022"),
    57: (("success",) + tuple(f"IS8-{r}" for r in range(1, 18))
         + ("clean_miss",), None, "", "D-030"),
    58: ("header/state/result per WIRE_FORMAT", None, "", "WIRE_FORMAT"),
    59: ("every physics step post-handoff; every kinematic step pre-handoff",
         None, "", "WIRE_FORMAT"),
    60: ("single RNG root per trial in trial_header; all streams derive",
         None, "", "WIRE_FORMAT"),
    61: ("1,000-trial representative workload, cloud CPU vs GPU spot, "
         "$/1k trials, winner provisioned, both measurements committed",
         None, "", "A-004"),
    62: ({"F_ax_N": (50.0, 100.0, 200.0), "F_lat_N": (10.0, 25.0),
          "t_s": (0.5, 1.0, 2.0)}, None, "", "D-027"),
    63: ({"k_max": "mu_trac * m_rv * g / 35 mm over #64 x #65",
          "k_min": "n_F / delta_work (n_F named Phase 2 unknown; class "
                   "placeholder ~1 N/mm)",
          "emits": "window, required band, intersection, mask — data, "
                   "not verdicts; interpretation in ARCHITECTURE §6.7 only",
          "pinned_check": {"mu_trac": 0.2, "m_rv_kg": 300.0,
                           "k_max_n_mm": 17.0}}, None, "", "D-028"),
    64: ((0.2, 0.35, 0.5), None, "", "D-028"),
    65: ((300.0, 500.0, 800.0), None, "kg", "D-028"),
}


def test_all_65_entries_present():
    assert sorted(params.PARAMS.keys()) == list(range(1, 66))


@pytest.mark.parametrize("num", sorted(EXPECTED), ids=lambda n: f"p{n:02d}")
def test_entry_matches_committed_doc(num):
    value, default, unit, citation = EXPECTED[num]
    entry = params.PARAMS[num]
    assert entry.value == value, f"#{num} value"
    assert entry.default == default, f"#{num} default"
    assert entry.unit == unit, f"#{num} unit"
    assert citation in entry.source, f"#{num} source must cite {citation!r}"
    assert entry.name, f"#{num} needs a name"


def test_expected_covers_all_65():
    assert sorted(EXPECTED) == list(range(1, 66))


def test_sweeps_are_immutable():
    for entry in params.PARAMS.values():
        assert not isinstance(entry.value, list), \
            f"#{entry.num}: sweeps must be tuples, not lists"
