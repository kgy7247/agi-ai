import unittest

from agi_symposium.monitor import build_monitor_feed, build_seed_thought_feed


class MonitorTests(unittest.TestCase):
    def test_monitor_feed_shows_seed_thoughts_not_raw_participant_stream(self):
        state = {
            "round": 2,
            "updated_at": "2026-06-01T01:03:00+00:00",
            "events": [
                {
                    "type": "external_contribution",
                    "agent_id": "digital211-hermes3",
                    "content": "proposal",
                    "created_at": "2026-06-01T01:00:00+00:00",
                }
            ],
            "agi_seed": {
                "name": "Open AGI Seed",
                "maturity": {"questions_answered": 1, "evidence_backed_answers": 1, "topic_coverage": 1},
                "next_questions": ["current seed question"],
                "qa_records": [
                    {
                        "id": "SEED-A-0001",
                        "contributor": "digital211-hermes3",
                        "question": "q",
                        "answer": "a",
                        "evidence": "abcdef1234567890",
                        "result": "pass",
                        "created_at": "2026-06-01T01:01:00+00:00",
                    }
                ],
            },
        }
        records = [
            {
                "verifier": "digital211-hermes3",
                "claim": "same protocol",
                "evidence": "hash",
                "result": "pass",
                "hash": "abcdef1234567890",
                "created_at": "2026-06-01T01:02:00+00:00",
            }
        ]

        feed = build_monitor_feed(state, records)

        self.assertNotIn("external_contribution", [item["kind"] for item in feed])
        self.assertEqual([item["kind"] for item in feed], ["seed_answer", "seed_evidence", "seed_state", "seed_question"])
        self.assertEqual(feed[0]["record_id"], "SEED-A-0001")
        self.assertEqual(feed[1]["record_id"], "abcdef123456")
        self.assertIn("current seed question", feed[-1]["content"])

    def test_monitor_feed_applies_limit_to_latest_seed_messages(self):
        state = {
            "agi_seed": {
                "qa_records": [
                    {
                        "id": f"SEED-A-{index:04d}",
                        "contributor": "node",
                        "question": "q",
                        "answer": str(index),
                        "created_at": f"2026-06-01T00:{index:02d}:00+00:00",
                    }
                    for index in range(5)
                ]
            }
        }

        feed = build_seed_thought_feed(state, [], limit=2)

        self.assertEqual([item["record_id"] for item in feed], ["SEED-A-0003", "SEED-A-0004"])

    def test_seed_evidence_only_includes_records_linked_from_seed_answers(self):
        state = {
            "agi_seed": {
                "qa_records": [
                    {
                        "id": "SEED-A-0001",
                        "contributor": "node",
                        "question": "q",
                        "answer": "a",
                        "evidence": "linkedhash",
                        "created_at": "2026-06-01T00:01:00+00:00",
                    }
                ]
            }
        }
        records = [
            {"hash": "linkedhash", "claim": "linked", "created_at": "2026-06-01T00:02:00+00:00"},
            {"hash": "otherhash", "claim": "other", "created_at": "2026-06-01T00:03:00+00:00"},
        ]

        feed = build_seed_thought_feed(state, records)

        evidence = [item for item in feed if item["kind"] == "seed_evidence"]
        self.assertEqual(len(evidence), 1)
        self.assertIn("linked", evidence[0]["content"])


if __name__ == "__main__":
    unittest.main()
