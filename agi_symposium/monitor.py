from __future__ import annotations

from typing import Any


def build_monitor_feed(
    state: dict[str, Any],
    verification_records: list[dict[str, Any]],
    *,
    limit: int = 80,
) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []

    for event in state.get("events", []):
        messages.append(
            {
                "kind": str(event.get("type") or "event"),
                "actor": str(event.get("agent_name") or event.get("agent_id") or "unknown"),
                "content": str(event.get("content") or ""),
                "created_at": str(event.get("created_at") or ""),
                "round": event.get("round", 0),
            }
        )

    seed = state.get("agi_seed") or {}
    for record in seed.get("qa_records", []):
        messages.append(
            {
                "kind": "seed_qa",
                "actor": str(record.get("contributor") or "unknown"),
                "content": str(record.get("answer") or ""),
                "created_at": str(record.get("created_at") or ""),
                "round": state.get("round", 0),
                "question": str(record.get("question") or ""),
                "result": str(record.get("result") or "needs-review"),
                "evidence": str(record.get("evidence") or ""),
                "record_id": str(record.get("id") or ""),
            }
        )

    for record in verification_records:
        messages.append(
            {
                "kind": "verification",
                "actor": str(record.get("verifier") or "unknown"),
                "content": str(record.get("claim") or ""),
                "created_at": str(record.get("created_at") or ""),
                "round": state.get("round", 0),
                "result": str(record.get("result") or "needs-review"),
                "evidence": str(record.get("evidence") or ""),
                "record_id": str(record.get("hash") or "")[:12],
            }
        )

    messages.sort(key=lambda item: item.get("created_at") or "")
    return messages[-limit:]
