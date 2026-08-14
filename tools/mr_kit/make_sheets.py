"""Print-ready AprilTag sheets for the P-03 measurement window.

Generates the four PDFs under research/mr_kit/ (S1 outer 150 mm, S2 inner
10 mm, S3 ring r=55, S4 mounting guide) at exact physical scale on US
Letter, plus 300-dpi PNG twins in a build directory for machine
verification (verify_sheets.py). Geometry per INTERFACE_SPEC §3.2–§3.5
(D-016); tag bitmaps are the vendored AprilRobotics reference images
(assets/PROVENANCE.md) scaled nearest-neighbor only.

Instrument aid under NO_HARDWARE.md rev 2 (printed fiducial targets are a
permitted instrument class). Nothing here is product geometry.

Usage: sim/.venv/bin/python tools/mr_kit/make_sheets.py [--build-dir DIR]
"""
import argparse
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

KIT = Path(__file__).resolve().parent
REPO = KIT.parent.parent
OUT = REPO / "research" / "mr_kit"

LETTER_MM = (215.9, 279.4)
MM_PER_IN = 25.4
PNG_DPI = 300

# 36h11: PNG is 10x10 modules, black edge = 8 modules (IS §3.1).
MODULES_PNG = 10
MODULES_BLACK = 8

OUTER_EDGE_MM = 150.0    # IS §3.2 outer tag black edge
INNER_EDGE_MM = 10.0     # IS §3.3 inner tags black edge
RING_RADIUS_MM = 55.0    # IS §3.3 ring radius
RING_PITCH_DEG = 45.0    # IS §3.3 angular pitch
PLATE_MM = 200.0         # IS §3.2 plate
OUTER_TO_RING_MM = 185.0 # IS §4: T_stud_plate translation (0, 0, +185)


def _tag_array(tag_id):
    path = KIT / "assets" / f"tag36_11_{tag_id:05d}.png"
    arr = np.array(Image.open(path).convert("L"), dtype=float) / 255.0
    if arr.shape != (MODULES_PNG, MODULES_PNG):
        raise SystemExit(f"{path.name}: expected 10x10, got {arr.shape}")
    return np.kron(arr, np.ones((20, 20)))  # crisp raster, still nearest


def _page():
    w_in, h_in = LETTER_MM[0] / MM_PER_IN, LETTER_MM[1] / MM_PER_IN
    fig = plt.figure(figsize=(w_in, h_in))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, LETTER_MM[0])
    ax.set_ylim(0, LETTER_MM[1])
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


def _draw_tag(ax, tag_id, cx, cy, black_edge_mm):
    full = black_edge_mm * MODULES_PNG / MODULES_BLACK
    half = full / 2.0
    ax.imshow(_tag_array(tag_id),
              extent=[cx - half, cx + half, cy - half, cy + half],
              cmap="gray", vmin=0.0, vmax=1.0,
              interpolation="nearest", zorder=2)


def _scale_bar(ax, x, y):
    ax.plot([x, x + 100.0], [y, y], color="black", lw=1.2)
    for t in (0.0, 50.0, 100.0):
        ax.plot([x + t, x + t], [y - 2.0, y + 2.0], color="black", lw=1.2)
    ax.text(x + 50.0, y - 4.0,
            "scale check: this bar must measure 100 ± 1 mm",
            ha="center", va="top", fontsize=8)


def _footer(ax, sheet_id, note):
    ax.text(LETTER_MM[0] / 2, 12.0,
            f"{sheet_id} · WyZantium P-03 measurement kit · "
            "PRINT AT 100% / “Actual Size” · matte paper · "
            "verify the scale bar before use",
            ha="center", va="bottom", fontsize=8)
    if note:
        ax.text(LETTER_MM[0] / 2, 6.0, note,
                ha="center", va="bottom", fontsize=7, color="0.35")


def sheet_s1():
    fig, ax = _page()
    cx, cy = LETTER_MM[0] / 2, 158.0
    _draw_tag(ax, 0, cx, cy, OUTER_EDGE_MM)
    half = PLATE_MM / 2.0
    ax.plot([cx - half, cx + half, cx + half, cx - half, cx - half],
            [cy - half, cy - half, cy + half, cy + half, cy - half],
            color="0.55", lw=0.8, ls=(0, (4, 3)), zorder=1)
    for dx, dy in ((0, half), (0, -half), (half, 0), (-half, 0)):
        px, py = cx + dx, cy + dy
        if dx == 0:
            ax.plot([px, px], [py - 2.5, py + 2.5], color="0.55", lw=0.8)
        else:
            ax.plot([px - 2.5, px + 2.5], [py, py], color="0.55", lw=0.8)
    ax.text(cx, cy + half + 4.0,
            "ID 0 — outer tag, 150 mm black edge · dashed = 200 mm "
            "plate outline (reference only)",
            ha="center", va="bottom", fontsize=9)
    _scale_bar(ax, (LETTER_MM[0] - 100.0) / 2, 36.0)
    _footer(ax, "S1_outer_150mm",
            "MR-001/002 outer-scale target. Print several copies: mud is "
            "cumulative (MR-001) and MR-002 needs clean tags.")
    return fig


def sheet_s2():
    fig, ax = _page()
    cx, cy = LETTER_MM[0] / 2, 226.0
    _draw_tag(ax, 1, cx, cy, INNER_EDGE_MM)
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = cx + sx * 20.0, cy + sy * 20.0
            ax.plot([x, x - sx * 6.0], [y, y], color="black", lw=0.8)
            ax.plot([x, x], [y, y - sy * 6.0], color="black", lw=0.8)
    ax.text(cx, cy + 26.0,
            "ID 1 — inner-scale target, 10 mm black edge · cut on "
            "crop marks, mount flat",
            ha="center", va="bottom", fontsize=9)

    ax.text(LETTER_MM[0] / 2, 165.0,
            "Spares — IDs 1–8 at 10 mm (cut as needed)",
            ha="center", va="bottom", fontsize=9)
    for k in range(8):
        col, row = k % 4, k // 4
        x = LETTER_MM[0] / 2 + (col - 1.5) * 40.0
        y = 140.0 - row * 45.0
        _draw_tag(ax, k + 1, x, y, INNER_EDGE_MM)
        ax.text(x, y - 12.0, f"ID {k + 1}", ha="center", va="top",
                fontsize=7)
    _scale_bar(ax, (LETTER_MM[0] - 100.0) / 2, 36.0)
    _footer(ax, "S2_inner_10mm", "")
    return fig


def ring_centers(cx, cy):
    """Paper positions of ring tags k=1..8 per IS §3.5: center =
    (h, -55 sin a, +55 cos a), a_k = 45(k-1) deg, clockwise from 12
    o'clock as seen from the approach side; paper right = -Y_stud."""
    out = []
    for k in range(1, 9):
        a = math.radians(RING_PITCH_DEG * (k - 1))
        out.append((k, cx + RING_RADIUS_MM * math.sin(a),
                    cy + RING_RADIUS_MM * math.cos(a)))
    return out


def sheet_s3():
    fig, ax = _page()
    cx, cy = LETTER_MM[0] / 2, 160.0
    for k, x, y in ring_centers(cx, cy):
        _draw_tag(ax, k, x, y, INNER_EDGE_MM)
        lx = cx + 70.0 * math.sin(math.radians(45.0 * (k - 1)))
        ly = cy + 70.0 * math.cos(math.radians(45.0 * (k - 1)))
        ax.text(lx, ly, f"{k}", ha="center", va="center", fontsize=7,
                color="0.4")
    ax.plot([cx - 8.0, cx + 8.0], [cy, cy], color="black", lw=0.6)
    ax.plot([cx, cx], [cy - 8.0, cy + 8.0], color="black", lw=0.6)
    for ang in (0, 90, 180, 270):
        x = cx + 80.0 * math.sin(math.radians(ang))
        y = cy + 80.0 * math.cos(math.radians(ang))
        ax.plot([x - 3.0 * math.cos(math.radians(ang)),
                 x + 3.0 * math.cos(math.radians(ang))],
                [y + 3.0 * math.sin(math.radians(ang)),
                 y - 3.0 * math.sin(math.radians(ang))],
                color="0.55", lw=0.8)
    ax.text(cx, cy + 92.0,
            "Inner ring — 8 × 10 mm tags (IDs 1–8), centers on "
            "r = 55 mm, 45° pitch,\nID 1 at 12 o’clock, all upright "
            "(IS §3.5) · crosshair = stud-axis center",
            ha="center", va="bottom", fontsize=9)
    ax.text(cx, cy - 92.0,
            "MR-003: use flat on the board (layout L-A) or raised on a "
            "shop-bought spacer (L-B).\nSpacer height: ARBITRARY, measured "
            "and recorded — never cut to a spec dimension.",
            ha="center", va="top", fontsize=8)
    _scale_bar(ax, (LETTER_MM[0] - 100.0) / 2, 36.0)
    _footer(ax, "S3_ring_r55", "")
    return fig


def sheet_s4():
    fig, ax = _page()
    ax.text(LETTER_MM[0] / 2, 262.0,
            "S4 — Mounting guide (NOT TO SCALE — nothing on this "
            "page is a target)",
            ha="center", va="bottom", fontsize=11, weight="bold")

    # Board schematic, half scale: outer tag sheet above, ring sheet below.
    s = 0.5
    bx, by = LETTER_MM[0] / 2, 155.0
    bw, bh = 240.0 * s, 340.0 * s
    ax.add_patch(plt.Rectangle((bx - bw / 2, by - bh / 2), bw, bh,
                               fill=False, ec="black", lw=1.0))
    oy = by + 92.5 * s
    ax.add_patch(plt.Rectangle((bx - 100.0 * s, oy - 100.0 * s),
                               200.0 * s, 200.0 * s, fill=False,
                               ec="0.3", lw=0.8))
    ax.text(bx, oy, "S1\n(outer tag,\nID 0)", ha="center", va="center",
            fontsize=8)
    ry = oy - OUTER_TO_RING_MM * s
    ax.add_patch(plt.Circle((bx, ry), 55.0 * s, fill=False, ec="0.3",
                            lw=0.8, ls=(0, (3, 3))))
    ax.text(bx, ry, "S3\n(ring)", ha="center", va="center", fontsize=8)
    x_dim = bx + 130.0 * s
    ax.annotate("", xy=(x_dim, oy), xytext=(x_dim, ry),
                arrowprops=dict(arrowstyle="<->", lw=0.9))
    ax.text(x_dim + 4.0, (oy + ry) / 2,
            "185 mm\ncenter-to-center\n(tape measure,\n±2 mm OK)",
            ha="left", va="center", fontsize=8)

    steps = (
        "1. Rigid board on tripod A; camera (iPhone) on tripod B.",
        "2. Mount S1 with its tag center 185 mm above the S3 ring center "
        "(dimension at right); both level, centers on a vertical line.",
        "3. Layout L-A (coplanar): S3 taped flat on the board.",
        "4. Layout L-B (collar): S3 on a shop-bought spacer stack — "
        "board → spacer → S3. Measure the standoff with the tape "
        "and RECORD it in the checklist. Use ≥2 different arbitrary "
        "heights across the day. NEVER cut or machine a spacer to a spec "
        "value (NO_HARDWARE rev 2).",
        "5. Set view angles with the protractor at the board edge "
        "(±2° is fine); camera positions per checklist: axial, "
        "then 30° oblique (D-025).",
        "6. Photograph the rig once per setup change (the checklist says "
        "when).",
    )
    y = 70.0
    for s_txt in steps:
        ax.text(18.0, y, s_txt, ha="left", va="top", fontsize=8.5,
                wrap=True)
        y -= 11.0 if len(s_txt) < 90 else 16.0
    _footer(ax, "S4_mounting_guide", "")
    return fig


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--build-dir", default=str(KIT / "build"),
                   help="PNG twins for verification land here (not "
                        "committed)")
    args = p.parse_args()
    build = Path(args.build_dir)
    OUT.mkdir(parents=True, exist_ok=True)
    build.mkdir(parents=True, exist_ok=True)

    sheets = {
        "S1_outer_150mm": sheet_s1,
        "S2_inner_10mm": sheet_s2,
        "S3_ring_r55": sheet_s3,
        "S4_mounting_guide": sheet_s4,
    }
    for name, fn in sheets.items():
        fig = fn()
        fig.savefig(OUT / f"{name}.pdf", format="pdf")
        fig.savefig(build / f"{name}.png", format="png", dpi=PNG_DPI)
        plt.close(fig)
        print(f"wrote {OUT / (name + '.pdf')} (+ png twin)")


if __name__ == "__main__":
    main()
