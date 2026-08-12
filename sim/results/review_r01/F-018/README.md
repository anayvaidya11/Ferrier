# F-018 probe — cross-platform regeneration divergence

Run: `sim/.venv/bin/python studies/R01_PHASE1_REVIEW/probes/probe_f018.py`
(regenerates 5 tier1 + 2 gate frozen trials on the M4; 3 arms per trial).

**Load-bearing numbers (all 7/7):** trial_ids resolve in the committed
lists; raw sha256 mismatch; **mismatch survives code_git_sha
normalization** (record BODY diverges — per-frame float drift,
darwin/arm64 vs the freeze's c7i.8xlarge/ubuntu); local double
regeneration byte-identical (determinism holds per instance class).

**Note on the script's verdict field:** result.json says REFUTED because
the probe's conservative code-freeze-integrity gate requires the sim tree
byte-identical to the freeze SHA, and two additive post-freeze files
exist (perception/mr_ingest.py + tests/test_mr_ingest.py — imported
nowhere in the trial path, verified by two independent review agents).
The finding's substance — the committed verification recipe fails off the
freeze platform while same-platform determinism holds — is CONFIRMED by
the four 7/7 criteria above. Artifact left byte-exact as the script wrote
it; this README records the interpretation (FINDINGS.md F-018).
