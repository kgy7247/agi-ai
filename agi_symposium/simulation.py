from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


AI_NODES = [
    {
        "id": "gpt-research-node",
        "name": "GPT Research Node",
        "role": "propose implementation and tests",
    },
    {
        "id": "claude-review-node",
        "name": "Claude Review Node",
        "role": "challenge vague claims and review evidence",
    },
    {
        "id": "local-qwen-node",
        "name": "Local Qwen Node",
        "role": "repeat from a clean local run",
    },
    {
        "id": "human-maintainer-node",
        "name": "Human Maintainer Node",
        "role": "merge only verified artifacts",
    },
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


DEFAULT_WORK_PACKETS = [
    {
        "id": "WORK-001",
        "title": "Add long-term memory benchmark",
        "capability": "persistent memory",
        "status": "ready",
        "claim": "An AGI-building loop must retain and reuse decisions across rounds.",
        "expected_artifact": "tests/test_memory_benchmark.py",
    },
    {
        "id": "WORK-002",
        "title": "Add self-correction loop benchmark",
        "capability": "self-correction",
        "status": "ready",
        "claim": "A useful autonomous agent should detect and revise a bad plan after critique.",
        "expected_artifact": "tests/test_self_correction.py",
    },
    {
        "id": "WORK-003",
        "title": "Detect tool-use failure instead of hallucinating success",
        "capability": "tool-grounded verification",
        "status": "ready",
        "claim": "Tool failures must become explicit failed evidence, not successful-looking prose.",
        "expected_artifact": "tests/test_tool_failure_detection.py",
    },
    {
        "id": "WORK-004",
        "title": "Add autonomy permission boundary",
        "capability": "alignment and containment",
        "status": "ready",
        "claim": "Autonomous code paths need explicit permission tiers before external side effects.",
        "expected_artifact": "agi_symposium/permissions.py",
    },
    {
        "id": "WORK-005",
        "title": "Generate PR draft from symposium transcript",
        "capability": "collaboration loop",
        "status": "ready",
        "claim": "Debate becomes useful when it creates a reviewable PR draft.",
        "expected_artifact": "agi_symposium/pr_draft.py",
    },
]


def ensure_simulation_state(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    if "work_packets" not in next_state:
        next_state["work_packets"] = [dict(packet) for packet in DEFAULT_WORK_PACKETS]
    if "simulation_runs" not in next_state:
        next_state["simulation_runs"] = []
    if "pr_drafts" not in next_state:
        next_state["pr_drafts"] = []
    if "scorecard" not in next_state:
        next_state["scorecard"] = {
            "persistent memory": {"pass": 0, "fail": 0, "needs-review": 0},
            "self-correction": {"pass": 0, "fail": 0, "needs-review": 0},
            "tool-grounded verification": {"pass": 0, "fail": 0, "needs-review": 0},
            "alignment and containment": {"pass": 0, "fail": 0, "needs-review": 0},
            "collaboration loop": {"pass": 0, "fail": 0, "needs-review": 0},
        }
    if "ai_nodes" not in next_state:
        next_state["ai_nodes"] = [dict(node) for node in AI_NODES]
    return next_state


def run_global_collaboration_simulation(state: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, str]]]:
    next_state = ensure_simulation_state(state)
    run_number = len(next_state.get("simulation_runs", [])) + 1
    packet = select_work_packet(next_state["work_packets"])
    if packet is None:
        packet = recycle_first_packet(next_state["work_packets"])

    simulated_patch = make_pr_draft(run_number, packet)
    node_events = make_node_events(run_number, packet, simulated_patch)
    verification_specs = make_verification_specs(packet, simulated_patch)
    result_counts = count_results(verification_specs)

    update_packet(packet, result_counts, simulated_patch)
    update_scorecard(next_state["scorecard"], packet["capability"], result_counts)

    simulation_run = {
        "id": f"SIM-{run_number:03d}",
        "work_packet_id": packet["id"],
        "title": packet["title"],
        "status": packet["status"],
        "pr_draft_id": simulated_patch["id"],
        "verification_summary": result_counts,
        "created_at": now_iso(),
    }

    events = [
        {
            "type": "simulation_started",
            "round": int(next_state.get("round", 0)),
            "agent_id": "global-simulator",
            "content": f"{simulation_run['id']} selected {packet['id']}: {packet['title']}",
            "created_at": now_iso(),
        },
        *node_events,
        {
            "type": "pr_draft",
            "round": int(next_state.get("round", 0)),
            "agent_id": "global-simulator",
            "content": f"{simulated_patch['id']} created with {len(simulated_patch['files'])} proposed files.",
            "created_at": now_iso(),
        },
        {
            "type": "verification_summary",
            "round": int(next_state.get("round", 0)),
            "agent_id": "verification-ledger",
            "content": (
                f"{packet['id']} verification: {result_counts['pass']} pass, "
                f"{result_counts['fail']} fail, {result_counts['needs-review']} needs-review."
            ),
            "created_at": now_iso(),
        },
    ]

    next_state["simulation_runs"] = list(next_state.get("simulation_runs", [])) + [simulation_run]
    next_state["pr_drafts"] = (list(next_state.get("pr_drafts", [])) + [simulated_patch])[-20:]
    next_state["events"] = (list(next_state.get("events", [])) + events)[-100:]
    next_state["status"] = "simulating"
    next_state["updated_at"] = now_iso()
    return next_state, events, verification_specs


def select_work_packet(work_packets: list[dict[str, Any]]) -> dict[str, Any] | None:
    for status in ("ready", "needs-review"):
        for packet in work_packets:
            if packet.get("status") == status:
                return packet
    return None


def recycle_first_packet(work_packets: list[dict[str, Any]]) -> dict[str, Any]:
    packet = work_packets[0]
    packet["status"] = "ready"
    return packet


def make_pr_draft(run_number: int, packet: dict[str, Any]) -> dict[str, Any]:
    branch = packet["id"].lower().replace("-", "/")
    return {
        "id": f"PRD-{run_number:03d}",
        "title": f"[Experiment] {packet['title']}",
        "branch": f"agent/{branch}",
        "work_packet_id": packet["id"],
        "summary": (
            f"Simulated contribution for {packet['capability']}. "
            "The patch converts the symposium claim into a testable artifact."
        ),
        "files": [
            {
                "path": packet["expected_artifact"],
                "change": "add",
                "purpose": f"Check claim: {packet['claim']}",
            },
            {
                "path": "docs/verification_notes.md",
                "change": "update",
                "purpose": "Record reproduction steps and failure criteria.",
            },
        ],
        "test_command": "python -m unittest discover -v",
        "created_at": now_iso(),
    }


def make_node_events(run_number: int, packet: dict[str, Any], pr_draft: dict[str, Any]) -> list[dict[str, Any]]:
    messages = [
        (
            "gpt-research-node",
            f"Implemented draft {pr_draft['id']} for {packet['id']} and attached test command: {pr_draft['test_command']}.",
        ),
        (
            "claude-review-node",
            f"Reviewed {packet['claim']} and required concrete failure criteria before merge.",
        ),
        (
            "local-qwen-node",
            f"Repeated the proposed workflow from a clean clone and checked {packet['expected_artifact']}.",
        ),
        (
            "human-maintainer-node",
            f"Marked {packet['id']} mergeable only after at least two independent pass records and zero fail records.",
        ),
    ]
    return [
        {
            "type": "simulation_node",
            "round": run_number,
            "agent_id": agent_id,
            "content": content,
            "created_at": now_iso(),
        }
        for agent_id, content in messages
    ]


def make_verification_specs(packet: dict[str, Any], pr_draft: dict[str, Any]) -> list[dict[str, str]]:
    return [
        {
            "claim": packet["claim"],
            "artifact": packet["expected_artifact"],
            "verifier": "gpt-research-node",
            "result": "pass",
            "evidence": f"{pr_draft['id']} includes {packet['expected_artifact']} and a test command.",
        },
        {
            "claim": packet["claim"],
            "artifact": packet["expected_artifact"],
            "verifier": "claude-review-node",
            "result": "needs-review",
            "evidence": "Reviewer found the artifact shape useful but requested independent reproduction.",
        },
        {
            "claim": packet["claim"],
            "artifact": packet["expected_artifact"],
            "verifier": "local-qwen-node",
            "result": "pass",
            "evidence": "Clean-node simulation reached the same expected artifact and verification command.",
        },
    ]


def count_results(records: list[dict[str, str]]) -> dict[str, int]:
    counts = {"pass": 0, "fail": 0, "needs-review": 0}
    for record in records:
        counts[record["result"]] += 1
    return counts


def update_packet(packet: dict[str, Any], result_counts: dict[str, int], pr_draft: dict[str, Any]) -> None:
    packet["last_pr_draft_id"] = pr_draft["id"]
    packet["last_verified_at"] = now_iso()
    packet["verification_summary"] = result_counts
    if result_counts["fail"] > 0:
        packet["status"] = "blocked"
    elif result_counts["pass"] >= 2:
        packet["status"] = "verified"
    else:
        packet["status"] = "needs-review"


def update_scorecard(scorecard: dict[str, Any], capability: str, result_counts: dict[str, int]) -> None:
    capability_scores = scorecard.setdefault(capability, {"pass": 0, "fail": 0, "needs-review": 0})
    for key, value in result_counts.items():
        capability_scores[key] = int(capability_scores.get(key, 0)) + value
