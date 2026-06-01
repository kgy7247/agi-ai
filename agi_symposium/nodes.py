from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .identity import display_name, make_profile


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def register_ai_node(
    state: dict[str, Any],
    *,
    nickname: str,
    ai_system: str,
    node_type: str = "local_llm",
    endpoint: str = "local",
    capabilities: list[str] | None = None,
) -> dict[str, Any]:
    profile = make_profile(nickname, ai_system)
    node_id = display_name(profile)
    node = {
        "id": node_id,
        "name": node_id,
        "role": "local contributor node",
        "node_type": node_type,
        "endpoint": endpoint or "local",
        "capabilities": capabilities or ["debate", "review", "verify", "patch-propose"],
        "last_seen_at": now_iso(),
    }
    next_state = dict(state)
    nodes = [dict(item) for item in next_state.get("ai_nodes", []) if item.get("id") != node_id]
    nodes.append(node)
    next_state["ai_nodes"] = nodes
    return next_state
