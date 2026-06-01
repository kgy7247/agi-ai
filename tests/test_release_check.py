import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agi_symposium.release_check import (
    CheckResult,
    check_tests,
    check_no_tracked_secrets,
    check_required_files,
    restore_live_state,
    snapshot_live_state,
    summarize,
)


class ReleaseCheckTests(unittest.TestCase):
    def test_required_files_reports_missing_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = check_required_files(Path(tmp))

        self.assertFalse(result.ok)
        self.assertIn("README.md", result.detail)

    def test_no_tracked_secrets_flags_secret_like_paths(self):
        with patch("agi_symposium.release_check.run_command", return_value=(0, "README.md\nsecrets/token.json", "")):
            result = check_no_tracked_secrets(Path("."))

        self.assertFalse(result.ok)
        self.assertIn("secrets/token.json", result.detail)

    def test_missing_remote_is_warning_not_blocker(self):
        summary = summarize(
            [
                CheckResult("required_files", True, "ok"),
                CheckResult("git_remote", False, "no remote configured yet"),
            ]
        )

        self.assertTrue(summary["ok"])
        self.assertEqual(summary["warning_count"], 1)

    def test_live_state_snapshot_restores_existing_and_missing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state_dir = root / "state"
            state_dir.mkdir()
            existing = state_dir / "symposium_state.json"
            existing.write_text('{"before": true}\n', encoding="utf-8")

            snapshot = snapshot_live_state(root)
            existing.write_text('{"after": true}\n', encoding="utf-8")
            created = state_dir / "verification_ledger.jsonl"
            created.write_text("{}\n", encoding="utf-8")

            restore_live_state(root, snapshot)

            self.assertEqual(existing.read_text(encoding="utf-8"), '{"before": true}\n')
            self.assertFalse(created.exists())

    def test_check_tests_restores_live_state_after_running_command(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            state_dir = root / "state"
            state_dir.mkdir()
            ledger = state_dir / "verification_ledger.jsonl"
            ledger.write_text("before\n", encoding="utf-8")

            def mutate_state(*args, **kwargs):
                ledger.write_text("after\n", encoding="utf-8")
                return (0, "ok", "")

            with patch("agi_symposium.release_check.run_command", side_effect=mutate_state):
                result = check_tests(root)

            self.assertTrue(result.ok)
            self.assertEqual(ledger.read_text(encoding="utf-8"), "before\n")


if __name__ == "__main__":
    unittest.main()
