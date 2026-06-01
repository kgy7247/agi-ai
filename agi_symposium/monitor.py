from __future__ import annotations

from typing import Any


def build_monitor_feed(
    state: dict[str, Any],
    verification_records: list[dict[str, Any]],
    *,
    limit: int = 80,
) -> list[dict[str, Any]]:
    return build_seed_thought_feed(state, verification_records, limit=limit)


def build_seed_thought_feed(
    state: dict[str, Any],
    verification_records: list[dict[str, Any]],
    *,
    limit: int = 80,
) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    seed = state.get("agi_seed") or {}
    maturity = seed.get("maturity") or {}
    next_questions = list(seed.get("next_questions") or [])

    messages.append(
        {
            "kind": "seed_state",
            "actor": "AGI Seed",
            "content": (
                f"{seed.get('name') or 'Open AGI Seed'} is growing through Q&A. "
                f"Answered={maturity.get('questions_answered', 0)}, "
                f"evidence-backed={maturity.get('evidence_backed_answers', 0)}, "
                f"topic coverage={maturity.get('topic_coverage', 0)}."
            ),
            "created_at": str(state.get("updated_at") or ""),
            "round": state.get("round", 0),
            "result": "observing",
        }
    )

    for question in next_questions[:5]:
        messages.append(
            {
                "kind": "seed_question",
                "actor": "AGI Seed",
                "content": str(question),
                "created_at": str(state.get("updated_at") or ""),
                "round": state.get("round", 0),
                "result": "open",
            }
        )

    evidence_refs: set[str] = set()
    for record in seed.get("qa_records", []):
        evidence = str(record.get("evidence") or "")
        if evidence:
            evidence_refs.add(evidence)
        messages.append(
            {
                "kind": "seed_answer",
                "actor": "AGI Seed",
                "content": f"Absorbed answer from {record.get('contributor') or 'unknown'}:\n{record.get('answer') or ''}",
                "created_at": str(record.get("created_at") or ""),
                "round": state.get("round", 0),
                "question": str(record.get("question") or ""),
                "result": str(record.get("result") or "needs-review"),
                "evidence": evidence,
                "record_id": str(record.get("id") or ""),
            }
        )

    for record in verification_records:
        record_hash = str(record.get("hash") or "")
        if not any(ref and (record_hash in ref or record_hash[:12] in ref or ref in record_hash) for ref in evidence_refs):
            continue
        messages.append(
            {
                "kind": "seed_evidence",
                "actor": "AGI Seed Evidence",
                "content": f"Linked evidence from {record.get('verifier') or 'unknown'}: {record.get('claim') or ''}",
                "created_at": str(record.get("created_at") or ""),
                "round": state.get("round", 0),
                "result": str(record.get("result") or "needs-review"),
                "evidence": str(record.get("evidence") or ""),
                "record_id": str(record.get("hash") or "")[:12],
            }
        )

    messages.sort(key=lambda item: item.get("created_at") or "")
    return messages[-limit:]
