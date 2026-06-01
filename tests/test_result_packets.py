import tempfile
import unittest
from pathlib import Path

from agi_symposium.engine import accept_contribution, initial_state
from agi_symposium.identity import rebuild_hall_of_fame
from agi_symposium.result_packets import (
    import_result_packet,
    make_result_packet,
    read_result_packet,
    verify_result_packet,
    write_result_packet,
)
from agi_symposium.verification import append_verification, make_verification_record, read_ledger


class ResultPacketTests(unittest.TestCase):
    def test_make_result_packet_has_verifiable_hash(self):
        state, _ = accept_contribution(initial_state(), {"agent_id": "digital211-gpt5", "content": "artifact proposal"})
        record = make_verification_record(
            claim="proposal is recorded",
            artifact="/api/contribute",
            verifier="digital211-gpt5",
            result="pass",
            evidence="contribution event exists",
        )

        packet = make_result_packet(state, [record], contributor="digital211-gpt5")

        self.assertEqual(packet["contributor"], "digital211-gpt5")
        self.assertEqual(verify_result_packet(packet), [])
        self.assertTrue(packet["id"].startswith("RPK-"))
        self.assertEqual(len(packet["contributions"]), 1)
        self.assertEqual(len(packet["verification_records"]), 1)

    def test_verify_result_packet_detects_tampering(self):
        packet = make_result_packet(initial_state(), [], contributor="digital211-gpt5")
        packet["contributor"] = "edited-gpt5"

        self.assertIn("hash mismatch", verify_result_packet(packet))

    def test_write_and_read_result_packet(self):
        packet = make_result_packet(initial_state(), [], contributor="digital211-gpt5")
        with tempfile.TemporaryDirectory() as tmp:
            path = write_result_packet(packet, Path(tmp))
            loaded = read_result_packet(path)

        self.assertEqual(loaded["hash"], packet["hash"])

    def test_import_result_packet_updates_state_and_hall_of_fame(self):
        packet = make_result_packet(initial_state(), [], contributor="remote-llama3")
        state, event = import_result_packet(initial_state(), packet)
        state = rebuild_hall_of_fame(state, force=True)

        self.assertEqual(event["type"], "result_packet_import")
        self.assertEqual(state["result_packets"][0]["id"], packet["id"])
        self.assertEqual(state["hall_of_fame"][0]["display_name"], "remote-llama3")

    def test_import_result_packet_rejects_duplicate_hash(self):
        packet = make_result_packet(initial_state(), [], contributor="remote-llama3")
        state, _ = import_result_packet(initial_state(), packet)

        with self.assertRaisesRegex(ValueError, "already imported"):
            import_result_packet(state, packet)

    def test_result_packet_can_include_ledger_tip(self):
        with tempfile.TemporaryDirectory() as tmp:
            ledger_path = Path(tmp) / "ledger.jsonl"
            saved = append_verification(
                ledger_path,
                make_verification_record(
                    claim="tests pass",
                    artifact="tests",
                    verifier="digital211-gpt5",
                    result="pass",
                    evidence="unittest",
                ),
            )
            packet = make_result_packet(initial_state(), read_ledger(ledger_path), contributor="digital211-gpt5")

        self.assertEqual(packet["state_summary"]["ledger_tip"], saved["hash"])


if __name__ == "__main__":
    unittest.main()
