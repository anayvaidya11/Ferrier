"""T11 — A-007 replay artifacts, rendered from logged state ONLY.

The animation draws the head-center trajectory from the record's sim_truth
lines against the committed D-016 funnel cross-section, plus the logged
wall-wrench trace — no imagery anywhere (D-007 untouched: the record holds
no pixels, and none are synthesized). Every artifact is labeled SIMULATED
and carries its trial_id; the sidecar JSON is the A-007 traceability map
from artifact → committed trial record.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import animation  # noqa: E402

from wyzantium_sim import geometry  # noqa: E402

_LABEL = "SIMULATED"
_MAX_FRAMES = 240


def _parse(record_path):
    lines = [json.loads(l) for l in
             Path(record_path).read_text(encoding="utf-8").splitlines()]
    header, result = lines[0], lines[-1]
    ts, xs, ys, wrench_t, wrench_mag = [], [], [], [], []
    for l in lines:
        if l.get("type") != "sim_truth":
            continue
        p = l["T_world_head"]["t"]
        ts.append(l["t"])
        xs.append(p[0] * 1000.0)   # wire metres → mm (repo convention)
        ys.append(p[1] * 1000.0)
        if "contact_wrench" in l:
            w = l["contact_wrench"]
            wrench_t.append(l["t"])
            wrench_mag.append((w[0] ** 2 + w[1] ** 2 + w[2] ** 2) ** 0.5)
    return header, result, ts, xs, ys, wrench_t, wrench_mag


def _funnel_outline(ax):
    """D-016 cross-section in the x-y plane: mouth at x=0 (Ø220), throat at
    depth 180 (Ø42) — committed geometry, not imagery."""
    mouth_r = geometry.FUNNEL_MOUTH_DIAMETER_MM / 2.0
    throat_r = geometry.FUNNEL_THROAT_DIAMETER_MM / 2.0
    depth = geometry.FUNNEL_DEPTH_MM
    for sign in (1.0, -1.0):
        ax.plot([0.0, -depth], [sign * mouth_r, sign * throat_r],
                color="0.35", lw=2)
    ax.axvline(0.0, color="0.8", lw=0.8, ls=":")


def render_artifact(record_path, out_dir, *, fps=24,
                    max_frames=_MAX_FRAMES) -> tuple:
    record_path = Path(record_path)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    header, result, ts, xs, ys, wt, wm = _parse(record_path)
    trial_id = header["trial_id"]

    stride = max(1, len(ts) // max_frames)
    idx = list(range(0, len(ts), stride))
    if idx[-1] != len(ts) - 1:
        idx.append(len(ts) - 1)

    fig, (ax_tr, ax_w) = plt.subplots(
        1, 2, figsize=(10, 4.4), gridspec_kw={"width_ratios": [3, 2]})
    fig.suptitle(f"{_LABEL} — trial {trial_id} — outcome: "
                 f"{result['outcome']}", fontsize=11)
    fig.text(0.5, 0.015,
             "WyZantium Phase 1 · replay of a committed trial record · "
             "rendered from logged state only (D-007: no imagery)",
             ha="center", fontsize=7, color="0.4")

    _funnel_outline(ax_tr)
    ax_tr.set_xlabel("x (mm, stud frame)")
    ax_tr.set_ylabel("y (mm)")
    ax_tr.set_xlim(max(xs) * 1.05, min(min(xs), -200.0) * 1.1)
    yspan = max(200.0, max(abs(v) for v in ys) * 1.2)
    ax_tr.set_ylim(-yspan, yspan)
    trail, = ax_tr.plot([], [], color="tab:blue", lw=1)
    head, = ax_tr.plot([], [], "o", color="tab:red", ms=6)

    ax_w.set_xlabel("t (s)")
    ax_w.set_ylabel("|wall force| (N)")
    ax_w.set_xlim(ts[0], ts[-1])
    ax_w.set_ylim(0.0, max(wm) * 1.15 if wm else 1.0)
    wline, = ax_w.plot([], [], color="tab:orange", lw=1.2)

    def draw(k):
        i = idx[k]
        trail.set_data(xs[:i + 1], ys[:i + 1])
        head.set_data([xs[i]], [ys[i]])
        upto = ts[i]
        pts = [(a, b) for a, b in zip(wt, wm) if a <= upto]
        if pts:
            wline.set_data([p[0] for p in pts], [p[1] for p in pts])
        return trail, head, wline

    anim = animation.FuncAnimation(fig, draw, frames=len(idx), blit=True)
    gif_path = out_dir / f"{trial_id}.simulated.gif"
    anim.save(gif_path, writer=animation.PillowWriter(fps=fps))
    plt.close(fig)

    sidecar = out_dir / f"{trial_id}.simulated.json"
    with open(sidecar, "w", encoding="utf-8") as f:
        json.dump({
            "label": _LABEL.lower(),
            "trial_id": trial_id,
            "outcome": result["outcome"],
            "attempts_used": result["attempts_used"],
            "t_total": result["t_total"],
            "source_record": str(record_path),
            "code_git_sha": header["code_git_sha"],
            "source": "A-007; PHASE1_PLAN §2 replay/ row; rendered from "
                      "logged state only (D-007)",
        }, f, indent=1)
    return gif_path, sidecar
