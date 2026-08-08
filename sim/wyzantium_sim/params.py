"""PHASE1_PARAMETERS.md as a typed registry — all 65 entries, transcribed.

The committed document is the source of truth; tests/test_params.py carries an
independent transcription (double-entry) and the two must agree. Encoding:
discrete sweeps are tuples, continuous ranges are {"lo": x, "hi": y},
structured values are dicts, recorded procedures are strings (recorded, not
executed here). `default` is set only where the document names one.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Param:
    num: int
    name: str
    value: object
    default: object = None
    unit: str = ""
    source: str = ""
    label: str = ""


_ENTRIES = [
    # Geometry (all from D-016 / INTERFACE_SPEC)
    Param(1, "stud_neck_diameter", 25.0, None, "mm", "D-016", "ASSUMED"),
    Param(2, "stud_head_diameter", 40.0, None, "mm", "D-016", "ASSUMED"),
    Param(3, "stud_exposed_length", 90.0, None, "mm", "D-016", "ASSUMED"),
    Param(4, "funnel_mouth_diameter", 220.0, None, "mm", "IS §6", "derived"),
    Param(5, "funnel_throat_diameter", 42.0, None, "mm", "D-016", "ASSUMED"),
    Param(6, "funnel_depth", 180.0, None, "mm", "D-016", "ASSUMED"),
    Param(7, "funnel_wall_half_angle", 26.0, None, "deg", "IS §6", "derived"),
    Param(8, "plate_envelope", (200.0, 200.0), None, "mm", "D-016", "ASSUMED"),
    Param(9, "outer_tag",
          {"size_mm": 150.0, "center_stud_mm": (0.0, 0.0, 185.0)},
          None, "mm", "IS §3.2, §3.5", "ASSUMED"),
    Param(10, "inner_ring",
          {"count": 8, "tag_size_mm": 10.0, "radius_mm": 55.0,
           "pitch_deg": 45.0},
          None, "", "IS §3.3, §3.5", "ASSUMED"),
    Param(11, "collar_standoff_h_c", {"lo": 10.0, "hi": 40.0},
          None, "mm", "D-016; studies/H08 §3 (observability floor ~8 mm)",
          "swept"),
    Param(12, "funnel_lip_band", {"lo": 110.0, "hi": 125.0},
          None, "mm", "IS §6", "derived"),
    Param(13, "contact_annulus_radius", 160.0, None, "mm", "IS §6", "derived"),
    Param(14, "capture_plane", "head_frame YZ plane at x = 0",
          None, "", "IS §6", "decided"),
    Param(15, "handoff_trigger_x", 50.0, None, "mm", "IS §6, D-006",
          "decided"),
    # Frames and cameras
    Param(16, "T_stud_plate",
          {"t_mm": (0.0, 0.0, 185.0), "rotation": "identity"},
          None, "", "IS §4", "ASSUMED"),
    Param(17, "cam_a_extrinsic",
          {"t_mm": (-50.0, 0.0, 140.0), "boresight": "+X"},
          None, "", "IS §4, D-012", "ASSUMED"),
    Param(18, "cam_b_extrinsic",
          {"t_mm": (100.0, -250.0, 0.0), "yaw_deg": 30.0,
           "band_deg": (15.0, 45.0)},
          None, "", "IS §4, D-025", "ASSUMED (angle decided, D-025)"),
    Param(19, "focal_a_px", 1371.0, None, "px", "D-012",
          "derived: 1920/(2*tan 35°)"),
    Param(20, "focal_b_px", 880.0, None, "px", "D-012",
          "derived: 1920/(2*tan 47.5°)"),
    # Envelope and error budget
    Param(21, "capture_envelope_position", 35.0, None, "mm", "D-015",
          "ASSUMED"),
    Param(22, "capture_envelope_angle", 10.0, None, "deg", "D-015",
          "ASSUMED"),
    Param(23, "budget_allocations",
          {"position_mm": (15.0, 25.0, 3.0), "angle_deg": (3.0, 6.0, 1.0),
           "scale_sweep": (0.5, 1.0, 2.0)},
          None, "", "IS §5, D-019", "declared sweep centers"),
    # Guidance
    Param(24, "approach_tow_sector", 20.0, None, "deg", "D-018", "normative"),
    Param(25, "stage_boundaries",
          {"outer_m": (3.0, 0.2), "inner_m": (0.2, 0.0)},
          None, "m", "D-004", "decided"),
    Param(26, "stage_speeds",
          {"outer": {"lo": 0.5, "hi": 2.0}, "inner": {"lo": 0.1, "hi": 0.3},
           "insertion": {"lo": 0.02, "hi": 0.15}},
          (1.0, 0.2, 0.05), "m/s", "IS §9.1", "swept; defaults arbitrary"),
    Param(27, "attempts_per_encounter", (1, 2, 3, 5), 3, "",
          "IS §9.1, D-005", "swept; default arbitrary"),
    Param(28, "retry_backout_distance", 300.0, None, "mm", "D-005",
          "decided"),
    Param(29, "conf_min_attempt",
          (0.50, 0.60, 0.70, 0.80, 0.85, 0.90, 0.95), 0.85, "", "D-017",
          "swept; default arbitrary; tradeoff curve is a deliverable"),
    Param(30, "insertion_commit_rule",
          "pose_source = multi_tag_fused (>=2 tags) AND stage = inner_servo "
          "AND conf >= threshold",
          None, "", "WIRE_FORMAT; studies/H08", "decided"),
    # Contact
    Param(31, "mu_contact", {"lo": 0.1, "hi": 0.8}, 0.4, "", "IS §9.1",
          "swept; default arbitrary; distinct from #64 mu_trac (D-028)"),
    Param(32, "restitution_e", {"lo": 0.1, "hi": 0.4}, 0.2, "", "IS §9.1",
          "swept; default arbitrary"),
    Param(33, "solver_convergence_procedure",
          "halve timestep until success-rate delta < 1% over a 500-trial "
          "probe; values logged per run in trial_header",
          None, "", "HOLES H-03", "decided procedure"),
    Param(34, "compliance_topology",
          "T1: rigid steel funnel on compliant instrumented base; rigid "
          "bodies + one 6-DOF spring-damper + hard stops (RATIFIED "
          "2026-08-02)",
          None, "", "D-027", "RATIFIED"),
    Param(35, "compliance_stiffness_k", (1.0, 3.0, 10.0, 30.0, 70.0),
          None, "N/mm", "D-026; studies/H04 §4",
          "swept log grid; Phase 1 outputs the required-stiffness band"),
    Param(36, "head_effective_mass", (8.0, 15.0, 30.0), 15.0, "kg",
          "D-026; IS §9.1", "swept class range"),
    # Perception injection (D-007, D-008-R)
    Param(37, "perception_rate", (10, 30, 60), 30, "Hz", "IS §9.1",
          "swept; class-value default"),
    Param(38, "perception_latency", (10, 30, 100), 30, "ms", "IS §9.1",
          "swept; class-value default"),
    Param(39, "detection_probability_model",
          "literature anchors per research/data/perception_prior.md "
          "(near-field plateau, onset-of-failure falloff); view-angle "
          "falloff shape is a swept parameter until MR data lands",
          None, "", "research/data/perception_prior.md; D-008-R",
          "sourced anchors + declared sweep"),
    Param(40, "pose_cov_sigma_px", (0.3, 0.5, 1.0), 0.5, "px",
          "research/data/perception_prior.md; MEASUREMENT_REQUESTS",
          "swept class value; replaced by measured reproj_rms_px"),
    Param(41, "mud_model",
          {"form": "P_mask(f) * max(0, 1 - f/f_c)",
           "f_c": (0.6, 0.8, 1.0)},
          0.8, "", "D-023; IS §9.1", "decided form; f_c swept"),
    Param(42, "flip_model_kappa", (0.5, 1.0, 2.0), 1.0, "",
          "studies/H08 §4; IS §9.1", "shape assumption pending MR-003"),
    Param(43, "sensor_dropout",
          {"bernoulli_p": (0.0, 0.05, 0.1, 0.2, 0.3),
           "burst": "geometric, mean 5"},
          None, "", "IS §9", "ASSUMED model"),
    Param(44, "lens_contamination", {"lo": 0.0, "hi": 0.5}, None, "",
          "IS §9", "EXT"),
    Param(45, "rain_proxy", {"lo": 0.0, "hi": 0.3}, None, "", "IS §9",
          "EXT — no literature found"),
    Param(46, "partial_destruction",
          "per-tag knockout over sampled 2^9 combinations", None, "",
          "IS §9", "ASSUMED model"),
    Param(47, "illuminance_grid", (1, 2, 5, 10, 50, 100, 1000, 10000),
          None, "lux", "IS §9", "log grid; sub-10 lux MR-002 else EXT"),
    Param(48, "occlusion_grids",
          {"outer": {"lo": 0.0, "hi": 0.7}, "inner": {"lo": 0.0, "hi": 0.9},
           "step": 0.1, "independent": True},
          None, "", "IS §9", "MR-001 else EXT"),
    # Environment, DOE, outcomes, logging, compute
    Param(49, "host_pitch_roll", 20.0, None, "deg", "IS §9, D-024",
          "uniform ±20°, terrain input"),
    Param(50, "doe_tier1", "one-factor marginal grids at nominal elsewhere",
          None, "", "D-021", "decided"),
    Param(51, "doe_tier2_min_n", 4000, None, "trials", "D-021",
          "decided (LHS joint)"),
    Param(52, "doe_tier3", "failure-replay set (A-007 artifacts)",
          None, "", "D-021", "decided"),
    Param(53, "total_trials_min", 10000, None, "trials",
          "MASTER_CONTEXT Phase 1, D-021", "decided"),
    Param(54, "latch_predicate",
          {"radial_mm": 3.0, "speed_max_ms": 0.1, "hold_ms": 100.0},
          None, "", "D-020", "decided"),
    Param(55, "encounter_time_budget", (5, 15, 30), 15, "min", "D-022",
          "swept; default arbitrary"),
    Param(56, "success_definition",
          "D-020 latch within attempt budget AND t <= T; first/multi-attempt "
          "reported separately",
          None, "", "D-022, D-005", "decided"),
    Param(57, "outcome_classes",
          ("success",) + tuple(f"IS8-{r}" for r in range(1, 19))
          + ("clean_miss",),
          None, "", "IS §8 (18 rows); FAILURE_TAXONOMY.md; D-030; D-033",
          "decided (revised 2026-08-02 H-15; 2026-08-08 D-033)"),
    Param(58, "trial_record_schema", "header/state/result per WIRE_FORMAT",
          None, "", "WIRE_FORMAT", "decided"),
    Param(59, "sim_truth_logging_rate",
          "every physics step post-handoff; every kinematic step pre-handoff",
          None, "", "WIRE_FORMAT", "decided"),
    Param(60, "seed_policy",
          "single RNG root per trial in trial_header; all streams derive",
          None, "", "WIRE_FORMAT", "decided"),
    Param(61, "compute_decision_test",
          "1,000-trial representative workload, cloud CPU vs GPU spot, "
          "$/1k trials, winner provisioned, both measurements committed",
          None, "", "ARCHITECTURE §5, A-004", "decided procedure"),
    Param(62, "jam_detection_thresholds",
          {"F_ax_N": (50.0, 100.0, 200.0), "F_lat_N": (10.0, 25.0),
           "t_s": (0.5, 1.0, 2.0)},
          None, "", "IS §8 row 17, D-027",
          "swept, defaults arbitrary; recalibrated in Phase 1 week one as a "
          "recorded revision"),
    Param(63, "k_feasibility_window",
          {"k_max": "mu_trac * m_rv * g / 35 mm over #64 x #65",
           "k_min": "n_F / delta_work (n_F named Phase 2 unknown; class "
                    "placeholder ~1 N/mm)",
           "emits": "window, required band, intersection, mask — data, "
                    "not verdicts; interpretation in ARCHITECTURE §6.7 only",
           "pinned_check": {"mu_trac": 0.2, "m_rv_kg": 300.0,
                            "k_max_n_mm": 17.0}},
          None, "", "D-028; studies/H04 Addendum A1", "derived semantics"),
    Param(64, "mu_trac", (0.2, 0.35, 0.5), None, "",
          "studies/H04 Addendum A1; D-028",
          "swept; distinct from #31 mu_contact"),
    Param(65, "m_rv", (300.0, 500.0, 800.0), None, "kg",
          "studies/H04 Addendum A1; D-028",
          "swept class range; independent of the target's 500 kg"),
]

PARAMS = {p.num: p for p in _ENTRIES}
