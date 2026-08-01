# WyZen Target-State Stream — Wire Format

**Status:** Phase 0 deliverable, v1.0, 2026-08-01. One contract between every stage
(MASTER_CONTEXT §2.3); traceability and labels as in `INTERFACE_SPEC.md`.

**Encoding:** NDJSON — one JSON object per line, UTF-8, LF-terminated. Versioned via
`v`. Producers: perception (Phase 1: the injected model, D-007; Phase 3: the real
stack). Consumers: guidance, abort gate, telemetry, the sim harness logger.

## The omitted-not-zeroed rule

**A field that could not be determined is omitted — never emitted as zero, null, or a
default.** (Carried verbatim from Ghost Medic's `DATA_FORMAT.md` discipline, §2.3.)

**Worked example of the failure this prevents:** perception loses the tag mid-inner-
servo and emits `"pose": {"t": [0,0,0], ...}` "as a placeholder." The consumer reads a
valid pose stating the stud is **at the funnel mouth center** — zero is a location, not
an absence — and commands the insertion lunge into whatever is actually there. Under
this contract the producer omits `pose` entirely; the consumer's required-field check
fails; the confidence gate holds the vehicle; nobody moves steel on a phantom (D-013).

## Fields

Every field: name, type, units, frame, valid range, required/optional, absence
semantics. Unknown fields MUST be ignored (forward compatibility).

| Field | Type | Units / frame | Range | Req? | Absent means |
|---|---|---|---|---|---|
| `v` | int | — | ≥1 (this doc: 1) | **R** | Line invalid — reject |
| `type` | string | — | `"target_state"` | **R** | Line invalid — reject |
| `t_capture` | float | s, producer steady clock | ≥0, monotonic | **R** | Line invalid — reject |
| `t_emit` | float | s, same clock | ≥ `t_capture` | **R** | Line invalid — reject |
| `pose` | object | `T_head_stud` — stud_frame in head_frame (INTERFACE_SPEC §4): `{"t":[x,y,z] m, "q":[w,x,y,z] unit}` | ‖t‖ ≤ 10 m; ‖q‖ = 1 ±1e-6 | O | **No pose available this frame.** Guidance must not act on position (D-013) |
| `pose_cov` | float[21] | m², m·rad, rad²; upper triangle of 6×6, order [x y z rx ry rz] | PSD | O (R if `pose` present) | Pose without stated uncertainty is invalid — treat line as pose-absent |
| `pose_source` | string enum | `outer_tag` \| `inner_ring` \| `multi_tag_fused` \| `contact_force` \| `none` | — | **R** | Line invalid — reject. **This enum is what makes D-013 enforceable: there is no value meaning "guessed"** |
| `conf` | float | — | [0,1] | **R** | Line invalid — reject (the gate keys on it) |
| `tags` | array | per-tag: `{"id": int, "reproj_err": float px, "ambiguity_flag": bool, "ambiguity_ratio": float}` | id per INTERFACE_SPEC §3.4 | O | No tag detections this frame |
| `fault` | object | `{"class": "mired"\|"depleted"\|"damaged"\|"destroyed"\|"unknown", "conf": [0,1]}` (REQ-012) | — | O | No classification available — consumers must not assume "fine" |
| `degradation` | object | `{"occlusion_est": [0,1], "illuminance_lux": >0, "dropout": bool}` — each key itself optional | — | O | That observation unavailable (omitted, not zeroed — 0 lux is a measurement, not a default) |
| `stage` | string enum | `acquire` \| `outer_servo` \| `inner_servo` \| `contact_insert` \| `latched` \| `abort` \| `escalate` (D-004) | — | **R** | Line invalid — reject |
| `attempt` | object | `{"n": int ≥1, "last_contact_offset": {"frame": "head_frame", "t": [x,y,z] m}}` (D-005) | n ≤ attempts-per-encounter | O | First approach; no prior contact data |
| `abort_reason` | string enum | `low_confidence` \| `ambiguity_persistent` \| `inner_ring_absent` \| `contact_anomaly` \| `attempt_budget_exhausted` \| `constellation_inconsistent` \| `latch_fail` \| `command` | — | O (R when `stage` ∈ {abort, escalate}) | Not aborting |
| `escalation` | object | `{"imagery_ref": string, "recommend": "human_decision"}` | — | O (R when `stage` = escalate) | Not escalating |

Clock source: the producer's monotonic steady clock, named because DDIL forbids
assuming synchronized wall time (REQ-005); consumers use `t_emit − t_capture` for
latency and their own receive time for staleness.

**`pose_cov` represents** the estimator's frame-to-frame uncertainty under its noise
model. **It does not represent:** the two-solution ambiguity (that is `ambiguity_flag`
— a flip is a discrete wrong answer, not a wide Gaussian), calibration bias (D-012
extrinsics are assumed), or model error in the injected curves (D-008-R labels).
Consumers must not treat small covariance as immunity to those.

**Threshold:** the confidence gate holds any actuation when `conf < conf_min_attempt`.
**`conf_min_attempt` is a swept Phase 1 parameter (D-017), sweep {0.50–0.95}, default
0.85 — the default is arbitrary and labeled so; §1.5's refusal-vs-damage asymmetry,
not a round number, is what ultimately sets it, and the sweep's refusal-rate vs.
damage-risk tradeoff curve is a Phase 1 deliverable (ARCHITECTURE §6).** Insertion
commit additionally requires `pose_source` = `multi_tag_fused` **(≥2 fused tags — a
single tag's orientation is flip-prone at all inner-servo angles, studies/H08, D-011
qualification)** and `stage` = `inner_servo` (D-004, D-013).

## Failure semantics — what the stream looks like

- **Perception degrading:** `conf` falls; `degradation` reports why; `pose` still
  present. The gate, not the producer, decides to stop acting.
- **Tag gone:** `pose` and `tags` omitted, `pose_source: "none"`, `conf` reflects
  absence; `stage` transitions per INTERFACE_SPEC §8 rows 1–4.
- **Below threshold:** `stage: "escalate"`, `abort_reason: "low_confidence"`,
  `escalation` present with imagery reference — the system refuses, sends imagery,
  recommends a human (§2.3 honesty discipline in steel; D-013).
- **Latch failure:** `stage: "abort"`, `abort_reason: "latch_fail"`, `attempt.n`
  incremented on the next approach with `last_contact_offset` applied (D-005).
- **Comms loss:** nothing changes on the wire — the stream is produced and consumed
  onboard (REQ-011); telemetry buffers store-and-forward (REQ-005).

## Consumer checklist (ordered)

1. **Version check:** `v` == 1, else reject line.
2. **Required fields present:** `type`, `t_capture`, `t_emit`, `pose_source`, `conf`,
   `stage` — else reject line.
3. **Frame verification:** any `pose` consumed AS `T_head_stud` per INTERFACE_SPEC §4
   — a consumer needing another frame transforms explicitly; never guess.
4. **Staleness check:** receive-time age beyond the consumer's staleness bound →
   treat as pose-absent.
5. **Confidence gate:** apply `conf_min_attempt` and the `pose_source` restrictions
   before any actuation decision.
6. **Omitted-field handling:** absence = unknown; never substitute defaults for
   `pose`, `fault`, or `degradation`.
7. **Unknown fields:** ignore, preserve on relay (forward compatibility).

## Trial record schema (A-007, D-006, ARCHITECTURE §6.4–6.5)

One NDJSON file per trial: a header line, the full interleaved state sequence, a result
line. This is what makes every trial bit-identically re-runnable and every replay
artifact traceable to a committed record. Same rules as above (versioned, omitted-not-
zeroed, unknown fields ignored).

- **Header** — `{"v":1, "type":"trial_header", "trial_id": string (unique, stable),
  "seed": int (single RNG root; all streams derive from it), "code_git_sha": string
  (repo commit the harness ran from), "engine": {"name","version"},
  "sweep_point": object (every §9 axis value for this trial), "params_ref": string
  (path to the committed parameter file)}` — all required. A trial whose header cannot
  name its seed, SHA, and sweep point is not a result; it is an anecdote.
- **State sequence** — interleaved, timestamped on the sim clock:
  - `target_state` lines exactly as specified above (the injected perception output);
  - `{"type":"sim_truth", "t": float, "T_world_head": pose, "T_world_stud": pose,
    "contact_wrench": [fx,fy,fz,mx,my,mz] (N, N·m, head_frame; omitted before
    contact), "actuator_cmd": object}` — the ground truth the injected model degrades
    from, logged every physics step after capture-plane handoff and every kinematic
    step before it (D-006).
- **Result** — `{"v":1, "type":"trial_result", "outcome": "success" |
  "IS8-<row>" (failure class keyed to INTERFACE_SPEC §8 row number, e.g. "IS8-5" =
  ambiguity flip) | "clean_miss", "first_attempt_success": bool, "attempts_used": int,
  "t_total": float, "handoff_reached": bool}` — required; unclassifiable failures
  extend §8 by recorded amendment before they get an outcome string (ARCHITECTURE
  §6.2).

## Annotated reference lines

```json
{"v":1,"type":"target_state","t_capture":142.031,"t_emit":142.043,"pose":{"t":[2.412,0.113,-0.071],"q":[0.008,0.002,0.9999,0.011]},"pose_cov":[0.0009,0,0,0,0,0,0.0016,0,0,0,0,0.0016,0,0,0,0.0007,0,0,0.0011,0,0.0011],"pose_source":"outer_tag","conf":0.96,"tags":[{"id":0,"reproj_err":0.41,"ambiguity_flag":false,"ambiguity_ratio":6.2}],"degradation":{"occlusion_est":0.05,"illuminance_lux":41000},"stage":"outer_servo"}
```
Nominal outer servo at 2.4 m: single outer tag, tight covariance, high ambiguity ratio
(solutions well separated), daylight. Gate passes; guidance closes range.

```json
{"v":1,"type":"target_state","t_capture":198.550,"t_emit":198.561,"pose":{"t":[0.291,0.019,0.024],"q":[0.013,0.007,0.9998,0.004]},"pose_cov":[0.0002,0,0,0,0,0,0.0004,0,0,0,0,0.0004,0,0,0,0.0004,0,0,0.0006,0,0.0006],"pose_source":"inner_ring","conf":0.90,"tags":[{"id":3,"reproj_err":0.62,"ambiguity_flag":false,"ambiguity_ratio":4.1},{"id":4,"reproj_err":0.55,"ambiguity_flag":false,"ambiguity_ratio":4.8}],"degradation":{"occlusion_est":0.32,"illuminance_lux":9.4},"stage":"inner_servo"}
```
Degraded but workable: 32% estimated mud, 9.4 lux, only 2 of 8 inner tags — but any
single tag yields full pose (D-011), two agree, conf ≥ 0.85. Insertion may proceed.

```json
{"v":1,"type":"target_state","t_capture":201.104,"t_emit":201.117,"pose":{"t":[0.242,-0.008,0.031],"q":[0.702,0.011,0.712,0.009]},"pose_cov":[0.0002,0,0,0,0,0,0.0004,0,0,0,0,0.0004,0,0,0,0.0122,0,0,0.0140,0,0.0006],"pose_source":"inner_ring","conf":0.61,"tags":[{"id":7,"reproj_err":1.90,"ambiguity_flag":true,"ambiguity_ratio":1.08}],"degradation":{"occlusion_est":0.38,"illuminance_lux":8.9},"stage":"inner_servo"}
```
Ambiguity flip detected: single near-head-on tag, `ambiguity_ratio` 1.08 (the two IPPE
solutions nearly tied), rotation covariance blown out, `ambiguity_flag` true. Consumer
rejects the frame (checklist 5 + INTERFACE_SPEC §8 row 5); Cam B's oblique view is the
designed remedy (D-012).

```json
{"v":1,"type":"target_state","t_capture":214.400,"t_emit":214.409,"pose_source":"none","conf":0.11,"degradation":{"occlusion_est":0.71,"illuminance_lux":3.1},"stage":"escalate","abort_reason":"low_confidence","escalation":{"imagery_ref":"frames/214.4_camA.png","recommend":"human_decision"}}
```
Abort on low confidence: note `pose` and `tags` are **omitted, not zeroed** — 71% mud
at 3 lux left nothing to act on. The system refuses, sends imagery, recommends a human
(D-013, §2.3).

```json
{"v":1,"type":"target_state","t_capture":233.902,"t_emit":233.911,"pose":{"t":[0.301,0.027,-0.012],"q":[0.006,0.004,0.9999,0.008]},"pose_cov":[0.0002,0,0,0,0,0,0.0004,0,0,0,0,0.0004,0,0,0,0.0004,0,0,0.0006,0,0.0006],"pose_source":"multi_tag_fused","conf":0.88,"tags":[{"id":2,"reproj_err":0.70,"ambiguity_flag":false,"ambiguity_ratio":3.9},{"id":6,"reproj_err":0.66,"ambiguity_flag":false,"ambiguity_ratio":4.4}],"stage":"inner_servo","attempt":{"n":2,"last_contact_offset":{"frame":"head_frame","t":[0.0,-0.019,0.008]}}}
```
Retry in progress: second attempt (D-005), re-approaching with the measured contact
offset from attempt 1 applied (19 mm left, 8 mm high at the wall).

```json
{"v":1,"type":"target_state","t_capture":236.508,"t_emit":236.514,"pose":{"t":[0.058,0.003,0.001],"q":[0.004,0.001,0.9999,0.002]},"pose_cov":[0.0001,0,0,0,0,0,0.0001,0,0,0,0,0.0001,0,0,0,0.0002,0,0,0.0002,0,0.0002],"pose_source":"contact_force","conf":0.93,"stage":"abort","abort_reason":"latch_fail","attempt":{"n":2,"last_contact_offset":{"frame":"head_frame","t":[0.0,0.002,-0.001]}}}
```
Latch failure at full insertion: pose now sourced from contact force (stage 3, D-004 —
the wall is the sensor), stud seated but no latch confirm. Back out per D-005; attempt
budget will decide between retry and escalation.
