"""T8 — run_trial: the composition root and the unit of replay (PHASE1_PLAN §2).

run_trial(seed, sweep_point, engine, curve_set) → record path. One WIRE_FORMAT
NDJSON record per call, bit-identically reproducible from its header: single
RNG root, no wall clock anywhere (a timestamped trial_id would break the
same-seed gate), engine.load() unconditional per call so a reused engine
instance replays identically.

Composition (D-006 two-stage split; D-005 retry loop; #59 cadence):
kinematic attempt → perception frames along the trajectory → guidance
machine per frame → confidence gate at the handoff crossing → contact stage
→ outcome classification (classify/outcomes.py, T9). Perception frames are
generated post-hoc along the
OPEN-LOOP kinematic trajectory: T5 has no perception-in-the-loop by design,
so hold/reject_frame decisions cannot slow the approach — only
abort/escalate/retry alter the record (labeled limitation, revisit at T10).

Arbitrary code-level choices (spec gaps recorded 2026-08-04, chassis_error
precedent):
- CONTACT_MAX_S per-attempt contact cap (PHASE1_PLAN §6 risk: unbounded
  rattle); G_INSERTION_STANDIN: a constant -x drive acceleration stands
  in for the commanded insertion push (T4c/T7 precedent) and doubles as
  the post-handoff actuator_cmd {"mode": "gravity_insert"}; its 0.1 m/s²
  magnitude is sized to the commanded-insertion speed class (peak ~0.2
  m/s at pocket depth) — free-fall 9.81 reaches 2.2 m/s at the m_rv
  300 kg default and destabilizes the contact solver. Pre-handoff
  actuator_cmd is the commanded stage speed {"mode": "velocity"}.
- The trial's default SolverSettings uses timestep 2e-4 s (T7 wedge-test
  precedent): 1 ms is unstable for hard contact at the 300 kg m_rv
  inertia.
- sigma_px comes from PARAMS[40].default — injector-required but absent
  from scenarios.SWEEP_AXES (pre-existing axis-list gap, flagged for a
  recorded amendment; not edited here).
- Jam thresholds: #62 mid-grid cell (T7 test precedent) until #62 joins
  the sweep axes.
- Frame truth is zero-order-held on the kinematic step grid (≤ ds worth
  of lag); sightings use the coplanar layout (injector default, D-011
  selection pending MR-003).
- After contact-driven aborts and gate refusals the machine's attempt
  counter is resynced (machine.attempt_n self-increments only on
  perception aborts), and machine.stage resets to "acquire" at the start
  of every attempt; a gate refusal consumes the attempt with abort_reason
  "low_confidence" (coarse, labeled).
- The commit gate: #30's predicate names a frame class (multi_tag_fused ∧
  inner_servo ∧ conf ≥ min), not a unique instant — the trial commits at
  the FIRST gate-allowing frame inside the inner-servo window before the
  insertion onset (#26's D-004 stage-3 boundary), and refuses the attempt
  if no frame allowed by onset (D-013). Commit is decided while vision is
  still the guidance source; the terminal frames foreshorten past the
  committed camera extrinsics' useful band.
- Kinematic misses re-approach from START_MM; aborts retry per D-005
  retry_plan. The chassis substream restarts identically each attempt, so
  retries replay the same noise realization (deterministic; fidelity
  limitation, revisit at T10).
- The loop records one classify.AttemptEnd per attempt started, plus
  whether any ID-0 detection ever appeared; classify() maps the trace
  under the FAILURE_TAXONOMY §"Classifier precedence" order. A machine
  escalation with reason "attempt_budget_exhausted" is recorded as a
  budget truncation (no abort_reason on that attempt): the machine reuses
  that enum value for both time and attempt budgets (enum gap noted in
  machine.py), and neither is a perception abort.
"""

from __future__ import annotations

import functools
import hashlib
import json
import math
import subprocess
from dataclasses import replace
from pathlib import Path

from wyzantium_sim import params, scenarios
from wyzantium_sim.classify.outcomes import AttemptEnd, Trace, classify
from wyzantium_sim.contact import runner
from wyzantium_sim.contact.engine import SolverSettings, T1ModelSpec
from wyzantium_sim.guidance import gate
from wyzantium_sim.guidance.machine import (
    GuidanceMachine, contact_offset_mm, retry_plan,
)
from wyzantium_sim.kinematic.stage import (
    INSERTION_ONSET_RANGE_MM, START_MM, KinematicStage,
)
from wyzantium_sim.logging.trial_logger import (
    TrialLogger, pose_mm_to_m, upper21_to_6x6,
)
from wyzantium_sim.perception.inject import PerceptionInjector
from wyzantium_sim.perception.sightings import sightings_for
from wyzantium_sim.perception import timing

CONTACT_MAX_S = 10.0                    # arbitrary per-attempt contact cap
G_INSERTION_STANDIN = (-0.1, 0.0, 0.0)  # insertion drive stand-in (docstring)
TRIAL_TIMESTEP_S = 2.0e-4               # T7 wedge precedent (docstring)
PARAMS_REF = "PHASE1_PARAMETERS.md"
DEFAULT_OUT_DIR = Path(__file__).resolve().parent.parent / "results" / "trials"

_INJECTOR_KEYS = ("outer_occlusion", "inner_occlusion", "illuminance_lux",
                  "rain", "dropout_p", "lens_contamination", "mud_f_c",
                  "flip_kappa", "perception_rate_hz", "perception_latency_ms",
                  "curve_set")


@functools.cache
def _git_sha() -> str:
    """Repo commit the harness ran from; '-dirty' when the tree differs.
    Cached per process so both runs of a same-seed pair record one value."""
    cwd = Path(__file__).resolve().parent
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=cwd, check=True,
                         capture_output=True, text=True).stdout.strip()
    status = subprocess.run(["git", "status", "--porcelain"], cwd=cwd,
                            check=True, capture_output=True, text=True)
    return sha + ("-dirty" if status.stdout.strip() else "")


def _trial_id(seed, sweep_point, engine_name) -> str:
    digest = hashlib.sha1(json.dumps(
        sweep_point, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return f"{engine_name}-{seed}-{digest[:8]}"


def _head_center(pose_mm):
    return pose_mm.apply((70.0, 0.0, 0.0))


def run_trial(seed, sweep_point, engine, curve_set, *, out_dir=None,
              solver=None, contact_max_s=CONTACT_MAX_S) -> Path:
    seed = int(seed)
    sp = scenarios.build_sweep_point(**sweep_point)
    if sp["curve_set"] != curve_set:
        raise ValueError(f"sweep_point curve_set {sp['curve_set']!r} != "
                         f"argument {curve_set!r} (double-entry)")
    solver = (solver if solver is not None
              else SolverSettings(timestep_s=TRIAL_TIMESTEP_S))

    engine.load(T1ModelSpec(
        stiffness_k_n_mm=sp["stiffness_k_n_mm"],
        head_mass_kg=sp["head_mass_kg"], mu_contact=sp["mu_contact"],
        restitution_e=sp["restitution_e"],
        gravity_head_ms2=G_INSERTION_STANDIN), solver)

    cfg = {k: sp[k] for k in _INJECTOR_KEYS}
    cfg["sigma_px"] = params.PARAMS[40].default
    injector = PerceptionInjector(root_seed=seed, config=cfg)

    budget_s = float(sp["time_budget_min"]) * 60.0
    attempts_max = int(sp["attempts_per_encounter"])
    machine = GuidanceMachine(conf_min=sp["conf_min_attempt"],
                              attempts_max=attempts_max,
                              time_budget_s=budget_s)
    jam_grid = params.PARAMS[62].value
    jam = runner.JamThresholds(          # #62 mid-grid cell, labeled interim
        f_ax_n=jam_grid["F_ax_N"][len(jam_grid["F_ax_N"]) // 2],
        f_lat_n=jam_grid["F_lat_N"][len(jam_grid["F_lat_N"]) // 2],
        t_s=jam_grid["t_s"][len(jam_grid["t_s"]) // 2])

    trial_id = _trial_id(seed, sp, engine.engine_id["name"])
    out_dir = Path(out_dir) if out_dir is not None else DEFAULT_OUT_DIR
    log = TrialLogger(out_dir / f"{trial_id}.ndjson")
    log.header(trial_id=trial_id, seed=seed, code_git_sha=_git_sha(),
               engine=dict(engine.engine_id), sweep_point=sp,
               params_ref=PARAMS_REF, solver=solver.to_wire())

    speeds = (sp["speed_outer_ms"], sp["speed_inner_ms"],
              sp["speed_insertion_ms"])
    rate_hz = float(sp["perception_rate_hz"])
    knockout = int(sp["tag_knockout_mask"])

    attempt = 1
    start_mm, aim_mm = START_MM, (0.0, 0.0, 0.0)
    t_clock = 0.0
    handoff_reached_ever = False
    attempt_ends = []       # one classify.AttemptEnd per attempt started
    outer_seen = False      # any ID-0 detection ever (IS8-2 vs IS8-1)
    escalation_reason = None

    while True:
        if t_clock > budget_s:
            escalation_reason = "attempt_budget_exhausted"
            break
        machine.stage = "acquire"       # every attempt re-acquires (resync)
        kin = KinematicStage(root=seed, scale=sp["chassis_error_scale"],
                             start_mm=start_mm, aim_mm=aim_mm,
                             attempt=attempt, t0_s=t_clock,
                             speeds=speeds).run()

        n_frames = int(math.floor((kin.t_end_s - t_clock) * rate_hz)) + 1
        frame_ts = timing.frame_times(rate_hz, t_clock, n_frames)

        decision = None
        commit_line = None
        abort_center = None
        fi = 0
        prev_step = None

        def frame(tf, step):
            nonlocal commit_line, outer_seen
            truth_m = pose_mm_to_m(step.T_head_stud)
            line = injector.observe(
                float(tf), truth_m,
                sightings_for(truth_m, knockout_mask=knockout),
                machine.stage)
            line["attempt"] = {"n": attempt}
            if any(t.get("id") == 0 for t in line.get("tags") or ()):
                outer_seen = True
            d = machine.observe(line, step.range_mm, float(tf))
            if d.action in ("abort_retry", "escalate"):
                line["stage"] = d.stage
                line["abort_reason"] = d.abort_reason
                if d.escalation is not None:
                    line["escalation"] = d.escalation
            log.target_state(line)
            if (commit_line is None
                    and step.range_mm > INSERTION_ONSET_RANGE_MM
                    and gate.commit_allowed(line,
                                            sp["conf_min_attempt"])[0]):
                commit_line = line  # first allowing inner-servo frame
            return d

        for step in kin.steps:
            while (fi < n_frames and frame_ts[fi] < step.t_sim_s
                   and prev_step is not None):
                decision = frame(frame_ts[fi], prev_step)
                fi += 1
                if decision.action in ("abort_retry", "escalate"):
                    break
            if decision is not None and decision.action in ("abort_retry",
                                                            "escalate"):
                abort_center = _head_center(prev_step.T_head_stud)
                t_clock = float(frame_ts[fi - 1])
                break
            log.sim_truth_kinematic(
                step.t_sim_s, step.T_head_stud,
                {"mode": "velocity", "v_cmd_ms": float(step.v_cmd_ms)})
            prev_step = step
        else:
            while fi < n_frames:
                decision = frame(frame_ts[fi], prev_step)
                fi += 1
                if decision.action in ("abort_retry", "escalate"):
                    abort_center = _head_center(prev_step.T_head_stud)
                    t_clock = float(frame_ts[fi - 1])
                    break

        if decision is not None and decision.action == "escalate":
            escalation_reason = decision.abort_reason
            # "attempt_budget_exhausted" is a budget truncation, not a
            # perception abort on this attempt (machine reuses the enum
            # value for both budgets — enum gap noted in machine.py)
            attempt_ends.append(AttemptEnd(
                abort_reason=(None
                              if escalation_reason == "attempt_budget_exhausted"
                              else escalation_reason)))
            break
        if decision is not None and decision.action == "abort_retry":
            attempt_ends.append(AttemptEnd(
                abort_reason=decision.abort_reason))
            attempt = machine.attempt_n     # _abort_retry already advanced it
            plan = retry_plan(abort_center, (0.0, 0.0), attempt - 1)
            start_mm, aim_mm = plan.start_mm, plan.aim_mm
            continue

        t_clock = kin.t_end_s
        if not kin.handoff_reached:
            # kinematic miss (r_gt_annulus / no_crossing): consumes the
            # attempt, fresh approach from the committed start
            attempt_ends.append(AttemptEnd(miss_reason=kin.miss_reason))
            attempt += 1
            machine.attempt_n = attempt
            if attempt > attempts_max:
                break
            start_mm, aim_mm = START_MM, (0.0, 0.0, 0.0)
            continue

        handoff_reached_ever = True
        handoff = kin.handoff
        if commit_line is None:     # no frame allowed commit by onset
            attempt_ends.append(AttemptEnd(
                handoff_reached=True, refused=True,
                abort_reason="low_confidence"))
            attempt += 1
            machine.attempt_n = attempt
            if attempt > attempts_max:
                break
            plan = retry_plan(_head_center(handoff.T_head_stud), (0.0, 0.0),
                              attempt - 1)
            start_mm, aim_mm = plan.start_mm, plan.aim_mm
            continue

        if "pose_cov" in commit_line:
            handoff = replace(handoff,
                              pose_cov=upper21_to_6x6(commit_line["pose_cov"]))

        last_contacts = []
        end_pose = [handoff.T_head_stud]
        contact_this = False

        def on_step(r):
            nonlocal contact_this
            if r.contacts:
                contact_this = True
                last_contacts.clear()
                last_contacts.extend(r.contacts)
            end_pose[0] = r.T_head_stud
            log.sim_truth_contact(r, {"mode": "gravity_insert"})

        remaining = budget_s - handoff.t_sim_s
        out = runner.run_contact(
            engine, handoff, jam,
            max_time_s=max(solver.timestep_s, min(contact_max_s, remaining)),
            dt=solver.timestep_s, on_step=on_step)
        t_clock = out.t_end_s

        attempt_ends.append(AttemptEnd(
            handoff_reached=True, contact=contact_this,
            lip_strike=out.lip_strike, latched=out.latched, jam=out.jam,
            full_stroke=out.full_stroke, timed_out=out.timed_out,
            abort_reason=out.abort_reason))
        if out.latched:
            break
        # jam or contact timeout: consumes the attempt, D-005 retry
        attempt += 1
        machine.attempt_n = attempt
        if attempt > attempts_max:
            break
        offset = (contact_offset_mm(last_contacts) if last_contacts
                  else (0.0, 0.0))
        plan = retry_plan(_head_center(end_pose[0]), offset, attempt - 1)
        start_mm, aim_mm = plan.start_mm, plan.aim_mm

    outcome, false_capture = classify(Trace(
        attempts=tuple(attempt_ends), escalation_reason=escalation_reason,
        outer_tag_seen=outer_seen))
    attempts_used = min(attempt, attempts_max)
    log.result(outcome=outcome,
               first_attempt_success=(outcome == "success"
                                      and attempts_used == 1),
               attempts_used=attempts_used, t_total=float(t_clock),
               handoff_reached=handoff_reached_ever,
               false_capture=false_capture)
    return log.write()
