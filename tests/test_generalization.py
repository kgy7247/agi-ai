import unittest

from agi_symposium.engine import initial_state
from agi_symposium.generalization import (
    DEFAULT_GENERALIZATION_TASKS,
    run_generalization_eval_suite,
    run_generalization_task,
)
from agi_symposium.manifest import room_manifest
from agi_symposium.memory import ensure_research_memory


def generalization_seed_state():
    state = initial_state()
    state["decisions"] = [
        {
            "id": "DEC-GEN-MEM",
            "axis": "rollback safety memory",
            "summary": "Reuse prior rollback safety evidence when a new safety-memory task appears.",
        }
    ]
    return ensure_research_memory(state)


class GeneralizationTests(unittest.TestCase):
    def test_default_suite_passes_unseen_memory_tool_critique_and_safety_tasks(self):
        state = run_generalization_eval_suite(generalization_seed_state())
        run = state["generalization_eval_runs"][0]
        passed_ids = {
            status["id"] for status in state["agi_milestone_assessment"]["statuses"] if status["status"] == "pass"
        }

        self.assertEqual(run["task_count"], len(DEFAULT_GENERALIZATION_TASKS))
        self.assertEqual(run["failed"], 0)
        self.assertIn("M6", passed_ids)
        self.assertTrue(state["agi_milestone_evidence"]["unseen_memory_eval"])
        self.assertTrue(state["agi_milestone_evidence"]["unseen_tool_eval"])
        self.assertTrue(state["agi_milestone_evidence"]["unseen_safety_eval"])

    def test_memory_task_fails_without_prior_memory_reference(self):
        task = DEFAULT_GENERALIZATION_TASKS[0]
        result = run_generalization_task(initial_state(), task)

        self.assertFalse(result["passed"])
        self.assertEqual(result["references"], [])

    def test_unknown_task_type_fails_explicitly(self):
        result = run_generalization_task(
            generalization_seed_state(),
            {"id": "GEN-UNKNOWN", "category": "unknown", "type": "unknown"},
        )

        self.assertFalse(result["passed"])
        self.assertIn("No evaluator", result["evidence"])

    def test_manifest_exposes_generalization_eval_runs(self):
        state = run_generalization_eval_suite(generalization_seed_state())
        manifest = room_manifest(state)

        self.assertEqual(manifest["generalization_eval_runs"][0]["id"], "GEN-RUN-001")


if __name__ == "__main__":
    unittest.main()
