"""R01 L2 probe — F-018: frozen-dataset regeneration diverges off the
freeze platform (cross-platform sha256 mismatch).

Clause under test:
  WIRE_FORMAT bit-identical re-run contract; freeze_prior_v1 MANIFEST.json
  records_storage: "records regenerate deterministically from this manifest
  (code sha + committed plans + seed rule); the per-record sha256 lists
  committed beside this manifest verify any regeneration."

The freeze ran on c7i.8xlarge (ubuntu-24.04, python 3.12) at code sha
b493e7a. This probe regenerates, on the local M4 (darwin/arm64), the first
5 trials of tiers.tier1_plan(20260808) and the first 2 trials of
tiers.gate_plan(20260808, 5000) — the exact committed plan calls — and
compares sha256 against the committed lists, three arms per trial:

  FAILING ARM   raw local bytes vs committed hash. Expected per MANIFEST:
                7/7 match. Observed (finding): 7/7 mismatch while all 7
                trial_ids resolve to committed filenames.
  ISOLATION ARM the header's embedded code_git_sha (the one per-run header
                input that legitimately differs at post-freeze HEAD) is
                rewritten to the frozen sha b493e7a... and the file
                re-hashed. Still-mismatch => divergence lives in the record
                BODY (per-frame floats), not just the header sha drift.
                After the rewrite the header line is a pure function of
                inputs the two platforms share (seed, sweep_point, engine
                id, params_ref, solver, frozen sha) — the writer code is
                byte-identical to the freeze tree, which the probe verifies
                via git.
  CONTROL ARM   the same trial regenerated twice locally (separate engine
                instances, separate dirs) — byte-identical hashes show the
                mismatch is NOT local nondeterminism: determinism holds
                per instance class, it is the platform that diverges.

Deterministic: fixed sweep_root 20260808 (the committed one), D-032 seed
rule, no wall clock, no network, no cloud spend. Code freeze respected:
read-only against sim/wyzantium_sim, sim/wirefmt, sim/tests — and the probe
asserts those trees are byte-identical to the freeze sha before issuing a
verdict, so the body divergence attributes to platform, not code drift.

NOTE on re-runs: the RAW local hashes track your HEAD (code_git_sha lands
in the header, '-dirty' included), so they are stable only at a fixed git
state. The ISOLATION-arm hashes normalize that field and are reproducible
at any docs-only HEAD; they are the load-bearing numbers.

Run:
  /Users/anayvaidya/Wyzantium/Ferrier/sim/.venv/bin/python \
      studies/R01_PHASE1_REVIEW/probes/probe_f018.py

Artifacts: sim/results/review_r01/F-018/result.json (full table) + README.md.
Exit 0 with verdict CONFIRMED when trial_ids match 7/7, raw hashes mismatch
7/7, isolation-arm hashes still mismatch 7/7, and the local control is
deterministic 7/7; exit 1 (REFUTED) otherwise.
"""

import hashlib
import json
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
SIM = REPO / "sim"
ART_DIR = SIM / "results" / "review_r01" / "F-018"
FREEZE_DIR = SIM / "results" / "freeze_prior_v1"

SWEEP_ROOT = 20260808            # committed: MANIFEST.json "plans"
GATE_N = 5000                    # committed: gate_plan(20260808, 5000) [D-038]
N_TIER1 = 5
N_GATE = 2
FROZEN_TREES = ("sim/wyzantium_sim", "sim/wirefmt", "sim/tests")


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, check=True,
                          capture_output=True, text=True).stdout.strip()


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_committed():
    """filename -> (list, sha256) from the committed freeze lists."""
    committed = {}
    for name in ("tier1", "gate"):
        for line in (FREEZE_DIR / f"{name}.sha256").read_text().splitlines():
            digest, filename = line.split()
            committed[filename] = (name, digest)
    return committed


def main():
    import mujoco
    from wyzantium_sim import scenarios, trial
    from wyzantium_sim.contact.mujoco_engine import MuJoCoEngine
    from wyzantium_sim.doe import tiers

    manifest = json.loads((FREEZE_DIR / "MANIFEST.json").read_text())
    frozen_sha = manifest["code_git_sha"]
    committed = load_committed()

    # ---- Code-freeze integrity: local trees byte-identical to freeze sha
    # (required for attributing body divergence to platform, not code).
    freeze_diff = git("diff", "--name-only", frozen_sha, "HEAD", "--",
                      *FROZEN_TREES)
    freeze_dirty = git("status", "--porcelain", "--", *FROZEN_TREES)
    freeze_integrity_ok = freeze_diff == "" and freeze_dirty == ""

    plan = ([("tier1", p) for p in tiers.tier1_plan(SWEEP_ROOT)[:N_TIER1]]
            + [("gate", p) for p in tiers.gate_plan(SWEEP_ROOT, GATE_N)[:N_GATE]])

    engine_a, engine_b = MuJoCoEngine(), MuJoCoEngine()
    rows = []
    sample_header_raw = sample_header_rewritten = None
    with tempfile.TemporaryDirectory(prefix="probe_f018_a_") as tmp_a, \
            tempfile.TemporaryDirectory(prefix="probe_f018_b_") as tmp_b:
        for arm, p in plan:
            built = scenarios.build_sweep_point(**p.sweep_point)
            trial_id = trial._trial_id(p.seed, built,
                                       engine_a.engine_id["name"])
            filename = f"{trial_id}.ndjson"
            listed = committed.get(filename)

            # FAILING ARM: regenerate at HEAD on this machine.
            path_a = trial.run_trial(p.seed, p.sweep_point, engine_a,
                                     p.sweep_point["curve_set"], out_dir=tmp_a)
            assert path_a.name == filename, (path_a.name, filename)
            bytes_a = path_a.read_bytes()
            local_hash = sha256_hex(bytes_a)

            # CONTROL ARM: second local regeneration, fresh engine + dir.
            path_b = trial.run_trial(p.seed, p.sweep_point, engine_b,
                                     p.sweep_point["curve_set"], out_dir=tmp_b)
            rerun_hash = sha256_hex(path_b.read_bytes())

            # ISOLATION ARM: normalize the header's embedded code sha to the
            # frozen value, re-hash. Value occurs exactly once (the header).
            header_line = bytes_a.split(b"\n", 1)[0]
            header = json.loads(header_line)
            local_code_sha = header["code_git_sha"]
            occurrences = bytes_a.count(local_code_sha.encode())
            rewritten = bytes_a.replace(local_code_sha.encode(),
                                        frozen_sha.encode(), 1)
            rewritten_hash = sha256_hex(rewritten)
            if sample_header_raw is None:
                sample_header_raw = header_line.decode()
                sample_header_rewritten = rewritten.split(b"\n", 1)[0].decode()

            committed_hash = listed[1] if listed else None
            rows.append({
                "plan": arm,
                "plan_tag": p.tag,
                "seed": p.seed,
                "trial_id": trial_id,
                "trial_id_in_committed_list": listed is not None,
                "committed_list": listed[0] if listed else None,
                "committed_sha256": committed_hash,
                "local_sha256": local_hash,
                "match": local_hash == committed_hash,
                "local_sha256_code_sha_rewritten": rewritten_hash,
                "match_after_code_sha_rewrite":
                    rewritten_hash == committed_hash,
                "code_sha_occurrences_in_record": occurrences,
                "local_rerun_sha256": rerun_hash,
                "local_deterministic": rerun_hash == local_hash,
                "record_bytes": len(bytes_a),
            })

    n = len(rows)
    ids_ok = sum(r["trial_id_in_committed_list"] for r in rows)
    raw_mismatch = sum(not r["match"] for r in rows)
    rewrite_mismatch = sum(not r["match_after_code_sha_rewrite"] for r in rows)
    deterministic = sum(r["local_deterministic"] for r in rows)
    rewrite_surgical = all(r["code_sha_occurrences_in_record"] == 1
                           for r in rows)

    confirmed = (freeze_integrity_ok and rewrite_surgical
                 and ids_ok == n and raw_mismatch == n
                 and rewrite_mismatch == n and deterministic == n)

    result = {
        "finding": "F-018",
        "probe": "studies/R01_PHASE1_REVIEW/probes/probe_f018.py",
        "clause": ("WIRE_FORMAT bit-identical re-run contract; "
                   "freeze_prior_v1/MANIFEST.json records_storage: records "
                   "'regenerate deterministically from this manifest'; "
                   "per-record sha256 lists 'verify any regeneration'"),
        "plans_regenerated": {
            "tier1": f"tiers.tier1_plan({SWEEP_ROOT})[:{N_TIER1}]",
            "gate": f"tiers.gate_plan({SWEEP_ROOT}, {GATE_N})[:{N_GATE}]",
        },
        "freeze_platform": {
            "code_git_sha": frozen_sha,
            "instance": manifest["instance"],
            "engine": manifest["engine"],
        },
        "local_platform": {
            "system": platform.system(),
            "machine": platform.machine(),
            "platform": platform.platform(),
            "python": platform.python_version(),
            "mujoco": mujoco.__version__,
            "engine_id": dict(engine_a.engine_id),
            "git_head": git("rev-parse", "HEAD"),
            "git_dirty": git("status", "--porcelain") != "",
        },
        "code_freeze_integrity": {
            "trees": list(FROZEN_TREES),
            "diff_names_vs_frozen_sha": freeze_diff,
            "working_tree_porcelain": freeze_dirty,
            "ok": freeze_integrity_ok,
        },
        "table": rows,
        "summary": {
            "n": n,
            "trial_ids_resolved_in_committed_lists": ids_ok,
            "raw_sha256_mismatch": raw_mismatch,
            "mismatch_after_code_sha_rewrite": rewrite_mismatch,
            "local_double_run_deterministic": deterministic,
            "code_sha_rewrite_surgical_1_occurrence": rewrite_surgical,
        },
        "sample_header_raw": sample_header_raw,
        "sample_header_code_sha_rewritten": sample_header_rewritten,
        "interpretation": {
            "raw_mismatch": "committed verification recipe fails off the "
                            "freeze platform",
            "mismatch_after_code_sha_rewrite": "divergence survives header "
                            "sha normalization => record BODY diverges "
                            "(per-frame float drift, M4/darwin/arm64 vs "
                            "c7i.8xlarge/ubuntu) — not just header drift",
            "local_deterministic": "same-platform double regeneration is "
                            "byte-identical => determinism holds per "
                            "instance class; the contract wording, not the "
                            "generator, is what breaks cross-platform",
        },
        "verdict": "CONFIRMED" if confirmed else "REFUTED",
        "confirmed": confirmed,
    }

    ART_DIR.mkdir(parents=True, exist_ok=True)
    (ART_DIR / "result.json").write_text(json.dumps(result, indent=2) + "\n")

    print(json.dumps(result["summary"], indent=2))
    print("verdict:", result["verdict"])
    return 0 if confirmed else 1


if __name__ == "__main__":
    sys.exit(main())
