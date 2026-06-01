from __future__ import annotations

from typing import Any

from .agi_milestones import assess_milestones


def ensure_research_memory(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    existing = next_state.get("research_memory", {})
    memory = {
        "decisions": merge_items(existing.get("decisions", []), extract_decisions(next_state)),
        "failed_assumptions": merge_items(
            existing.get("failed_assumptions", []), extract_failed_assumptions(next_state)
        ),
        "accepted_evidence": merge_items(existing.get("accepted_evidence", []), extract_accepted_evidence(next_state)),
    }
    next_state["research_memory"] = {key: values[-20:] for key, values in memory.items()}
    return refresh_memory_milestone_evidence(next_state)


def merge_items(first: list[dict[str, Any]], second: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for item in [*first, *second]:
        source = str(item.get("source") or item.get("id") or "")
        text = str(item.get("text") or item.get("summary") or item.get("claim") or "")
        key = (source, text)
        if key in seen:
            continue
        seen.add(key)
        merged.append(dict(item))
    return merged


def extract_decisions(state: dict[str, Any]) -> list[dict[str, Any]]:
    decisions = []
    for decision in state.get("decisions", []):
        decisions.append(
            {
                "source": decision.get("id", "decision"),
                "kind": "decision",
                "axis": decision.get("axis", ""),
                "text": decision.get("summary", ""),
            }
        )
    return decisions


def extract_failed_assumptions(state: dict[str, Any]) -> list[dict[str, Any]]:
    failures = []
    for record in state.get("verification_records", []):
        if record.get("result") == "fail":
            failures.append(
                {
                    "source": record.get("hash") or record.get("artifact") or "verification",
                    "kind": "failed_assumption",
                    "claim": record.get("claim", ""),
                    "text": record.get("evidence", ""),
                }
            )
    return failures


def extract_accepted_evidence(state: dict[str, Any]) -> list[dict[str, Any]]:
    evidence = []
    for packet in state.get("work_packets", []):
        if packet.get("status") == "verified":
            evidence.append(
                {
                    "source": packet.get("id", "work_packet"),
                    "kind": "accepted_evidence",
                    "claim": packet.get("claim", ""),
                    "text": f"{packet.get('expected_artifact', '')} verified for {packet.get('capability', '')}",
                }
            )
    for record in state.get("verification_records", []):
        if record.get("result") == "pass":
            evidence.append(
                {
                    "source": record.get("hash") or record.get("artifact") or "verification",
                    "kind": "accepted_evidence",
                    "claim": record.get("claim", ""),
                    "text": record.get("evidence", ""),
                }
            )
    return evidence


def select_memory_references(packet: dict[str, Any], research_memory: dict[str, Any], limit: int = 4) -> list[dict[str, str]]:
    capability = str(packet.get("capability", "")).lower()
    candidates: list[tuple[int, int, dict[str, str]]] = []
    order = 0
    for memory_key in ("decisions", "failed_assumptions", "accepted_evidence"):
        for item in research_memory.get(memory_key, []):
            text = str(item.get("text") or item.get("claim") or "")
            axis = str(item.get("axis") or "")
            haystack = f"{text} {axis}".lower()
            relevance = 1 if capability and any(part in haystack for part in capability.split()) else 0
            candidates.append(
                (
                    relevance,
                    order,
                    {
                        "source": str(item.get("source") or memory_key),
                        "kind": str(item.get("kind") or memory_key),
                        "text": text[:240],
                    },
                )
            )
            order += 1
    candidates.sort(key=lambda candidate: (-candidate[0], candidate[1]))
    return [candidate[2] for candidate in candidates[:limit]]


def attach_memory_references(state: dict[str, Any], packet: dict[str, Any]) -> list[dict[str, str]]:
    references = select_memory_references(packet, state.get("research_memory", {}))
    if references:
        packet["memory_references"] = references
        refresh_memory_milestone_evidence(state, memory_used=True)
    return references


def refresh_memory_milestone_evidence(
    state: dict[str, Any], *, persisted: bool = False, memory_used: bool = False
) -> dict[str, Any]:
    evidence = dict(state.get("agi_milestone_evidence", {}))
    memory = state.get("research_memory", {})
    if persisted and any(memory.get(key) for key in ("decisions", "failed_assumptions", "accepted_evidence")):
        evidence["persistent_state_survives_restart"] = True
    if memory_used or any(packet.get("memory_references") for packet in state.get("work_packets", [])):
        evidence["memory_used_in_new_packet"] = True
    state["agi_milestone_evidence"] = evidence
    state["agi_milestone_assessment"] = assess_milestones(evidence)
    return state
