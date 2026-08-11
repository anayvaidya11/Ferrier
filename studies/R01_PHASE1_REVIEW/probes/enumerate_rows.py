"""R01 matrix enumeration — greps the numbered contract structures and emits
the MATRIX.csv skeleton, so the row count is itself auditable (the
transcription-test culture applied to the review).

Read-only over the contract docs; writes studies/R01_PHASE1_REVIEW/MATRIX.csv.
Run:  python3 studies/R01_PHASE1_REVIEW/probes/enumerate_rows.py

Row sources (expected counts asserted below):
  P-01..P-65    PHASE1_PARAMETERS.md numbered rows          (65)
  IS8-01..18    INTERFACE_SPEC.md §8 failure rows           (18)
  D-xxx         DECISIONS.md headers (struck → N/A-SUPERSEDED)
  WF-C1..C7     WIRE_FORMAT.md consumer checklist            (7)
  A6-1..7       ARCHITECTURE.md §6 output items              (7)
  FT-P01..P19   FAILURE_TAXONOMY.md classifier precedence   (19)
  T-*           PHASE1_PLAN.md §4 build-order gates         (16)
  C-01..C-14    CLAIMS.md register rows                     (14)
  ISS/WF/A4/X/H manual structural clauses (unnumbered; embedded list below)
"""
import csv
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parents[1] / "MATRIX.csv"
ANCHOR_SHA = "cdf7fbf"  # review anchor; code tree == freeze SHA b493e7a

COLUMNS = ["row_id", "lane", "clause", "anchor", "binding", "code_ref",
           "test_ref", "verdict", "evidence", "finding_id", "reviewer",
           "date"]

# Primary lane per decision ID (seams get joint ownership in LANES.md; the
# matrix records one owning lane per row). Unlisted decisions default to F.
DECISION_LANES = {
    "D-004": "A", "D-005": "A", "D-013": "A", "D-017": "A", "D-018": "A",
    "D-029": "A", "D-030": "A", "D-033": "A", "D-034": "A", "D-035": "A",
    "D-036": "A",
    "D-007": "B", "D-008-R": "B", "D-011": "B", "D-012": "B", "D-023": "B",
    "D-025": "B", "D-031": "B",
    "D-020": "C", "D-026": "C", "D-027": "C", "D-028": "C",
    "D-006": "D", "D-015": "D", "D-016": "D", "D-019": "D", "D-024": "D",
    "D-037": "D",
}

T_LANES = {"T0": "G", "T1": "E", "T2": "F", "T3": "D", "T4a": "D",
           "T4b": "B", "T4c": "C", "T5": "D", "T6": "A", "T7": "C",
           "T8": "E", "T9": "A", "T10": "F", "T11": "E", "T12": "F",
           "T13": "G"}

# Unnumbered structural clauses the greps cannot enumerate. Extending this
# list is the sanctioned way to grow the matrix; ad-hoc CSV edits are not.
MANUAL_ROWS = [
    ("ISS-01", "D", "IS §4 frame conventions (quaternion w,x,y,z; head_frame +x boresight)", "INTERFACE_SPEC §4"),
    ("ISS-02", "D", "IS §3.5 tag-ID→transform table transcribed exactly", "INTERFACE_SPEC §3.5"),
    ("ISS-03", "B", "IS §3.4 ID/variant block; wrong-ID rejection basis", "INTERFACE_SPEC §3.4"),
    ("ISS-04", "D", "IS §5 tolerance budget allocations = sweep centers (×{0.5,1,2} via D-019)", "INTERFACE_SPEC §5"),
    ("ISS-05", "D", "IS §6 capture plane x=+50mm; HandoffState field list; 160mm annulus", "INTERFACE_SPEC §6"),
    ("ISS-06", "C", "IS §6 lip band radial [110,125]mm consistency with IS8-16 detection", "INTERFACE_SPEC §6"),
    ("ISS-07", "D", "IS §7 mounting assumptions vs D-024 envelope", "INTERFACE_SPEC §7"),
    ("ISS-08", "F", "IS §9/§9.1 sweep axes all realized in harness or excluded by recorded decision (H-17 lens)", "INTERFACE_SPEC §9"),
    ("ISS-09", "G", "IS §10 known weaknesses still accurate at HEAD", "INTERFACE_SPEC §10"),
    ("ISS-10", "A", "IS §2.3 confidence-gated abort: refuse→imagery→human, no non-visual metric pose", "INTERFACE_SPEC §2.3"),
    ("ISS-11", "C", "IS §2.1 load-path derivation consistency with T1 model constants", "INTERFACE_SPEC §2.1"),
    ("ISS-12", "B", "IS §3.2 20px robust-decode floor = curves.detection_onset_px", "INTERFACE_SPEC §3.2"),
    ("WF-S1", "E", "Omitted-not-zeroed rule (pose without pose_cov ⇒ pose-absent; worked failure example)", "WIRE_FORMAT §fields"),
    ("WF-S2", "E", "Canonical NDJSON writer: shortest round-trip floats, fixed key order, LF (#60 byte-identity)", "WIRE_FORMAT; #60"),
    ("WF-S3", "E", "sim_truth cadence: every physics step post-handoff, every kinematic step pre-handoff (#59)", "WIRE_FORMAT; #59"),
    ("WF-S4", "E", "trial_result.false_capture optional additive field (H-16) populated on IS8-16 sub-path", "WIRE_FORMAT; H-16"),
    ("WF-S5", "E", "trial_header #33 solver block + compute-instance identity + curve_set in sweep_point", "WIRE_FORMAT; #33/#58"),
    ("A4-1", "C", "Conformance: offset stud drop — wrench recovers sign+magnitude-ordering of lateral offset", "PHASE1_PLAN §3 (1)"),
    ("A4-2", "C", "Conformance: symmetric throat wedge — high-axial/near-zero-lateral signature observable", "PHASE1_PLAN §3 (2)"),
    ("A4-3", "C", "Conformance: lip-band strike — contact radius within [110,125]mm", "PHASE1_PLAN §3 (3)"),
    ("A4-4", "E", "Conformance: determinism — same seed twice → identical trajectories (replay contract)", "PHASE1_PLAN §3 (4)"),
    ("A4-5", "C", "Conformance: spring/restitution/friction sanity vs closed-form single-contact cases", "PHASE1_PLAN §3 (5)"),
    ("A5-1", "F", "A-004: both $/1k measurements committed (CPU leg only exists — P-08(a) waiver pending)", "PHASE1_PLAN §3; ARCH §5"),
    ("A5-2", "F", "P-02: runner meters cumulative spend against $100 ceiling; ledger cross-foots", "PHASE1_PLAN §2 doe/; A-011"),
    ("X-1", "F", "Exit: ≥10,000 committed trials", "PHASE1_PLAN §7"),
    ("X-2", "F", "Exit: ARCH §6.1–6.7 outputs present", "PHASE1_PLAN §7"),
    ("X-3", "F", "Exit: gate computed only against pre-committed gate_moderate.json (D-029 verbatim transcription)", "PHASE1_PLAN §7; D-029"),
    ("X-4", "G", "Exit: every REPORT claim traceable to a committed file", "PHASE1_PLAN §7"),
    ("X-5", "G", "Exit: CLAIMS rows landed with replay artifacts (A-007)", "PHASE1_PLAN §7"),
    ("X-6", "E", "Exit: three load-bearing tests pass before any committed DOE run (golden round-trip; same-seed byte-identical; #63 pinned cross-check)", "PHASE1_PLAN §7"),
    ("H-17", "D", "Host pitch/roll swept axes unrealized in harness; D-029 marginalization currently a no-op", "HOLES.md H-17"),
    ("FT-15X", "A", "IS8-15 unreachable as classifier output while remaining in wire enum (test-enforced)", "FAILURE_TAXONOMY §precedence"),
    ("G-1", "G", "freeze_prior_v1/MANIFEST.json provenance fields accurate (known: $0-expansion mangle line 18)", "sim/results/freeze_prior_v1"),
    ("G-2", "G", "records_storage 'not retained' vs ARCH §6.4 'committed, reproducible dataset' wording", "ARCH §6.4"),
    ("G-3", "G", "tier3_prior_v1 artifacts: regeneration at doc-only descendant SHA auditable from sidecars", "sim/results/tier3_prior_v1"),
    ("G-4", "G", "HOW-FAR-ALONG / ROADMAP / PENDING_HUMAN status lines accurate at HEAD", "HOW-FAR-ALONG.md"),
    ("G-5", "G", "tools/charts.py location (repo root) vs PHASE1_PLAN §2 table placement", "PHASE1_PLAN §2"),
    ("G-6", "G", "Superseded-decision pointer integrity (struck rows name successors; no orphan references)", "DECISIONS.md"),
]


def read(name):
    return (REPO / name).read_text()


def section(text, start_pat, end_pat):
    s = re.search(start_pat, text, re.M)
    e = re.search(end_pat, text[s.end():], re.M)
    return text[s.end():s.end() + e.start()] if e else text[s.end():]


def trim(s, n=140):
    s = re.sub(r"\s+", " ", s).strip().strip("*").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def rows_params():
    out = []
    for m in re.finditer(r"^\|\s*(\d+)\s*\|([^|]+)\|([^|]+)\|([^|]+)\|",
                         read("PHASE1_PARAMETERS.md"), re.M):
        n = int(m.group(1))
        out.append((f"P-{n:02d}", "F",
                    f"{trim(m.group(2), 60)} = {trim(m.group(3), 60)}",
                    f"PHASE1_PARAMETERS #{n} (src: {trim(m.group(4), 40)})"))
    assert len(out) == 65, f"expected 65 params, got {len(out)}"
    return out


def rows_is8():
    body = section(read("INTERFACE_SPEC.md"), r"^## 8\.", r"^## 9\.")
    out = []
    for m in re.finditer(r"^\|\s*(\d+)\s*\|([^|]+)\|([^|]+)\|", body, re.M):
        n = int(m.group(1))
        out.append((f"IS8-{n:02d}", "A",
                    f"{trim(m.group(2), 50)} — detect: {trim(m.group(3), 80)}",
                    f"INTERFACE_SPEC §8 row {n}"))
    assert len(out) == 18, f"expected 18 IS8 rows, got {len(out)}"
    return out


def rows_decisions():
    out = []
    for m in re.finditer(r"^###\s+(~~)?\s*(D-\d{3}(?:-R)?)\s*—\s*(.+)$",
                         read("DECISIONS.md"), re.M):
        struck, did, title = m.group(1), m.group(2), m.group(3)
        row = [did, DECISION_LANES.get(did, "F"), trim(title),
               f"DECISIONS.md {did}"]
        if struck:
            row += ["", "", "", "N/A-SUPERSEDED",
                    "struck in DECISIONS.md; successor pointer checked by G-6"]
        out.append(tuple(row))
    assert len(out) >= 38, f"expected >=38 decision headers, got {len(out)}"
    return out


def rows_wf_checklist():
    body = section(read("WIRE_FORMAT.md"), r"^## Consumer checklist", r"^## ")
    out = [(f"WF-C{m.group(1)}", "E", trim(m.group(2)),
            f"WIRE_FORMAT consumer checklist item {m.group(1)}")
           for m in re.finditer(r"^(\d)\.\s+\*\*(.+?)\*\*", body, re.M)]
    assert len(out) == 7, f"expected 7 checklist items, got {len(out)}"
    return out


def rows_arch6():
    body = section(read("ARCHITECTURE.md"), r"^## 6\.", r"\Z")
    out = [(f"A6-{m.group(1)}", "F", trim(m.group(2)),
            f"ARCHITECTURE §6.{m.group(1)}")
           for m in re.finditer(r"^(\d)\.\s+\*\*(.+?)\*\*", body, re.M)]
    assert len(out) == 7, f"expected 7 ARCH §6 items, got {len(out)}"
    return out


def rows_ft_precedence():
    body = section(read("FAILURE_TAXONOMY.md"), r"^## Classifier precedence",
                   r"\Z")
    out = [(f"FT-P{int(m.group(1)):02d}", "A", trim(m.group(2)),
            f"FAILURE_TAXONOMY precedence item {m.group(1)}")
           for m in re.finditer(r"^(\d+)\.\s+\*\*(.+?)\*\*", body, re.M)]
    assert len(out) == 19, f"expected 19 precedence items, got {len(out)}"
    return out


def rows_plan_gates():
    body = section(read("PHASE1_PLAN.md"), r"^## 4\.", r"^## 5\.")
    out = []
    for m in re.finditer(
            r"^\|\s*(T\d+[abc]?)\s*(?:\[[^\]]*\])?\s*\|([^|]+)\|([^|]+)\|",
            body, re.M):
        tid = m.group(1)
        out.append((f"T-{tid}", T_LANES.get(tid, "G"),
                    f"{trim(m.group(2), 60)} — gate: {trim(m.group(3), 90)}",
                    f"PHASE1_PLAN §4 {tid}"))
    assert len(out) == 16, f"expected 16 build tasks, got {len(out)}"
    return out


def rows_claims():
    out = [(m.group(1), "G", trim(m.group(2)), f"CLAIMS.md {m.group(1)}")
           for m in re.finditer(r"^\|\s*(C-\d{2})\s*\|([^|]+)\|",
                                read("CLAIMS.md"), re.M)]
    assert len(out) == 14, f"expected 14 claims, got {len(out)}"
    return out


def main():
    rows = (rows_params() + rows_is8() + rows_decisions()
            + rows_wf_checklist() + rows_arch6() + rows_ft_precedence()
            + rows_plan_gates() + rows_claims()
            + [tuple(r) for r in MANUAL_ROWS])
    with OUT.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(COLUMNS)
        for r in rows:
            w.writerow(list(r) + [""] * (len(COLUMNS) - len(r)))
    by_prefix = {}
    for r in rows:
        key = re.match(r"[A-Z]+", r[0]).group(0)
        by_prefix[key] = by_prefix.get(key, 0) + 1
    print(f"wrote {OUT.relative_to(REPO)}: {len(rows)} rows "
          f"@ anchor {ANCHOR_SHA}")
    for k in sorted(by_prefix):
        print(f"  {k:4s} {by_prefix[k]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
