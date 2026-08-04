"""T4c cycle A — spec dataclasses for the contact engine boundary.

Double-entry: committed numbers are re-transcribed here from the docs, independently
of wyzantium_sim.geometry, so a code edit cannot silently drift from the spec.

Sources: PHASE1_PLAN §3 (ContactEngine protocol, StepResult contents);
PHASE1_PARAMETERS #1-#3, #4-#7, #12-#14 (geometry), #31/#32 (mu_contact,
restitution defaults), #34 (T1 topology), #36 (M_eff); INTERFACE_SPEC §6
(handoff state vector — six fields, nothing else crosses, D-006);
WIRE_FORMAT (trial_header.solver is a JSON object; contact_wrench is
[fx,fy,fz,mx,my,mz] N, N·m, head_frame).
"""

import dataclasses
import json

from wyzantium_sim.contact import engine
from wyzantium_sim.kinematic.handoff import HandoffState

# PHASE1_PARAMETERS §Geometry, transcribed
STUD_NECK_D_MM = 25.0     # 1
STUD_HEAD_D_MM = 40.0     # 2
STUD_EXPOSED_MM = 90.0    # 3
MOUTH_D_MM = 220.0        # 4
THROAT_D_MM = 42.0        # 5
DEPTH_MM = 180.0          # 6
LIP_BAND_MM = (110.0, 125.0)  # 12
ANNULUS_R_MM = 160.0      # 13

MU_CONTACT_DEFAULT = 0.4  # 31
RESTITUTION_DEFAULT = 0.2  # 32
M_EFF_DEFAULT_KG = 15.0   # 36 default


def make_spec(**overrides):
    defaults = dict(stiffness_k_n_mm=10.0, head_mass_kg=M_EFF_DEFAULT_KG)
    defaults.update(overrides)
    return engine.T1ModelSpec(**defaults)


class TestT1ModelSpec:
    def test_committed_geometry(self):
        spec = make_spec()
        assert spec.stud_neck_d_mm == STUD_NECK_D_MM
        assert spec.stud_head_d_mm == STUD_HEAD_D_MM
        assert spec.stud_exposed_mm == STUD_EXPOSED_MM
        assert spec.mouth_d_mm == MOUTH_D_MM
        assert spec.throat_d_mm == THROAT_D_MM
        assert spec.depth_mm == DEPTH_MM
        assert spec.lip_band_mm == LIP_BAND_MM
        assert spec.annulus_r_mm == ANNULUS_R_MM

    def test_material_defaults_are_params_31_32(self):
        spec = make_spec()
        assert spec.mu_contact == MU_CONTACT_DEFAULT
        assert spec.restitution_e == RESTITUTION_DEFAULT

    def test_sweep_axes_are_explicit_ctor_args(self):
        spec = make_spec(stiffness_k_n_mm=70.0, head_mass_kg=30.0,
                         mu_contact=0.8, restitution_e=0.1)
        assert spec.stiffness_k_n_mm == 70.0
        assert spec.head_mass_kg == 30.0
        assert spec.mu_contact == 0.8
        assert spec.restitution_e == 0.1

    def test_frozen(self):
        spec = make_spec()
        try:
            spec.mouth_d_mm = 0.0
        except dataclasses.FrozenInstanceError:
            return
        raise AssertionError("T1ModelSpec must be frozen (D-016: geometry is committed)")


class TestSolverSettings:
    def test_wire_dict_is_json_object(self):
        s = engine.SolverSettings()
        wire = s.to_wire()
        assert isinstance(wire, dict)
        json.dumps(wire)  # #33: must land in trial_header.solver as-is

    def test_wire_dict_carries_timestep(self):
        s = engine.SolverSettings(timestep_s=0.0005)
        assert s.to_wire()["timestep_s"] == 0.0005


class TestHandoffState:
    def test_fields_are_exactly_the_is6_list(self):
        # IS §6: T_head_stud, v (m/s), omega (rad/s), pose covariance 6x6,
        # attempt index, sim time. Nothing else crosses (D-006).
        names = [f.name for f in dataclasses.fields(HandoffState)]
        assert names == [
            "T_head_stud", "v_ms", "omega_rads", "pose_cov", "attempt", "t_sim_s",
        ]

    def test_frozen(self):
        assert dataclasses.fields(HandoffState)[0].name  # is a dataclass
        params = dataclasses.asdict  # noqa: F841 (dataclass API present)
        assert getattr(HandoffState, "__dataclass_params__").frozen


class TestStepResult:
    def test_carries_body_states_contacts_and_wall_wrench(self):
        cp = engine.ContactPoint(pos_head_mm=(120.0, 0.0, 0.0),
                                 normal=(-1.0, 0.0, 0.0),
                                 force_n=(0.0, 0.0, 5.0))
        r = engine.StepResult(
            t_sim_s=0.1,
            T_head_stud=None,
            stud_v_ms=(0.0, 0.0, 0.0),
            stud_omega_rads=(0.0, 0.0, 0.0),
            contacts=(cp,),
            wall_wrench=(0.0, 0.0, 5.0, 0.0, 0.0, 0.0),
        )
        assert len(r.wall_wrench) == 6  # WIRE_FORMAT: [fx,fy,fz,mx,my,mz] N, N·m
        assert r.contacts[0].pos_head_mm == (120.0, 0.0, 0.0)
