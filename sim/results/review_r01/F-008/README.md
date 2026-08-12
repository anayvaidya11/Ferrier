# F-008 L2 probe — inner-tag decode pixel extent uses constellation span: 10 mm tags decode at 3 m

**Status: CONFIRMED** (L2). Probe: `studies/R01_PHASE1_REVIEW/probes/probe_f008.py`
→ `result.json` here. Run at HEAD `2b9a5c7` (numbers verified identical when
re-run at `5c31f07` and `0c76b52` — post-anchor commits are docs/results only);
every module the probe exercises
(`perception/sightings|inject|detection|curves`, `geometry`, `params`, `frames`,
`kinematic/stage`) is byte-identical to the R01 anchor `cdf7fbf` ≡ freeze
`b493e7a` (the only post-anchor code-tree delta is the `mr_ingest` addition,
reviewed at its own SHA `7e9bb47`, not touched here). Code freeze respected:
the control arm monkeypatches in memory only.

## Clause

- **IS §3.3** inner-ring readability arithmetic [derived]: a **10 mm** tag
  subtends **39 px at 300 mm** and 116 px at 100 mm — the per-tag pixel extent
  is what clears the floor "across the inner-servo range" (D-004, D-012).
- **IS §3.2**: robust-decode floor **~20 px across the tag**.
- **D-034 / FAILURE_TAXONOMY IS8-2**: with the outer tag gone, the approach
  should be dark at acquisition range — IS8-2's basis is "zero ID-0 detections
  across the whole approach"; `machine.py:193` opens the dark-window hold wall
  only on `pose_source == "none" and no tags`.

## Expectation per the documents

10 mm inner tags are readable from ~0.3 m in, not at ~3 m. Under the code's own
pixel model (`px = f_px · span / dist`, Cam B f = 880 px) a 10 mm tag at 2.81 m
from Cam B subtends **~3.1 px** — far below the 20 px floor and below the
prior_v1 ramp bottom (onset 20 − width 10 = 10 px), so p_detect = 0 exactly.
With `knockout_mask=1` (outer tag destroyed) every acquisition-range frame
should therefore be dark: `pose_source: "none"`, D-034 window opens, IS8-2
reachable.

## What the code does instead

`sightings.py:69` hard-codes `span_m = 0.11` (2 × 55 mm ring radius,
constellation span) for **every** inner-tag sighting; `inject.py:107` computes
the decode extent from that span: 880 × 0.11 / 2.81 m ≈ **34.4 px** — above
the 20 px floor, size factor 1.0, p_detect ≈ 0.996 per tag at 2.9 m.

## Probe design (probe33 style: failing condition + control, side by side)

Fixed seed 20260811, N = 1000 frames per arm, truth pose t = (2.9, 0, 0) m with
the frozen `Q_NOMINAL` (as-committed; F-012 is probed separately),
`knockout_mask = 1`, nominal degradation (`sim/scenarios/nominal.json` sweep
point, injector config assembled exactly as `trial.py:143–144`). Pure-python
perception injection — no MuJoCo step needed; runs in ~1 s.

- **Arm 1 (HEAD, failing condition):** frozen behavior, constellation-span
  convention.
- **Arm 2 (control):** `sightings._SPAN_M["inner"]` monkeypatched in memory to
  the per-tag size `geometry.INNER_TAG_SIZE_MM` = 0.010 m; identical seed,
  pose, config; patch restored in `finally`.

## Observed (result.json)

| | Arm 1 — HEAD (span 0.11 m) | Arm 2 — control (per-tag 0.010 m) |
|---|---|---|
| px extent at 2.81 m (Cam B) | **34.4 px** (> 20 px floor) | **3.13 px** (< 10 px ramp bottom) |
| analytic p_detect per inner tag | 0.9958–0.9971 | **0.0** |
| inner detections, 1000 frames | **7,967** (mean 7.97/frame) | **0** |
| frames with all 8 inner tags | 967 / 1000 | 0 |
| `pose_source` counts | `multi_tag_fused`: **1000** | `none`: **1000** |
| frames carrying a fused pose | 1000 | 0 |
| ID-0 (outer) detections | 0 (destroyed) | 0 (destroyed) |

Arm 1: with the outer tag destroyed, the injector still emits a full fused
inner-ring pose on every single frame at 2.9 m — `machine.py`'s dark-window
predicate (`pose_source == "none"`, no tags) can never fire, so D-034's
sustained-dark semantics are bypassed while the IS8-2 classifier basis
("no ID-0 the whole approach") simultaneously holds. Arm 2: restoring the
per-tag extent yields zero inner detections at acquisition range — every frame
is dark, exactly the IS8-2 dark-window regime the documents commit to.

(Arm 1's `conf` is low (mean 0.063) because the flip-ambiguity ratio at 2.9 m
scales the evidence mass down — a separate mechanism; the finding is about the
detection/pose stream itself, which is fully healthy where it must be dark.)

## Verdict

**CONFIRMED.** The decode pixel extent for inner tags uses the 110 mm
constellation span rather than the 10 mm per-tag size, letting the inner ring
decode ~all 8 tags per frame at acquisition range. Outer-destroyed cells
(`tag_knockout_mask` bit 0) therefore never enter the committed dark-window
path. Class B — joins the P-08 ratification sitting and the batched re-run.

## Re-run

```
cd /Users/anayvaidya/Wyzantium/Ferrier
sim/.venv/bin/python studies/R01_PHASE1_REVIEW/probes/probe_f008.py
```

Deterministic (fixed root seed, no wall clock): regenerates `result.json`
byte-identically on the same instance class (F-018 caveat).
