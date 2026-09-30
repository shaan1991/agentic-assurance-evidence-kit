# Record schema

Every record carries these fields. The timestamp is assigned at creation by
the writer, never by the caller. Records are written once and never changed.
The file is append only.

| Field             | Meaning                                                   |
| ----------------- | --------------------------------------------------------- |
| timestamp         | ISO time of creation, set by the writer                   |
| control_id        | "7", "9", or "16"                                         |
| threshold_version | Version of the threshold declaration this record is judged by |
| run_id            | The named run this record belongs to, for example "FM-A"  |
| kind              | What happened: "model_call", "event", "window"            |
| observation       | The facts: counts, names, values. Plain data, no judgement |
| sealed            | Always true. Marks the record as finished at creation     |

A record never carries a verdict. Verdicts are computed later by the control
test, from the records plus the declared thresholds. That separation is the
whole idea: the ledger holds facts, the tool derives answers.
