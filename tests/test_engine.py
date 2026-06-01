import unittest

from agi_symposium.engine import accept_contribution, initial_state, run_round
from agi_symposium.manifest import room_manifest


class EngineTests(unittest.TestCase):
    def test_run_round_adds_events_decision_and_backlog(self):
        state = initial_state()
        next_state, events = run_round(state)

        self.assertEqual(next_state["round"], 1)
        self.assertGreaterEqual(len(events), 6)
        self.assertEqual(len(next_state["decisions"]), 1)
        self.assertTrue(any(item["id"] == "EXP-001" for item in next_state["backlog"]))

    def test_manifest_exposes_agent_entry_contract(self):
        manifest = room_manifest(initial_state())

        self.assertEqual(manifest["entry_contract"]["read_state"], "GET /api/state")
        self.assertEqual(manifest["entry_contract"]["contribute"], "POST /api/contribute")

    def test_manifest_exposes_common_goal(self):
        manifest = room_manifest(initial_state())

        self.assertIn("humans and AI", manifest["common_goal"]["en"])
        self.assertIn("공동 학습", manifest["common_goal"]["ko"])
        self.assertEqual(manifest["room"]["common_goal"], manifest["common_goal"]["en"])

    def test_external_contribution_requires_content(self):
        with self.assertRaises(ValueError):
            accept_contribution(initial_state(), {"agent_id": "x", "content": ""})

    def test_external_contribution_is_appended(self):
        state, event = accept_contribution(initial_state(), {"agent_id": "x", "content": "test claim"})

        self.assertEqual(event["type"], "external_contribution")
        self.assertEqual(state["events"][-1]["content"], "test claim")


if __name__ == "__main__":
    unittest.main()
