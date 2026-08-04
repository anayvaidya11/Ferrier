"""H08 interim flip model (until MR-003) — studies/H08_AMBIGUITY_MODEL.md.

§2: discriminability D ≈ f · S² · sin θ / d²  [px]; branches distinguishable
when D > k·σ_px with class values k = 3, σ_px = 0.5 px.
§4: coplanar layout injects a flip per frame with
p_flip = 0.5 · max(0, 1 − D/(k·σ_px)) · κ, κ swept {0.5, 1, 2}; only the
0.5 coin-flip ceiling and the zero floor are principled — the ramp is a
labeled assumption. Collar layout: no flip while ≥2 tags are visible and
the standoff is observable (§3); single-tag frames fall back to coplanar.
"""
K_THRESHOLD = 3.0  # H08 §2 class value


def discriminability(f_px, span_m, dist_m, tilt_rad):
    import math
    return f_px * span_m * span_m * math.sin(tilt_rad) / (dist_m * dist_m)


def p_flip(d_px, sigma_px, kappa, k=K_THRESHOLD):
    ramp = max(0.0, 1.0 - d_px / (k * sigma_px))
    return min(0.5, 0.5 * ramp * kappa)


def p_flip_for_layout(d_px, sigma_px, kappa, layout, n_tags_visible,
                      standoff_observable, k=K_THRESHOLD):
    if layout == "collar" and n_tags_visible >= 2 and standoff_observable:
        return 0.0
    return p_flip(d_px, sigma_px, kappa, k)


def reflect_about_boresight(q):
    """The wrong ambiguity branch: rotation reflected about the line of
    sight (+x boresight). Equivalent to conjugation by a 180° rotation
    about x: (w, x, y, z) → (w, x, −y, −z). First-order stand-in for the
    IPPE mirror solution."""
    w, x, y, z = q
    return (w, x, -y, -z)
