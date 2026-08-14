# mr_kit — P-03 measurement-window kit

Generator + verification + frame-processing tooling for the MR-001/002/003
measurement window (`MEASUREMENT_REQUESTS.md`, `PENDING_HUMAN.md` P-03).
Everything here is an **instrument aid** under `NO_HARDWARE.md` rev 2
(printed fiducial targets, checklists, offline analysis) — nothing is
product geometry, and nothing touches `sim/wyzantium_sim` runtime code.

Committed outputs live in `research/mr_kit/` (sheets S1–S4, three day
checklists, shopping list) and `research/data/*.template.csv`.

## Dependencies (kit-only — deliberately NOT in sim/pyproject.toml)

```
sim/.venv/bin/python -m pip install pupil-apriltags opencv-python pillow-heif
```

`pupil-apriltags` wraps the AprilRobotics reference C detector (D-010); its
version lands in every CSV row's `detector_version`. OpenCV supplies video
decode + pose (IPPE/SQPNP) for reproj/flip; pillow-heif reads iPhone HEIC.

## Regenerate / verify

```
sim/.venv/bin/python tools/mr_kit/make_sheets.py       # PDFs + PNG twins
sim/.venv/bin/python tools/mr_kit/verify_sheets.py     # scale + decode gates
sim/.venv/bin/python tools/mr_kit/make_templates.py --selftest
```

`verify_sheets.py` asserts: US Letter page boxes; every sheet decodes to
exactly the expected tag IDs; measured black edges 150/10 mm; S3 ring
r = 55 mm at 45° pitch with ID 1 at 12 o'clock (IS §3.2–§3.5); the S4
schematic contains no decodable tag.

## Processing captured data

One command per condition — see the data-entry block in each checklist.
`detect_frames.py` validates every row through
`wyzantium_sim.perception.mr_ingest` before it prints/appends, so collected
data cannot be schema-rejected at swap time.

Tag bitmaps: `assets/` (vendored reference images — see
`assets/PROVENANCE.md`). `build/` is scratch (PNG twins, selftest CSVs),
not committed.
