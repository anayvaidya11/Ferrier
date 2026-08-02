"""Canonical NDJSON encoding for the WyZen wire contract (WIRE_FORMAT.md).

Canonical form: known fields in the WIRE_FORMAT documented order, unknown
fields preserved after them in first-seen order (unknown-ignored-and-preserved
rule), compact separators, shortest round-trip floats, LF line endings.
Nulls are rejected outright: a field that could not be determined is omitted,
never emitted as zero, null, or a default (omitted-not-zeroed rule).
"""
import json

# Field order as documented in WIRE_FORMAT.md, per line type.
CANONICAL_ORDER = {
    "target_state": [
        "v", "type", "t_capture", "t_emit", "pose", "pose_cov", "pose_source",
        "conf", "tags", "fault", "degradation", "stage", "attempt",
        "abort_reason", "escalation",
    ],
    "trial_header": [
        "v", "type", "trial_id", "seed", "code_git_sha", "engine",
        "sweep_point", "params_ref", "solver",
    ],
    "sim_truth": [
        "v", "type", "t", "T_world_head", "T_world_stud", "contact_wrench",
        "actuator_cmd",
    ],
    "trial_result": [
        "v", "type", "outcome", "first_attempt_success", "attempts_used",
        "t_total", "handoff_reached", "false_capture",
    ],
}


class EncodingError(ValueError):
    pass


def _reject_nulls(value, path):
    if value is None:
        raise EncodingError(
            f"null at {path}: omitted-not-zeroed — omit the field instead"
        )
    if isinstance(value, dict):
        for k, v in value.items():
            _reject_nulls(v, f"{path}.{k}")
    elif isinstance(value, list):
        for i, v in enumerate(value):
            _reject_nulls(v, f"{path}[{i}]")


def dumps_line(obj):
    """Serialize one wire line to its canonical JSON string (no newline)."""
    _reject_nulls(obj, "$")
    order = CANONICAL_ORDER.get(obj.get("type"), [])
    known = {k: obj[k] for k in order if k in obj}
    unknown = {k: v for k, v in obj.items() if k not in known}
    return json.dumps({**known, **unknown}, separators=(",", ":"))


def write_ndjson(path, lines):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for obj in lines:
            f.write(dumps_line(obj))
            f.write("\n")


def read_ndjson(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]
