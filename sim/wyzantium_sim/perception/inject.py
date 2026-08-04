"""D-007: perception is injected, not rendered — the injection orchestrator.

Consumes ground truth (T_head_stud) plus a per-frame scene description (which
tags could geometrically be seen, at what range/angle/camera — supplied by
the kinematic stage from T5 onward; NOTE: `truth.t` here must be METRES per
the WIRE_FORMAT pose contract, while the kinematic stage produces mm — the
T8 trial composition owns that /1000 conversion) and emits WIRE_FORMAT
target_state lines: detections sampled per #39/D-023/#43–#45, pose noise per #40 through
the #19/#20 camera models, flips per studies/H08 §4, timing per #37/#38.
Omitted-not-zeroed is enforced structurally: a frame with no detections
carries no pose/pose_cov/tags at all.

Arbitrary code-level choices, labeled: conf = evidence mass of the detected
tags, 1 − Π(1 − p_i), scaled by min(1, worst ambiguity ratio) — revised
from mean-p 2026-08-04 (T8 composition finding: the mean under-reported
multi-tag evidence and sat structurally below the #30 commit threshold at
close range, where per-tag p ≈ cos(view angle) is low while the fused
constellation is excellent); lens contamination applies to Cam B only
(#44 names Cam B dominant); layout defaults to coplanar (D-011 selection
is MR-003's; coplanar is the conservative flip case).
"""
import math
from dataclasses import dataclass

from wyzantium_sim import params, rng
from wyzantium_sim.frames import Pose
from wyzantium_sim.perception import (
    curves, detection, dropout, flip, noise, timing,
)

REQUIRED_KEYS = (
    "outer_occlusion", "inner_occlusion", "illuminance_lux", "rain",
    "dropout_p", "lens_contamination", "mud_f_c", "flip_kappa", "sigma_px",
    "perception_rate_hz", "perception_latency_ms", "curve_set",
)

_FOCAL_PX = {"A": params.PARAMS[19].value, "B": params.PARAMS[20].value}


class ConfigError(ValueError):
    pass


def _conf(ps, ratio):
    """Evidence-mass confidence proxy (labeled arbitrary, see module
    docstring): 1 − Π(1 − p_i) over the detected tags, ambiguity-scaled."""
    miss = 1.0
    for p in ps:
        miss *= 1.0 - p
    return max(0.0, min(1.0, (1.0 - miss) * min(1.0, ratio)))


@dataclass(frozen=True)
class TagSighting:
    """One geometrically-possible tag observation this frame. span_m is the
    size driving both decode (px extent) and flip discriminability for this
    sighting's context — the tag for a lone tag, the visible constellation
    span for fused inner-ring frames."""
    tag_id: int
    camera: str
    dist_m: float
    view_angle_rad: float
    span_m: float


class PerceptionInjector:
    def __init__(self, root_seed, config, layout="coplanar",
                 standoff_observable=False):
        missing = [k for k in REQUIRED_KEYS if k not in config]
        if missing:
            raise ConfigError(f"missing config keys: {', '.join(missing)}")
        self.config = dict(config)
        self.curve = curves.get(config["curve_set"])
        self.layout = layout
        self.standoff_observable = standoff_observable
        self._det = rng.substream(root_seed, "perception.detection")
        self._noise = rng.substream(root_seed, "perception.noise")
        self._flip = rng.substream(root_seed, "perception.flip")
        self._dropout = dropout.FrameDropout(
            rng.substream(root_seed, "perception.dropout"),
            p=config["dropout_p"],
        )

    def observe(self, t, truth, sightings, stage):
        cfg = self.config
        line = {
            "v": 1,
            "type": "target_state",
            "t_capture": t,
            "t_emit": timing.emit_time(t, cfg["perception_latency_ms"]),
            "stage": stage,
        }

        if self._dropout.sample():
            line["pose_source"] = "none"
            line["conf"] = 0.0
            line["degradation"] = {
                "dropout": True,
                "illuminance_lux": cfg["illuminance_lux"],
            }
            return line

        detected = []
        for s in sightings:
            occ = (cfg["outer_occlusion"] if s.tag_id == 0
                   else cfg["inner_occlusion"])
            px_size = _FOCAL_PX[s.camera] * s.span_m / s.dist_m
            p = detection.p_detect(
                px_size, s.view_angle_rad, occ, cfg["mud_f_c"],
                cfg["illuminance_lux"], self.curve,
            )
            p *= dropout.rain_factor(cfg["rain"])
            if s.camera == "B":
                p *= dropout.contamination_factor(cfg["lens_contamination"])
            if self._det.random() < p:
                detected.append((s, p))

        occ_est = max(
            (cfg["outer_occlusion"] if s.tag_id == 0
             else cfg["inner_occlusion"])
            for s in sightings
        ) if sightings else 0.0
        line["degradation"] = {
            "occlusion_est": occ_est,
            "illuminance_lux": cfg["illuminance_lux"],
        }

        if not detected:
            line["pose_source"] = "none"
            line["conf"] = 0.0
            return line

        inner_ids = [s.tag_id for s, _ in detected if s.tag_id != 0]
        if len(detected) >= 2:
            line["pose_source"] = "multi_tag_fused"
        elif inner_ids:
            line["pose_source"] = "inner_ring"
        else:
            line["pose_source"] = "outer_tag"

        # Representative geometry: the nearest detected sighting.
        rep, _ = min(detected, key=lambda pair: pair[0].dist_m)
        f_px = _FOCAL_PX[rep.camera]
        sigma = cfg["sigma_px"]
        cov = noise.pose_cov_upper21(sigma, f_px, rep.dist_m, rep.span_m)
        sig = [math.sqrt(cov[0]), math.sqrt(cov[6]), math.sqrt(cov[11]),
               math.sqrt(cov[15]), math.sqrt(cov[15]), math.sqrt(cov[15])]
        draws = self._noise.standard_normal(6)
        t_noisy = tuple(truth.t[i] + draws[i] * sig[i] for i in range(3))
        half = [0.5 * draws[3 + i] * sig[3 + i] for i in range(3)]
        norm = math.sqrt(1.0 + sum(h * h for h in half))
        dq = (1.0 / norm, half[0] / norm, half[1] / norm, half[2] / norm)
        noisy = Pose(t_noisy, truth.q).compose(Pose((0.0, 0.0, 0.0), dq))

        d_px = flip.discriminability(
            f_px, rep.span_m, rep.dist_m, rep.view_angle_rad
        )
        p_fl = flip.p_flip_for_layout(
            d_px, sigma, cfg["flip_kappa"], self.layout,
            n_tags_visible=len(detected),
            standoff_observable=self.standoff_observable,
        )
        flipped = bool(self._flip.random() < p_fl)
        q_out = (flip.reflect_about_boresight(noisy.q) if flipped
                 else noisy.q)
        ratio = d_px / (flip.K_THRESHOLD * sigma)

        line["pose"] = {"t": list(noisy.t), "q": list(q_out)}
        line["pose_cov"] = cov
        line["tags"] = [
            {"id": s.tag_id,
             "reproj_err": float(abs(self._noise.normal(0.0, sigma))),
             "ambiguity_flag": bool(flipped or ratio < 1.0),
             "ambiguity_ratio": float(ratio)}
            for s, _ in detected
        ]
        line["conf"] = _conf([p for _, p in detected], ratio)
        return line
