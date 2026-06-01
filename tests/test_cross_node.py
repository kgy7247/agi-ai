import unittest

from agi_symposium.cross_node import make_cross_node_review_records, reproduce_result_packet_across_nodes
from agi_symposium.engine import initial_state
from agi_symposium.manifest import room_manifest
from agi_symposium.result_packets import make_result_packet


class CrossNodeTests(unittest.TestCase):
    def test_two_independent_nodes_reproduce_valid_result_packet(self):
        packet = make_result_packet(initial_state(), [], contributor="digital211-gpt5")
        state = reproduce_result_packet_across_nodes(initial_state(), packet)
        run = state["cross_node_reproduction_runs"][0]
        passed_ids = {
            status["id"] for status in state["agi_milestone_assessment"]["statuses"] if status["status"] == "pass"
        }

        self.assertEqual(run["result"], "pass")
        self.assertEqual(len(run["reviewers"]), 2)
        self.assertEqual(len(run["verification_record_hashes"]), 2)
        self.assertEqual(state["verification_records"][0]["result"], "pass")
        self.assertEqual(state["verification_records"][1]["result"], "pass")
        self.assertIn("M5", passed_ids)

    def test_tampered_packet_creates_failed_independent_reviews(self):
        packet = make_result_packet(initial_state(), [], contributor="digital211-gpt5")
        packet["contributor"] = "tampered-node"
        state = reproduce_result_packet_across_nodes(initial_state(), packet)
        run = state["cross_node_reproduction_runs"][0]

        self.assertEqual(run["result"], "fail")
        self.assertIn("hash mismatch", run["errors"])
        self.assertEqual(state["verification_records"][0]["result"], "fail")
        self.assertEqual(state["verification_records"][1]["result"], "fail")

    def test_cross_node_review_records_are_hash_chained(self):
        packet = make_result_packet(initial_state(), [], contributor="digital211-gpt5")
        records = make_cross_node_review_records(
            packet,
            [
                {"id": "node-a", "node_type": "local_llm"},
                {"id": "node-b", "node_type": "hosted_llm"},
            ],
            [],
        )

        self.assertEqual(records[0]["previous_hash"], "GENESIS")
        self.assertEqual(records[1]["previous_hash"], records[0]["hash"])
        self.assertEqual(records[0]["metadata"]["kind"], "cross_node_reproduction")

    def test_manifest_exposes_cross_node_reproduction_runs(self):
        packet = make_result_packet(initial_state(), [], contributor="digital211-gpt5")
        state = reproduce_result_packet_across_nodes(initial_state(), packet)
        manifest = room_manifest(state)

        self.assertEqual(manifest["cross_node_reproduction_runs"][0]["id"], "XNODE-001")


if __name__ == "__main__":
    unittest.main()
