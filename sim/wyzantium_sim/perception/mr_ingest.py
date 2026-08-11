"""MR-CSV ingestion: bench data → the mr_v1 CurveSet + fit report.

Parses the three MEASUREMENT_REQUESTS.md output schemas (incl. the
2026-08-02 `reproj_rms_px` addition) and applies PRE-REGISTERED fit rules —
committed here, tested on synthetic CSVs, before any real data exists, so
the swap session has zero remaining modeling freedom:

  angle    — #39's swept cos^n exponent from MR-001 clean rows (occlusion
             0), per-(scale, range) ratios against the view_angle 0
             baseline, n_frames-weighted least squares in log space.
  mud      — D-023 form fitted for f_c (grid 0.3–1.2, 0.001 step) on
             per-geometry ratios M(f) = p(f)/p(0); the weighted-RMS form
             residual and the measured curve are reported so the human can
             judge whether the committed form survives measurement.
  lux      — MR-002 is non-transferable (instrument-specific absolutes):
             each (scale, angle) series is normalized at its brightest
             point, the knee is searched over the measured lux values only,
             the floor is closed-form least squares given the knee.
  sigma_px — n_detected-weighted median of reproj_rms_px across all three
             CSVs (#40's swept class value's measured replacement).
  flip     — H08 §4 two-parameter fit (bench discriminability constant C,
             kappa) on coplanar rows with informative rates (0.02–0.45;
             the 0.5 clamp and the zero tail carry no slope information),
             k = 3 and sigma from the reproj fit; pooled collar rate
             reported for the D-011 selection evidence.

Seam shape, stated plainly: angle/lux fits land in the CurveSet; the IS
§3.2 decode floor, the onset ramp width, and the #39 fp anchor are carried
from prior_v1 (the bench cannot re-measure them). mud_f_c, sigma_px, and
flip_kappa are SWEEP AXES, not CurveSet fields — their fitted values ride
in the report, and collapsing those sweeps is a recorded revision, never a
side effect of registration. `build_mr_curveset` never registers; the swap
session calls `curves.register` explicitly (ROADMAP curve-swap protocol).

When data cannot honestly anchor a fit, this module raises MRDataError and
stops — it never invents, estimates, or interpolates (NO_HARDWARE rev 2).
"""
import csv
import io
import math
from dataclasses import dataclass, field

from wyzantium_sim.perception.curves import PRIOR_V1, CurveSet


class MRDataError(ValueError):
    pass


@dataclass(frozen=True)
class MRFitReport:
    angle_exponent_hat: float
    mud_f_c_hat: float
    mud_form_residual_rms: float
    mud_curve: tuple          # ((occlusion_frac, measured M), ...) sorted
    lux_knee_hat: float
    lux_floor_hat: float
    sigma_px_hat: float
    flip_kappa_hat: float
    flip_c_hat: float         # bench f*S^2/d^2 [px] — rig, not spec, value
    collar_flip_rate: float
    warnings: tuple = field(default=())


_MR001_FLOATS = ("tag_scale_mm", "range_m", "view_angle_deg",
                 "occlusion_frac_est", "illuminance_lux", "reproj_rms_px")
_MR002_FLOATS = ("tag_scale_mm", "view_angle_deg", "illuminance_lux",
                 "exposure_ms", "reproj_rms_px")
_MR003_FLOATS = ("view_angle_deg", "reproj_rms_px")

_MR001_COLS = _MR001_FLOATS + ("n_frames", "n_detected",
                               "detector_version", "notes")
_MR002_COLS = _MR002_FLOATS + ("gain_setting", "n_frames", "n_detected",
                               "detector_version", "notes")
_MR003_COLS = _MR003_FLOATS + ("layout", "collar_standoff_mm",
                               "cam_position", "n_frames", "n_detected",
                               "n_flipped", "detector_version", "notes")


def _rows(path, required):
    text = path.read_text()
    body = "\n".join(ln for ln in text.splitlines()
                     if not ln.startswith("#"))
    reader = csv.DictReader(io.StringIO(body))
    missing = [c for c in required if c not in (reader.fieldnames or ())]
    if missing:
        raise MRDataError(
            f"{path.name}: missing required column(s) {', '.join(missing)}"
        )
    return list(reader)


def _convert(path, i, raw, floats, ints):
    row = dict(raw)
    try:
        for c in floats:
            row[c] = float(raw[c])
        for c in ints:
            row[c] = int(raw[c])
    except (TypeError, ValueError) as e:
        raise MRDataError(f"{path.name} row {i}: {e}") from None
    if row["n_frames"] <= 0:
        raise MRDataError(f"{path.name} row {i}: n_frames must be positive")
    if not 0 <= row["n_detected"] <= row["n_frames"]:
        raise MRDataError(
            f"{path.name} row {i}: n_detected {row['n_detected']} outside "
            f"[0, n_frames={row['n_frames']}]"
        )
    return row


def read_mr001(path):
    out = []
    for i, raw in enumerate(_rows(path, _MR001_COLS), start=1):
        row = _convert(path, i, raw, _MR001_FLOATS,
                       ("n_frames", "n_detected"))
        if not 0.0 <= row["occlusion_frac_est"] <= 1.0:
            raise MRDataError(
                f"{path.name} row {i}: occlusion_frac_est outside [0, 1]"
            )
        out.append(row)
    return out


def read_mr002(path):
    return [
        _convert(path, i, raw, _MR002_FLOATS, ("n_frames", "n_detected"))
        for i, raw in enumerate(_rows(path, _MR002_COLS), start=1)
    ]


def read_mr003(path):
    out = []
    for i, raw in enumerate(_rows(path, _MR003_COLS), start=1):
        row = _convert(path, i, raw, _MR003_FLOATS,
                       ("n_frames", "n_detected", "n_flipped"))
        if row["layout"] not in ("coplanar", "collar"):
            raise MRDataError(
                f"{path.name} row {i}: layout must be coplanar|collar, "
                f"got {row['layout']!r}"
            )
        if row["cam_position"] not in ("axial", "oblique"):
            raise MRDataError(
                f"{path.name} row {i}: cam_position must be axial|oblique"
            )
        if not 0 <= row["n_flipped"] <= row["n_detected"]:
            raise MRDataError(
                f"{path.name} row {i}: n_flipped {row['n_flipped']} outside "
                f"[0, n_detected={row['n_detected']}]"
            )
        standoff = (raw["collar_standoff_mm"] or "").strip()
        row["collar_standoff_mm"] = float(standoff) if standoff else None
        out.append(row)
    return out


def _rate(row):
    return row["n_detected"] / row["n_frames"]


def _clean_series(mr001):
    """MR-001 occlusion==0 rows grouped by (scale, range); the ratio
    baseline for the angle fit."""
    series = {}
    for r in mr001:
        if r["occlusion_frac_est"] == 0.0:
            key = (r["tag_scale_mm"], r["range_m"])
            series.setdefault(key, []).append(r)
    if not series:
        raise MRDataError(
            "MR-001 has no occlusion_frac_est == 0 rows to baseline the "
            "ratio fits; the loader stops rather than interpolate"
        )
    return series


def _fit_angle_exponent(mr001):
    num = den = 0.0
    for rows in _clean_series(mr001).values():
        base = next((r for r in rows if r["view_angle_deg"] == 0.0), None)
        if base is None or _rate(base) <= 0.0:
            continue
        p0 = _rate(base)
        for r in rows:
            ang, p = r["view_angle_deg"], _rate(r)
            if ang <= 0.0 or p <= 0.0:
                continue
            lc = math.log(math.cos(math.radians(ang)))
            num += r["n_frames"] * lc * math.log(p / p0)
            den += r["n_frames"] * lc * lc
    if den == 0.0:
        raise MRDataError("MR-001 has no off-axis clean rows for the "
                          "angle-exponent fit")
    return num / den


def _fit_mud(mr001):
    _clean_series(mr001)  # baseline-existence gate shared with the angle fit
    baselines = {}
    for r in mr001:
        if r["occlusion_frac_est"] == 0.0:
            key = (r["tag_scale_mm"], r["range_m"], r["view_angle_deg"])
            baselines[key] = _rate(r)
    points = []  # (f, measured M, weight)
    for r in mr001:
        key = (r["tag_scale_mm"], r["range_m"], r["view_angle_deg"])
        p0 = baselines.get(key, 0.0)
        if p0 <= 0.0:
            continue
        points.append((r["occlusion_frac_est"], _rate(r) / p0,
                       r["n_frames"]))
    if not points:
        raise MRDataError("MR-001 occlusion baselines are all zero")

    best_fc, best_sse = None, math.inf
    for step in range(300, 1201):
        fc = step / 1000.0
        sse = sum(w * (m - (1.0 - f) * max(0.0, 1.0 - f / fc)) ** 2
                  for f, m, w in points)
        if sse < best_sse:
            best_fc, best_sse = fc, sse
    total_w = sum(w for _, _, w in points)
    residual_rms = math.sqrt(best_sse / total_w)

    by_f = {}
    for f, m, w in points:
        s_m, s_w = by_f.get(f, (0.0, 0.0))
        by_f[f] = (s_m + w * m, s_w + w)
    curve = tuple(sorted((f, s_m / s_w) for f, (s_m, s_w) in by_f.items()))
    return best_fc, residual_rms, curve


def _fit_lux(mr002):
    series = {}
    for r in mr002:
        key = (r["tag_scale_mm"], r["view_angle_deg"])
        series.setdefault(key, []).append(r)
    points = []  # (lux, normalized rate, weight)
    for rows in series.values():
        base = max(rows, key=lambda r: r["illuminance_lux"])
        p0 = _rate(base)
        if p0 <= 0.0:
            continue
        points.extend((r["illuminance_lux"], _rate(r) / p0, r["n_frames"])
                      for r in rows)
    if not points:
        raise MRDataError("MR-002 has no usable series (all-dark data)")

    candidates = sorted({lux for lux, _, _ in points if lux > 1.0})
    if not candidates:
        raise MRDataError("MR-002 needs at least one lux value above 1")
    best = None
    for knee in candidates:
        log_knee = math.log10(knee)
        num = den = 0.0
        for lux, y, w in points:
            if lux < knee:
                frac = math.log10(max(lux, 1.0)) / log_knee
                num += w * (y - frac) * (1.0 - frac)
                den += w * (1.0 - frac) ** 2
        floor = min(1.0, max(0.0, num / den)) if den > 0.0 else 1.0
        sse = 0.0
        for lux, y, w in points:
            if lux >= knee:
                pred = 1.0
            else:
                frac = math.log10(max(lux, 1.0)) / log_knee
                pred = floor + (1.0 - floor) * frac
            sse += w * (y - pred) ** 2
        if best is None or sse < best[0]:
            best = (sse, knee, floor)
    return best[1], best[2]


def _weighted_median_sigma(all_rows):
    pairs = sorted((r["reproj_rms_px"], r["n_detected"])
                   for r in all_rows if r["n_detected"] > 0)
    if not pairs:
        raise MRDataError("no detected frames anywhere; reproj_rms_px "
                          "cannot replace sigma_px")
    total = sum(w for _, w in pairs)
    cum = 0.0
    for value, w in pairs:
        cum += w
        if cum >= total / 2.0:
            return value
    return pairs[-1][0]


def _fit_flip(mr003, sigma_px):
    k_sigma = 3.0 * sigma_px  # H08 §2 class threshold k = 3
    informative = []  # (angle_rad, flip rate, weight)
    for r in mr003:
        if r["layout"] != "coplanar" or r["n_detected"] == 0:
            continue
        rate = r["n_flipped"] / r["n_detected"]
        if r["view_angle_deg"] > 0.0 and 0.02 < rate < 0.45:
            informative.append((math.radians(r["view_angle_deg"]), rate,
                                r["n_detected"]))
    if not informative:
        raise MRDataError("MR-003 has no informative coplanar flip rows "
                          "(rates all clamped or zero)")

    best = None
    ratio = (200.0 / 0.5) ** (1.0 / 599)
    for step in range(600):
        c = 0.5 * ratio ** step
        num = den = 0.0
        ms = []
        for ang, y, w in informative:
            m = 0.5 * max(0.0, 1.0 - c * math.sin(ang) / k_sigma)
            ms.append(m)
            num += w * m * y
            den += w * m * m
        if den == 0.0:
            continue
        kappa = max(0.0, num / den)
        sse = sum(w * (y - min(0.5, kappa * m)) ** 2
                  for (_, y, w), m in zip(informative, ms))
        if best is None or sse < best[0]:
            best = (sse, c, kappa)
    _, c_hat, kappa_hat = best

    collar_flipped = sum(r["n_flipped"] for r in mr003
                         if r["layout"] == "collar")
    collar_detected = sum(r["n_detected"] for r in mr003
                          if r["layout"] == "collar")
    collar_rate = (collar_flipped / collar_detected if collar_detected
                   else 0.0)
    return kappa_hat, c_hat, collar_rate


def build_mr_curveset(mr001_path, mr002_path, mr003_path, name="mr_v1"):
    """Parse the three MR CSVs and produce (CurveSet, MRFitReport).

    Never registers the set; `curves.register` is the swap session's
    explicit act, recorded with before/after results per ROADMAP."""
    mr001 = read_mr001(mr001_path)
    mr002 = read_mr002(mr002_path)
    mr003 = read_mr003(mr003_path)

    exponent = _fit_angle_exponent(mr001)
    f_c_hat, mud_residual, mud_curve = _fit_mud(mr001)
    knee, floor = _fit_lux(mr002)
    sigma_hat = _weighted_median_sigma(mr001 + mr002 + mr003)
    kappa_hat, c_hat, collar_rate = _fit_flip(mr003, sigma_hat)

    curve_set = CurveSet(
        name=name,
        detection_onset_px=PRIOR_V1.detection_onset_px,
        detection_onset_width_px=PRIOR_V1.detection_onset_width_px,
        angle_falloff_exponent=exponent,
        lux_knee=knee,
        lux_floor_p=floor,
        fp_rate_per_image=PRIOR_V1.fp_rate_per_image,
    )
    report = MRFitReport(
        angle_exponent_hat=exponent,
        mud_f_c_hat=f_c_hat,
        mud_form_residual_rms=mud_residual,
        mud_curve=mud_curve,
        lux_knee_hat=knee,
        lux_floor_hat=floor,
        sigma_px_hat=sigma_hat,
        flip_kappa_hat=kappa_hat,
        flip_c_hat=c_hat,
        collar_flip_rate=collar_rate,
        warnings=(
            "decode floor, onset width, fp rate carried from prior_v1 "
            "(bench cannot re-measure them)",
            "mud_f_c / sigma_px / flip_kappa are sweep axes: fitted values "
            "ride in this report; collapsing the sweeps is a recorded "
            "revision, not a registration side effect",
        ),
    )
    return curve_set, report
