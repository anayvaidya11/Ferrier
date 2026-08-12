#!/usr/bin/env python
"""Probe F-012 — Q_NOMINAL realized as Ry(180°): head-up vs plate-up
inverted in every trial.

Claim under test (FINDINGS.md F-012): kinematic/stage.py:37 pins
Q_NOMINAL = (0, 0, 1, 0) = Ry(180°), which maps stud +X → −X (correct,
anti-parallel engagement) but ALSO stud +Z → −Z — so the outer tag at
stud-frame (0, 0, +185 mm) renders at z = −185 mm in head_frame ("plate
up" rendered plate-DOWN). IS §4 + §7 commit the opposite: with +Z head-up,
+Z stud plate-up, and a level host attitude (nominal host_pitch/roll = 0),
the nominal relative orientation is Rz(180°) = (0, 0, 0, 1). Cam A (head
(−50, 0, +140) mm, boresight ∥ +X) consequently views the outer tag ~37.7°
oblique at 300 mm and ~62.4° at the handoff, where the committed nominal
is ~6.1° / ~14.8° — every frozen trial's outer-tag perception geometry is
tilted 4–48° worse than committed, at the literature model's ~60° validity
edge.

Clauses:
  IS §4 frame table — stud_frame "+Z toward outer tag ('plate up')";
      head_frame "+Z head-up"; "At nominal full engagement, head +X and
      stud +X are anti-parallel".
  IS §7 — "orientation rearward, level with chassis"; nominal sweep point
      host_pitch_deg = host_roll_deg = 0.
  IS §3.2 — outer tag center (0, 0, +185 mm) in stud_frame.

Method (probe33 style — failing condition + nominal control, side by side):
  part 0 (analytic) — the IS §4 reading made numeric: the constraints
      {stud +X → −X_head, stud +Z → +Z_head, right-handed} are satisfied
      by Rz(180) = (0,0,0,1) and violated by the frozen (0,0,1,0) on the
      +Z row; plus the ideal-center camera geometry at 300 mm / 50 mm for
      both quaternions (the four angles the finding cites).
  arm A (frozen) — N=50 nominal-cell run_trial (real MuJoCo, the
      committed sim/scenarios/nominal.json sweep point), per-trial
      outer-tag z in head_frame and cam A view angle at the frame nearest
      300 mm range and at the minimum-range (handoff-proximal) frame,
      plus the outcome census.
  arm B (control) — identical seeds, identical everything, with
      kinematic.stage.Q_NOMINAL monkeypatched in memory to Rz(180) =
      (0, 0, 0, 1); patch restored in `finally`.

Instrumentation is a recording wrapper around trial.sightings_for (pure
observation: it calls the real function and returns its result unchanged;
it consumes no RNG). Seeds follow the D-032 seed rule via
tiers.derive_seed(SWEEP_ROOT, "f012:{i:05d}") — probe-specific root, no
collision with committed sweeps. Both arms use the SAME seeds, so rows
pair one-to-one. Trial NDJSON records go to a TemporaryDirectory; only
parsed numbers land in result.json. Deterministic: fixed root, no wall
clock in any recorded quantity.

Code freeze respected: sim/ is imported, never modified; both patches are
in-memory only.

Run:
  /Users/anayvaidya/Wyzantium/Ferrier/sim/.venv/bin/python \
      studies/R01_PHASE1_REVIEW/probes/probe_f012.py
"""

import json
import math
import os
import statistics
import subprocess
import sys
import tempfile

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..",
                                    ".."))
sys.path.insert(0, os.path.join(REPO, "sim"))

from wyzantium_sim import frames, trial  # noqa: E402
from wyzantium_sim.contact.mujoco_engine import MuJoCoEngine  # noqa: E402
from wyzantium_sim.doe import tiers  # noqa: E402
from wyzantium_sim.kinematic import stage as stage_mod  # noqa: E402
from wyzantium_sim.perception import curves  # noqa: E402
from wyzantium_sim.perception.sightings import sightings_for  # noqa: E402

OUT_DIR = os.path.join(REPO, "sim", "results", "review_r01", "F-012")

SWEEP_ROOT = 20260811          # probe-specific (probe_driver convention)
N_TRIALS = 50
Q_FROZEN = (0.0, 0.0, 1.0, 0.0)   # stage.py:37 — Ry(180°)
Q_RZ180 = (0.0, 0.0, 0.0, 1.0)    # IS §4 reading — Rz(180°)

OUTER_TAG_STUD_M = (0.0, 0.0, 0.185)   # IS §3.2 (mm → m)
HEAD_CENTER_STUD_M = (0.070, 0.0, 0.0)  # stage.HEAD_CENTER_STUD_MM (m)
CHECK_RANGE_M = 0.300           # "at 300 mm" checkpoint


def r6(x):
    return None if x is None else round(float(x), 6)


# ------------------------------------------------- part 0: IS §4 reading
def _apply(q, v):
    return frames.Pose(t=(0.0, 0.0, 0.0), q=q).apply(v)


def is4_reading():
    """The frame-table constraints as numbers. The committed nominal must
    map stud +X to head −X (anti-parallel engagement), stud +Z to head +Z
    (plate-up == head-up under the §7 level attitude), and stay
    right-handed (so stud +Y → head −Y). Rz(180) is the unique proper
    rotation doing all three."""
    tol = 1e-12

    def rowcheck(q):
        x, y, z = (_apply(q, v) for v in ((1, 0, 0), (0, 1, 0), (0, 0, 1)))
        return {
            "maps_stud_X_to": [r6(v) for v in x],
            "maps_stud_Y_to": [r6(v) for v in y],
            "maps_stud_Z_to": [r6(v) for v in z],
            "anti_parallel_X_ok": max(abs(a - b) for a, b in
                                      zip(x, (-1, 0, 0))) < tol,
            "plate_up_head_up_Z_ok": max(abs(a - b) for a, b in
                                         zip(z, (0, 0, 1))) < tol,
        }

    frozen = rowcheck(Q_FROZEN)
    rz = rowcheck(Q_RZ180)
    return {
        "constraints": [
            "IS §4: head +X and stud +X anti-parallel at nominal engagement",
            "IS §4 + §7: stud +Z 'plate up' and head +Z 'head-up' both "
            "world-up at level attitude (nominal host_pitch = host_roll "
            "= 0) => stud +Z maps to head +Z",
            "right-handed (+Y = Z x X in both frames)",
        ],
        "q_frozen_Ry180": frozen,
        "q_Rz180": rz,
        "unique_solution_is_Rz180": (rz["anti_parallel_X_ok"]
                                     and rz["plate_up_head_up_Z_ok"]),
        "frozen_violates_Z_row": not frozen["plate_up_head_up_Z_ok"],
    }


# ------------------------------------- part 0b: ideal-center camera table
def truth_at(center_m, q):
    """T_head_stud placing the stud-head center at center_m, no chassis
    error — exactly stage._pose() in metres."""
    off = _apply(q, HEAD_CENTER_STUD_M)
    return frames.Pose(t=tuple(c - o for c, o in zip(center_m, off)), q=q)


def tag0_geom(truth_m):
    """(outer-tag z in head_frame, cam A view angle deg) via the real
    sightings_for — the exact geometry every trial frame consumes."""
    z = truth_m.apply(OUTER_TAG_STUD_M)[2]
    va = next((math.degrees(s.view_angle_rad)
               for s in sightings_for(truth_m) if s.tag_id == 0), None)
    return z, va


def analytic_table():
    n_exp = curves.get("prior_v1").angle_falloff_exponent
    out = {}
    for label, q in (("frozen_Ry180", Q_FROZEN), ("Rz180", Q_RZ180)):
        rows = {}
        for name, cx in (("at_300mm", CHECK_RANGE_M), ("at_handoff", 0.050)):
            z, va = tag0_geom(truth_at((cx, 0.0, 0.0), q))
            rows[name] = {
                "outer_tag_z_m": r6(z),
                "cam_a_view_deg": r6(va),
                "prior_v1_angle_factor": r6(
                    math.cos(math.radians(va)) ** n_exp),
            }
        out[label] = rows
    return out


# --------------------------------------------------------- trial capture
def run_arm(label, q_nominal, seeds, sweep_point):
    """N run_trial calls at the nominal cell with stage.Q_NOMINAL set to
    q_nominal, recording per-frame outer-tag geometry via a wrapper on
    trial.sightings_for."""
    captured = []       # (range_m, tag0_z_m, tag0_view_deg) per frame

    def recording_sf(truth_m, knockout_mask=0, h_mm=0.0):
        out = sightings_for(truth_m, knockout_mask=knockout_mask, h_mm=h_mm)
        hc = truth_m.apply(HEAD_CENTER_STUD_M)
        z, va = (truth_m.apply(OUTER_TAG_STUD_M)[2],
                 next((math.degrees(s.view_angle_rad)
                       for s in out if s.tag_id == 0), None))
        captured.append((math.sqrt(sum(v * v for v in hc)), z, va))
        return out

    saved_sf = trial.sightings_for
    saved_q = stage_mod.Q_NOMINAL
    engine = MuJoCoEngine()
    per_trial, census = [], {}
    n_frames_total, n_tag0_sighted = 0, 0
    try:
        trial.sightings_for = recording_sf
        stage_mod.Q_NOMINAL = q_nominal
        with tempfile.TemporaryDirectory(prefix=f"probe_f012_{label}_") as td:
            for i, seed in enumerate(seeds):
                captured.clear()
                path = trial.run_trial(seed, sweep_point, engine,
                                       sweep_point["curve_set"], out_dir=td)
                text = path.read_text(encoding="utf-8").rstrip("\n")
                result = json.loads(text[text.rfind("\n") + 1:])
                census[result["outcome"]] = census.get(
                    result["outcome"], 0) + 1

                n_frames_total += len(captured)
                n_tag0_sighted += sum(1 for _, _, va in captured
                                      if va is not None)
                k300 = min(range(len(captured)),
                           key=lambda k: abs(captured[k][0] - CHECK_RANGE_M))
                kho = min(range(len(captured)),
                          key=lambda k: captured[k][0])
                per_trial.append({
                    "i": i, "seed": seed,
                    "outcome": result["outcome"],
                    "attempts_used": result["attempts_used"],
                    "range_at_300mm_frame_m": r6(captured[k300][0]),
                    "outer_tag_z_at_300mm_m": r6(captured[k300][1]),
                    "cam_a_view_at_300mm_deg": r6(captured[k300][2]),
                    "range_at_handoff_frame_m": r6(captured[kho][0]),
                    "outer_tag_z_at_handoff_m": r6(captured[kho][1]),
                    "cam_a_view_at_handoff_deg": r6(captured[kho][2]),
                })
    finally:
        trial.sightings_for = saved_sf
        stage_mod.Q_NOMINAL = saved_q

    def agg(key):
        vals = [t[key] for t in per_trial if t[key] is not None]
        return {"n": len(vals), "mean": r6(statistics.fmean(vals)),
                "min": r6(min(vals)), "max": r6(max(vals))}

    return {
        "q_nominal": list(q_nominal),
        "n_trials": len(per_trial),
        "outcome_census": dict(sorted(census.items())),
        "frames_observed": n_frames_total,
        "frames_with_tag0_sighted": n_tag0_sighted,
        "aggregates": {
            "outer_tag_z_at_300mm_m": agg("outer_tag_z_at_300mm_m"),
            "cam_a_view_at_300mm_deg": agg("cam_a_view_at_300mm_deg"),
            "outer_tag_z_at_handoff_m": agg("outer_tag_z_at_handoff_m"),
            "cam_a_view_at_handoff_deg": agg("cam_a_view_at_handoff_deg"),
        },
        "per_trial": per_trial,
    }


def git_sha():
    try:
        return subprocess.check_output(
            ["git", "-C", REPO, "rev-parse", "--short", "HEAD"],
            text=True).strip()
    except Exception:
        return "unknown"


def main():
    is4 = is4_reading()
    analytic = analytic_table()

    nominal = tiers.load_nominal()["sweep_point"]
    seeds = [tiers.derive_seed(SWEEP_ROOT, f"f012:{i:05d}")
             for i in range(N_TRIALS)]

    arm_a = run_arm("armA", Q_FROZEN, seeds, nominal)
    arm_b = run_arm("armB", Q_RZ180, seeds, nominal)

    a, b = arm_a["aggregates"], arm_b["aggregates"]
    an = analytic
    checks = {
        # IS §4 reading: Rz(180) is the committed nominal, frozen breaks it
        "is4_unique_solution_is_Rz180": is4["unique_solution_is_Rz180"],
        "is4_frozen_violates_plate_up": is4["frozen_violates_Z_row"],
        # arm A (frozen): tag renders BELOW the head, angles at the cited
        # oblique values — every one of the 50 trials
        "armA_tag_z_negative_all_trials": all(
            t["outer_tag_z_at_300mm_m"] < -0.10
            and t["outer_tag_z_at_handoff_m"] < -0.10
            for t in arm_a["per_trial"]),
        "armA_tag_z_mean_near_minus_0p185": abs(
            a["outer_tag_z_at_300mm_m"]["mean"] - (-0.185)) < 0.03,
        "armA_view_300mm_near_37p7": abs(
            a["cam_a_view_at_300mm_deg"]["mean"]
            - an["frozen_Ry180"]["at_300mm"]["cam_a_view_deg"]) < 6.0,
        "armA_view_handoff_near_62p4": abs(
            a["cam_a_view_at_handoff_deg"]["mean"]
            - an["frozen_Ry180"]["at_handoff"]["cam_a_view_deg"]) < 6.0,
        # arm B (Rz(180) control): tag ABOVE the head, committed angles
        "armB_tag_z_positive_all_trials": all(
            t["outer_tag_z_at_300mm_m"] > 0.10
            and t["outer_tag_z_at_handoff_m"] > 0.10
            for t in arm_b["per_trial"]),
        "armB_tag_z_mean_near_plus_0p185": abs(
            b["outer_tag_z_at_300mm_m"]["mean"] - 0.185) < 0.03,
        "armB_view_300mm_near_6p1": abs(
            b["cam_a_view_at_300mm_deg"]["mean"]
            - an["Rz180"]["at_300mm"]["cam_a_view_deg"]) < 6.0,
        "armB_view_handoff_near_14p8": abs(
            b["cam_a_view_at_handoff_deg"]["mean"]
            - an["Rz180"]["at_handoff"]["cam_a_view_deg"]) < 6.0,
    }
    confirmed = all(checks.values())

    result = {
        "finding": "F-012",
        "probe": "probe_f012.py",
        "claim": "Q_NOMINAL = (0,0,1,0) = Ry(180°) inverts head-up vs "
                 "plate-up: the outer tag renders at z = -185 mm in "
                 "head_frame instead of +185 mm, and cam A views it "
                 "~37.7°/~62.4° oblique (300 mm / handoff) where the IS §4 "
                 "committed nominal Rz(180°) = (0,0,0,1) gives "
                 "~6.1°/~14.8°",
        "code_git_sha": git_sha(),
        "sweep": {
            "sweep_point_source": "sim/scenarios/nominal.json (committed "
                                  "nominal cell, D-032 (a))",
            "seed_rule": "tiers.derive_seed(SWEEP_ROOT, 'f012:{i:05d}') — "
                         "D-032 (b) scheme, probe-specific root",
            "sweep_root": SWEEP_ROOT,
            "n_trials_per_arm": N_TRIALS,
            "same_seeds_both_arms": True,
            "engine": "mujoco (local M4, zero spend)",
        },
        "is4_reading": is4,
        "analytic_ideal_centers": analytic,
        "arm_a_frozen_Ry180": arm_a,
        "arm_b_control_Rz180": arm_b,
        "verdict_checks": checks,
        "confirmed": confirmed,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "result.json")
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
        f.write("\n")

    summary = {k: v for k, v in result.items()
               if k not in ("arm_a_frozen_Ry180", "arm_b_control_Rz180")}
    summary["arm_a_frozen_Ry180"] = {
        k: v for k, v in arm_a.items() if k != "per_trial"}
    summary["arm_b_control_Rz180"] = {
        k: v for k, v in arm_b.items() if k != "per_trial"}
    print(json.dumps(summary, indent=2))
    print(f"\nwrote {out}", file=sys.stderr)
    return 0 if confirmed else 1


if __name__ == "__main__":
    sys.exit(main())
