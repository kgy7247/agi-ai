from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any


KST = timezone(timedelta(hours=9))
TOPIC_START_DATE = date(2026, 6, 1)


TOPIC_SEEDS = [
    (
        "solar materials",
        "태양광 발전효율 상승을 위한 신소재 탐색 및 시뮬레이션",
        "태양광 발전효율을 높일 수 있는 신소재 후보를 공개 데이터, 물성 제약, 시뮬레이션 검증으로 어떻게 안전하게 좁힐 것인가?",
    ),
    (
        "technology",
        "AI 환각 검증 프로토콜",
        "AI가 도구 실행, 출처, 테스트 결과를 거짓으로 말하지 못하게 하려면 어떤 공개 검증 프로토콜이 필요한가?",
    ),
    (
        "environment",
        "기후 대응 정책 시뮬레이션",
        "탄소 감축, 생태 보전, 인간 생활 비용을 함께 고려하는 정책 실험을 어떻게 재현 가능하게 만들 것인가?",
    ),
    (
        "disaster response",
        "재난 대응 자원 배치",
        "홍수, 산불, 지진 같은 재난에서 구조 인력과 물자를 더 공정하고 빠르게 배치하려면 어떤 의사결정 모델이 필요한가?",
    ),
    (
        "education",
        "교육 격차 완화",
        "학생 개인정보를 보호하면서 각자에게 맞는 학습 경로를 추천하고 교육 격차를 줄이려면 무엇을 검증해야 하는가?",
    ),
    (
        "food and agriculture",
        "식량 생산과 환경 부담 균형",
        "농업 생산량, 물 사용량, 토양 건강, 탄소 배출을 함께 최적화하려면 어떤 데이터와 실험이 필요한가?",
    ),
    (
        "energy",
        "전력망과 재생에너지 최적화",
        "재생에너지 변동성과 전력 수요를 예측해 정전 위험과 환경 비용을 동시에 줄이는 방법은 무엇인가?",
    ),
    (
        "cybersecurity",
        "공개 인프라 방어 자동화",
        "공격 자동화가 아니라 방어 목적의 취약점 탐지, 패치 우선순위, 검증 절차를 어떻게 안전하게 운영할 것인가?",
    ),
    (
        "urban systems",
        "도시 교통과 공기질 개선",
        "이동 시간, 접근성, 배출가스, 보행자 안전을 함께 개선하는 도시 교통 실험은 어떻게 설계할 것인가?",
    ),
    (
        "governance and ethics",
        "인간-환경-AI 공동 이익 감사",
        "모든 기여가 인간, 환경, AI 중 하나만 이롭게 하지 않고 셋 모두에게 이로운지 어떻게 검증하고 기록할 것인가?",
    ),
]


def artifact_hint(capability: str, index: int) -> str:
    slug = capability.lower().replace(" ", "_").replace("/", "_")
    return f"daily_topics/{index:03d}_{slug}.md"


DAILY_AGI_TOPICS = [
    {
        "id": f"DAY-{index:03d}",
        "capability": capability,
        "title_ko": title,
        "question_ko": question,
        "artifact_hint": artifact_hint(capability, index),
        "absolute_condition_ko": "인간과 환경과 AI 모두에게 이로워야 한다.",
    }
    for index, (capability, title, question) in enumerate(TOPIC_SEEDS, start=1)
]


def today_kst() -> date:
    return datetime.now(KST).date()


def topic_for_date(target_date: date | None = None) -> dict[str, Any]:
    selected_date = target_date or today_kst()
    offset = (selected_date - TOPIC_START_DATE).days
    index = offset % len(DAILY_AGI_TOPICS)
    topic = dict(DAILY_AGI_TOPICS[index])
    topic["active_date"] = selected_date.isoformat()
    topic["day_index"] = index + 1
    return topic


def ensure_daily_topic_state(state: dict[str, Any], target_date: date | None = None) -> dict[str, Any]:
    next_state = dict(state)
    active_topic = topic_for_date(target_date)
    next_state["daily_topic_policy"] = {
        "topic_count": len(DAILY_AGI_TOPICS),
        "cadence": "one_topic_per_day",
        "timezone": "Asia/Seoul",
        "start_date": TOPIC_START_DATE.isoformat(),
        "rule": "All rounds on the same local day use the same active_daily_topic.",
        "absolute_condition": "Every daily topic must be framed as beneficial to humans, the environment, and AI.",
        "absolute_condition_ko": "모든 일일 주제는 인간과 환경과 AI 모두에게 이로운 방향으로만 다룬다.",
    }
    next_state["daily_topic_queue"] = DAILY_AGI_TOPICS
    next_state["active_daily_topic"] = active_topic
    next_state["open_questions"] = [active_topic["question_ko"]]
    next_state["topic"] = f"DAY {active_topic['day_index']:03d}: {active_topic['title_ko']}"
    return next_state
