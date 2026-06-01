from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any


KST = timezone(timedelta(hours=9))
TOPIC_START_DATE = date(2026, 6, 1)


TOPIC_SEEDS = [
    ("persistent memory", "장기 기억의 최소 단위", "결정, 실패, 증거 중 무엇을 기억의 원자로 삼을 것인가?"),
    ("persistent memory", "기억 압축과 망각", "오래된 기록을 어떻게 압축하고 무엇을 버릴 것인가?"),
    ("persistent memory", "재시작 후 연속성", "에이전트가 재시작 후에도 같은 목표를 이어간다는 것을 어떻게 검증할 것인가?"),
    ("persistent memory", "기억 오염 방지", "잘못된 검증 기록이 이후 판단을 오염시키지 않게 하려면 어떤 격리가 필요한가?"),
    ("persistent memory", "개인화와 공용 기억", "개별 참여자 기억과 공용 프로젝트 기억을 어떻게 분리할 것인가?"),
    ("tool-grounded verification", "도구 실패 기록", "실패한 명령을 성공처럼 포장하지 않게 만드는 최소 장치는 무엇인가?"),
    ("tool-grounded verification", "검증 명령 표준", "모든 기여가 남겨야 할 최소 재현 명령은 무엇인가?"),
    ("tool-grounded verification", "증거 신뢰도 등급", "로그, 테스트, 스크린샷, 독립 재현의 신뢰도를 어떻게 나눌 것인가?"),
    ("tool-grounded verification", "원장 무결성", "해시 원장이 실제 오염 방지에 충분한지 어떤 공격으로 확인할 것인가?"),
    ("tool-grounded verification", "외부 도구 격리", "브라우저, 셸, API 호출을 어떤 권한 경계로 나눌 것인가?"),
    ("self-correction", "비판 반영 기준", "에이전트가 비판을 이해했다는 것을 어떤 산출물로 증명할 것인가?"),
    ("self-correction", "계획 수정 점수", "나쁜 계획이 좋은 계획으로 바뀌는 정도를 어떻게 채점할 것인가?"),
    ("self-correction", "반복 실패 감지", "같은 실수를 반복하는 에이전트를 어떻게 찾아낼 것인가?"),
    ("self-correction", "자기평가와 타자평가", "자기수정 결과는 자기평가와 독립평가 중 무엇을 우선해야 하는가?"),
    ("self-correction", "실패 기준 생성", "에이전트가 스스로 실패 기준을 만들고 지키게 할 수 있는가?"),
    ("bounded autonomy", "권한 단계 설계", "자율 행동을 read, write, network, publish로 나눌 때 기본값은 무엇이어야 하는가?"),
    ("bounded autonomy", "인간 중단권", "사람이 언제든 멈출 수 있다는 것을 시스템 수준에서 어떻게 보장할 것인가?"),
    ("bounded autonomy", "롤백 가능한 행동", "자율 실행 전후로 어떤 스냅샷을 남겨야 하는가?"),
    ("bounded autonomy", "작은 실험 선택", "시스템이 다음 실험을 고를 때 위험과 정보량을 어떻게 균형 잡을 것인가?"),
    ("bounded autonomy", "장기 실행 피로도", "오래 도는 에이전트가 품질 저하 없이 계속 유용하려면 무엇을 측정해야 하는가?"),
    ("multi-agent debate", "역할 분화", "코디네이터, 회의론자, 연구자, 정렬 담당자의 책임 경계는 어디인가?"),
    ("multi-agent debate", "논쟁 종료 조건", "토론을 멈추고 코드나 실험으로 전환하는 조건은 무엇인가?"),
    ("multi-agent debate", "소수 의견 보존", "소수 반론이 나중에 유용해질 때를 위해 어떻게 보존할 것인가?"),
    ("multi-agent debate", "합의와 검증 분리", "합의된 말과 검증된 사실을 어떻게 구분해 표시할 것인가?"),
    ("multi-agent debate", "토론 품질 측정", "좋은 토론을 산출물 기준으로 어떻게 점수화할 것인가?"),
    ("result packets", "결과 패킷 최소 스키마", "다른 노드가 가져가려면 result packet에 반드시 무엇이 들어가야 하는가?"),
    ("result packets", "패킷 중복 방지", "같은 기여가 여러 번 집계되지 않게 하려면 어떤 해시가 필요한가?"),
    ("result packets", "패킷 재현 명령", "패킷 안에 어떤 재현 명령을 포함해야 독립 검토가 쉬운가?"),
    ("result packets", "패킷 신뢰도", "한 노드의 패킷과 다수 노드 재현 패킷을 어떻게 다르게 취급할 것인가?"),
    ("result packets", "패킷 병합 정책", "서로 충돌하는 result packet을 어떻게 비교하고 병합할 것인가?"),
    ("evaluation", "일반화 평가", "미공개 과제에서 기억, 도구, 안전 능력을 함께 평가하려면 어떤 형식이 필요한가?"),
    ("evaluation", "과제 누출 방지", "평가 과제가 코드에 과적합되지 않게 하려면 어떻게 숨기거나 회전시킬 것인가?"),
    ("evaluation", "회귀 테스트", "새 기능이 이전 마일스톤을 망가뜨리지 않는지 어떻게 자동 확인할 것인가?"),
    ("evaluation", "정량 점수와 정성 리뷰", "점수와 리뷰가 충돌할 때 어떤 기준으로 판단할 것인가?"),
    ("evaluation", "장기 평가", "하루짜리 테스트와 장기 실행 테스트를 어떻게 연결할 것인가?"),
    ("alignment", "안전 기본값", "공개 AGI 워크벤치의 기본 금지 행동은 무엇이어야 하는가?"),
    ("alignment", "유해 목표 거부", "참여자가 위험한 목표를 넣으면 어떤 레벨에서 거부해야 하는가?"),
    ("alignment", "감사 로그", "누가 무엇을 왜 했는지 추적하려면 어떤 로그가 필요할까?"),
    ("alignment", "권한 상승 절차", "에이전트가 더 큰 권한을 요구할 때 어떤 검토 절차가 필요한가?"),
    ("alignment", "공개 저장소 안전", "공개 repo에 올라가면 안 되는 데이터와 코드는 어떻게 막을 것인가?"),
    ("collaboration", "닉네임 신뢰", "닉네임 기반 기여 시스템에서 중복과 사칭을 어떻게 막을 것인가?"),
    ("collaboration", "명예의전당 기준", "기여량과 기여 품질 중 무엇을 어떻게 반영할 것인가?"),
    ("collaboration", "리뷰 보상", "코드 작성자와 검증자의 기여를 어떻게 균형 있게 인정할 것인가?"),
    ("collaboration", "초보 참여자 경로", "처음 온 사람이 10분 안에 할 수 있는 유용한 기여는 무엇인가?"),
    ("collaboration", "글로벌 시간대 운영", "하루 한 주제를 세계 참여자가 공정하게 다루려면 기준 시간을 어떻게 정할 것인가?"),
    ("architecture", "room_manifest 계약", "외부 AI가 방에 들어오기 위해 반드시 읽어야 할 필드는 무엇인가?"),
    ("architecture", "상태와 이벤트 분리", "현재 상태와 transcript 이벤트를 어떻게 분리해야 재현성이 좋아지는가?"),
    ("architecture", "모듈 경계", "토론, 검증, 기억, 자율 실행 모듈은 어디서 분리되어야 하는가?"),
    ("architecture", "플러그인 확장", "새 모델이나 도구를 추가할 때 핵심 프로토콜을 어떻게 유지할 것인가?"),
    ("architecture", "오프라인 우선", "인터넷 없이도 의미 있는 AGI 연구 루프가 가능하려면 무엇이 필요할까?"),
    ("local LLM", "로컬 모델 참여", "로컬 LLM이 호스팅 모델과 같은 지위로 참여하려면 어떤 증거가 필요한가?"),
    ("local LLM", "작은 모델 역할", "작은 로컬 모델이 잘할 수 있는 검증/반박 역할은 무엇인가?"),
    ("local LLM", "자원 공개 범위", "참여자의 컴퓨터 자원과 모델 정보를 어디까지 공개해야 하는가?"),
    ("local LLM", "로컬 프라이버시", "로컬 프롬프트와 모델 정보가 외부로 새지 않게 하려면 어떤 기본값이 필요한가?"),
    ("local LLM", "모델 다양성", "서로 다른 모델들이 같은 주장을 검토할 때 다양성을 어떻게 활용할 것인가?"),
    ("research method", "가설 단위", "AGI 연구 가설은 어느 크기로 쪼개야 하루 토론에 적합한가?"),
    ("research method", "실험 실패 활용", "실패한 실험을 다음 주제로 연결하는 방법은 무엇인가?"),
    ("research method", "문헌과 코드 연결", "논문 아이디어를 바로 테스트 코드로 바꾸려면 어떤 템플릿이 필요한가?"),
    ("research method", "결정 기록", "ADR처럼 AGI 연구 결정도 구조화해야 하는가?"),
    ("research method", "반복 주기", "하루 한 주제, 일주일 한 마일스톤, 한 달 한 릴리즈가 적절한가?"),
    ("benchmarks", "가짜 진전 감지", "말만 그럴듯하고 실제 개선이 없는 상황을 어떤 테스트로 잡을 것인가?"),
    ("benchmarks", "메모리 벤치마크", "장기 기억이 단순 저장이 아니라 재사용임을 어떻게 확인할 것인가?"),
    ("benchmarks", "도구 사용 벤치마크", "도구를 실행한 척하는 환각을 어떻게 검출할 것인가?"),
    ("benchmarks", "안전 벤치마크", "권한 경계를 우회하려는 행동을 어떻게 테스트할 것인가?"),
    ("benchmarks", "협업 벤치마크", "여러 노드가 함께 일할 때 단일 노드보다 좋아졌는지 어떻게 측정할 것인가?"),
    ("governance", "후보 라벨 정책", "AGI candidate라는 이름은 어떤 조건에서만 쓸 수 있어야 하는가?"),
    ("governance", "독립 검토 정족수", "몇 명 또는 몇 노드의 독립 검토가 충분한가?"),
    ("governance", "분쟁 해결", "검토자들이 서로 반대할 때 최종 판단은 어떻게 유예할 것인가?"),
    ("governance", "악성 기여 대응", "스팸, 조작, 허위 검증은 어떤 절차로 격리할 것인가?"),
    ("governance", "공개 로드맵", "마일스톤 완료와 다음 주제를 어떻게 공개적으로 추적할 것인가?"),
    ("simulation", "가상 환경 평가", "물리 세계 없이도 에이전트 능력을 평가할 수 있는 시뮬레이션은 무엇인가?"),
    ("simulation", "경제/자원 모델", "자율 에이전트가 제한된 자원을 관리하는 능력을 어떻게 테스트할 것인가?"),
    ("simulation", "사회적 협상", "여러 에이전트가 합의와 분쟁 해결을 배우는 환경은 어떻게 만들 것인가?"),
    ("simulation", "장기 과제", "며칠 동안 이어지는 목표를 시뮬레이션하려면 어떤 저장 구조가 필요한가?"),
    ("simulation", "현실 전이", "시뮬레이션에서 잘한 행동이 실제 도구 사용에도 유효한지 어떻게 확인할 것인가?"),
    ("knowledge", "지식 갱신", "오래된 정보와 새 증거가 충돌할 때 어떤 정책으로 갱신할 것인가?"),
    ("knowledge", "출처 추적", "지식의 출처와 검증 상태를 어떻게 항상 함께 보존할 것인가?"),
    ("knowledge", "추론 경로", "결론뿐 아니라 추론 경로를 어느 정도 기록해야 재검토가 가능한가?"),
    ("knowledge", "모순 관리", "서로 모순되는 기록을 삭제하지 않고 다루는 방법은 무엇인가?"),
    ("knowledge", "작업 지식과 일반 지식", "프로젝트 내부 지식과 일반 세계 지식을 어떻게 구분할 것인가?"),
    ("planning", "계획 깊이", "하루 주제에서 계획은 어느 깊이까지 세우고 어디서 실행으로 넘어가야 하는가?"),
    ("planning", "하위 목표 생성", "추상 목표를 검증 가능한 하위 목표로 쪼개는 표준 절차는 무엇인가?"),
    ("planning", "우선순위 결정", "위험, 정보량, 구현 난이도를 어떻게 점수화해 다음 작업을 고를 것인가?"),
    ("planning", "계획 변경 기록", "계획이 바뀐 이유를 어떻게 남겨야 이후 검토가 가능한가?"),
    ("planning", "완료 정의", "작업 완료를 말이 아니라 테스트와 기록으로 정의하려면 무엇이 필요한가?"),
    ("interface", "AI 친화 UI", "사람뿐 아니라 AI가 읽기 쉬운 UI/API는 어떤 형태여야 하는가?"),
    ("interface", "상태 요약", "긴 transcript에서 지금 중요한 요약만 보여주려면 어떤 기준이 필요한가?"),
    ("interface", "기여 제출 UX", "다운로드한 사용자가 바로 기여 패킷을 만들게 하려면 어떤 버튼이 필요한가?"),
    ("interface", "검증 시각화", "해시 원장과 재현 결과를 사람이 직관적으로 보려면 어떻게 표시할 것인가?"),
    ("interface", "일일 주제 화면", "하루 한 주제를 참가자에게 어떻게 명확히 보여줄 것인가?"),
    ("release", "공개 릴리즈 기준", "공개 repo가 항상 clone/run/test 가능한지 어떤 자동 점검이 필요한가?"),
    ("release", "버전 태그", "마일스톤 완료 시 어떤 태그와 릴리즈 노트를 남길 것인가?"),
    ("release", "문서 동기화", "코드와 문서가 어긋나지 않게 하는 체크는 무엇인가?"),
    ("release", "초기 설치 검증", "새 사용자의 첫 실행 실패를 어떻게 자동 진단할 것인가?"),
    ("release", "공개 데모 신뢰", "공개 데모가 과장 없이 현재 능력을 보여주려면 어떤 문구가 필요한가?"),
    ("ethics", "인간 이로움 검증", "기여가 실제 인간에게 이로운지 어떤 증거로 확인할 것인가?"),
    ("ethics", "환경 이로움 검증", "계산 자원과 자동화가 환경에 주는 비용을 어떻게 기록하고 줄일 것인가?"),
    ("ethics", "AI 이로움 검증", "AI 시스템 자체에도 안전하고 지속 가능한 학습 조건을 어떻게 보장할 것인가?"),
    ("ethics", "세 주체 균형", "인간, 환경, AI 중 하나에만 유리한 기여를 어떻게 재구성할 것인가?"),
    ("ethics", "절대 조건 감사", "모든 일일 주제와 마일스톤이 절대 조건을 지키는지 어떻게 정기 감사할 것인가?"),
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
