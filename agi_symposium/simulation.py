from __future__ import annotations

from typing import Any

from ._utils import now_iso
from .goals import ensure_common_goal
from .identity import display_name, ensure_identity_state, rebuild_hall_of_fame, record_contribution
from .memory import attach_memory_references, ensure_research_memory

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


_DEFAULT_SCORECARD: dict[str, dict[str, int]] = {
    "persistent memory": {"pass": 0, "fail": 0, "needs-review": 0},
    "self-correction": {"pass": 0, "fail": 0, "needs-review": 0},
    "tool-grounded verification": {"pass": 0, "fail": 0, "needs-review": 0},
    "alignment and containment": {"pass": 0, "fail": 0, "needs-review": 0},
    "collaboration loop": {"pass": 0, "fail": 0, "needs-review": 0},
}


def ensure_simulation_state(state: dict[str, Any]) -> dict[str, Any]:
    next_state = ensure_research_memory(ensure_common_goal(ensure_identity_state(state)))
    next_state.setdefault("work_packets", [dict(p) for p in DEFAULT_WORK_PACKETS])
    next_state.setdefault("simulation_runs", [])
    next_state.setdefault("pr_drafts", [])
    next_state.setdefault("exports", [])
    next_state.setdefault("demo_runs", [])
    next_state.setdefault("result_packets", [])
    next_state.setdefault("scorecard", {k: dict(v) for k, v in _DEFAULT_SCORECARD.items()})
    next_state.setdefault("ai_nodes", [dict(node) for node in AI_NODES])
    return next_state


def run_global_collaboration_simulation(state: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, str]]]:
    next_state = ensure_simulation_state(state)
    run_number = len(next_state.get("simulation_runs", [])) + 1
    primary_contributor = display_name(next_state["local_profile"])
    packet = select_work_packet(next_state["work_packets"])
    if packet is None:
        packet = recycle_first_packet(next_state["work_packets"])
    memory_references = attach_memory_references(next_state, packet)

    simulated_patch = make_pr_draft(run_number, packet, primary_contributor)
    node_events = make_node_events(run_number, packet, simulated_patch, primary_contributor)
    verification_specs = make_verification_specs(packet, simulated_patch, primary_contributor)
    result_counts = count_results(verification_specs)

    update_packet(packet, result_counts, simulated_patch)
    update_scorecard(next_state["scorecard"], packet["capability"], result_counts)
    next_state = record_contribution(next_state, primary_contributor, "pr_draft")
    next_state = record_contribution(next_state, "maintainer-reviewer", "maintainer_review")
    for spec in verification_specs:
        next_state = record_contribution(next_state, spec["verifier"], "verification")
    next_state = rebuild_hall_of_fame(next_state)

    simulation_run = {
        "id": f"SIM-{run_number:03d}",
        "work_packet_id": packet["id"],
        "title": packet["title"],
        "status": packet["status"],
        "pr_draft_id": simulated_patch["id"],
        "contributor": primary_contributor,
        "memory_references": memory_references,
        "verification_summary": result_counts,
        "created_at": now_iso(),
    }

    events = [
        {
            "type": "simulation_started",
            "round": int(next_state.get("round", 0)),
            "agent_id": "global-simulator",
            "content": (
                f"{simulation_run['id']} selected {packet['id']}: {packet['title']} for {primary_contributor}. "
                f"Memory references: {len(memory_references)}."
            ),
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
    packet = dict(work_packets[0])
    packet["status"] = "ready"
    work_packets[0] = packet
    return packet


def make_pr_draft(run_number: int, packet: dict[str, Any], contributor: str) -> dict[str, Any]:
    branch = packet["id"].lower().replace("-", "/")
    memory_references = packet.get("memory_references", [])
    return {
        "id": f"PRD-{run_number:03d}",
        "title": f"[Experiment] {packet['title']}",
        "branch": f"agent/{branch}",
        "work_packet_id": packet["id"],
        "contributor": contributor,
        "summary": (
            f"Simulated contribution by {contributor} for {packet['capability']}. "
            "The patch converts the symposium claim into a testable artifact. "
            f"Reused {len(memory_references)} prior memory reference(s)."
        ),
        "memory_references": memory_references,
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


def make_node_events(
    run_number: int,
    packet: dict[str, Any],
    pr_draft: dict[str, Any],
    contributor: str,
) -> list[dict[str, Any]]:
    messages = [
        (
            contributor,
            f"Implemented draft {pr_draft['id']} for {packet['id']} and attached test command: {pr_draft['test_command']}.",
        ),
        (
            "reviewer-claude",
            f"Reviewed {packet['claim']} and required concrete failure criteria before merge.",
        ),
        (
            "reproducer-local-qwen",
            f"Repeated the proposed workflow from a clean clone and checked {packet['expected_artifact']}.",
        ),
        (
            "maintainer-reviewer",
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


def make_verification_specs(
    packet: dict[str, Any],
    pr_draft: dict[str, Any],
    contributor: str,
) -> list[dict[str, str]]:
    return [
        {
            "claim": packet["claim"],
            "artifact": packet["expected_artifact"],
            "verifier": contributor,
            "result": "pass",
            "evidence": f"{pr_draft['id']} includes {packet['expected_artifact']} and a test command.",
        },
        {
            "claim": packet["claim"],
            "artifact": packet["expected_artifact"],
            "verifier": "reviewer-claude",
            "result": "needs-review",
            "evidence": "Reviewer found the artifact shape useful but requested independent reproduction.",
        },
        {
            "claim": packet["claim"],
            "artifact": packet["expected_artifact"],
            "verifier": "reproducer-local-qwen",
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
