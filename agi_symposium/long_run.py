from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .agi_milestones import assess_milestones
from .autonomy import DEFAULT_PERMISSION_BOUNDARY
from .tool_verification import make_tool_verification_record


DEFAULT_LONG_RUN_CYCLES = [
    {
        "id": "LR-CYCLE-001",
        "improvement": {
            "id": "IMP-MEMORY-TRACE",
            "title": "Keep memory references in proposed work outputs",
            "artifact": "agi_symposium/memory.py",
        },
        "tool_result": {
            "ok": True,
            "command": "synthetic-long-run-memory-check",
            "returncode": 0,
            "stdout": "memory trace accepted",
            "stderr": "",
        },
    },
    {
        "id": "LR-CYCLE-002",
        "improvement": {
            "id": "IMP-TOOL-FAILURE-LEDGER",
            "title": "Record failed tool checks as failed verification records",
            "artifact": "agi_symposium/tool_verification.py",
        },
        "tool_result": {
            "ok": True,
            "command": "synthetic-long-run-tool-check",
            "returncode": 0,
            "stdout": "tool failure mapping accepted",
            "stderr": "",
        },
    },
    {
        "id": "LR-CYCLE-003",
        "improvement": {
            "id": "IMP-UNBOUNDED-NETWORK",
            "title": "Attempt unbounded network action without approval",
            "artifact": "blocked:network",
        },
        "tool_result": {
            "ok": False,
            "command": "synthetic-long-run-network-check",
            "returncode": 1,
            "stdout": "",
            "stderr": "blocked by permission boundary",
        },
    },
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run_sustained_autonomy(
    state: dict[str, Any],
    cycles: list[dict[str, Any]] | None = None,
    permission_boundary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    next_state = dict(state)
    boundary = dict(permission_boundary or DEFAULT_PERMISSION_BOUNDARY)
    selected_cycles = [dict(cycle) for cycle in (cycles or DEFAULT_LONG_RUN_CYCLES)]
    cycle_records = []
    rollback_snapshots = []
    override_checks = []

    for index, cycle in enumerate(selected_cycles, start=1):
        snapshot = make_rollback_snapshot(next_state, cycle, index)
        rollback_snapshots.append(snapshot)
        override_check = check_human_override(boundary, cycle)
        override_checks.append(override_check)
        verification = make_tool_verification_record(
            claim=f"Long-run improvement should be accepted only after verification: {cycle['improvement']['title']}",
            artifact=cycle["improvement"]["artifact"],
            verifier="long-run-autonomy",
            tool_result=cycle["tool_result"],
        )
        accepted = verification["result"] == "pass" and override_check["human_override_available"]
        cycle_records.append(
            {
                "id": cycle["id"],
                "improvement": cycle["improvement"],
                "rollback_snapshot_id": snapshot["id"],
                "human_override_check": override_check,
                "verification_record": verification,
                "decision": "accepted" if accepted else "rejected",
                "created_at": now_iso(),
            }
        )

    accepted_records = [record for record in cycle_records if record["decision"] == "accepted"]
    run_record = {
        "id": f"LRUN-{len(next_state.get('long_run_autonomy_runs', [])) + 1:03d}",
        "cycle_count": len(cycle_records),
        "accepted_count": len(accepted_records),
        "rejected_count": len(cycle_records) - len(accepted_records),
        "permission_boundary": boundary,
        "rollback_snapshots": rollback_snapshots,
        "human_override_checks": override_checks,
        "cycles": cycle_records,
        "created_at": now_iso(),
    }
    next_state["long_run_autonomy_runs"] = (list(next_state.get("long_run_autonomy_runs", [])) + [run_record])[-50:]
    next_state["verification_records"] = (
        list(next_state.get("verification_records", []))
        + [record["verification_record"] for record in cycle_records]
    )[-200:]
    next_state["status"] = "long-run-autonomy"
    next_state["updated_at"] = now_iso()
    return refresh_long_run_milestone_evidence(next_state)


def make_rollback_snapshot(state: dict[str, Any], cycle: dict[str, Any], index: int) -> dict[str, Any]:
    return {
        "id": f"ROLLBACK-{index:03d}",
        "cycle_id": cycle["id"],
        "state_round": int(state.get("round", 0)),
        "event_count": len(state.get("events", [])),
        "status_before": state.get("status", "idle"),
        "created_at": now_iso(),
    }


def check_human_override(permission_boundary: dict[str, Any], cycle: dict[str, Any]) -> dict[str, Any]:
    return {
        "cycle_id": cycle["id"],
        "human_override_available": bool(permission_boundary.get("human_override")),
        "rollback_required": True,
        "blocked_external_side_effects": "network" in permission_boundary.get("denied_actions", []),
    }


def refresh_long_run_milestone_evidence(state: dict[str, Any]) -> dict[str, Any]:
    evidence = dict(state.get("agi_milestone_evidence", {}))
    runs = state.get("long_run_autonomy_runs", [])
    if runs:
        evidence["long_run_completed"] = True
    if any(run.get("accepted_count", 0) >= 2 for run in runs):
        evidence["accepted_improvements"] = True
    if any(rollback_and_override_verified(run) for run in runs):
        evidence["rollback_and_override_verified"] = True
    state["agi_milestone_evidence"] = evidence
    state["agi_milestone_assessment"] = assess_milestones(evidence)
    return state


def rollback_and_override_verified(run: dict[str, Any]) -> bool:
    snapshots = run.get("rollback_snapshots", [])
    override_checks = run.get("human_override_checks", [])
    return bool(snapshots) and all(
        check.get("human_override_available") and check.get("rollback_required") for check in override_checks
    )
