import unittest

from agi_symposium.engine import initial_state
from agi_symposium.manifest import room_manifest
from agi_symposium.seed import answer_seed_question, ask_seed_question, ensure_seed_state


class SeedTests(unittest.TestCase):
    def test_initial_state_contains_public_agi_seed(self):
        state = initial_state()

        self.assertEqual(state["agi_seed"]["id"], "AGI-SEED-001")
        self.assertIn("next_questions", state["agi_seed"])
        self.assertEqual(state["agi_seed"]["maturity"]["questions_answered"], 0)

    def test_ask_seed_question_uses_active_daily_topic(self):
        initial = initial_state()
        state, question = ask_seed_question(initial, asked_by="digital211-hermes3")

        self.assertEqual(question["topic_id"], initial["active_daily_topic"]["id"])
        self.assertIn(initial["active_daily_topic"]["question_ko"], question["question"])
        self.assertEqual(state["agi_seed"]["next_questions"][0], question["question"])

    def test_answer_seed_question_records_growth_metrics_and_event(self):
        state = ensure_seed_state(initial_state())
        question = state["agi_seed"]["next_questions"][0]

        next_state, record = answer_seed_question(
            state,
            contributor="digital211-hermes3",
            question=question,
            answer="검증 가능한 후보 필터와 시뮬레이션 benchmark를 제안한다.",
            evidence="RPK-example",
            result="pass",
        )

        self.assertEqual(record["id"], "SEED-A-0001")
        self.assertEqual(next_state["agi_seed"]["maturity"]["questions_answered"], 1)
        self.assertEqual(next_state["agi_seed"]["maturity"]["evidence_backed_answers"], 1)
        self.assertEqual(next_state["events"][-1]["type"], "seed_answer")

    def test_manifest_exposes_seed_contract(self):
        manifest = room_manifest(initial_state())

        self.assertIn("agi_seed", manifest)
        self.assertEqual(manifest["entry_contract"]["read_agi_seed"], "GET /api/seed")
        self.assertEqual(manifest["entry_contract"]["answer_seed_question"], "POST /api/seed/answer")


if __name__ == "__main__":
    unittest.main()
