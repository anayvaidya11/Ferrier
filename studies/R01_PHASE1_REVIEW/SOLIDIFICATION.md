# R01 Metric Solidification Sweep (Lane F2)

Not violations — opportunities to make the numbers harder. Dispositions:
DONE (computation-only, landed pre-REPORT) / RE-RUN (folds into the batched
freeze_prior_v2 run) / RECORDED (caveat documented, no computation) /
DECLINED (with reason).

| # | Item | Disposition | Evidence |
|---|---|---|---|
| S-01 | Gate-cell CI method named + committed — freeze states "0.0% (N=5,000, CI [0, 0.08%])": Clopper-Pearson one-sided? rule-of-three gives 0.06%; Wilson differs. Reconcile with D-038's Wilson-based sizing | | |
| S-02 | Per-cell N adequacy vs cell-level pass/fail language in tier1 summary; disclose absence of multiplicity correction across axis×level cells or add one | | |
| S-03 | #33 convergence statistic audited at a 0-success refusal-dominated cell — convergence *of what* (success rate degenerate at 0; refusal rate? outcome census?); verify probe artifacts cover the frozen configuration | | |
| S-04 | Seed/substream discipline: D-032 seed rule vs rng.py spawn; substream reuse across attempts within a trial; spawn-key stability across kill/resume at the frozen plans' resume points | | |
| S-05 | Pooling guard extended to (curve_set, code_git_sha) pairs BEFORE prior_v2/mr_v1 exist, so cross-freeze pooling is mechanically impossible | | |
| S-06 | Refusal-vs-failure census emitted alongside the headline rate (success / refusal-escalation / damage-class split); reconcile D-029 gate wording with D-017 refusal-is-a-deliverable framing | | |
| S-07 | #63 pinned cross-check reproduced with numeric tolerance stated, not implied ((0.2, 300 kg) → k_max ≈ 17 N/mm → {30, 70} masked infeasible) | | |
| S-08 | D-014/D-017 curve JSONs carry per-point N and binomial CIs; charts render them | | |
| S-09 | Spend-ledger cross-foot vs A-004 committed $/1k × realized counts (simultaneously recovers the manifest's mangled dollar figure for F-002) | | |
| S-10 | Determinism scope recorded: byte-identical regeneration claimed from the manifest — instance-class/BLAS caveat (M4 vs c7i.8xlarge float identity) documented or cross-platform verification artifact committed | | |
