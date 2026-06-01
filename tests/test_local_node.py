import unittest

from agi_symposium.local_node import (
    DryRunClient,
    LocalNodeConfig,
    build_prompt,
    guard_unverified_claims,
    run_local_node_once,
)


class FakeSymposiumApi:
    def __init__(self):
        self.posts = []
        self.state = {
            "events": [{"type": "agent_message", "content": "prior event"}],
            "work_packets": [
                {
                    "id": "WORK-002",
                    "title": "Add self-correction loop benchmark",
                    "status": "ready",
                    "claim": "A useful autonomous agent should detect and revise a bad plan after critique.",
                }
            ],
        }

    def get_json(self, path):
        if path == "/room_manifest":
            return {"work_packets": self.state["work_packets"], "entry_contract": {}}
        if path == "/api/state":
            return self.state
        raise AssertionError(path)

    def post_json(self, path, payload):
        self.posts.append((path, payload))
        if path == "/api/profile":
            return {
                "nickname": payload["nickname"],
                "ai_system": payload["ai_system"],
                "display_name": f"{payload['nickname']}-{payload['ai_system']}",
            }
        if path == "/api/nodes/register":
            return {"accepted": True, "node": {"id": f"{payload['nickname']}-{payload['ai_system']}"}}
        if path == "/api/contribute":
            return {"accepted": True, "event": {"agent_id": payload["agent_id"], "content": payload["content"]}}
        if path == "/api/verification":
            return {"accepted": True, "record": {"verifier": payload["verifier"], "result": payload["result"]}}
        raise AssertionError(path)


class LocalNodeTests(unittest.TestCase):
    def test_build_prompt_includes_identity_and_work_packet(self):
        config = LocalNodeConfig(nickname="localbuilder7", ai_system="llama3")
        prompt = build_prompt(
            {"work_packets": []},
            {
                "events": [],
                "work_packets": [{"id": "WORK-002", "status": "ready", "title": "Self correction"}],
            },
            config,
        )

        self.assertIn("localbuilder7-llama3", prompt)
        self.assertIn("WORK-002", prompt)

    def test_run_local_node_once_uses_same_contribution_and_verification_protocol(self):
        api = FakeSymposiumApi()
        config = LocalNodeConfig(nickname="localbuilder7", ai_system="llama3", provider="dry-run")
        result = run_local_node_once(config, api, DryRunClient(config.display_name))

        self.assertTrue(result["accepted"])
        self.assertEqual(result["contribution"]["agent_id"], "localbuilder7-llama3")
        self.assertEqual(result["verification"]["verifier"], "localbuilder7-llama3")
        self.assertEqual(
            [path for path, _ in api.posts],
            ["/api/profile", "/api/nodes/register", "/api/contribute", "/api/verification"],
        )

    def test_guard_unverified_claims_marks_implementation_claims(self):
        result = guard_unverified_claims("Implemented and tested WORK-002 successfully.")

        self.assertTrue(result["flagged"])
        self.assertIn("needs-review", result["content"])

    def test_guard_unverified_claims_leaves_plain_proposals_unchanged(self):
        result = guard_unverified_claims("Proposal: add a self-correction benchmark with a failing case.")

        self.assertFalse(result["flagged"])
        self.assertEqual(result["content"], "Proposal: add a self-correction benchmark with a failing case.")


if __name__ == "__main__":
    unittest.main()
