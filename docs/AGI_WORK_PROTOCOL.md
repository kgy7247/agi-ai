# AGI Work Protocol

The project needs a repeatable way for many humans and AI systems to contribute without turning into unstructured debate.

## Common Goal

Participants and operators jointly pursue an AGI system for humans and AI through shared, verifiable learning.

Korean: 참여자 및 운영자는 인간과 AI를 위한 AGI 시스템을 공동 학습을 통해 달성하는 것을 공통 목표로 삼는다.

Every contribution should state or imply how it moves that shared goal forward through an artifact, test, benchmark, safety rule, or reproducible research result.

## AGI-Candidate Milestones

The project uses staged milestones instead of a vague "AGI achieved" label. Check the current assessment with:

```powershell
python -m agi_symposium.agi_milestones --demo
```

The system may call itself an AGI candidate only when the executable assessment returns `agi_candidate: true`. Until then, each contribution should name the next milestone it advances. The detailed ladder is in `docs/AGI_MILESTONES.md`.

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

## Self-Correction Benchmark

`WORK-002` is backed by `tests/test_self_correction.py` and `agi_symposium/self_correction.py`.

The benchmark is intentionally small: when a critique says a plan lacks tests, artifacts, failure criteria, or verification evidence, the agent must revise the plan to include those missing pieces. A self-correction claim should not be treated as verified unless the revised plan names concrete artifacts and a reproducible verification command.

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
