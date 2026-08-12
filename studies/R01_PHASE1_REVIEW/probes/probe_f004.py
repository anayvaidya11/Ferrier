#!/usr/bin/env python
"""Probe F-004 — stale wall timers across D-005 attempt boundaries.

Claim under test (FINDINGS.md F-004): GuidanceMachine's _hold_since /
_ring_absent_since / _ambiguity_streak are initialized only in __init__ and
never reset at attempt boundaries — trial.py's boundary handling touches only
machine.stage ("acquire", trial.py:181) and machine.attempt_n (trial.py:238,
248, 267, 308). A fresh D-005 attempt therefore inherits the previous
attempt's open window, and its first qualifying frame can abort/escalate
instantly instead of after the committed sustained window.

Clauses:
  D-036 — ring absence aborts on "< 2 inner tags CONTINUOUSLY for 5 s"
          (row 3); stochastic gaps reject frames.
  D-034 — "single blips are held frames, not aborts"; row 2 escalates only
          when the dark window exceeds HOLD_TIMEOUT_S (5 s).
  D-005 — an abort backs out 300 mm and re-approaches as a NEW attempt;
          trial.py:181's own comment: "every attempt re-acquires (resync)".

Method (probe33 style, per variant):
  arm 1 (repro)  — ONE machine driven through attempt 1 that ends with an
                   open window, then the attempt boundary exactly as
                   trial.py performs it, then attempt 2's frame stream.
  arm 2 (control)— a FRESH machine fed the IDENTICAL attempt-2 stream
                   (same absolute t_s values, same frames).

Variants:
  R  — D-036 ring-absence window (abort_retry "inner_ring_absent")
  Da — D-034 dark window, attempt-2 darkness starting at the boundary
  Db — D-034 single isolated dark blip as attempt 2's first frame
  S  — row-5 ambiguity streak across a contact-jam boundary
       (trial.py:307-308 path: no machine abort decision ends the attempt)

Fully deterministic: the machine has no RNG stream (#60) and every frame
timestamp is T0 + k*DT integer-indexed. No MuJoCo step is needed — the
finding is entirely in the guidance layer; local, zero spend, < 1 s.

Code freeze respected: sim/ is imported, never modified. The attempt
boundary is emulated exactly as trial.py performs it (stage + attempt_n
only), which is the point of the finding.

Run:
  /Users/anayvaidya/Wyzantium/Ferrier/sim/.venv/bin/python \
      studies/R01_PHASE1_REVIEW/probes/probe_f004.py
"""

import json
import os
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..",
                                    ".."))
sys.path.insert(0, os.path.join(REPO, "sim"))

from wyzantium_sim.guidance.machine import (   # noqa: E402
    AMBIGUITY_PERSIST_FRAMES, GuidanceMachine, HOLD_TIMEOUT_S)

OUT_DIR = os.path.join(REPO, "sim", "results", "review_r01", "F-004")

RATE_HZ = 30.0
DT = 1.0 / RATE_HZ
T0 = 100.0                 # arbitrary fixed stream origin
CONF_MIN = 0.85            # #29 default
ATTEMPTS_MAX = 3           # #27 default
TIME_BUDGET_S = 900.0      # #55 default

MAX_CONTROL_FRAMES = 400   # > 5 s wall at 30 Hz, bounded


# ---------------------------------------------------------------- frames
# Synthetic target_state lines, same shapes as sim/tests/test_guidance.py.

def clean_outer():
    """Detected outer-tag tracking frame (outer range): action=continue."""
    return {"pose_source": "outer_tag", "conf": 0.90, "stage": "outer_servo",
            "tags": [{"id": 0, "reproj_err": 0.4, "ambiguity_flag": False,
                      "ambiguity_ratio": 1.0}]}


def gap_frame():
    """One inner tag at inner range: < 2-inner ring gap (D-036 domain)."""
    return {"pose_source": "inner_ring", "conf": 0.90, "stage": "inner_servo",
            "tags": [{"id": 2, "reproj_err": 0.5, "ambiguity_flag": False,
                      "ambiguity_ratio": 1.0}]}


def dark_frame():
    """Fully-dark frame — no tags, pose_source none (D-034 row-2 domain)."""
    return {"pose_source": "none", "conf": 0.0, "stage": "outer_servo",
            "pose": None, "tags": None}


def flagged_frame():
    """Ambiguity-flagged detection at inner range (IS §8 row 5 domain)."""
    return {"pose_source": "multi_tag_fused", "conf": 0.90,
            "stage": "inner_servo",
            "tags": [{"id": 1, "reproj_err": 0.6, "ambiguity_flag": True,
                      "ambiguity_ratio": 0.6},
                     {"id": 2, "reproj_err": 0.5, "ambiguity_flag": False,
                      "ambiguity_ratio": 1.0}]}


def make_machine():
    return GuidanceMachine(conf_min=CONF_MIN, attempts_max=ATTEMPTS_MAX,
                           time_budget_s=TIME_BUDGET_S)


def feed(machine, stream):
    """Feed [(k, line, range_mm), ...]; return list of (k, Decision)."""
    return [(k, machine.observe(line, range_mm, T0 + k * DT))
            for k, line, range_mm in stream]


def t_of(k):
    return T0 + k * DT


def attempt_boundary(machine):
    """Exactly what trial.py does between attempts and nothing more:
    machine.stage = "acquire" (trial.py:181). attempt_n was already
    advanced by _abort_retry (trial.py:238)."""
    machine.stage = "acquire"


def run_until(machine, start_k, mkline, range_mm, stop_actions,
              max_frames=MAX_CONTROL_FRAMES):
    """Feed identical frames until an action in stop_actions (or cap).
    Returns (frames_fed, last_decision, k_last)."""
    k = start_k
    for i in range(max_frames):
        d = machine.observe(mkline(), range_mm, t_of(k))
        if d.action in stop_actions:
            return i + 1, d, k
        k += 1
    return max_frames, d, k - 1


# ------------------------------------------------------------- variant R
def variant_ring():
    """D-036 window carried across a D-005 boundary."""
    doc_window_s = HOLD_TIMEOUT_S

    def attempt1(m):
        # 1 s clean outer tracking, then 4.5 s of ring gaps (window opens,
        # every frame reject_frame — inside the wall), then attempt 1 ends
        # on an unrelated row-5 ambiguity abort (flagged frames never touch
        # _ring_absent_since).
        k = 0
        for _ in range(30):
            d = m.observe(clean_outer(), 1500.0, t_of(k)); k += 1
            assert d.action == "continue", d
        window_open_k = k
        for _ in range(135):                      # 4.5 s < 5 s wall
            d = m.observe(gap_frame(), 250.0, t_of(k)); k += 1
            assert d.action == "reject_frame", d
        for _ in range(AMBIGUITY_PERSIST_FRAMES):
            d = m.observe(flagged_frame(), 250.0, t_of(k)); k += 1
        assert d.action == "abort_retry", d
        assert d.abort_reason == "ambiguity_persistent", d
        return k, window_open_k

    # attempt-2 stream: 8 s of HEALTHY outer tracking during the D-005
    # backout/re-approach (>300 mm: cannot reset the ring window — the
    # reset at machine.py:183 sits inside the <=300 mm guard), then ring
    # gaps at 250 mm.
    def attempt2(m, k):
        travel = [(k + i, clean_outer(), 1500.0) for i in range(240)]
        for kk, line, rng in travel:
            d = m.observe(line, rng, t_of(kk))
            assert d.action == "continue", d
        k2 = k + 240
        first_gap_t = t_of(k2)
        n, d, k_last = run_until(m, k2, gap_frame, 250.0,
                                 ("abort_retry", "escalate"))
        return {"first_gap_frame_t_s": round(first_gap_t, 6),
                "frames_below_2_inner_before_abort": n,
                "in_attempt_absence_s": round(t_of(k_last) - first_gap_t, 6),
                "action": d.action, "abort_reason": d.abort_reason}, k2

    # arm 1: one machine across the boundary
    m1 = make_machine()
    k_end, window_open_k = attempt1(m1)
    attempt_boundary(m1)
    arm1, k2 = attempt2(m1, k_end)
    arm1["attempt_n_at_abort"] = m1.attempt_n
    arm1["stale_window_opened_t_s"] = round(t_of(window_open_k), 6)
    arm1["stale_age_at_first_gap_s"] = round(
        arm1["first_gap_frame_t_s"] - t_of(window_open_k), 6)

    # arm 2: fresh machine, identical attempt-2 stream (same t_s values)
    m2 = make_machine()
    arm2, _ = attempt2(m2, k_end)

    return {
        "clause": "D-036: '< 2 inner tags continuously for 5 s' aborts; "
                  "stochastic gaps reject frames",
        "doc_window_s": doc_window_s,
        "attempt1_absence_carried_s": 4.5,
        "arm1_stale_machine": arm1,
        "arm2_fresh_machine_control": arm2,
        "violation": (arm1["in_attempt_absence_s"] < 1.0
                      and arm1["action"] == "abort_retry"
                      and arm2["in_attempt_absence_s"] > doc_window_s),
    }


# ------------------------------------------------------------ variant Da
def variant_dark_immediate():
    """D-034 dark window carried across the boundary; attempt 2 goes dark
    at its first frame. The stale machine escalates after a fraction of
    the wall; the fresh control needs the full 5 s."""
    def attempt1(m):
        k = 0
        for _ in range(30):
            d = m.observe(clean_outer(), 2500.0, t_of(k)); k += 1
            assert d.action == "continue", d
        window_open_k = k
        for _ in range(135):                      # 4.5 s dark, all held
            d = m.observe(dark_frame(), 2500.0, t_of(k)); k += 1
            assert d.action == "hold", d
        for _ in range(AMBIGUITY_PERSIST_FRAMES):  # row 5 ends the attempt
            d = m.observe(flagged_frame(), 250.0, t_of(k)); k += 1
        assert d.action == "abort_retry", d
        return k, window_open_k

    def attempt2(m, k):
        first_dark_t = t_of(k)
        n, d, k_last = run_until(m, k, dark_frame, 2500.0, ("escalate",))
        return {"first_dark_frame_t_s": round(first_dark_t, 6),
                "dark_frames_before_escalate": n,
                "in_attempt_darkness_s": round(t_of(k_last) - first_dark_t, 6),
                "action": d.action, "abort_reason": d.abort_reason}

    m1 = make_machine()
    k_end, window_open_k = attempt1(m1)
    attempt_boundary(m1)
    arm1 = attempt2(m1, k_end)
    arm1["stale_window_opened_t_s"] = round(t_of(window_open_k), 6)

    m2 = make_machine()
    arm2 = attempt2(m2, k_end)

    return {
        "clause": "D-034: row 2 escalates only when the dark window "
                  "exceeds HOLD_TIMEOUT_S; any detection resets",
        "doc_window_s": HOLD_TIMEOUT_S,
        "attempt1_darkness_carried_s": 4.5,
        "arm1_stale_machine": arm1,
        "arm2_fresh_machine_control": arm2,
        "violation": (arm1["in_attempt_darkness_s"]
                      < arm2["in_attempt_darkness_s"] - 1.0
                      and arm1["action"] == "escalate"),
    }


# ------------------------------------------------------------ variant Db
def variant_dark_blip():
    """D-034's exact sentence — 'single blips are held frames, not
    aborts' — violated: ONE isolated dark frame as attempt 2's first
    frame escalates on the stale machine, holds on the fresh one."""
    def attempt1(m):
        k = 0
        for _ in range(30):
            d = m.observe(clean_outer(), 2500.0, t_of(k)); k += 1
            assert d.action == "continue", d
        for _ in range(135):
            d = m.observe(dark_frame(), 2500.0, t_of(k)); k += 1
            assert d.action == "hold", d
        for _ in range(AMBIGUITY_PERSIST_FRAMES):
            d = m.observe(flagged_frame(), 250.0, t_of(k)); k += 1
        assert d.action == "abort_retry", d
        return k

    m1 = make_machine()
    k_end = attempt1(m1)
    attempt_boundary(m1)
    k_blip = k_end + 240          # blip arrives 8 s into attempt 2
    d1 = m1.observe(dark_frame(), 2500.0, t_of(k_blip))

    m2 = make_machine()
    d2 = m2.observe(dark_frame(), 2500.0, t_of(k_blip))

    return {
        "clause": "D-034: 'single blips are held frames, not aborts'",
        "blip_t_s": round(t_of(k_blip), 6),
        "arm1_stale_machine": {"action": d1.action,
                               "abort_reason": d1.abort_reason,
                               "in_attempt_darkness_s": 0.0,
                               "dark_frames_seen_this_attempt": 1},
        "arm2_fresh_machine_control": {"action": d2.action,
                                       "abort_reason": d2.abort_reason},
        "violation": d1.action == "escalate" and d2.action == "hold",
        "note": "no frames fed between boundary and blip: any attempt-2 "
                "frame reaching machine.py:214 (clean fall-through) resets "
                "_hold_since, so this arm stands for re-approaches whose "
                "early frames are non-resetting (dark/flagged/gap) — the "
                "gate cell's dropout regime; variant Da needs no such gap",
    }


# ------------------------------------------------------------- variant S
def variant_streak():
    """_ambiguity_streak carried across a contact-jam boundary
    (trial.py:306-314: jam consumes the attempt with NO machine abort
    decision, so no row-5 reset fires; only attempt_n is touched)."""
    def attempt1(m):
        k = 0
        for _ in range(30):
            d = m.observe(clean_outer(), 1500.0, t_of(k)); k += 1
            assert d.action == "continue", d
        for _ in range(AMBIGUITY_PERSIST_FRAMES - 1):   # streak parks at 4
            d = m.observe(flagged_frame(), 250.0, t_of(k)); k += 1
            assert d.action == "reject_frame", d
        return k

    def boundary_contact_jam(m):
        # trial.py:307-308 after a jam: attempt += 1; machine.attempt_n =
        # attempt. Next loop iteration does machine.stage = "acquire".
        m.attempt_n += 1
        m.stage = "acquire"

    m1 = make_machine()
    k_end = attempt1(m1)
    boundary_contact_jam(m1)
    k2 = k_end + 240
    n1, d1, _ = run_until(m1, k2, flagged_frame, 250.0, ("abort_retry",
                                                         "escalate"))

    m2 = make_machine()
    m2.attempt_n = 2              # mirror the attempt index
    n2, d2, _ = run_until(m2, k2, flagged_frame, 250.0, ("abort_retry",
                                                         "escalate"))

    return {
        "clause": "IS §8 row 5 'persistent' realized as "
                  f"AMBIGUITY_PERSIST_FRAMES={AMBIGUITY_PERSIST_FRAMES} "
                  "consecutive flagged frames",
        "doc_window_frames": AMBIGUITY_PERSIST_FRAMES,
        "attempt1_flagged_frames_carried": AMBIGUITY_PERSIST_FRAMES - 1,
        "arm1_stale_machine": {
            "in_attempt_flagged_frames_before_abort": n1,
            "action": d1.action, "abort_reason": d1.abort_reason},
        "arm2_fresh_machine_control": {
            "in_attempt_flagged_frames_before_abort": n2,
            "action": d2.action, "abort_reason": d2.abort_reason},
        "violation": n1 == 1 and n2 == AMBIGUITY_PERSIST_FRAMES,
    }


def git_sha():
    try:
        return subprocess.check_output(
            ["git", "-C", REPO, "rev-parse", "--short", "HEAD"],
            text=True).strip()
    except Exception:
        return "unknown"


def main():
    variants = {
        "R_ring_absence_D036": variant_ring(),
        "Da_dark_window_D034": variant_dark_immediate(),
        "Db_dark_blip_D034": variant_dark_blip(),
        "S_ambiguity_streak_row5": variant_streak(),
    }
    confirmed = all(v["violation"] for v in variants.values())
    result = {
        "finding": "F-004",
        "probe": "probe_f004.py",
        "claim": "GuidanceMachine wall timers (_hold_since, "
                 "_ring_absent_since, _ambiguity_streak) survive D-005 "
                 "attempt boundaries; a new attempt's first qualifying "
                 "frame aborts/escalates instantly instead of after the "
                 "committed sustained window",
        "code_git_sha": git_sha(),
        "machine_constants": {"HOLD_TIMEOUT_S": HOLD_TIMEOUT_S,
                              "AMBIGUITY_PERSIST_FRAMES":
                                  AMBIGUITY_PERSIST_FRAMES,
                              "conf_min": CONF_MIN,
                              "attempts_max": ATTEMPTS_MAX,
                              "time_budget_s": TIME_BUDGET_S},
        "stream": {"rate_hz": RATE_HZ, "t0_s": T0,
                   "deterministic": True,
                   "rng": "none (machine has no RNG stream, #60)"},
        "boundary_emulation": {
            "abort_retry": "machine.stage='acquire' only (trial.py:181; "
                           "attempt_n already advanced by _abort_retry)",
            "contact_jam": "attempt_n += 1 then stage='acquire' "
                           "(trial.py:307-308, 181)"},
        "variants": variants,
        "confirmed": confirmed,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, "result.json")
    with open(out, "w") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    print(json.dumps(result, indent=2))
    print(f"\nwrote {out}", file=sys.stderr)
    return 0 if confirmed else 1


if __name__ == "__main__":
    sys.exit(main())
