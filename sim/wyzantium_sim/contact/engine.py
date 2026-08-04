"""ContactEngine boundary types (PHASE1_PLAN §3).

`load(T1ModelSpec, SolverSettings)` / `set_state(HandoffState)` / `step(dt) →
StepResult` / `state()`. StepResult carries body states plus per-contact-point
reports (position in head_frame, normal, force) and the aggregated wall wrench —
per-point data is deliberate: ARCH §4 needs lateral-error direction, IS8-16 needs
contact radius in the lip band, IS8-17 needs the axial/lateral split.

Units: positions mm (repo convention, D-016), velocities m/s (IS §6), forces N,
moments N·m, all in head_frame (WIRE_FORMAT contact_wrench). Geometry defaults
are the D-016 committed set via wyzantium_sim.geometry; material defaults are
PHASE1_PARAMETERS #31/#32. Solver defaults below are code-level first-pass
values (arbitrary, pre-#33 probe) — the #33 convergence procedure revises the
timestep and the values are logged per run in trial_header.solver.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Protocol

from wyzantium_sim import geometry


@dataclass(frozen=True)
class T1ModelSpec:
    """T1 topology (#34, D-027): rigid stud, rigid funnel on one 6-DOF
    spring-damper base with hard stops. Sweep axes are ctor args; geometry is
    the committed D-016 set and is not a knob."""

    stiffness_k_n_mm: float
    head_mass_kg: float
    mu_contact: float = 0.4       # #31 default
    restitution_e: float = 0.2    # #32 default
    # Not committed anywhere (spec gaps, 2026-08-04) — arbitrary code-level
    # defaults: mission gravity is head-up +Z (IS §4), stud-side body mass is
    # a target-vehicle class value.
    gravity_head_ms2: tuple = (0.0, 0.0, -9.81)
    stud_mass_kg: float = 300.0

    stud_neck_d_mm: float = geometry.STUD_NECK_DIAMETER_MM
    stud_head_d_mm: float = geometry.STUD_HEAD_DIAMETER_MM
    stud_exposed_mm: float = geometry.STUD_EXPOSED_LENGTH_MM
    mouth_d_mm: float = geometry.FUNNEL_MOUTH_DIAMETER_MM
    throat_d_mm: float = geometry.FUNNEL_THROAT_DIAMETER_MM
    depth_mm: float = geometry.FUNNEL_DEPTH_MM
    lip_band_mm: tuple = geometry.LIP_BAND_MM
    annulus_r_mm: float = geometry.ANNULUS_RADIUS_MM


@dataclass(frozen=True)
class SolverSettings:
    """First-pass numerical settings (pre-#33). Serialized verbatim into
    trial_header.solver (H-03: logged per run)."""

    timestep_s: float = 0.001
    integrator: str = "implicitfast"
    solver_iterations: int = 100

    def to_wire(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ContactPoint:
    """One contact report: position in head_frame (mm), unit normal pointing
    from the funnel surface toward the stud (head_frame), and the force the
    wall exerts on the stud (N, head_frame)."""

    pos_head_mm: tuple
    normal: tuple
    force_n: tuple


@dataclass(frozen=True)
class StepResult:
    """Everything downstream consumes StepResult only (PHASE1_PLAN §3)."""

    t_sim_s: float
    T_head_stud: object
    stud_v_ms: tuple
    stud_omega_rads: tuple
    contacts: tuple = field(default_factory=tuple)
    wall_wrench: tuple = (0.0,) * 6  # [fx,fy,fz,mx,my,mz] N, N·m, head_frame
    funnel_t_mm: tuple = (0.0, 0.0, 0.0)  # 6-DOF base translation (mm)


class ContactEngine(Protocol):
    def load(self, spec: T1ModelSpec, solver: "SolverSettings") -> None: ...

    def set_state(self, handoff) -> None: ...

    def step(self, dt: float) -> StepResult: ...

    def state(self) -> StepResult: ...
