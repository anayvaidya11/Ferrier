"""#40: swept corner-noise class value σ_px propagated to a pose covariance
through the committed camera models (#19/#20).

First-order propagation, the same pattern as H08 §3's noise-equivalent
depth δz ≈ σ_px·d²/(f·r):
  lateral   σ = σ_px · d / f            [m]
  depth     σ = σ_px · d² / (f · S)     [m]  (S = visible constellation span)
  rotation  σ = σ_px · d / (f · S)      [rad]
head_frame +x is the boresight/depth axis (IS §4), so var(x) carries the
depth term and y/z the lateral term. Diagonal 6×6 → 21-element upper
triangle (WIRE_FORMAT order [x y z rx ry rz]); PSD by construction.
Magnitude honesty: σ_px is a swept class value until MR reproj_rms_px lands
(perception_prior Paper 5 anchors the functional form only).
"""


def pose_cov_upper21(sigma_px, f_px, dist_m, span_m):
    lat = sigma_px * dist_m / f_px
    depth = sigma_px * dist_m * dist_m / (f_px * span_m)
    rot = sigma_px * dist_m / (f_px * span_m)
    variances = [depth * depth, lat * lat, lat * lat,
                 rot * rot, rot * rot, rot * rot]
    cov = []
    for i in range(6):
        for j in range(i, 6):
            cov.append(variances[i] if i == j else 0.0)
    return cov
