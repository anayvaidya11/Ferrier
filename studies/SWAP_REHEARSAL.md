# The mr_v1 Swap, Rehearsed — and the Runbook for the Real One

**Status:** rehearsal complete 2026-08-14. All numbers below are
**SYNTHETIC** (inputs generated from `sim/tests/test_mr_ingest.py` ground
truth); they exist to prove the *mechanism*, not to say anything about
perception. Artifacts: `sim/results/swap_rehearsal/`.

## Why this exists

The swap session (late August, after the P-03 bench days) is the single
moment the Phase 1 gate number can honestly move. Its fit rules were
pre-registered and unit-tested long ago (`mr_ingest.py`), but the
execution path — fit, register, re-run the committed plans at scale,
report before/after — had never been run end-to-end. Rehearsing it found
one real defect and retired every mechanism unknown.

## The finding: the worker-registration seam (fixed)

`perception/curves.py` registration is in-process, but
`doe/runner.py run_sweep` executes trials in `ProcessPoolExecutor`
workers — fresh interpreters where only `prior_v1` exists. Any
multi-worker `mr_v1` sweep died with a `KeyError` at
`inject.py`'s `curves.get()`. The real swap would have crashed at scale
on the instance.

**Fix:** `run_sweep(..., curve_sets=())` threads extra `CurveSet` objects
into the worker initializer, which registers them idempotently; a
same-name set with different values is refused (never-edit-in-place).
Pinned by `sim/tests/test_swap_seam.py`: the multi-worker mr_v1 sweep
passes with the seam, the pre-seam failure still raises without it,
prior_v1 callers are untouched (5 tests).

## What the rehearsal proved (synthetic, miniature scale, local M4, $0)

`tools/swap_mr_v1.py --rehearse --out sim/results/swap_rehearsal`:

1. **Fit recovery** — the pre-registered fits recovered the generating
   parameters within the committed test tolerances (angle exponent
   2.0013 vs 2.0; mud f_c 0.700 vs 0.7; lux knee 10.0 exact; floor
   0.2496 vs 0.25; σ_px 0.42 exact; flip κ 1.3085 vs 1.3).
2. **Seed-paired re-run through the fixed seam** — tier1 (98), tier2
   (30), gate (50) on BOTH curve sets, 8 workers; every mr_v1 header
   stamps `curve_set: mr_v1`.
3. **Before/after moves coherently** (synthetic mr_v1 is deliberately
   harsher: angle exponent 2 vs 1): tier1 88/98 → 85/98; tier2 2/30 →
   1/30; gate 0/50 → 0/50 (all refusals, both sides). Both numbers
   reported, never a delta alone.
4. **Determinism through the new seam** — a second full rehearsal run
   reproduced all six per-record sha256 lists byte-identically.
5. **The pooling guard fires in anger** — `MixedCurveSetsError` on a
   deliberately mixed prior_v1+mr_v1 directory (`guard_demo.json`).

## The real-swap runbook (late August)

Preconditions: P-03 bench days done; three real CSVs committed as
`research/data/mr001_mud_detection.csv`, `mr002_lowlux_detection.csv`,
`mr003_flip_rate.csv` (the kit's `detect_frames.py` writes loader-valid
rows); compute decision made per A-004 policy (instance vs local is the
human's call — the full re-run is ~14k trials, ~$0.15 at the committed
A-004 rate; **explicit go required before any billable launch**).

```
# on the chosen compute, repo synced including .git:
python tools/swap_mr_v1.py --out <runs>/swap_mr_v1 --workers 32 \
    --usd-per-1k 0.009502167853532263
```

One command does, in order: build_mr_curveset (pre-registered fits; it
RAISES rather than interpolate on inadequate data), register mr_v1, run
tier1/tier2/gate on mr_v1 **seed-paired with freeze_prior_v2** (same
SWEEP_ROOT + tags → same seeds; the curve set is the only changed input),
and write `before_after.json` against the committed
`freeze_prior_v2/freeze_summary.json`. Spend is metered per P-02.

Then, in-session: commit the output directory's JSONs + sha lists (freeze
naming: `freeze_mr_v1` or similar), re-render D-014/D-017 figures on the
mr_v1 dataset, restate the gate number against `gate_moderate.json`, and
update HOW-FAR-ALONG + ROADMAP. The fit report's warnings travel with the
result: decode floor / onset width / fp anchor are carried from prior_v1
(the bench cannot re-measure them), and mud_f_c / σ_px / flip_kappa
remain sweep axes — their fitted values ride in the report; collapsing a
sweep is a recorded revision.

## What the rehearsal deliberately did not do

No real data touched; no cloud spend; no full-scale run; no figure
rendering (charts operate on any dataset and were exercised by the
freezes). The gate number did not move and cannot move until the bench
CSVs land — that remains the program's one honest lever.
