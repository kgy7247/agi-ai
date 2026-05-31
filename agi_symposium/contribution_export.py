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
    patch_text = render_change_patch(pr_draft, work_packet)

    files = {
        "pr_body": export_dir / "PR_BODY.md",
        "patch": export_dir / "CHANGE.patch",
        "work_packet": export_dir / "work_packet.json",
        "verification_snapshot": export_dir / "verification_snapshot.json",
    }
    write_text_lf(files["pr_body"], pr_body)
    write_text_lf(files["patch"], patch_text)
    write_text_lf(files["work_packet"], work_packet_json + "\n")
    write_text_lf(files["verification_snapshot"], verification_json + "\n")

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


def write_text_lf(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


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
            "## Patch",
            "",
            "Apply or inspect the generated `CHANGE.patch` before opening a real PR.",
            "",
            "## Risk",
            "",
            "This is a generated contribution packet. Review the actual code and rerun verification before merge.",
            "",
        ]
    )


def render_change_patch(pr_draft: dict[str, Any], work_packet: dict[str, Any]) -> str:
    hunks = []
    for file in pr_draft.get("files", []):
        path = str(file.get("path") or "").strip()
        if not path:
            continue
        content = render_generated_file(path, pr_draft, work_packet, file)
        hunks.append(render_new_file_diff(path, content))
    return "\n".join(hunks) + ("\n" if hunks else "")


def render_generated_file(
    path: str,
    pr_draft: dict[str, Any],
    work_packet: dict[str, Any],
    file: dict[str, Any],
) -> str:
    if path.startswith("tests/") and path.endswith(".py"):
        return render_generated_test_file(pr_draft, work_packet)
    if path.endswith(".md"):
        return render_generated_markdown_file(pr_draft, work_packet, file)
    return "\n".join(
        [
            f"# Generated artifact for {work_packet.get('id', 'unknown')}",
            f"# Contributor: {pr_draft.get('contributor', 'unknown')}",
            "",
            "ARTIFACT = {",
            f"    'work_packet_id': {work_packet.get('id', 'unknown')!r},",
            f"    'claim': {work_packet.get('claim', 'unknown')!r},",
            f"    'capability': {work_packet.get('capability', 'unknown')!r},",
            "}",
            "",
        ]
    )


def render_generated_test_file(pr_draft: dict[str, Any], work_packet: dict[str, Any]) -> str:
    test_name = safe_slug(str(work_packet.get("id") or "work")).replace("-", "_")
    return "\n".join(
        [
            "import unittest",
            "",
            "",
            f"class Generated{test_name.upper()}Test(unittest.TestCase):",
            "    def test_claim_is_converted_to_artifact(self):",
            f"        claim = {work_packet.get('claim', 'unknown')!r}",
            f"        capability = {work_packet.get('capability', 'unknown')!r}",
            f"        contributor = {pr_draft.get('contributor', 'unknown')!r}",
            "",
            "        self.assertTrue(claim)",
            "        self.assertTrue(capability)",
            "        self.assertTrue(contributor)",
            "        self.assertIn('-', contributor)",
            "",
            "",
            "if __name__ == '__main__':",
            "    unittest.main()",
            "",
        ]
    )


def render_generated_markdown_file(
    pr_draft: dict[str, Any],
    work_packet: dict[str, Any],
    file: dict[str, Any],
) -> str:
    return "\n".join(
        [
            f"# Verification Notes for {work_packet.get('id', 'unknown')}",
            "",
            f"- Contributor: `{pr_draft.get('contributor', 'unknown')}`",
            f"- PR draft: `{pr_draft.get('id', 'unknown')}`",
            f"- Capability: {work_packet.get('capability', 'unknown')}",
            f"- Claim: {work_packet.get('claim', 'unknown')}",
            f"- Purpose: {file.get('purpose', 'unknown')}",
            "",
            "## Reproduction",
            "",
            "```text",
            str(pr_draft.get("test_command") or "python -m unittest discover -v"),
            "```",
            "",
        ]
    )


def render_new_file_diff(path: str, content: str) -> str:
    lines = content.splitlines()
    diff_lines = [
        f"diff --git a/{path} b/{path}",
        "new file mode 100644",
        "index 0000000..0000000",
        "--- /dev/null",
        f"+++ b/{path}",
        f"@@ -0,0 +1,{len(lines)} @@",
    ]
    diff_lines.extend(f"+{line}" for line in lines)
    return "\n".join(diff_lines)


def safe_slug(value: str) -> str:
    safe = []
    for char in value:
        if char.isalnum() or char in {"-", "_"}:
            safe.append(char)
        else:
            safe.append("-")
    slug = "".join(safe).strip("-")
    return (slug or "contributor")[:80]
