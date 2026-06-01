import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agi_symposium import server


class ServerSecurityTests(unittest.TestCase):
    def test_non_local_host_requires_explicit_network_flag(self):
        self.assertTrue(server.is_local_host("127.0.0.1"))
        self.assertTrue(server.is_local_host("localhost"))
        self.assertTrue(server.is_local_host("[::1]"))
        self.assertFalse(server.is_local_host("0.0.0.0"))

    def test_result_packet_import_path_must_stay_under_exports(self):
        with tempfile.TemporaryDirectory() as tmp:
            export_dir = Path(tmp) / "exports"
            export_dir.mkdir()
            packet = export_dir / "result-packets" / "RPK-safe.json"
            packet.parent.mkdir()
            packet.write_text("{}", encoding="utf-8")

            with patch("agi_symposium.server.EXPORT_DIR", export_dir):
                self.assertEqual(server.resolve_result_packet_import_path(str(packet)), packet.resolve())
                with self.assertRaises(ValueError):
                    server.resolve_result_packet_import_path(str(Path(tmp) / "outside.json"))


if __name__ == "__main__":
    unittest.main()
