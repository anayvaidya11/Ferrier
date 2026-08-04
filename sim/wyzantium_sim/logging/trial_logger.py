"""T8 — trial logger: buffered, producer-strict canonical NDJSON (WIRE_FORMAT).

Owns the wire seams the stage code refuses to own:

- mm→m: kinematic/contact poses are mm (repo convention); wire poses are
  metres (handoff.py and inject.py docstrings assign the /1000 to T8).
- World frame (arbitrary code-level choice, chassis_error precedent —
  WIRE_FORMAT names T_world_head/T_world_stud but no spec pins a world
  frame): world ≡ stud frame. T_world_stud is identity on every line and
  T_world_head = pose_mm_to_m(T_head_stud)⁻¹, so T_head_stud is exactly
  recoverable and no information is invented. Host attitude axes
  (host_pitch/roll_deg) are recorded in the sweep_point but realized
  nowhere pre-T10; this convention stays honest about that.
- contact_wrench is sticky-omitted: absent until the first step that
  reports contact, emitted from then on (zero-after-contact is a
  measurement, not a default — omitted-not-zeroed rule).
- Every line is validated at buffer time; a line that fails the contract
  raises TrialLogError instead of reaching disk.

Interleaving is the caller's job (trial.py merges kinematic steps and
perception frames by (t, kind), sim_truth first at equal t — documented
there). write() serializes once, via records.write_ndjson (fixed key
order, shortest round-trip floats, LF) for the byte-identity gate.
"""
from pathlib import Path

from wirefmt import records, validator
from wyzantium_sim import frames

_MM = 0.001


class TrialLogError(ValueError):
    pass


def pose_mm_to_m(pose):
    """Repo-convention mm pose → WIRE_FORMAT metres pose (q unchanged)."""
    return frames.Pose(tuple(v * _MM for v in pose.t), pose.q)


def upper21_to_6x6(cov21):
    """Wire 21-float upper triangle → symmetric 6×6 nested tuples (SI)."""
    m = [[0.0] * 6 for _ in range(6)]
    k = 0
    for i in range(6):
        for j in range(i, 6):
            m[i][j] = m[j][i] = float(cov21[k])
            k += 1
    return tuple(tuple(row) for row in m)


_IDENTITY_WIRE = frames.Pose.identity().to_wire()


class TrialLogger:
    def __init__(self, path):
        self.path = Path(path)
        self.lines = []
        self._contact_seen = False

    def _buffer(self, line):
        errors = validator.validate_line(line)
        if errors:
            raise TrialLogError("; ".join(errors))
        self.lines.append(line)

    def header(self, *, trial_id, seed, code_git_sha, engine, sweep_point,
               params_ref, solver=None):
        line = {"v": 1, "type": "trial_header", "trial_id": trial_id,
                "seed": seed, "code_git_sha": code_git_sha, "engine": engine,
                "sweep_point": sweep_point, "params_ref": params_ref}
        if solver is not None:
            line["solver"] = solver
        self._buffer(line)

    def target_state(self, line):
        self._buffer(line)

    def _sim_truth(self, t_s, t_head_stud_mm, actuator_cmd, wrench):
        head_m = pose_mm_to_m(t_head_stud_mm)
        line = {"v": 1, "type": "sim_truth", "t": float(t_s),
                "T_world_head": head_m.inverse().to_wire(),
                "T_world_stud": dict(_IDENTITY_WIRE)}
        if wrench is not None:
            line["contact_wrench"] = [float(w) for w in wrench]
        line["actuator_cmd"] = actuator_cmd
        self._buffer(line)

    def sim_truth_kinematic(self, t_s, t_head_stud_mm, actuator_cmd):
        """Pre-handoff cadence (#59): one line per kinematic step. Always
        pre-contact, so contact_wrench is structurally absent."""
        self._sim_truth(t_s, t_head_stud_mm, actuator_cmd, wrench=None)

    def sim_truth_contact(self, step, actuator_cmd):
        """Post-handoff cadence (#59): one line per physics StepResult."""
        if step.contacts:
            self._contact_seen = True
        wrench = step.wall_wrench if self._contact_seen else None
        self._sim_truth(step.t_sim_s, step.T_head_stud, actuator_cmd, wrench)

    def result(self, *, outcome, first_attempt_success, attempts_used,
               t_total, handoff_reached, false_capture=None):
        line = {"v": 1, "type": "trial_result", "outcome": outcome,
                "first_attempt_success": first_attempt_success,
                "attempts_used": attempts_used, "t_total": float(t_total),
                "handoff_reached": handoff_reached}
        if false_capture is not None:
            line["false_capture"] = false_capture
        self._buffer(line)

    def write(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        records.write_ndjson(self.path, self.lines)
        return self.path
