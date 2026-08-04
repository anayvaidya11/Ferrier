"""Contact-stage runner: D-020 latch + IS8-17 jam evaluated per step (T7).

Drives a loaded ContactEngine from a HandoffState until latch, jam, or
timeout, evaluating per step:

- D-020 latch (#54, committed): latched ⟺ stud-head center within 3 mm
  radial of the throat axis at engagement depth, closing speed ≤ 0.1 m/s,
  condition held 100 ms. The throat axis follows the compliant base's
  lateral translation (funnel_t_mm); base rotation is neglected for the
  radial test (small-angle, labeled below).
- IS8-17 jam (#62, committed criterion, swept thresholds): axial contact
  force > F_ax_jam ∧ |lateral| < F_lat_jam, continuously, with no latch
  confirm within t_jam → jam, abort_reason "jam_detected" (the observable
  behind D-027's T5-promotion trigger).
- IS8-16 lip strike (#12): any contact point with radial position in the
  lip band [110, 125] mm while the head center is still before the capture
  plane (x > 0) → lip_strike flagged with the observed radii; scored as its
  own outcome class by the T9 classifier, never folded into capture or miss.

Arbitrary code-level choices (spec gaps recorded 2026-08-04, chassis_error
precedent):
- ENGAGEMENT_DEPTH_X_MM: D-020's "engagement depth" has no committed number
  (the IS §6 latch-pocket arithmetic never names it); chosen as the pocket
  seat — the pocket-floor face at x = -220 plus the head radius 20.
- ENGAGE_BAND_MM: tolerance on "at engagement depth".
- Jam timer accumulates while the force signature holds continuously and
  resets when it breaks.
- The caller supplies the insertion driver (gravity or initial velocity);
  no actuator model exists pre-T8.
- Base rotation is neglected for the radial and lip-band tests (small
  angle): StepResult exposes only funnel_t_mm — the base's rotation is
  not available at the ContactEngine boundary.

The optional on_step callback receives every StepResult — the T8 logging
seam (sim_truth every physics step post-handoff, #59).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from wyzantium_sim import params

ENGAGEMENT_DEPTH_X_MM = -200.0  # arbitrary: pocket-floor face -220 + head r 20
ENGAGE_BAND_MM = 5.0            # arbitrary


@dataclass(frozen=True)
class JamThresholds:
    """One #62 sweep cell (F_ax_jam N, F_lat_jam N, t_jam s)."""
    f_ax_n: float
    f_lat_n: float
    t_s: float


@dataclass(frozen=True)
class ContactOutcome:
    latched: bool
    latch_time_s: float | None
    jam: bool
    jam_time_s: float | None
    lip_strike: bool
    lip_radii_mm: tuple
    timed_out: bool
    abort_reason: str | None
    t_end_s: float


def _head_center(result):
    return result.T_head_stud.apply((70.0, 0.0, 0.0))


def run_contact(eng, handoff, jam: JamThresholds, max_time_s: float,
                dt: float = 0.001, on_step=None) -> ContactOutcome:
    latch = params.PARAMS[54].value  # {"radial_mm", "speed_max_ms", "hold_ms"}
    lip_lo, lip_hi = params.PARAMS[12].value["lo"], params.PARAMS[12].value["hi"]

    eng.set_state(handoff)
    t0 = handoff.t_sim_s
    hold_s = 0.0
    jam_timer_s = 0.0
    lip_radii = []
    r = eng.state()
    n_steps = int(max_time_s / dt)

    for _ in range(n_steps):
        r = eng.step(dt)
        if on_step is not None:
            on_step(r)

        c = _head_center(r)
        base = r.funnel_t_mm

        # IS8-16: lip-band contact before capture-plane crossing. The lip
        # band is defined about the funnel axis (IS §6), which follows the
        # compliant base like the D-020 throat axis below — so both rho and
        # the capture plane are measured against the displaced base.
        if c[0] - base[0] > 0.0:
            for cp in r.contacts:
                rho = math.hypot(cp.pos_head_mm[1] - base[1],
                                 cp.pos_head_mm[2] - base[2])
                if lip_lo <= rho <= lip_hi:
                    lip_radii.append(rho)

        # D-020 latch predicate, evaluated against the displaced throat axis
        radial = math.hypot(c[1] - base[1], c[2] - base[2])
        at_depth = (c[0] - base[0]) <= ENGAGEMENT_DEPTH_X_MM + ENGAGE_BAND_MM
        slow = math.hypot(*r.stud_v_ms) <= latch["speed_max_ms"]
        if radial <= latch["radial_mm"] and at_depth and slow:
            hold_s += dt
            if hold_s * 1000.0 >= latch["hold_ms"]:
                return ContactOutcome(
                    latched=True, latch_time_s=r.t_sim_s - t0,
                    jam=False, jam_time_s=None,
                    lip_strike=bool(lip_radii),
                    lip_radii_mm=tuple(lip_radii), timed_out=False,
                    abort_reason=None, t_end_s=r.t_sim_s)
        else:
            hold_s = 0.0

        # IS8-17 jam signature (only meaningful before latch)
        f_ax = abs(r.wall_wrench[0])
        f_lat = math.hypot(r.wall_wrench[1], r.wall_wrench[2])
        if f_ax > jam.f_ax_n and f_lat < jam.f_lat_n:
            jam_timer_s += dt
            if jam_timer_s >= jam.t_s:
                return ContactOutcome(
                    latched=False, latch_time_s=None,
                    jam=True, jam_time_s=r.t_sim_s - t0,
                    lip_strike=bool(lip_radii),
                    lip_radii_mm=tuple(lip_radii), timed_out=False,
                    abort_reason="jam_detected", t_end_s=r.t_sim_s)
        else:
            jam_timer_s = 0.0

    return ContactOutcome(
        latched=False, latch_time_s=None, jam=False, jam_time_s=None,
        lip_strike=bool(lip_radii), lip_radii_mm=tuple(lip_radii),
        timed_out=True, abort_reason=None, t_end_s=r.t_sim_s)
