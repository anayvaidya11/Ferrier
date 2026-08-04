"""T8 — truth pose → TagSighting geometry (perception/sightings.py).

The sighting generator is pure geometry: which tags could be seen, at what
range/view angle, by which camera (D-012 roles: A = outer, B = inner ring).
Detection realism lives in the injector's decode-floor curve, not here.

Hand-check frame: nominal approach orientation Q_NOMINAL = (0,0,1,0) is the
180°-about-Y flip (IS §4), so +X_stud → -X_head and (x,y,z)_stud →
(-x,y,-z)_head. With truth t = (2.0, 0, 0.185) m the outer-tag center
(0,0,185) mm_stud lands exactly at (2.0, 0, 0) m_head, its face normal at
(-1,0,0) — pointing back at the cameras.
"""
import math

import pytest

from wyzantium_sim import frames
from wyzantium_sim.perception import sightings

Q_NOMINAL = (0.0, 0.0, 1.0, 0.0)
Q_IDENTITY = (1.0, 0.0, 0.0, 0.0)
TRUTH = frames.Pose(t=(2.0, 0.0, 0.185), q=Q_NOMINAL)


def by_id(sights):
    return {s.tag_id: s for s in sights}


class TestNominalConstellation:
    def test_all_nine_tags_sighted_head_on(self):
        assert len(sightings.sightings_for(TRUTH)) == 9

    def test_outer_tag_geometry_hand_check(self):
        # tag 0 center at (2.0, 0, 0) m_head; cam A at (-0.050, 0, 0.140)
        # (PARAMS[17]): separation (2.05, 0, -0.140), dist = hypot,
        # view angle = atan(0.14 / 2.05) off the -X face normal.
        s = by_id(sightings.sightings_for(TRUTH))[0]
        assert s.camera == "A"
        assert s.dist_m == pytest.approx(math.hypot(2.05, 0.14), abs=1e-9)
        assert s.view_angle_rad == pytest.approx(
            math.atan2(0.14, 2.05), abs=1e-9)
        assert s.span_m == 0.15

    def test_inner_tag_geometry_hand_check(self):
        # tag 1 (alpha = 0) center (0, 0, 55) mm_stud → (2.0, 0, 0.130)
        # m_head; cam B at (0.100, -0.250, 0) (PARAMS[18]): separation
        # (1.9, 0.25, 0.130).
        s = by_id(sightings.sightings_for(TRUTH))[1]
        assert s.camera == "B"
        d = math.sqrt(1.9**2 + 0.25**2 + 0.130**2)
        assert s.dist_m == pytest.approx(d, abs=1e-9)
        assert s.span_m == 0.11

    def test_inner_ring_standoff_shifts_centers(self):
        # L-B standoff h_mm moves inner centers by -h along X_head (the
        # 180°-about-Y flip); the outer tag never moves.
        flat = by_id(sightings.sightings_for(TRUTH, h_mm=0.0))
        raised = by_id(sightings.sightings_for(TRUTH, h_mm=20.0))
        assert raised[0].dist_m == flat[0].dist_m
        assert raised[1].dist_m != flat[1].dist_m


class TestVisibility:
    def test_back_facing_tags_excluded(self):
        # identity orientation: faces point +X_head, away from the cameras
        away = frames.Pose(t=(2.0, 0.0, 0.185), q=Q_IDENTITY)
        assert sightings.sightings_for(away) == []


class TestKnockout:
    def test_mask_bit_k_kills_tag_k(self):
        s = by_id(sightings.sightings_for(TRUTH, knockout_mask=0b1))
        assert 0 not in s and len(s) == 8

    def test_inner_mask_leaves_outer_only(self):
        mask = sum(1 << k for k in range(1, 9))
        s = sightings.sightings_for(TRUTH, knockout_mask=mask)
        assert [x.tag_id for x in s] == [0]


class TestPurity:
    def test_deterministic(self):
        assert (sightings.sightings_for(TRUTH)
                == sightings.sightings_for(TRUTH))
