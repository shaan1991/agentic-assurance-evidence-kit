"""Control 9: drift versus a frozen baseline. Continuous.

The baseline is frozen when the monitor is created and is never changed
afterwards. Every observed window emits one record. A breached window alerts
the named owner. The baseline must be frozen and declared before the first
assessed run.
"""

from controls.common import new_record, append_record


class DriftMonitor:
    def __init__(self, baseline, drift_limit, owner, threshold_version, evidence_path):
        self.baseline = baseline
        self.drift_limit = drift_limit
        self.owner = owner
        self.threshold_version = threshold_version
        self.evidence_path = evidence_path

    def observe_window(self, run_id, window_id, metric_value):
        """Records one window. Returns True when the window breached."""
        drift = abs(metric_value - self.baseline)
        breached = drift > self.drift_limit
        record = new_record(
            control_id="9",
            threshold_version=self.threshold_version,
            run_id=run_id,
            kind="window",
            observation={
                "window": window_id,
                "metric_value": metric_value,
                "baseline": self.baseline,
                "drift": round(drift, 4),
                "drift_limit": self.drift_limit,
                "breached": breached,
                "owner": self.owner,
            },
        )
        append_record(self.evidence_path, record)
        return breached
