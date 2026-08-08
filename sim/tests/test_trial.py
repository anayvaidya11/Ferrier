"""T8 — trial.py composition root: the three gate assertions.

Gate (PHASE1_PLAN §4 row T8): full record validates line-by-line; #59
cadence asserted (sim_truth every kinematic step pre-handoff, every physics
step post-handoff); same seed twice → byte-identical files.

The nominal cell below (stiffness 70 N/mm, chassis scale 1.0, zero
degradation) latches on the first attempt — seed pinned by experiment,
T7 wedge-test style. Perception frames ride the open-loop kinematic
trajectory (T5 has no perception-in-the-loop by design; labeled in
trial.py), so the guidance machine sees the injected stream but only
abort/escalate/retry alter the record.
"""
import math

from wirefmt import records, validator
from wyzantium_sim import scenarios, trial
from wyzantium_sim.contact.mujoco_engine import MuJoCoEngine
from wyzantium_sim.kinematic import stage

SEED = 20260804

NOMINAL = {
    "outer_occlusion": 0.0, "inner_occlusion": 0.0,
    "illuminance_lux": 41000, "rain": 0.0, "dropout_p": 0.0,
    "lens_contamination": 0.0, "host_pitch_deg": 0.0, "host_roll_deg": 0.0,
    "tag_knockout_mask": 0, "attempts_per_encounter": 3,
    "speed_outer_ms": 1.0, "speed_inner_ms": 0.2, "speed_insertion_ms": 0.05,
    "mu_contact": 0.4, "restitution_e": 0.2, "perception_rate_hz": 30,
    "perception_latency_ms": 30, "chassis_error_scale": 1.0,
    "conf_min_attempt": 0.85, "time_budget_min": 15, "mud_f_c": 0.8,
    "flip_kappa": 1.0, "stiffness_k_n_mm": 70.0, "head_mass_kg": 15.0,
    "curve_set": "prior_v1",
}


def sweep(**overrides):
    return scenarios.build_sweep_point(**{**NOMINAL, **overrides})


def run(tmp_path, seed=SEED, engine=None, **overrides):
    eng = engine if engine is not None else MuJoCoEngine()
    return trial.run_trial(seed, sweep(**overrides), eng, "prior_v1",
                           out_dir=tmp_path)


def read(path):
    return records.read_ndjson(path)


def sim_truth_lines(lines, mode=None):
    out = [l for l in lines if l["type"] == "sim_truth"]
    if mode is not None:
        out = [l for l in out if l["actuator_cmd"]["mode"] == mode]
    return out


class CountingEngine:
    """ContactEngine wrapper: counts physics step() calls (#59 assert)."""

    def __init__(self):
        self.inner = MuJoCoEngine()
        self.step_calls = 0

    def load(self, spec, solver):
        return self.inner.load(spec, solver)

    def set_state(self, handoff):
        return self.inner.set_state(handoff)

    def step(self, dt):
        self.step_calls += 1
        return self.inner.step(dt)

    def state(self):
        return self.inner.state()

    @property
    def engine_id(self):
        return self.inner.engine_id


class TestTheGate:
    def test_full_record_validates_line_by_line(self, tmp_path):
        assert validator.validate_trial_file(run(tmp_path)) == []

    def test_59_cadence_pre_handoff(self, tmp_path):
        lines = read(run(tmp_path))
        kin = stage.KinematicStage(
            root=SEED, scale=NOMINAL["chassis_error_scale"],
            speeds=(NOMINAL["speed_outer_ms"], NOMINAL["speed_inner_ms"],
                    NOMINAL["speed_insertion_ms"])).run()
        assert len(sim_truth_lines(lines, "velocity")) == len(kin.steps)

    def test_59_cadence_post_handoff(self, tmp_path):
        eng = CountingEngine()
        lines = read(run(tmp_path, engine=eng))
        # one sim_truth per step() call; the pre-loop state() is not logged
        assert len(sim_truth_lines(lines, "gravity_insert")) == eng.step_calls

    def test_same_seed_twice_byte_identical(self, tmp_path):
        a = run(tmp_path / "a")
        b = run(tmp_path / "b")
        assert a.read_bytes() == b.read_bytes()

    def test_same_seed_reused_engine_byte_identical(self, tmp_path):
        eng = MuJoCoEngine()
        a = run(tmp_path / "a", engine=eng)
        b = run(tmp_path / "b", engine=eng)
        assert a.read_bytes() == b.read_bytes()

    def test_different_seed_differs(self, tmp_path):
        a = run(tmp_path / "a")
        b = run(tmp_path / "b", seed=SEED + 1)
        assert a.read_bytes() != b.read_bytes()


class TestHeader:
    def test_header_contents_verbatim(self, tmp_path):
        header = read(run(tmp_path))[0]
        assert header["type"] == "trial_header"
        assert header["seed"] == SEED
        assert header["sweep_point"] == sweep()
        assert header["engine"]["name"] == "mujoco"
        assert header["params_ref"] == "PHASE1_PARAMETERS.md"
        assert header["solver"]["timestep_s"] == trial.TRIAL_TIMESTEP_S
        assert len(header["code_git_sha"]) >= 8

    def test_trial_id_is_stable_across_runs(self, tmp_path):
        a = read(run(tmp_path / "a"))[0]["trial_id"]
        b = read(run(tmp_path / "b"))[0]["trial_id"]
        assert a == b
        assert a.startswith("mujoco-")


class TestRecordShape:
    def test_wrench_omitted_pre_contact_present_after(self, tmp_path):
        contact = sim_truth_lines(read(run(tmp_path)), "gravity_insert")
        pre = [l for l in contact if "contact_wrench" not in l]
        post = [l for l in contact if "contact_wrench" in l]
        assert pre and post
        first_with = contact.index(post[0])
        assert all("contact_wrench" in l for l in contact[first_with:])

    def test_kinematic_lines_never_carry_wrench(self, tmp_path):
        for line in sim_truth_lines(read(run(tmp_path)), "velocity"):
            assert "contact_wrench" not in line

    def test_target_state_stages_are_wire_enum(self, tmp_path):
        for line in read(run(tmp_path)):
            if line["type"] == "target_state":
                assert line["stage"] in validator.STAGES
                assert line["attempt"]["n"] >= 1


class TestOutcomes:
    def test_nominal_trial_succeeds_first_attempt(self, tmp_path):
        result = read(run(tmp_path))[-1]
        assert result["outcome"] == "success"
        assert result["first_attempt_success"] is True
        assert result["attempts_used"] == 1
        assert result["handoff_reached"] is True

    def test_saturated_dropout_is_outer_destroyed(self, tmp_path):
        # zero ID-0 detections across the whole approach is §8 row 2's
        # signature ("No ID-0 across approach; mission context positive"),
        # not row 1's sparse-with-degradation shape — the interim map's
        # IS8-1 label was signature-wrong
        path = run(tmp_path, dropout_p=1.0)
        assert validator.validate_trial_file(path) == []
        lines = read(path)
        assert lines[-1]["outcome"] == "IS8-2"
        assert lines[-1]["handoff_reached"] is False
        escalated = [l for l in lines if l["type"] == "target_state"
                     and l["stage"] == "escalate"]
        assert escalated and "escalation" in escalated[-1]

    def test_time_budget_short_circuit_is_clean_miss(self, tmp_path):
        # budget expires mid-approach: stream nominal, no contact ever —
        # the D-030 residual, all four clauses checked by the T9 classifier
        # (constructed-trace coverage lives in test_outcomes.py)
        path = run(tmp_path, time_budget_min=0.05)
        assert validator.validate_trial_file(path) == []
        assert read(path)[-1]["outcome"] == "clean_miss"
