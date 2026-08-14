# MR-002 day checklist — detection below 10 lux (~0.5 day)

Goal: `research/data/mr002_lowlux_detection.csv` — 20 rows, N ≥ 100 frames
each. **Clean tags** (fresh prints, not the MR-001 muddy ones). Absolutes are
instrument-specific → the whole dataset carries the **non-transferable**
label; only the relative trend is carried forward.

## The exposure ceiling (derived — Door 1; this closes MR-002's "the value
## the spec assumes" with shown arithmetic)

Motion blur must stay under ~1 px at the committed approach speeds, so the
low-light penalty appears as sensor noise, not as unbounded exposure time:

- Outer case: f_A ≈ 1371 px (#19), v = 1.0 m/s (IS §9.1 outer default) at
  r = 1.0 m → 1371 px/s → **1 px in 0.73 ms**
- Inner case: f_B ≈ 880 px (#20), v = 0.2 m/s at r = 0.20 m → 880 px/s →
  1 px in 1.14 ms

Strictest committed case = 0.73 ms. **Fix shutter at 1/2000 s (0.5 ms); if
the app lacks it, 1/1500 s (0.67 ms). Never slower.** Lock ISO too; record
both per row (`exposure_ms`, `gain_setting`). Label: *derived* from
committed #12/#19/#20 values; recorded here 2026-08-14.

## Rig

- [ ] Darkened room; single dimmable lamp; lux measured **at the tag plane**
      per condition (lux-meter app)
- [ ] Same tripod rig as MR-001; camera untouched during capture
- [ ] Shutter fixed at the ceiling above, ISO locked, focus locked

## Grid — 20 conditions (tick as captured)

Outer = S1/ID 0 at 1.0 m · Inner = S2 solo/ID 1 at 0.20 m

| Lux | 150 mm, 0° | 150 mm, 40° | 10 mm, 0° | 10 mm, 40° |
|---|---|---|---|---|
| 50 | ☐ | ☐ | ☐ | ☐ |
| 10 | ☐ | ☐ | ☐ | ☐ |
| 5  | ☐ | ☐ | ☐ | ☐ |
| 2  | ☐ | ☐ | ☐ | ☐ |
| 1  | ☐ | ☐ | ☐ | ☐ |

Per condition: set lamp → confirm lux → ~4 s video → name it
`mr002_<lux>lux_<scale>mm_<angle>.mov`.

Start at 50 lux: the loader normalizes each series at its brightest point —
skipping 50 lux orphans the series.

## Data entry (per condition)

```
sim/.venv/bin/python tools/mr_kit/detect_frames.py --mr 002 \
  --input mr002_5lux_150mm_0.mov --tag-id 0 --tag-scale-mm 150 \
  --view-angle-deg 0 --lux 5 --exposure-ms 0.5 --gain-setting ISO3200 \
  --f35-mm <your lens f35> \
  --append research/data/mr002_lowlux_detection.csv
```

(First: `cp research/data/mr002_lowlux_detection.template.csv research/data/mr002_lowlux_detection.csv`)
