# Vendored tag bitmaps — provenance

`tag36_11_00000.png` … `tag36_11_00008.png` (IDs 0–8) fetched 2026-08-14 from
the official AprilRobotics reference-image repository (the tag family of
record per D-010):

- Repo: https://github.com/AprilRobotics/apriltag-imgs
- Path: `tag36h11/tag36_11_0000N.png`
- Commit at fetch: `f3fd9a7add5bfd82a886fc65240fdb8e3c9ac5a1` (master)

Each PNG is 10×10 px: 1 px = 1 tag module; the 8×8 black-edge region spans
pixels 1–8 (stated tag dimension per INTERFACE_SPEC §3.1), with a 1-module
white quiet zone baked in. `make_sheets.py` scales these nearest-neighbor
only — the bitmaps are exact binary grids and are never resampled.
