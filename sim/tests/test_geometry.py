"""D-016 dimension set and the INTERFACE_SPEC §3.5 tag table.

The §3.5 rule, transcribed independently here: ID 0 (outer) at
(0, 0, +185) mm in stud_frame; IDs 1–8 (inner ring, k = 1..8) at
(h, −55·sin α_k, +55·cos α_k) with α_k = 45°·(k−1); h = 0 (layout L-A) or
h_c (L-B). All tag faces normal +X_stud, upright: +Z_tag ∥ +X_stud,
+Y_tag ∥ +Z_stud. Geometry constants must equal the matching
PHASE1_PARAMETERS entries — a cross-check, not a re-declaration.
"""
import math

from wyzantium_sim import frames, geometry, params


def approx3(a, b, tol=1e-9):
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def test_tag_table_covers_variant_0_constellation():
    table = geometry.tag_table()
    assert sorted(table.keys()) == list(range(0, 9))


def test_outer_tag_center_from_spec():
    assert approx3(geometry.tag_table()[0].t, (0.0, 0.0, 185.0))


def test_inner_ring_centers_follow_the_spec_rule():
    table = geometry.tag_table()
    for k in range(1, 9):
        alpha = math.radians(45.0 * (k - 1))
        expected = (0.0, -55.0 * math.sin(alpha), 55.0 * math.cos(alpha))
        assert approx3(table[k].t, expected), f"ID {k}"
    # Spot anchors: first tag at 12 o'clock (+Z); quarter points.
    assert approx3(table[1].t, (0.0, 0.0, 55.0))
    assert approx3(table[3].t, (0.0, -55.0, 0.0))
    assert approx3(table[5].t, (0.0, 0.0, -55.0))
    assert approx3(table[7].t, (0.0, 55.0, 0.0))


def test_collar_standoff_moves_inner_ring_only():
    table = geometry.tag_table(h_mm=25.0)
    assert approx3(table[0].t, (0.0, 0.0, 185.0))
    for k in range(1, 9):
        assert table[k].t[0] == 25.0


def test_tag_orientation_axes():
    # +Z_tag ∥ +X_stud and +Y_tag ∥ +Z_stud, for every tag.
    for tag_id, pose in geometry.tag_table().items():
        rot = frames.Pose((0.0, 0.0, 0.0), pose.q)
        assert approx3(rot.apply((0.0, 0.0, 1.0)), (1.0, 0.0, 0.0)), \
            f"ID {tag_id}: +Z_tag must map to +X_stud"
        assert approx3(rot.apply((0.0, 1.0, 0.0)), (0.0, 0.0, 1.0)), \
            f"ID {tag_id}: +Y_tag must map to +Z_stud"


def test_variant_0_id_block():
    # §3.4/§3.5: IDs 0–15 = variant 0; outside the block = rejection (row 14).
    assert geometry.VARIANT_0_IDS == range(0, 16)
    assert geometry.is_expected_id(8) and geometry.is_expected_id(15)
    assert not geometry.is_expected_id(16) and not geometry.is_expected_id(-1)


def test_constants_equal_params_entries():
    p = params.PARAMS
    assert geometry.STUD_NECK_DIAMETER_MM == p[1].value
    assert geometry.STUD_HEAD_DIAMETER_MM == p[2].value
    assert geometry.STUD_EXPOSED_LENGTH_MM == p[3].value
    assert geometry.FUNNEL_MOUTH_DIAMETER_MM == p[4].value
    assert geometry.FUNNEL_THROAT_DIAMETER_MM == p[5].value
    assert geometry.FUNNEL_DEPTH_MM == p[6].value
    assert geometry.PLATE_ENVELOPE_MM == p[8].value
    assert geometry.OUTER_TAG_SIZE_MM == p[9].value["size_mm"]
    assert geometry.OUTER_TAG_CENTER_MM == p[9].value["center_stud_mm"]
    assert geometry.INNER_RING_RADIUS_MM == p[10].value["radius_mm"]
    assert geometry.INNER_RING_COUNT == p[10].value["count"]
    assert geometry.INNER_TAG_SIZE_MM == p[10].value["tag_size_mm"]
    assert (geometry.LIP_BAND_MM
            == (p[12].value["lo"], p[12].value["hi"]))
    assert geometry.ANNULUS_RADIUS_MM == p[13].value
    assert geometry.HANDOFF_TRIGGER_X_MM == p[15].value
