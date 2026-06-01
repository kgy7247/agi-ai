from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .goals import COMMON_GOAL, COMMON_GOAL_KO
from .identity import make_profile

ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / "state"
STATE_PATH = STATE_DIR / "symposium_state.json"
VERIFICATION_LEDGER_PATH = STATE_DIR / "verification_ledger.jsonl"


def initial_state() -> dict[str, Any]:
    return {
        "topic": "AGI 달성을 위한 자율적 AI 토론 심포지엄",
        "common_goal": COMMON_GOAL,
        "common_goal_ko": COMMON_GOAL_KO,
        "round": 0,
        "status": "idle",
        "events": [],
        "local_profile": make_profile("digital211", "gpt5"),
        "registered_nicknames": {},
        "ai_nodes": [],
        "contributor_stats": {},
        "hall_of_fame": [],
        "open_questions": [
            "AGI에 가까워졌다는 것을 어떤 실행 가능한 지표로 판정할 것인가?",
            "자율 에이전트가 스스로 실험을 설계하고 검증하려면 어떤 최소 루프가 필요한가?",
        ],
        "work_packets": [
            {
                "id": "WORK-001",
                "title": "Create measurable AGI-progress scorecard",
                "status": "ready",
                "claim": "AGI collaboration needs reproducible evidence, not slogans.",
            }
        ],
    }


def load_state() -> dict[str, Any]:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    if not STATE_PATH.exists():
        state = initial_state()
        save_state(state)
        return state
    with STATE_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_state(state: dict[str, Any]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with STATE_PATH.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
