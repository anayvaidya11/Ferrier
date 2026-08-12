"""R01 L2 probe — F-007: lone inner-tag frames use the full 110 mm
constellation span for flip discriminability, making them flip-immune.

Clause under test
-----------------
- D-011 qualification (2026-08-01, from studies/H08): "a lone 10 mm tag
  cannot self-disambiguate the two-solution ambiguity at any view angle at
  inner-servo ranges (discriminability ~1.4 px, below the noise floor)".
- studies/H08 SS2 table: single inner tag, S = 10 mm, Cam B at 0.25 m ->
  f*S^2/d^2 = 1.4 px, "no solution — a lone inner tag cannot
  self-disambiguate at any angle". SS4: coplanar flip model uses D from SS2
  with the *visible* span.
- WIRE_FORMAT worked example 3: a single near-head-on inner tag emits
  ambiguity_ratio 1.08, ambiguity_flag true.

Observed code behavior (the finding): sightings.py:69 hard-codes
span_m = _SPAN_M["inner"] = 0.11 (2 x 55 mm ring radius) for EVERY inner
tag regardless of how many are visible, so a lone tag inherits the full
constellation's discriminability (~139 px at 0.246 m / 52 deg) and can
never flag or flip.

Probe design (probe33 style: failing condition + nominal control)
-----------------------------------------------------------------
Both arms drive the frozen PerceptionInjector directly (no MuJoCo, no
cloud) with knockout_mask = 503 = 0b111110111 — every tag destroyed except
inner tag 3 — over N = 3000 frames at deterministic sampled inner-servo
poses (root seed 20260804 for poses AND injector substreams; identical
pose list and identical detection draws in both arms, so the detected
frame sets are paired).

- Arm 1 (HEAD, FAILING): sightings_for() as frozen -> lone tag 3 carries
  span_m = 0.11. Record ambiguity_flag rate, min ambiguity_ratio, the
  p_flip the injector actually used (flip.p_flip_for_layout instrumented),
  and realized flips (flip.reflect_about_boresight instrumented).
- H08 expectation, computed per detected frame from the same realized
  geometry with the doc's lone-tag span S = 0.010 m:
  D_doc = f_B * S^2 * sin(view)/d^2, ratio_doc = D_doc/(k*sigma_px),
  p_doc = min(0.5, 0.5*max(0, 1 - ratio_doc)*kappa), k = 3,
  sigma_px = 0.5 (PARAMS #40 default, as trial.py pins), kappa = 1.0
  (nominal flip_kappa).
- Arm 2 (CONTROL): in-memory monkeypatch of the span convention only —
  when a frame's visible inner count is 1, that sighting's span_m becomes
  0.010 (geometry.INNER_TAG_SIZE_MM). Everything else identical. Per H08
  the flags/flips must appear at the doc-expected scale.

Config: committed nominal sweep point (sim/scenarios/nominal.json) +
sigma_px pinned at PARAMS[40].default exactly as trial.py:144 does.
Detection is unaffected by the span swap here (both px extents sit above
the 20 px prior_v1 onset), so both arms detect the same frames — the ONLY
live difference is the span fed to flip discriminability.

Verdict rule
------------
CONFIRMED iff Arm 1 shows flag rate 0, min ratio > 10, p_flip
identically 0, zero flips, WHILE the doc expectation over the same frames
is materially flip-prone (mean p_doc > 0.05) and Arm 2 realizes it:
flag rate > 0.9, ratio < 1 frames present, injector-used p_flip equal to
the doc formula (|diff| < 1e-9), realized flips within 3 sigma of the
binomial expectation. Otherwise REFUTED.

Re-run
------
  /Users/anayvaidya/Wyzantium/Ferrier/sim/.venv/bin/python \
      studies/R01_PHASE1_REVIEW/probes/probe_f007.py

Writes sim/results/review_r01/F-007/result.json. Deterministic: fixed
seeds, no wall clock. Code freeze respected: monkeypatching is in-memory
only, inside this process.
"""
import json
import math
import pathlib
import subprocess
import sys

import numpy as np

REPO = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "sim"))

from wyzantium_sim import geometry, params                     # noqa: E402
from wyzantium_sim.frames import Pose                          # noqa: E402
from wyzantium_sim.kinematic.stage import Q_NOMINAL            # noqa: E402
from wyzantium_sim.perception import flip, inject, sightings   # noqa: E402

ROOT_SEED = 20260804
N_FRAMES = 3000
KNOCKOUT_MASK = 503          # 0b111110111: all tags gone except inner tag 3
LONE_TAG_ID = 3
S_DOC_M = geometry.INNER_TAG_SIZE_MM * 0.001   # 0.010 — H08 lone-tag span
SPAN_HEAD_M = 2.0 * geometry.INNER_RING_RADIUS_MM * 0.001  # 0.11 frozen
F_B_PX = params.PARAMS[20].value               # 880 px, Cam B
K = flip.K_THRESHOLD                           # 3.0, H08 SS2
OUT_DIR = REPO / "sim" / "results" / "review_r01" / "F-007"

# Inner-servo pose window (T_head_stud, metres, frozen Q_NOMINAL attitude):
# chosen so lone tag 3 sits at ~0.25-0.29 m from Cam B at ~52-60 deg view —
# the H08 SS2 lone-inner-tag regime (doc row: 0.25 m, "no solution").
X_RANGE = (0.24, 0.26)
Y_RANGE = (0.01, 0.05)
Z_RANGE = (-0.02, 0.02)


def build_config():
    nominal = json.loads(
        (REPO / "sim" / "scenarios" / "nominal.json").read_text()
    )["sweep_point"]
    cfg = {k: nominal[k] for k in inject.REQUIRED_KEYS if k in nominal}
    # trial.py:144 behavior: sigma_px pinned at the PARAMS #40 default.
    cfg["sigma_px"] = params.PARAMS[40].default
    assert set(cfg) == set(inject.REQUIRED_KEYS), sorted(
        set(inject.REQUIRED_KEYS) - set(cfg))
    return cfg


def sample_poses():
    rng = np.random.default_rng(ROOT_SEED)
    xs = rng.uniform(*X_RANGE, N_FRAMES)
    ys = rng.uniform(*Y_RANGE, N_FRAMES)
    zs = rng.uniform(*Z_RANGE, N_FRAMES)
    return [Pose((xs[i], ys[i], zs[i]), Q_NOMINAL) for i in range(N_FRAMES)]


class FlipRecorder:
    """In-memory instrumentation of the frozen flip module (no file edits)."""

    def __init__(self):
        self.p_used = []      # p_flip the injector consumed, per call
        self.d_used = []      # discriminability px the injector consumed
        self.flips = 0        # reflect_about_boresight invocations

    def install(self):
        self._orig_pfl = flip.p_flip_for_layout
        self._orig_ref = flip.reflect_about_boresight

        def rec_pfl(d_px, sigma_px, kappa, layout, n_tags_visible,
                    standoff_observable, k=flip.K_THRESHOLD):
            p = self._orig_pfl(d_px, sigma_px, kappa, layout,
                               n_tags_visible=n_tags_visible,
                               standoff_observable=standoff_observable, k=k)
            self.d_used.append(float(d_px))
            self.p_used.append(float(p))
            return p

        def rec_ref(q):
            self.flips += 1
            return self._orig_ref(q)

        flip.p_flip_for_layout = rec_pfl
        flip.reflect_about_boresight = rec_ref

    def uninstall(self):
        flip.p_flip_for_layout = self._orig_pfl
        flip.reflect_about_boresight = self._orig_ref


def lone_span_control(sights):
    """Arm-2 monkeypatch of the span convention: a lone visible inner tag
    carries its OWN 10 mm size (H08 SS2 lone-tag row), not the 110 mm
    constellation span. Multi-tag frames untouched."""
    inner = [s for s in sights if s.tag_id != 0]
    if len(inner) != 1:
        return sights
    return [
        inject.TagSighting(
            tag_id=s.tag_id, camera=s.camera, dist_m=s.dist_m,
            view_angle_rad=s.view_angle_rad,
            span_m=S_DOC_M if s.tag_id != 0 else s.span_m)
        for s in sights
    ]


def h08_expected(dist_m, view_rad, sigma_px, kappa):
    """H08 SS2+SS4 with the doc's lone-tag span S = 0.010 m."""
    d_doc = flip.discriminability(F_B_PX, S_DOC_M, dist_m, view_rad)
    ratio_doc = d_doc / (K * sigma_px)
    p_doc = flip.p_flip(d_doc, sigma_px, kappa)
    return d_doc, ratio_doc, p_doc


def run_arm(poses, cfg, control):
    rec = FlipRecorder()
    rec.install()
    try:
        injector = inject.PerceptionInjector(
            ROOT_SEED, cfg, layout="coplanar", standoff_observable=False)
        rate = cfg["perception_rate_hz"]
        stats = {
            "detected_frames": 0, "flag_count": 0, "ratios": [],
            "dists": [], "views_deg": [], "spans": [], "px_sizes": [],
            "p_doc": [], "detected_idx": [],
        }
        for i, truth in enumerate(poses):
            sights = sightings.sightings_for(
                truth, knockout_mask=KNOCKOUT_MASK, h_mm=0.0)
            assert len(sights) == 1, f"frame {i}: expected lone sighting"
            s = sights[0]
            assert s.tag_id == LONE_TAG_ID and s.camera == "B"
            if control:
                sights = lone_span_control(sights)
                s = sights[0]
            line = injector.observe(i / rate, truth, sights, "inner_servo")
            if "tags" not in line:
                continue
            (tag,) = line["tags"]
            assert tag["id"] == LONE_TAG_ID
            stats["detected_frames"] += 1
            stats["detected_idx"].append(i)
            stats["flag_count"] += bool(tag["ambiguity_flag"])
            stats["ratios"].append(tag["ambiguity_ratio"])
            stats["dists"].append(s.dist_m)
            stats["views_deg"].append(math.degrees(s.view_angle_rad))
            stats["spans"].append(s.span_m)
            stats["px_sizes"].append(F_B_PX * s.span_m / s.dist_m)
            _, _, p_doc = h08_expected(
                s.dist_m, s.view_angle_rad, cfg["sigma_px"],
                cfg["flip_kappa"])
            stats["p_doc"].append(p_doc)
    finally:
        rec.uninstall()
    n = stats["detected_frames"]
    assert len(rec.p_used) == n, "one flip-model call per detected frame"
    p_doc_sum = float(sum(stats["p_doc"]))
    p_doc_var = float(sum(p * (1.0 - p) for p in stats["p_doc"]))
    summary = {
        "arm": "lone_span_0.010_CONTROL" if control else "head_span_0.11_FAILING",
        "span_m_used": sorted(set(round(v, 6) for v in stats["spans"])),
        "n_frames": N_FRAMES,
        "n_detected": n,
        "dist_m_range": [min(stats["dists"]), max(stats["dists"])],
        "view_deg_range": [min(stats["views_deg"]), max(stats["views_deg"])],
        "px_size_range": [min(stats["px_sizes"]), max(stats["px_sizes"])],
        "flag_count": stats["flag_count"],
        "flag_rate": stats["flag_count"] / n,
        "ambiguity_ratio_min": min(stats["ratios"]),
        "ambiguity_ratio_max": max(stats["ratios"]),
        "p_flip_used_min": min(rec.p_used),
        "p_flip_used_max": max(rec.p_used),
        "p_flip_used_mean": float(np.mean(rec.p_used)),
        "flips_realized": rec.flips,
        "flip_rate_realized": rec.flips / n,
        "h08_expected_S0.010": {
            "p_flip_mean": p_doc_sum / n,
            "expected_flips": p_doc_sum,
            "binomial_3sigma": 3.0 * math.sqrt(p_doc_var),
        },
        "p_flip_used_vs_h08_maxabsdiff": float(max(
            abs(pu - pd) for pu, pd in zip(rec.p_used, stats["p_doc"]))),
    }
    return summary, stats


def main():
    cfg = build_config()
    poses = sample_poses()

    arm1, s1 = run_arm(poses, cfg, control=False)
    arm2, s2 = run_arm(poses, cfg, control=True)

    # Paired arms: identical detection draws and identical p_detect (both px
    # extents above the 20 px onset) -> same detected frame set.
    paired = s1["detected_idx"] == s2["detected_idx"]

    exp = arm2["h08_expected_S0.010"]
    arm1_flip_immune = (
        arm1["flag_count"] == 0
        and arm1["ambiguity_ratio_min"] > 10.0
        and arm1["p_flip_used_max"] == 0.0
        and arm1["flips_realized"] == 0
    )
    doc_expects_flips = arm1["h08_expected_S0.010"]["p_flip_mean"] > 0.05
    arm2_matches_h08 = (
        arm2["flag_rate"] > 0.9
        and arm2["ambiguity_ratio_max"] < 1.0
        and arm2["p_flip_used_vs_h08_maxabsdiff"] < 1e-9
        and abs(arm2["flips_realized"] - exp["expected_flips"])
        <= exp["binomial_3sigma"]
        and arm2["flips_realized"] > 0
    )
    confirmed = bool(
        arm1_flip_immune and doc_expects_flips and arm2_matches_h08 and paired)

    sha = subprocess.run(
        ["git", "-C", str(REPO), "rev-parse", "HEAD"],
        capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(
        ["git", "-C", str(REPO), "status", "--porcelain",
         "sim/wyzantium_sim", "sim/wirefmt", "sim/tests"],
        capture_output=True, text=True).stdout.strip()

    result = {
        "finding": "F-007",
        "probe": "studies/R01_PHASE1_REVIEW/probes/probe_f007.py",
        "clause": ("D-011 qualification (lone 10 mm tag cannot "
                   "self-disambiguate); studies/H08 SS2 lone-inner-tag row + "
                   "SS4 (D from the *visible* span); WIRE_FORMAT worked "
                   "example 3 (lone tag -> ratio 1.08, flag true)"),
        "code_git_sha": sha + ("-dirty-sim" if dirty else ""),
        "root_seed": ROOT_SEED,
        "n_frames": N_FRAMES,
        "knockout_mask": KNOCKOUT_MASK,
        "lone_tag_id": LONE_TAG_ID,
        "config": cfg,
        "layout": "coplanar",
        "pose_window_m": {"x": X_RANGE, "y": Y_RANGE, "z": Z_RANGE,
                          "q": list(Q_NOMINAL)},
        "focal_b_px": F_B_PX,
        "spans_m": {"frozen_inner_constellation": SPAN_HEAD_M,
                    "h08_lone_tag": S_DOC_M},
        "arms": {"arm1_head_FAILING": arm1, "arm2_control_H08_span": arm2},
        "detected_sets_paired": paired,
        "checks": {
            "arm1_flip_immune_at_head": arm1_flip_immune,
            "h08_expects_flip_prone_here": doc_expects_flips,
            "arm2_realizes_h08_scale": arm2_matches_h08,
        },
        "verdict": "CONFIRMED" if confirmed else "REFUTED",
        "confirmed": confirmed,
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "result.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    print(f"\nwrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
