import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agi_symposium import autorun
from agi_symposium.local_node import DryRunClient, LocalNodeConfig


class FakeAutoRunApi:
    def __init__(self):
        self.posts = []
        self.state = {
            "active_daily_topic": {"id": "DAY-001"},
            "events": [],
            "work_packets": [],
        }

    def get_json(self, path):
        if path == "/room_manifest":
            return {"active_daily_topic": {"id": "DAY-001"}, "work_packets": []}
        if path == "/api/state":
            return self.state
        if path == "/api/seed":
            return {"next_questions": ["DAY-001 seed question"]}
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
            return {"accepted": True, "event": {"type": "external_contribution", **payload}}
        if path == "/api/verification":
            return {"accepted": True, "record": {"verifier": payload["verifier"], "hash": "abc123"}}
        if path == "/api/result-packets/export":
            return {"accepted": True, "packet": {"id": "RPK-abc123"}}
        if path == "/api/seed/answer":
            return {"accepted": True, "record": {"id": "SEED-A-0001"}}
        if path == "/api/hall-of-fame/rebuild":
            return {
                "hall_of_fame": [
                    {"rank": 1, "display_name": payload.get("display_name", "digital211-hermes3")},
                    {"rank": 2, "display_name": "other-node"},
                ]
            }
        raise AssertionError(path)


class AutoRunTests(unittest.TestCase):
    def test_autorun_cycle_posts_contribution_exports_packet_and_rebuilds_ranking(self):
        api = FakeAutoRunApi()
        config = autorun.AutoRunConfig(nickname="digital211", ai_system="hermes3", provider="dry-run", model="hermes3")
        node_config = LocalNodeConfig(nickname="digital211", ai_system="hermes3")

        with tempfile.TemporaryDirectory() as tmp:
            log_path = Path(tmp) / "autorun_runs.jsonl"
            with patch("agi_symposium.autorun.AUTORUN_LOG_PATH", log_path), patch(
                "agi_symposium.autorun.STATE_DIR", Path(tmp)
            ), patch("agi_symposium.autorun.write_public_monitor_snapshot", return_value={"messages": [{"kind": "seed_state"}]}):
                record = autorun.run_autorun_cycle(config, api, DryRunClient(node_config.display_name))

        self.assertEqual(record["status"], "pass")
        self.assertEqual(record["contributor"], "digital211-hermes3")
        self.assertEqual(record["active_daily_topic_id"], "DAY-001")
        self.assertEqual(record["result_packet_id"], "RPK-abc123")
        self.assertEqual(record["seed_answer_id"], "SEED-A-0001")
        self.assertEqual(record["public_monitor_messages"], 1)
        self.assertEqual(record["public_monitor_publish"]["status"], "disabled")
        self.assertIn("/api/seed/answer", [path for path, _ in api.posts])
        self.assertIn("/api/result-packets/export", [path for path, _ in api.posts])
        self.assertIn("/api/hall-of-fame/rebuild", [path for path, _ in api.posts])

    def test_find_rank_returns_none_when_contributor_is_absent(self):
        self.assertIsNone(autorun.find_rank([{"rank": 1, "display_name": "other"}], "digital211-hermes3"))

    def test_publish_public_monitor_snapshot_commits_and_pushes_changed_snapshot(self):
        calls = []

        def fake_run_git(args):
            calls.append(args)
            if args[0] == "status":
                return autorun.subprocess.CompletedProcess(["git", *args], 0, stdout=" M docs/public-monitor.json\n", stderr="")
            if args[0] == "add":
                return autorun.subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")
            if args[0] == "commit":
                return autorun.subprocess.CompletedProcess(
                    ["git", *args],
                    0,
                    stdout="[main abc1234] Auto-refresh public seed monitor\n 1 file changed\n",
                    stderr="",
                )
            if args[0] == "push":
                return autorun.subprocess.CompletedProcess(["git", *args], 0, stdout="", stderr="")
            raise AssertionError(args)

        with patch("agi_symposium.autorun.run_git", side_effect=fake_run_git):
            result = autorun.publish_public_monitor_snapshot()

        self.assertEqual(result["status"], "published")
        self.assertEqual(result["path"], "docs/public-monitor.json")
        self.assertEqual([call[0] for call in calls], ["status", "add", "commit", "push"])

    def test_publish_public_monitor_snapshot_skips_when_unchanged(self):
        with patch(
            "agi_symposium.autorun.run_git",
            return_value=autorun.subprocess.CompletedProcess(["git", "status"], 0, stdout="", stderr=""),
        ) as run_git:
            result = autorun.publish_public_monitor_snapshot()

        self.assertEqual(result["status"], "no-change")
        self.assertEqual(run_git.call_count, 1)


if __name__ == "__main__":
    unittest.main()
