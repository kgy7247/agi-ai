import unittest

from agi_symposium.identity import (
    display_name,
    make_profile,
    rebuild_hall_of_fame,
    record_contribution,
)


class IdentityTests(unittest.TestCase):
    def test_make_profile_formats_nickname_and_ai_system(self):
        profile = make_profile("digital211", "gpt5")

        self.assertEqual(profile["nickname"], "digital211")
        self.assertEqual(profile["ai_system"], "gpt5")
        self.assertEqual(profile["display_name"], "digital211님의gpt5")
        self.assertEqual(display_name(profile), "digital211님의gpt5")

    def test_profile_sanitizes_unstable_characters(self):
        profile = make_profile("dig ital!!211", "gpt 5")

        self.assertEqual(profile["display_name"], "dig-ital-211님의gpt-5")

    def test_hall_of_fame_ranks_most_contributions(self):
        state = {}
        state = record_contribution(state, "digital211님의gpt5", "verification")
        state = record_contribution(state, "other님의claude", "verification")
        state = record_contribution(state, "digital211님의gpt5", "pr_draft")
        state = rebuild_hall_of_fame(state, force=True)

        self.assertEqual(state["hall_of_fame"][0]["display_name"], "digital211님의gpt5")
        self.assertEqual(state["hall_of_fame"][0]["total"], 2)


if __name__ == "__main__":
    unittest.main()

