import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agi_symposium.release_check import (
    CheckResult,
    check_no_tracked_secrets,
    check_required_files,
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


if __name__ == "__main__":
    unittest.main()
