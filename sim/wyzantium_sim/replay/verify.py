"""T11 — byte-identical replay from a record's header (WIRE_FORMAT
contract: seed, SHA, engine, sweep_point, solver reproduce the trial).

Statuses tell the honest story apart:
  identical                — every byte matches.
  identical_except_code_sha — all lines match except the header's
                              code_git_sha (replayed at a different commit;
                              the record's content is reproduced, its
                              provenance stamp is today's).
  diverged                 — anything else; n_diff_lines counts them.
"""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path

from wyzantium_sim import trial
from wyzantium_sim.contact.engine import SolverSettings
from wyzantium_sim.contact.mujoco_engine import MuJoCoEngine


def _newton():
    from wyzantium_sim.contact.newton_engine import NewtonEngine
    return NewtonEngine()


ENGINE_FACTORIES = {"mujoco": MuJoCoEngine, "newton": _newton}


@dataclass(frozen=True)
class ReplayVerdict:
    status: str            # identical | identical_except_code_sha | diverged
    replayed_path: Path
    n_diff_lines: int


def replay_record(record_path, out_dir=None,
                  engine_factories=ENGINE_FACTORIES) -> ReplayVerdict:
    record_path = Path(record_path)
    original = record_path.read_bytes()
    header = json.loads(original.split(b"\n", 1)[0])

    engine = engine_factories[header["engine"]["name"]]()
    solver = SolverSettings(**header["solver"])
    sp = header["sweep_point"]

    if out_dir is None:
        out_dir = Path(tempfile.mkdtemp(prefix="wyz-replay-"))
    replayed = trial.run_trial(header["seed"], sp, engine, sp["curve_set"],
                               out_dir=Path(out_dir), solver=solver)
    fresh = replayed.read_bytes()

    if fresh == original:
        return ReplayVerdict("identical", replayed, 0)

    a, b = original.split(b"\n"), fresh.split(b"\n")
    if len(a) == len(b):
        diff = [i for i, (x, y) in enumerate(zip(a, b)) if x != y]
        if diff == [0]:
            ha, hb = json.loads(a[0]), json.loads(b[0])
            ha.pop("code_git_sha"), hb.pop("code_git_sha")
            if ha == hb:
                return ReplayVerdict("identical_except_code_sha", replayed, 1)
        n = len(diff)
    else:
        n = abs(len(a) - len(b)) + sum(
            x != y for x, y in zip(a, b))
    return ReplayVerdict("diverged", replayed, n)
