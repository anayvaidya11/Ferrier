# F-017 L2 probe — trial_header carries no compute-instance identity

**Verdict: CONFIRMED** (Class B/med; additive schema revision, joins the
batched re-freeze per FINDINGS.md). Probe:
`studies/R01_PHASE1_REVIEW/probes/probe_f017.py`.

## Clause

- **ARCHITECTURE.md §5** (A-004 compute plan): "both measurements are
  committed alongside the trial records (**engine and instance identity land
  in every `trial_header`**)."
- **PHASE1_PLAN.md §2**, wirefmt row: "trial_header (incl. #33 solver block +
  **compute-instance identity**)".

## Expectation per doc

Every trial_header names both the physics engine that produced it **and** the
compute instance it ran on. Two identities, one sentence, one commitment.

## Method

Regenerate one committed-nominal trial (seed **101**, sweep point verbatim
from `sim/scenarios/nominal.json`, local MuJoCo, code freeze respected — the
entire header path `trial.py` + `wirefmt/` is byte-identical to freeze SHA
`b493e7a`). Then check **each half of the ARCH §5 sentence at all four layers
of the wire contract**, side by side:

| Layer | instance identity (FAILING arm) | engine identity (CONTROL arm) |
|---|---|---|
| Produced header (seed 101) | absent — key set is exactly `{v, type, trial_id, seed, code_git_sha, engine, sweep_point, params_ref, solver}` | present: `{"name": "mujoco", "version": "3.11.0"}` |
| `trial_header.v1.schema.json` | no property matches any instance token (`instance/host/machine/platform/node/...`) in properties or required | `engine` required, sub-schema requires `{name, version}` |
| Canonical writer order (`records.CANONICAL_ORDER`) | no instance field | `engine` in documented order |
| Validator (`_validate_trial_header`) | no instance token in the check source; header **as written validates clean** (`[]`) | deleting `engine` from the same header fails: `"engine must be {name, version}"` |

Token scan is word-bounded (so `isinstance(` in validator source cannot
false-positive) and runs against schema property/required keys, the canonical
order list, and the validator function source only.

## Observed

- FAILING arm: instance identity absent at **all four layers**; the validator
  happily accepts a header that cannot name its producing machine
  (`validate_line` → `[]`).
- CONTROL arm: engine identity present at all four layers **and enforced**
  (removal → validation error).

One noun of the ARCH §5 sentence landed through the whole stack; the other
never entered it — WIRE_FORMAT.md's header spec itself (lines 99–104) already
omits it, so the miss propagated doc → schema → writer → validator. The probe
ran on `Darwin/arm64`, an identity with nowhere to land in the record it
produced — exactly the gap that compounds F-018 (cross-platform sha256
divergence with no field to say which instance class produced the frozen
bytes).

Numbers: `result.json`. The regenerated header itself: `trial_header.json`
(trial_id `mujoco-101-5f428a24`).

## How to re-run

```sh
cd /Users/anayvaidya/Wyzantium/Ferrier
sim/.venv/bin/python studies/R01_PHASE1_REVIEW/probes/probe_f017.py
```

Deterministic (fixed seed, no wall clock): a re-run reproduces `result.json`
byte-for-byte, including the trial_id. Exit 0 = CONFIRMED, exit 1 = REFUTED.
Seconds on the M4; zero cloud spend. `code_git_sha` in the header will track
your HEAD (and `-dirty` state) — the key-set assertion is SHA-independent.
