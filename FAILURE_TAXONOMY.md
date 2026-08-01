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

**Reading the table the way a cofounder would:** rows 3, 9, 10, 16 are the mechanical
design agenda; rows 1, 5 are the perception agenda; rows 2, 4, 6, 7, 8, 13 are
target-side robustness — cheap steel, but every gram is adoption cost (§1.7, D-001).
