"""T12 — #63 feasibility windows and mask (D-028 semantics: intersection,
not verdict; emits data, interpretation is normative in ARCH §6.7 only).

Per class (μ_trac ∈ #64, m_rv ∈ #65): k_max = μ_trac·m_rv·g / 35 mm
(D-015 capture envelope), k_min = n_F/δ_work — n_F is a named Phase 2
unknown, class placeholder ≈ 1 N/mm (studies/H04 §4). The required band is
D-026's deliverable: the contiguous committed-k range whose marginal
success clears the threshold (default 0.60, the D-029 gate bar), at the
nominal M_eff. Pinned cross-check (studies/H04 Addendum A1): at
(0.2, 300 kg), k_max ≈ 17 N/mm → sweep cells k = 30, 70 masked infeasible.
"""

from __future__ import annotations

from wyzantium_sim.analysis.curves import sensitivity

G_MS2 = 9.81
DELTA_MAX_MM = 35.0                 # D-015 capture envelope, positional
K_MIN_PLACEHOLDER_N_MM = 1.0        # #63: n_F/δ_work stand-in, Phase 2 fills
MU_TRAC = (0.2, 0.35, 0.5)          # #64
M_RV_KG = (300.0, 500.0, 800.0)     # #65
K_CELLS_N_MM = (1.0, 3.0, 10.0, 30.0, 70.0)   # D-026 log grid


def window(mu_trac: float, m_rv_kg: float) -> tuple:
    """[k_min, k_max] for one vehicle class (N/mm)."""
    return (K_MIN_PLACEHOLDER_N_MM, mu_trac * m_rv_kg * G_MS2 / DELTA_MAX_MM)


def required_band(rows, nominal, *, threshold=0.60):
    """D-026: contiguous stiffness range whose marginal success ≥ threshold
    (None when no cell clears it). Emitted at the nominal M_eff — the
    Tier-1 marginal structure holds head_mass at nominal on the k axis."""
    curve = sensitivity(rows, nominal).get("stiffness_k_n_mm")
    if not curve:
        return None
    passing = [s.value for s in curve if s.success >= threshold]
    if not passing:
        return None
    return (min(passing), max(passing))


def feasibility(rows, nominal, *, threshold=0.60) -> dict:
    """The #63 emission: per-class window, mask over the committed k
    cells, required band, and their intersection. Data only."""
    band = required_band(rows, nominal, threshold=threshold)
    classes = []
    for mu in MU_TRAC:
        for m in M_RV_KG:
            k_min, k_max = window(mu, m)
            inter = None
            if band is not None:
                lo, hi = max(band[0], k_min), min(band[1], k_max)
                inter = (lo, hi) if lo <= hi else None
            classes.append({
                "mu_trac": mu, "m_rv_kg": m,
                "k_min_n_mm": k_min, "k_max_n_mm": k_max,
                "mask": {str(k): (k_min <= k <= k_max)
                         for k in K_CELLS_N_MM},
                "intersection_n_mm": inter,
            })
    return {
        "source": "#63; D-028 (intersection, not verdict); D-026 band; "
                  "D-015 35 mm; interpretation: ARCHITECTURE §6.7 only",
        "required_band_n_mm": band,
        "band_threshold": threshold,
        "classes": classes,
    }
