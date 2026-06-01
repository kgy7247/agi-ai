from __future__ import annotations

import argparse
import json
from pathlib import Path

from .identity import rebuild_hall_of_fame
from .result_packets import (
    import_result_packet,
    make_result_packet,
    read_result_packet,
    verify_result_packet,
    write_result_packet,
)
from .storage import EXPORT_DIR, VERIFICATION_LEDGER_PATH, append_events, load_state, save_state
from .verification import read_ledger


def export_packet(contributor: str | None) -> dict:
    packet = make_result_packet(load_state(), read_ledger(VERIFICATION_LEDGER_PATH), contributor=contributor)
    path = write_result_packet(packet, EXPORT_DIR)
    return {"accepted": True, "packet": packet, "path": str(path)}


def verify_packet(path: Path) -> dict:
    packet = read_result_packet(path)
    errors = verify_result_packet(packet)
    return {"ok": not errors, "errors": errors, "packet_id": packet.get("id")}


def import_packet(path: Path) -> dict:
    packet = read_result_packet(path)
    state, event = import_result_packet(load_state(), packet)
    state = rebuild_hall_of_fame(state)
    save_state(state)
    append_events([event])
    return {"accepted": True, "event": event, "state": state}


def main() -> None:
    parser = argparse.ArgumentParser(description="Export, verify, or import AGI symposium result packets.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser("export")
    export_parser.add_argument("--contributor", default=None)

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("path")

    import_parser = subparsers.add_parser("import")
    import_parser.add_argument("path")

    args = parser.parse_args()
    if args.command == "export":
        result = export_packet(args.contributor)
    elif args.command == "verify":
        result = verify_packet(Path(args.path))
    else:
        result = import_packet(Path(args.path))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
