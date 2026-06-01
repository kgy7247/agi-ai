import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agi_symposium.public_monitor import build_public_monitor_snapshot, write_public_monitor_snapshot


class PublicMonitorTests(unittest.TestCase):
    def test_public_monitor_snapshot_contains_only_public_seed_view(self):
        state = {
            "updated_at": "2026-06-01T00:00:00+00:00",
            "round": 1,
            "active_daily_topic": {
                "id": "DAY-001",
                "title_ko": "태양광 발전효율 상승",
                "question_ko": "question",
                "absolute_condition_ko": "benefit all",
            },
            "agi_seed": {
                "id": "AGI-SEED-001",
                "name": "Open AGI Seed",
                "purpose_ko": "seed purpose",
                "maturity": {"questions_answered": 1},
                "qa_records": [
                    {
                        "id": "SEED-A-0001",
                        "contributor": "digital211-hermes3",
                        "question": "q",
                        "answer": "a",
                        "evidence": "hash123",
                        "created_at": "2026-06-01T00:01:00+00:00",
                    }
                ],
            },
        }
        ledger = [{"hash": "hash123", "claim": "claim", "created_at": "2026-06-01T00:02:00+00:00"}]

        with patch("agi_symposium.public_monitor.load_state", return_value=state), patch(
            "agi_symposium.public_monitor.read_ledger", return_value=ledger
        ), patch("agi_symposium.public_monitor.verify_ledger", return_value=[]):
            snapshot = build_public_monitor_snapshot()

        self.assertEqual(snapshot["agi_seed"]["id"], "AGI-SEED-001")
        self.assertEqual(snapshot["active_daily_topic"]["id"], "DAY-001")
        self.assertEqual([message["kind"] for message in snapshot["messages"]], ["seed_state", "seed_answer", "seed_evidence"])
        self.assertNotIn("events", snapshot)

    def test_write_public_monitor_snapshot_writes_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "public-monitor.json"
            with patch(
                "agi_symposium.public_monitor.build_public_monitor_snapshot",
                return_value={"schema_version": "0.1", "messages": []},
            ):
                write_public_monitor_snapshot(path)

            self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["schema_version"], "0.1")


if __name__ == "__main__":
    unittest.main()
