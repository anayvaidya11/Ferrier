# F-016 probe — latency axis (#38) behaviorally inert; WF checklist item 4 unrealized

Run: `sim/.venv/bin/python studies/R01_PHASE1_REVIEW/probes/probe_f016.py`.

**Verdict: CONFIRMED** — `latency_axis_inert_all_pairs: true` (10 ms vs
100 ms arms: identical outcomes, byte-diffs confined to t_emit fields and
the header's sweep_point latency value) while the control axis is live.
Mechanism: `perception_latency_ms` is consumed solely at inject.py:90 to
stamp t_emit; no decision consumer reads t_emit (gate does presence-only
checks; frames consumed at capture time, closed_loop.py:59–60); no
staleness bound exists anywhere in sim code. The frozen Tier-1 latency
marginal is fake-flat.
