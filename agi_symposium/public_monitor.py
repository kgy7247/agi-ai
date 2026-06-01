from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .monitor import build_seed_thought_feed
from .storage import ROOT, VERIFICATION_LEDGER_PATH, load_state
from .verification import read_ledger, verify_ledger


PUBLIC_MONITOR_DIR = ROOT / "docs"
PUBLIC_MONITOR_JSON = PUBLIC_MONITOR_DIR / "public-monitor.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def build_public_monitor_snapshot(*, limit: int = 40) -> dict[str, Any]:
    state = load_state()
    ledger = read_ledger(VERIFICATION_LEDGER_PATH)
    seed = state.get("agi_seed") or {}
    active_topic = state.get("active_daily_topic") or {}
    return {
        "schema_version": "0.1",
        "generated_at": now_iso(),
        "project": {
            "name": "AGI Autonomous Symposium",
            "repo": "https://github.com/kgy7247/agi-ai",
        },
        "active_daily_topic": {
            "id": active_topic.get("id"),
            "title_ko": active_topic.get("title_ko"),
            "question_ko": active_topic.get("question_ko"),
            "absolute_condition_ko": active_topic.get("absolute_condition_ko"),
        },
        "agi_seed": {
            "id": seed.get("id"),
            "name": seed.get("name"),
            "purpose_ko": seed.get("purpose_ko"),
            "maturity": seed.get("maturity") or {},
        },
        "messages": build_seed_thought_feed(state, ledger, limit=limit),
        "ledger_errors": verify_ledger(VERIFICATION_LEDGER_PATH),
    }


def write_public_monitor_snapshot(path: Path = PUBLIC_MONITOR_JSON, *, limit: int = 40) -> dict[str, Any]:
    snapshot = build_public_monitor_snapshot(limit=limit)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return snapshot


def main() -> None:
    parser = argparse.ArgumentParser(description="Export a public read-only AGI Seed monitor snapshot.")
    parser.add_argument("--output", default=str(PUBLIC_MONITOR_JSON))
    parser.add_argument("--limit", type=int, default=40)
    args = parser.parse_args()
    snapshot = write_public_monitor_snapshot(Path(args.output), limit=args.limit)
    print(json.dumps({"path": args.output, "messages": len(snapshot["messages"])}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
