# Tier-3 replay artifacts — pre-swap (`prior_v1`), SIMULATED

A-007 deliverable: one replayable artifact per failure class observed in the
`freeze-prior-v1` dataset (success, IS8-1, IS8-2, IS8-3), rendered from
logged trial state only (D-007: no imagery) by `wyzantium_sim.replay`.

Every GIF carries its trial_id; every sidecar JSON maps artifact → trial
record (seed, code SHA). The records themselves regenerate deterministically
from the committed plans and seed rule — these four were regenerated locally
from the frozen plans (`tiers.tier1_plan/tier2_plan(20260808)`) at a
doc-only descendant of the freeze SHA `b493e7a`; the sidecars carry the
exact stamp. Pre-swap labeled: this set is regenerated under `mr_v1` after
the P-03 measurement window, and both sets are kept (ROADMAP protocol).

To re-render any of these:
`sim/.venv/bin/python -m wyzantium_sim.replay render <record> --out <dir>`
