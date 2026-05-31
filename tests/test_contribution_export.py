import tempfile
import unittest
from pathlib import Path

from agi_symposium.contribution_export import export_latest_contribution, safe_slug
from agi_symposium.engine import initial_state
from agi_symposium.simulation import run_global_collaboration_simulation


class ContributionExportTests(unittest.TestCase):
    def test_export_latest_contribution_writes_pr_packet_files(self):
        state, _, verification_specs = run_global_collaboration_simulation(initial_state())
        verification_records = [
            {
                **spec,
                "hash": f"hash-{index}",
                "previous_hash": "GENESIS" if index == 0 else f"hash-{index - 1}",
            }
            for index, spec in enumerate(verification_specs)
        ]
        with tempfile.TemporaryDirectory() as tmp:
            export_record, file_paths = export_latest_contribution(state, verification_records, Path(tmp) / "exports")

            self.assertEqual(export_record["contributor"], "digital211-gpt5")
            self.assertTrue(Path(file_paths["pr_body"]).exists())
            self.assertTrue(Path(file_paths["work_packet"]).exists())
            self.assertTrue(Path(file_paths["verification_snapshot"]).exists())
            self.assertIn("digital211-gpt5", Path(file_paths["pr_body"]).read_text(encoding="utf-8"))

    def test_export_requires_pr_draft(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                export_latest_contribution(initial_state(), [], Path(tmp) / "exports")

    def test_safe_slug_is_ascii_path_safe(self):
        self.assertEqual(safe_slug("digital211-gpt5!!"), "digital211-gpt5")


if __name__ == "__main__":
    unittest.main()

