"""Rigid-transform algebra — INTERFACE_SPEC §4 conventions.

T_A_B is the pose of frame B expressed in frame A; p_A = T_A_B · p_B.
Quaternions are unit, order [w, x, y, z] (WIRE_FORMAT).
"""
import math

import pytest

from wyzen_sim import frames

TOL = 1e-12


def approx3(a, b, tol=1e-9):
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def rot_z_90():
    # 90° about +Z: (1,0,0) -> (0,1,0)
    half = math.radians(45.0)
    return frames.Pose((0.0, 0.0, 0.0),
                       (math.cos(half), 0.0, 0.0, math.sin(half)))


def test_identity_leaves_points_alone():
    p = (1.2, -3.4, 5.6)
    assert approx3(frames.Pose.identity().apply(p), p)


def test_known_90_degree_rotation():
    assert approx3(rot_z_90().apply((1.0, 0.0, 0.0)), (0.0, 1.0, 0.0))


def test_translation_applies_after_rotation():
    # p_A = R·p_B + t
    pose = frames.Pose((10.0, 0.0, 0.0), rot_z_90().q)
    assert approx3(pose.apply((1.0, 0.0, 0.0)), (10.0, 1.0, 0.0))


def test_compose_matches_sequential_application():
    t_a_b = frames.Pose((0.1, -0.2, 0.3), rot_z_90().q)
    half = math.radians(30.0)
    t_b_c = frames.Pose((-1.0, 2.0, 0.5),
                        (math.cos(half), math.sin(half), 0.0, 0.0))
    p_c = (0.7, 0.8, -0.9)
    via_compose = t_a_b.compose(t_b_c).apply(p_c)
    sequential = t_a_b.apply(t_b_c.apply(p_c))
    assert approx3(via_compose, sequential)


def test_pose_composed_with_inverse_is_identity():
    pose = frames.Pose((0.4, -1.1, 2.2), rot_z_90().q)
    ident = pose.compose(pose.inverse())
    assert approx3(ident.t, (0.0, 0.0, 0.0))
    # q and -q are the same rotation.
    assert min(abs(ident.q[0] - 1.0), abs(ident.q[0] + 1.0)) < 1e-9
    assert all(abs(c) < 1e-9 for c in ident.q[1:])


def test_unit_norm_preserved_under_repeated_composition():
    pose = rot_z_90()
    acc = frames.Pose.identity()
    for _ in range(1000):
        acc = acc.compose(pose)
    norm = math.hypot(*acc.q)
    assert abs(norm - 1.0) < 1e-9


def test_non_unit_quaternion_rejected():
    with pytest.raises(ValueError, match="unit"):
        frames.Pose((0.0, 0.0, 0.0), (0.9, 0.0, 0.0, 0.0))


def test_wire_round_trip():
    pose = frames.Pose((2.412, 0.113, -0.071), rot_z_90().q)
    again = frames.Pose.from_wire(pose.to_wire())
    assert approx3(again.t, pose.t) and approx3(again.q, pose.q, 1e-12)
    assert set(pose.to_wire().keys()) == {"t", "q"}
