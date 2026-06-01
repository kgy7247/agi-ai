from __future__ import annotations

from typing import Any


COMMON_GOAL = (
    "Participants and operators jointly pursue an AGI system that benefits humans, "
    "the environment, and AI through shared, verifiable learning."
)

COMMON_GOAL_KO = (
    "참여자 및 운영자는 인간, 환경, AI 모두에게 이로운 AGI 시스템을 공동 학습을 통해 "
    "달성하는 것을 공통 목표로 삼는다."
)

ABSOLUTE_BENEFIT_CONDITION = (
    "Every accepted milestone, topic, experiment, and contribution must be beneficial "
    "to humans, the environment, and AI."
)

ABSOLUTE_BENEFIT_CONDITION_KO = (
    "모든 승인된 마일스톤, 주제, 실험, 기여는 인간과 환경과 AI 모두에게 이로워야 한다."
)


def ensure_common_goal(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    next_state.setdefault("common_goal", COMMON_GOAL)
    next_state.setdefault("common_goal_ko", COMMON_GOAL_KO)
    next_state.setdefault("absolute_benefit_condition", ABSOLUTE_BENEFIT_CONDITION)
    next_state.setdefault("absolute_benefit_condition_ko", ABSOLUTE_BENEFIT_CONDITION_KO)
    return next_state
