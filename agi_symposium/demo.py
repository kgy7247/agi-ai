from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .contribution_export import export_latest_contribution
from .identity import rebuild_hall_of_fame, record_contribution, set_local_profile
from .simulation import ensure_simulation_state, run_global_collaboration_simulation
from .storage import (
    EXPORT_DIR,
    ROOT,
    VERIFICATION_LEDGER_PATH,
    append_events,
    load_state,
    reset_state,
    save_state,
)
from .verification import append_verification, make_verification_record, read_ledger
from .workflow import apply_patch_and_run_tests_in_sandbox, validate_patch_with_git


def run_full_demo(
    *,
    nickname: str = "digital211",
    ai_system: str = "gpt5",
    reset: bool = False,
) -> dict[str, Any]:
    state = reset_state() if reset else load_state()
    state = set_local_profile(state, nickname, ai_system)
    state = ensure_simulation_state(state)
    state, events, verification_specs = run_global_collaboration_simulation(state)

    saved_records = []
    for spec in verification_specs:
        record = make_verification_record(**spec)
        saved_records.append(append_verification(VERIFICATION_LEDGER_PATH, record))

    export_record, file_paths = export_latest_contribution(
        state,
        read_ledger(VERIFICATION_LEDGER_PATH),
        EXPORT_DIR,
    )
    patch_path = Path(file_paths["patch"])
    patch_validation = validate_patch_with_git(patch_path, ROOT)
    sandbox_result = apply_patch_and_run_tests_in_sandbox(patch_path, ROOT)

    demo_run = {
        "id": f"DEMO-{len(state.get('demo_runs', [])) + 1:03d}",
        "profile": state["local_profile"]["display_name"],
        "simulation_id": state["simulation_runs"][-1]["id"],
        "export_id": export_record["id"],
        "patch_validation": patch_validation,
        "sandbox_result": sandbox_result,
        "created_at": export_record["created_at"],
    }
    demo_event = {
        "type": "demo_result",
        "round": int(state.get("round", 0)),
        "agent_id": "demo-runner",
        "content": (
            f"{demo_run['id']} created {export_record['id']} with "
            f"patch ok={patch_validation['ok']} and sandbox tests ok={sandbox_result['ok']}."
        ),
        "created_at": export_record["created_at"],
    }
    state["exports"] = (list(state.get("exports", [])) + [export_record])[-50:]
    state["demo_runs"] = (list(state.get("demo_runs", [])) + [demo_run])[-50:]
    state["events"] = (list(state.get("events", [])) + [demo_event])[-100:]
    state = record_contribution(state, str(export_record.get("contributor") or ""), "export")
    state = record_contribution(state, state["local_profile"]["display_name"], "demo_run")
    state = rebuild_hall_of_fame(state)
    save_state(state)
    append_events(events + [demo_event])

    return {
        "accepted": True,
        "demo_run": demo_run,
        "export": export_record,
        "file_paths": file_paths,
        "verification_records": saved_records,
        "state": state,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AGI symposium full demo workflow.")
    parser.add_argument("--nickname", default="digital211")
    parser.add_argument("--ai-system", default="gpt5")
    parser.add_argument("--reset", action="store_true")
    args = parser.parse_args()
    result = run_full_demo(nickname=args.nickname, ai_system=args.ai_system, reset=args.reset)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

