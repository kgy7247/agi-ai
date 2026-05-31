import unittest

from agi_symposium.identity import (
    display_name,
    ensure_identity_state,
    make_profile,
    rebuild_hall_of_fame,
    record_contribution,
    set_local_profile,
)


class IdentityTests(unittest.TestCase):
    def test_make_profile_formats_nickname_and_ai_system(self):
        profile = make_profile("digital211", "gpt5")

        self.assertEqual(profile["nickname"], "digital211")
        self.assertEqual(profile["ai_system"], "gpt5")
        self.assertEqual(profile["display_name"], "digital211-gpt5")
        self.assertEqual(display_name(profile), "digital211-gpt5")

    def test_profile_sanitizes_to_ascii_characters(self):
        profile = make_profile("dig ital!!211한글", "gpt 5")

        self.assertEqual(profile["display_name"], "dig-ital-211-gpt-5")

    def test_hall_of_fame_ranks_most_contributions(self):
        state = {}
        state = record_contribution(state, "digital211-gpt5", "verification")
        state = record_contribution(state, "other-claude", "verification")
        state = record_contribution(state, "digital211-gpt5", "pr_draft")
        state = rebuild_hall_of_fame(state, force=True)

        self.assertEqual(state["hall_of_fame"][0]["display_name"], "digital211-gpt5")
        self.assertEqual(state["hall_of_fame"][0]["total"], 2)

    def test_duplicate_nickname_is_rejected(self):
        state = ensure_identity_state(
            {
                "local_profile": make_profile("digital211", "gpt5"),
                "registered_nicknames": {
                    "taken": {
                        "display_name": "taken-claude",
                        "owner": "remote",
                        "updated_at": "2026-01-01T00:00:00+00:00",
                    }
                },
            }
        )

        with self.assertRaisesRegex(ValueError, "nickname already registered: taken"):
            set_local_profile(state, "taken", "gpt5")

    def test_current_nickname_can_change_ai_system(self):
        state = ensure_identity_state({"local_profile": make_profile("digital211", "gpt5")})
        state = set_local_profile(state, "digital211", "claude")

        self.assertEqual(state["local_profile"]["display_name"], "digital211-claude")
        self.assertEqual(state["registered_nicknames"]["digital211"]["display_name"], "digital211-claude")

    def test_previous_local_nickname_stays_reserved_after_change(self):
        state = ensure_identity_state({"local_profile": make_profile("digital211", "gpt5")})
        state = set_local_profile(state, "newname", "gpt5")

        self.assertEqual(state["registered_nicknames"]["digital211"]["owner"], "local")
        self.assertEqual(state["registered_nicknames"]["newname"]["owner"], "local")


if __name__ == "__main__":
    unittest.main()
