# R01 Lane Charters — Mass Surgical Review of Phase 1

**Anchor:** all verdicts at HEAD `cdf7fbf` (code tree verified byte-identical to
freeze SHA `b493e7a` — every post-freeze commit is docs/results only, so matrix
verdicts apply directly to the frozen dataset). **Code freeze:** no commit may
touch `sim/wyzantium_sim/`, `sim/wirefmt/`, or `sim/tests/` until all lanes
finish read passes; the review branch commits only matrix/findings/probe
artifacts. Findings are recorded, never silently patched (MASTER_CONTEXT §4.3;
HOLES.md pattern).

**Conduct:** documents win (MASTER_CONTEXT §2.5); behavioral change requires a
human-ratified D-xxx with before/after probe artifacts (D-034/035/036
archetype); causal attribution must be probe-tested per-axis, never inferred —
H-18's first causal story was wrong and Tier-1 marginals falsified it.

**Boundary rule:** the H-18 bug cluster lived at *composition seams* (per-frame
readings of IS §8 rows against stochastic 30 Hz detection). Seams below are
marked ⚭ and get read by both lanes.

| Lane | Rank | Files | Charter docs | Deep-scrutiny lens |
|---|---|---|---|---|
| **A** — guidance semantics & outcome classification | 1 | `guidance/gate.py`, `guidance/machine.py`, `classify/outcomes.py` (+ `test_guidance.py`, `test_outcomes.py`) | IS §8 all rows; FAILURE_TAXONOMY precedence; D-004/005/013/017/018/029/030/033/034/035/036 | Apply the H-18 disease test to every §8 row that never got the persistence treatment (rows 6–14, 16–18 realizations under stochastic detection); hold-timer reset semantics; retry × attempt-budget × encounter-timer interactions; D-018 sector enforcement during retry offsets. This code alone produced H-18 and sets the 0% gate cell. ⚭B (confidence consumption vs production), ⚭E (outcome semantics vs trial_result serialization) |
| **B** — perception injection & curve seam | 2 | `perception/*` (incl. `mr_ingest.py`, post-freeze addition reviewed at its own SHA `7e9bb47`), `rng.py` (+ perception tests, `test_mr_ingest.py`) | D-007, D-008-R, D-023, #37–#45, studies/H08, `research/data/perception_prior.md` | Evidence-mass confidence production (half of H-18's mechanism); seam shape — mud_f_c/sigma_px/flip_kappa are sweep axes NOT CurveSet fields (mr_ingest docstring states it; verify nothing pretends otherwise); a seam bug found after the mr_v1 swap doubles the re-run bill and confounds before/after attribution |
| **C** — contact stage & engines | 5 | `contact/*` (+ contact/conformance tests) | D-020, D-027, IS §8 rows 16/17, #62/#63, PHASE1_PLAN §3 suite | `HARD_STOP_TRANS_M` "arbitrary placeholder" (mujoco_engine.py); Newton stub status honesty; latch predicate exactness (3 mm / 0.1 m/s / 100 ms); jam criterion vs probe62 finding; at the gate cell most trials refuse pre-contact, so contact bugs move nominal/mild cells and IS8-16/17 counts, not the headline |
| **D** — kinematic stage, frames, handoff | 6 | `kinematic/*`, `frames.py`, `geometry.py`, `scenarios.py` (+ their tests) | D-006/015/016/019/024/037, IS §3.5/§4/§5/§6, H-17 | `stage.py:19` "pose_cov placeholder until T6" comment — stale or a real gap feeding the confidence gate?; D-037 closed-loop time mapping (holds freeze position, error indexed by arc length); H-17 NOT-REALIZED row; handoff field list == IS §6 |
| **E** — wire format, logging, trial, replay | 4 | `wirefmt/*`, `logging/trial_logger.py`, `trial.py`, `replay/*` (+ their tests) | WIRE_FORMAT entire; A-007; #58–60 | Two of three load-bearing exit tests live here; omitted-not-zeroed enforcement; canonical-writer byte identity; #59 cadence; mm↔m seam in trial composition (inject docstring flags it); replay bit-identity scope (same platform only?) |
| **F1** — parameter transcription | 3 | `params.py`, `sim/scenarios/*.json` (+ `test_params.py`, `test_scenarios.py`) | PHASE1_PARAMETERS all 65; D-029 | Re-verify 65/65 doc-value equality independently of the existing transcription test (the test could share a wrong constant with the code); gate_moderate.json == D-029 verbatim; sweep_point serializer covers every §9/§9.1 axis |
| **F2** — DOE, analysis, results provenance, statistics | 3 | `doe/*`, `analysis/*`, `sim/results/*` (+ doe/analysis tests) | D-021/028/032/038, ARCH §5–6, A-004 | Owns SOLIDIFICATION.md sweep in full; CI methods; pooling guard; seed/substream + kill/resume; spend cross-foot; manifest provenance; feasibility #63 pinned cross-check tolerance |
| **G** — contract self-consistency & provenance hygiene | 7 | all `*.md` cross-refs, MANIFEST, tier3 README, HOW-FAR-ALONG, PENDING_HUMAN, REPORT stub | MASTER_CONTEXT documents-win + §4.3 | records_storage vs ARCH §6.4; manifest `$0`-expansion mangle; superseded-decision pointer integrity; REPORT stub header now false ("No simulation exists yet"); status-line accuracy |

## Verification protocol (evidence ladder)

- **L0 DRAFT** — reading-based claim. Not actionable, not reported outward.
- **L1 VERIFIED** — concrete failure scenario written; a different-lane
  prosecutor independently concurs on the clause reading (documents-win
  adjudication). Sufficient for Class M/E/S/T.
- **L2 CONFIRMED** — required for Class B: reproducing probe artifact in
  `sim/results/review_r01/F-NNN/` — deterministic seed, small N, failing
  condition **plus nominal control** (probe33 style), local M4 MuJoCo, no
  spend.

**Prosecutor kill taxonomy** (mandatory pass before any finding advances):
(a) behavior ratified by a later D-xxx; (b) clause superseded (D-003/008/009
chains); (c) scenario outside committed sweep domains; (d) coverage exists
under a different test name; (e) attribution error — any "X causes the gate
outcome" claim must be probed with X varied in isolation. A killed finding is
RECLASSIFIED or REJECTED with the kill recorded — rejected findings are
evidence too.

*Protocol amendment (2026-08-11 late, usage economy — human-flagged): the
standalone L2 probe campaign was over-built. Every Class B finding already
carried two independent reproductions (lane reviewer + prosecutor, committed
in raw_lanes.json) — sufficient evidence for the ratification sitting. From
here forward, probe artifacts are built **fix-time** (before/after in the
fixing session, the D-034/035/036 shape), never as standalone multi-agent
campaigns. The in-flight run was allowed to finish because >half its results
were already durable and F-012's probe (contamination magnitude of the
orientation inversion) carries genuine sitting-decision value.*

## Triage classes (pipeline per class)

- **M mechanical** (no behavior, no record bytes): one batched PR after read
  passes; proof = same-seed byte-identical trial vs a frozen record; gstack
  /review on the batch.
- **B behavioral**: L2 finding + before-probe → PENDING_HUMAN P-08 → one
  ratification sitting → fix + after-probe → single batched re-run (with
  H-17) → `freeze_prior_v2`; `freeze_prior_v1` retained as evidence.
- **E erratum**: frozen artifact bytes untouched — sidecar errata files;
  contract-meaning errata take the dated in-place-revision convention with
  human sign-off.
- **S solidification**: SOLIDIFICATION.md; computation-only items land
  pre-REPORT; trial-needing items fold into the batched re-run.
- **T test gap**: write a test asserting committed behavior; passes → commit
  (freeze unaffected); fails → reclassify B/E.
