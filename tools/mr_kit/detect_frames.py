"""Offline frame processing for MR-001/002/003 → loader-valid CSV rows.

Takes one condition's captured frames (a directory of stills — JPEG/PNG/
HEIC — or one video file), runs the reference AprilTag detector
(pupil-apriltags wraps the AprilRobotics C implementation, D-010), and
emits one CSV row: n_frames, n_detected, (n_flipped for MR-003),
reproj_rms_px, detector_version. The row is validated through
wyzantium_sim.perception.mr_ingest before it is printed/appended, so a
day's data can never be rejected at swap time for schema reasons.

Pose/flip/reproj mechanics: detection (the P(detect) decision) is the
reference detector alone; reprojection residual and the MR-003 flip
judgment use OpenCV pose estimation on the reference detector's corners
(IPPE two-solution for planar layouts — branch choice under noise is
exactly what MR-003 measures — SQPNP for the non-planar collar model).
Flip = chosen solution's plate-normal horizontal sign contradicting the
rig direction (--rig-tilt-direction). 0° rows are recorded but carry no
fit information (mr_ingest skips view_angle <= 0 in the flip fit).

Intrinsics (bench-grade, non-transferable): --fx-px, or --f35-mm
(35 mm-equivalent focal length, fx = width * f35 / 36), or EXIF
FocalLengthIn35mmFilm from the first still. Principal point = image
center. Recorded in notes.

Examples:
  detect_frames.py --mr 001 --input cond_037.mov --tag-id 0 \\
      --tag-scale-mm 150 --range-m 3.0 --view-angle-deg 20 \\
      --occlusion-frac 0.3 --lux 800 --f35-mm 26 \\
      --append research/data/mr001_mud_detection.csv
  detect_frames.py --mr 003 --input cond_12/ --layout collar \\
      --collar-standoff-mm 18.4 --cam-position oblique \\
      --view-angle-deg 6 --rig-tilt-direction left --f35-mm 26 \\
      --append research/data/mr003_flip_rate.csv
"""
import argparse
import math
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from pillow_heif import register_heif_opener
from pupil_apriltags import Detector
import pupil_apriltags

register_heif_opener()

KIT = Path(__file__).resolve().parent
REPO = KIT.parent.parent
sys.path.insert(0, str(REPO / "sim"))
from wyzantium_sim.perception import mr_ingest  # noqa: E402

STILL_EXTS = {".jpg", ".jpeg", ".png", ".heic", ".heif", ".tif", ".tiff"}
VIDEO_EXTS = {".mov", ".mp4", ".m4v", ".avi"}

# IS §3.2–§3.5 rig model constants (mm), rig frame: origin ring center,
# X right / Y up as seen from the camera side, Z out of the plate.
RING_R, RING_PITCH = 55.0, 45.0
INNER_EDGE, OUTER_EDGE = 10.0, 150.0
OUTER_CENTER_Y = 185.0

DETECTOR_VERSION = (f"pupil-apriltags {pupil_apriltags.__version__} "
                    f"+ opencv {cv2.__version__}")


def frames(path):
    path = Path(path)
    if path.is_dir():
        stills = sorted(p for p in path.iterdir()
                        if p.suffix.lower() in STILL_EXTS)
        if not stills:
            sys.exit(f"no stills found in {path}")
        for p in stills:
            yield np.array(Image.open(p).convert("L"))
    elif path.suffix.lower() in VIDEO_EXTS:
        cap = cv2.VideoCapture(str(path))
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            yield cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cap.release()
    else:
        yield np.array(Image.open(path).convert("L"))


def fx_from_exif(path):
    path = Path(path)
    still = (sorted(p for p in path.iterdir()
                    if p.suffix.lower() in STILL_EXTS)[0]
             if path.is_dir() else path)
    if still.suffix.lower() in VIDEO_EXTS:
        return None, None
    img = Image.open(still)
    f35 = img.getexif().get(41989)  # FocalLengthIn35mmFilm
    if not f35:
        return None, None
    return img.width * float(f35) / 36.0, f"exif f35={f35}mm"


def tag_model(tag_id, layout, standoff):
    """Corner model points (rig frame, mm) in apriltag corner order:
    bottom-left, bottom-right, top-right, top-left of the upright tag."""
    if tag_id == 0:
        cx, cy, cz, s = 0.0, OUTER_CENTER_Y, 0.0, OUTER_EDGE
    elif 1 <= tag_id <= 8:
        a = math.radians(RING_PITCH * (tag_id - 1))
        cz = standoff if layout == "collar" else 0.0
        cx, cy, s = RING_R * math.sin(a), RING_R * math.cos(a), INNER_EDGE
    else:
        return None
    h = s / 2.0
    return np.array([[cx - h, cy - h, cz], [cx + h, cy - h, cz],
                     [cx + h, cy + h, cz], [cx - h, cy + h, cz]],
                    dtype=np.float64)


def solve(obj, img_pts, K):
    planar = np.ptp(obj[:, 2]) < 1e-9
    if planar:
        # IPPE requires the object plane at z=0; a constant-z model (e.g.
        # ring-only collar detections) is the same plane translated.
        obj = obj.copy()
        obj[:, 2] = 0.0
        flag = cv2.SOLVEPNP_IPPE
    else:
        flag = cv2.SOLVEPNP_SQPNP
    try:
        n, rvecs, tvecs, errs = cv2.solvePnPGeneric(
            obj, img_pts, K, None, flags=flag)
    except cv2.error:
        return None
    if n == 0:
        return None
    errs = np.asarray(errs).reshape(-1)
    best = int(np.argmin(errs))
    return rvecs[best], float(errs[best])


def process(args):
    det = Detector(families="tag36h11")
    K = np.array([[args.fx_px, 0, 0], [0, args.fx_px, 0], [0, 0, 1]],
                 dtype=np.float64)
    want_flip = args.mr == "003"
    expected = ({args.tag_id} if args.mr in ("001", "002")
                else set(range(0, 9)))

    n_frames = n_detected = n_flipped = 0
    reproj = []
    for gray in frames(args.input):
        n_frames += 1
        if K[0, 2] == 0:
            K[0, 2], K[1, 2] = gray.shape[1] / 2.0, gray.shape[0] / 2.0
        ds = [d for d in det.detect(np.ascontiguousarray(gray))
              if d.tag_id in expected]
        if not ds:
            continue
        n_detected += 1

        obj_rows, img_rows = [], []
        for d in ds:
            m = tag_model(d.tag_id, args.layout, args.collar_standoff_mm)
            if m is None:
                continue
            obj_rows.append(m)
            img_rows.append(np.asarray(d.corners, dtype=np.float64))
        if not obj_rows:
            continue
        obj = np.concatenate(obj_rows)
        img_pts = np.concatenate(img_rows)
        sol = solve(obj, img_pts, K)
        if sol is None:
            continue
        rvec, err = sol
        reproj.append(err)
        if want_flip:
            R, _ = cv2.Rodrigues(rvec)
            n_cam_x = float((R @ np.array([0.0, 0.0, 1.0]))[0])
            expect_neg = args.rig_tilt_direction == "left"
            if (n_cam_x < 0) != expect_neg:
                n_flipped += 1

    rms = float(np.mean(reproj)) if reproj else 0.0
    return n_frames, n_detected, n_flipped, rms


def build_row(args, n_frames, n_detected, n_flipped, rms):
    notes = args.notes or ""
    notes = (notes + ("; " if notes else "")
             + f"fx_px={args.fx_px:.0f} ({args.fx_source})").replace(",", ";")
    r = f"{rms:.3f}"
    if args.mr == "001":
        return (f"{args.tag_scale_mm},{args.range_m},{args.view_angle_deg},"
                f"{args.occlusion_frac},{args.lux},{n_frames},{n_detected},"
                f"{r},{DETECTOR_VERSION},{notes}")
    if args.mr == "002":
        return (f"{args.tag_scale_mm},{args.view_angle_deg},{args.lux},"
                f"{args.exposure_ms},{args.gain_setting},{n_frames},"
                f"{n_detected},{r},{DETECTOR_VERSION},{notes}")
    standoff = ("" if args.layout == "coplanar"
                else f"{args.collar_standoff_mm}")
    return (f"{args.layout},{standoff},{args.cam_position},"
            f"{args.view_angle_deg},{n_frames},{n_detected},{n_flipped},"
            f"{r},{DETECTOR_VERSION},{notes}")


def validate_row(mr, row):
    template = {
        "001": ("mr001_mud_detection.template.csv", mr_ingest.read_mr001),
        "002": ("mr002_lowlux_detection.template.csv", mr_ingest.read_mr002),
        "003": ("mr003_flip_rate.template.csv", mr_ingest.read_mr003),
    }
    name, reader = template[mr]
    header = (REPO / "research" / "data" / name).read_text()
    with tempfile.NamedTemporaryFile("w", suffix=".csv",
                                     delete=False) as f:
        f.write(header + row + "\n")
        tmp = Path(f.name)
    try:
        assert len(reader(tmp)) == 1
    finally:
        tmp.unlink()


def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--mr", required=True, choices=("001", "002", "003"))
    p.add_argument("--input", required=True,
                   help="directory of stills or one video file")
    p.add_argument("--append", help="CSV to append the validated row to "
                                    "(copy the template first)")
    p.add_argument("--notes", default="")
    p.add_argument("--fx-px", type=float)
    p.add_argument("--f35-mm", type=float,
                   help="35mm-equivalent focal length (fx = W*f35/36)")
    p.add_argument("--tag-id", type=int, default=None,
                   help="MR-001/002 target tag (0 = 150 mm outer, "
                        "1 = 10 mm solo)")
    p.add_argument("--tag-scale-mm", type=float)
    p.add_argument("--range-m", type=float)
    p.add_argument("--view-angle-deg", type=float)
    p.add_argument("--occlusion-frac", type=float)
    p.add_argument("--lux", type=float)
    p.add_argument("--exposure-ms", type=float)
    p.add_argument("--gain-setting", default="")
    p.add_argument("--layout", choices=("coplanar", "collar"))
    p.add_argument("--collar-standoff-mm", type=float, default=0.0)
    p.add_argument("--cam-position", choices=("axial", "oblique"))
    p.add_argument("--rig-tilt-direction", choices=("left", "right"),
                   default="left",
                   help="MR-003: which way the board normal points in "
                        "the image at positive view angle")
    args = p.parse_args()

    need = {"001": ("tag_id", "tag_scale_mm", "range_m", "view_angle_deg",
                    "occlusion_frac", "lux"),
            "002": ("tag_id", "tag_scale_mm", "view_angle_deg", "lux",
                    "exposure_ms"),
            "003": ("layout", "cam_position", "view_angle_deg")}
    missing = [k for k in need[args.mr] if getattr(args, k) in (None, "")]
    if missing:
        sys.exit(f"--mr {args.mr} requires: "
                 + ", ".join("--" + m.replace("_", "-") for m in missing))
    if args.mr == "003" and args.layout == "collar" \
            and not args.collar_standoff_mm:
        sys.exit("collar layout requires --collar-standoff-mm (the "
                 "MEASURED spacer height)")

    if args.fx_px:
        args.fx_source = "flag"
    elif args.f35_mm:
        args.fx_px, args.fx_source = None, None
        first = next(frames(args.input))
        args.fx_px = first.shape[1] * args.f35_mm / 36.0
        args.fx_source = f"f35={args.f35_mm}mm"
    else:
        args.fx_px, args.fx_source = fx_from_exif(args.input)
        if not args.fx_px:
            sys.exit("no intrinsics: pass --fx-px or --f35-mm "
                     "(EXIF f35 not found)")

    counts = process(args)
    row = build_row(args, *counts)
    validate_row(args.mr, row)
    n_frames, n_detected, n_flipped, rms = counts
    print(f"n_frames={n_frames} n_detected={n_detected} "
          + (f"n_flipped={n_flipped} " if args.mr == "003" else "")
          + f"reproj_rms_px={rms:.3f}")
    print(row)
    if args.append:
        with open(args.append, "a") as f:
            f.write(row + "\n")
        print(f"appended to {args.append}")


if __name__ == "__main__":
    main()
