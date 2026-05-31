import tempfile
import unittest
from pathlib import Path

from agi_symposium.verification import (
    append_verification,
    make_verification_record,
    verify_ledger,
)


class VerificationTests(unittest.TestCase):
    def test_append_verification_creates_valid_hash_chain(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            first = make_verification_record(
                claim="tests pass",
                artifact="tests/test_engine.py",
                verifier="agent-a",
                result="pass",
                evidence="python -m unittest discover -v",
            )
            saved_first = append_verification(path, first)
            second = make_verification_record(
                claim="manifest exists",
                artifact="/room_manifest",
                verifier="agent-b",
                result="pass",
                evidence="GET /room_manifest returned 200",
            )
            saved_second = append_verification(path, second)

            self.assertEqual(saved_first["previous_hash"], "GENESIS")
            self.assertEqual(saved_second["previous_hash"], saved_first["hash"])
            self.assertEqual(verify_ledger(path), [])

    def test_verify_ledger_detects_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger.jsonl"
            record = make_verification_record(
                claim="original claim",
                artifact="artifact",
                verifier="agent-a",
                result="pass",
                evidence="evidence",
            )
            append_verification(path, record)
            text = path.read_text(encoding="utf-8").replace("original claim", "edited claim")
            path.write_text(text, encoding="utf-8")

            self.assertEqual(verify_ledger(path), ["line 1: hash mismatch"])


if __name__ == "__main__":
    unittest.main()
