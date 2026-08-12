# F-004 L2 probe — guidance wall timers persist across D-005 retry attempts

**Status: CONFIRMED** (L2). Probe: `studies/R01_PHASE1_REVIEW/probes/probe_f004.py`
→ `result.json` here. Run at HEAD `0c76b52`; both modules the probe exercises
(`guidance/machine.py`, and `trial.py` whose boundary handling the probe
emulates) are byte-identical to the R01 anchor `cdf7fbf` ≡ freeze `b493e7a`
(verified: `git diff --quiet cdf7fbf..HEAD -- sim/wyzantium_sim/guidance/
sim/wyzantium_sim/trial.py`). Code freeze respected: `sim/` is imported, never
modified; no monkeypatching was even needed — the attempt boundary is emulated
in the probe's own driver exactly as `trial.py` performs it.

## Clause

- **D-036**: inner-ring absence (rows 3/4) is **sustained time** — "< 2 inner
  tags continuously for 5 s" aborts; stochastic gaps are rejected frames
  (RING_PERSIST_FRAMES retired).
- **D-034**: row 2's no-detection frame is a **held frame, not an abort** —
  "single blips are held frames, not aborts"; escalation requires the dark
  window to exceed `HOLD_TIMEOUT_S` (5 s).
- **D-005**: an abort backs out 300 mm and re-approaches as a **new attempt**;
  `trial.py:181`'s own comment: "every attempt re-acquires (resync)".
- **IS §8 row 5**: "persistent" ambiguity, realized as
  `AMBIGUITY_PERSIST_FRAMES = 5` consecutive flagged frames.

## Expectation per the documents

Each D-005 re-approach is a fresh acquisition: its evidence windows (5 s dark
wall, 5 s ring-absence wall, 5-frame ambiguity streak) should accumulate from
that attempt's own frames. A new attempt's first gap/dark/flagged frame is one
frame of evidence — a reject/hold — never an instant abort or escalation.

## What the code does instead

`machine.py:102–104` initializes `_ambiguity_streak` / `_ring_absent_since` /
`_hold_since` **only in `__init__`**. `trial.py` constructs the machine once
per trial (line 149) and at every attempt boundary touches only
`machine.stage = "acquire"` (181) and `machine.attempt_n` (238, 248, 267,
307–308). An attempt that *ends with a window open* (e.g. 4.5 s of ring gaps,
then a row-5 abort) hands the open window to the next attempt: the wall-clock
comparison `t_s - self._ring_absent_since > HOLD_TIMEOUT_S` (machine.py:167,
same shape at 197) is already deep in violation by the time the re-approach
delivers its first qualifying frame, because the D-005 backout/travel itself
consumes many seconds. The `_ring_absent_since = None` reset (machine.py:183)
sits inside the `range_mm <= 300` guard, so healthy outer-range tracking
during the re-approach cannot clear it.

## Probe design (probe33 style: failing condition + fresh-machine control)

Fully deterministic: fixed 30 Hz frame index over `t = 100.0 + k/30` s, no
RNG (the machine has no RNG stream by design, #60), no MuJoCo step needed —
the finding is entirely in the guidance layer; runs in <1 s. Synthetic
`target_state` frame dicts shaped as in `sim/tests/test_guidance.py`.
Machine at committed defaults: `conf_min=0.85`, `attempts_max=3`,
`time_budget_s=900`. Per variant:

- **Arm 1 (repro):** ONE machine driven through attempt 1 ending with an open
  window, then the boundary exactly as `trial.py` performs it, then
  attempt 2's frame stream.
- **Arm 2 (control):** a FRESH machine fed the IDENTICAL attempt-2 stream —
  same frames, same absolute `t_s` values.

## Observed (result.json)

| Variant | Arm 1 — stale machine | Arm 2 — fresh control |
|---|---|---|
| **R** — D-036 ring absence: attempt 1 carries 4.5 s of gaps, ends on a row-5 abort; attempt 2 re-approaches 8 s clean at 1500 mm, then gaps at 250 mm | `abort_retry inner_ring_absent` on the **first** gap frame — **0.000 s** in-attempt absence (stale window opened 12.67 s earlier, in attempt 1) | abort after **152** gap frames = **5.033 s**, per D-036 |
| **Da** — D-034 dark window: attempt 1 carries 4.5 s of darkness; attempt 2 dark from its first frame | `escalate low_confidence` after **12** dark frames = **0.367 s** | escalate after **152** dark frames = **5.033 s** |
| **Db** — D-034's exact sentence: ONE isolated dark blip 8 s into attempt 2 | **`escalate`** on the single blip | **`hold`** (blip is a held frame) |
| **S** — row-5 streak across a contact-jam boundary (`trial.py:307–308`: jam consumes the attempt with no machine decision, so no row-5 reset fires) | `abort_retry ambiguity_persistent` after **1** flagged frame | abort after **5** flagged frames |

All four variants: `violation: true`. Overall `confirmed: true`.

Amplification (variant R, arm 1): the instant abort also burned the attempt —
`attempt_n_at_abort = 3`. A stale window converts what D-036 prices at ≥5 s of
per-attempt evidence into one frame per attempt, so an `attempts_max=3` budget
can be exhausted by 2 stray gap frames across attempts 2–3 — directly feeding
the refusal-dominated 0 % gate cell.

Note on Db: no frames are fed between the boundary and the blip in arm 1 —
any attempt-2 frame reaching the clean fall-through (machine.py:214) resets
`_hold_since`, so Db stands for re-approaches whose early frames are
non-resetting (dark/flagged/gap), i.e. the gate cell's dropout regime.
Variant Da needs no such gap.

## Verdict

**CONFIRMED.** The stale timers make a new attempt's first qualifying frame an
instant abort/escalation, violating D-034's held-frame semantics and D-036's
sustained-time window; the fresh-machine controls behave exactly per the
documents on the identical stream. Class B — behavioral fix (reset the three
fields at the attempt boundary) rides the P-08 ratification + batched re-run.

## Re-run

```
cd /Users/anayvaidya/Wyzantium/Ferrier
sim/.venv/bin/python studies/R01_PHASE1_REVIEW/probes/probe_f004.py
```

Exit 0 = confirmed; rewrites `result.json` here (byte-identical across runs —
verified twice at `0c76b52`).
