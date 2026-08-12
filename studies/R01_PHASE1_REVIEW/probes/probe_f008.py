"""R01 L2 probe — F-008: inner-tag decode pixel extent uses constellation span.

Claim under test (FINDINGS.md F-008): the injector computes decode
probability from px_size = f_px * span_m / dist_m, where sightings.py
hard-codes span_m = 0.11 m (constellation span) for EVERY inner tag. At
acquisition range (~2.9 m) that yields ~34 px — above the IS §3.2 20 px
decode floor — so 10 mm tags decode essentially always, where IS §3.3's
per-tag arithmetic (10 mm => 39 px at 300 mm, 8.6e-4 rad/px) puts the
per-tag extent at ~3 px, far below the floor. Consequence: with
knockout_mask=1 (outer tag destroyed) a healthy fused inner pose stream
exists across the whole approach, bypassing D-034 dark-window semantics
and coexisting with IS8-2's basis ("no ID-0 at expected range").

Arms (probe33 style — failing condition + nominal control, side by side):
  arm1_head_span  — frozen HEAD behavior: knockout_mask=1, truth
                    x = 2.9 m, nominal degradation, N = 1000 frames.
                    Expected per the finding: ~all 8 inner tags detected
                    per frame, pose_source = multi_tag_fused.
  arm2_pertag_ctl — identical, but sightings._SPAN_M["inner"] is
                    monkeypatched IN MEMORY (code freeze respected) to the
                    per-tag size 0.010 m (geometry.INNER_TAG_SIZE_MM).
                    Expected per IS §3.2/§3.3: ~3 px < 20 px floor (and
                    below the 10 px ramp bottom) => ZERO inner detections
                    at 2.9 m — the IS8-2 dark window restored.

Deterministic: fixed root seed, no wall clock. Local only, no MuJoCo step
needed (perception injection is pure-python); runs in seconds on an M4.

Run:
  /Users/anayvaidya/Wyzantium/Ferrier/sim/.venv/bin/python \
      studies/R01_PHASE1_REVIEW/probes/probe_f008.py

Writes sim/results/review_r01/F-008/result.json.
"""

import json
import math
import subprocess
from collections import Counter
from pathlib import Path

from wyzantium_sim import geometry, params, scenarios
from wyzantium_sim.frames import Pose
from wyzantium_sim.kinematic.stage import Q_NOMINAL
from wyzantium_sim.perception import curves, detection, sightings
from wyzantium_sim.perception.inject import PerceptionInjector
from wyzantium_sim.perception.sightings import sightings_for

REPO = Path(__file__).resolve().parents[3]
OUT_DIR = REPO / "sim" / "results" / "review_r01" / "F-008"

SEED = 20260811          # fixed — probe determinism
N_FRAMES = 1000
RATE_HZ = 30.0
KNOCKOUT_MASK = 1        # bit 0: outer tag (ID 0) destroyed (#16 axis)
TRUTH_X_M = 2.9          # acquisition range (D-004 start is 3.0 m)
PER_TAG_SPAN_M = geometry.INNER_TAG_SIZE_MM * 0.001   # 0.010 m
_INJECTOR_KEYS = (       # trial.py:_INJECTOR_KEYS (frozen composition)
    "outer_occlusion", "inner_occlusion", "illuminance_lux", "rain",
    "dropout_p", "lens_contamination", "mud_f_c", "flip_kappa",
    "perception_rate_hz", "perception_latency_ms", "curve_set",
)


def _git_sha():
    out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, check=True,
                         capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain",
                            "--", "sim/wyzantium_sim", "sim/wirefmt"],
                           cwd=REPO, check=True, capture_output=True,
                           text=True).stdout.strip()
    return out + ("-dirty" if dirty else "")


def _nominal_injector_config():
    """Nominal degradation exactly as trial.py builds it (trial.py:143-144)."""
    sp = scenarios.load_scenario(
        scenarios.SCENARIO_DIR / "nominal.json")["sweep_point"]
    cfg = {k: sp[k] for k in _INJECTOR_KEYS}
    cfg["sigma_px"] = params.PARAMS[40].default
    return cfg


def _px_table(truth, cfg):
    """Per-sighting pixel extents under both span conventions, plus the
    analytic p_detect each convention yields (RNG-free arithmetic)."""
    curve = curves.get(cfg["curve_set"])
    f_px = {"A": params.PARAMS[19].value, "B": params.PARAMS[20].value}
    rows = []
    for s in sightings_for(truth, knockout_mask=KNOCKOUT_MASK):
        px_span = f_px[s.camera] * s.span_m / s.dist_m
        px_tag = f_px[s.camera] * PER_TAG_SPAN_M / s.dist_m
        common = dict(view_angle_rad=s.view_angle_rad,
                      mud_fraction=cfg["inner_occlusion"],
                      f_c=cfg["mud_f_c"],
                      illuminance_lux=cfg["illuminance_lux"], curve=curve)
        rows.append({
            "tag_id": s.tag_id, "camera": s.camera,
            "dist_m": round(s.dist_m, 6),
            "view_angle_deg": round(math.degrees(s.view_angle_rad), 3),
            "span_m_injected": s.span_m,
            "px_size_span_convention": round(px_span, 3),
            "px_size_per_tag_convention": round(px_tag, 3),
            "p_detect_span_convention": round(
                detection.p_detect(px_span, **common), 6),
            "p_detect_per_tag_convention": round(
                detection.p_detect(px_tag, **common), 6),
        })
    return rows


def _run_arm(truth, cfg):
    """N_FRAMES injector observations at a fixed truth pose. Fresh injector,
    same root seed per arm — arms differ only in the span convention that
    sightings_for embeds at call time."""
    injector = PerceptionInjector(root_seed=SEED, config=cfg)
    sights = sightings_for(truth, knockout_mask=KNOCKOUT_MASK)
    pose_sources = Counter()
    inner_det_hist = Counter()   # inner tags detected per frame -> frames
    frames_with_pose = 0
    frames_all8 = 0
    outer_detected_total = 0
    conf_sum = 0.0
    for i in range(N_FRAMES):
        line = injector.observe(i / RATE_HZ, truth, sights, "acquire")
        pose_sources[line["pose_source"]] += 1  # always set by observe()
        tags = line.get("tags") or []
        n_inner = sum(1 for t in tags if t["id"] != 0)
        outer_detected_total += sum(1 for t in tags if t["id"] == 0)
        inner_det_hist[n_inner] += 1
        if "pose" in line:
            frames_with_pose += 1
        if n_inner == 8:
            frames_all8 += 1
        conf_sum += line.get("conf", 0.0)
    n_inner_total = sum(k * v for k, v in inner_det_hist.items())
    return {
        "n_frames": N_FRAMES,
        "sightings_per_frame": len(sights),
        "span_m_in_effect": sights[0].span_m if sights else None,
        "inner_detections_total": n_inner_total,
        "mean_inner_tags_per_frame": round(n_inner_total / N_FRAMES, 4),
        "frames_with_all_8_inner": frames_all8,
        "frames_with_pose": frames_with_pose,
        "frames_pose_source_none": pose_sources.get("none", 0),
        "pose_source_counts": dict(sorted(pose_sources.items())),
        "inner_detected_histogram": {str(k): v for k, v in
                                     sorted(inner_det_hist.items())},
        "outer_detections_total": outer_detected_total,
        "mean_conf": round(conf_sum / N_FRAMES, 4),
    }


def main():
    truth = Pose((TRUTH_X_M, 0.0, 0.0), Q_NOMINAL)  # frozen nominal quat
    cfg = _nominal_injector_config()
    curve = curves.get(cfg["curve_set"])

    # ---- Arm 1: HEAD behavior (constellation-span convention, frozen) ----
    px_head = _px_table(truth, cfg)
    arm1 = _run_arm(truth, cfg)

    # ---- Arm 2: control — per-tag span monkeypatched in memory ----------
    saved = sightings._SPAN_M["inner"]
    try:
        sightings._SPAN_M["inner"] = PER_TAG_SPAN_M
        px_ctl = _px_table(truth, cfg)
        arm2 = _run_arm(truth, cfg)
    finally:
        sightings._SPAN_M["inner"] = saved

    # ---- Verdict ---------------------------------------------------------
    arm1_decodes = (arm1["mean_inner_tags_per_frame"] > 7.5
                    and arm1["frames_with_pose"] >= 0.99 * N_FRAMES
                    and arm1["pose_source_counts"].get(
                        "multi_tag_fused", 0) >= 0.99 * N_FRAMES)
    arm2_dark = (arm2["inner_detections_total"] == 0
                 and arm2["frames_with_pose"] == 0
                 and arm2["frames_pose_source_none"] == N_FRAMES)
    confirmed = bool(arm1_decodes and arm2_dark)

    result = {
        "finding": "F-008",
        "claim": ("Inner-tag decode pixel extent uses the 110 mm "
                  "constellation span; 10 mm tags decode at ~2.9 m, so "
                  "knockout_mask=1 (outer destroyed) still yields a full "
                  "fused pose at acquisition range, bypassing D-034 "
                  "dark-window semantics (IS8-2 basis)."),
        "clauses": ["IS §3.3 per-tag readability arithmetic "
                    "(10 mm => 39 px at 300 mm)",
                    "IS §3.2 20 px robust-decode floor",
                    "D-034 sustained dark window; FAILURE_TAXONOMY IS8-2"],
        "code_git_sha": _git_sha(),
        "probe": "studies/R01_PHASE1_REVIEW/probes/probe_f008.py",
        "seed": SEED,
        "n_frames": N_FRAMES,
        "truth_pose_m": {"t": [TRUTH_X_M, 0.0, 0.0],
                         "q": list(Q_NOMINAL),
                         "note": "frozen Q_NOMINAL as-committed (see F-012; "
                                 "this probe tests F-008 at HEAD behavior)"},
        "knockout_mask": KNOCKOUT_MASK,
        "config": cfg,
        "curve": {"detection_onset_px": curve.detection_onset_px,
                  "detection_onset_width_px": curve.detection_onset_width_px,
                  "ramp_bottom_px": (curve.detection_onset_px
                                     - curve.detection_onset_width_px)},
        "focal_px": {"A": params.PARAMS[19].value,
                     "B": params.PARAMS[20].value},
        "span_conventions_m": {"constellation_span": saved,
                               "per_tag": PER_TAG_SPAN_M},
        "px_table_arm1_head_span": px_head,
        "px_table_arm2_per_tag": px_ctl,
        "arm1_head_span": arm1,
        "arm2_pertag_control": arm2,
        "verdict": {
            "arm1_inner_ring_decodes_at_2p9m": bool(arm1_decodes),
            "arm2_zero_inner_detections": bool(arm2_dark),
            "confirmed": confirmed,
        },
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "result.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        f.write("\n")

    print(f"F-008 probe → {out}")
    print(f"  arm1 (HEAD, span 0.11):  mean inner/frame ="
          f" {arm1['mean_inner_tags_per_frame']}, all-8 frames ="
          f" {arm1['frames_with_all_8_inner']}/{N_FRAMES}, pose_source ="
          f" {arm1['pose_source_counts']}, mean conf = {arm1['mean_conf']}")
    print(f"  arm2 (ctl, span 0.010): inner detections ="
          f" {arm2['inner_detections_total']}, pose_source ="
          f" {arm2['pose_source_counts']}")
    px1 = px_head[0]["px_size_span_convention"] if px_head else None
    px2 = px_head[0]["px_size_per_tag_convention"] if px_head else None
    print(f"  px extent at 2.9 m: span-convention ~{px1} px vs per-tag"
          f" ~{px2} px vs {curve.detection_onset_px} px floor")
    print(f"  CONFIRMED = {confirmed}")
    return confirmed


if __name__ == "__main__":
    main()
