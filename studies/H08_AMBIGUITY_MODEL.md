# H-08 — Derived Flip Model and Camera-Geometry Bounds

**Status:** derivation of record for the pre-MR-003 injected flip model and the D-025
Cam B obliquity band. Label: **derived, first-order** — the scaling law is closed-form;
the noise constants are class values; **MR-003 validates or replaces every number
here.** Assumptions listed at the bottom.

## 1. The ambiguity, stated

A planar target under weak perspective admits two pose solutions whose normals are
reflections about the line of sight (Collins & Bartoli, IPPE — cited as the source of
the two-solution *structure*, which is analytic; this study derives nothing that paper
already gives). A detector "flip" is selecting the wrong branch. What is NOT derivable
is how often real corner noise causes the wrong branch to win — that is MR-003's
purchase (MEASUREMENT_REQUESTS.md).

## 2. First-order discriminability scaling [derived]

For a target of span S at distance d, viewed at tilt θ, focal length f (px): the depth
relief across the target is Δz = S·sin θ, and the differential perspective signal that
separates the two solutions scales as

**D ≈ f · S² · sin θ · / d²  [px]**

The branches are distinguishable when D > k·σ_px. Class values: σ_px = 0.5 px corner
noise, k = 3 → threshold 1.5 px.

**Numbers (D-016 geometry, D-012/D-025 cameras — f_A ≈ 1371 px, f_B ≈ 880 px):**

| Target | S | Camera, d | f·S²/d² | θ_min = asin(1.5·d²/(f·S²)) |
|---|---|---|---|---|
| Outer tag | 150 mm | A, 3 m | 3.4 px | **≈ 26°** — near-head-on flips are live at acquisition range |
| Outer tag | 150 mm | A, 1 m | 30.9 px | ≈ 2.8° |
| Single inner tag | 10 mm | B, 0.25 m | 1.4 px | **no solution — a lone inner tag cannot self-disambiguate at any angle** |
| Inner ring as constellation | 110 mm | B, 0.25 m | 170 px | ≈ 0.5° |
| Adjacent 2-tag baseline (worst partial occlusion) | ~42 mm | B, 0.25 m | 24.8 px | ≈ 3.5° |

**Consequences (propagated):** D-011 gains the single-tag orientation qualification;
WIRE_FORMAT's insertion-commit rule requires `multi_tag_fused` (≥2 tags); the outer
tag's 26°-at-3 m row is why the flip axis matters at acquisition, not just insertion.

## 3. The collar removes the ambiguity structurally [derived]

A non-coplanar constellation has no two-fold ambiguity (PnP on non-coplanar points is
generically unique) — *provided the depth separation is observable*. Noise-equivalent
depth at ring radius r: δz ≈ σ_px · d² / (f · r). Worst inner-servo case (d = 0.5 m,
Cam B): δz ≈ 0.5 · 0.25 / (880 · 0.055) ≈ **2.6 mm**. Requiring h_c ≥ 3·δz gives
**h_c ≥ ~8 mm** — the D-016 sweep band [10, 40] mm is observable throughout. This is
the derived case for the collar candidate; MR-003 measures whether the coplanar
layout's measured flip rate makes the collar necessary.

## 4. Interim injected flip model (until MR-003)

- Collar layout: no flip injected while ≥2 tags visible and h_c observable (§3);
  single-tag frames fall back to the coplanar rule.
- Coplanar layout: flip injected per frame with
  **p_flip = 0.5 · max(0, 1 − D/(k·σ_px)) · κ**, D from §2 using the *visible*
  constellation span. κ (scale) is a **swept parameter {0.5, 1.0, 2.0}** — the
  functional form is an assumption, labeled; only its ceiling (0.5 = coin flip) and
  floor (0 when discriminable) are principled.

## 5. Cam B obliquity band (feeds D-025) [derived, first-order]

- **Lower bound:** under partial occlusion the visible constellation can degrade to an
  adjacent tag pair (S ≈ 42 mm). Discriminability for that pair at 0.25 m needs
  θ ≥ ~3.5° (§2 table); margin ×4 for the unmodeled terms below → **β ≥ 15°**.
- **Upper bound:** far-side ring tags foreshorten by cos β and the full ring must stay
  in frame through insertion at Cam B's standoff (~270 mm); beyond ~45° the far tags'
  effective module pitch falls below the decode floor derived in INTERFACE_SPEC §3.3.
  → **β ≤ 45°**.
- **Selected: β = 30°** (D-025) — center of the band; the translation offsets remain
  [ASSUMED] within it.

## 6. Commit-rule geometry check (added 2026-08-02) [derived]

**Question raised:** insertion commit requires ≥2 fused tags; if Cam B's field of view
at contact were ~100 mm across, two ring tags (ring Ø110 mm) could never be
simultaneously in frame where the rule is evaluated.

**Check against committed geometry** (Cam B extrinsic (+100, −250, 0) mm, yaw 30°,
HFOV ~95°, D-025/IS §4; plate standoff from mouth d_p ∈ [200, 70] mm through inner
servo, IS §6):

- **Range never collapses.** Cam B–to–plate-center range = √((100+d_p)² + 250²):
  390 mm at commit entry (d_p = 200) → 302 mm at full engagement (d_p = 70). FOV width
  at 302 mm = 2·302·tan 47.5° ≈ **660 mm** — six ring diameters. The ~100 mm-across
  premise does not occur with the committed standoff mounting; keeping viewing
  distance through insertion is exactly what the off-axis position buys (D-012).
- **The binding constraint is lip occlusion, not FOV.** Tracing the sight line from
  Cam B to plate center: it passes the mouth plane at radius ≈119 mm against a lip
  outer radius of 125 mm — a graze — once d_p ≲ 100 mm. Far-side ring tags (the +Y
  arc) are progressively occluded by the funnel shell in the last ~100 mm; **near-side
  tags keep clear sight lines to contact.**
- **Worst surviving constellation = an adjacent near-side pair** (baseline ~42 mm) —
  precisely the case §2's table already covers (θ_min ≈ 3.5°, and Cam B sits at 30°),
  and the case D-025's lower bound was set by. With 8 tags at 45° pitch, any 90° arc
  contains ≥2 tags, so a near-side adjacent pair always exists — this is now a stated
  requirement on ring population: **azimuthal coverage must guarantee ≥2 tags in the
  Cam-B-side semicircle** (8 × 45° satisfies it; any descoping below 5 tags would not).
- **The rule's vision demand ends at contact:** stage 3 is contact-force-guided
  (D-004; `pose_source: contact_force`), so no vision requirement extends into the
  final occluded centimeters.

**Verdict: the ≥2-tag commit rule survives its own geometry.** The check is cheap now
and is committed here so Phase 1 builds against verified geometry, not an assumption.

## Assumptions (all validated or replaced by MR-003)

1. Weak-perspective two-solution model; real detectors flip via the same mechanism.
2. σ_px = 0.5 px corner noise and k = 3 — class values, not measurements.
3. Foreshortening treated first-order; no lens distortion; no motion blur term.
4. The κ-scaled linear ramp in §4 is a shape assumption — MR-003's measured curve
   replaces it.
