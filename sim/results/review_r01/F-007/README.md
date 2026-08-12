# F-007 L2 probe — lone inner-tag frames use the full 110 mm constellation span for flip discriminability: flip-immune where H08 says "cannot self-disambiguate at any angle"

**Status: CONFIRMED** (L2). Probe: `studies/R01_PHASE1_REVIEW/probes/probe_f007.py`
→ `result.json` here. Run at HEAD `2b9a5c7`; every module the probe exercises
(`perception/sightings|inject|flip|detection|curves|noise|dropout|mud|timing`,
`geometry`, `params`, `frames`, `rng`, `kinematic/stage`) is byte-identical to
the R01 anchor `cdf7fbf` ≡ freeze `b493e7a` (the only post-anchor code-tree
delta is the `mr_ingest` addition, reviewed at its own SHA `7e9bb47`, not
touched here). Code freeze respected: all instrumentation and the control-arm
span swap are in-memory monkeypatches inside the probe process.

## Clause

- **D-011 qualification** (from studies/H08): a lone 10 mm tag **cannot
  self-disambiguate** the two-solution ambiguity at any view angle at
  inner-servo ranges.
- **H08 §2** lone-inner-tag row: S = 10 mm, Cam B at 0.25 m → f·S²/d² =
  1.4 px < 1.5 px threshold — "**no solution** — a lone inner tag cannot
  self-disambiguate at any angle". **§4**: the coplanar flip model takes D
  from §2 "using the ***visible* constellation span**"; `inject.TagSighting`'s
  own docstring commits to "the tag for a lone tag, the visible constellation
  span for fused inner-ring frames".
- **WIRE_FORMAT worked example 3**: a single near-head-on inner tag emits
  `ambiguity_ratio` 1.08, `ambiguity_flag` true — lone-tag frames are supposed
  to be visibly flip-suspect on the wire.

## Expectation per the documents

With every tag knocked out except inner tag 3 (`knockout_mask = 503`), frames
at 0.25–0.29 m / 52–60° from Cam B carry S = 0.010 m, so
D = f·S²·sinθ/d² ≈ 0.86–1.18 px < k·σ = 1.5 px: **every detected frame flags**
(ratio 0.58–0.78 < 1) and flips inject at
p_flip = 0.5·(1 − D/1.5)·κ ≈ 0.11–0.21 (κ = 1 nominal) — mean **0.166**,
i.e. ~265 flips over the 1,596 detected frames.

## What the code does instead

`sightings.py:69` hard-codes `span_m = _SPAN_M["inner"] = 0.11` (2 × 55 mm
ring radius) for **every** inner-tag sighting regardless of visible count.
The lone tag inherits the full constellation's discriminability:
D ≈ 105–141 px, ratio **69.7–94.3**, p_flip **identically 0** — flag never
raised, flip never injected, and `conf` never ambiguity-attenuated
(min(1, ratio) = 1). The #46 knockout axis and high inner-occlusion cells
therefore cannot produce the committed lone-tag flip behavior anywhere in the
frozen dataset.

## Probe design (probe33 style: failing condition + control, side by side)

Root seed **20260804** (poses and all injector substreams), **N = 3000**
frames per arm, `knockout_mask = 503` (lone inner tag 3), nominal sweep point
(`sim/scenarios/nominal.json`) with `sigma_px` pinned at `PARAMS[40].default`
= 0.5 exactly as `trial.py:144`; layout coplanar (trial default). Truth poses
sampled in x ∈ [0.24, 0.26], y ∈ [0.01, 0.05], z ∈ [−0.02, 0.02] m at frozen
`Q_NOMINAL` → tag 3 at 0.249–0.292 m / 52.2–60.2° from Cam B. Pure-python
perception injection, no MuJoCo step, ~1 s wall time, zero spend.
`flip.p_flip_for_layout` and `flip.reflect_about_boresight` are wrapped
in-memory to record the p_flip the injector actually consumed and each
realized flip.

- **Arm 1 (HEAD, failing condition):** frozen behavior — lone tag 3 carries
  span_m = 0.11.
- **Arm 2 (control):** identical seed/poses/config; the lone sighting's
  span_m is replaced in memory with the per-tag size 0.010 m
  (`geometry.INNER_TAG_SIZE_MM`) — the H08 §4 / TagSighting-docstring
  convention. Both px extents (331–389 px vs 30.1–35.3 px) sit above the
  20 px detection onset, so detection is span-invariant: both arms detect the
  **same 1,596 frames** (verified, `detected_sets_paired = true`) and the only
  live difference is the span feeding flip discriminability.

## Observed (result.json)

| | Arm 1 — HEAD (span 0.11 m) | Arm 2 — control (per-tag 0.010 m) |
|---|---|---|
| detected frames (of 3000) | 1,596 | 1,596 (identical set) |
| ambiguity_flag rate | **0.0** (0 frames) | **1.0** (1,596 frames) |
| ambiguity_ratio range | **69.7 – 94.3** (min ≫ 1) | 0.576 – 0.779 (all < 1) |
| p_flip the injector used | **identically 0** | 0.110 – 0.212, mean 0.1660 |
| p_flip vs H08 formula (S = 0.010) | max abs diff 0.212 (doc says 0.11–0.21, code uses 0) | max abs diff **0.0** (exact) |
| flips realized | **0** | **238** (expected 265.0 ± 44.5 at 3σ — within) |

H08-expected mean p_flip over these exact frames with S = 0.010: **0.1660**
(both arms, same geometry). The frozen arm realizes none of it; the control
arm realizes it at exactly the committed scale.

## Verdict

**CONFIRMED.** The frozen code makes lone inner-tag frames flip-immune
(flag rate 0, min ratio 69.7, p_flip ≡ 0, 0/1596 flips) in the exact regime
where D-011/H08 §2 commit "no solution at any angle", while swapping only the
span convention to the documented per-tag 0.010 m reproduces flags on 100% of
detected frames and flips at the H08-expected rate (238 vs 265 ± 44.5).
Class B; joins the P-08 ratification sitting.

## Re-run

```
cd /Users/anayvaidya/Wyzantium/Ferrier
sim/.venv/bin/python studies/R01_PHASE1_REVIEW/probes/probe_f007.py
```

Deterministic — fixed root seed 20260804, no wall-clock dependence; re-run
verified byte-identical `result.json`.
