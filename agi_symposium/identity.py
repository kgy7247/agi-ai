from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any


DEFAULT_PROFILE = {
    "nickname": "digital211",
    "ai_system": "gpt5",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def clean_identity_part(value: str, fallback: str) -> str:
    cleaned = re.sub(r"[^0-9A-Za-z가-힣_.-]+", "-", value.strip()).strip("-")
    return (cleaned or fallback)[:48]


def make_profile(nickname: str, ai_system: str) -> dict[str, str]:
    profile = {
        "nickname": clean_identity_part(nickname, DEFAULT_PROFILE["nickname"]),
        "ai_system": clean_identity_part(ai_system, DEFAULT_PROFILE["ai_system"]),
    }
    profile["display_name"] = display_name(profile)
    return profile


def display_name(profile: dict[str, Any]) -> str:
    nickname = clean_identity_part(str(profile.get("nickname") or ""), DEFAULT_PROFILE["nickname"])
    ai_system = clean_identity_part(str(profile.get("ai_system") or ""), DEFAULT_PROFILE["ai_system"])
    return f"{nickname}님의{ai_system}"


def ensure_identity_state(state: dict[str, Any]) -> dict[str, Any]:
    next_state = dict(state)
    if "local_profile" not in next_state:
        next_state["local_profile"] = make_profile(DEFAULT_PROFILE["nickname"], DEFAULT_PROFILE["ai_system"])
    else:
        profile = next_state["local_profile"]
        next_state["local_profile"] = make_profile(
            str(profile.get("nickname") or DEFAULT_PROFILE["nickname"]),
            str(profile.get("ai_system") or DEFAULT_PROFILE["ai_system"]),
        )
    if "contributor_stats" not in next_state:
        next_state["contributor_stats"] = {}
    if "hall_of_fame" not in next_state:
        next_state["hall_of_fame"] = []
    if "last_hall_of_fame_update_at" not in next_state:
        next_state["last_hall_of_fame_update_at"] = None
    return next_state


def set_local_profile(state: dict[str, Any], nickname: str, ai_system: str) -> dict[str, Any]:
    next_state = ensure_identity_state(state)
    next_state["local_profile"] = make_profile(nickname, ai_system)
    next_state["updated_at"] = now_iso()
    return next_state


def record_contribution(
    state: dict[str, Any],
    contributor: str,
    contribution_type: str,
    amount: int = 1,
) -> dict[str, Any]:
    next_state = ensure_identity_state(state)
    contributor = contributor.strip()[:120] or display_name(next_state["local_profile"])
    stats = dict(next_state.get("contributor_stats", {}))
    entry = dict(
        stats.get(
            contributor,
            {
                "display_name": contributor,
                "total": 0,
                "by_type": {},
                "first_seen_at": now_iso(),
                "last_seen_at": None,
            },
        )
    )
    entry["total"] = int(entry.get("total", 0)) + amount
    by_type = dict(entry.get("by_type", {}))
    by_type[contribution_type] = int(by_type.get(contribution_type, 0)) + amount
    entry["by_type"] = by_type
    entry["last_seen_at"] = now_iso()
    stats[contributor] = entry
    next_state["contributor_stats"] = stats
    next_state["updated_at"] = now_iso()
    return next_state


def rebuild_hall_of_fame(state: dict[str, Any], *, force: bool = False) -> dict[str, Any]:
    next_state = ensure_identity_state(state)
    last_updated = next_state.get("last_hall_of_fame_update_at")
    if not force and last_updated and seconds_since(last_updated) < 3600:
        return next_state

    rows = sorted(
        next_state.get("contributor_stats", {}).values(),
        key=lambda item: (-int(item.get("total", 0)), str(item.get("display_name", ""))),
    )
    hall_of_fame = []
    for index, row in enumerate(rows[:20], start=1):
        hall_of_fame.append(
            {
                "rank": index,
                "display_name": row.get("display_name", ""),
                "total": int(row.get("total", 0)),
                "by_type": row.get("by_type", {}),
                "last_seen_at": row.get("last_seen_at"),
            }
        )
    next_state["hall_of_fame"] = hall_of_fame
    next_state["last_hall_of_fame_update_at"] = now_iso()
    next_state["updated_at"] = now_iso()
    return next_state


def seconds_since(iso_value: str) -> float:
    try:
        then = datetime.fromisoformat(iso_value)
    except ValueError:
        return 3600
    if then.tzinfo is None:
        then = then.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - then).total_seconds()

