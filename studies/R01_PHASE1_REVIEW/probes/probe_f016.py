#!/usr/bin/env python
"""Probe F-016 — staleness check unrealized; latency axis (#38) behaviorally inert.

Claim under test (FINDINGS.md F-016): no consumer reads `t_emit` or holds a
staleness bound — WIRE_FORMAT consumer checklist item 4 ("receive-time age
beyond the consumer's staleness bound -> treat as pose-absent") is realized
nowhere. `perception_latency_ms` feeds `timing.emit_time` (inject.py:90) and
nothing else; frames are consumed at CAPTURE time (closed_loop.py:59-60:
`t = next_frame_t; d = on_frame(t, last)`). The frozen Tier-1 latency
marginal {10, 30, 100} ms (tier1.json:20) is therefore fake-flat.

Method (probe33 style — failing condition beside a nominal live control):

  FAILING ARM (latency pairs) — seeds 101/202/303, full run_trial at the
      committed nominal sweep point differing ONLY in perception_latency_ms:
      10 vs 100 ms (the tier1 marginal's endpoints). Assert per pair:
        * trial_result byte-equal (outcome invariance under a 10x latency step)
        * every sim_truth line byte-equal
        * every target_state pair differs ONLY in t_emit, with
          t_emit == timing.emit_time(t_capture, latency) exactly per arm
        * header differs only in sweep_point.perception_latency_ms and
          trial_id — and trial_id is recomputed from trial.py's _trial_id
          formula (a sha1 of the sweep_point), i.e. a pure derivative of
          the latency value, not a behavioral difference
        * after normalizing exactly those fields, the two records are
          byte-identical end to end.

  CONTROL ARM (rate pairs) — same seeds, same procedure, same normalization,
      on the NEIGHBORING committed timing axis: perception_rate_hz 30 vs 10
      (both tier1 cells, same H-06 basis line). The identical methodology
      must find live differences (it does: frame times move, RNG draw
      sequences shift, records diverge) — proving the latency arm's
      byte-identity is inertness, not a blind comparator.

  RUNTIME INTROSPECTION (grep made mechanical) — one instrumented run at
      latency=100 ms: PerceptionInjector.observe is monkeypatched (in-memory
      only) to return a spy dict recording every read of "t_emit" with the
      reading file; GuidanceMachine.observe is wrapped to log the clock each
      frame is consumed at. Assert: zero t_emit VALUE reads from any
      wyzantium_sim decision module (the only value reads are wirefmt
      serialization/validation); gate.py touches t_emit solely via `in`
      (checklist item 2, presence); every frame is consumed at
      t_s == t_capture and never at t_emit.

  STATIC SCAN — every *.py under sim/wyzantium_sim and sim/wirefmt: "t_emit"
      appears only in the producer (perception/inject.py, perception/
      timing.py), the presence check (guidance/gate.py, no value access),
      and the wire layer (records.py order table, validator.py monotonicity
      check); "perception_latency_ms" only in axis plumbing + inject.py;
      the token "stale" appears in NO sim source file.

Deterministic: fixed seeds, fixed sweep points, no wall clock (run_trial has
none by design); local MuJoCo, 13 trials total, zero cloud spend. Code
freeze respected: sim/ is imported and monkeypatched in-memory only, never
edited.

Run:
  /Users/anayvaidya/Wyzantium/Ferrier/sim/.venv/bin/python \
      studies/R01_PHASE1_REVIEW/probes/probe_f016.py

Artifacts: sim/results/review_r01/F-016/{result.json, README.md}.
Exit 0 = CONFIRMED, exit 1 = REFUTED.
"""

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "sim"))

from wirefmt import records                                    # noqa: E402
from wyzantium_sim import scenarios, trial                     # noqa: E402
from wyzantium_sim.contact.mujoco_engine import MuJoCoEngine   # noqa: E402
from wyzantium_sim.guidance.machine import GuidanceMachine     # noqa: E402
from wyzantium_sim.perception import timing                    # noqa: E402
from wyzantium_sim.perception.inject import PerceptionInjector # noqa: E402

OUT_DIR = REPO / "sim" / "results" / "review_r01" / "F-016"
NOMINAL_PATH = REPO / "sim" / "scenarios" / "nominal.json"
PROBE_FILE = str(Path(__file__).resolve())

SEEDS = (101, 202, 303)
LAT_LO, LAT_HI = 10, 100     # tier1.json:20 marginal endpoints (H-06)
RATE_LO, RATE_HI = 10, 30    # tier1.json:19 cells (H-06) — live control
SPY_SEED = 101

ENGINE = MuJoCoEngine()      # run_trial calls engine.load() per call (T8)


# ------------------------------------------------------------ trial running

def nominal_sweep():
    return dict(json.loads(NOMINAL_PATH.read_text())["sweep_point"])


def expected_trial_id(seed, sp):
    """trial.py:_trial_id, recomputed independently."""
    digest = hashlib.sha1(json.dumps(
        sp, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return f"mujoco-{seed}-{digest[:8]}"


def run_one(seed, overrides, tmp_root, tag):
    sp = nominal_sweep()
    sp.update(overrides)
    out_dir = Path(tmp_root) / f"{tag}_{seed}"
    path = trial.run_trial(seed, sp, ENGINE, sp["curve_set"],
                           out_dir=out_dir)
    raw = path.read_text(encoding="utf-8").splitlines()
    return records.read_ndjson(path), raw


def normalize(lines, axis):
    """Drop exactly the fields the finding predicts may differ: t_emit on
    target_state lines; the varied axis inside header.sweep_point; trial_id
    (a sha1 derivative of the sweep_point). Everything else must survive
    byte-identically through the canonical writer."""
    out = []
    for ln in lines:
        ln = json.loads(json.dumps(ln))          # deep copy
        if ln["type"] == "trial_header":
            ln.pop("trial_id")
            ln["sweep_point"].pop(axis)
        elif ln["type"] == "target_state":
            ln.pop("t_emit", None)
        out.append(records.dumps_line(ln))
    return out


# ------------------------------------------------------ pair comparisons

def compare_latency_pair(seed, tmp_root):
    lo, lo_raw = run_one(seed, {"perception_latency_ms": LAT_LO},
                         tmp_root, "lat_lo")
    hi, hi_raw = run_one(seed, {"perception_latency_ms": LAT_HI},
                         tmp_root, "lat_hi")

    same_len = len(lo) == len(hi)
    n_raw_diff = sum(a != b for a, b in zip(lo_raw, hi_raw))
    diff_types = {}
    only_t_emit = True
    t_emit_law = True
    header_ok = True

    for a, b in zip(lo, hi):
        if records.dumps_line(a) == records.dumps_line(b):
            continue
        diff_types[a["type"]] = diff_types.get(a["type"], 0) + 1
        if a["type"] == "target_state":
            ka, kb = dict(a), dict(b)
            tea, teb = ka.pop("t_emit"), kb.pop("t_emit")
            if ka != kb:
                only_t_emit = False
            if (tea != timing.emit_time(a["t_capture"], LAT_LO)
                    or teb != timing.emit_time(b["t_capture"], LAT_HI)
                    or a["t_capture"] != b["t_capture"]):
                t_emit_law = False
        elif a["type"] == "trial_header":
            ka, kb = json.loads(json.dumps(a)), json.loads(json.dumps(b))
            ids = (ka.pop("trial_id"), kb.pop("trial_id"))
            lats = (ka["sweep_point"].pop("perception_latency_ms"),
                    kb["sweep_point"].pop("perception_latency_ms"))
            header_ok = (ka == kb and lats == (LAT_LO, LAT_HI)
                         and ids[0] == expected_trial_id(
                             seed, lo[0]["sweep_point"])
                         and ids[1] == expected_trial_id(
                             seed, hi[0]["sweep_point"]))
        else:
            only_t_emit = False      # a sim_truth/trial_result diff = live

    result_lo = next(l for l in lo if l["type"] == "trial_result")
    result_hi = next(l for l in hi if l["type"] == "trial_result")
    norm_identical = normalize(lo, "perception_latency_ms") == \
        normalize(hi, "perception_latency_ms")

    inert = (same_len and result_lo == result_hi and only_t_emit
             and t_emit_law and header_ok and norm_identical)
    return {
        "seed": seed,
        "latency_ms_pair": [LAT_LO, LAT_HI],
        "n_lines": [len(lo), len(hi)],
        "outcome": result_lo,
        "outcome_byte_equal": result_lo == result_hi,
        "raw_lines_differing": n_raw_diff,
        "differing_line_types": diff_types,
        "target_state_diffs_confined_to_t_emit": only_t_emit,
        "t_emit_equals_t_capture_plus_latency_exactly": t_emit_law,
        "header_diff_confined_to_latency_and_derived_trial_id": header_ok,
        "trial_ids": [lo[0]["trial_id"], hi[0]["trial_id"]],
        "normalized_records_byte_identical": norm_identical,
        "pair_inert": inert,
    }


def compare_rate_pair(seed, tmp_root):
    """Identical methodology on the neighboring committed timing axis; the
    comparator must report LIVE differences here for the latency result to
    mean inertness rather than blindness."""
    lo, _ = run_one(seed, {"perception_rate_hz": RATE_LO},
                    tmp_root, "rate_lo")
    hi, _ = run_one(seed, {"perception_rate_hz": RATE_HI},
                    tmp_root, "rate_hi")
    norm_lo = normalize(lo, "perception_rate_hz")
    norm_hi = normalize(hi, "perception_rate_hz")
    result_lo = next(l for l in lo if l["type"] == "trial_result")
    result_hi = next(l for l in hi if l["type"] == "trial_result")
    n_diff = (sum(a != b for a, b in zip(norm_lo, norm_hi))
              + abs(len(norm_lo) - len(norm_hi)))
    return {
        "seed": seed,
        "rate_hz_pair": [RATE_LO, RATE_HI],
        "n_lines": [len(lo), len(hi)],
        "outcomes": [result_lo, result_hi],
        "outcome_byte_equal": result_lo == result_hi,
        "normalized_records_byte_identical": norm_lo == norm_hi,
        "normalized_lines_differing_or_extra": n_diff,
        "pair_live": norm_lo != norm_hi,
    }


# ------------------------------------------------- runtime introspection

class _Rec:
    value_reads = []      # files reading line["t_emit"] / line.get("t_emit")
    contains_checks = []  # files testing "t_emit" in line


def _caller():
    f = sys._getframe(2)
    while f is not None and f.f_code.co_filename == PROBE_FILE:
        f = f.f_back
    fn = f.f_code.co_filename if f is not None else "?"
    try:
        return str(Path(fn).resolve().relative_to(REPO))
    except ValueError:
        return fn


class SpyLine(dict):
    def __getitem__(self, k):
        if k == "t_emit":
            _Rec.value_reads.append(_caller())
        return dict.__getitem__(self, k)

    def get(self, k, default=None):
        if k == "t_emit":
            _Rec.value_reads.append(_caller())
        return dict.get(self, k, default)

    def __contains__(self, k):
        if k == "t_emit":
            _Rec.contains_checks.append(_caller())
        return dict.__contains__(self, k)


def spy_run(tmp_root):
    """One full trial at latency=100 ms with every wire line spied on and
    the machine's consumption clock logged. In-memory monkeypatch only."""
    _Rec.value_reads, _Rec.contains_checks = [], []
    consumption = {"n_frames": 0, "all_at_t_capture": True,
                   "any_at_t_emit": False}

    orig_observe = PerceptionInjector.observe
    orig_mobserve = GuidanceMachine.observe

    def spy_observe(self, t, truth, sightings, stage):
        return SpyLine(orig_observe(self, t, truth, sightings, stage))

    def spy_mobserve(self, line, range_mm, t_s):
        consumption["n_frames"] += 1
        tc = dict.__getitem__(line, "t_capture")
        te = dict.__getitem__(line, "t_emit")
        if t_s != tc:
            consumption["all_at_t_capture"] = False
        if t_s == te:
            consumption["any_at_t_emit"] = True
        return orig_mobserve(self, line, range_mm, t_s)

    PerceptionInjector.observe = spy_observe
    GuidanceMachine.observe = spy_mobserve
    try:
        sp = nominal_sweep()
        sp["perception_latency_ms"] = LAT_HI   # t_emit = t_capture + 0.1 s
        trial.run_trial(SPY_SEED, sp, ENGINE, sp["curve_set"],
                        out_dir=Path(tmp_root) / "spy")
    finally:
        PerceptionInjector.observe = orig_observe
        GuidanceMachine.observe = orig_mobserve

    def tally(items):
        out = {}
        for f in items:
            out[f] = out.get(f, 0) + 1
        return out

    value_by_file = tally(_Rec.value_reads)
    contains_by_file = tally(_Rec.contains_checks)
    decision_value_reads = {f: n for f, n in value_by_file.items()
                            if f.startswith("sim/wyzantium_sim/")}
    ok = (consumption["n_frames"] > 0
          and consumption["all_at_t_capture"]
          and not consumption["any_at_t_emit"]
          and not decision_value_reads
          and all(f.startswith("sim/wirefmt/") for f in value_by_file)
          and contains_by_file.get(
              "sim/wyzantium_sim/guidance/gate.py", 0) > 0)
    return {
        "seed": SPY_SEED,
        "latency_ms": LAT_HI,
        "frames_consumed": consumption["n_frames"],
        "every_frame_consumed_at_t_capture": consumption["all_at_t_capture"],
        "any_frame_consumed_at_t_emit": consumption["any_at_t_emit"],
        "t_emit_value_reads_by_file": value_by_file,
        "t_emit_value_reads_from_wyzantium_sim_modules": decision_value_reads,
        "t_emit_presence_checks_by_file": contains_by_file,
        "note": ("wirefmt reads are the producer-side serialization layer "
                 "(records.py canonical order, validator.py t_emit >= "
                 "t_capture); gate.py's touches are membership tests only — "
                 "checklist item 2 (presence), never item 4 (staleness)"),
        "introspection_ok": ok,
    }


# ------------------------------------------------------------ static scan

def static_scan():
    def hits(root, token):
        out = {}
        for p in sorted(root.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            lines = [i + 1 for i, l in
                     enumerate(p.read_text(encoding="utf-8").splitlines())
                     if token in l]
            if lines:
                out[str(p.relative_to(REPO))] = lines
        return out

    sim_pkg = REPO / "sim" / "wyzantium_sim"
    wirefmt = REPO / "sim" / "wirefmt"
    t_emit_sim = hits(sim_pkg, "t_emit")
    t_emit_wire = hits(wirefmt, "t_emit")
    lat_sim = hits(sim_pkg, "perception_latency_ms")
    stale = {**hits(sim_pkg, "stale"), **hits(wirefmt, "stale")}
    gate_src = (sim_pkg / "guidance" / "gate.py").read_text(encoding="utf-8")

    expected_t_emit = {
        "sim/wyzantium_sim/perception/inject.py",    # producer (line 90)
        "sim/wyzantium_sim/perception/timing.py",    # producer helper (#38)
        "sim/wyzantium_sim/guidance/gate.py",        # presence check only
    }
    expected_lat = {
        "sim/wyzantium_sim/scenarios.py",            # axis list
        "sim/wyzantium_sim/trial.py",                # config plumbing
        "sim/wyzantium_sim/perception/inject.py",    # -> t_emit, nothing else
    }
    gate_value_access = ('line["t_emit"]' in gate_src
                         or '.get("t_emit"' in gate_src)
    ok = (set(t_emit_sim) == expected_t_emit
          and set(lat_sim) == expected_lat
          and not gate_value_access
          and not stale)
    return {
        "t_emit_files_in_wyzantium_sim": t_emit_sim,
        "t_emit_files_expected": sorted(expected_t_emit),
        "t_emit_files_in_wirefmt_serialization_layer": t_emit_wire,
        "perception_latency_ms_files": lat_sim,
        "perception_latency_ms_files_expected": sorted(expected_lat),
        "gate_reads_t_emit_value": gate_value_access,
        "files_containing_token_stale": stale,
        "capture_time_consumption_site": {
            "file": "sim/wyzantium_sim/kinematic/closed_loop.py",
            "lines_59_60": [
                l.rstrip() for l in
                (sim_pkg / "kinematic" / "closed_loop.py")
                .read_text(encoding="utf-8").splitlines()[58:60]],
        },
        "scan_ok": ok,
    }


# ------------------------------------------------------------------ main

def git_sha():
    try:
        return subprocess.check_output(
            ["git", "-C", str(REPO), "rev-parse", "--short", "HEAD"],
            text=True).strip()
    except Exception:
        return "unknown"


def main():
    with tempfile.TemporaryDirectory(prefix="probe_f016_") as tmp:
        latency_pairs = [compare_latency_pair(s, tmp) for s in SEEDS]
        rate_pairs = [compare_rate_pair(s, tmp) for s in SEEDS]
        introspection = spy_run(tmp)
    scan = static_scan()

    latency_inert = all(p["pair_inert"] for p in latency_pairs)
    control_live = all(p["pair_live"] for p in rate_pairs)
    confirmed = (latency_inert and control_live
                 and introspection["introspection_ok"] and scan["scan_ok"])

    result = {
        "finding": "F-016",
        "probe": "studies/R01_PHASE1_REVIEW/probes/probe_f016.py",
        "clause": ("WIRE_FORMAT consumer checklist item 4: 'Staleness "
                   "check: receive-time age beyond the consumer's staleness "
                   "bound -> treat as pose-absent'"),
        "claim": ("no consumer reads t_emit or holds a staleness bound; "
                  "perception_latency_ms feeds timing.emit_time and nothing "
                  "else; frames are consumed at capture time "
                  "(closed_loop.py:59-60) — the frozen Tier-1 latency "
                  "marginal {10,30,100} ms is behaviorally inert"),
        "code_git_sha": git_sha(),
        "sweep_point_source": "sim/scenarios/nominal.json (committed nominal)",
        "seeds": list(SEEDS),
        "arms": {
            "latency_pairs_FAILING": latency_pairs,
            "rate_pairs_CONTROL": rate_pairs,
        },
        "runtime_introspection": introspection,
        "static_scan": scan,
        "latency_axis_inert_all_pairs": latency_inert,
        "control_axis_live_all_pairs": control_live,
        "verdict": "CONFIRMED" if confirmed else "REFUTED",
        "confirmed": confirmed,
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    out = OUT_DIR / "result.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    print(f"\nwrote {out}", file=sys.stderr)
    return 0 if confirmed else 1


if __name__ == "__main__":
    sys.exit(main())
