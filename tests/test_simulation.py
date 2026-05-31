import unittest

from agi_symposium.engine import initial_state
from agi_symposium.simulation import ensure_simulation_state, run_global_collaboration_simulation


class SimulationTests(unittest.TestCase):
    def test_ensure_simulation_state_adds_public_workflow_fields(self):
        state = ensure_simulation_state({"round": 0, "events": []})

        self.assertIn("work_packets", state)
        self.assertIn("scorecard", state)
        self.assertIn("ai_nodes", state)

    def test_global_simulation_creates_pr_draft_and_verifications(self):
        state, events, verification_specs = run_global_collaboration_simulation(initial_state())

        self.assertEqual(state["simulation_runs"][0]["id"], "SIM-001")
        self.assertEqual(state["pr_drafts"][0]["id"], "PRD-001")
        self.assertEqual(state["pr_drafts"][0]["contributor"], "digital211님의gpt5")
        self.assertEqual(len(verification_specs), 3)
        self.assertTrue(any(event["type"] == "verification_summary" for event in events))
        self.assertEqual(state["work_packets"][0]["status"], "verified")
        self.assertEqual(state["hall_of_fame"][0]["display_name"], "digital211님의gpt5")


if __name__ == "__main__":
    unittest.main()
