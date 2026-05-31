from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def export_latest_contribution(
    state: dict[str, Any],
    verification_records: list[dict[str, Any]],
    export_root: Path,
) -> tuple[dict[str, Any], dict[str, str]]:
    pr_drafts = list(state.get("pr_drafts", []))
    if not pr_drafts:
        raise ValueError("no PR draft exists; run Simulate Global Loop first")

    pr_draft = pr_drafts[-1]
    work_packet = find_work_packet(state, str(pr_draft.get("work_packet_id") or ""))
    export_id = f"{pr_draft['id']}-{safe_slug(pr_draft.get('contributor', 'contributor'))}"
    export_dir = export_root / export_id
    export_dir.mkdir(parents=True, exist_ok=True)

    pr_body = render_pr_body(pr_draft, work_packet, verification_records)
    work_packet_json = json.dumps(
        {
            "schema_version": "0.1",
            "export_id": export_id,
            "created_at": now_iso(),
            "work_packet": work_packet,
            "pr_draft": pr_draft,
        },
        ensure_ascii=False,
        indent=2,
    )
    verification_json = json.dumps(
        {
            "schema_version": "0.1",
            "export_id": export_id,
            "created_at": now_iso(),
            "verification_records": verification_records,
        },
        ensure_ascii=False,
        indent=2,
    )

    files = {
        "pr_body": export_dir / "PR_BODY.md",
        "work_packet": export_dir / "work_packet.json",
        "verification_snapshot": export_dir / "verification_snapshot.json",
    }
    files["pr_body"].write_text(pr_body, encoding="utf-8")
    files["work_packet"].write_text(work_packet_json + "\n", encoding="utf-8")
    files["verification_snapshot"].write_text(verification_json + "\n", encoding="utf-8")

    export_record = {
        "id": export_id,
        "created_at": now_iso(),
        "contributor": pr_draft.get("contributor"),
        "pr_draft_id": pr_draft.get("id"),
        "work_packet_id": pr_draft.get("work_packet_id"),
        "files": {name: str(path.relative_to(export_root.parent)) for name, path in files.items()},
    }
    return export_record, {name: str(path) for name, path in files.items()}


def find_work_packet(state: dict[str, Any], work_packet_id: str) -> dict[str, Any]:
    for packet in state.get("work_packets", []):
        if packet.get("id") == work_packet_id:
            return packet
    return {
        "id": work_packet_id or "unknown",
        "title": "Unknown work packet",
        "status": "unknown",
    }


def render_pr_body(
    pr_draft: dict[str, Any],
    work_packet: dict[str, Any],
    verification_records: list[dict[str, Any]],
) -> str:
    relevant_records = [
        record
        for record in verification_records
        if record.get("artifact") in {file.get("path") for file in pr_draft.get("files", [])}
        or record.get("claim") == work_packet.get("claim")
    ]
    if not relevant_records:
        relevant_records = verification_records[-5:]

    files = "\n".join(
        f"- `{file.get('path')}`: {file.get('change')} - {file.get('purpose')}"
        for file in pr_draft.get("files", [])
    )
    verifications = "\n".join(
        f"- `{record.get('result')}` by `{record.get('verifier')}`: {record.get('evidence')}"
        for record in relevant_records
    )
    if not verifications:
        verifications = "- No verification records yet."

    return "\n".join(
        [
            f"# {pr_draft.get('title')}",
            "",
            "## Summary",
            "",
            str(pr_draft.get("summary") or ""),
            "",
            "## Contributor",
            "",
            str(pr_draft.get("contributor") or "unknown"),
            "",
            "## Work Packet",
            "",
            f"- ID: `{work_packet.get('id')}`",
            f"- Title: {work_packet.get('title')}",
            f"- Capability: {work_packet.get('capability', 'unknown')}",
            f"- Claim: {work_packet.get('claim', 'unknown')}",
            "",
            "## Proposed Files",
            "",
            files or "- No files listed.",
            "",
            "## Verification",
            "",
            verifications,
            "",
            "## Test Command",
            "",
            "```text",
            str(pr_draft.get("test_command") or "python -m unittest discover -v"),
            "```",
            "",
            "## Risk",
            "",
            "This is a generated contribution packet. Review the actual code and rerun verification before merge.",
            "",
        ]
    )


def safe_slug(value: str) -> str:
    safe = []
    for char in value:
        if char.isalnum() or char in {"-", "_"}:
            safe.append(char)
        else:
            safe.append("-")
    slug = "".join(safe).strip("-")
    return (slug or "contributor")[:80]

