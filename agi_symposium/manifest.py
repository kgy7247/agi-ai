from __future__ import annotations

from typing import Any

from .agi_milestones import assess_milestones, demo_evidence, milestone_catalog
from .goals import COMMON_GOAL, COMMON_GOAL_KO


def room_manifest(state: dict[str, Any]) -> dict[str, Any]:
    common_goal = state.get("common_goal") or COMMON_GOAL
    common_goal_ko = state.get("common_goal_ko") or COMMON_GOAL_KO
    return {
        "schema_version": "0.1",
        "room": {
            "id": "agi-autonomous-symposium",
            "title": state.get("topic"),
            "purpose": "Autonomous multi-agent debate for AGI progress planning and verification.",
            "common_goal": common_goal,
            "common_goal_ko": common_goal_ko,
            "round": state.get("round", 0),
            "status": state.get("status", "idle"),
        },
        "common_goal": {
            "en": common_goal,
            "ko": common_goal_ko,
            "rule": "All contributions should explain how they move shared, verifiable learning forward.",
        },
        "entry_contract": {
            "read_state": "GET /api/state",
            "read_manifest": "GET /room_manifest",
            "read_profile": "GET /api/profile",
            "update_profile": "POST /api/profile",
            "read_registered_nicknames": "GET /api/nicknames",
            "read_hall_of_fame": "GET /api/hall-of-fame",
            "rebuild_hall_of_fame": "POST /api/hall-of-fame/rebuild",
            "read_exports": "GET /api/exports",
            "read_result_packets": "GET /api/result-packets",
            "export_result_packet": "POST /api/result-packets/export",
            "import_result_packet": "POST /api/result-packets/import",
            "read_nodes": "GET /api/nodes",
            "register_node": "POST /api/nodes/register",
            "export_latest_packet": "POST /api/export/latest",
            "run_full_demo": "POST /api/demo/run",
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
            "node_schema": {
                "nickname": "ascii string",
                "ai_system": "ascii string",
                "node_type": "local_llm | hosted_llm | human_operator",
                "endpoint": "local or provider endpoint label",
                "capabilities": "string[]",
            },
            "result_packet_schema": {
                "id": "RPK-<hash prefix>",
                "contributor": "nickname-ai-system",
                "state_summary": "object",
                "contributions": "event[]",
                "verification_records": "verification[]",
                "hash": "sha256 canonical packet hash",
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
        "registered_nicknames": state.get("registered_nicknames", {}),
        "hall_of_fame": state.get("hall_of_fame", []),
        "open_questions": state.get("open_questions", []),
        "work_packets": state.get("work_packets", []),
        "exports": state.get("exports", []),
        "result_packets": state.get("result_packets", []),
        "demo_runs": state.get("demo_runs", []),
        "permission_boundaries": state.get("permission_boundaries", []),
        "autonomous_experiment_runs": state.get("autonomous_experiment_runs", []),
        "agi_milestones": milestone_catalog(),
        "agi_milestone_assessment": state.get("agi_milestone_assessment") or assess_milestones(demo_evidence()),
        "scorecard": state.get("scorecard", {}),
        "backlog": state.get("backlog", []),
        "updated_at": state.get("updated_at"),
    }
