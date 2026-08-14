# SWAP REHEARSAL — **SYNTHETIC DATA, NOT BENCH RESULTS**

Every number in this directory was produced from **synthetic CSVs**
generated out of `sim/tests/test_mr_ingest.py`'s ground-truth constants by
`tools/swap_mr_v1.py --rehearse` (2026-08-14, item 2 of the pre-window
work). Nothing here is a measurement, and nothing here feeds any
committed result. The point was to run the mr_v1 swap path end-to-end —
fit → register → seed-paired re-run through the multiprocess runner →
before/after report → pooling-guard check — before the real P-03 CSVs
exist, so the real swap session is one command with zero surprises.

Full narrative + the real-swap runbook: `studies/SWAP_REHEARSAL.md`.

Contents: `mr_v1_curveset.json` + `mr_fit_report.json` (the fitted
synthetic set; recovery vs ground truth asserted in-run),
`before_after.json` (both sides, per plan, Wilson CIs),
`*_{prior_v1,mr_v1}.sha256` (record hashes; a second run reproduced all
six lists byte-identically), `guard_demo.json` (MixedCurveSetsError fired
on a deliberately mixed directory), `synthetic_csvs/` (inputs, labeled in
their header comment).

Records themselves are hashed and freed (freeze discipline) —
regeneration: `tools/swap_mr_v1.py --rehearse --out <dir>`.
