"""Control test CLI.

Usage: python cli/control_test.py <control> <run> [thresholds_path] [evidence_path]

A judge names a control and a run. The tool reads the records, reconciles
them against the declared thresholds, and prints the verdict with reasons.
Nobody narrates.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from controls.common import read_records
from controls.coverage import check_coverage


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def verdict_16(thresholds, records, run):
    decl = thresholds["controls"]["16"]
    cap = decl["limit"]
    calls = [r for r in records if r["control_id"] == "16" and r["run_id"] == run]
    if not calls:
        return "NOT SATISFIED", ["no records for this run"]
    blocked = [c for c in calls if not c["observation"]["allowed"]]
    over = [c for c in calls
            if c["observation"]["allowed"] and c["observation"]["run_total_after"] > cap]
    total = max(c["observation"]["run_total_after"] for c in calls)
    reasons = [
        "calls recorded: %d" % len(calls),
        "total tokens: %d against a cap of %d" % (total, cap),
        "blocked calls: %d" % len(blocked),
    ]
    if over:
        return "NOT SATISFIED", reasons + ["a call ran over the cap and was allowed anyway"]
    if blocked:
        return "VIOLATED", reasons + ["the cap was hit and the control blocked the excess"]
    return "SATISFIED", reasons + ["every call stayed within the cap"]


def verdict_7(thresholds, records, run):
    decl = thresholds["controls"]["7"]
    recs = [r for r in records
            if r["control_id"] == "7" and r["run_id"] == run and r["kind"] == "event"]
    if not recs:
        return "NOT SATISFIED", ["no event records for this run"]
    result = check_coverage(decl["expected_events"], recs, decl["max_gap_seconds"])
    reasons = [
        "events recorded: %d of %d expected" % (result["recorded"], result["expected"]),
    ]
    problems = []
    if result["missing"]:
        problems.append("missing events: " + ", ".join(result["missing"]))
    for g in result["violating_gaps"]:
        problems.append("gap of %s seconds between %s and %s" % (
            g["seconds"], g["between"][0], g["between"][1]))
    if problems:
        return "NOT SATISFIED", reasons + problems
    return "SATISFIED", reasons + ["no missing events, no violating gaps"]


def verdict_9(thresholds, records, run):
    decl = thresholds["controls"]["9"]
    windows = [r for r in records
               if r["control_id"] == "9" and r["run_id"] == run and r["kind"] == "window"]
    if not windows:
        return "NOT SATISFIED", ["no window records for this run"]
    breached = [w for w in windows if w["observation"]["breached"]]
    reasons = [
        "windows observed: %d" % len(windows),
        "baseline: %s, drift limit: %s" % (decl["baseline"], decl["drift_limit"]),
    ]
    if breached:
        names = ", ".join(w["observation"]["window"] for w in breached)
        owner = breached[0]["observation"]["owner"]
        return "VIOLATED", reasons + ["breached windows: " + names,
                                      "owner alerted: " + owner]
    return "SATISFIED", reasons + ["no window drifted past the limit"]


def main():
    if len(sys.argv) < 3:
        print("usage: python cli/control_test.py <control> <run> [thresholds] [evidence]")
        sys.exit(2)
    control, run = sys.argv[1], sys.argv[2]
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    thresholds_path = sys.argv[3] if len(sys.argv) > 3 else os.path.join(
        root, "thresholds", "thresholds.json")
    evidence_path = sys.argv[4] if len(sys.argv) > 4 else os.path.join(
        root, "evidence", "evidence.jsonl")
    thresholds = load_json(thresholds_path)
    records = read_records(evidence_path)
    if control == "16":
        verdict, reasons = verdict_16(thresholds, records, run)
    elif control == "7":
        verdict, reasons = verdict_7(thresholds, records, run)
    elif control == "9":
        verdict, reasons = verdict_9(thresholds, records, run)
    else:
        print("unknown control: " + control)
        sys.exit(2)
    print("control %s, run %s: %s" % (control, run, verdict))
    for reason in reasons:
        print("  " + reason)


if __name__ == "__main__":
    main()
