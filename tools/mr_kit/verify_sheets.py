"""Machine verification of the generated sheets (plan gate for item 1).

Checks, per sheet: PDF page is exactly US Letter; the 300-dpi PNG twin
decodes with the reference detector to exactly the expected tag IDs; the
measured black-edge sizes and the S3 ring geometry (r = 55 mm, 45° pitch,
ID 1 at 12 o'clock) match INTERFACE_SPEC §3.2–§3.5 within print-irrelevant
tolerance. Exits nonzero on any failure.

Usage: sim/.venv/bin/python tools/mr_kit/verify_sheets.py [--build-dir DIR]
"""
import argparse
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image
from pupil_apriltags import Detector
from pypdf import PdfReader

KIT = Path(__file__).resolve().parent
OUT = KIT.parent.parent / "research" / "mr_kit"

MM_PER_PX = 25.4 / 300.0
LETTER_PT = (612.0, 792.0)
PAGE_H_MM = 279.4

FAILURES = []


def check(ok, msg):
    tag = "ok " if ok else "FAIL"
    print(f"  [{tag}] {msg}")
    if not ok:
        FAILURES.append(msg)


def detections(det, build, name):
    img = np.array(Image.open(build / f"{name}.png").convert("L"))
    return det.detect(img)


def center_mm(d):
    x, y = d.center
    return x * MM_PER_PX, PAGE_H_MM - y * MM_PER_PX


def edge_mm(d):
    c = d.corners
    sides = [np.linalg.norm(c[i] - c[(i + 1) % 4]) for i in range(4)]
    return float(np.mean(sides)) * MM_PER_PX


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--build-dir", default=str(KIT / "build"))
    args = p.parse_args()
    build = Path(args.build_dir)
    det = Detector(families="tag36h11")

    for name in ("S1_outer_150mm", "S2_inner_10mm", "S3_ring_r55",
                 "S4_mounting_guide"):
        page = PdfReader(OUT / f"{name}.pdf").pages[0]
        box = page.mediabox
        print(f"{name}:")
        check(abs(float(box.width) - LETTER_PT[0]) < 0.5
              and abs(float(box.height) - LETTER_PT[1]) < 0.5,
              f"PDF page {float(box.width):.1f}x{float(box.height):.1f} pt "
              "== US Letter")

        ds = detections(det, build, name)
        ids = sorted(d.tag_id for d in ds)

        if name == "S1_outer_150mm":
            check(ids == [0], f"decodes exactly ID 0 (got {ids})")
            if ids == [0]:
                e = edge_mm(ds[0])
                check(abs(e - 150.0) < 1.5,
                      f"black edge {e:.2f} mm == 150 mm")
        elif name == "S2_inner_10mm":
            check(ids == [1, 1, 2, 3, 4, 5, 6, 7, 8],
                  f"decodes solo ID1 + spares 1-8 (got {ids})")
            for d in ds:
                e = edge_mm(d)
                check(abs(e - 10.0) < 0.3,
                      f"ID {d.tag_id} black edge {e:.2f} mm == 10 mm")
        elif name == "S3_ring_r55":
            check(ids == [1, 2, 3, 4, 5, 6, 7, 8],
                  f"decodes ring IDs 1-8 (got {ids})")
            if ids == [1, 2, 3, 4, 5, 6, 7, 8]:
                pts = {d.tag_id: center_mm(d) for d in ds}
                cx = sum(x for x, _ in pts.values()) / 8.0
                cy = sum(y for _, y in pts.values()) / 8.0
                for k, (x, y) in sorted(pts.items()):
                    r = math.hypot(x - cx, y - cy)
                    check(abs(r - 55.0) < 0.5,
                          f"ID {k} radius {r:.2f} mm == 55 mm")
                    ang = math.degrees(math.atan2(x - cx, y - cy)) % 360.0
                    want = (45.0 * (k - 1)) % 360.0
                    delta = min(abs(ang - want), 360.0 - abs(ang - want))
                    check(delta < 1.0,
                          f"ID {k} at {ang:.2f}° == {want:.0f}° "
                          "(clockwise from 12 o'clock)")
                for d in ds:
                    e = edge_mm(d)
                    check(abs(e - 10.0) < 0.3,
                          f"ID {d.tag_id} black edge {e:.2f} mm == 10 mm")
        else:
            check(ids == [], f"schematic page has no decodable tags "
                             f"(got {ids})")

    if FAILURES:
        print(f"\n{len(FAILURES)} check(s) FAILED")
        sys.exit(1)
    print("\nall sheet checks passed")


if __name__ == "__main__":
    main()
