import unittest

from agi_symposium.engine import initial_state
from agi_symposium.nodes import register_ai_node, sanitize_endpoint


class NodeTests(unittest.TestCase):
    def test_register_ai_node_adds_local_llm_node(self):
        state = register_ai_node(
            initial_state(),
            nickname="localbuilder7",
            ai_system="llama3",
            endpoint="http://localhost:11434",
        )

        node = state["ai_nodes"][-1]
        self.assertEqual(node["id"], "localbuilder7-llama3")
        self.assertEqual(node["node_type"], "local_llm")
        self.assertEqual(node["endpoint"], "http://127.0.0.1:11434")
        self.assertIn("verify", node["capabilities"])

    def test_register_ai_node_replaces_existing_node_record(self):
        state = initial_state()
        state = register_ai_node(state, nickname="node1", ai_system="llama3", endpoint="a")
        state = register_ai_node(state, nickname="node1", ai_system="llama3", endpoint="b")

        matching = [node for node in state["ai_nodes"] if node.get("id") == "node1-llama3"]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["endpoint"], "b")

    def test_sanitize_endpoint_has_local_fallback(self):
        self.assertEqual(sanitize_endpoint(""), "local")


if __name__ == "__main__":
    unittest.main()
