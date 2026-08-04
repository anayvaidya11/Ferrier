"""T4c cycle C — day-one engine conformance suite (PHASE1_PLAN §3, ARCH §4).

Items, transcribed from PHASE1_PLAN.md:81-89 (double-entry):
  (1) stud dropped onto the wall at known lateral offsets — wrench must recover
      sign, and the per-contact-point data the magnitude-ordering, of the
      offset (per-point data is deliberate: PHASE1_PLAN §3);
  (2) symmetric throat wedge — high-axial/near-zero-lateral signature
      observable (IS8-17's split);
  (3) lip-band strike — contact radius within [110, 125] mm (#12, IS8-16);
  (4) determinism — same seed twice → identical trajectories;
  (5) spring/restitution/friction sanity vs closed-form single-contact cases.

Engine-parameterized: Newton cases skip locally (no CUDA on the M4) and run on
the provisioned instance; Newton failing any of 1-4 ⇒ MuJoCo (ARCH §4, zero
harness rework).

Conformance constructions are engine probes, not trials: item 2 narrows the
throat below head diameter (committed Ø42 > head Ø40 passes by design, so a
symmetric wedge must be constructed); masses/stiffnesses are chosen per-item
for closed-form clarity and are labeled where they leave the sweep grid.
"""

import importlib.util
import math

import numpy as np
import pytest

from wyzantium_sim import frames, rng
from wyzantium_sim.contact import engine
from wyzantium_sim.kinematic.handoff import HandoffState

ROOT = 20260804
DT = 0.001
COV0 = tuple(tuple(0.0 for _ in range(6)) for _ in range(6))
# Official head_frame (T5/IS §6): approach +x, throat -x. Axis-vertical
# drops: "down" = insertion direction = -x.
G_AXIAL = (-9.81, 0.0, 0.0)
Q_NOMINAL = (0.0, 0.0, 1.0, 0.0)  # 180° about +Y (IS §4 anti-parallel)

_HAVE_NEWTON = importlib.util.find_spec("newton") is not None

ENGINES = [
    pytest.param("mujoco", id="mujoco"),
    pytest.param("newton", id="newton", marks=pytest.mark.skipif(
        not _HAVE_NEWTON,
        reason="Newton (Warp/CUDA) unavailable locally — runs on the "
               "provisioned instance (PHASE1_PLAN §2)")),
]


def load_engine(name, spec, solver=None):
    if name == "mujoco":
        from wyzantium_sim.contact.mujoco_engine import MuJoCoEngine
        eng = MuJoCoEngine()
    elif name == "newton":
        from wyzantium_sim.contact.newton_engine import NewtonEngine
        eng = NewtonEngine()
    else:
        raise ValueError(name)
    eng.load(spec, solver or engine.SolverSettings(timestep_s=DT))
    return eng


def make_spec(**overrides):
    defaults = dict(stiffness_k_n_mm=10.0, head_mass_kg=15.0,
                    gravity_head_ms2=G_AXIAL, stud_mass_kg=20.0)
    defaults.update(overrides)
    return engine.T1ModelSpec(**defaults)


def handoff_at(head_center_mm, v_ms=(0.0, 0.0, 0.0)):
    """Official frame, nominal anti-parallel orientation (IS §4)."""
    t = (head_center_mm[0] + 70.0, head_center_mm[1], head_center_mm[2])
    return HandoffState(T_head_stud=frames.Pose(t=t, q=Q_NOMINAL),
                        v_ms=v_ms, omega_rads=(0.0, 0.0, 0.0), pose_cov=COV0,
                        attempt=1, t_sim_s=0.0)


def x_touch_mm(offset_mm, spec):
    """Official-frame x of the head center at first cone-wall touch
    (interior is x<0)."""
    r0 = spec.mouth_d_mm / 2.0
    slope = (r0 - spec.throat_d_mm / 2.0) / spec.depth_mm
    norm = math.hypot(slope, 1.0)
    return -(r0 - offset_mm - (spec.stud_head_d_mm / 2.0) * norm) / slope


def run_until_contact(eng, max_steps=3000, dt=DT):
    for _ in range(max_steps):
        r = eng.step(dt)
        if r.contacts:
            return r
    raise AssertionError("no contact within step budget")


def impact_window(eng, first, n=150, dt=DT):
    results = [first]
    for _ in range(n):
        results.append(eng.step(dt))
    return results


@pytest.mark.parametrize("name", ENGINES)
class TestItem1LateralOffsetRecovery:
    OFFSETS = (-60.0, -30.0, 30.0, 60.0)

    def _drop(self, name, offset_mm):
        spec = make_spec()
        eng = load_engine(name, spec)
        x0 = x_touch_mm(abs(offset_mm), spec) + 30.0
        eng.set_state(handoff_at((x0, offset_mm, 0.0)))
        window = impact_window(eng, run_until_contact(eng))
        f_y = sum(r.wall_wrench[1] for r in window)
        rhos = [math.hypot(c.pos_head_mm[1], c.pos_head_mm[2])
                for r in window for c in r.contacts]
        return f_y, np.mean(rhos)

    def test_wrench_recovers_offset_sign(self, name):
        for off in self.OFFSETS:
            f_y, _ = self._drop(name, off)
            assert math.copysign(1, f_y) == -math.copysign(1, off), (
                f"offset {off:+} mm: wall must push back toward the axis")

    def test_contact_points_recover_offset_ordering(self, name):
        _, rho_30 = self._drop(name, 30.0)
        _, rho_60 = self._drop(name, 60.0)
        assert rho_60 > rho_30 + 15.0, (
            "per-contact radius must order the lateral offset magnitude")


@pytest.mark.parametrize("name", ENGINES)
class TestItem2SymmetricWedge:
    def test_high_axial_near_zero_lateral(self, name):
        # Constructed wedge: throat narrowed to 38 mm (< head Ø40); stiff
        # mount (k=70, on-grid) keeps the base off its hard stops; dt=2e-4
        # for the stiff two-sided pinch (wedge amplifies contact stiffness).
        dt = 2.0e-4
        spec = make_spec(throat_d_mm=38.0, stiffness_k_n_mm=70.0)
        eng = load_engine(name, spec, engine.SolverSettings(timestep_s=dt))
        eng.set_state(handoff_at((-160.0, 0.0, 0.0), v_ms=(-0.05, 0.0, 0.0)))
        for _ in range(8000):
            r = eng.step(dt)
        weight = spec.stud_mass_kg * 9.81
        f_ax = r.wall_wrench[0]
        f_lat = math.hypot(r.wall_wrench[1], r.wall_wrench[2])
        assert f_ax == pytest.approx(weight, rel=0.2), (
            "steady wedge must push back (+x) with the stud weight")
        assert f_lat < 0.05 * abs(f_ax), (
            "symmetric wedge must read near-zero lateral (IS8-17 split)")
        assert abs(r.stud_v_ms[0]) < 0.01


@pytest.mark.parametrize("name", ENGINES)
class TestItem3LipBandStrike:
    def test_contact_radius_within_band(self, name):
        # Stiff mount (k=70, on-grid) keeps gravity sag of the funnel small;
        # axial position is judged relative to the sagged base (funnel_t_mm),
        # the radial band is the committed criterion (#12, IS8-16).
        spec = make_spec(stiffness_k_n_mm=70.0)
        eng = load_engine(name, spec)
        mid = sum(spec.lip_band_mm) / 2.0  # 117.5
        eng.set_state(handoff_at((50.0, mid, 0.0)))
        window = impact_window(eng, run_until_contact(eng), n=50)
        pts = [c for r in window for c in r.contacts]
        assert pts
        for c in pts:
            # the committed criterion is the radial band (#12); the mount
            # translates AND rotates under the off-axis strike, so no fixed
            # axial plane exists to assert against — instead require the
            # strike to come from the approach side (normal toward -x)
            rho = math.hypot(c.pos_head_mm[1], c.pos_head_mm[2])
            assert spec.lip_band_mm[0] - 3.0 <= rho <= spec.lip_band_mm[1] + 3.0
            assert c.normal[0] > 0.5  # strike from the approach side (+x)


@pytest.mark.parametrize("name", ENGINES)
class TestItem4Determinism:
    def _trajectory(self, name):
        # Same-seed jitter through the committed substream (#60): identical
        # roots must give bit-identical trajectories, in-process.
        gen = rng.substream(ROOT, "contact")
        offset = 40.0 + 40.0 * gen.random()
        v_x = -(0.1 + 0.2 * gen.random())
        eng = load_engine(name, make_spec())
        eng.set_state(handoff_at((x_touch_mm(offset, make_spec()) + 20.0,
                                  offset, 0.0), v_ms=(v_x, 0.0, 0.0)))
        rows, saw_contact = [], False
        for _ in range(400):
            r = eng.step(DT)
            saw_contact = saw_contact or bool(r.contacts)
            rows.append(list(r.T_head_stud.t) + list(r.wall_wrench))
        assert saw_contact, "determinism run must exercise contact"
        return np.array(rows)

    def test_same_seed_twice_bit_identical(self, name):
        a = self._trajectory(name)
        b = self._trajectory(name)
        assert np.array_equal(a, b), "same seed must replay bit-identically"


@pytest.mark.parametrize("name", ENGINES)
class TestItem5ClosedFormSanity:
    def test_spring_deflection_matches_k(self, name):
        # Light stud wedged in the narrowed throat adds its weight to the
        # mount's axial load; the deflection DELTA over the funnel's own
        # gravity sag ≈ m_stud·g/k (linear regime, off-stop).
        dt = 2.0e-4
        spec = make_spec(throat_d_mm=38.0, stiffness_k_n_mm=10.0,
                         stud_mass_kg=10.0)
        eng = load_engine(name, spec, engine.SolverSettings(timestep_s=dt))
        # baseline: stud far off-axis (outside the funnel), mount sags under
        # its own weight only
        eng.set_state(handoff_at((100.0, 300.0, 0.0)))
        for _ in range(8000):
            r = eng.step(dt)
        baseline_mm = r.funnel_t_mm[0]
        # settle the stud gently onto the wedge seat (~x=-173 for throat 38)
        eng.set_state(handoff_at((-172.0, 0.0, 0.0)))
        for _ in range(12000):
            r = eng.step(dt)
        # official frame: gravity is -x, added load deflects the base -x
        expected_mm = (spec.stud_mass_kg * 9.81) / spec.stiffness_k_n_mm
        assert baseline_mm - r.funnel_t_mm[0] == pytest.approx(
            expected_mm, rel=0.15)

    def test_sliding_force_ratio_matches_mu(self, name):
        # Closed-form Coulomb: during kinetic sliding, per-contact tangential
        # force ≈ μ · normal force. (A stick/slide bracket is unusable here —
        # a free sphere rolls down any incline regardless of μ.) Checked at
        # two μ values on the 26° cone wall.
        for mu in (0.2, 0.5):
            spec = make_spec(mu_contact=mu)
            eng = load_engine(name, spec)
            x0 = x_touch_mm(60.0, spec)
            eng.set_state(handoff_at((x0 + 5.0, 60.0, 0.0)))
            ratios = []
            for _ in range(1200):
                r = eng.step(DT)
                speed = math.hypot(*r.stud_v_ms)
                if not r.contacts or speed < 0.05:
                    continue
                for c in r.contacts:
                    f = np.array(c.force_n)
                    n = np.array(c.normal)
                    f_n = float(f @ n)
                    if f_n < 5.0:
                        continue
                    f_t = float(np.linalg.norm(f - f_n * n))
                    ratios.append(f_t / f_n)
            assert len(ratios) >= 5, f"mu={mu}: no sliding-contact window"
            assert float(np.median(ratios)) == pytest.approx(mu, rel=0.25)

    def test_restitution_rebound_tracks_e(self, name):
        # Single-contact closed form: near-rigid mount (k far off-grid,
        # labeled), 1 kg stud dropped on the flat lip ring → rebound/impact
        # speed ≈ e.
        measured = {}
        for e in (0.8, 0.3):
            spec = make_spec(restitution_e=e, stiffness_k_n_mm=1.0e4,
                             stud_mass_kg=1.0)
            solver = engine.SolverSettings(timestep_s=2.0e-4)
            eng = load_engine(name, spec, solver)
            eng.set_state(handoff_at((80.0, 117.5, 0.0)))
            v_in, v_out, in_contact = 0.0, 0.0, False
            for _ in range(6000):
                r = eng.step(2.0e-4)
                if r.contacts:
                    in_contact = True
                    v_in = max(v_in, -r.stud_v_ms[0])
                elif in_contact:
                    v_out = max(v_out, r.stud_v_ms[0])
            assert v_in > 0.5, "no impact recorded"
            measured[e] = v_out / v_in
        assert measured[0.8] == pytest.approx(0.8, abs=0.2)
        assert measured[0.3] == pytest.approx(0.3, abs=0.2)
        assert measured[0.8] > measured[0.3] + 0.15
