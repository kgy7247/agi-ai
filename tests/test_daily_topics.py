import unittest
from datetime import date

from agi_symposium.daily_topics import DAILY_AGI_TOPICS, TOPIC_START_DATE, ensure_daily_topic_state, topic_for_date
from agi_symposium.engine import initial_state, run_round
from agi_symposium.manifest import room_manifest


class DailyTopicTests(unittest.TestCase):
    def test_daily_topic_queue_has_exactly_100_topics(self):
        self.assertEqual(len(DAILY_AGI_TOPICS), 100)
        self.assertEqual(DAILY_AGI_TOPICS[0]["id"], "DAY-001")
        self.assertEqual(DAILY_AGI_TOPICS[-1]["id"], "DAY-100")

    def test_topic_for_date_rotates_one_topic_per_day(self):
        first = topic_for_date(TOPIC_START_DATE)
        second = topic_for_date(date(2026, 6, 2))

        self.assertEqual(first["id"], "DAY-001")
        self.assertEqual(second["id"], "DAY-002")
        self.assertNotEqual(first["question_ko"], second["question_ko"])

    def test_daily_topic_state_sets_one_open_question_and_absolute_condition(self):
        state = ensure_daily_topic_state({}, TOPIC_START_DATE)

        self.assertEqual(state["active_daily_topic"]["id"], "DAY-001")
        self.assertEqual(state["open_questions"], [state["active_daily_topic"]["question_ko"]])
        self.assertIn("인간과 환경과 AI", state["active_daily_topic"]["absolute_condition_ko"])
        self.assertEqual(state["daily_topic_policy"]["topic_count"], 100)

    def test_run_round_uses_active_daily_topic(self):
        state = ensure_daily_topic_state(initial_state(), TOPIC_START_DATE)
        next_state, events = run_round(state)

        self.assertEqual(next_state["decisions"][0]["axis"], state["active_daily_topic"]["capability"])
        self.assertTrue(any(state["active_daily_topic"]["question_ko"] in event["content"] for event in events))

    def test_manifest_exposes_daily_topic_and_absolute_condition(self):
        manifest = room_manifest(initial_state())

        self.assertIn("daily_topic_policy", manifest)
        self.assertIn("active_daily_topic", manifest)
        self.assertEqual(len(manifest["daily_topic_queue"]), 100)
        self.assertIn("environment", manifest["absolute_benefit_condition"]["en"])


if __name__ == "__main__":
    unittest.main()
