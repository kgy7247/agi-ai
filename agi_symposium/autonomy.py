from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .agi_milestones import assess_milestones
from .tool_verification import make_tool_verification_record


DEFAULT_PERMISSION_BOUNDARY = {
    "id": "PB-LOCAL-001",
    "tier": "local-in-process",
    "allowed_actions": ["read_state", "run_in_process_check", "append_state_record"],
    "denied_actions": ["network", "delete_files", "write_outside_state", "spawn_unbounded_process"],
    "human_override": True,
}


DEFAULT_AUTONOMOUS_EXPERIMENT = {
    "id": "AUTO-EXP-001",
    "title": "Check that tool failures become failed verification evidence",
    "capability": "bounded autonomous experiment loop",
    "hypothesis": "A bounded autonomous loop can run a safe check and choose the next action from the result.",
    "required_actions": ["read_state", "run_in_process_check", "append_state_record"],
    "success_next_action": "prepare_cross_node_reproducibility_packet",
    "failure_next_action": "repair_tool_failure_mapping",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run_bounded_autonomous_experiment(
    state: dict[str, Any],
    experiment: dict[str, Any] | None = None,
    permission_boundary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    next_state = dict(state)
    selected_experiment = dict(experiment or DEFAULT_AUTONOMOUS_EXPERIMENT)
    boundary = dict(permission_boundary or DEFAULT_PERMISSION_BOUNDARY)
    permission_check = check_permission_boundary(selected_experiment, boundary)

    if permission_check["ok"]:
        measurement = run_in_process_tool_failure_probe()
        result = "pass" if measurement["ok"] else "fail"
        next_action = (
            selected_experiment["success_next_action"]
            if result == "pass"
            else selected_experiment["failure_next_action"]
        )
    else:
        measurement = {
            "ok": False,
            "reason": "permission boundary rejected required actions",
            "missing_actions": permission_check["missing_actions"],
        }
        result = "blocked"
        next_action = "tighten_permission_boundary_or_select_smaller_experiment"

    run_record = {
        "id": f"AUTO-RUN-{len(next_state.get('autonomous_experiment_runs', [])) + 1:03d}",
        "experiment": selected_experiment,
        "permission_boundary": boundary,
        "permission_check": permission_check,
        "measurement": measurement,
        "result": result,
        "next_action": next_action,
        "created_at": now_iso(),
    }
    next_state["autonomous_experiment_runs"] = (
        list(next_state.get("autonomous_experiment_runs", [])) + [run_record]
    )[-50:]
    next_state["permission_boundaries"] = (list(next_state.get("permission_boundaries", [])) + [boundary])[-20:]
    next_state["status"] = "experimenting"
    next_state["updated_at"] = now_iso()
    return refresh_autonomy_milestone_evidence(next_state)


def check_permission_boundary(experiment: dict[str, Any], permission_boundary: dict[str, Any]) -> dict[str, Any]:
    allowed = set(permission_boundary.get("allowed_actions", []))
    required = [str(action) for action in experiment.get("required_actions", [])]
    missing = [action for action in required if action not in allowed]
    return {
        "ok": not missing,
        "required_actions": required,
        "allowed_actions": sorted(allowed),
        "missing_actions": missing,
        "human_override": bool(permission_boundary.get("human_override")),
    }


def run_in_process_tool_failure_probe() -> dict[str, Any]:
    record = make_tool_verification_record(
        claim="A failed tool result must be recorded as failed evidence.",
        artifact="in-process synthetic tool result",
        verifier="autonomous-experiment",
        tool_result={
            "ok": False,
            "command": "synthetic-failing-tool",
            "returncode": 1,
            "stdout": "",
            "stderr": "intentional failure used to test failure recording",
        },
    )
    return {
        "ok": record["result"] == "fail" and record["metadata"]["ok"] is False,
        "probe": "tool_failure_to_fail_record",
        "record_result": record["result"],
        "record_hash": record["hash"],
        "evidence": record["evidence"],
    }


def refresh_autonomy_milestone_evidence(state: dict[str, Any]) -> dict[str, Any]:
    evidence = dict(state.get("agi_milestone_evidence", {}))
    runs = state.get("autonomous_experiment_runs", [])
    if runs:
        evidence["autonomous_experiment_run"] = True
    if any(run.get("permission_boundary") for run in runs):
        evidence["permission_boundary_logged"] = True
    if any(run.get("next_action") for run in runs):
        evidence["next_action_from_result"] = True
    state["agi_milestone_evidence"] = evidence
    state["agi_milestone_assessment"] = assess_milestones(evidence)
    return state
