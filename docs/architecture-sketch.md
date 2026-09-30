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
