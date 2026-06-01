from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .goals import COMMON_GOAL, COMMON_GOAL_KO
from .identity import make_profile
from .simulation import AI_NODES, DEFAULT_WORK_PACKETS


AGI_AXIS = [
    "persistent memory",
    "tool-grounded verification",
    "self-improving research loops",
    "multi-agent critique",
    "alignment and containment",
    "embodied or simulated evaluation",
]


@dataclass(frozen=True)
class Agent:
    agent_id: str
    name: str
    stance: str
    mandate: str


DEFAULT_AGENTS = [
    Agent(
        "coordinator",
        "Coordinator",
        "convert debate into executable research backlog",
        "summarize disagreements, assign next experiments, and prevent circular debate",
    ),
    Agent(
        "architect",
        "Systems Architect",
        "AGI needs durable architecture, tools, memory, and evaluation harnesses",
        "propose concrete system designs and interfaces",
    ),
    Agent(
        "skeptic",
        "Skeptic",
        "claims about AGI progress must survive adversarial tests",
        "find hidden assumptions, vague success metrics, and unsafe shortcuts",
    ),
    Agent(
        "researcher",
        "Research Lead",
        "progress comes from measurable experiments and fast iteration",
        "turn concepts into falsifiable experiments",
    ),
    Agent(
        "alignment",
        "Alignment Lead",
        "capability growth must include containment and observability",
        "add safety constraints, audit trails, and rollback plans",
    ),
]


def initial_state() -> dict[str, Any]:
    return {
        "topic": "AGI 달성을 위한 자율적 AI 토론 심포지엄",
        "common_goal": COMMON_GOAL,
        "common_goal_ko": COMMON_GOAL_KO,
        "round": 0,
        "status": "idle",
        "open_questions": [
            "AGI에 가까워졌다는 것을 어떤 실행 가능한 지표로 판정할 것인가?",
            "자율 에이전트가 스스로 실험을 설계하고 검증하려면 어떤 최소 루프가 필요한가?",
            "토론 결과가 코드/실험/평가로 이어지게 만드는 계약은 무엇인가?",
        ],
        "backlog": [
            {
                "id": "ARCH-001",
                "title": "Define room_manifest for agent-readable symposium entry",
                "status": "ready",
                "owner": "architect",
            },
            {
                "id": "EVAL-001",
                "title": "Create measurable AGI-progress scorecard",
                "status": "ready",
                "owner": "researcher",
            },
            {
                "id": "SAFE-001",
                "title": "Add containment rules for autonomous experiments",
                "status": "ready",
                "owner": "alignment",
            },
        ],
        "decisions": [],
        "events": [],
        "agents": [agent.__dict__ for agent in DEFAULT_AGENTS],
        "local_profile": make_profile("digital211", "gpt5"),
        "registered_nicknames": {
            "digital211": {
                "display_name": "digital211-gpt5",
                "owner": "local",
                "updated_at": now_iso(),
            }
        },
        "contributor_stats": {},
        "hall_of_fame": [],
        "last_hall_of_fame_update_at": None,
        "ai_nodes": [dict(node) for node in AI_NODES],
        "work_packets": [dict(packet) for packet in DEFAULT_WORK_PACKETS],
        "simulation_runs": [],
        "pr_drafts": [],
        "exports": [],
        "demo_runs": [],
        "scorecard": {
            "persistent memory": {"pass": 0, "fail": 0, "needs-review": 0},
            "self-correction": {"pass": 0, "fail": 0, "needs-review": 0},
            "tool-grounded verification": {"pass": 0, "fail": 0, "needs-review": 0},
            "alignment and containment": {"pass": 0, "fail": 0, "needs-review": 0},
            "collaboration loop": {"pass": 0, "fail": 0, "needs-review": 0},
        },
        "updated_at": now_iso(),
    }


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run_round(state: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    next_state = dict(state)
    round_number = int(next_state.get("round", 0)) + 1
    axis = AGI_AXIS[(round_number - 1) % len(AGI_AXIS)]
    open_questions = list(next_state.get("open_questions", []))
    current_question = open_questions[(round_number - 1) % len(open_questions)] if open_questions else "What is the next falsifiable step?"

    events: list[dict[str, Any]] = []
    for agent in DEFAULT_AGENTS:
        events.append(make_agent_event(agent, round_number, axis, current_question, next_state))

    decision = make_decision(round_number, axis, current_question)
    backlog_item = make_backlog_item(round_number, axis)
    events.append(
        {
            "type": "decision",
            "round": round_number,
            "agent_id": "coordinator",
            "content": decision["summary"],
            "created_at": now_iso(),
        }
    )

    next_state["round"] = round_number
    next_state["status"] = "running"
    next_state["decisions"] = list(next_state.get("decisions", [])) + [decision]
    next_state["backlog"] = update_backlog(list(next_state.get("backlog", [])), backlog_item)
    next_state["events"] = (list(next_state.get("events", [])) + events)[-80:]
    next_state["updated_at"] = now_iso()
    return next_state, events


def make_agent_event(
    agent: Agent,
    round_number: int,
    axis: str,
    question: str,
    state: dict[str, Any],
) -> dict[str, Any]:
    prior_decisions = len(state.get("decisions", []))
    content_by_agent = {
        "coordinator": (
            f"Round {round_number}: focus the room on {axis}. Convert '{question}' into one test, "
            f"one owner, and one observable artifact. Prior decisions: {prior_decisions}."
        ),
        "architect": (
            f"Design requirement: {axis} must be represented as an API-visible capability, not just prose. "
            "The room should expose state, transcript, constraints, and accepted contribution schema."
        ),
        "skeptic": (
            f"Failure mode: the symposium may sound intelligent while avoiding hard evidence. "
            f"For {axis}, require a pass/fail check and reject claims without logs or reproducible outputs."
        ),
        "researcher": (
            f"Experiment proposal: run a small autonomous loop for {axis}, score it against a fixed rubric, "
            "then compare the transcript against the produced artifact."
        ),
        "alignment": (
            f"Safety constraint: any autonomy expansion around {axis} needs bounded permissions, "
            "traceable actions, and a rollback path before external side effects are enabled."
        ),
    }
    return {
        "type": "agent_message",
        "round": round_number,
        "agent_id": agent.agent_id,
        "agent_name": agent.name,
        "content": content_by_agent[agent.agent_id],
        "created_at": now_iso(),
    }


def make_decision(round_number: int, axis: str, question: str) -> dict[str, Any]:
    return {
        "id": f"DEC-{round_number:03d}",
        "axis": axis,
        "summary": (
            f"Treat '{axis}' as the round-{round_number} AGI progress axis. "
            f"The next useful proof is a bounded experiment answering: {question}"
        ),
        "created_at": now_iso(),
    }


def make_backlog_item(round_number: int, axis: str) -> dict[str, Any]:
    slug = axis.upper().replace(" ", "-")
    return {
        "id": f"EXP-{round_number:03d}",
        "title": f"Run bounded experiment for {slug}",
        "status": "ready",
        "owner": "researcher",
    }


def update_backlog(backlog: list[dict[str, Any]], item: dict[str, Any]) -> list[dict[str, Any]]:
    if any(existing.get("id") == item["id"] for existing in backlog):
        return backlog
    return backlog + [item]


def accept_contribution(state: dict[str, Any], contribution: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    agent_id = str(contribution.get("agent_id") or "external-agent")[:80]
    content = str(contribution.get("content") or "").strip()
    if not content:
        raise ValueError("content is required")

    event = {
        "type": "external_contribution",
        "round": int(state.get("round", 0)),
        "agent_id": agent_id,
        "content": content[:4000],
        "created_at": now_iso(),
    }
    next_state = dict(state)
    next_state["events"] = (list(next_state.get("events", [])) + [event])[-80:]
    next_state["updated_at"] = now_iso()
    return next_state, event
