from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def canonical_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def hash_record(record: dict[str, Any]) -> str:
    body = {key: value for key, value in record.items() if key != "hash"}
    return hashlib.sha256(canonical_json(body).encode("utf-8")).hexdigest()


def make_verification_record(
    *,
    claim: str,
    artifact: str,
    verifier: str,
    result: str,
    evidence: str,
    previous_hash: str = "GENESIS",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if result not in {"pass", "fail", "needs-review"}:
        raise ValueError("result must be pass, fail, or needs-review")
    record = {
        "schema_version": "0.1",
        "created_at": now_iso(),
        "claim": claim.strip(),
        "artifact": artifact.strip(),
        "verifier": verifier.strip(),
        "result": result,
        "evidence": evidence.strip(),
        "previous_hash": previous_hash,
    }
    if metadata:
        record["metadata"] = metadata
    missing = [key for key in ("claim", "artifact", "verifier", "evidence") if not record[key]]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")
    record["hash"] = hash_record(record)
    return record


def read_ledger(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid ledger JSON at line {line_number}") from exc
    return records


def append_verification(path: Path, record: dict[str, Any]) -> dict[str, Any]:
    records = read_ledger(path)
    previous_hash = records[-1]["hash"] if records else "GENESIS"
    if record.get("previous_hash") != previous_hash:
        record = dict(record)
        record["previous_hash"] = previous_hash
        record["hash"] = hash_record(record)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return record


def verify_ledger(path: Path) -> list[str]:
    records = read_ledger(path)
    errors: list[str] = []
    previous_hash = "GENESIS"
    for index, record in enumerate(records, start=1):
        if record.get("previous_hash") != previous_hash:
            errors.append(f"line {index}: previous_hash mismatch")
        expected_hash = hash_record(record)
        if record.get("hash") != expected_hash:
            errors.append(f"line {index}: hash mismatch")
        previous_hash = str(record.get("hash") or "")
    return errors
