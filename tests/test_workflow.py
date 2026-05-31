import tempfile
import unittest
from pathlib import Path

from agi_symposium.contribution_export import export_latest_contribution
from agi_symposium.engine import initial_state
from agi_symposium.simulation import ensure_simulation_state, run_global_collaboration_simulation
from agi_symposium.storage import ROOT
from agi_symposium.workflow import validate_patch_with_git


class WorkflowTests(unittest.TestCase):
    def test_validate_patch_with_git_accepts_generated_patch(self):
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
            _, file_paths = export_latest_contribution(state, verification_records, Path(tmp) / "exports")
            result = validate_patch_with_git(Path(file_paths["patch"]), ROOT)

            self.assertTrue(result["ok"], result)
            self.assertEqual(result["returncode"], 0)

    def test_simulation_state_contains_demo_run_list(self):
        state = ensure_simulation_state({})

        self.assertIn("demo_runs", state)
        self.assertEqual(state["demo_runs"], [])


if __name__ == "__main__":
    unittest.main()

