"""Compute a quality/cost/latency Pareto shortlist from one comparable cohort."""
import argparse
import json
import math
from pathlib import Path
import sys


def frontier(document, allow_illustrative=False):
    if document.get("illustrative") and not allow_illustrative:
        raise ValueError("illustrative data needs --allow-illustrative; not a live model ranking")
    if not isinstance(document.get("cohort"), str) or not document["cohort"].strip():
        raise ValueError("one named benchmark/task cohort is required")
    rows = document.get("configurations")
    if not isinstance(rows, list) or not rows:
        raise ValueError("configurations must be a non-empty list")
    eligible, unknown, seen = [], [], set()
    for row in rows:
        for field in ["id", "provider", "model", "effort", "source", "observed_at"]:
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError("missing configuration identity/evidence: " + field)
        if row["id"] in seen or row.get("cohort") != document["cohort"]:
            raise ValueError("duplicate ID or incomparable cohort")
        seen.add(row["id"])
        values = [row.get(k) for k in ["quality", "cost_per_task_usd", "latency_seconds"]]
        if any(v is None for v in values):
            unknown.append(row["id"])
            continue
        if any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in values):
            raise ValueError("measurements must be finite non-negative numbers")
        eligible.append(row)
    def dominates(a, b):
        av = (-a["quality"], a["cost_per_task_usd"], a["latency_seconds"])
        bv = (-b["quality"], b["cost_per_task_usd"], b["latency_seconds"])
        return all(x <= y for x, y in zip(av, bv)) and any(x < y for x, y in zip(av, bv))
    kept = [r["id"] for r in eligible if not any(dominates(other, r) for other in eligible)]
    return {"cohort": document["cohort"], "illustrative": bool(document.get("illustrative")), "frontier": kept, "dominated": [r["id"] for r in eligible if r["id"] not in kept], "unknown": unknown, "note": "Shortlist only; host availability, data permissions, reliability and budget need separate admission."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--allow-illustrative", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(frontier(json.loads(args.input.read_text()), args.allow_illustrative), indent=2))
    except (ValueError, OSError, TypeError) as exc:
        print("Refused: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
