"""CSV templates for the three MR outputs, headers exactly per mr_ingest.

Writes research/data/mr00{1,2,3}_*.template.csv (the real files land
beside them minus ".template") with `#` header comments the loader strips.
--selftest writes synthetic filled copies to the build dir and runs them
through wyzantium_sim.perception.mr_ingest.read_mr00{1,2,3} — the same
hard gates the real swap session will apply.

Usage: sim/.venv/bin/python tools/mr_kit/make_templates.py [--selftest]
"""
import argparse
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parent
REPO = KIT.parent.parent
DATA = REPO / "research" / "data"

MR001 = "mr001_mud_detection.template.csv"
MR002 = "mr002_lowlux_detection.template.csv"
MR003 = "mr003_flip_rate.template.csv"

HDR001 = ("tag_scale_mm,range_m,view_angle_deg,occlusion_frac_est,"
          "illuminance_lux,n_frames,n_detected,reproj_rms_px,"
          "detector_version,notes")
HDR002 = ("tag_scale_mm,view_angle_deg,illuminance_lux,exposure_ms,"
          "gain_setting,n_frames,n_detected,reproj_rms_px,"
          "detector_version,notes")
HDR003 = ("layout,collar_standoff_mm,cam_position,view_angle_deg,"
          "n_frames,n_detected,n_flipped,reproj_rms_px,"
          "detector_version,notes")

T001 = f"""\
# MR-001 — AprilTag 36h11 detection rate vs. mud occlusion (MEASUREMENT_REQUESTS.md)
# One row per condition. Units: tag_scale_mm [mm], range_m [m],
# view_angle_deg [deg], occlusion_frac_est in [0,1], illuminance_lux [lux],
# reproj_rms_px [px] (mean RMS corner reprojection residual, from
# detect_frames.py).
# occlusion_frac_est estimation method (REQUIRED, fill in before data lands):
#   <describe how occlusion fraction was estimated from the pre-condition
#    stills, e.g. grid overlay count on the photograph>
# Loader hard gates (mr_ingest.py): occlusion 0 baseline rows must exist per
# geometry; 0 <= n_detected <= n_frames; occlusion_frac_est in [0,1].
{HDR001}
"""

T002 = f"""\
# MR-002 — detection rate vs. illuminance below 10 lux (MEASUREMENT_REQUESTS.md)
# One row per condition. exposure_ms is the FIXED shutter used (ceiling
# derivation on CHECKLIST_MR002); gain_setting is the locked ISO (string ok).
# Absolutes are NON-TRANSFERABLE (instrument-specific); only the relative
# trend is carried forward.
{HDR002}
"""

T003 = f"""\
# MR-003 — detection and pose-flip rate vs. view angle, both layouts (MEASUREMENT_REQUESTS.md)
# One row per condition. layout in {{coplanar,collar}}; collar_standoff_mm
# empty for coplanar rows, else the MEASURED shop-bought spacer height;
# cam_position in {{axial,oblique}}; n_flipped judged against rig geometry
# (recovered-normal sign, detect_frames.py).
# Loader hard gates: enums as above; 0 <= n_flipped <= n_detected <= n_frames.
{HDR003}
"""


def write_templates():
    DATA.mkdir(parents=True, exist_ok=True)
    for name, text in ((MR001, T001), (MR002, T002), (MR003, T003)):
        (DATA / name).write_text(text)
        print(f"wrote {DATA / name}")


def selftest(build):
    sys.path.insert(0, str(REPO / "sim"))
    from wyzantium_sim.perception import mr_ingest

    build.mkdir(parents=True, exist_ok=True)
    ver, notes = "selftest-0", "synthetic"

    rows001 = []
    for scale, rng in ((150.0, 3.0), (150.0, 1.0), (10.0, 0.30)):
        for ang in (0.0, 20.0, 40.0):
            for occ in (0.0, 0.3, 0.5):
                import math
                p = max(0.05, math.cos(math.radians(ang)) ** 1.5
                        * (1.0 - occ) * max(0.0, 1.0 - occ / 0.8))
                rows001.append(f"{scale},{rng},{ang},{occ},800,100,"
                               f"{int(round(100 * p))},0.4,{ver},{notes}")
    f001 = build / "mr001_filled.csv"
    f001.write_text(T001 + "\n".join(rows001) + "\n")

    rows002 = []
    for scale in (150.0, 10.0):
        for ang in (0.0, 40.0):
            for lux, p in ((50, 1.0), (10, 0.9), (5, 0.7), (2, 0.5),
                           (1, 0.3)):
                rows002.append(f"{scale},{ang},{lux},0.5,ISO1600,100,"
                               f"{int(100 * p)},0.5,{ver},{notes}")
    f002 = build / "mr002_filled.csv"
    f002.write_text(T002 + "\n".join(rows002) + "\n")

    rows003 = []
    for layout, standoff in (("coplanar", ""), ("collar", "18.4"),
                             ("collar", "31.0")):
        for cam in ("axial", "oblique"):
            for ang in (0.0, 2.0, 4.0, 6.0, 8.0, 10.0, 15.0, 30.0):
                if layout == "coplanar" and cam == "axial" and ang > 0:
                    flip = max(0, int(round(100 * (0.40 - 0.038 * ang))))
                else:
                    flip = 0
                rows003.append(f"{layout},{standoff},{cam},{ang},100,98,"
                               f"{flip},0.45,{ver},{notes}")
    f003 = build / "mr003_filled.csv"
    f003.write_text(T003 + "\n".join(rows003) + "\n")

    n1 = len(mr_ingest.read_mr001(f001))
    n2 = len(mr_ingest.read_mr002(f002))
    n3 = len(mr_ingest.read_mr003(f003))
    print(f"selftest: read_mr001 {n1} rows, read_mr002 {n2} rows, "
          f"read_mr003 {n3} rows — all accepted")

    for name in (MR001, MR002, MR003):
        empty = mr_ingest._rows(DATA / name, ())
        assert empty == [], f"{name}: template should parse to zero rows"
    print("selftest: committed templates parse clean (zero data rows)")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--selftest", action="store_true")
    p.add_argument("--build-dir", default=str(KIT / "build"))
    args = p.parse_args()
    write_templates()
    if args.selftest:
        selftest(Path(args.build_dir))


if __name__ == "__main__":
    main()
