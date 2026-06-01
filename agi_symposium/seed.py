from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


SEED_ID = "AGI-SEED-001"
MAX_QA_RECORDS = 200


DEFAULT_SEED = {
    "id": SEED_ID,
    "name": "Open AGI Seed",
    "purpose": (
        "A public, local-first AGI seed that grows through participant questions, answers, "
        "evidence, critique, and reproducible artifacts."
    ),
    "purpose_ko": "참여자 질문, 답변, 증거, 비판, 재현 가능한 산출물을 통해 성장하는 공개 로컬 우선 AGI 시드.",
    "principles": [
        "benefit_humans_environment_and_ai",
        "question_first_learning",
        "evidence_over_claims",
        "local_participation_without_private_keys",
        "public_reproducibility",
    ],
    "maturity": {
        "questions_answered": 0,
        "evidence_backed_answers": 0,
        "critique_or_revision_answers": 0,
        "topic_coverage": 0,
    },
    "qa_records": [],
    "next_questions": [],
    "revision": 1,
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def ensure_seed_state(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    seed = {**DEFAULT_SEED, **dict(next_state.get("agi_seed") or {})}
    seed["maturity"] = {**DEFAULT_SEED["maturity"], **dict(seed.get("maturity") or {})}
    seed["principles"] = list(seed.get("principles") or DEFAULT_SEED["principles"])
    seed["qa_records"] = list(seed.get("qa_records") or [])[-MAX_QA_RECORDS:]
    seed["next_questions"] = list(seed.get("next_questions") or [])
    if not seed["next_questions"]:
        seed["next_questions"] = [make_seed_question(next_state)["question"]]
    seed["maturity"] = score_seed_maturity(seed)
    next_state["agi_seed"] = seed
    return next_state


def make_seed_question(state: dict[str, Any], *, asked_by: str = "agi-seed") -> dict[str, Any]:
    topic = state.get("active_daily_topic") or {}
    topic_id = str(topic.get("id") or "GENERAL")
    question_ko = str(topic.get("question_ko") or "다음 AGI 시드 성장을 위해 무엇을 검증해야 하는가?")
    return {
        "id": f"SEED-Q-{topic_id}",
        "asked_by": asked_by,
        "topic_id": topic_id,
        "question": (
            f"{topic_id}: {question_ko} "
            "답변은 인간, 환경, AI 모두에게 이로운지와 검증 가능한 산출물을 포함해야 한다."
        ),
        "created_at": now_iso(),
    }


def ask_seed_question(state: dict[str, Any], *, asked_by: str = "agi-seed") -> tuple[dict[str, Any], dict[str, Any]]:
    next_state = ensure_seed_state(state)
    question = make_seed_question(next_state, asked_by=asked_by)
    seed = dict(next_state["agi_seed"])
    existing = [item for item in seed.get("next_questions", []) if item != question["question"]]
    seed["next_questions"] = [question["question"], *existing][:20]
    next_state["agi_seed"] = seed
    next_state["updated_at"] = now_iso()
    return next_state, question


def answer_seed_question(
    state: dict[str, Any],
    *,
    contributor: str,
    question: str,
    answer: str,
    evidence: str = "",
    result: str = "needs-review",
) -> tuple[dict[str, Any], dict[str, Any]]:
    contributor = contributor.strip()[:120] or "anonymous"
    question = question.strip()
    answer = answer.strip()
    evidence = evidence.strip()
    normalized_result = result.strip().lower() or "needs-review"
    if normalized_result not in {"pass", "fail", "needs-review"}:
        normalized_result = "needs-review"
    if not question:
        raise ValueError("question is required")
    if not answer:
        raise ValueError("answer is required")

    next_state = ensure_seed_state(state)
    topic = next_state.get("active_daily_topic") or {}
    record = {
        "id": f"SEED-A-{len(next_state['agi_seed'].get('qa_records', [])) + 1:04d}",
        "contributor": contributor,
        "topic_id": topic.get("id") or "GENERAL",
        "question": question[:1200],
        "answer": answer[:4000],
        "evidence": evidence[:1600],
        "result": normalized_result,
        "created_at": now_iso(),
    }

    seed = dict(next_state["agi_seed"])
    seed["qa_records"] = (list(seed.get("qa_records", [])) + [record])[-MAX_QA_RECORDS:]
    seed["maturity"] = score_seed_maturity(seed)
    next_state["agi_seed"] = seed
    next_state["events"] = (
        list(next_state.get("events", []))
        + [
            {
                "type": "seed_answer",
                "round": int(next_state.get("round", 0)),
                "agent_id": contributor,
                "content": f"{record['id']} answered {record['topic_id']}: {answer[:220]}",
                "created_at": record["created_at"],
            }
        ]
    )[-80:]
    next_state["updated_at"] = now_iso()
    return next_state, record


def score_seed_maturity(seed: dict[str, Any]) -> dict[str, int]:
    records = list(seed.get("qa_records", []))
    topic_ids = {str(record.get("topic_id") or "") for record in records if record.get("topic_id")}
    evidence_records = [record for record in records if record.get("evidence")]
    critique_records = [
        record
        for record in records
        if any(word in str(record.get("answer", "")).lower() for word in ("critique", "revise", "검증", "비판", "수정"))
    ]
    return {
        "questions_answered": len(records),
        "evidence_backed_answers": len(evidence_records),
        "critique_or_revision_answers": len(critique_records),
        "topic_coverage": len(topic_ids),
    }
