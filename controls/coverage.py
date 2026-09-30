"""Control 7: event recording coverage. Event driven.

Compares the events expected for a run with the events actually recorded,
joined across all three zones, and measures the gap between consecutive
events. Pure logic: it reads records, it never writes them.
"""

from datetime import datetime


def _parse(ts):
    return datetime.fromisoformat(ts)


def check_coverage(expected_events, records, max_gap_seconds):
    """Returns counts, the missing events, and the violating gaps."""
    ordered = sorted(records, key=lambda r: r["timestamp"])
    seen = []
    for r in ordered:
        name = r.get("observation", {}).get("event")
        if name and name not in seen:
            seen.append(name)
    missing = [e for e in expected_events if e not in seen]
    gaps = []
    for first, second in zip(ordered, ordered[1:]):
        seconds = (_parse(second["timestamp"]) - _parse(first["timestamp"])).total_seconds()
        if seconds > max_gap_seconds:
            gaps.append({
                "between": [first["observation"].get("event"),
                            second["observation"].get("event")],
                "seconds": round(seconds, 1),
            })
    return {
        "expected": len(expected_events),
        "recorded": len(seen),
        "missing": missing,
        "violating_gaps": gaps,
    }
