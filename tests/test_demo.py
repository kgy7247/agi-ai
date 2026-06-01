import os
import unittest

from agi_symposium.demo import run_full_demo
from agi_symposium.release_check import restore_live_state, snapshot_live_state
from agi_symposium.storage import ROOT


class DemoTests(unittest.TestCase):
    @unittest.skipIf(os.environ.get("AGI_SYMPOSIUM_SANDBOX") == "1", "avoid recursive sandbox demo")
    def test_run_full_demo_returns_verified_result(self):
        snapshot = snapshot_live_state(ROOT)
        try:
            result = run_full_demo(nickname="testcli", ai_system="gpt5", reset=True)
        finally:
            restore_live_state(ROOT, snapshot)

        self.assertTrue(result["accepted"])
        self.assertEqual(result["demo_run"]["profile"], "testcli-gpt5")
        self.assertTrue(result["demo_run"]["patch_validation"]["ok"])
        self.assertTrue(result["demo_run"]["sandbox_result"]["ok"])
        self.assertTrue(result["demo_run"]["sandbox_result"]["tests"]["ok"])
        self.assertIn("CHANGE.patch", result["file_paths"]["patch"])


if __name__ == "__main__":
    unittest.main()
