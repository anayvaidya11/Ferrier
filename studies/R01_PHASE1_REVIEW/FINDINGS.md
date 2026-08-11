# R01 Findings Ledger

Every finding is an F-NNN entry with ALL mandatory fields; a finding missing
any field is L0 by definition. Statuses: DRAFT (L0) → VERIFIED (L1) →
CONFIRMED (L2) → triaged {M, B, E, S, T} → RESOLVED (with evidence path) |
REJECTED (kill recorded) | RECLASSIFIED.

Template:

```
## F-NNN — <title>
- **Clause violated:** <verbatim quote ≤2 lines> (<doc §anchor>)
- **Observed:** <code_ref @ cdf7fbf> — <what the code actually does>
- **Failure scenario:** <specific sweep point / stream pattern → expected-per-doc vs actual>
- **Probe:** sim/results/review_r01/F-NNN/ | "not required (class M/E/S/T)"
- **Class:** M | B | E | S | T   **Status:** DRAFT | VERIFIED | CONFIRMED | ...
- **Prosecution:** <kill attempts and why they failed, or the kill that landed>
- **Disposition:** <fix path / PENDING_HUMAN P-08 item / erratum path>
```

Seed findings (from planning-phase inspection, pre-lane; lanes verify or kill):

## F-001 — REPORT stub header states "No simulation exists yet"
- **Clause violated:** "If the repository and a published claim disagree, the repository is right" (MASTER_CONTEXT §4.3); the stub line is itself now a false repo statement
- **Observed:** sim/REPORT.md:1 @ cdf7fbf — "STUB — Phase 1 deliverable. Not yet written. No simulation exists yet." 13,400 frozen trials exist.
- **Failure scenario:** any reader (incl. the P-05-style review packet flow) takes the stub line at face value → false status
- **Probe:** not required
- **Class:** M  **Status:** VERIFIED (self-evident from repo state)
- **Prosecution:** pending lane G pass
- **Disposition:** stub line correction in the Class M batch (full REPORT is T13, post-swap)

## F-002 — freeze MANIFEST.json regeneration-cost field mangled by shell expansion
- **Clause violated:** manifest provenance accuracy (A-007 / ARCH §6.4 committed-dataset discipline)
- **Observed:** sim/results/freeze_prior_v1/MANIFEST.json:18 — "…at the committed A-004 rate: ~/bin/zsh.13." (unquoted heredoc expanded `$0`)
- **Failure scenario:** auditor reads the frozen manifest → nonsense provenance field in the record of record
- **Probe:** not required
- **Class:** E  **Status:** VERIFIED
- **Prosecution:** pending lane G pass
- **Disposition:** MANIFEST_ERRATA.md sidecar (frozen bytes untouched); corrected figure recovered from sim/results/a004/ + spend_ledger.json

## F-003 — kinematic/stage.py:19 "pose_cov placeholder until T6" comment vs T6 done
- **Clause violated:** TBD by lane D — either a stale comment (M) or a real zero-covariance feed into the D-013/D-017 gate (B)
- **Observed:** sim/wyzantium_sim/kinematic/stage.py:19 @ cdf7fbf
- **Failure scenario:** if real: gate consumes zeroed pose_cov → confidence semantics diverge from WIRE_FORMAT omitted-not-zeroed rule
- **Probe:** required if lane D reads it as behavioral
- **Class:** TBD  **Status:** DRAFT
- **Prosecution:** —
- **Disposition:** —
