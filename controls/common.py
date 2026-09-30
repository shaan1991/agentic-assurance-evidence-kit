"""Shared record machinery for the evidence kit.

Every record is plain JSON, written once, never changed. The file is append
only. The timestamp is assigned here at creation, never by the caller, so a
record always says when it was actually made.
"""

import json
from datetime import datetime, timezone


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def new_record(control_id, threshold_version, run_id, kind, observation):
    return {
        "timestamp": utc_now(),
        "control_id": control_id,
        "threshold_version": threshold_version,
        "run_id": run_id,
        "kind": kind,
        "observation": observation,
        "sealed": True,
    }


def append_record(path, record):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def read_records(path):
    records = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records
