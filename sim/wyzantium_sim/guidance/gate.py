"""The confidence gate (D-013/D-017, #29/#30).

Commit predicate, exact (#30): pose_source = multi_tag_fused ∧ stage =
inner_servo ∧ conf ≥ conf_min_attempt. Two additional committed constraints
are enforced here because the gate is the last decision layer before
actuation:

- ≥2 INNER-ring tags (id != 0): H-08 / IS §10 item 10 / IS §8 row 3 all mean
  two inner tags, while the perception injector labels any ≥2 detections
  multi_tag_fused (outer id-0 + one inner would pass a pose_source-only
  check). Flagged inconsistency (2026-08-04); the gate enforces the stricter
  reading. When no tag array is present the pose_source value is trusted.
- D-018 (#24): heading within the ±20° cone of the stud +X axis, computed
  from T_head_stud alone — the anti-parallel nominal (IS §4) is 0°.

The gate never mutates state and consumes only the wire line — it is the
"between the stream and every consumer that can move steel" check
(ARCHITECTURE §2). Refusal semantics (escalate, imagery, human) live in
machine.py; this module only answers "may steel move on this frame?".
"""

from __future__ import annotations

import math

from wyzantium_sim import frames

REQUIRED_FIELDS = ("type", "t_capture", "t_emit", "pose_source", "conf",
                   "stage")
SECTOR_DEG = 20.0        # #24, D-018, normative
INNER_TAGS_MIN = 2       # H-08 / IS §8 row 3
# D-045: WIRE_FORMAT consumer-checklist item 4 realized — capture-age beyond
# the staleness bound ⇒ pose-absent. The bound is the #38 committed latency
# sweep ceiling (a labeled class value taken from the committed sweep, not
# measured): consumers tolerate up to the swept ceiling; older is stale.
STALENESS_BOUND_S = 0.100

_HEAD_AXIS_NOMINAL = (-1.0, 0.0, 0.0)  # stud +X at anti-parallel engagement


def heading_misalign_deg(q) -> float:
    """Angle between the stud +X axis (from T_head_stud's rotation) and the
    anti-parallel nominal."""
    axis = frames.Pose(t=(0.0, 0.0, 0.0), q=tuple(q)).apply((1.0, 0.0, 0.0))
    dot = sum(a * b for a, b in zip(axis, _HEAD_AXIS_NOMINAL))
    return math.degrees(math.acos(max(-1.0, min(1.0, dot))))


def commit_allowed(line: dict, conf_min: float,
                   sector_deg: float = SECTOR_DEG) -> tuple:
    """(allowed, reason). Applies the WIRE_FORMAT consumer checklist's gate
    step plus the #30 predicate; reasons name the failed conjunct."""
    if line.get("v") != 1:
        return False, "version: v != 1"
    for f in REQUIRED_FIELDS:
        if f not in line:
            return False, f"required field {f} missing"
    if line["t_emit"] - line["t_capture"] > STALENESS_BOUND_S + 1e-9:
        return False, (f"stale: capture age {line['t_emit'] - line['t_capture']:.3f}s "
                       f"beyond the {STALENESS_BOUND_S}s bound — treated "
                       "pose-absent (WIRE_FORMAT checklist 4, D-045)")
    if line["pose_source"] != "multi_tag_fused":
        return False, f"pose_source is {line['pose_source']!r}, not multi_tag_fused"
    if line["stage"] != "inner_servo":
        return False, f"stage is {line['stage']!r}, not inner_servo"
    if line["conf"] < conf_min:
        return False, f"conf {line['conf']} below threshold {conf_min}"
    tags = line.get("tags")
    if tags is not None:
        inner = [t for t in tags if t.get("id") != 0]
        if len(inner) < INNER_TAGS_MIN:
            return False, (f"only {len(inner)} inner-ring tags decoded "
                           f"(≥{INNER_TAGS_MIN} required, H-08)")
        flagged = [t.get("id") for t in tags if t.get("ambiguity_flag")]
        if flagged:
            # D-044 (R01 F-005): a row-5-rejected frame is not commit
            # evidence — IS §8 row 5 says reject; committing is acting.
            return False, (f"ambiguity_flag set on tag(s) {flagged} — "
                           "rejected frames are not commit evidence "
                           "(IS §8 row 5, D-044)")
    pose = line.get("pose")
    if pose is None:
        # WIRE_FORMAT: absent pose means "no pose available this frame —
        # guidance must not act on position (D-013)"; committing is acting.
        return False, "pose absent — cannot commit without a pose (D-013)"
    mis = heading_misalign_deg(pose["q"])
    if mis > sector_deg:
        return False, (f"heading {mis:.1f}° outside the ±{sector_deg}° "
                       "D-018 sector")
    return True, "commit"
