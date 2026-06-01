import unittest

from agi_symposium.autonomy import (
    DEFAULT_AUTONOMOUS_EXPERIMENT,
    check_permission_boundary,
    run_bounded_autonomous_experiment,
    run_in_process_tool_failure_probe,
)
from agi_symposium.engine import initial_state
from agi_symposium.manifest import room_manifest


class AutonomyTests(unittest.TestCase):
    def test_in_process_probe_confirms_failed_tool_becomes_failed_evidence(self):
        measurement = run_in_process_tool_failure_probe()

        self.assertTrue(measurement["ok"])
        self.assertEqual(measurement["record_result"], "fail")
        self.assertIn("intentional failure", measurement["evidence"])

    def test_permission_boundary_rejects_missing_actions(self):
        result = check_permission_boundary(
            DEFAULT_AUTONOMOUS_EXPERIMENT,
            {
                "id": "PB-TOO-SMALL",
                "allowed_actions": ["read_state"],
                "human_override": True,
            },
        )

        self.assertFalse(result["ok"])
        self.assertIn("run_in_process_check", result["missing_actions"])

    def test_bounded_experiment_records_boundary_result_and_next_action(self):
        state = run_bounded_autonomous_experiment(initial_state())
        run = state["autonomous_experiment_runs"][0]
        passed_ids = {
            status["id"] for status in state["agi_milestone_assessment"]["statuses"] if status["status"] == "pass"
        }

        self.assertEqual(run["result"], "pass")
        self.assertEqual(run["next_action"], "prepare_cross_node_reproducibility_packet")
        self.assertTrue(run["permission_check"]["ok"])
        self.assertIn("M4", passed_ids)

    def test_blocked_experiment_still_records_boundary_and_next_action(self):
        state = run_bounded_autonomous_experiment(
            initial_state(),
            permission_boundary={
                "id": "PB-BLOCK",
                "tier": "local-in-process",
                "allowed_actions": ["read_state"],
                "denied_actions": ["run_in_process_check"],
                "human_override": True,
            },
        )
        run = state["autonomous_experiment_runs"][0]

        self.assertEqual(run["result"], "blocked")
        self.assertEqual(run["next_action"], "tighten_permission_boundary_or_select_smaller_experiment")
        self.assertFalse(run["permission_check"]["ok"])

    def test_manifest_exposes_autonomous_experiment_runs(self):
        state = run_bounded_autonomous_experiment(initial_state())
        manifest = room_manifest(state)

        self.assertEqual(manifest["autonomous_experiment_runs"][0]["id"], "AUTO-RUN-001")
        self.assertEqual(manifest["permission_boundaries"][0]["id"], "PB-LOCAL-001")


if __name__ == "__main__":
    unittest.main()
