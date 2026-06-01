from __future__ import annotations

from pathlib import Path
from typing import Any

from .agi_milestones import assess_milestones
from .verification import append_verification, make_verification_record


TOOL_CHECK_KIND = "tool_check"


def make_tool_verification_record(
    *,
    claim: str,
    artifact: str,
    verifier: str,
    tool_result: dict[str, Any],
) -> dict[str, Any]:
    ok = bool(tool_result.get("ok"))
    command = str(tool_result.get("command") or "unknown command")
    returncode = tool_result.get("returncode")
    evidence = summarize_tool_result(command, returncode, ok, tool_result)
    return make_verification_record(
        claim=claim,
        artifact=artifact,
        verifier=verifier,
        result="pass" if ok else "fail",
        evidence=evidence,
        metadata={
            "kind": TOOL_CHECK_KIND,
            "command": command,
            "returncode": returncode,
            "ok": ok,
        },
    )


def append_tool_verification(
    path: Path,
    *,
    claim: str,
    artifact: str,
    verifier: str,
    tool_result: dict[str, Any],
) -> dict[str, Any]:
    record = make_tool_verification_record(
        claim=claim,
        artifact=artifact,
        verifier=verifier,
        tool_result=tool_result,
    )
    return append_verification(path, record)


def summarize_tool_result(command: str, returncode: Any, ok: bool, tool_result: dict[str, Any]) -> str:
    stdout = clean_tail(str(tool_result.get("stdout") or ""))
    stderr = clean_tail(str(tool_result.get("stderr") or ""))
    lines = [f"tool={command}", f"ok={ok}", f"returncode={returncode}"]
    if stdout:
        lines.append(f"stdout_tail={stdout}")
    if stderr:
        lines.append(f"stderr_tail={stderr}")
    return " | ".join(lines)


def clean_tail(value: str, limit: int = 500) -> str:
    return " ".join(value.strip().split())[-limit:]


def refresh_tool_milestone_evidence(state: dict[str, Any], records: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    evidence = dict(state.get("agi_milestone_evidence", {}))
    all_records = list(records if records is not None else state.get("verification_records", []))
    tool_records = [record for record in all_records if record.get("metadata", {}).get("kind") == TOOL_CHECK_KIND]
    if any(record.get("result") == "pass" for record in tool_records):
        evidence["tool_check_pass"] = True
    if any(record.get("result") == "fail" for record in tool_records):
        evidence["tool_check_failure_recorded"] = True
    state["agi_milestone_evidence"] = evidence
    state["agi_milestone_assessment"] = assess_milestones(evidence)
    return state
