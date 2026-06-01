import unittest

from agi_symposium.monitor import build_monitor_feed


class MonitorTests(unittest.TestCase):
    def test_monitor_feed_combines_events_seed_answers_and_verification(self):
        state = {
            "round": 2,
            "events": [
                {
                    "type": "external_contribution",
                    "agent_id": "digital211-hermes3",
                    "content": "proposal",
                    "created_at": "2026-06-01T01:00:00+00:00",
                }
            ],
            "agi_seed": {
                "qa_records": [
                    {
                        "id": "SEED-A-0001",
                        "contributor": "digital211-hermes3",
                        "question": "q",
                        "answer": "a",
                        "evidence": "RPK-1",
                        "result": "pass",
                        "created_at": "2026-06-01T01:01:00+00:00",
                    }
                ]
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

        self.assertEqual([item["kind"] for item in feed], ["external_contribution", "seed_qa", "verification"])
        self.assertEqual(feed[1]["record_id"], "SEED-A-0001")
        self.assertEqual(feed[2]["record_id"], "abcdef123456")

    def test_monitor_feed_applies_limit_to_latest_messages(self):
        state = {
            "events": [
                {"type": "event", "agent_id": str(index), "content": str(index), "created_at": f"2026-06-01T00:{index:02d}:00+00:00"}
                for index in range(5)
            ]
        }

        feed = build_monitor_feed(state, [], limit=2)

        self.assertEqual([item["content"] for item in feed], ["3", "4"])


if __name__ == "__main__":
    unittest.main()
