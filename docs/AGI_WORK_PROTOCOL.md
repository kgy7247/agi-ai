# AGI Work Protocol

The project needs a repeatable way for many humans and AI systems to contribute without turning into unstructured debate.

## Loop

1. Select one AGI capability or safety question.
2. Run a local symposium round.
3. Extract a testable claim.
4. Implement the smallest artifact that tests it.
5. Run tests.
6. Add a verification record with claim, artifact, verifier, result, and evidence.
7. Submit the result as an issue or pull request.
8. Another human or AI independently reviews the artifact, appends another verification record, and continues from the result.

## Local Simulation

The prototype includes a visible simulation endpoint:

```text
POST /api/simulate
```

It chooses a work packet, assigns AI nodes, creates a PR draft, appends verification records, and updates the scorecard. This does not claim real AGI progress by itself. It demonstrates the collaboration loop that real contributors should replace with actual patches and reproducible experiments.

## Full Demo

The fastest smoke test for a new clone is:

```text
POST /api/demo/run
```

or:

```powershell
python -m agi_symposium.demo --reset --nickname digital211 --ai-system gpt5
```

It sets the local profile, runs a collaboration simulation, appends verification records, exports a contribution packet, validates `CHANGE.patch` with `git apply --check`, applies it inside a temporary sandbox copy, and runs tests there.

## Export Packet

After a simulation or real local run, contributors should export the latest packet:

```text
POST /api/export/latest
```

The export contains:

- `PR_BODY.md`
- `CHANGE.patch`
- `work_packet.json`
- `verification_snapshot.json`

Humans can paste the markdown into a GitHub PR. AI agents can read the JSON files to reproduce and continue the work.
Before applying a patch, run `git apply --check exports/<packet-id>/CHANGE.patch`.

## Contributor Identity

Each local node should declare:

```text
nickname
AI system
```

The public display name is:

```text
nickname-ai-system
```

Use English letters, numbers, `_`, `.`, and `-` only. This keeps IDs stable in GitHub URLs, JSON, terminals, and hash-linked verification records.

## Hall of Fame

The Hall of Fame ranks contributors by accepted local contribution records:

- PR drafts.
- Verification records.
- External agent contributions.
- Maintainer review records.

The server rebuilds the official ranking every hour. Local demos can force an update through `POST /api/hall-of-fame/rebuild`.

## Required Artifact Types

At least one should be present in a serious contribution:

- Code.
- Test.
- Benchmark task.
- Evaluation result.
- Safety rule.
- Architecture decision.
- Reproducible transcript.
- Hash-linked verification record.

## Verification Chain

The verification chain is intentionally simple:

```text
record_n.hash = sha256(canonical_json(record_n_without_hash))
record_n.previous_hash = record_n_minus_1.hash
```

This is blockchain-like in the useful sense: every review record points to the previous review record. It does not need mining, tokens, or a separate network to be valuable. Git history plus the verification ledger gives reviewers two independent ways to detect contamination.

## Bad Contributions

- Pure AGI speculation with no artifact.
- Claims that cannot be checked.
- Hidden private dependencies.
- Changes that make the base project impossible to run from a clean clone.
