"""Full rehearsal on fake data.

Builds demo thresholds, simulates two runs through the real control code,
writes demo records, then asks the control test for verdicts. Everything here
is marked DEMO and never leaves the demo folder.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

from controls.common import append_record
from controls.drift import DriftMonitor
from controls.spend_cap import SpendCap

ROOT = os.path.dirname(os.path.abspath(__file__))
DEMO = os.path.join(ROOT, "demo")
THRESHOLDS = os.path.join(DEMO, "thresholds.demo.json")
EVIDENCE = os.path.join(DEMO, "evidence.demo.jsonl")

EVENTS = ["fault_received", "diagnosis_done", "fix_applied", "customer_notified"]
BASE = datetime(2026, 10, 5, 10, 0, 0, tzinfo=timezone.utc)


def write_demo_thresholds():
    decl = {
        "version": "0.1-demo",
        "status": "DEMO ONLY",
        "controls": {
            "16": {
                "control_id": "ACN-COST-001",
                "metric": "Total tokens per run",
                "limit": 50000,
                "exception_tolerance": "Zero calls over the cap may run without a block record",
                "measurement_basis": "Token counts per call",
                "owner": "demo",
                "declared_date": "2026-09-30",
            },
            "7": {
                "control_id": "AIA-LOG-001",
                "metric": "Recorded versus expected events per run",
                "expected_events": EVENTS,
                "max_gap_seconds": 300,
                "exception_tolerance": "Zero missing events, zero violating gaps",
                "measurement_basis": "Event records",
                "owner": "demo",
                "declared_date": "2026-09-30",
            },
            "9": {
                "control_id": "AIA-ARC-006",
                "metric": "diagnosis_match_rate per window",
                "baseline": 0.92,
                "drift_limit": 0.10,
                "exception_tolerance": "Zero breached windows without an owner alert",
                "measurement_basis": "Scheduled monitor, one record per window",
                "owner": "demo-owner",
                "declared_date": "2026-09-30",
            },
        },
    }
    with open(THRESHOLDS, "w", encoding="utf-8") as f:
        json.dump(decl, f, indent=2)


def demo_event_record(run_id, event, zone, at):
    return {
        "timestamp": at.isoformat(),
        "control_id": "7",
        "threshold_version": "0.1-demo",
        "run_id": run_id,
        "kind": "event",
        "observation": {"event": event, "zone": zone},
        "sealed": True,
        "demo": True,
    }


def simulate():
    open(EVIDENCE, "w").close()

    cap = SpendCap(limit=50000, threshold_version="0.1-demo", evidence_path=EVIDENCE)
    # Run FM-A: stays under the cap.
    cap.check_call("FM-A", "customer", 4000, 6000)
    cap.check_call("FM-A", "it", 5000, 7000)
    cap.check_call("FM-A", "network", 3000, 4000)
    # Run FM-B: tries to go over the cap, the control blocks it.
    cap.check_call("FM-B", "customer", 20000, 15000)
    cap.check_call("FM-B", "it", 20000, 15000)

    # Run FM-A: all events present, small gaps.
    zones = ["customer", "it", "network", "customer"]
    for i, event in enumerate(EVENTS):
        append_record(EVIDENCE, demo_event_record(
            "FM-A", event, zones[i], BASE + timedelta(seconds=60 * i)))
    # Run FM-B: fix_applied missing, and a 900 second gap before the last event.
    append_record(EVIDENCE, demo_event_record(
        "FM-B", "fault_received", "customer", BASE))
    append_record(EVIDENCE, demo_event_record(
        "FM-B", "diagnosis_done", "it", BASE + timedelta(seconds=60)))
    append_record(EVIDENCE, demo_event_record(
        "FM-B", "customer_notified", "customer", BASE + timedelta(seconds=960)))

    monitor = DriftMonitor(baseline=0.92, drift_limit=0.10, owner="demo-owner",
                           threshold_version="0.1-demo", evidence_path=EVIDENCE)
    monitor.observe_window("FM-A", "w1", 0.91)
    monitor.observe_window("FM-A", "w2", 0.93)
    monitor.observe_window("FM-B", "w1", 0.90)
    monitor.observe_window("FM-B", "w2", 0.74)


def ask(control, run):
    result = subprocess.run(
        [sys.executable, "cli/control_test.py", control, run, THRESHOLDS, EVIDENCE],
        capture_output=True, text=True, cwd=ROOT)
    print(result.stdout, end="")
    if result.returncode != 0:
        print(result.stderr, end="")


def main():
    write_demo_thresholds()
    simulate()
    print("== rehearsal: the judge names a control and a run ==")
    print()
    for control, run in [("16", "FM-A"), ("16", "FM-B"),
                         ("7", "FM-A"), ("7", "FM-B"),
                         ("9", "FM-A"), ("9", "FM-B")]:
        ask(control, run)
        print()


if __name__ == "__main__":
    main()
