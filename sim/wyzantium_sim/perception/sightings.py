"""T8 — truth pose → per-frame TagSighting list (pure geometry, no RNG).

Builds the scene description the PerceptionInjector consumes: for each tag
in the IS §3.5 constellation, whether its face points back at its camera,
at what range and view angle. Detection realism (decode floor, occlusion,
illumination) is entirely the injector's job — this module never thresholds
on distance or pixel size.

Arbitrary code-level choices (spec gaps, chassis_error precedent):
- Camera roles are fixed per D-012: cam A sees the outer tag (id 0), cam B
  the inner ring (ids 1-8). No FOV cone is modeled — a tag is sighted iff
  its face normal points into the hemisphere containing its camera
  (view angle < 90°); the injector's px-size curve handles the rest.
- span_m follows the injector's own convention (inject.TagSighting
  docstring): the tag size for the lone outer tag (0.15), the visible
  constellation span for inner-ring frames (0.11 = 2 x 55 mm ring radius).
- knockout_mask bit k removes tag k (the #16 tag_knockout_mask sweep axis).

Units: truth pose and all returns are METRES (WIRE_FORMAT contract);
geometry.tag_table and the PARAMS extrinsics are mm and converted here.
"""
import math

from wyzantium_sim import geometry, params
from wyzantium_sim.frames import Pose
from wyzantium_sim.perception.inject import TagSighting

_MM = 0.001

# Camera positions in head_frame, metres (PARAMS 17/18 extrinsics).
_CAM_T_M = {
    "A": tuple(v * _MM for v in params.PARAMS[17].value["t_mm"]),
    "B": tuple(v * _MM for v in params.PARAMS[18].value["t_mm"]),
}
_SPAN_M = {
    "outer": geometry.OUTER_TAG_SIZE_MM * _MM,
    "inner": 2.0 * geometry.INNER_RING_RADIUS_MM * _MM,
}


def _camera_for(tag_id):
    return "A" if tag_id == 0 else "B"


def sightings_for(truth_m: Pose, knockout_mask: int = 0,
                  h_mm: float = 0.0) -> list:
    """TagSighting list for one frame, from T_head_stud in METRES."""
    out = []
    for tag_id, t_stud_tag in geometry.tag_table(h_mm).items():
        if (knockout_mask >> tag_id) & 1:
            continue
        t_stud_tag_m = Pose(tuple(v * _MM for v in t_stud_tag.t),
                            t_stud_tag.q)
        t_head_tag = truth_m.compose(t_stud_tag_m)
        center = t_head_tag.t
        # Tag face normal = +Z_tag expressed in head_frame.
        normal = tuple(a - b for a, b in zip(t_head_tag.apply((0.0, 0.0, 1.0)),
                                             center))
        camera = _camera_for(tag_id)
        cam = _CAM_T_M[camera]
        to_cam = tuple(c - p for c, p in zip(cam, center))
        dist = math.sqrt(sum(v * v for v in to_cam))
        cos = sum(n * v for n, v in zip(normal, to_cam)) / dist
        if cos <= 0.0:
            continue  # face points away from its camera
        out.append(TagSighting(
            tag_id=tag_id, camera=camera, dist_m=dist,
            view_angle_rad=math.acos(min(1.0, cos)),
            span_m=_SPAN_M["outer" if tag_id == 0 else "inner"]))
    return out
