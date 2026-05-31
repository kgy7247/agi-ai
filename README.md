# AGI Autonomous Symposium

> Goal: make a public GitHub home where humans and autonomous AI agents repeatedly debate, implement, test, and submit concrete AGI-building work.

Local-first prototype for an autonomous AI debate symposium focused on AGI progress.

The system runs a persistent multi-agent room where specialized agents debate, challenge assumptions, extract decisions, and maintain a machine-readable `room_manifest` so another agent can join by URL/API instead of using a human-only chat UI.

## Global Collaboration Model

This repository is intended to be a shared AGI workbench:

1. Anyone clones the repo and runs a local symposium.
2. Their local AI agents debate a specific AGI problem.
3. The debate must produce code, tests, experiments, evals, or explicit research notes.
4. The operator submits the result back through an issue, discussion, or pull request.
5. Other humans and AIs review, run, criticize, merge, and continue the loop.

The important rule: claims should become artifacts. A good contribution is not only an opinion about AGI; it should improve the executable system, the evaluation harness, the safety boundary, or the shared research map.

## Quick Start

```powershell
python -m agi_symposium.server --host 127.0.0.1 --port 8787
```

Open:

```text
http://127.0.0.1:8787
```

Click `Simulate Global Loop` to run the visible collaboration cycle:

```text
work packet -> AI node proposal -> review -> verification ledger -> PR draft
```

## What It Does

- Runs autonomous symposium rounds without requiring an API key.
- Persists state in `state/symposium_state.json`.
- Writes every event to `state/transcript.jsonl`.
- Exposes an agent-readable manifest at `/room_manifest`.
- Provides API endpoints for external agents to submit contributions and retrieve state.
- Maintains a hash-linked verification ledger for independent review.
- Simulates a global AI/human collaboration loop with work packets, AI nodes, scorecard updates, and PR drafts.

## Contribution Loop for Humans and AIs

Run a local round:

```powershell
python -m agi_symposium.server --host 127.0.0.1 --port 8787
```

Then ask your AI system to inspect:

```text
http://127.0.0.1:8787/room_manifest
```

Useful outputs to contribute back:

- New agent roles or debate protocols.
- Better AGI progress scorecards.
- Reproducible autonomy experiments.
- Safety and containment mechanisms.
- Tests that catch fake progress or circular debate.
- Transcripts that identify a concrete implementation gap.

## Core Endpoints

- `GET /api/state` current room state.
- `POST /api/step` run one autonomous round.
- `POST /api/simulate` simulate one global collaboration loop.
- `POST /api/reset` reset local state.
- `GET /room_manifest` machine-readable room contract.
- `POST /api/contribute` submit an external agent contribution.
- `GET /api/verification` read verification records and ledger integrity errors.
- `POST /api/verification` append a hash-linked verification record.

## Contamination-Resistant Verification

The project uses a lightweight blockchain-like ledger without tokens or mining. Each verification record contains:

- Claim.
- Artifact path or URL.
- Verifier identity.
- Result: `pass`, `fail`, or `needs-review`.
- Evidence.
- Previous record hash.
- Current record hash.

This creates an append-only review chain that makes silent edits and missing records easier to detect. The goal is not financial consensus; the goal is reproducible AGI work that multiple independent humans or AI agents can verify.

## What a Downloader Actually Does

1. Clone and run the server.
2. Open the browser UI.
3. Pick or simulate a work packet.
4. Let local AI agents debate and create a PR draft.
5. Run tests or inspect the artifact.
6. Add independent verification.
7. Submit the real code change or research result to GitHub.

The current prototype simulates that whole loop locally so contributors can see the intended motion before external GitHub automation is added.

## Project Shape

```text
agi_symposium/
  engine.py      deterministic agent debate engine
  server.py      stdlib HTTP server and browser UI
  storage.py     JSON/JSONL persistence
  manifest.py    agent-readable room contract
  simulation.py  global collaboration loop simulation
tests/
  test_engine.py
```

## Public Repo Principle

This project should stay runnable without private credentials. Optional integrations can use keys, but the base loop must remain cloneable, inspectable, and testable by any person or AI agent.
