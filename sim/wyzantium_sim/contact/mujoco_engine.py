"""MuJoCo adapter for the ContactEngine protocol (T4c).

Model (T1, #34/D-027): rigid stud (free body) vs rigid funnel mounted on a
6-DOF spring-damper base with hard stops. World frame == head_frame: origin at
the funnel mouth center, +X toward the throat (mouth plane x=0, throat at
x=+180 mm). The funnel cone is a ring of N_FACETS thin boxes (MuJoCo
convexifies meshes, which would fill the funnel; facets keep it hollow), plus
the flat lip ring [110,125] mm at x=0 (IS8-16 band), a throat land, and a
pocket floor.

Committed numbers come in via T1ModelSpec (D-016 geometry, #31/#32/#35/#36).
Everything below marked "arbitrary" is a code-level choice the docs do not
commit (spec gaps recorded 2026-08-04): mount damping ratio, rotational
stiffness, stud body mass/inertia, contact stiffness, facet count, pocket
depth. Changing a committed number is a decision revision; changing an
arbitrary constant is tuning.

Units at the boundary: mm poses, m/s velocities, N / N·m wrench, head_frame
(WIRE_FORMAT). Internally MuJoCo is metres. Free-joint angular rate is
body-frame (MuJoCo convention); documented for T5.

Restitution mapping (#32): contact solref uses the direct spring-damper form
(-K_C, -B_C) with B_C = 2·ζ·√(K_C·m_stud) and ζ = -ln e / √(π² + ln² e) — the
closed-form mass-spring-damper rebound relation; conformance item 5 checks it.
"""

from __future__ import annotations

import math

import mujoco
import numpy as np

from wyzantium_sim import frames
from wyzantium_sim.contact.engine import (
    ContactPoint,
    SolverSettings,
    StepResult,
    T1ModelSpec,
)

# --- arbitrary code-level constants (labeled; not committed anywhere) ---
N_FACETS = 24                 # cone/lip/throat facet count
WALL_HALF_THICK_M = 0.0025    # facet half-thickness
MOUNT_DAMPING_RATIO = 0.7     # 6-DOF base damping ratio
K_ROT_NM_PER_RAD = 500.0      # base rotational stiffness (angular DOFs)
FUNNEL_DIAG_INERTIA = 0.3     # kg·m², funnel body
STUD_DIAG_INERTIA = 5.0       # kg·m², stud body
K_CONTACT_N_M = 2.0e5         # contact normal stiffness for solref
POCKET_FLOOR_X_M = 0.2225     # pocket floor center (face at x=220 mm)
THROAT_LAND_LEN_M = 0.040     # throat tube length behind x=180 mm
HARD_STOP_TRANS_M = 0.035     # ±35 mm (§5 capture envelope)
HARD_STOP_ROT_RAD = math.radians(10.0)  # ±10°

STUD_HEAD_CENTER_STUD_M = 0.070  # exposed 90 − head radius 20 (D-016)


def _zeta_from_restitution(e: float) -> float:
    if e >= 1.0:
        return 0.0
    ln_e = math.log(max(e, 1e-6))
    return -ln_e / math.sqrt(math.pi**2 + ln_e**2)


def _quat_attr(R: np.ndarray) -> str:
    q = np.empty(4)
    mujoco.mju_mat2Quat(q, R.flatten())
    return " ".join(f"{v:.9f}" for v in q)


def _facet_geoms(spec: T1ModelSpec) -> list:
    """Cone wall + lip ring + throat land boxes, as MJCF geom strings."""
    r0 = spec.mouth_d_mm / 2000.0        # 0.110
    r1 = spec.throat_d_mm / 2000.0       # 0.021
    depth = spec.depth_mm / 1000.0       # 0.180
    lip_in = spec.lip_band_mm[0] / 1000.0
    lip_out = spec.lip_band_mm[1] / 1000.0
    t = WALL_HALF_THICK_M
    slant = math.hypot(depth, r0 - r1)
    geoms = []
    for i in range(N_FACETS):
        th = 2.0 * math.pi * (i + 0.5) / N_FACETS
        c, s = math.cos(th), math.sin(th)
        radial = np.array([0.0, c, s])
        tang = np.array([0.0, -s, c])
        # cone facet: e1 along slant (mouth→throat), e3 = e1×e2 (interior normal)
        e1 = np.array([depth, (r1 - r0) * c, (r1 - r0) * s]) / slant
        e3 = np.cross(e1, tang)
        mid = np.array([depth / 2.0, (r0 + r1) / 2.0 * c, (r0 + r1) / 2.0 * s])
        center = mid - e3 * t
        R = np.column_stack([e1, tang, e3])
        geoms.append(
            f'<geom name="cone{i}" type="box" pos="{center[0]:.6f} {center[1]:.6f} '
            f'{center[2]:.6f}" quat="{_quat_attr(R)}" '
            f'size="{slant / 2.0 + 0.002:.6f} {math.pi * r0 / N_FACETS:.6f} {t}"/>'
        )
        # lip ring facet at x=0, face toward -x
        lm = (lip_in + lip_out) / 2.0
        Rl = np.column_stack([radial, tang, np.array([1.0, 0.0, 0.0])])
        geoms.append(
            f'<geom name="lip{i}" type="box" pos="{t:.6f} {lm * c:.6f} {lm * s:.6f}" '
            f'quat="{_quat_attr(Rl)}" '
            f'size="{(lip_out - lip_in) / 2.0:.6f} {math.pi * lip_out / N_FACETS:.6f} {t}"/>'
        )
        # throat land: axis-parallel tube from depth to depth+len
        rt = r1 + t
        # right-handed: x̂ × (−tang) = +radial (thickness along the radial axis)
        Rt = np.column_stack([np.array([1.0, 0.0, 0.0]), -tang, radial])
        geoms.append(
            f'<geom name="throat{i}" type="box" '
            f'pos="{depth + THROAT_LAND_LEN_M / 2.0:.6f} {rt * c:.6f} {rt * s:.6f}" '
            f'quat="{_quat_attr(Rt)}" '
            f'size="{THROAT_LAND_LEN_M / 2.0:.6f} {math.pi * r1 / N_FACETS:.6f} {t}"/>'
        )
    geoms.append(
        f'<geom name="pocket_floor" type="cylinder" '
        f'pos="{POCKET_FLOOR_X_M:.6f} 0 0" quat="0.7071068 0 0.7071068 0" '
        f'size="{r1 + 0.003:.6f} {WALL_HALF_THICK_M}"/>'
    )
    return geoms


def _build_xml(spec: T1ModelSpec, solver: SolverSettings) -> str:
    k_trans = spec.stiffness_k_n_mm * 1000.0          # N/mm → N/m
    b_trans = 2.0 * MOUNT_DAMPING_RATIO * math.sqrt(k_trans * spec.head_mass_kg)
    b_rot = 2.0 * MOUNT_DAMPING_RATIO * math.sqrt(
        K_ROT_NM_PER_RAD * FUNNEL_DIAG_INERTIA)
    zeta = _zeta_from_restitution(spec.restitution_e)
    b_contact = 2.0 * zeta * math.sqrt(K_CONTACT_N_M * spec.stud_mass_kg)
    g = spec.gravity_head_ms2
    head_r = spec.stud_head_d_mm / 2000.0
    neck_r = spec.stud_neck_d_mm / 2000.0

    slides = "\n".join(
        f'<joint name="base_t{a}" type="slide" axis="{ax}" stiffness="{k_trans}" '
        f'damping="{b_trans}" range="-{HARD_STOP_TRANS_M} {HARD_STOP_TRANS_M}" '
        f'limited="true"/>'
        for a, ax in (("x", "1 0 0"), ("y", "0 1 0"), ("z", "0 0 1")))
    hinges = "\n".join(
        f'<joint name="base_r{a}" type="hinge" axis="{ax}" '
        f'stiffness="{K_ROT_NM_PER_RAD}" damping="{b_rot}" '
        f'range="-{HARD_STOP_ROT_RAD} {HARD_STOP_ROT_RAD}" limited="true"/>'
        for a, ax in (("x", "1 0 0"), ("y", "0 1 0"), ("z", "0 0 1")))

    return f"""
<mujoco model="t1_contact">
  <compiler angle="radian"/>
  <option timestep="{solver.timestep_s}" integrator="{solver.integrator}"
          iterations="{solver.solver_iterations}"
          gravity="{g[0]} {g[1]} {g[2]}"/>
  <default>
    <geom solref="{-K_CONTACT_N_M} {-b_contact:.4f}" solimp="0.99 0.999 0.0001"
          friction="{spec.mu_contact} 0.005 0.0001"/>
  </default>
  <worldbody>
    <body name="funnel" pos="0 0 0">
      <inertial pos="{spec.depth_mm / 2000.0} 0 0" mass="{spec.head_mass_kg}"
                diaginertia="{FUNNEL_DIAG_INERTIA} {FUNNEL_DIAG_INERTIA} {FUNNEL_DIAG_INERTIA}"/>
      {slides}
      {hinges}
      {chr(10).join(_facet_geoms(spec))}
    </body>
    <body name="stud" pos="-0.5 0 0">
      <freejoint name="stud_free"/>
      <inertial pos="{STUD_HEAD_CENTER_STUD_M / 2.0} 0 0" mass="{spec.stud_mass_kg}"
                diaginertia="{STUD_DIAG_INERTIA} {STUD_DIAG_INERTIA} {STUD_DIAG_INERTIA}"/>
      <geom name="stud_head" type="sphere" pos="{STUD_HEAD_CENTER_STUD_M} 0 0"
            size="{head_r}"/>
      <geom name="stud_neck" type="capsule" fromto="0 0 0 {STUD_HEAD_CENTER_STUD_M} 0 0"
            size="{neck_r}"/>
    </body>
  </worldbody>
</mujoco>
"""


class MuJoCoEngine:
    """ContactEngine adapter over mujoco.MjModel/MjData."""

    def __init__(self):
        self._model = None
        self._data = None
        self._stud_body = -1

    @property
    def engine_id(self) -> dict:
        return {"name": "mujoco", "version": mujoco.__version__}

    def load(self, spec: T1ModelSpec, solver: SolverSettings) -> None:
        self._model = mujoco.MjModel.from_xml_string(_build_xml(spec, solver))
        self._data = mujoco.MjData(self._model)
        self._stud_body = mujoco.mj_name2id(
            self._model, mujoco.mjtObj.mjOBJ_BODY, "stud")
        self._base_qadr = [
            self._model.jnt_qposadr[mujoco.mj_name2id(
                self._model, mujoco.mjtObj.mjOBJ_JOINT, f"base_t{a}")]
            for a in "xyz"]
        mujoco.mj_forward(self._model, self._data)

    def set_state(self, handoff) -> None:
        d = self._data
        pose = handoff.T_head_stud
        d.qpos[:] = 0.0
        d.qvel[:] = 0.0
        jadr = self._model.jnt_qposadr[
            mujoco.mj_name2id(self._model, mujoco.mjtObj.mjOBJ_JOINT, "stud_free")]
        vadr = self._model.jnt_dofadr[
            mujoco.mj_name2id(self._model, mujoco.mjtObj.mjOBJ_JOINT, "stud_free")]
        d.qpos[jadr:jadr + 3] = [v / 1000.0 for v in pose.t]
        d.qpos[jadr + 3:jadr + 7] = pose.q
        d.qvel[vadr:vadr + 3] = handoff.v_ms
        d.qvel[vadr + 3:vadr + 6] = handoff.omega_rads
        d.time = handoff.t_sim_s
        mujoco.mj_forward(self._model, self._data)

    def step(self, dt: float) -> StepResult:
        if dt != self._model.opt.timestep:
            self._model.opt.timestep = dt
        mujoco.mj_step(self._model, self._data)
        return self._result()

    def state(self) -> StepResult:
        return self._result()

    def _result(self) -> StepResult:
        m, d = self._model, self._data
        jadr = m.jnt_qposadr[
            mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "stud_free")]
        vadr = m.jnt_dofadr[
            mujoco.mj_name2id(m, mujoco.mjtObj.mjOBJ_JOINT, "stud_free")]
        pose = frames.Pose(
            t=tuple(float(v) * 1000.0 for v in d.qpos[jadr:jadr + 3]),
            q=tuple(float(v) for v in d.qpos[jadr + 3:jadr + 7]))
        contacts, wrench = self._contact_reports()
        return StepResult(
            t_sim_s=float(d.time),
            T_head_stud=pose,
            stud_v_ms=tuple(float(v) for v in d.qvel[vadr:vadr + 3]),
            stud_omega_rads=tuple(float(v) for v in d.qvel[vadr + 3:vadr + 6]),
            contacts=contacts,
            wall_wrench=wrench,
            funnel_t_mm=tuple(
                float(d.qpos[a]) * 1000.0 for a in self._base_qadr),
        )

    def _contact_reports(self):
        m, d = self._model, self._data
        pts = []
        f_tot = np.zeros(3)
        tau_tot = np.zeros(3)
        buf = np.zeros(6)
        for i in range(d.ncon):
            con = d.contact[i]
            g1, g2 = int(con.geom[0]), int(con.geom[1])
            b1, b2 = int(m.geom_bodyid[g1]), int(m.geom_bodyid[g2])
            if self._stud_body not in (b1, b2):
                continue
            mujoco.mj_contactForce(m, d, i, buf)
            frame = np.array(con.frame).reshape(3, 3)
            f_world = frame.T @ buf[:3]      # acts on geom2 along +normal
            n_world = frame[0].copy()        # points geom1 → geom2
            if b1 == self._stud_body:        # stud is geom1: flip to wall-on-stud
                f_world = -f_world
                n_world = -n_world
            pos = np.array(con.pos)
            pts.append(ContactPoint(
                pos_head_mm=tuple(float(v) * 1000.0 for v in pos),
                normal=tuple(float(v) for v in n_world),
                force_n=tuple(float(v) for v in f_world)))
            f_tot += f_world
            tau_tot += np.cross(pos, f_world)
        wrench = tuple(float(v) for v in np.concatenate([f_tot, tau_tot]))
        return tuple(pts), wrench
