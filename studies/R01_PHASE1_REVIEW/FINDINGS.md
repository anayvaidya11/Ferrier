# R01 Findings Ledger

Review executed 2026-08-11: 8 lanes + adversarial prosecution, 16 agents,
225/225 matrix rows verdicted (see MATRIX.csv; raw lane output in
raw_lanes.json). 25 lane findings → 24 ADVANCED, 1 RECLASSIFIED, 0 REJECTED;
duplicates merged below (σ_px found independently by lanes B, F1, F2). Every
ADVANCE ruling includes independent prosecutor reproduction or concurrence at
HEAD — the L1 bar. Class B findings additionally need the L2 probe artifact
in `sim/results/review_r01/F-NNN/` before the P-08 ratification sitting.

**Statuses:** DRAFT (L0) → VERIFIED (L1) → CONFIRMED (L2) → triaged
{M,B,E,S,T} → RESOLVED | REJECTED | RECLASSIFIED.

## Resolution — P-08 ratified 2026-08-11 ("I ratify P-08"), fixes applied

Before = each finding's committed probe artifact; after =
`sim/results/review_r01/F-0NN/after_fix.json` (probes/after_fix_r01.py, all
8 arms passing). **freeze_prior_v2 landed 2026-08-12** (13,900 trials at
`f6325bd`, c7i.8xlarge, $0.132 metered): every row below is **RESOLVED**.
Gate cell restated pre-swap: 0/5,000 — still 100% policy refusal, but the
composition validates the fixes (4,964 IS8-1 + 36 IS8-5 ambiguity refusals
now that D-043 flip realism exists; the D-042 attempt-seam IS8-3 artifacts
are gone). Tier-1 88.0% [87.1, 88.9] over the widened 98-cell pool. The
honest lever on the gate number remains the P-03 measurement window.

| Finding | Decision | Fix | After-arm |
|---|---|---|---|
| F-012 | D-041 | Q_NOMINAL = Rz(180°) | q=(0,0,0,1); tag z +0.185; view 6.1° |
| F-004 | D-042 | machine.begin_attempt() at attempt boundaries | fresh walls: gap→reject_frame, blip→hold |
| F-007/F-008 | D-043 | per-tag decode extent; visible-span flip/noise | lone-tag flag rate >0.5; 0 inner detections at 2.9 m |
| F-005 | D-044 | gate ambiguity conjunct + trial honors machine reject | flagged frame refused ("D-044"), control commits |
| F-016 | D-045 | arrival-time consumption + staleness bound | dropout cell: t_total differs across latency arms |
| F-009 | D-046(a) | σ_px joins SWEEP_AXES + Tier-1 grid | lands with the D-046 batch (Wave 2) |
| F-017 | D-046(f) | instance identity in trial_header | lands with the D-046 batch (Wave 2) |
| F-018 | — | erratum (E-2) + D-046(f) structural fix | per-instance-class contract recorded |
| F-013/F-014 | D-046(d) | recorded exclusions | no realization; written down |
| #62 pin | D-040/D-046(e) | grid stands; pin recorded | REPORT documents semantics |
| H-17 | D-046(b) | host tilt through truth/sightings/handoff/contact | test_host_tilt_composes_into_truth_orientation |

## Class B — behavioral (ratification + batched re-run required)

## F-004 — Guidance wall timers persist across D-005 retry attempts [A; B/high; **CONFIRMED** — probe: attempt 2 aborts at 0.000 s vs 5.033 s fresh-machine control, 4/4 variants; sim/results/review_r01/F-004]
- **Clause:** D-034 "any detection resets the window; single blips are held frames, not aborts"; D-036 ring absence is *sustained time*
- **Observed:** `_hold_since`/`_ring_absent_since`/`_ambiguity_streak` initialized only in `__init__`, never reset at attempt boundaries; `trial.py:181` resets only `machine.stage`. A fresh attempt's first gap frame inherits the previous attempt's open window.
- **Failure scenario:** gate cell, attempts=3: attempt 2's first <2-inner frame at ≤300 mm instantly aborts `inner_ring_absent` without 5 s of absence in that approach; a single dark blip instantly escalates.
- **Prosecution:** ADVANCE — both seams reproduced at HEAD with fresh-machine controls.
- **Probe:** required — F-004 dir; machine-level repro + isolation at gate_moderate, N=50, fixed seeds.

## F-005 — Ambiguity-rejected frames still serve as commit evidence [A; B/med; VERIFIED — probe deferred to fix-time per LANES protocol amendment 2026-08-11; static trace: gate.py has no ambiguity reference, machine rejects, trial latches from gate alone]
- **Clause:** IS §8 row 5 "Reject frame; require multi-tag or oblique confirmation"; WIRE_FORMAT checklist 5 + worked flip example
- **Observed:** `trial.py:206` latches `commit_line` from `gate.commit_allowed()` alone, ignoring the machine's `reject_frame`; `gate.py:44–74` never reads `tags[].ambiguity_flag`.
- **Failure scenario:** flip_kappa=2 coplanar: a flagged frame (ratio 0.92, conf 0.87) is machine-rejected per row 5 yet authorizes insertion; bites hardest at D-017's low conf_min arms.
- **Prosecution:** ADVANCE — reproduced at HEAD (gate returns (True,'commit') on the same line the machine rejects).
- **Probe:** required — instrumented run logging gate-passes where ambiguity_flag=True ∧ machine rejected.

## F-007 — Lone/sparse inner-tag frames use the full 110 mm constellation span for flip discriminability [B; B/high; **CONFIRMED** — probe: 0/1596 flags where H08 expects mean p_flip 0.166; per-tag-span control yields 238 flips vs 265±44.5 expected (3σ); sim/results/review_r01/F-007]
- **Clause:** D-011 qualification (lone 10 mm tag cannot self-disambiguate); H08 §2 (D from *visible* span) + §4; WIRE_FORMAT worked example (lone tag → ratio 1.08, flag true)
- **Observed:** `sightings_for()` hard-codes `span_m=0.11` for every inner tag regardless of visible count → lone tag 3 at 0.246 m/52°: D=139 px, p_flip=0, ratio=93 (flag False) where H08 expects flip-prone.
- **Failure scenario:** #46 knockout leaving one inner tag, or inner_occlusion ~0.8: flips and near-1 ratios expected per committed model; injected never.
- **Prosecution:** ADVANCE — reproduced (0/1397 frames flagged on a lone tag at 61°).
- **Probe:** required — knockout_mask=503, N=3000 frames, tag-span control.

## F-008 — Inner-tag decode pixel extent uses constellation span: 10 mm tags decode at 3 m [B; B/high; **CONFIRMED** — probe: 34.4 px (span convention) vs 3.1 px (per-tag) at 2.9 m; 1000/1000 frames multi_tag_fused with outer destroyed, 0 in control; sim/results/review_r01/F-008]
- **Clause:** IS §3.3 per-tag readability arithmetic (10 mm ⇒ 39 px at 300 mm); IS §3.2 20 px floor
- **Observed:** decode probability computed from 110 mm ring span → 33–34 px at 2.9 m where the true per-tag extent is ~3 px; knockout_mask=1 (outer destroyed) still yields full fused pose at acquisition range.
- **Failure scenario:** IS8-2's basis ("no ID-0 at expected range") coexists with a healthy pose stream; D-034 dark-window semantics bypassed in outer-destroyed cells.
- **Prosecution:** ADVANCE — reproduced (all 8 inner tags detected at 2.9 m).
- **Probe:** required — knockout_mask=1 at 2.9 m, N=1000 frames, both span conventions logged.

## F-009 — σ_px (#40) committed sweep {0.3, 0.5, 1.0} px unrealizable: pinned at default, no recorded exclusion [B+F1+F2 independently; B/med; VERIFIED — probe deferred to fix-time per LANES amendment; paired-seed pilots (78 trials, 4 cells) already show σ shifts conf monotonically (0.269→0.253→0.235 mid-cell) and flag rate +40% at σ=1.0]
- **Clause:** PHASE1_PARAMETERS #40; ARCH §3 pose-covariance row ("Swept σ_px {0.3, 0.5, 1.0} px stands in")
- **Observed:** `sigma_px` absent from `SWEEP_AXES` (build_sweep_point raises on it); absent from tier1/tier2 grids AND tier1's excluded block; `trial.py:144` pins `PARAMS[40].default`; trial.py's own docstring promises "a recorded amendment" that does not exist.
- **Failure scenario:** all 13,400 frozen trials ran σ_px=0.5; the #40 marginal feeding D-014/D-017 does not exist; an unrecorded H-17-style exclusion.
- **Prosecution:** ADVANCE ×3 — all kills fail; D-032(e) excludes only pitch/roll+curve_set.
- **Probe:** required (trivial) — SweepPointError repro + monkeypatched σ isolation run.

## F-012 — Q_NOMINAL realized as Ry(180°): head-up vs plate-up inverted in every trial [D; B/high; **CONFIRMED** — probe: 10/10 checks, N=50/arm; tag z −0.185 vs +0.185, view 37.7°/62.4° vs 6.1°/14.8°. Nuance: nominal-cell outcomes 50/50 success in BOTH arms — contamination concentrates in the degraded bands, i.e. the gate cell; sim/results/review_r01/F-012]
- **Clause:** IS §4 frame table (+Z head-up; +Z stud "plate up"; anti-parallel +X at engagement) + §7 level host attitude ⇒ nominal is Rz(180°)=(0,0,0,1)
- **Observed:** `Q_NOMINAL=(0,0,1,0)`=Ry(180°): X→−X *and Z→−Z* — outer tag renders at z=−185 mm in head_frame instead of +185. Cam A view angle at 300 mm: 37.7° realized vs 6.1° upright; at handoff 62.4° vs 14.8° — at the literature model's ~60° validity edge.
- **Failure scenario:** every frozen trial's outer-tag perception geometry is tilted ~4–48° worse than the committed nominal; detection rates, confidence, and therefore the refusal-dominated gate cell all inherit it.
- **Prosecution:** ADVANCE — prosecutor's independent venv probe reproduced all numbers exactly.
- **Probe:** required — monkeypatch arm A (frozen quat) vs arm B (Rz(180)), N=50 nominal trials each, local MuJoCo.

## F-016 — Staleness check unrealized; swept latency axis (#38) behaviorally inert [E; B/high; **CONFIRMED** — probe: latency_axis_inert_all_pairs true, control axis live; sim/results/review_r01/F-016]
- **Clause:** WIRE_FORMAT consumer checklist item 4 (staleness → treat as pose-absent)
- **Observed:** no consumer reads `t_emit` or holds a staleness bound; `perception_latency_ms` feeds `timing.emit_time` and nothing else — frames are consumed at capture time (`closed_loop.py:59–60`).
- **Failure scenario:** the frozen Tier-1 latency marginal {10,30,100} ms is fake-flat — the exact hazard D-032(e) excluded pitch/roll to avoid, yet latency stayed in tier1.json.
- **Prosecution:** ADVANCE — byte-diffs confined to t_emit fields across latency arms.
- **Probe:** required — latency 10 vs 100 ms pairs, assert outcome invariance (the inertness made mechanical).

## F-017 — trial_header carries no compute-instance identity [E; B/med; **CONFIRMED** — probe: identity absent at all 4 contract layers, engine present+enforced at all 4; sim/results/review_r01/F-017]
- **Clause:** ARCH §5 "engine and instance identity land in every trial_header"; PHASE1_PLAN §2 wirefmt row
- **Observed:** canonical header order has no instance field; schema defines none; validator checks none; trial.py writes none.
- **Failure scenario:** standalone records can't name their producing machine — compounding F-018's cross-platform divergence.
- **Prosecution:** ADVANCE. **Note:** additive schema revision (v1 additive, H-16 precedent) — behavioral only in record bytes; joins the batched re-freeze.
- **Probe:** required (trivial) — header key-set assertion.

## Class E — errata / recorded-clarification (no code behavior change)

## F-018 — Frozen-dataset regeneration diverges off the freeze platform: 5/5 sampled sha256 mismatch on M4 [E; E/high; **CONFIRMED** — probe: 7/7 raw mismatch, 7/7 after SHA normalization (body divergence), 7/7 local double-run deterministic. The script's own verdict field reads REFUTED only because its freeze-integrity gate trips on the two additive unimported post-freeze files — see F-018/README.md; sim/results/review_r01/F-018]
- **Clause:** WIRE_FORMAT bit-identical re-run contract; MANIFEST records_storage regeneration instruction
- **Observed:** first 5 tier1 trials regenerated on darwin/arm64 at the anchor tree: trial_ids match, all 5 hashes mismatch — and the mismatch survives rewriting code_git_sha (body float divergence, M4 vs c7i.8xlarge), on top of the header's embedded SHA drift (cdf7fbf vs b493e7a).
- **Prosecution:** ADVANCE — independently reproduced 2/2.
- **Disposition:** determinism is per-instance-class, not cross-platform. Erratum + MANIFEST clarification wording + S-10; F-017's instance field is the structural fix. Verification recipe must say "same instance class".

## F-010 — D-023 parenthetical "f_c = 1.0 degenerates to the literature mask model" is false [B; E/low; VERIFIED]
- At f_c=1.0, P=(1−f)·P_mask=(1−f)² under prior_v1 — the mask model squared. Code implements the normative product exactly; the doc parenthetical misleads. Dated in-place doc repair at ratification.

## F-013 — IS §5 "sweeps each contributor ×{0.5,1,2}": mount-tolerance contributor unrealized, no recorded exclusion [D; E/low; VERIFIED]
- Only the chassis allocation feeds D-019; tag table/funnel never perturbed. Needs recorded exclusion or realization (human's call at sitting).

## F-014 — D-019 "(correlation length 2 m, swept)" — sweep realized nowhere [D; E/low; VERIFIED]
- Constructor default only; absent from every grid and parameter row. Same disposition class as F-013.

## F-020 — A-004 GPU leg unmet at freeze [F2; E/low; VERIFIED]
- Already queued: P-08(a) D-039 waiver draft. Ledger row exists so the audit trail closes through the ratification.

## F-023 — ARCH §6.4 "results sufficient to re-run" vs records-not-retained: regeneration-closure wording gap [G; E/low; VERIFIED]
- Recommended: dated ARCH §6.4 clarification defining the committed deliverable as the regeneration closure (plans + seed rule + SHA + per-record sha256), with the F-018 instance-class caveat attached.

## F-002 — MANIFEST records_storage field mangled by $0 shell expansion [seed; E/med; **CONFIRMED by lane G**]
- Corrected figure recovered independently: 13,400 × $0.009502167853532263/1k = **$0.1273** ("~$0.13."), consistent with spend_ledger. Disposition: MANIFEST_ERRATA.md sidecar; frozen bytes untouched.

## Class M — mechanical batch (byte-identity proof required)

## F-001 — REPORT stub "No simulation exists yet" false at HEAD [seed; M/med; **CONFIRMED by lane G**] → stub line correction.
## F-003 — stage.py:19 "pose_cov placeholder until T6" comment [seed; M/low; **RESOLVED-ANALYSIS by lane D**]: HandoffState.pose_cov has zero consumers; trial.py:275–277 overwrites ZERO_COV with the commit frame's real cov before contact; wire pose_cov comes from the injector. Stale comment only.
## F-021 — IS §10 item 11 still declares funnel compliance unratified, contradicted by D-027 and IS §2.3's own "RATIFIED" header [G; M/med; RECLASSIFIED E→M by prosecutor] → dated §10 repair citing D-027.
## F-022 — Orphan "(D-003)" citations (ARCH:13; IS:37,41,357,358) point at the struck decision; content lives in D-003-R [G; M/low] → retarget citations.
## F-024 — Tier-3 sidecars' source_record fields point at dead session-scratchpad paths [G; M/low] → sidecar regeneration writes repo-relative refs (indirect closure via trial_id already verified stronger than drafted).

## Class S / T — solidification & test gaps

## F-011 — HARD_STOP_TRANS_M placeholder load-bearing at low-k D-026 cells [C; S/med; VERIFIED] — at k∈{1,3} N/mm the base rides the uncommitted ±35 mm stop (38.2 mm demand); the D-026 band's low edge and #63 intersections inherit an unrecorded constant. Probe + parameter row or decision at sitting.
## F-006 — D-034 dark-frame routing pinned only at outer range [A; T/low] — add inner-range dark-frame test (passes today).
## F-015 — T4a Poisson dispersion check is dead code [D; T/low] — assert index of dispersion; mean-only today.
## F-019 — D-029 hardcode-guard test scans only top-level modules [F1; T/low] — make glob recursive; doe/tiers.py (the sole band consumer) currently unscanned.

## Notable CONFORMS-WITH-NOTE (no finding, recorded for REPORT)
- IS8-17: `trial.py:153` pins #62 thresholds at mid-grid ("until #62 joins the sweep axes", labeled interim) — folds into the P-08(b) #62 decision.
- All 8 "no Phase 1 producer" classifier rows grep-verified as genuinely producer-less and labeled in the committed taxonomy.
