from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .agi_milestones import assess_milestones
from .identity import record_contribution
from .result_packets import verify_result_packet
from .simulation import ensure_simulation_state
from .verification import make_verification_record


CROSS_NODE_REVIEW_KIND = "cross_node_reproduction"


DEFAULT_REVIEW_NODES = [
    {
        "id": "independent-qwen-reviewer",
        "node_type": "local_llm",
        "capability": "clean packet reproduction",
    },
    {
        "id": "independent-llama-reviewer",
        "node_type": "local_llm",
        "capability": "independent hash and evidence review",
    },
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def reproduce_result_packet_across_nodes(
    state: dict[str, Any],
    packet: dict[str, Any],
    reviewers: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    next_state = ensure_simulation_state(state)
    reviewer_nodes = reviewers or DEFAULT_REVIEW_NODES
    errors = verify_result_packet(packet)
    review_records = make_cross_node_review_records(
        packet,
        reviewer_nodes,
        errors,
        previous_hash=last_state_record_hash(next_state),
    )
    pass_count = len([record for record in review_records if record["result"] == "pass"])
    result = "pass" if not errors and pass_count >= 2 else "fail"
    run_record = {
        "id": f"XNODE-{len(next_state.get('cross_node_reproduction_runs', [])) + 1:03d}",
        "packet_id": packet.get("id", ""),
        "packet_hash": packet.get("hash", ""),
        "reviewers": [node["id"] for node in reviewer_nodes],
        "verification_record_hashes": [record["hash"] for record in review_records],
        "result": result,
        "errors": errors,
        "created_at": now_iso(),
    }

    next_state["verification_records"] = (
        list(next_state.get("verification_records", [])) + review_records
    )[-200:]
    next_state["cross_node_reproduction_runs"] = (
        list(next_state.get("cross_node_reproduction_runs", [])) + [run_record]
    )[-50:]
    next_state["status"] = "cross-node-review"
    next_state["updated_at"] = now_iso()
    for node in reviewer_nodes:
        next_state = record_contribution(next_state, node["id"], "cross_node_review")
    return refresh_cross_node_milestone_evidence(next_state)


def make_cross_node_review_records(
    packet: dict[str, Any],
    reviewers: list[dict[str, str]],
    errors: list[str],
    *,
    previous_hash: str = "GENESIS",
) -> list[dict[str, Any]]:
    records = []
    prior_hash = previous_hash
    for index, reviewer in enumerate(reviewers, start=1):
        reviewer_id = reviewer["id"]
        result = "pass" if not errors else "fail"
        evidence = (
            f"{reviewer_id} reproduced packet {packet.get('id')} with hash {packet.get('hash')}"
            if not errors
            else f"{reviewer_id} could not reproduce packet {packet.get('id')}: {'; '.join(errors)}"
        )
        record = make_verification_record(
            claim="Result packet can be reproduced by an independent node.",
            artifact=f"result-packet:{packet.get('id', '')}",
            verifier=reviewer_id,
            result=result,
            evidence=evidence,
            previous_hash=prior_hash,
            metadata={
                "kind": CROSS_NODE_REVIEW_KIND,
                "reviewer_index": index,
                "packet_id": packet.get("id", ""),
                "packet_hash": packet.get("hash", ""),
                "node_type": reviewer.get("node_type", "unknown"),
            },
        )
        prior_hash = record["hash"]
        records.append(record)
    return records


def last_state_record_hash(state: dict[str, Any]) -> str:
    records = state.get("verification_records", [])
    if records:
        return str(records[-1].get("hash") or "GENESIS")
    return "GENESIS"


def refresh_cross_node_milestone_evidence(state: dict[str, Any]) -> dict[str, Any]:
    evidence = dict(state.get("agi_milestone_evidence", {}))
    runs = state.get("cross_node_reproduction_runs", [])
    pass_runs = [run for run in runs if run.get("result") == "pass"]
    if pass_runs:
        evidence["result_packet_reproduced"] = True
    latest_pass = pass_runs[-1] if pass_runs else {}
    reviewers = latest_pass.get("reviewers", [])
    if len(reviewers) >= 1:
        evidence["independent_node_a_review"] = True
    if len(reviewers) >= 2:
        evidence["independent_node_b_review"] = True
    state["agi_milestone_evidence"] = evidence
    state["agi_milestone_assessment"] = assess_milestones(evidence)
    return state
