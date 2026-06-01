import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agi_symposium.engine import initial_state
from agi_symposium.memory import ensure_research_memory
from agi_symposium.simulation import run_global_collaboration_simulation
from agi_symposium.storage import load_state, save_state


def memory_seed_state():
    state = initial_state()
    state["decisions"] = [
        {
            "id": "DEC-MEM",
            "axis": "persistent memory",
            "summary": "Retain verified decisions across restarts before selecting new work.",
        }
    ]
    state["verification_records"] = [
        {
            "claim": "Persistent memory should survive restarts.",
            "artifact": "state/symposium_state.json",
            "verifier": "memory-test",
            "result": "pass",
            "evidence": "Saved state was loaded again with the same research memory.",
            "hash": "hash-memory-pass",
        }
    ]
    return ensure_research_memory(state)


class MemoryTests(unittest.TestCase):
    def test_research_memory_survives_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with patch("agi_symposium.storage.STATE_DIR", root), patch(
                "agi_symposium.storage.STATE_PATH", root / "symposium_state.json"
            ), patch("agi_symposium.storage.TRANSCRIPT_PATH", root / "transcript.jsonl"), patch(
                "agi_symposium.storage.VERIFICATION_LEDGER_PATH", root / "verification_ledger.jsonl"
            ):
                save_state(memory_seed_state())
                loaded = load_state()

        self.assertEqual(loaded["research_memory"]["decisions"][0]["source"], "DEC-MEM")
        self.assertTrue(loaded["agi_milestone_evidence"]["persistent_state_survives_restart"])

    def test_simulation_reuses_research_memory_in_new_work_packet(self):
        state, _, _ = run_global_collaboration_simulation(memory_seed_state())

        references = state["simulation_runs"][0]["memory_references"]
        self.assertGreaterEqual(len(references), 1)
        self.assertEqual(references[0]["source"], "DEC-MEM")
        self.assertTrue(state["agi_milestone_evidence"]["memory_used_in_new_packet"])
        self.assertEqual(state["pr_drafts"][0]["memory_references"][0]["source"], "DEC-MEM")


if __name__ == "__main__":
    unittest.main()
