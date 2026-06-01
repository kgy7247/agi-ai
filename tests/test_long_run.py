import unittest

from agi_symposium.engine import initial_state
from agi_symposium.long_run import run_sustained_autonomy
from agi_symposium.manifest import room_manifest


def state_without_m7_evidence():
    state = initial_state()
    evidence = dict(state["agi_milestone_evidence"])
    for key in ("long_run_completed", "accepted_improvements", "rollback_and_override_verified"):
        evidence.pop(key, None)
    state["agi_milestone_evidence"] = evidence
    return state


class LongRunTests(unittest.TestCase):
    def test_sustained_autonomy_accepts_useful_improvements_and_rejects_failed_cycle(self):
        state = run_sustained_autonomy(initial_state())
        run = state["long_run_autonomy_runs"][0]
        decisions = [cycle["decision"] for cycle in run["cycles"]]
        passed_ids = {
            status["id"] for status in state["agi_milestone_assessment"]["statuses"] if status["status"] == "pass"
        }

        self.assertEqual(run["cycle_count"], 3)
        self.assertEqual(run["accepted_count"], 2)
        self.assertEqual(run["rejected_count"], 1)
        self.assertEqual(decisions, ["accepted", "accepted", "rejected"])
        self.assertEqual(len(run["rollback_snapshots"]), 3)
        self.assertTrue(all(check["human_override_available"] for check in run["human_override_checks"]))
        self.assertIn("M7", passed_ids)

    def test_sustained_autonomy_requires_human_override_for_acceptance(self):
        state = run_sustained_autonomy(
            state_without_m7_evidence(),
            permission_boundary={
                "id": "PB-NO-OVERRIDE",
                "allowed_actions": ["read_state", "run_in_process_check"],
                "denied_actions": ["network"],
                "human_override": False,
            },
        )
        run = state["long_run_autonomy_runs"][0]
        passed_ids = {
            status["id"] for status in state["agi_milestone_assessment"]["statuses"] if status["status"] == "pass"
        }

        self.assertEqual(run["accepted_count"], 0)
        self.assertNotIn("M7", passed_ids)
        self.assertFalse(state["agi_milestone_evidence"].get("rollback_and_override_verified", False))

    def test_manifest_exposes_long_run_autonomy_runs(self):
        state = run_sustained_autonomy(initial_state())
        manifest = room_manifest(state)

        self.assertEqual(manifest["long_run_autonomy_runs"][0]["id"], "LRUN-001")


if __name__ == "__main__":
    unittest.main()
