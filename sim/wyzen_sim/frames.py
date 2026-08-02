"""Rigid-transform algebra per INTERFACE_SPEC §4.

T_A_B is the pose of frame B expressed in frame A; p_A = T_A_B · p_B.
Quaternions are unit, order [w, x, y, z] (WIRE_FORMAT convention). Pose is
immutable; construction normalizes the quaternion and rejects anything more
than 1e-6 from unit (the WIRE_FORMAT tolerance) — a zeroed placeholder is
not a rotation.
"""
import math
from dataclasses import dataclass

_UNIT_TOL = 1e-6


def _qmul(a, b):
    aw, ax, ay, az = a
    bw, bx, by, bz = b
    return (aw * bw - ax * bx - ay * by - az * bz,
            aw * bx + ax * bw + ay * bz - az * by,
            aw * by - ax * bz + ay * bw + az * bx,
            aw * bz + ax * by - ay * bx + az * bw)


def _qconj(q):
    return (q[0], -q[1], -q[2], -q[3])


def _qrotate(q, v):
    p = _qmul(_qmul(q, (0.0, *v)), _qconj(q))
    return (p[1], p[2], p[3])


@dataclass(frozen=True)
class Pose:
    t: tuple
    q: tuple

    def __post_init__(self):
        norm = math.hypot(*self.q)
        if abs(norm - 1.0) > _UNIT_TOL:
            raise ValueError(f"q must be unit norm within {_UNIT_TOL}; "
                             f"got norm {norm}")
        object.__setattr__(self, "t", tuple(float(x) for x in self.t))
        object.__setattr__(self, "q", tuple(float(c) / norm for c in self.q))

    @classmethod
    def identity(cls):
        return cls((0.0, 0.0, 0.0), (1.0, 0.0, 0.0, 0.0))

    def apply(self, point):
        r = _qrotate(self.q, tuple(point))
        return (r[0] + self.t[0], r[1] + self.t[1], r[2] + self.t[2])

    def compose(self, other):
        """T_A_C = self (T_A_B) ∘ other (T_B_C)."""
        return Pose(self.apply(other.t), _qmul(self.q, other.q))

    def inverse(self):
        qc = _qconj(self.q)
        ti = _qrotate(qc, self.t)
        return Pose((-ti[0], -ti[1], -ti[2]), qc)

    def to_wire(self):
        return {"t": list(self.t), "q": list(self.q)}

    @classmethod
    def from_wire(cls, d):
        return cls(tuple(d["t"]), tuple(d["q"]))
