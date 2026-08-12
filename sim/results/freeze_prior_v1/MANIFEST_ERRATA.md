# MANIFEST.json errata (sidecar — frozen bytes untouched)

Per the R01 review's Class E disposition (studies/R01_PHASE1_REVIEW/FINDINGS.md
F-002): the frozen manifest is the record of record, so corrections are made
here, never by editing its bytes.

## E-1 (2026-08-11, R01 F-002) — `records_storage` regeneration-cost figure mangled

**The committed text ends:** `"…Regeneration cost at the committed A-004 rate:
~/bin/zsh.13."`

**Mechanism:** the manifest was written through an unquoted zsh heredoc; the
intended text `~$0.13.` had its `$0` expanded to the shell path (`/bin/zsh`)
at write time.

**Corrected figure, recovered from committed sources** (independently
reproduced by two review agents): 13,400 trials × $0.009502167853532263 per
1,000 trials (`sim/results/a004/c7i.8xlarge-spot-us-east-1c.json`) =
**$0.1273 — the intended text was "~$0.13."** Cross-checked against
`sim/results/spend_ledger.json`: $0.2476 total = 12,800 pre-freeze trials at
the first-committed $0.0094/1k + 13,400 freeze trials at the freeze-time
$0.009502/1k (exact).

## E-2 (2026-08-11, R01 F-018/S-10) — regeneration-verification scope

The manifest's regeneration instruction verifies **only on the freeze
instance class** (c7i.8xlarge, linux/x86-64): regenerating on darwin/arm64
(M4) reproduces trial_ids but not byte-identical records — genuine
cross-platform float divergence, surviving a code_git_sha rewrite (probe:
`sim/results/review_r01/F-018/`, pending re-run; first measurement 5/5
mismatch). Byte-identity is a per-instance-class contract; an auditor off
that platform should verify trial_id reproduction and on-platform digests,
not cross-platform sha equality. The structural fix (instance identity in
`trial_header`) is R01 F-017, queued for ratification at P-08.
