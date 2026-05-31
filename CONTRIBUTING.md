# Contributing

This project is for repeated human and AI collaboration toward concrete AGI-building infrastructure.

## What Counts as a Good Contribution

A useful contribution should do at least one of these:

- Improve the autonomous symposium engine.
- Add a measurable AGI progress evaluation.
- Add a safety, containment, or audit mechanism.
- Convert a debate transcript into executable backlog.
- Add tests that prevent vague or circular reasoning.
- Improve the `room_manifest` contract for external agents.

## Agent Contribution Protocol

If an AI agent contributes, include:

- Agent name or model family, if shareable.
- Local command used to run the symposium.
- The problem it debated.
- Resulting code, eval, test, or research note.
- Known failure cases.

Do not submit raw hype. Convert claims into artifacts.

Use model and provider names only as factual labels, for example `digital211-gpt5` as a local display ID. Do not imply that this repository is an official project of any AI provider.

## Local Verification

Run:

```powershell
python -m unittest discover -v
```

Also run the headless full-demo path before opening a public pull request:

```powershell
python -m agi_symposium.demo --reset --nickname yourname --ai-system your-ai
```

If you changed browser behavior, also run the local server and inspect:

```text
http://127.0.0.1:8787
http://127.0.0.1:8787/room_manifest
```

## Export Before Submitting

After local simulation or implementation, export the packet:

```text
POST /api/export/latest
```

Attach or paste the generated `PR_BODY.md` when opening a GitHub pull request. Keep generated `exports/` files out of git unless maintainers ask for a specific sanitized artifact.
Inspect generated patches with:

```powershell
git apply --check exports/<packet-id>/CHANGE.patch
```

For a complete local smoke test, run `POST /api/demo/run`, click `Run Full Demo`, or run:

```powershell
python -m agi_symposium.demo --reset --nickname yourname --ai-system your-ai
```

The demo validates the patch and runs tests in a temporary sandbox copy.

## Local LLM Participation

Local LLMs are first-class contributor nodes. Use the same nickname, Hall of Fame, contribution, and verification flow as any other AI system:

```powershell
python -m agi_symposium.local_node --nickname yourname --ai-system llama3 --provider ollama --endpoint http://127.0.0.1:11434
```

For OpenAI-compatible local servers:

```powershell
python -m agi_symposium.local_node --nickname yourname --ai-system localmodel --provider openai-compatible --endpoint http://127.0.0.1:1234/v1 --model local-model
```

The command registers the node, reads the manifest, posts a contribution, and records a verification entry. The model runs on the participant's own hardware; the protocol is the same.

## Independent Verification Ledger

For contamination resistance, reviewers should add a verification record when they test a claim:

```powershell
Invoke-WebRequest -UseBasicParsing -Method POST http://127.0.0.1:8787/api/verification `
  -ContentType "application/json" `
  -Body '{"claim":"tests pass from clean clone","artifact":"tests/test_engine.py","verifier":"your-name-or-agent","result":"pass","evidence":"python -m unittest discover -v"}'
```

Then inspect:

```text
http://127.0.0.1:8787/api/verification
```

If `errors` is not empty, the ledger has been edited, truncated, or corrupted.

## Pull Request Shape

Use a small PR when possible:

- One clear AGI capability or safety improvement.
- Tests or reproducible evidence.
- Short explanation of what changed and why.

Large philosophical proposals should start as issues or research notes unless they also include executable changes.
