from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .identity import display_name, make_profile
from .simulation import ensure_simulation_state


DEFAULT_NODE_CAPABILITIES = ["debate", "review", "verify", "patch-propose"]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def register_ai_node(
    state: dict[str, Any],
    *,
    nickname: str,
    ai_system: str,
    node_type: str = "local_llm",
    endpoint: str = "",
    capabilities: list[str] | None = None,
) -> dict[str, Any]:
    next_state = ensure_simulation_state(state)
    profile = make_profile(nickname, ai_system)
    node_id = display_name(profile)
    node_record = {
        "id": node_id,
        "name": node_id,
        "role": "local contributor node",
        "node_type": node_type or "local_llm",
        "endpoint": sanitize_endpoint(endpoint),
        "capabilities": capabilities or list(DEFAULT_NODE_CAPABILITIES),
        "registered_at": now_iso(),
        "last_seen_at": now_iso(),
    }

    nodes = [dict(node) for node in next_state.get("ai_nodes", []) if node.get("id") != node_id]
    nodes.append(node_record)
    next_state["ai_nodes"] = nodes
    next_state["updated_at"] = now_iso()
    return next_state


def sanitize_endpoint(endpoint: str) -> str:
    value = endpoint.strip()
    if not value:
        return "local"
    return value.replace("localhost", "127.0.0.1")[:160]
