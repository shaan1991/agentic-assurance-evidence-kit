# Agentic Assurance Evidence Kit

Scaffold for the TM Forum "Agentic Assurance: The Quest for Proof" hackathon.
It holds the control machinery both judges and auditors care about: declared
thresholds, bound records, and a query tool that answers from the records.

## The one rule

Bring the tools, not the evidence. Everything in this repo is scaffolding.
Threshold values, dated declarations, assessed runs, and the evidence file
are created at the event, on the real platform. A threshold chosen after
seeing the result is a description, not a test.

## Layout

- `thresholds/thresholds.template.json` — the declaration template. Copy it to
  `thresholds.json`, fill in real values after observing the platform, and
  date it before any assessed run.
- `records/schema.md` and `records/example.json` — what every record carries.
- `evidence/` — where the evidence file lives at the event. JSONL, append only.
- `controls/common.py` — record creation and the append only writer.
- `controls/spend_cap.py` — control 16: the per run token spend cap wrapper.
- `controls/coverage.py` — control 7: event coverage and gap measurement.
- `controls/drift.py` — control 9: drift versus a frozen baseline.
- `cli/control_test.py` — the query tool. A judge names a control and a run,
  the tool prints the verdict with reasons. Nobody narrates.
- `demo.py` — a full rehearsal on fake data: two runs, then the verdicts.
- `docs/` — the architecture sketch and the judgement day checklist.

## Quickstart

Run the rehearsal:

    python demo.py

Ask the tool about a control and a run:

    python cli/control_test.py 16 FM-A demo/thresholds.demo.json demo/evidence.demo.jsonl
    python cli/control_test.py 7 FM-B demo/thresholds.demo.json demo/evidence.demo.jsonl

## What gets filled in at the event

1. Copy `thresholds/thresholds.template.json` to `thresholds/thresholds.json`,
   set real limits after observing the platform, and date the declarations.
2. Freeze control 9's baseline before the first assessed run.
3. Port the wrappers to the real model gateway and event stream.
4. Produce the satisfied and violated runs. Keep every record.
5. Record the gaps honestly. The gap list is scored.

## Event facts, confirmed in the Sep 30 immersion webinar

- Prebuilt code and tools are explicitly allowed. The organisers said you can
  prepare and use your own code. This repo is the prebuilt toolkit.
- NVIDIA Nemotron models are required. A solution is only valid if the agents
  use Nemotron, served on AWS Bedrock. The four flavours: Nano 30B
  (efficient, medium tasks), Omni (multimodal), Super 120B (better
  reasoning), Ultra (frontier reasoning, complex orchestration). At the
  event, the wrappers get ported to call Nemotron through the event's Agent
  Gateway. Nemotron may also be used for adversarial testing of the controls.
- The ServiceNow AI Control Tower to AWS integration is mandatory and its
  use is part of the judging criteria. The event provides a guided flow in
  Workshop Studio: in AICT, open the integration tab, use the default Amazon
  connector, and fill in the access key ID, secret access key, management
  account ID, SDC assume role, and CloudWatch workgroup. Name connectors and
  agents with the team name. AICT is shared by all teams, not multi tenant.
- The judges speak four component names. This is how they map to the kit:
  the control register is the threshold declaration document; the evaluator
  is the control logic invoked at the enforcement point; the evidence ledger
  is the records plus the JSONL evidence file, which never interprets; the
  query tool is `cli/control_test.py`.
