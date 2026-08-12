"""T10 — tier generators: committed grids → deterministic trial plans.

Gate (PHASE1_PLAN §4 row T10, tier-counts clause): tier cell counts correct.
D-021 fixes the tier shapes (Tier 1 one-factor marginals at nominal
elsewhere; Tier 2 LHS N ≥ 4,000 over the joint degradation space); D-032
commits the grids as scenario data (same discipline as gate_moderate.json:
code never hardcodes them) plus the seed rule. Double-entry: this file
carries its own literal transcription of every grid and the cell
arithmetic; the package reads sim/scenarios/*.json and must agree.

Host pitch/roll are excluded from both tiers — unrealized in the harness
(H-17); a grid over a no-op axis would emit fake-flat curves.
"""
import json
from pathlib import Path

from wyzantium_sim import scenarios
from wyzantium_sim.doe import tiers

SCENARIO_DIR = Path(__file__).resolve().parent.parent / "scenarios"

# Independently transcribed nominal point (IS §9.1 defaults column + zero
# degradation; 41000 lux = undegraded daylight, deliberately off the #47
# grid; stiffness 10 N/mm = log-grid midpoint, IS §9.1 lists no default).
NOMINAL = {
    "outer_occlusion": 0.0, "inner_occlusion": 0.0,
    "illuminance_lux": 41000, "rain": 0.0, "dropout_p": 0.0,
    "lens_contamination": 0.0, "host_pitch_deg": 0.0, "host_roll_deg": 0.0,
    "tag_knockout_mask": 0, "attempts_per_encounter": 3,
    "speed_outer_ms": 1.0, "speed_inner_ms": 0.2, "speed_insertion_ms": 0.05,
    "mu_contact": 0.4, "restitution_e": 0.2, "perception_rate_hz": 30,
    "perception_latency_ms": 30, "chassis_error_scale": 1.0,
    "conf_min_attempt": 0.85, "time_budget_min": 15, "mud_f_c": 0.8,
    "flip_kappa": 1.0, "sigma_px": 0.5, "stiffness_k_n_mm": 10.0, "head_mass_kg": 15.0,
    "curve_set": "prior_v1",
}

# Independently transcribed Tier-1 grids. Sources: IS §9 committed steps
# (occlusions, illuminance, dropout), IS §9.1 committed sets; arbitrary
# labeled grids where the spec gives only a range (rain, lens, speeds,
# mu, e, conf — see tier1.json "basis" per axis).
GRIDS = {
    "outer_occlusion": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7],
    "inner_occlusion": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
    "illuminance_lux": [1, 2, 5, 10, 50, 100, 1000, 10000],
    "rain": [0.0, 0.1, 0.2, 0.3],
    "dropout_p": [0.0, 0.05, 0.1, 0.2, 0.3],
    "lens_contamination": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
    "tag_knockout_mask": [0, 1, 2, 4, 8, 16, 32, 64, 128, 256],
    "attempts_per_encounter": [1, 2, 3, 5],
    "speed_outer_ms": [0.5, 1.0, 1.5, 2.0],
    "speed_inner_ms": [0.1, 0.2, 0.3],
    "speed_insertion_ms": [0.02, 0.05, 0.1, 0.15],
    "mu_contact": [0.1, 0.2, 0.4, 0.6, 0.8],
    "restitution_e": [0.1, 0.2, 0.3, 0.4],
    "perception_rate_hz": [10, 30, 60],
    "perception_latency_ms": [10, 30, 100],
    "chassis_error_scale": [0.5, 1.0, 2.0],
    "conf_min_attempt": [0.5, 0.6, 0.7, 0.8, 0.85, 0.9, 0.95],
    "time_budget_min": [5, 15, 30],
    "mud_f_c": [0.6, 0.8, 1.0],
    "flip_kappa": [0.5, 1.0, 2.0],
    # D-046(a): the #40 committed sweep, realized (R01 F-009)
    "sigma_px": [0.3, 0.5, 1.0],
    "stiffness_k_n_mm": [1.0, 3.0, 10.0, 30.0, 70.0],
    "head_mass_kg": [8.0, 15.0, 30.0],
    # D-046(b): host attitude realized (H-17 closure) — D-024 envelope
    "host_pitch_deg": [-20.0, -10.0, 0.0, 10.0, 20.0],
    "host_roll_deg": [-20.0, -10.0, 0.0, 10.0, 20.0],
}

# The cell arithmetic, independently: every grid value is a cell, minus the
# grid points that duplicate the shared nominal cell, plus that one cell.
N_DEDUPED = sum(1 for axis, grid in GRIDS.items() if NOMINAL[axis] in grid)
N_CELLS = sum(len(g) for g in GRIDS.values()) - N_DEDUPED + 1


class TestCommittedFiles:
    def test_nominal_file_matches_transcription(self):
        assert tiers.load_nominal()["sweep_point"] == NOMINAL

    def test_tier1_grids_match_transcription(self):
        committed = tiers.load_tier1()["grids"]
        assert {a: g["cells"] for a, g in committed.items()} == GRIDS

    def test_every_grid_axis_documents_its_basis(self):
        assert all(g["basis"].strip()
                   for g in tiers.load_tier1()["grids"].values())

    def test_excluded_axes_are_curve_set_only(self):
        # D-046(b) retired the pitch/roll exclusions (H-17 realized);
        # the curve-swap seam is the one remaining non-marginal axis.
        excluded = tiers.load_tier1()["excluded"]
        assert set(excluded) == {"curve_set"}

    def test_spend_file_carries_the_p02_ceiling(self):
        spend = tiers.load_spend()
        assert spend["ceiling_usd"] == 100
        assert "P-02" in spend["source"]


class TestTier1Cells:
    def test_cell_count_matches_the_arithmetic(self):
        assert len(tiers.tier1_cells()) == N_CELLS == 98  # D-046: +2 sigma_px, +4 pitch, +4 roll

    def test_nominal_cell_appears_exactly_once(self):
        cells = tiers.tier1_cells()
        assert sum(1 for c in cells if c.axis is None) == 1
        assert [c.sweep_point for c in cells if c.axis is None] == [NOMINAL]

    def test_cells_are_nominal_elsewhere(self):
        # D-021: one-factor marginal grids at nominal elsewhere
        for c in tiers.tier1_cells():
            if c.axis is None:
                continue
            assert c.sweep_point == {**NOMINAL, c.axis: c.value}

    def test_no_cell_duplicates_the_nominal_point(self):
        points = [json.dumps(c.sweep_point, sort_keys=True)
                  for c in tiers.tier1_cells()]
        assert len(points) == len(set(points))

    def test_every_grid_value_is_covered(self):
        cells = tiers.tier1_cells()
        for axis, grid in GRIDS.items():
            got = {c.value for c in cells if c.axis == axis}
            expect = {v for v in grid if v != NOMINAL[axis]}
            assert got == expect, axis


class TestTier1Plan:
    def test_plan_size_is_cells_times_replicates(self):
        plan = tiers.tier1_plan(20260808, replicates=2)
        assert len(plan) == N_CELLS * 2

    def test_default_replicates_come_from_the_file(self):
        t1 = tiers.load_tier1()
        plan = tiers.tier1_plan(20260808)
        assert len(plan) == N_CELLS * t1["replicates_default"]

    def test_tags_and_seeds_are_unique(self):
        plan = tiers.tier1_plan(20260808, replicates=3)
        assert len({p.tag for p in plan}) == len(plan)
        assert len({p.seed for p in plan}) == len(plan)

    def test_plan_is_deterministic_in_the_sweep_root(self):
        a = tiers.tier1_plan(20260808, replicates=2)
        b = tiers.tier1_plan(20260808, replicates=2)
        c = tiers.tier1_plan(20260809, replicates=2)
        assert a == b
        assert {p.seed for p in a}.isdisjoint({p.seed for p in c})

    def test_every_point_builds_as_a_full_sweep_point(self):
        for p in tiers.tier1_plan(20260808, replicates=1):
            assert scenarios.build_sweep_point(**p.sweep_point) \
                == p.sweep_point


class TestTier2Plan:
    def test_default_n_meets_the_d021_floor(self):
        assert tiers.load_tier2()["n_min"] >= 4000

    def test_lhs_stratifies_grid_axes(self):
        # LHS property: over n = 8k samples of an 8-cell axis, each cell
        # appears exactly n/8 times
        plan = tiers.tier2_plan(20260808, n=40)
        counts = {}
        for p in plan:
            v = p.sweep_point["outer_occlusion"]
            counts[v] = counts.get(v, 0) + 1
        assert set(counts.values()) == {5}

    def test_samples_stay_inside_their_domains(self):
        for p in tiers.tier2_plan(20260808, n=64):
            sp = p.sweep_point
            assert 0.0 <= sp["rain"] <= 0.3
            assert 0.0 <= sp["lens_contamination"] <= 0.5
            assert sp["illuminance_lux"] in GRIDS["illuminance_lux"]
            assert sp["dropout_p"] in GRIDS["dropout_p"]
            assert 0 <= sp["tag_knockout_mask"] <= 511
            assert isinstance(sp["tag_knockout_mask"], int)

    def test_system_parameters_sit_at_nominal(self):
        # D-021: Tier 2 is the joint DEGRADATION space
        degradation = set(tiers.load_tier2()["domains"])
        for p in tiers.tier2_plan(20260808, n=16):
            for axis, v in p.sweep_point.items():
                if axis not in degradation:
                    assert v == NOMINAL[axis], axis

    def test_pitch_roll_excluded_from_the_joint_space(self):
        assert {"host_pitch_deg", "host_roll_deg"}.isdisjoint(
            tiers.load_tier2()["domains"])

    def test_deterministic_and_root_sensitive(self):
        assert tiers.tier2_plan(20260808, n=16) \
            == tiers.tier2_plan(20260808, n=16)
        assert tiers.tier2_plan(20260808, n=16) \
            != tiers.tier2_plan(20260809, n=16)


class TestGatePlan:
    def test_samples_stay_inside_the_d029_band(self):
        # the band is read from gate_moderate.json here too — no literals
        band = scenarios.load_gate_moderate()["band"]
        for p in tiers.gate_plan(20260808, n=64):
            sp = p.sweep_point
            assert sp["outer_occlusion"] in band["outer_occlusion"]["cells"]
            assert sp["inner_occlusion"] in band["inner_occlusion"]["cells"]
            assert sp["illuminance_lux"] in band["illuminance_lux"]["cells"]
            assert band["rain"]["lo"] <= sp["rain"] <= band["rain"]["hi"]
            assert sp["dropout_p"] == band["dropout_p"]["value"]
            assert (band["lens_contamination"]["lo"] <= sp["lens_contamination"]
                    <= band["lens_contamination"]["hi"])
            assert sp["tag_knockout_mask"] \
                == band["tag_knockout_mask"]["value"]

    def test_system_parameters_sit_at_nominal(self):
        gate_json = scenarios.load_gate_moderate()
        band = set(gate_json["band"])
        # D-046(b): encounter geometry (host pitch/roll) marginalizes per
        # trial; everything else still sits at its labeled default.
        geometry = {a for a, s in
                    gate_json.get("encounter_geometry_realization", {}).items()
                    if isinstance(s, dict)}
        for p in tiers.gate_plan(20260808, n=8):
            for axis, v in p.sweep_point.items():
                if axis not in band | geometry:
                    assert v == NOMINAL[axis], axis

    def test_gate_marginalizes_host_attitude_within_the_envelope(self):
        # D-046(b): the D-029 "marginalize over their full committed
        # distributions" text is now a real per-trial draw, not a no-op.
        pitches = set()
        for p in tiers.gate_plan(20260808, n=64):
            sp = p.sweep_point
            assert -20.0 <= sp["host_pitch_deg"] <= 20.0
            assert -20.0 <= sp["host_roll_deg"] <= 20.0
            pitches.add(round(sp["host_pitch_deg"], 3))
        assert len(pitches) > 8  # varies across trials — not pinned at 0

    def test_deterministic_and_independent_of_tier2(self):
        assert tiers.gate_plan(20260808, n=8) == tiers.gate_plan(20260808,
                                                                 n=8)
        gate_rain = [p.sweep_point["rain"]
                     for p in tiers.gate_plan(20260808, n=8)]
        t2_rain = [p.sweep_point["rain"]
                   for p in tiers.tier2_plan(20260808, n=8)]
        assert gate_rain != t2_rain  # distinct derived sampler streams


class TestSeedRule:
    def test_seed_is_a_pure_function_of_root_and_tag(self):
        assert tiers.derive_seed(1, "tier2:00001") \
            == tiers.derive_seed(1, "tier2:00001")
        assert tiers.derive_seed(1, "tier2:00001") \
            != tiers.derive_seed(2, "tier2:00001")
        assert tiers.derive_seed(1, "tier2:00001") \
            != tiers.derive_seed(1, "tier2:00002")

    def test_seed_fits_the_wire_integer(self):
        s = tiers.derive_seed(20260808, "gate:00000")
        assert 0 < s < 2 ** 63

    def test_replicates_get_distinct_seeds_at_the_same_point(self):
        # the pre-D-032 hazard: same sweep point + same seed → same
        # trial_id → silent overwrite; distinct replicate seeds fix it
        plan = [p for p in tiers.tier1_plan(20260808, replicates=2)
                if p.tag.startswith("tier1:nominal")]
        assert len(plan) == 2
        assert plan[0].seed != plan[1].seed
        assert plan[0].sweep_point == plan[1].sweep_point
