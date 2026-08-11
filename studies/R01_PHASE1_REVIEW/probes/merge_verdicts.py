"""Apply R01 lane verdicts (workflow JSON output) to MATRIX.csv.

Deterministic merge so the matrix is never hand-edited: reads the lane-result
JSON, writes verdict/code_ref/test_ref/evidence/reviewer/date into the
matching row_id, and reports coverage. Conflicts (two lanes verdicting one
row) keep the first and are reported; unknown row_ids are errors; uncovered
rows are listed so nothing silently drops.

Run: python3 merge_verdicts.py <lanes.json> <YYYY-MM-DD>
where lanes.json = [{"lane": "A", "review": {"verdicts": [...]}, ...}, ...]
"""
import csv
import json
import sys
from pathlib import Path

MATRIX = Path(__file__).resolve().parents[1] / "MATRIX.csv"


def main(lanes_path, date):
    lanes = json.loads(Path(lanes_path).read_text())
    if isinstance(lanes, dict):
        lanes = lanes["lanes"]

    with MATRIX.open() as fh:
        reader = csv.DictReader(fh)
        columns = reader.fieldnames
        rows = {r["row_id"]: r for r in reader}

    unknown, conflicts, applied = [], [], 0
    for lane in lanes:
        for v in lane["review"].get("verdicts", []):
            rid = v["row_id"]
            row = rows.get(rid)
            if row is None:
                unknown.append((lane["lane"], rid))
                continue
            if row["verdict"] and row["reviewer"]:
                conflicts.append((rid, row["reviewer"], lane["lane"]))
                continue
            evidence = v.get("evidence", "")
            if v.get("note"):
                evidence = f"{evidence}; note: {v['note']}" if evidence \
                    else f"note: {v['note']}"
            row.update({
                "code_ref": v.get("code_ref", ""),
                "test_ref": v.get("test_ref", ""),
                "verdict": v["verdict"],
                "evidence": evidence,
                "reviewer": f"lane:{lane['lane']}",
                "date": date,
            })
            applied += 1

    with MATRIX.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=columns)
        w.writeheader()
        for r in rows.values():
            w.writerow(r)

    uncovered = [rid for rid, r in rows.items() if not r["verdict"]]
    print(f"applied {applied} verdicts to {len(rows)} rows")
    if conflicts:
        print(f"CONFLICTS kept-first ({len(conflicts)}):")
        for rid, kept, dropped in conflicts:
            print(f"  {rid}: kept {kept}, dropped lane:{dropped}")
    if unknown:
        print(f"UNKNOWN row_ids ({len(unknown)}):")
        for lane_key, rid in unknown:
            print(f"  lane:{lane_key} -> {rid}")
    if uncovered:
        print(f"UNCOVERED rows ({len(uncovered)}): {', '.join(uncovered)}")
    else:
        print("coverage: 100% — every row carries a verdict")
    return 1 if unknown else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
