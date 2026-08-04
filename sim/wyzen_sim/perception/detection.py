"""#39 detection-probability model (prior_v1 structure).

Composite of multiplicative factors, each tied to its committed source:
  size   — plateau ~1.0 above the IS §3.2 20 px decode floor (#39 anchor
           D1/D4: onset-of-failure, not gradual global degradation); linear
           ramp of arbitrary labeled width below the floor.
  angle  — cos^n falloff (#39: view-angle shape deliberately unanchored by
           the corpus; n lives in the curve set, arbitrary-labeled, MR-003
           replaces).
  mud    — D-023 (mud.py).
  lux    — 1.0 at/above the curve set's knee (LIT trend); below it, linear
           in log10 down to lux_floor_p at 1 lux (EXT — MR-002 region).
"""
import math

from wyzen_sim.perception import mud as mud_model


def _size_factor(px_size, curve):
    onset = curve.detection_onset_px
    width = curve.detection_onset_width_px
    if px_size >= onset:
        return 1.0
    if px_size <= onset - width:
        return 0.0
    return (px_size - (onset - width)) / width


def _angle_factor(view_angle_rad, curve):
    c = math.cos(view_angle_rad)
    if c <= 0.0:
        return 0.0
    return c ** curve.angle_falloff_exponent


def _lux_factor(illuminance_lux, curve):
    if illuminance_lux >= curve.lux_knee:
        return 1.0
    span = math.log10(curve.lux_knee)  # knee → 1 lux
    frac = math.log10(max(illuminance_lux, 1.0)) / span
    return curve.lux_floor_p + (1.0 - curve.lux_floor_p) * frac


def p_detect(px_size, view_angle_rad, mud_fraction, f_c, illuminance_lux,
             curve):
    return (_size_factor(px_size, curve)
            * _angle_factor(view_angle_rad, curve)
            * mud_model.detection_factor(mud_fraction, f_c)
            * _lux_factor(illuminance_lux, curve))
