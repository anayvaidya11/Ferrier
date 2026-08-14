"""Tier-3 replay artifacts for freeze_prior_v2 (A-007).

One artifact per outcome class the v2 DOE actually produced — success,
IS8-1, IS8-2 (Tier-1 marginals) and IS8-5 (gate cell) — each regenerated
deterministically from the committed plans (records are hash-and-freed in
the freeze), rendered from logged state only, sidecar carrying the F-024
regeneration recipe instead of an ephemeral path.

Candidate cells are chosen from the freeze census: the nominal cell for
success, outer_occlusion=0.5 for IS8-1, illuminance_lux=1 for IS8-2, and
a chunked scan of the gate plan for IS8-5 (36/5,000 in the freeze).
The driver asserts each rendered artifact's outcome matches its class
and that the class set equals the freeze census keys before writing.

Post-swap, the mr_v1 artifact set is the same command with --curve-set
mr_v1 once the set is registered (swap session).

Usage: sim/.venv/bin/python tools/tier3_v2.py \
    [--out sim/results/tier3_prior_v2] [--workers 8]
"""
import argparse
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
REPO = TOOLS.parent
sys.path.insert(0, str(REPO / "sim"))

from wyzantium_sim.analysis import dataset  # noqa: E402
from wyzantium_sim.doe import runner, tiers  # noqa: E402
from wyzantium_sim.replay.artifact import render_artifact  # noqa: E402

SWEEP_ROOT = 20260808  # the committed Phase 1 root (D-032)
FREEZE_SHA = "f6325bd"
GATE_CHUNK = 200

# class -> (plan name, tag prefix). Gate scan handled separately.
# IS8-2's producer probed 2026-08-14: the lux=1 cell classifies IS8-1
# (floor detections keep ID-0 sightings nonzero); zero-ID-0 comes from
# tag_knockout_mask=1 — the outer tag itself destroyed.
TIER1_CANDIDATES = {
    "success": "tier1:nominal:",
    "IS8-1": "tier1:outer_occlusion=0.5:",
    "IS8-2": "tier1:tag_knockout_mask=1:",
}


def _git_sha():
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                          capture_output=True, text=True).stdout.strip()


def find_in_slice(plan_slice, outcome, scratch, workers):
    """Run a deterministic plan slice; return (record path, tag) of the
    first trial classifying as `outcome`, or None."""
    result = runner.run_sweep(plan_slice, scratch, workers=workers)
    rows = {r.trial_id: r for r in dataset.load_dataset(scratch)}
    for path, planned in zip(result.paths, plan_slice):
        r = rows.get(path.stem)
        if r is not None and r.outcome == outcome:
            return path, planned.tag
    return None


def freeze_census_classes():
    s = json.loads((REPO / "sim" / "results" / "freeze_prior_v2"
                    / "freeze_summary.json").read_text())
    classes = set()
    for plan in ("tier1", "tier2", "gate"):
        classes |= set(s[plan]["census"])
    return classes


def sidecar_fixup(sidecar_path, tag, plan_expr):
    side = json.loads(sidecar_path.read_text())
    side["source_record"] = (
        f"not retained - regenerate: trial tag {tag!r} of {plan_expr} "
        f"(seed embedded in trial_id) via runner.run_sweep; freeze "
        f"reference {FREEZE_SHA} (freeze_prior_v2/MANIFEST.json); "
        "byte-identity is per-instance-class (R01 F-018)")
    side["plan"] = plan_expr
    side["tag"] = tag
    side["curve_set"] = "prior_v1"
    side["regenerated_on"] = platform.platform()
    side["regeneration_sha_note"] = (
        f"code_git_sha above is a descendant of freeze SHA {FREEZE_SHA}; "
        "the only sim-runtime delta since the freeze is the additive "
        "run_sweep(curve_sets=...) swap seam, default-inert for prior_v1 "
        "(pinned by sim/tests/test_swap_seam.py)")
    with open(sidecar_path, "w", encoding="utf-8") as f:
        json.dump(side, f, indent=1)
    return side


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO / "sim" / "results"
                                         / "tier3_prior_v2"))
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--scratch", default=str(TOOLS / "mr_kit" / "build"
                                             / "tier3_records"))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    scratch_root = Path(args.scratch)

    produced = freeze_census_classes()
    wanted = {"success", "IS8-1", "IS8-2", "IS8-5"}
    if wanted != produced:
        sys.exit(f"class set mismatch: freeze census {sorted(produced)} "
                 f"vs driver targets {sorted(wanted)} — update the driver")

    t1 = tiers.tier1_plan(SWEEP_ROOT)
    found = {}

    for outcome, prefix in TIER1_CANDIDATES.items():
        cell = tuple(p for p in t1 if p.tag.startswith(prefix))
        scratch = scratch_root / outcome
        scratch.mkdir(parents=True, exist_ok=True)
        hit = find_in_slice(cell[:10], outcome, scratch, args.workers)
        if hit is None:
            hit = find_in_slice(cell, outcome, scratch, args.workers)
        if hit is None:
            sys.exit(f"{outcome}: no trial in cell {prefix!r} classified "
                     "as expected — census drift, investigate")
        found[outcome] = (hit, f"tiers.tier1_plan({SWEEP_ROOT})")
        print(f"[tier3] {outcome}: {hit[1]}", flush=True)

    gate = tiers.gate_plan(SWEEP_ROOT, 5000)
    scratch = scratch_root / "IS8-5"
    scratch.mkdir(parents=True, exist_ok=True)
    hit = None
    for start in range(0, len(gate), GATE_CHUNK):
        hit = find_in_slice(gate[start:start + GATE_CHUNK], "IS8-5",
                            scratch, args.workers)
        if hit:
            break
    if hit is None:
        sys.exit("IS8-5: not found in the full gate plan — census drift")
    found["IS8-5"] = (hit, f"tiers.gate_plan({SWEEP_ROOT}, 5000)")
    print(f"[tier3] IS8-5: {hit[1]}", flush=True)

    for outcome, ((record, tag), plan_expr) in found.items():
        gif, sidecar = render_artifact(record, out)
        side = sidecar_fixup(sidecar, tag, plan_expr)
        assert side["outcome"] == outcome, (side["outcome"], outcome)
        assert gif.stem.split(".")[0] == side["trial_id"]
        print(f"[tier3] rendered {outcome}: {gif.name}", flush=True)

    shutil.rmtree(scratch_root)
    print(f"[tier3] done -> {out} (sha at regeneration: "
          f"{_git_sha()[:12]})", flush=True)


if __name__ == "__main__":
    main()
