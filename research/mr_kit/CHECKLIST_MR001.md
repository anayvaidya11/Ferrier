# MR-001 day checklist — tag detection vs. mud (~1.5 days)

Goal: `research/data/mr001_mud_detection.csv` — 112 rows (14 geometries ×
8 mud levels), N ≥ 100 frames each. Governing text: `MEASUREMENT_REQUESTS.md`
MR-001 + Execution grids. **This is the axis the whole gate band hangs on.**

## Rig (once)

- [ ] Print S1 (several copies) and S2; verify each sheet's scale bar = 100 ± 1 mm
- [ ] Tag sheet flat on rigid board, board on tripod A
- [ ] iPhone on tripod B, manual-exposure app, **lock focus + exposure; camera
      untouched during capture** — re-lock only between geometry setups
- [ ] Fix one daylight-class exposure for the whole day; record lux at the tag
      plane per condition (lux-meter app)
- [ ] Tape measure for range, protractor at board edge for view angle (±2° OK)

## Geometry table

| G | Tag | Sheet / ID | Range | View angle |
|---|---|---|---|---|
| G01–G04 | 150 mm | S1 / ID 0 | 3.0 m | 0°, 20°, 40°, 60° |
| G05–G08 | 150 mm | S1 / ID 0 | 1.0 m | 0°, 20°, 40°, 60° |
| G09–G11 | 10 mm | S2 solo / ID 1 | 0.30 m | 0°, 20°, 40° |
| G12–G14 | 10 mm | S2 solo / ID 1 | 0.15 m | 0°, 20°, 40° |

(G01=3.0m/0°, G02=3.0m/20°, G03=3.0m/40°, G04=3.0m/60°, G05=1.0m/0°,
G06=1.0m/20°, G07=1.0m/40°, G08=1.0m/60°, G09=0.30m/0°, G10=0.30m/20°,
G11=0.30m/40°, G12=0.15m/0°, G13=0.15m/20°, G14=0.15m/40°)

## Procedure per mud level

Mud is **cumulative**: mud the tag once per level (visually estimated % of
tag area, soil + water mix), then cycle all 14 geometries **in the printed
order below** before adding the next level.

1. [ ] **Photograph the tag state** (still, close-up) — occlusion fraction is
   estimated from these later; note your estimation method in the CSV header
2. [ ] Move camera to the geometry; re-lock focus/exposure; hands off
3. [ ] Record ~4 s video at 30 fps (≥ 100 frames)
4. [ ] Note lux reading; name the clip `mr001_L<level>_G<nn>.mov`

## Randomized geometry order (seed 20260814 — do not reshuffle)

Regenerate: `random.Random(20260814)`, shuffle G01–G14 once per level, levels
ascending. Tick each condition as captured:

| Mud | Order |
|---|---|
|  0% | G02 G03 G11 G08 G04 G05 G07 G14 G13 G01 G09 G10 G06 G12 |
| 10% | G10 G08 G09 G02 G14 G07 G06 G11 G12 G13 G03 G04 G01 G05 |
| 20% | G04 G07 G12 G03 G11 G02 G08 G05 G06 G13 G01 G14 G09 G10 |
| 30% | G05 G03 G08 G04 G14 G07 G12 G10 G09 G11 G02 G13 G01 G06 |
| 40% | G03 G10 G09 G12 G13 G11 G07 G04 G08 G02 G01 G14 G06 G05 |
| 50% | G13 G10 G12 G06 G01 G11 G04 G03 G05 G02 G14 G09 G07 G08 |
| 60% | G14 G12 G05 G02 G09 G01 G07 G04 G13 G03 G08 G06 G11 G10 |
| 70% | G03 G06 G08 G12 G07 G04 G11 G14 G02 G10 G09 G01 G05 G13 |

## Data entry (per condition, after the day — Claude can run these)

```
sim/.venv/bin/python tools/mr_kit/detect_frames.py --mr 001 \
  --input mr001_L30_G05.mov --tag-id 0 --tag-scale-mm 150 \
  --range-m 1.0 --view-angle-deg 0 --occlusion-frac 0.30 --lux <reading> \
  --f35-mm <your lens f35> \
  --append research/data/mr001_mud_detection.csv
```

(10 mm geometries: `--tag-id 1 --tag-scale-mm 10`. First copy the template:
`cp research/data/mr001_mud_detection.template.csv research/data/mr001_mud_detection.csv`)

## Integrity gates (the loader rejects a day that violates these)

- The 0% level is mandatory — it is the per-geometry baseline
  (`mr_ingest` raises without occlusion = 0 rows)
- One row per condition; n_detected never exceeds n_frames (automatic via
  `detect_frames.py`)
- **Overrun rule: defer remaining cells, never extend the 3-day budget**
