from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .identity import display_name, record_contribution
from .simulation import ensure_simulation_state
from .verification import canonical_json, hash_record


RESULT_PACKET_SCHEMA_VERSION = "0.1"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def packet_hash(packet: dict[str, Any]) -> str:
    body = {key: value for key, value in packet.items() if key not in {"id", "hash"}}
    return hash_record(body)


def make_result_packet(
    state: dict[str, Any],
    verification_records: list[dict[str, Any]],
    *,
    contributor: str | None = None,
) -> dict[str, Any]:
    state = ensure_simulation_state(state)
    contributor_id = (contributor or display_name(state["local_profile"])).strip()
    if not contributor_id:
        raise ValueError("contributor is required")

    events = [
        event
        for event in state.get("events", [])
        if event.get("agent_id") == contributor_id or event.get("contributor") == contributor_id
    ][-20:]
    records = [record for record in verification_records if record.get("verifier") == contributor_id][-20:]
    nodes = [node for node in state.get("ai_nodes", []) if node.get("id") == contributor_id]
    latest_ledger_hash = verification_records[-1]["hash"] if verification_records else "GENESIS"

    packet = {
        "schema_version": RESULT_PACKET_SCHEMA_VERSION,
        "created_at": now_iso(),
        "contributor": contributor_id,
        "node": nodes[-1] if nodes else {"id": contributor_id, "node_type": "unknown"},
        "state_summary": {
            "topic": state.get("topic"),
            "round": state.get("round", 0),
            "status": state.get("status", "idle"),
            "work_packets": state.get("work_packets", []),
            "scorecard": state.get("scorecard", {}),
            "ledger_tip": latest_ledger_hash,
        },
        "contributions": events,
        "verification_records": records,
    }
    packet["hash"] = packet_hash(packet)
    packet["id"] = f"RPK-{packet['hash'][:12]}"
    return packet


def verify_result_packet(packet: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ("schema_version", "created_at", "contributor", "state_summary", "hash", "id"):
        if key not in packet:
            errors.append(f"missing field: {key}")
    if packet.get("schema_version") != RESULT_PACKET_SCHEMA_VERSION:
        errors.append(f"unsupported schema_version: {packet.get('schema_version')}")
    if packet.get("hash") and packet_hash(packet) != packet.get("hash"):
        errors.append("hash mismatch")
    if packet.get("id") and packet.get("hash") and packet.get("id") != f"RPK-{str(packet['hash'])[:12]}":
        errors.append("id does not match hash")
    if not packet.get("contributor"):
        errors.append("contributor is required")
    return errors


def write_result_packet(packet: dict[str, Any], export_root: Path) -> Path:
    errors = verify_result_packet(packet)
    if errors:
        raise ValueError("; ".join(errors))
    packet_dir = export_root / "result-packets"
    packet_dir.mkdir(parents=True, exist_ok=True)
    packet_path = packet_dir / f"{packet['id']}.json"
    packet_path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return packet_path


def read_result_packet(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def import_result_packet(state: dict[str, Any], packet: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    errors = verify_result_packet(packet)
    if errors:
        raise ValueError("; ".join(errors))

    next_state = ensure_simulation_state(state)
    existing_packets = list(next_state.get("result_packets", []))
    if any(item.get("hash") == packet.get("hash") for item in existing_packets):
        raise ValueError(f"result packet already imported: {packet.get('id')}")

    summary = {
        "id": packet["id"],
        "hash": packet["hash"],
        "contributor": packet["contributor"],
        "created_at": packet["created_at"],
        "verification_count": len(packet.get("verification_records", [])),
        "contribution_count": len(packet.get("contributions", [])),
    }
    event = {
        "type": "result_packet_import",
        "round": int(next_state.get("round", 0)),
        "agent_id": packet["contributor"],
        "content": (
            f"Imported {packet['id']} with {summary['contribution_count']} contributions "
            f"and {summary['verification_count']} verification records."
        ),
        "packet_id": packet["id"],
        "packet_hash": packet["hash"],
        "created_at": now_iso(),
    }
    next_state["result_packets"] = (existing_packets + [summary])[-100:]
    next_state["events"] = (list(next_state.get("events", [])) + [event])[-100:]
    next_state = record_contribution(next_state, packet["contributor"], "result_packet_import")
    next_state["updated_at"] = now_iso()
    return next_state, event


def packet_to_canonical_text(packet: dict[str, Any]) -> str:
    return canonical_json(packet)
