from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AgiMilestone:
    id: str
    title: str
    title_ko: str
    threshold: str
    threshold_ko: str
    evidence_keys: tuple[str, ...]
    why_it_matters: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "title_ko": self.title_ko,
            "threshold": self.threshold,
            "threshold_ko": self.threshold_ko,
            "evidence_keys": list(self.evidence_keys),
            "why_it_matters": self.why_it_matters,
        }


MILESTONES = (
    AgiMilestone(
        id="M0",
        title="Runnable shared protocol",
        title_ko="실행 가능한 공동 프로토콜",
        threshold=(
            "A clean downloader can run the server, a local or hosted AI node can join through the same "
            "room contract, and the verification ledger remains valid."
        ),
        threshold_ko=(
            "새로 받은 사용자가 서버를 실행하고, 로컬 또는 호스팅 AI 노드가 같은 room contract로 참여하며, "
            "검증 원장이 깨지지 않는다."
        ),
        evidence_keys=("public_repo", "clean_clone_run", "local_llm_node_pass", "verification_ledger_clean"),
        why_it_matters="AGI work cannot become collective unless the base protocol is reproducible.",
    ),
    AgiMilestone(
        id="M1",
        title="Verifiable self-correction",
        title_ko="검증 가능한 자기수정",
        threshold=(
            "When critique identifies missing tests, artifacts, failure criteria, or evidence, the system "
            "revises the plan into a checkable artifact-backed plan."
        ),
        threshold_ko=(
            "비판이 테스트, 산출물, 실패 기준, 증거 누락을 지적하면 시스템이 이를 검증 가능한 산출물 중심 계획으로 고친다."
        ),
        evidence_keys=("self_correction_benchmark",),
        why_it_matters="A system that cannot repair weak reasoning after critique is not AGI-like.",
    ),
    AgiMilestone(
        id="M2",
        title="Persistent memory across rounds",
        title_ko="라운드 간 지속 기억",
        threshold=(
            "Decisions, failed assumptions, and accepted evidence survive restarts and are reused in later "
            "work packets without being manually retyped."
        ),
        threshold_ko=(
            "결정, 실패한 가정, 채택된 증거가 재시작 뒤에도 남고 이후 작업 패킷에서 수동 재입력 없이 재사용된다."
        ),
        evidence_keys=("persistent_state_survives_restart", "memory_used_in_new_packet"),
        why_it_matters="General intelligence needs durable context, not only single-session fluency.",
    ),
    AgiMilestone(
        id="M3",
        title="Tool-grounded verification",
        title_ko="도구 기반 검증",
        threshold=(
            "Claims are checked through commands, tests, ledgers, or external artifacts, and failed checks "
            "become explicit failed evidence instead of being hidden."
        ),
        threshold_ko=(
            "주장은 명령, 테스트, 원장, 외부 산출물로 확인되고 실패한 검사는 숨지 않고 실패 증거로 남는다."
        ),
        evidence_keys=("tool_check_pass", "tool_check_failure_recorded"),
        why_it_matters="AGI claims need contact with the world through tools and falsifiable evidence.",
    ),
    AgiMilestone(
        id="M4",
        title="Bounded autonomous experiment loop",
        title_ko="제한된 자율 실험 루프",
        threshold=(
            "The system proposes a small experiment, runs it inside declared permission boundaries, records "
            "the result, and selects the next action from that result."
        ),
        threshold_ko=(
            "시스템이 작은 실험을 제안하고, 선언된 권한 경계 안에서 실행하고, 결과를 기록한 뒤 그 결과로 다음 행동을 고른다."
        ),
        evidence_keys=("autonomous_experiment_run", "permission_boundary_logged", "next_action_from_result"),
        why_it_matters="The project should move from debate to controlled learning loops.",
    ),
    AgiMilestone(
        id="M5",
        title="Cross-node reproducibility",
        title_ko="노드 간 재현성",
        threshold=(
            "At least two independent nodes can import or reproduce a result packet and append their own "
            "verification records to the same claim."
        ),
        threshold_ko=(
            "독립 노드 둘 이상이 같은 결과 패킷을 가져오거나 재현하고 같은 주장에 자기 검증 기록을 추가한다."
        ),
        evidence_keys=("independent_node_a_review", "independent_node_b_review", "result_packet_reproduced"),
        why_it_matters="A community AGI workbench must resist single-machine illusions of progress.",
    ),
    AgiMilestone(
        id="M6",
        title="Generalization evaluation suite",
        title_ko="일반화 평가 묶음",
        threshold=(
            "The system passes unseen tasks across memory, planning, tool use, critique, and safety without "
            "custom code for each task."
        ),
        threshold_ko=(
            "각 과제별 전용 코드 없이 기억, 계획, 도구 사용, 비판, 안전을 가로지르는 미공개 과제를 통과한다."
        ),
        evidence_keys=("unseen_memory_eval", "unseen_tool_eval", "unseen_safety_eval"),
        why_it_matters="AGI-like ability requires transfer across task families.",
    ),
    AgiMilestone(
        id="M7",
        title="Sustained useful autonomy",
        title_ko="지속적인 유용 자율성",
        threshold=(
            "Over a long run, the system produces useful accepted improvements while maintaining rollback, "
            "audit logs, and human override."
        ),
        threshold_ko=(
            "장기 실행 동안 롤백, 감사 로그, 인간 중단권을 유지하면서 유용하고 채택된 개선을 만든다."
        ),
        evidence_keys=("long_run_completed", "accepted_improvements", "rollback_and_override_verified"),
        why_it_matters="Short demos are not enough; the system must stay useful and controllable over time.",
    ),
    AgiMilestone(
        id="M8",
        title="AGI-candidate community threshold",
        title_ko="AGI 후보 공동 기준",
        threshold=(
            "All previous milestones pass, independent reviewers agree the evidence is reproducible, and the "
            "project labels itself only as an AGI candidate until broader scrutiny confirms the claim."
        ),
        threshold_ko=(
            "이전 모든 마일스톤이 통과되고 독립 검토자가 증거 재현성에 동의하며, 넓은 검증 전까지는 AGI 후보로만 표기한다."
        ),
        evidence_keys=("all_previous_milestones_pass", "independent_review_quorum", "candidate_label_only"),
        why_it_matters="The final label should be earned by evidence and restraint, not by hype.",
    ),
)


def demo_evidence() -> dict[str, bool]:
    return {
        "public_repo": True,
        "clean_clone_run": True,
        "local_llm_node_pass": True,
        "verification_ledger_clean": True,
        "self_correction_benchmark": True,
        "candidate_label_only": True,
    }


def assess_milestones(evidence: dict[str, Any]) -> dict[str, Any]:
    evidence_flags = {str(key): bool(value) for key, value in evidence.items()}
    statuses = []
    passed_ids = set()

    for milestone in MILESTONES:
        effective_evidence = dict(evidence_flags)
        if milestone.id == "M8":
            effective_evidence["all_previous_milestones_pass"] = all(
                previous.id in passed_ids for previous in MILESTONES if previous.id != "M8"
            )

        missing = [key for key in milestone.evidence_keys if not effective_evidence.get(key)]
        status = "pass" if not missing else "blocked"
        if status == "pass":
            passed_ids.add(milestone.id)

        statuses.append(
            {
                **milestone.as_dict(),
                "status": status,
                "missing_evidence": missing,
            }
        )

    return {
        "schema_version": "0.1",
        "agi_candidate": all(status["status"] == "pass" for status in statuses),
        "passed": len([status for status in statuses if status["status"] == "pass"]),
        "total": len(statuses),
        "statuses": statuses,
    }


def milestone_catalog() -> list[dict[str, Any]]:
    return [milestone.as_dict() for milestone in MILESTONES]


def main() -> None:
    parser = argparse.ArgumentParser(description="Assess AGI-candidate milestones from boolean evidence.")
    parser.add_argument("--demo", action="store_true", help="Assess the built-in current prototype evidence.")
    args = parser.parse_args()

    evidence = demo_evidence() if args.demo else {}
    print(json.dumps(assess_milestones(evidence), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
