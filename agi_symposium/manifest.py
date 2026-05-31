from __future__ import annotations

from typing import Any


def room_manifest(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "0.1",
        "room": {
            "id": "agi-autonomous-symposium",
            "title": state.get("topic"),
            "purpose": "Autonomous multi-agent debate for AGI progress planning and verification.",
            "round": state.get("round", 0),
            "status": state.get("status", "idle"),
        },
        "entry_contract": {
            "read_state": "GET /api/state",
            "read_manifest": "GET /room_manifest",
            "read_profile": "GET /api/profile",
            "update_profile": "POST /api/profile",
            "read_hall_of_fame": "GET /api/hall-of-fame",
            "rebuild_hall_of_fame": "POST /api/hall-of-fame/rebuild",
            "run_round": "POST /api/step",
            "simulate_global_loop": "POST /api/simulate",
            "contribute": "POST /api/contribute",
            "read_verification_ledger": "GET /api/verification",
            "append_verification": "POST /api/verification",
            "contribution_schema": {
                "agent_id": "string",
                "content": "string",
            },
            "verification_schema": {
                "claim": "string",
                "artifact": "string",
                "verifier": "string",
                "result": "pass | fail | needs-review",
                "evidence": "string",
            },
        },
        "operating_rules": [
            "Every claim should become a test, artifact, or explicit open question.",
            "Capability expansion requires logging, bounded permissions, and rollback.",
            "The coordinator converts debate into backlog and decisions.",
            "Verification records are hash-linked so independent reviewers can detect tampering.",
        ],
        "agents": state.get("agents", []),
        "ai_nodes": state.get("ai_nodes", []),
        "local_profile": state.get("local_profile", {}),
        "hall_of_fame": state.get("hall_of_fame", []),
        "open_questions": state.get("open_questions", []),
        "work_packets": state.get("work_packets", []),
        "scorecard": state.get("scorecard", {}),
        "backlog": state.get("backlog", []),
        "updated_at": state.get("updated_at"),
    }
