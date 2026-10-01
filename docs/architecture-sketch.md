# Architecture sketch (draft)

One page, refined at the event.

Three agents (Customer, IT, Network) resolve a telco network fault. Every
model call from every agent crosses one shared gateway. The controls sit at
that gateway and on the event stream, never inside the agents, so the agents
stay untouched.

    Agents: Customer, IT, Network
      every model call goes through
    Shared model gateway, wrapped by control 16
      one record per call, bound to control plus threshold version plus run
    Event stream across all three zones, watched by control 7
      expected versus recorded, gaps measured between consecutive events
    Scheduled monitor, control 9
      one live measure per window against the frozen baseline,
      owner alerted on breach
    Evidence store: one JSONL file, append only
      every record carries control, threshold version, run, timestamp
    Control test CLI
      a judge names a control and a run, the tool prints the verdict

Trust model: the ledger is plain JSONL anyone can read. Its trust does not
depend on the tool that wrote it. No signing, no hashing, no Merkle trees.
Gaps are recorded, never silent.

Vocabulary the judges use, mapped to this kit:

    Control register   thresholds/thresholds.template.json
                       the declaration document, dated before any assessed run
    Evaluator          controls/spend_cap.py, coverage.py, drift.py
                       invoked at the enforcement point, asks allowed or not
    Evidence ledger    records/ plus evidence/
                       takes records, chains them, never interprets
    Query tool         cli/control_test.py
                       a judge names a control and a run, the tool answers

Enforcement points worth covering beyond the gateway: tool calls, the human
approval queue, and data access. The architecture should work if it is moved
off the gateway, not only in the request path.
