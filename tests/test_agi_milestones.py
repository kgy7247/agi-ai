import unittest

from agi_symposium.agi_milestones import MILESTONES, assess_milestones, demo_evidence
from agi_symposium.engine import initial_state
from agi_symposium.manifest import room_manifest


class AgiMilestoneTests(unittest.TestCase):
    def test_demo_evidence_completes_initial_milestones_but_not_agi_candidate(self):
        assessment = assess_milestones(demo_evidence())
        passed_ids = {status["id"] for status in assessment["statuses"] if status["status"] == "pass"}

        self.assertIn("M0", passed_ids)
        self.assertIn("M1", passed_ids)
        self.assertIn("M2", passed_ids)
        self.assertIn("M3", passed_ids)
        self.assertIn("M4", passed_ids)
        self.assertIn("M5", passed_ids)
        self.assertIn("M6", passed_ids)
        self.assertIn("M7", passed_ids)
        self.assertFalse(assessment["agi_candidate"])

    def test_all_required_evidence_marks_agi_candidate(self):
        evidence = {
            key: True
            for milestone in MILESTONES
            for key in milestone.evidence_keys
            if key != "all_previous_milestones_pass"
        }

        assessment = assess_milestones(evidence)

        self.assertTrue(assessment["agi_candidate"])
        self.assertEqual(assessment["passed"], assessment["total"])

    def test_missing_evidence_lists_blockers(self):
        assessment = assess_milestones({"public_repo": True})
        m0 = next(status for status in assessment["statuses"] if status["id"] == "M0")

        self.assertEqual(m0["status"], "blocked")
        self.assertIn("clean_clone_run", m0["missing_evidence"])
        self.assertIn("local_llm_node_pass", m0["missing_evidence"])

    def test_room_manifest_exposes_milestones_for_external_agents(self):
        manifest = room_manifest(initial_state())

        self.assertIn("agi_milestones", manifest)
        self.assertIn("agi_milestone_assessment", manifest)
        self.assertEqual(manifest["agi_milestones"][0]["id"], "M0")


if __name__ == "__main__":
    unittest.main()
