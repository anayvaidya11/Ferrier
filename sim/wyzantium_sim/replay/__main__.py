"""CLI: python -m wyzantium_sim.replay {verify,render} <record> [--out DIR]"""

from __future__ import annotations

import argparse
from pathlib import Path

from wyzantium_sim.replay.artifact import render_artifact
from wyzantium_sim.replay.verify import replay_record


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wyzantium_sim.replay")
    sub = ap.add_subparsers(dest="cmd", required=True)
    pv = sub.add_parser("verify")
    pv.add_argument("record", type=Path)
    pv.add_argument("--out", type=Path, default=None)
    pr = sub.add_parser("render")
    pr.add_argument("record", type=Path)
    pr.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)

    if args.cmd == "verify":
        v = replay_record(args.record, out_dir=args.out)
        print(f"{v.status} (diff lines: {v.n_diff_lines}) → {v.replayed_path}")
        return 0 if v.status != "diverged" else 1
    gif, sidecar = render_artifact(args.record, args.out)
    print(f"artifact: {gif}\nsidecar:  {sidecar}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
