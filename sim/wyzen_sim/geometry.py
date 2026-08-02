"""D-016 dimension set and the INTERFACE_SPEC §3.5 tag constellation.

All lengths in mm, frames per IS §4. These constants are the same numbers as
the matching PHASE1_PARAMETERS entries — tests/test_geometry.py cross-checks
them; changing any is a recorded decision revision, not a code edit (D-016).
"""
import math

from wyzen_sim.frames import Pose

# Stud and funnel (D-016; IS §2, §6)
STUD_NECK_DIAMETER_MM = 25.0
STUD_HEAD_DIAMETER_MM = 40.0
STUD_EXPOSED_LENGTH_MM = 90.0
FUNNEL_MOUTH_DIAMETER_MM = 220.0
FUNNEL_THROAT_DIAMETER_MM = 42.0
FUNNEL_DEPTH_MM = 180.0
PLATE_ENVELOPE_MM = (200.0, 200.0)

# Capture geometry (IS §6, D-006)
LIP_BAND_MM = (110.0, 125.0)
ANNULUS_RADIUS_MM = 160.0
HANDOFF_TRIGGER_X_MM = 50.0

# Fiducial constellation (IS §3.2, §3.3, §3.5)
OUTER_TAG_SIZE_MM = 150.0
OUTER_TAG_CENTER_MM = (0.0, 0.0, 185.0)
INNER_RING_COUNT = 8
INNER_TAG_SIZE_MM = 10.0
INNER_RING_RADIUS_MM = 55.0
INNER_RING_PITCH_DEG = 45.0

# §3.5: all tag faces normal +X_stud, upright — +Z_tag ∥ +X_stud,
# +Y_tag ∥ +Z_stud. That axis permutation is the 120° rotation about
# (1,1,1)/√3: q = (1/2, 1/2, 1/2, 1/2).
_Q_TAG = (0.5, 0.5, 0.5, 0.5)

# §3.4/§3.5 ID allocation: IDs 0–15 = variant 0 (0 outer, 1–8 inner,
# 9–15 reserved). A decoded ID outside the block is a rejection (§8 row 14).
VARIANT_0_IDS = range(0, 16)


def is_expected_id(tag_id):
    return tag_id in VARIANT_0_IDS


def tag_table(h_mm=0.0):
    """Tag ID → T_stud_tag per the §3.5 rule.

    h_mm is the inner-ring standoff: 0 for layout L-A (coplanar), the swept
    collar height h_c for L-B. The outer tag never moves.
    """
    table = {0: Pose(OUTER_TAG_CENTER_MM, _Q_TAG)}
    for k in range(1, INNER_RING_COUNT + 1):
        alpha = math.radians(INNER_RING_PITCH_DEG * (k - 1))
        center = (float(h_mm),
                  -INNER_RING_RADIUS_MM * math.sin(alpha),
                  INNER_RING_RADIUS_MM * math.cos(alpha))
        table[k] = Pose(center, _Q_TAG)
    return table
