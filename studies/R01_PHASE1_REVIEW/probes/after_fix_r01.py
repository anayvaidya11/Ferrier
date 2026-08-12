"""R01 after-fix evidence (D-034/035/036 archetype, second half).

Runs the fixed code against each finding's failure condition and writes
sim/results/review_r01/F-0NN/after_fix.json BESIDE the committed before
artifact (never overwriting it). Before = the committed probe result.json;
after = this. Deterministic, local, no spend.

Run: sim/.venv/bin/python studies/R01_PHASE1_REVIEW/probes/after_fix_r01.py
Exit 0 iff every after-arm shows the ratified behavior.
"""
import json
import math
import sys
from pathlib import Path

from wyzantium_sim import frames
from wyzantium_sim.guidance import gate
from wyzantium_sim.guidance.machine import GuidanceMachine
from wyzantium_sim.kinematic import stage
from wyzantium_sim.perception.inject import PerceptionInjector
from wyzantium_sim.perception.sightings import sightings_for

OUT = Path(__file__).resolve().parents[3] / "sim" / "results" / "review_r01"
RESULTS = {}
OK = True


def record(fid, payload, fixed):
    global OK
    payload["fixed"] = fixed
    OK = OK and fixed
    RESULTS[fid] = payload
    (OUT / fid).mkdir(parents=True, exist_ok=True)
    with open(OUT / fid / "after_fix.json", "w") as fh:
        json.dump(payload, fh, indent=1)
        fh.write("\n")


def line(**over):
    base = {"v": 1, "type": "target_state", "t_capture": 10.0,
            "t_emit": 10.03, "pose": {"t": [0.12, 0.0, 0.0],
                                      "q": [0.0, 0.0, 0.0, 1.0]},
            "pose_cov": [1e-6] * 21, "pose_source": "multi_tag_fused",
            "conf": 0.90, "stage": "inner_servo",
            "tags": [{"id": 1, "reproj_err": 0.4, "ambiguity_flag": False,
                      "ambiguity_ratio": 1.0},
                     {"id": 2, "reproj_err": 0.5, "ambiguity_flag": False,
                      "ambiguity_ratio": 1.0}]}
    base.update(over)
    return base


def dark():
    return line(stage="outer_servo", pose_source="none", conf=0.0,
                pose=None, tags=None)


def strip_absent(ln):
    return {k: v for k, v in ln.items() if v is not None}


# --- F-004: attempt boundary resets walls (D-042) ---
m = GuidanceMachine()
gap = line(pose_source="inner_ring",
           tags=[{"id": 3, "reproj_err": 0.4, "ambiguity_flag": False,
                  "ambiguity_ratio": 2.0}])
t = 1.0
for _ in range(120):                      # 4 s of ring absence: open window
    d = m.observe(strip_absent(gap), range_mm=299.0, t_s=t)
    t += 1.0 / 30.0
m.begin_attempt()                          # what trial.py does now (D-042)
d2 = m.observe(strip_absent(gap), range_mm=299.0, t_s=t + 2.0)
md = GuidanceMachine()
for _ in range(120):                       # 4 s dark: open dark window
    md.observe(strip_absent(dark()), range_mm=2500.0, t_s=t)
    t += 1.0 / 30.0
md.begin_attempt()
d3 = md.observe(strip_absent(dark()), range_mm=2500.0, t_s=t + 2.0)
record("F-004", {
    "ring_gap_after_begin_attempt": d2.action,
    "dark_blip_after_begin_attempt": d3.action,
}, fixed=(d2.action == "reject_frame" and d3.action == "hold"))

# --- F-005: flagged frames are not commit evidence (D-044) ---
flagged = line(conf=0.87, tags=[
    {"id": 1, "reproj_err": 0.4, "ambiguity_flag": True,
     "ambiguity_ratio": 0.92},
    {"id": 2, "reproj_err": 0.5, "ambiguity_flag": False,
     "ambiguity_ratio": 0.92},
    {"id": 3, "reproj_err": 0.5, "ambiguity_flag": False,
     "ambiguity_ratio": 0.92}])
allowed, reason = gate.commit_allowed(flagged, 0.85)
ctrl_allowed, _ = gate.commit_allowed(line(conf=0.87), 0.85)
record("F-005", {
    "flagged_frame_allowed": allowed, "refusal_reason": reason,
    "unflagged_control_allowed": ctrl_allowed,
    "before": "gate returned (True,'commit') on machine-rejected lines "
              "(raw_lanes.json dual reproduction)",
}, fixed=(not allowed and "D-044" in reason and ctrl_allowed))

# --- F-007: lone inner tag flip-prone again (D-043) ---
cfg = {"outer_occlusion": 0.0, "inner_occlusion": 0.0,
       "illuminance_lux": 800, "rain": 0.0, "dropout_p": 0.0,
       "lens_contamination": 0.0, "mud_f_c": 0.8, "flip_kappa": 1.0,
       "sigma_px": 0.5, "perception_rate_hz": 30,
       "perception_latency_ms": 30, "curve_set": "prior_v1"}
inj = PerceptionInjector(20260804, dict(cfg))
truth = frames.Pose((0.25, 0.0, 0.185), (0.0, 0.0, 0.0, 1.0))
s_lone = sightings_for(truth, knockout_mask=0b111110111)  # lone tag 3
flags = flips = det = 0
for k in range(1500):
    ln = inj.observe(0.1 + k / 30.0, truth, s_lone, "inner_servo")
    tags = ln.get("tags") or []
    if tags:
        det += 1
        flags += any(tg["ambiguity_flag"] for tg in tags)
record("F-007", {
    "lone_tag_frames_detected": det, "flag_rate": flags / max(det, 1),
    "before": "0/1596 flags, ratio 69-94 (span 0.11 immunity)",
}, fixed=(det > 0 and flags / max(det, 1) > 0.5))

# --- F-008: 10 mm tags no longer decode at 3 m (D-043) ---
inj8 = PerceptionInjector(20260804, dict(cfg))
truth29 = frames.Pose((2.9, 0.0, 0.185), (0.0, 0.0, 0.0, 1.0))
s_no_outer = sightings_for(truth29, knockout_mask=1)
inner_detected = 0
for k in range(500):
    ln = inj8.observe(0.1 + k / 30.0, truth29, s_no_outer, "acquire")
    inner_detected += len(ln.get("tags") or [])
record("F-008", {
    "inner_detections_at_2p9m_500_frames": inner_detected,
    "before": "all 8 inner tags detected per frame (34.4 px span "
              "convention); per-tag truth ~3 px vs 20 px floor",
}, fixed=(inner_detected == 0))

# --- F-012: nominal orientation is Rz(180) (D-041) ---
res = stage.KinematicStage(root=20260811, scale=0.0).run()
q = res.handoff.T_head_stud.q
angle_300 = None
s0 = [s for s in sightings_for(frames.Pose((0.3, 0.0, 0.0),
                                           stage.Q_NOMINAL)) if s.tag_id == 0]
if s0:
    angle_300 = math.degrees(s0[0].view_angle_rad)
tag_pose = frames.Pose((0.3, 0.0, 0.0), stage.Q_NOMINAL).compose(
    frames.Pose((0.0, 0.0, 0.185), (1.0, 0.0, 0.0, 0.0)))
record("F-012", {
    "handoff_q": list(q), "outer_tag_z_m_at_300mm": tag_pose.t[2],
    "cam_a_view_angle_deg_at_300mm": angle_300,
    "before": "q=(0,0,1,0): tag z=-0.185, view 37.7 deg",
}, fixed=(tuple(q) == (0.0, 0.0, 0.0, 1.0) and tag_pose.t[2] > 0.18
          and angle_300 is not None and angle_300 < 10.0))

# --- F-016: latency axis live (D-045) ---
from wyzantium_sim.contact.mujoco_engine import MuJoCoEngine
from wyzantium_sim import trial as trial_mod
from wyzantium_sim.scenarios import load_scenario, SCENARIO_DIR
import tempfile
nominal = load_scenario(SCENARIO_DIR / "nominal.json")["sweep_point"]
# Cell with holds (dropout bursts): hold windows anchor to DELIVERY times
# under D-045, so latency shifts wall entry/exit and t_total. At the pure
# nominal cell nothing holds and arrival-driven path time is legitimately
# latency-invariant — that is physics, not inertness.
outs = {}
with tempfile.TemporaryDirectory() as tmp:
    for lat in (10, 100):
        sp = dict(nominal, perception_latency_ms=lat, dropout_p=0.2)
        p = trial_mod.run_trial(101, sp, MuJoCoEngine(), sp["curve_set"],
                                out_dir=Path(tmp) / str(lat))
        last = json.loads(p.read_text().splitlines()[-1])
        outs[lat] = {"outcome": last["outcome"], "t_total": last["t_total"]}
record("F-016", {
    "cell": "nominal + dropout_p 0.2 (holds occur)",
    "latency_10ms": outs[10], "latency_100ms": outs[100],
    "before": "byte-diffs confined to t_emit; outcomes and t_total "
              "identical across the swept axis at every cell",
}, fixed=(outs[10]["t_total"] != outs[100]["t_total"]
          or outs[10]["outcome"] != outs[100]["outcome"]))

# --- F-009: sigma_px is a real sweep axis (D-046(a)) ---
from wyzantium_sim import scenarios as scen
from wyzantium_sim.doe import tiers as tiers_mod
sp_hi = scen.build_sweep_point(**{**nominal, "sigma_px": 1.0})
grid = tiers_mod.load_tier1()["grids"].get("sigma_px", {}).get("cells")
record("F-009", {
    "build_sweep_point_sigma_1p0": sp_hi["sigma_px"],
    "tier1_grid": grid,
    "before": "SweepPointError('unknown axes'); pinned at PARAMS[40].default",
}, fixed=(sp_hi["sigma_px"] == 1.0 and grid == [0.3, 0.5, 1.0]))

# --- F-017: trial_header carries instance identity (D-046(f)) ---
from wirefmt import validator as wf_validator
with tempfile.TemporaryDirectory() as tmp:
    p = trial_mod.run_trial(101, nominal, MuJoCoEngine(),
                            nominal["curve_set"], out_dir=Path(tmp))
    hdr = json.loads(p.read_text().splitlines()[0])
record("F-017", {
    "header_instance": hdr.get("instance"),
    "validator_errors": wf_validator.validate_line(hdr),
    "before": "no instance field at any of the 4 contract layers",
}, fixed=(isinstance(hdr.get("instance"), dict)
          and bool(hdr["instance"].get("class"))
          and wf_validator.validate_line(hdr) == []))

print(json.dumps({k: v["fixed"] for k, v in RESULTS.items()}, indent=1))
sys.exit(0 if OK else 1)
