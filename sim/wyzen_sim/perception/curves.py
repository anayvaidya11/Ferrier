"""The curve-swap seam (D-008-R; ROADMAP curve-swap protocol).

A CurveSet bundles every perception-model constant that MR bench data can
later replace. `prior_v1` is the committed pre-MR set; when MR-001/002/003
CSVs land, a new set (e.g. `mr_v1`) is REGISTERED — never edited in place —
and the active set's name rides in trial_header.sweep_point so analysis can
refuse to pool across sets and both before/after results get reported.

Committed values: detection_onset_px = 20 (the IS §3.2 robust-decode floor);
fp_rate_per_image = 1.4e-5 (#39, well-anchored). Arbitrary-labeled values:
onset ramp width, view-angle falloff exponent (#39's swept shape), the
sub-10-lux floor (EXT — MR-002 region).
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class CurveSet:
    name: str
    detection_onset_px: float        # committed: IS §3.2 decode floor
    detection_onset_width_px: float  # arbitrary ramp width below the floor
    angle_falloff_exponent: float    # #39 swept view-angle shape (arbitrary)
    lux_knee: float                  # IS §9: LIT trend above, MR-002 below
    lux_floor_p: float               # arbitrary multiplier at 1 lux (EXT)
    fp_rate_per_image: float         # committed anchor, #39


PRIOR_V1 = CurveSet(
    name="prior_v1",
    detection_onset_px=20.0,
    detection_onset_width_px=10.0,
    angle_falloff_exponent=1.0,
    lux_knee=10.0,
    lux_floor_p=0.2,
    fp_rate_per_image=1.4e-5,
)

_REGISTRY = {PRIOR_V1.name: PRIOR_V1}


def get(name):
    return _REGISTRY[name]


def register(curve_set):
    if curve_set.name in _REGISTRY:
        raise ValueError(f"curve set {curve_set.name!r} already registered "
                         "(sets are never edited in place)")
    _REGISTRY[curve_set.name] = curve_set


def unregister(name):
    if name == PRIOR_V1.name:
        raise ValueError("prior_v1 is the committed baseline")
    _REGISTRY.pop(name, None)
