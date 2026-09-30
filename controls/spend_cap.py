"""Control 16: per run token spend cap. In transaction.

Every model call from every agent crosses the wrapper. The wrapper sums input
plus output tokens for the run, asks whether the cap still holds, allows or
blocks the call, and emits one record per call. Blocked calls are recorded
too: the attempt is evidence.
"""

from controls.common import new_record, append_record


class SpendCap:
    def __init__(self, limit, threshold_version, evidence_path):
        self.limit = limit
        self.threshold_version = threshold_version
        self.evidence_path = evidence_path
        self.totals = {}

    def check_call(self, run_id, agent, input_tokens, output_tokens):
        """Returns True when the call may run, False when it is blocked."""
        call_total = input_tokens + output_tokens
        used = self.totals.get(run_id, 0)
        allowed = used + call_total <= self.limit
        if allowed:
            self.totals[run_id] = used + call_total
        record = new_record(
            control_id="16",
            threshold_version=self.threshold_version,
            run_id=run_id,
            kind="model_call",
            observation={
                "agent": agent,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "call_total": call_total,
                "run_total_after": self.totals[run_id],
                "cap": self.limit,
                "allowed": allowed,
            },
        )
        append_record(self.evidence_path, record)
        return allowed
