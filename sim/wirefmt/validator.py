"""Producer-strict line validation for the WyZen wire contract (WIRE_FORMAT.md).

validate_line(obj) returns a list of error strings, empty when the line is
valid. Unknown fields are never errors (unknown-ignored-and-preserved rule);
every other rule in the WIRE_FORMAT field table is enforced here.
"""
import math

SCHEMA_VERSION = 1

POSE_SOURCES = {"outer_tag", "inner_ring", "multi_tag_fused", "contact_force",
                "none"}
STAGES = {"acquire", "outer_servo", "inner_servo", "contact_insert", "latched",
          "abort", "escalate"}
ABORT_REASONS = {"low_confidence", "ambiguity_persistent", "inner_ring_absent",
                 "contact_anomaly", "jam_detected", "attempt_budget_exhausted",
                 "constellation_inconsistent", "latch_fail", "command"}
FAULT_CLASSES = {"mired", "depleted", "damaged", "destroyed", "unknown"}
TAG_KEYS = {"id", "reproj_err", "ambiguity_flag", "ambiguity_ratio"}

LINE_TYPES = {"target_state", "trial_header", "sim_truth", "trial_result"}

_QUAT_TOL = 1e-6
_MAX_RANGE_M = 10.0


def _is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _check_pose(pose, errors, bound_range=True):
    # The 10 m bound applies to T_head_stud on the target-state stream;
    # world-frame poses in sim_truth are unbounded.
    if not isinstance(pose, dict):
        errors.append("pose must be an object")
        return
    t, q = pose.get("t"), pose.get("q")
    if not (isinstance(t, list) and len(t) == 3 and all(_is_num(x) for x in t)):
        errors.append("pose.t must be [x,y,z]")
    elif bound_range and math.hypot(*t) > _MAX_RANGE_M:
        errors.append(f"pose.t norm exceeds {_MAX_RANGE_M:.0f} m")
    if not (isinstance(q, list) and len(q) == 4 and all(_is_num(x) for x in q)):
        errors.append("pose.q must be [w,x,y,z]")
    elif abs(math.hypot(*q) - 1.0) > _QUAT_TOL:
        errors.append("pose.q must be unit norm (a zeroed placeholder is not a rotation)")


def _check_psd_upper21(cov, errors):
    if not (isinstance(cov, list) and len(cov) == 21
            and all(_is_num(x) for x in cov)):
        errors.append("pose_cov must be 21 floats (6x6 upper triangle)")
        return
    # Rebuild the symmetric 6x6, then Cholesky with a tiny jitter so exactly
    # singular PSD matrices pass while any negative direction fails.
    m = [[0.0] * 6 for _ in range(6)]
    k = 0
    for i in range(6):
        for j in range(i, 6):
            m[i][j] = m[j][i] = float(cov[k])
            k += 1
    jitter = 1e-12
    scale = max(abs(m[i][i]) for i in range(6)) or 1.0
    for i in range(6):
        m[i][i] += jitter * scale
    for i in range(6):
        for j in range(i + 1):
            s = m[i][j] - sum(m[i][t] * m[j][t] for t in range(j))
            if i == j:
                if s <= 0:
                    errors.append("pose_cov must be PSD")
                    return
                m[i][i] = math.sqrt(s)
            else:
                m[i][j] = s / m[j][j]


def _validate_target_state(obj, errors):
    for field in ("t_capture", "t_emit", "pose_source", "conf", "stage"):
        if field not in obj:
            errors.append(f"required field missing: {field}")
    if _is_num(obj.get("t_capture")) and _is_num(obj.get("t_emit")):
        if obj["t_emit"] < obj["t_capture"]:
            errors.append("t_emit must be >= t_capture")
    if "pose" in obj:
        _check_pose(obj["pose"], errors)
        if "pose_cov" not in obj:
            errors.append("pose_cov required when pose is present "
                          "(pose without uncertainty is pose-absent)")
    if "pose_cov" in obj:
        _check_psd_upper21(obj["pose_cov"], errors)
    if "pose_source" in obj and obj["pose_source"] not in POSE_SOURCES:
        errors.append(f"pose_source not in enum: {obj['pose_source']!r}")
    conf = obj.get("conf")
    if conf is not None and (not _is_num(conf) or not 0.0 <= conf <= 1.0):
        errors.append("conf must be in [0,1]")
    stage = obj.get("stage")
    if stage is not None and stage not in STAGES:
        errors.append(f"stage not in enum: {stage!r}")
    if stage in ("abort", "escalate") and "abort_reason" not in obj:
        errors.append(f"abort_reason required when stage is {stage}")
    if "abort_reason" in obj and obj["abort_reason"] not in ABORT_REASONS:
        errors.append(f"abort_reason not in enum: {obj['abort_reason']!r}")
    if stage == "escalate" and "escalation" not in obj:
        errors.append("escalation required when stage is escalate")
    if "fault" in obj:
        fault = obj["fault"]
        if not (isinstance(fault, dict)
                and fault.get("class") in FAULT_CLASSES):
            errors.append("fault.class not in enum")
    if "degradation" in obj:
        lux = obj["degradation"].get("illuminance_lux")
        if lux is not None and (not _is_num(lux) or lux <= 0):
            errors.append("degradation.illuminance_lux must be > 0 "
                          "(0 lux is a measurement, not a default; "
                          "unavailable is omitted)")
    if "tags" in obj:
        for i, tag in enumerate(obj["tags"]):
            if not (isinstance(tag, dict) and TAG_KEYS <= tag.keys()):
                errors.append(f"tags[{i}] missing documented keys "
                              f"{sorted(TAG_KEYS)}")
    if "attempt" in obj:
        n = obj["attempt"].get("n") if isinstance(obj["attempt"], dict) else None
        if not (isinstance(n, int) and n >= 1):
            errors.append("attempt.n must be an int >= 1")


OUTCOMES = {"success", "clean_miss"} | {f"IS8-{r}" for r in range(1, 18)}


def _validate_trial_header(obj, errors):
    for field, kind in (("trial_id", str), ("seed", int),
                        ("code_git_sha", str), ("sweep_point", dict),
                        ("params_ref", str)):
        value = obj.get(field)
        if not isinstance(value, kind) or isinstance(value, bool):
            errors.append(f"{field} must be present as {kind.__name__}")
    engine = obj.get("engine")
    if not (isinstance(engine, dict)
            and isinstance(engine.get("name"), str)
            and isinstance(engine.get("version"), str)):
        errors.append("engine must be {name, version}")


def _validate_sim_truth(obj, errors):
    if not _is_num(obj.get("t")):
        errors.append("t must be a number")
    for field in ("T_world_head", "T_world_stud"):
        if field not in obj:
            errors.append(f"required field missing: {field}")
        else:
            _check_pose(obj[field], errors, bound_range=False)
    if "contact_wrench" in obj:
        wrench = obj["contact_wrench"]
        if not (isinstance(wrench, list) and len(wrench) == 6
                and all(_is_num(x) for x in wrench)):
            errors.append("contact_wrench must be [fx,fy,fz,mx,my,mz]")
    if not isinstance(obj.get("actuator_cmd"), dict):
        errors.append("actuator_cmd must be an object")


def _validate_trial_result(obj, errors):
    outcome = obj.get("outcome")
    if outcome not in OUTCOMES:
        errors.append(f"outcome not in success | IS8-1..IS8-17 | clean_miss: "
                      f"{outcome!r}")
    for field in ("first_attempt_success", "handoff_reached"):
        if not isinstance(obj.get(field), bool):
            errors.append(f"{field} must be present as bool")
    attempts = obj.get("attempts_used")
    if not isinstance(attempts, int) or isinstance(attempts, bool) or attempts < 0:
        errors.append("attempts_used must be an int >= 0")
    if not _is_num(obj.get("t_total")):
        errors.append("t_total must be a number")
    if "false_capture" in obj and outcome != "IS8-16":
        errors.append("false_capture is the IS8-16 sub-path counter; "
                      "only valid with outcome IS8-16 (H-16)")


_TYPE_VALIDATORS = {
    "target_state": _validate_target_state,
    "trial_header": _validate_trial_header,
    "sim_truth": _validate_sim_truth,
    "trial_result": _validate_trial_result,
}


def _find_nulls(value, path, errors):
    if value is None:
        errors.append(f"null at {path}: omitted-not-zeroed — "
                      "an undetermined field is omitted, never null")
    elif isinstance(value, dict):
        for k, v in value.items():
            _find_nulls(v, f"{path}.{k}", errors)
    elif isinstance(value, list):
        for i, v in enumerate(value):
            _find_nulls(v, f"{path}[{i}]", errors)


def validate_line(obj):
    """Validate one wire line. Returns [] when valid (producer-strict)."""
    errors = []
    if not isinstance(obj, dict):
        return ["line must be a JSON object"]
    _find_nulls(obj, "$", errors)
    if obj.get("v") != SCHEMA_VERSION:
        errors.append(f"v must be {SCHEMA_VERSION}")
    line_type = obj.get("type")
    if line_type not in LINE_TYPES:
        errors.append(f"type not in {sorted(LINE_TYPES)}: {line_type!r}")
        return errors
    _TYPE_VALIDATORS[line_type](obj, errors)
    return errors


def validate_trial_file(path):
    """Validate a whole trial record: header first, result last, one of each,
    every line valid. Errors are prefixed with their 1-indexed line number."""
    from wirefmt import records
    lines = records.read_ndjson(path)
    errors = []
    if not lines:
        return ["file is empty"]
    for i, obj in enumerate(lines, start=1):
        for e in validate_line(obj):
            errors.append(f"line {i}: {e}")
    types = [obj.get("type") for obj in lines]
    if types[0] != "trial_header":
        errors.append("line 1: file must start with the trial_header")
    if types[-1] != "trial_result":
        errors.append(f"line {len(types)}: file must end with the trial_result")
    for name, count in (("trial_header", types.count("trial_header")),
                        ("trial_result", types.count("trial_result"))):
        if count > 1:
            errors.append(f"exactly one {name} allowed, found {count}")
    return errors
