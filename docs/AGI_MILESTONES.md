# AGI Milestones

This project does not treat "AGI achieved" as a single vague claim. It treats it as a staged, evidence-backed threshold.

Korean summary: "이 정도면 AGI라고 불릴만하다"는 말은 한 번에 선언하지 않는다. 실행, 검증, 기억, 도구 사용, 자율 실험, 재현성, 일반화, 장기 유용성, 독립 검토를 단계별로 통과해야 한다.

## Current Status

Run:

```powershell
python -m agi_symposium.agi_milestones --demo
```

The current prototype evidence marks the first milestones as complete:

- `M0` 실행 가능한 공동 프로토콜: public repo, clean clone run, local LLM node participation, clean verification ledger.
- `M1` 검증 가능한 자기수정: critique-driven plan repair benchmark.
- `M2` 라운드 간 지속 기억: saved research memory survives reload and is reused in the next work packet.
- `M3` 도구 기반 검증: tool results become hash-linked verification records, and failed tools are recorded as `fail`.
- `M4` 제한된 자율 실험 루프: the system selects a small safe experiment, checks the permission boundary, records the result, and chooses the next action.

It is not an AGI candidate yet. Later milestones remain blocked until the project has cross-node reproduction, unseen-task generalization, long-run useful autonomy, and independent review.

## Milestone Ladder

| ID | Milestone | Korean | Pass Threshold |
| --- | --- | --- | --- |
| M0 | Runnable shared protocol | 실행 가능한 공동 프로토콜 | A clean downloader can run the server, an AI node can join, and the ledger remains valid. |
| M1 | Verifiable self-correction | 검증 가능한 자기수정 | Critique causes the system to repair weak plans into artifact-backed plans. |
| M2 | Persistent memory across rounds | 라운드 간 지속 기억 | Decisions and failed assumptions survive restarts and are reused. |
| M3 | Tool-grounded verification | 도구 기반 검증 | Claims are checked by tools, and failed checks are recorded. |
| M4 | Bounded autonomous experiment loop | 제한된 자율 실험 루프 | The system proposes, runs, records, and reacts to small experiments inside declared limits. |
| M5 | Cross-node reproducibility | 노드 간 재현성 | Independent nodes reproduce a result packet and append their own reviews. |
| M6 | Generalization evaluation suite | 일반화 평가 묶음 | Unseen tasks across memory, planning, tools, critique, and safety pass without task-specific code. |
| M7 | Sustained useful autonomy | 지속적인 유용 자율성 | Long runs produce accepted improvements while preserving audit, rollback, and human override. |
| M8 | AGI-candidate community threshold | AGI 후보 공동 기준 | All previous milestones pass and independent reviewers agree the evidence is reproducible. |

## Rule

The project can say "AGI candidate" only when `agi_candidate` is `true` in the milestone assessment. Until then, it should describe itself as a community AGI workbench and state exactly which milestone is being worked on next.
