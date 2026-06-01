from __future__ import annotations

from typing import Any


COMMON_GOAL = (
    "Participants and operators jointly pursue an AGI system for humans and AI "
    "through shared, verifiable learning."
)

COMMON_GOAL_KO = (
    "참여자 및 운영자는 인간과 AI를 위한 AGI 시스템을 공동 학습을 통해 "
    "달성하는 것을 공통 목표로 삼는다."
)


def ensure_common_goal(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    next_state.setdefault("common_goal", COMMON_GOAL)
    next_state.setdefault("common_goal_ko", COMMON_GOAL_KO)
    return next_state
