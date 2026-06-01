from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .engine import initial_state
from .daily_topics import ensure_daily_topic_state
from .goals import ensure_common_goal
from .memory import ensure_research_memory, refresh_memory_milestone_evidence
from .seed import ensure_seed_state


ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / "state"
EXPORT_DIR = ROOT / "exports"
STATE_PATH = STATE_DIR / "symposium_state.json"
TRANSCRIPT_PATH = STATE_DIR / "transcript.jsonl"
VERIFICATION_LEDGER_PATH = STATE_DIR / "verification_ledger.jsonl"


def ensure_state_dir() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)


def load_state() -> dict[str, Any]:
    ensure_state_dir()
    if not STATE_PATH.exists():
        state = initial_state()
        save_state(state)
        return state
    with STATE_PATH.open("r", encoding="utf-8") as handle:
        state = ensure_seed_state(ensure_research_memory(ensure_daily_topic_state(ensure_common_goal(json.load(handle)))))
        return refresh_memory_milestone_evidence(state, persisted=True)


def save_state(state: dict[str, Any]) -> None:
    ensure_state_dir()
    temp_path = STATE_PATH.with_suffix(".tmp")
    with temp_path.open("w", encoding="utf-8") as handle:
        json.dump(state, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    temp_path.replace(STATE_PATH)


def append_events(events: list[dict[str, Any]]) -> None:
    ensure_state_dir()
    with TRANSCRIPT_PATH.open("a", encoding="utf-8") as handle:
        for event in events:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def reset_state() -> dict[str, Any]:
    state = initial_state()
    save_state(state)
    if TRANSCRIPT_PATH.exists():
        TRANSCRIPT_PATH.unlink()
    if VERIFICATION_LEDGER_PATH.exists():
        VERIFICATION_LEDGER_PATH.unlink()
    return state
