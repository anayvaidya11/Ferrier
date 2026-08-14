# MR-003 day checklist — flip rate vs. view angle, both layouts (~1 day)

Goal: `research/data/mr003_flip_rate.csv` — 66 rows, N ≥ 100 frames each.
**Highest-value entry: this also decides the D-011 layout selection.** It
measures wrong-branch pose selection under real noise — the thing sim
cannot honestly measure (it would measure its own assumption back).

## Spacer law (NO_HARDWARE rev 2 — read before building the rig)

The collar variant is raised on **shop-bought spacers of arbitrary height**
(PVC caps, wood blocks, stacked washers — whatever the store had).

- [ ] ≥ 2 different heights; **measure each with the tape and RECORD it**
- [ ] **NEVER cut, sand, or machine a spacer toward any particular value** —
      a spacer made to a spec dimension is product geometry (an artifact)
      and fails the three-question test. The shipped standoff is set later
      by the selection *analysis*, not by this rig.

## Rig

- [ ] Clean prints: S1 (outer) + S3 (ring) mounted per S4 — centers 185 mm
      apart on the vertical, board on tripod A
- [ ] Camera range: close enough that all 8 ring tags + the outer tag decode
      cleanly at 0° (start ~0.5 m; record the value used in the CSV `notes`
      — bench operating point, arbitrary-labeled)
- [ ] Two camera positions per condition set: **axial** (on the board
      normal) and **oblique** (~30° off-axis, D-025's Cam B stand-in)
- [ ] View angle = yaw the **board** with the protractor. Always yaw the
      same direction (board normal swings toward the camera's **left**) —
      the flip judgment needs a consistent sign: `--rig-tilt-direction left`

## Grid — 66 conditions (tick as captured)

Angles: **0° 2° 4° 6° 8° 10°** (the near-head-on band where the flip lives —
do not skip it; rates are only fit-informative between 2% and 45%)
then **15° 30° 45° 60° 75°**.

| Layout | Cam | 0 | 2 | 4 | 6 | 8 | 10 | 15 | 30 | 45 | 60 | 75 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| coplanar (S3 flat) | axial | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| coplanar | oblique | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| collar @ height 1 = ____ mm | axial | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| collar @ height 1 | oblique | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| collar @ height 2 = ____ mm | axial | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |
| collar @ height 2 | oblique | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ | ☐ |

Per condition: set angle → ~4 s video → name it
`mr003_<layout>_<h>mm_<cam>_<angle>.mov` (coplanar: h = 0).

## Data entry (per condition)

```
sim/.venv/bin/python tools/mr_kit/detect_frames.py --mr 003 \
  --input mr003_collar_18mm_oblique_6.mov --layout collar \
  --collar-standoff-mm 18.4 --cam-position oblique --view-angle-deg 6 \
  --rig-tilt-direction left --f35-mm <your lens f35> \
  --append research/data/mr003_flip_rate.csv
```

(Coplanar rows: `--layout coplanar`, no standoff flag. First:
`cp research/data/mr003_flip_rate.template.csv research/data/mr003_flip_rate.csv`)

## Integrity gates

- `layout ∈ {coplanar, collar}`, `cam_position ∈ {axial, oblique}` —
  enforced by the loader and by `detect_frames.py`
- Collar rows must carry their **measured** standoff
- 0° rows are captured and recorded but carry no fit information (the flip
  fit uses view_angle > 0 only) — capture them anyway, they anchor detection
- **Overrun rule: defer remaining cells, never extend the 3-day budget**
