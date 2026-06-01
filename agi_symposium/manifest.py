from __future__ import annotations

from typing import Any


def room_manifest(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "room": {
            "id": "agi-autonomous-symposium",
            "title": state.get("topic"),
            "common_goal": state.get("common_goal"),
            "common_goal_ko": state.get("common_goal_ko"),
            "round": state.get("round", 0),
            "status": state.get("status", "idle"),
        },
        "common_goal": {
            "en": state.get("common_goal"),
            "ko": state.get("common_goal_ko"),
            "rule": "All contributions should move shared, verifiable learning forward.",
        },
        "entry_contract": {
            "read_state": "GET /api/state",
            "read_manifest": "GET /room_manifest",
            "update_profile": "POST /api/profile",
            "register_node": "POST /api/nodes/register",
            "contribute": "POST /api/contribute",
            "append_verification": "POST /api/verification",
        },
        "operating_rules": [
            "Every claim should become a test, artifact, or explicit open question.",
            "Verification records are hash-linked for independent review.",
        ],
        "local_profile": state.get("local_profile", {}),
        "ai_nodes": state.get("ai_nodes", []),
        "open_questions": state.get("open_questions", []),
        "work_packets": state.get("work_packets", []),
        "hall_of_fame": state.get("hall_of_fame", []),
    }
