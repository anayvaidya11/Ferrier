"""R01 L2 probe — F-017: trial_header carries no compute-instance identity.

Clause under test:
  ARCHITECTURE.md §5 (A-004): "both measurements are committed alongside the
  trial records (engine and instance identity land in every `trial_header`)."
  PHASE1_PLAN.md §2 wirefmt row: "trial_header (incl. #33 solver block +
  compute-instance identity)".

ARCH §5 commits BOTH halves — engine identity AND instance identity — to
every trial_header. This probe regenerates one nominal trial and checks all
four layers of the wire contract for each half, side by side (probe33 style):

  FAILING ARM  (instance identity): produced header keys, schema properties,
               canonical writer order, validator checks — expected present
               per ARCH §5, observed absent everywhere.
  CONTROL ARM  (engine identity — the other noun of the same sentence):
               same four layers — present everywhere, and ENFORCED (deleting
               `engine` from the produced header makes validate_line fail,
               while the header that has never had any instance field
               validates clean).

Deterministic: fixed seed 101, committed nominal sweep point
(sim/scenarios/nominal.json), local MuJoCo, no wall clock, no network,
no cloud spend. Code freeze respected: read-only against sim/wyzantium_sim,
sim/wirefmt, sim/tests; no monkeypatching needed for this finding.

Run:
  /Users/anayvaidya/Wyzantium/Ferrier/sim/.venv/bin/python \
      studies/R01_PHASE1_REVIEW/probes/probe_f017.py

Artifacts: sim/results/review_r01/F-017/{result.json, README.md,
trial_header.json}. Exit 0 with verdict CONFIRMED when the failing arm shows
absence at all four layers and the control arm shows presence at all four;
exit 1 (REFUTED) otherwise.
"""

import inspect
import json
import platform
import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ART_DIR = REPO / "sim" / "results" / "review_r01" / "F-017"
SCHEMA_PATH = REPO / "sim" / "wirefmt" / "schema" / "trial_header.v1.schema.json"
NOMINAL_PATH = REPO / "sim" / "scenarios" / "nominal.json"

SEED = 101

# The nine keys the harness actually writes (WIRE_FORMAT header spec: eight
# required fields; `solver` optional-in-schema, always written per #33).
EXPECTED_HEADER_KEYS = {
    "v", "type", "trial_id", "seed", "code_git_sha", "engine",
    "sweep_point", "params_ref", "solver",
}

# Tokens any compute-instance identity field would plausibly carry.
# Word-bounded so `isinstance(` in validator source does not false-positive.
INSTANCE_TOKEN_RE = re.compile(
    r"\b(instance|instance_id|host|hostname|machine|platform|node|node_id"
    r"|uname|compute|cpu_model|worker)\b",
    re.IGNORECASE,
)


def tokens_in(text):
    return sorted({m.group(0).lower() for m in INSTANCE_TOKEN_RE.finditer(text)})


def main():
    from wirefmt import records, validator
    from wyzantium_sim import scenarios, trial
    from wyzantium_sim.contact.mujoco_engine import MuJoCoEngine

    # ---- Regenerate one nominal trial, seed 101 ------------------------
    nominal = json.loads(NOMINAL_PATH.read_text())["sweep_point"]
    sweep_point = scenarios.build_sweep_point(**nominal)
    with tempfile.TemporaryDirectory(prefix="probe_f017_") as tmp:
        record_path = trial.run_trial(SEED, sweep_point, MuJoCoEngine(),
                                      "prior_v1", out_dir=tmp)
        lines = records.read_ndjson(record_path)
    header = lines[0]
    assert header["type"] == "trial_header", "line 1 must be the trial_header"

    # ---- FAILING ARM: instance identity, four layers -------------------
    schema = json.loads(SCHEMA_PATH.read_text())
    schema_props = sorted(schema["properties"].keys())
    schema_required = sorted(schema["required"])
    canonical = records.CANONICAL_ORDER["trial_header"]
    vsrc = inspect.getsource(validator._validate_trial_header)

    instance_arm = {
        "header_keys": sorted(header.keys()),
        "header_keys_match_expected": set(header) == EXPECTED_HEADER_KEYS,
        "instance_tokens_in_header_keys": tokens_in(" ".join(header.keys())),
        "instance_tokens_in_schema_properties": tokens_in(" ".join(schema_props)),
        "instance_tokens_in_schema_required": tokens_in(" ".join(schema_required)),
        "instance_tokens_in_canonical_order": tokens_in(" ".join(canonical)),
        "instance_tokens_in_validator_checks": tokens_in(vsrc),
        "validate_line_errors_on_header_as_written": validator.validate_line(header),
    }
    instance_absent_everywhere = (
        instance_arm["header_keys_match_expected"]
        and not instance_arm["instance_tokens_in_header_keys"]
        and not instance_arm["instance_tokens_in_schema_properties"]
        and not instance_arm["instance_tokens_in_schema_required"]
        and not instance_arm["instance_tokens_in_canonical_order"]
        and not instance_arm["instance_tokens_in_validator_checks"]
        and instance_arm["validate_line_errors_on_header_as_written"] == []
    )

    # ---- CONTROL ARM: engine identity, same four layers -----------------
    beheaded = {k: v for k, v in header.items() if k != "engine"}
    engine_errors = validator.validate_line(beheaded)
    engine_arm = {
        "engine_in_header": header.get("engine"),
        "engine_in_schema_properties": "engine" in schema["properties"],
        "engine_in_schema_required": "engine" in schema["required"],
        "engine_subschema_required": schema["properties"]["engine"].get("required"),
        "engine_in_canonical_order": "engine" in canonical,
        "engine_checked_by_validator_source": "engine" in vsrc,
        "validate_line_errors_with_engine_removed": engine_errors,
    }
    engine_present_and_enforced = (
        isinstance(engine_arm["engine_in_header"], dict)
        and set(engine_arm["engine_in_header"]) >= {"name", "version"}
        and engine_arm["engine_in_schema_properties"]
        and engine_arm["engine_in_schema_required"]
        and engine_arm["engine_subschema_required"] == ["name", "version"]
        and engine_arm["engine_in_canonical_order"]
        and engine_arm["engine_checked_by_validator_source"]
        and any("engine" in e for e in engine_errors)
    )

    confirmed = instance_absent_everywhere and engine_present_and_enforced

    result = {
        "finding": "F-017",
        "probe": "studies/R01_PHASE1_REVIEW/probes/probe_f017.py",
        "clause": ("ARCH §5: 'engine and instance identity land in every "
                   "trial_header'; PHASE1_PLAN §2 wirefmt row: 'trial_header "
                   "(incl. #33 solver block + compute-instance identity)'"),
        "seed": SEED,
        "sweep_point_source": "sim/scenarios/nominal.json (committed nominal)",
        "trial_id": header["trial_id"],
        "code_git_sha": header["code_git_sha"],
        "engine": header["engine"],
        "expected_header_keys": sorted(EXPECTED_HEADER_KEYS),
        "arms": {
            "instance_identity_FAILING": instance_arm,
            "engine_identity_CONTROL": engine_arm,
        },
        "instance_absent_at_all_four_layers": instance_absent_everywhere,
        "engine_present_and_enforced_at_all_four_layers":
            engine_present_and_enforced,
        "runtime_platform_with_nowhere_to_land": {
            "system": platform.system(),
            "machine": platform.machine(),
            "python": platform.python_version(),
        },
        "verdict": "CONFIRMED" if confirmed else "REFUTED",
        "confirmed": confirmed,
    }

    ART_DIR.mkdir(parents=True, exist_ok=True)
    (ART_DIR / "result.json").write_text(json.dumps(result, indent=2) + "\n")
    (ART_DIR / "trial_header.json").write_text(
        records.dumps_line(header) + "\n")

    print(json.dumps(result, indent=2))
    return 0 if confirmed else 1


if __name__ == "__main__":
    sys.exit(main())
