# Pending Human Actions

Single ledger of everything owed by the human, so nothing is scattered. Dated when
added; struck through when done.

| # | Action | Needed by | Context |
|---|---|---|---|
| ~~P-01~~ | ~~Ratify the funnel compliance topology (H-04)~~ **DONE 2026-08-02 — T1 ratified as D-027**, with revised R4, refined k bounds, and the IS8-17 jam class | — | studies/H04 header + Addendum |
| ~~P-02~~ | ~~Set the cloud dollar ceiling for Phase 1 compute~~ **DONE 2026-08-02 — $100 hard ceiling ratified by the human** (recorded answer, planning session); expected spend $20–60; exceeding it requires a recorded amendment, not a quiet overrun (A-011) | — | A-004 test decides CPU vs GPU by measured cost; the DOE runner meters cumulative spend against the ceiling |
| P-03 | **Approve MR-001 / MR-002 / MR-003 procedures and purchase instruments** — procedures are now execution-ready; total human time budgeted at the 3-working-day bound | late August measurement window | `MEASUREMENT_REQUESTS.md`; NO_HARDWARE rev 2 three-question test answered per item |
| P-04 | **ASSIST registration** (https://assist.dla.mil) and retrieval of MIL-PRF-32383/7 (STUB slash sheet) | Phase 2 latest | Top UNVERIFIED item from `research/STANDARDS.md` |
| ~~P-05~~ | ~~Phase 0 gate sign-off~~ **DONE 2026-08-02 — signed by the human** (recorded answer, planning session), after the H-13..H-16 post-assessment closures. **Phase 0 is formally closed; the Phase 1 build is open** (A-011). Review packet kept below for reference | — | `HOLES.md` read 0 open (sixteen holes, all doors named); `PHASE1_PARAMETERS.md` 65/65 at signature |
| P-06 | **Obtain Whitney 1982 full text** (ASME JDSMC 104(1):65–77, DOI 10.1115/1.3149634) — any university library proxy with ASME access, or one email to anyone with .edu credentials | before any T5-promotion argument (Phase 1/2) | Currently cited by verified metadata/abstract only. If IS8-17 jamming promotes T5, this paper becomes the foundation of the anti-jamming argument and metadata won't carry it. **On completion, strike the paywall caveat in CLAIMS C-12, INTERFACE_SPEC §2.3, and studies/H04 A4-note** |
| P-07 | **Obtain Kallwies/Forkel/Wuensche ICRA 2020 full text** (DOI 10.1109/ICRA40945.2020.9197427) — same .edu route, IEEE Xplore | when convenient; strengthens #40 | The only paper quantifying AprilTag corner-localization accuracy; its absence is why pose covariance is a swept class value instead of a literature anchor (`perception_prior.md` UNVERIFIED — eight retrieval routes tried and failed) |

*Note: the hole-closure prompt's Part E-5 asked for a "rename repo to recovery-stack"
action here. That premise conflicts with committed A-001 (§2.5 says the repository IS
`anayvaidya11/Ferrier`, by explicit prior decision), so per the documents-win rule the
action was not added — recorded in the session report.*

---

## P-05 review packet (~45 minutes)

What to read before signing, in order. The signature asserts one sentence: *"The
interface spec is precise enough that Phase 1 builds directly against it with no
further design decisions"* (the MASTER_CONTEXT Phase 0 gate condition).

1. **`HOLES.md`** (~10 min) — the whole ledger. Check that every hole names its door
   and that no closure reads like invention. Pay attention to the post-assessment
   section (H-13..H-16): the self-assessment passed and then planning found four more;
   the two new decisions below are what closed the substantive ones.
2. **`DECISIONS.md` D-029 and D-030** (~10 min) — the only *new* decisions since the
   self-assessment. D-029 defines "moderate degradation" — the cell your kill-gate
   number is computed over. **This is the most consequential thing you are signing**:
   if the band feels wrong (too easy, too harsh), say so now, not after 10,000 trials.
   D-030 defines `clean_miss`.
3. **`PHASE1_PARAMETERS.md`** (~15 min) — read the header, then spot-check any five
   rows: follow each row's Source column to the committed document and confirm the
   value is actually there. The gate claim is that all 65 rows survive this check.
4. **`ROADMAP.md` Phase 0 §Week 2 + `studies/H04` header and Addendum** (~10 min) —
   confirm the T1 ratification you made (D-027) is recorded the way you meant it.

**To sign:** say so in a session (it gets recorded here with the date), or commit an
edit striking P-05 yourself. On signature: Phase 0 closes, Phase 1 build opens
(`PHASE1_PLAN.md`).
