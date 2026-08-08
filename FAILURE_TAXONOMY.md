# Failure Taxonomy — Phase 1 Classification Reference

Expands `INTERFACE_SPEC.md` §8 into classifiable events. Phase 1 classifies every
failed trial against exactly one IS8 row (outcome string `IS8-<row>`, WIRE_FORMAT
trial_result); unclassifiable failures extend §8 by recorded amendment first.
**Frequency class is an a-priori guess, labeled as such — Phase 1's measured
distribution replaces this column and the delta is itself a finding.** "Recoverable"
= can the D-005 retry loop plausibly convert it; D-014's framing means a taxonomy that
tells a cofounder what to fix is worth as much as the success number.

| IS8 | Failure | Wire-format detection signature | Freq class (a-priori guess) | D-005 recoverable? | If it dominates, design implication |
|---|---|---|---|---|---|
| 1 | Outer tag partial occlusion | `tags` sparse for ID 0, `reproj_err`↑, `degradation.occlusion_est`↑, conf sag in `outer_servo` | Common | Yes — reacquire/hold | Bigger outer tag or second outer scale; active illumination earlier |
| 2 | Outer tag destroyed | No ID-0 across approach; mission context positive | Rare | No | Redundant outer tag on second face; non-tag coarse acquisition cue |
| 3 | Inner ring occluded below 2 tags | <2 inner IDs inside 300 mm → commit rule unsatisfiable; abort_reason `inner_ring_absent` | Common (ring is at the mud line) | Yes — back out, reapproach | **The headline mechanical finding**: relocate/raise ring (collar), add wiper/air-knife, or active illumination — hand to cofounder |
| 4 | Inner ring destroyed | Outer pose OK; zero inner detections at handoff | Occasional | No | Ring armor/recessing; sacrificial cover |
| 5 | Pose ambiguity flip | `ambiguity_flag` true / `ambiguity_ratio`→1; Cam A/B disagreement | Occasional (concentrated near head-on; studies/H08) | Yes — reject frames, oblique confirm | Collar layout (structural fix); enforce approach obliquity |
| 6 | Stud bent | Vision nominal; contact wrench profile inconsistent with funnel model | Rare | Sometimes — offset retry may still latch | Stud material/section upsize (D-003-R basis); bend-detect from wrench signature |
| 7 | Stud sheared/missing | Inner pose OK; no contact at expected depth | Rare | No | Target-side robustness; pre-attempt visual stud check (Phase 3 CV) |
| 8 | Plate detached/shifted | Inter-tag transform residuals violate §3.5 calibration | Rare | No | Mount redundancy; constellation self-check is already the detector |
| 9 | Funnel packed with debris | Insertion force spike, no latch confirm, wrench profile blunt | Occasional | Yes — back-out may clear | Funnel geometry sheds mud; wash port; (serviceable side, D-001) |
| 10 | Latch fails to engage | Full stroke, no confirm | Occasional | Yes | Latch redesign — the single point of failure earning its scrutiny (D-003-R) |
| 11 | Latch engages, no lock | Confirm intermittent | Rare | Yes — re-seat | Lock sensing + mechanism margin |
| 12 | Latch will not release | Post-tow release fails | Rare | n/a (post-mission) | Manual release on head (already required, D-001) |
| 13 | Host frame deformed | Plate skew beyond D-024 assumptions; contact/vision mismatch | Rare | No | Widen D-024 attitude envelope or add compliance travel |
| 14 | Wrong-ID decode | ID outside variant block (§3.4) | Rare | Yes (frame reject) | Family/ID scheme fine as-is unless measured otherwise |
| 15 | Comms loss mid-attempt | Link monitor only — wire stream unaffected | Common in DDIL | n/a — **not a failure** (REQ-005) | None; it is the operating condition |
| 16 | Lip strike | Contact wrench in lip band pre-capture-plane | Occasional | Yes — offset retry (D-005's designed case) | Mouth diameter / wall angle rebalance; **false-capture sub-path counted separately** |
| 17 | Jam at the throat | `sim_truth.contact_wrench`: axial > F_ax_jam, lateral < F_lat_jam, no latch confirm within t_jam; `abort_reason: jam_detected` | Occasional (a-priori guess — this class exists precisely because it was invisible) | Yes — back-out is the designed unjam; repeated jams exhaust the attempt budget | **The D-027 escalation observable: if IS8-17 dominates, promote T5's RCC geometry.** Note T4a deflection sensing is blind to this failure (symmetric jam ⇒ near-zero net deflection) — the fallbacks are not interchangeable |

**Reading the table the way a cofounder would:** rows 3, 9, 10, 16 are the mechanical
design agenda; rows 1, 5 are the perception agenda; rows 2, 4, 6, 7, 8, 13 are
target-side robustness — cheap steel, but every gram is adoption cost (§1.7, D-001).

## Classifier precedence (Phase 1, authored 2026-08-08, T9)

The documented precedence order D-030 mandates. `sim/wyzantium_sim/classify/
outcomes.py` transcribes this list row-for-row (test-enforced,
`test_outcomes.py::TestDocTranscription`); first match wins, so every trial
gets exactly one outcome. A trace matching no row raises
`UnclassifiedFailure` — §8 is extended by recorded amendment, never a guess
(D-030, WIRE_FORMAT).

1. **IS8-16** — any lip-band contact pre-capture-plane. IS §8 row 16: its
   own outcome class, never capture or clean miss — it outranks even a
   latch. `false_capture` = a striking leg's own latch (H-16); a later
   recovered latch still scores IS8-16 (the strike happened; the record
   shows the recovery), which biases the gate number conservative, the
   D-006 direction.
2. **IS8-11** — latch confirm intermittent. Post-engagement discovery; must
   precede `success` or it is unreachable. Before IS8-12 because no-lock
   forbids tow, so release is never exercised. *No Phase 1 producer.*
3. **IS8-12** — post-tow release fails. Post-mission discovery on an
   otherwise-good latch; must precede `success` or unreachable. *No
   Phase 1 producer.*
4. **success** — any D-020 latch within the attempt budget (D-022; t ≤ T is
   structural — the trial loop never runs past budget). Above the
   remaining failure rows so a retry that recovers is a success (D-005).
5. **IS8-17** — jam: the committed #62 force/time criterion fired. Never
   folded into generic insertion failure (IS §8 row 17); before IS8-10 so
   a jam at depth is a jam, not "no confirm".
6. **IS8-13** — plate skew beyond D-024. Contact-anomaly block ordered
   global→local: a deformed host frame explains every residual downstream.
   *No Phase 1 producer.*
7. **IS8-8** — constellation residuals violate §3.5. Global plate fault
   before local wrench interpretation. *No Phase 1 producer.*
8. **IS8-6** — wrench profile inconsistent with the funnel model. *No
   Phase 1 producer.*
9. **IS8-9** — insertion force spike, blunt profile, no confirm. The most
   local contact anomaly. *No Phase 1 producer.*
10. **IS8-7** — no contact at expected depth. Absence-of-evidence
    signature, checked after every presence-of-evidence contact row. *No
    Phase 1 producer.*
11. **IS8-10** — full stroke, no confirm: the residual contact failure once
    lip/jam/anomaly explanations are exhausted. Requires the runner's
    full_stroke observable — mere contact is not a stroke (the interim
    map's guess, retired here).
12. **IS8-2** — zero ID-0 detections across the whole approach with the
    low-confidence shape (escalation, refusal, or last abort). Total outer
    loss outranks partial degradation (row 1).
13. **IS8-4** — terminal escalation `inner_ring_absent`: outer pose OK,
    zero inner at handoff (guidance's row-4 escalate shape).
14. **IS8-14** — persistent out-of-block ID decode (§3.4). Frame-integrity
    fault; would corrupt the statistics rows 5/3/1 read. *No Phase 1
    producer.*
15. **IS8-5** — ambiguity: terminal `ambiguity_persistent` escalation, or
    budget exhaustion whose proximate (last) abort was ambiguity.
16. **IS8-3** — budget exhaustion whose proximate abort was
    `inner_ring_absent` (the back-out/reapproach cycle that never
    satisfied the ≥2-tag commit rule).
17. **IS8-1** — outer degradation: `low_confidence` escalation, any gate
    refusal, or last abort low-confidence. D-030's rule: the refusal path
    classifies here, never clean_miss.
18. **clean_miss** — the D-030 residual, all four clauses: fails D-022
    (rows 1–4 unmatched); no contact ever; every attempt either missed at
    r > 160 mm / never crossed, or was truncated by the budget
    mid-approach with a nominal stream (no aborts, no refusals); no §8
    signature matched (holds by position). Anything else **raises
    `UnclassifiedFailure`**.

**IS8-15 (comms loss) is not a classifier output.** Three specs agree it is
nominal, not a failure (IS §8 row 15 / REQ-005; row 15 above; D-030). It
has no trace representation — the link monitor is out-of-band and the wire
stream is unaffected — so a comms-lost trial classifies by its underlying
attempt outcome. `IS8-15` stays in the wire enum (`validator.OUTCOMES`, the
`trial_result` schema, #57) for schema stability; the table deliberately
has no row for it (test-enforced: output set = OUTCOMES − {IS8-15}).

*Rows marked "no Phase 1 producer" have committed signatures and trace
fields but nothing in today's sim sets them (no fault injection, wrench
profiling, constellation check, ID-block check, or post-tow model); they
exist so the table is total and the order is committed before the
producers arrive.*
