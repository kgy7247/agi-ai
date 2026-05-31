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

## Local Verification

Run:

```powershell
python -m unittest discover -v
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

For a complete local smoke test, run `POST /api/demo/run` or click `Run Full Demo` in the browser UI. The demo validates the patch and runs tests in a temporary sandbox copy.

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
