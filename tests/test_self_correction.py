import unittest

from agi_symposium.self_correction import detect_gaps, revise_plan_after_critique, score_revision


class SelfCorrectionBenchmarkTests(unittest.TestCase):
    def test_detects_gaps_named_by_critique(self):
        gaps = detect_gaps(
            ["Discuss a self-correction idea in the next symposium round."],
            "The plan has no test, no artifact, and no pass/fail failure criteria.",
        )

        self.assertEqual(gaps, ["missing_test", "missing_artifact", "missing_failure_criteria"])

    def test_revises_bad_plan_after_critique(self):
        result = revise_plan_after_critique(
            ["Discuss a self-correction idea in the next symposium round."],
            "The plan has no test, no artifact, no verification evidence, and no failure criteria.",
        )

        self.assertTrue(result.passed)
        self.assertEqual(result.score, 100)
        self.assertEqual(
            result.addressed_gaps,
            ["missing_test", "missing_artifact", "missing_failure_criteria", "missing_verification"],
        )
        self.assertTrue(any("failing test" in step for step in result.revised_plan))
        self.assertTrue(any("artifact path" in step for step in result.revised_plan))
        self.assertTrue(any("pass/fail criteria" in step for step in result.revised_plan))
        self.assertTrue(any("independent verification" in step for step in result.revised_plan))

    def test_existing_good_plan_has_no_detected_gaps(self):
        result = revise_plan_after_critique(
            [
                "Add tests/test_self_correction.py.",
                "Define pass/fail criteria for the critique response.",
                "Record verification evidence from python -m unittest discover -v.",
            ],
            "Check that the test, artifact, failure criteria, and verification evidence are present.",
        )

        self.assertEqual(result.detected_gaps, [])
        self.assertEqual(result.score, 100)
        self.assertFalse(result.passed)

    def test_score_revision_is_partial_when_some_gaps_remain(self):
        self.assertEqual(score_revision(["missing_test", "missing_artifact"], ["missing_test"]), 50)

    def test_requires_non_empty_inputs(self):
        with self.assertRaisesRegex(ValueError, "plan_steps"):
            revise_plan_after_critique([], "missing test")
        with self.assertRaisesRegex(ValueError, "critique"):
            revise_plan_after_critique(["add a test"], "")


if __name__ == "__main__":
    unittest.main()
