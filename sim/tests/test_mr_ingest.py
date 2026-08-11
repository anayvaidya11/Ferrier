"""MR-CSV ingestion — the curve-swap seam tested on synthetic MR-format CSVs
(PHASE1_PLAN §5 week-3 gate; ROADMAP curve-swap protocol; D-008-R).

The fit procedures are PRE-REGISTERED here, before any real measurement
exists: synthetic CSVs in the exact MEASUREMENT_REQUESTS.md schemas are
generated from known ground-truth parameters, and the ingestion must recover
them. When MR-001/002/003 land under research/data/, the same code runs with
zero remaining modeling freedom.

Sources: MEASUREMENT_REQUESTS.md output formats (incl. the 2026-08-02
reproj_rms_px schema addition), D-023 (mud form), studies/H08 §2/§4 (flip
model, k = 3), #39/#40/#41, IS §3.2 (20 px decode floor is committed — the
bench cannot re-measure it, so mr_v1 carries it).
"""
import csv
import io
import math

import pytest

from wyzantium_sim.perception import curves, mr_ingest

# Ground truth the synthetic bench data is generated from.
N_TRUE = 2.0        # angle falloff exponent (#39 swept shape; MR-001 anchors)
F_C_TRUE = 0.7      # D-023 mud cutoff (#41 swept; MR-001 anchors)
KNEE_TRUE = 10.0    # lux knee (MR-002 anchors, relative trend only)
FLOOR_TRUE = 0.25   # lux floor multiplier at 1 lux (MR-002 anchors)
SIGMA_TRUE = 0.42   # px — reproj_rms_px replaces swept sigma_px (#40).
# Per-CSV reproj values are arranged so the n_detected-weighted median is
# 0.42 (MR-003 carries the majority of detections) while the unweighted
# row median is 0.38 — the test fails if the weighting is dropped.
KAPPA_TRUE = 1.3    # H08 §4 flip ramp scale (MR-003 anchors)
C_TRUE = 7.26       # bench discriminability constant f*S^2/d^2 [px]

N_FRAMES = 400
P0 = 0.96  # bench plateau detectability; cancels in every ratio-based fit

MR001_COLS = ["tag_scale_mm", "range_m", "view_angle_deg",
              "occlusion_frac_est", "illuminance_lux", "n_frames",
              "n_detected", "detector_version", "notes", "reproj_rms_px"]
MR002_COLS = ["tag_scale_mm", "view_angle_deg", "illuminance_lux",
              "exposure_ms", "gain_setting", "n_frames", "n_detected",
              "detector_version", "notes", "reproj_rms_px"]
MR003_COLS = ["layout", "collar_standoff_mm", "cam_position",
              "view_angle_deg", "n_frames", "n_detected", "n_flipped",
              "detector_version", "notes", "reproj_rms_px"]


def _mud_true(f):
    return (1.0 - f) * max(0.0, 1.0 - f / F_C_TRUE)


def _lux_true(lux):
    if lux >= KNEE_TRUE:
        return 1.0
    frac = math.log10(max(lux, 1.0)) / math.log10(KNEE_TRUE)
    return FLOOR_TRUE + (1.0 - FLOOR_TRUE) * frac


def _flip_true(angle_deg):
    d_px = C_TRUE * math.sin(math.radians(angle_deg))
    ramp = max(0.0, 1.0 - d_px / (3.0 * SIGMA_TRUE))
    return min(0.5, 0.5 * ramp * KAPPA_TRUE)


def _csv_text(cols, rows, comment=None):
    buf = io.StringIO()
    if comment:
        buf.write(f"# {comment}\n")
    w = csv.DictWriter(buf, fieldnames=cols)
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def _mr001_rows():
    geoms = ([(150, r, a) for r in (3.0, 1.0) for a in (0, 20, 40, 60)]
             + [(10, r, a) for r in (0.30, 0.15) for a in (0, 20, 40)])
    rows = []
    for scale, rng, ang in geoms:
        for f in [round(0.1 * i, 1) for i in range(8)]:
            p = (P0 * math.cos(math.radians(ang)) ** N_TRUE * _mud_true(f))
            rows.append({
                "tag_scale_mm": scale, "range_m": rng,
                "view_angle_deg": ang, "occlusion_frac_est": f,
                "illuminance_lux": 800, "n_frames": N_FRAMES,
                "n_detected": round(N_FRAMES * p),
                "detector_version": "apriltag3-ref", "notes": "",
                "reproj_rms_px": 0.38,
            })
    return rows


def _mr002_rows():
    rows = []
    for scale, ang in [(150, 0), (150, 40), (10, 0), (10, 40)]:
        base = P0 * math.cos(math.radians(ang)) ** N_TRUE
        for lux in (50, 10, 5, 2, 1):
            rows.append({
                "tag_scale_mm": scale, "view_angle_deg": ang,
                "illuminance_lux": lux, "exposure_ms": 8,
                "gain_setting": "g8", "n_frames": N_FRAMES,
                "n_detected": round(N_FRAMES * base * _lux_true(lux)),
                "detector_version": "apriltag3-ref", "notes": "",
                "reproj_rms_px": 0.35,
            })
    return rows


def _mr003_rows():
    angles = [0, 2, 4, 6, 8, 10, 15, 30, 45, 60, 75]
    variants = [("coplanar", ""), ("collar", 18.0), ("collar", 31.0)]
    rows = []
    for layout, standoff in variants:
        for cam in ("axial", "oblique"):
            for ang in angles:
                n_det = round(N_FRAMES * 0.95)
                p_fl = _flip_true(ang) if layout == "coplanar" else 0.0
                rows.append({
                    "layout": layout, "collar_standoff_mm": standoff,
                    "cam_position": cam, "view_angle_deg": ang,
                    "n_frames": N_FRAMES, "n_detected": n_det,
                    "n_flipped": round(n_det * p_fl),
                    "detector_version": "apriltag3-ref", "notes": "",
                    "reproj_rms_px": 0.42,
                })
    return rows


@pytest.fixture
def mr_paths(tmp_path):
    p1 = tmp_path / "mr001_mud_detection.csv"
    p1.write_text(_csv_text(MR001_COLS, _mr001_rows(),
                            comment="occlusion estimated from stills"))
    p2 = tmp_path / "mr002_lowlux_detection.csv"
    p2.write_text(_csv_text(MR002_COLS, _mr002_rows()))
    p3 = tmp_path / "mr003_flip_rate.csv"
    p3.write_text(_csv_text(MR003_COLS, _mr003_rows()))
    return p1, p2, p3


# --- parsers: exact MEASUREMENT_REQUESTS.md schemas ---

def test_read_mr001_parses_rows_and_skips_header_comment(mr_paths):
    rows = mr_ingest.read_mr001(mr_paths[0])
    assert len(rows) == 14 * 8
    r0 = rows[0]
    assert r0["tag_scale_mm"] == 150.0
    assert r0["n_detected"] <= r0["n_frames"]
    assert r0["reproj_rms_px"] == pytest.approx(0.38)


def test_missing_required_column_rejected(tmp_path):
    cols = [c for c in MR001_COLS if c != "range_m"]
    rows = [{k: v for k, v in r.items() if k != "range_m"}
            for r in _mr001_rows()[:3]]
    p = tmp_path / "bad.csv"
    p.write_text(_csv_text(cols, rows))
    with pytest.raises(mr_ingest.MRDataError, match="range_m"):
        mr_ingest.read_mr001(p)


def test_missing_reproj_rms_px_rejected(tmp_path):
    # The 2026-08-02 schema addition is mandatory: this column is what
    # replaces the swept sigma_px (#40).
    cols = [c for c in MR002_COLS if c != "reproj_rms_px"]
    rows = [{k: v for k, v in r.items() if k != "reproj_rms_px"}
            for r in _mr002_rows()[:3]]
    p = tmp_path / "bad.csv"
    p.write_text(_csv_text(cols, rows))
    with pytest.raises(mr_ingest.MRDataError, match="reproj_rms_px"):
        mr_ingest.read_mr002(p)


def test_count_inconsistencies_rejected(tmp_path):
    rows = _mr001_rows()[:2]
    rows[1]["n_detected"] = rows[1]["n_frames"] + 5
    p = tmp_path / "bad.csv"
    p.write_text(_csv_text(MR001_COLS, rows))
    with pytest.raises(mr_ingest.MRDataError, match="n_detected"):
        mr_ingest.read_mr001(p)

    rows3 = _mr003_rows()[:2]
    rows3[0]["n_flipped"] = rows3[0]["n_detected"] + 1
    p3 = tmp_path / "bad3.csv"
    p3.write_text(_csv_text(MR003_COLS, rows3))
    with pytest.raises(mr_ingest.MRDataError, match="n_flipped"):
        mr_ingest.read_mr003(p3)


def test_unknown_layout_rejected(tmp_path):
    rows = _mr003_rows()[:1]
    rows[0]["layout"] = "hexagonal"
    p = tmp_path / "bad.csv"
    p.write_text(_csv_text(MR003_COLS, rows))
    with pytest.raises(mr_ingest.MRDataError, match="layout"):
        mr_ingest.read_mr003(p)


def test_coplanar_standoff_parses_as_none(mr_paths):
    rows = mr_ingest.read_mr003(mr_paths[2])
    coplanar = [r for r in rows if r["layout"] == "coplanar"]
    collar = [r for r in rows if r["layout"] == "collar"]
    assert all(r["collar_standoff_mm"] is None for r in coplanar)
    assert {r["collar_standoff_mm"] for r in collar} == {18.0, 31.0}


# --- the pre-registered fits recover the generating parameters ---

def test_fit_recovers_angle_falloff_exponent(mr_paths):
    _, report = mr_ingest.build_mr_curveset(*mr_paths)
    assert report.angle_exponent_hat == pytest.approx(N_TRUE, abs=0.05)


def test_fit_recovers_mud_cutoff_and_reports_form_residual(mr_paths):
    _, report = mr_ingest.build_mr_curveset(*mr_paths)
    assert report.mud_f_c_hat == pytest.approx(F_C_TRUE, abs=0.02)
    # Data generated from the D-023 form itself -> near-zero residual.
    # On real data this number is what tells the human whether the
    # committed form survives measurement.
    assert report.mud_form_residual_rms < 0.01
    # The measured curve is reported alongside the fit so the swap session
    # can judge form adequacy without re-deriving it.
    fs = [f for f, _ in report.mud_curve]
    assert fs == sorted(fs) and 0.0 in fs
    m_at_03 = dict(report.mud_curve)[0.3]
    assert m_at_03 == pytest.approx(_mud_true(0.3), abs=0.02)


def test_fit_recovers_lux_knee_and_floor_from_relative_trend(mr_paths):
    # MR-002 carries the non-transferable label: only the relative trend is
    # used, so every series is normalized at its brightest point before the
    # fit and the knee is searched over the measured lux values only.
    _, report = mr_ingest.build_mr_curveset(*mr_paths)
    assert report.lux_knee_hat == KNEE_TRUE
    assert report.lux_floor_hat == pytest.approx(FLOOR_TRUE, abs=0.02)


def test_sigma_px_is_detection_weighted_median_of_reproj_rms(mr_paths):
    _, report = mr_ingest.build_mr_curveset(*mr_paths)
    assert report.sigma_px_hat == pytest.approx(SIGMA_TRUE)


def test_fit_recovers_flip_kappa_and_bench_constant(mr_paths):
    _, report = mr_ingest.build_mr_curveset(*mr_paths)
    assert report.flip_kappa_hat == pytest.approx(KAPPA_TRUE, abs=0.1)
    assert report.flip_c_hat == pytest.approx(C_TRUE, rel=0.10)


def test_collar_suppression_is_reported_for_d011(mr_paths):
    _, report = mr_ingest.build_mr_curveset(*mr_paths)
    assert report.collar_flip_rate == pytest.approx(0.0)


def test_insufficient_clean_rows_raise_rather_than_interpolate(tmp_path,
                                                               mr_paths):
    # NO_HARDWARE / MEASUREMENT_REQUESTS culture: when the data cannot
    # honestly anchor a fit, the loader files an error and stops - it never
    # invents. No occlusion==0 rows -> no ratio baseline -> MRDataError.
    rows = [r for r in _mr001_rows() if r["occlusion_frac_est"] > 0.0]
    p = tmp_path / "noclean.csv"
    p.write_text(_csv_text(MR001_COLS, rows))
    with pytest.raises(mr_ingest.MRDataError, match="occlusion"):
        mr_ingest.build_mr_curveset(p, mr_paths[1], mr_paths[2])


# --- the produced CurveSet and the seam contract ---

def test_built_curveset_fields_and_carried_constants(mr_paths):
    cs, report = mr_ingest.build_mr_curveset(*mr_paths)
    assert cs.name == "mr_v1"
    assert cs.angle_falloff_exponent == report.angle_exponent_hat
    assert cs.lux_knee == report.lux_knee_hat
    assert cs.lux_floor_p == report.lux_floor_hat
    # Committed constants the bench cannot re-measure are carried, labeled:
    # the IS §3.2 decode floor and the #39 false-positive anchor.
    assert cs.detection_onset_px == 20.0
    assert cs.fp_rate_per_image == pytest.approx(1.4e-5)


def test_build_does_not_register(mr_paths):
    mr_ingest.build_mr_curveset(*mr_paths)
    with pytest.raises(KeyError):
        curves.get("mr_v1")  # registration stays an explicit swap-session act


def test_registered_mr_v1_flows_through_the_injector_seam(mr_paths):
    from wyzantium_sim.perception.inject import PerceptionInjector
    cs, _ = mr_ingest.build_mr_curveset(*mr_paths)
    curves.register(cs)
    try:
        inj = PerceptionInjector(20260811, {
            "outer_occlusion": 0.0, "inner_occlusion": 0.0,
            "illuminance_lux": 800, "rain": 0.0, "dropout_p": 0.0,
            "lens_contamination": 0.0, "mud_f_c": 0.8, "flip_kappa": 1.0,
            "sigma_px": 0.5, "perception_rate_hz": 30,
            "perception_latency_ms": 30, "curve_set": "mr_v1",
        })
        assert inj.curve is cs
    finally:
        curves.unregister("mr_v1")


def test_swept_axis_recommendations_are_report_not_curveset(mr_paths):
    # mud_f_c, sigma_px, flip_kappa are SWEEP AXES (config), not CurveSet
    # fields - the seam cannot absorb them silently. The report carries the
    # fitted recommendations; collapsing the sweeps is a recorded revision.
    cs, report = mr_ingest.build_mr_curveset(*mr_paths)
    assert not hasattr(cs, "mud_f_c")
    assert not hasattr(cs, "sigma_px")
    assert report.mud_f_c_hat is not None
    assert report.sigma_px_hat is not None
    assert report.flip_kappa_hat is not None
