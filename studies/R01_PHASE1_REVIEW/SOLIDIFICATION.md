# R01 Metric Solidification Sweep (Lane F2) — dispositions 2026-08-11

Dispositions: DONE (verified/computed, land in REPORT) / CODE (analysis-layer
change, joins the Class M batch — no record bytes touched) / RECORDED (caveat
documented) / RE-RUN (folds into batched freeze_prior_v2).

| # | Item | Disposition | Evidence |
|---|---|---|---|
| S-01 | Gate-cell CI method | **DONE** | Freeze CI [0, 0.000768] matches **Wilson 95%** to the last digit (venv-computed); tier1 (3926/4400) and tier2 (26/4000) intervals also Wilson exact. CP two-sided 7.38e-4, CP one-sided 5.99e-4, rule-of-three 6.0e-4 all differ. REPORT names Wilson; reconciles with D-038's Wilson sizing. |
| S-02 | Per-cell N adequacy + multiplicity | **DONE** (disclose) | Tier-1 cells n=50 → worst-case Wilson half-width ~13.9 pp: fine for curve shape, not cell-level pass/fail reads. Summary JSON emits raw rates, no CIs, no multiplicity note across ~88 cells → REPORT discloses both. |
| S-03 | #33 convergence at refusal-dominated cell | **RECORDED** (+ candidate RE-RUN) | Gate probe covers frozen timestep but both arms score 0.0 — the success-rate delta is degenerate (0−0 < 1 pp halts vacuously). Convergence of the operative statistic (refusal census) unverified; re-probe on census recommended with the v2 run. |
| S-04 | Seed/substream + kill/resume | **DONE** | Seed rule (digest[:8]>>1) matches D-032(b), pure in (root, tag) → resume-stable; kill/resume byte-identity test proves end-to-end; substreams crc32-keyed order-independent. Retry-noise realization stays the labeled D-037 residual limitation. |
| S-05 | Pooling guard → (curve_set, code_git_sha) | **CODE** | Guard keys on curve_set only (dataset.py:55–59); TrialRow doesn't even load code_git_sha — pre/post-fix prior_v1 records would pool silently. Extend key before v2/mr_v1 exist. |
| S-06 | Refusal-vs-failure census | **DONE** | Gate cell 5,000 = 4,997 IS8-1 + 3 IS8-3 → success 0.0% / refusal 100.0% / damage 0.0%, zero false captures. The D-029 number is entirely policy refusal — headline framing for REPORT + D-017 tie-in. |
| S-07 | #63 pinned cross-check tolerance | **DONE** | test_analysis asserts k_max ≈ 16.82 abs=0.02, masks {30,70} False; feasibility_63.json carries 16.8171. Stated, not implied. |
| S-08 | Per-point N + CIs on curves | **DONE**/**CODE** (deferred to fix batch) | d014 charts render Wilson bands; committed index.json lacks per-point JSON; D-017 ThresholdStat has no CI fields → emit per-point JSON + D-017 CIs. Deferred from the M batch to the ratified-fix batch (2026-08-11): analysis outputs regenerate at freeze_prior_v2 anyway — doing it there avoids a double regeneration. |
| S-09 | Spend-ledger cross-foot | **DONE** | $0.2476 = 12,800 pre-freeze × $0.0094/1k + 13,400 × $0.009502/1k — exact. Recovers F-002's corrected figure: 13,400 × $0.009502/1k = **$0.1273** ("~$0.13."). |
| S-10 | Determinism scope | **RECORDED** | M4 regeneration of a frozen trial mismatches committed sha256 (F-018): header SHA drift + genuine cross-platform float divergence. Caveat: byte-identity is per-instance-class; verification recipe must say so. F-017's instance field is the structural fix. |

Cross-lane note (F2→G): `tier1_prior_v1_summary.json` / `tier2_prior_v1_summary.json`
carry no source/code-sha provenance and differ from the freeze (pre-freeze H-18
evidence snapshots) — label as historical evidence when REPORT cites them.
