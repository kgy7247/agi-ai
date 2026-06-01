import tempfile
import unittest
from pathlib import Path

from agi_symposium.engine import initial_state
from agi_symposium.tool_verification import (
    append_tool_verification,
    make_tool_verification_record,
    refresh_tool_milestone_evidence,
)
from agi_symposium.verification import read_ledger, verify_ledger
from agi_symposium.workflow import validate_patch_with_git


class ToolVerificationTests(unittest.TestCase):
    def test_successful_tool_result_becomes_pass_record(self):
        record = make_tool_verification_record(
            claim="tests should pass",
            artifact="tests",
            verifier="tool-runner",
            tool_result={
                "ok": True,
                "command": "python -m unittest discover -v",
                "returncode": 0,
                "stdout": "OK",
                "stderr": "",
            },
        )

        self.assertEqual(record["result"], "pass")
        self.assertEqual(record["metadata"]["kind"], "tool_check")
        self.assertIn("returncode=0", record["evidence"])

    def test_failed_tool_result_becomes_fail_record_in_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger_path = Path(tmp) / "verification_ledger.jsonl"
            repo_root = Path(tmp)
            tool_result = validate_patch_with_git(repo_root / "missing.patch", repo_root)
            record = append_tool_verification(
                ledger_path,
                claim="missing patch should not be accepted",
                artifact="missing.patch",
                verifier="tool-runner",
                tool_result=tool_result,
            )

            records = read_ledger(ledger_path)

        self.assertFalse(tool_result["ok"])
        self.assertEqual(record["result"], "fail")
        self.assertEqual(records[0]["result"], "fail")
        self.assertIn("patch file does not exist", records[0]["evidence"])
        self.assertEqual(verify_ledger(ledger_path), [])

    def test_tool_records_complete_m3_evidence(self):
        pass_record = make_tool_verification_record(
            claim="tool pass",
            artifact="artifact",
            verifier="tool-runner",
            tool_result={"ok": True, "command": "test-pass", "returncode": 0},
        )
        fail_record = make_tool_verification_record(
            claim="tool fail",
            artifact="artifact",
            verifier="tool-runner",
            tool_result={"ok": False, "command": "test-fail", "returncode": 1},
        )

        state = refresh_tool_milestone_evidence(initial_state(), [pass_record, fail_record])
        passed_ids = {
            status["id"] for status in state["agi_milestone_assessment"]["statuses"] if status["status"] == "pass"
        }

        self.assertIn("M3", passed_ids)


if __name__ == "__main__":
    unittest.main()
