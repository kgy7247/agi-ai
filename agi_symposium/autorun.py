from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import request
from urllib.parse import urlparse

from .identity import display_name, make_profile
from .local_node import (
    DEFAULT_OLLAMA_ENDPOINT,
    DEFAULT_SERVER_URL,
    HttpSymposiumApi,
    LocalNodeConfig,
    make_llm_client,
    run_local_node_once,
)
from .server import is_local_host
from .storage import STATE_DIR


AUTORUN_LOG_PATH = STATE_DIR / "autorun_runs.jsonl"


@dataclass(frozen=True)
class AutoRunConfig:
    nickname: str
    ai_system: str
    server_url: str = DEFAULT_SERVER_URL
    provider: str = "ollama"
    endpoint: str = DEFAULT_OLLAMA_ENDPOINT
    model: str = "llama3"
    mode: str = "daily-topic-autopilot"
    interval_seconds: int = 3600
    max_cycles: int | None = None
    export_result_packet: bool = True

    @property
    def display_name(self) -> str:
        return display_name(make_profile(self.nickname, self.ai_system))

    def local_node_config(self) -> LocalNodeConfig:
        return LocalNodeConfig(
            nickname=self.nickname,
            ai_system=self.ai_system,
            server_url=self.server_url,
            provider=self.provider,
            endpoint=self.endpoint,
            model=self.model,
            mode=self.mode,
        )


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def server_is_available(server_url: str, timeout: float = 2.0) -> bool:
    try:
        with request.urlopen(f"{server_url.rstrip('/')}/api/state", timeout=timeout) as response:
            return 200 <= response.status < 300
    except OSError:
        return False


def start_local_server(server_url: str) -> subprocess.Popen[str]:
    parsed = urlparse(server_url)
    host = parsed.hostname or "127.0.0.1"
    if not is_local_host(host):
        raise ValueError("autorun can only start a local server")
    port = str(parsed.port or 8787)
    return subprocess.Popen(
        [sys.executable, "-m", "agi_symposium.server", "--host", host, "--port", port],
        cwd=Path(__file__).resolve().parents[1],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True,
    )


def wait_for_server(server_url: str, timeout_seconds: float = 10.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if server_is_available(server_url):
            return
        time.sleep(0.25)
    raise TimeoutError(f"server did not become available: {server_url}")


def run_autorun_cycle(
    config: AutoRunConfig,
    api: HttpSymposiumApi | None = None,
    llm: Any | None = None,
) -> dict[str, Any]:
    api = api or HttpSymposiumApi(config.server_url)
    node_config = config.local_node_config()
    llm = llm or make_llm_client(node_config)

    started_at = now_iso()
    node_result = run_local_node_once(node_config, api, llm)
    seed = api.get_json("/api/seed")
    seed_questions = list(seed.get("next_questions") or [])
    seed_answer: dict[str, Any] | None = None
    if seed_questions:
        seed_answer = api.post_json(
            "/api/seed/answer",
            {
                "contributor": config.display_name,
                "question": seed_questions[0],
                "answer": node_result.get("contribution", {}).get("content") or "",
                "evidence": node_result.get("verification", {}).get("hash") or "/api/verification",
                "result": "needs-review" if node_result.get("content_guard", {}).get("flagged") else "pass",
            },
        )
    export_result: dict[str, Any] | None = None
    if config.export_result_packet:
        export_result = api.post_json("/api/result-packets/export", {"contributor": config.display_name})
    hall_of_fame = api.post_json("/api/hall-of-fame/rebuild", {})
    state = api.get_json("/api/state")
    active_topic = state.get("active_daily_topic") or {}

    record = {
        "schema_version": "0.1",
        "created_at": started_at,
        "status": "pass",
        "contributor": config.display_name,
        "active_daily_topic_id": active_topic.get("id"),
        "contribution_type": node_result.get("contribution", {}).get("type"),
        "verification_hash": node_result.get("verification", {}).get("hash"),
        "result_packet_id": (export_result or {}).get("packet", {}).get("id"),
        "seed_answer_id": (seed_answer or {}).get("record", {}).get("id"),
        "hall_of_fame_rank": find_rank(hall_of_fame.get("hall_of_fame", []), config.display_name),
        "content_guard": node_result.get("content_guard", {}),
    }
    append_autorun_record(record)
    return record


def find_rank(hall_of_fame: list[dict[str, Any]], display_name_value: str) -> int | None:
    for row in hall_of_fame:
        if row.get("display_name") == display_name_value:
            return int(row.get("rank", 0) or 0)
    return None


def append_autorun_record(record: dict[str, Any]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with AUTORUN_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def run_autorun_loop(config: AutoRunConfig, *, start_server: bool = False) -> list[dict[str, Any]]:
    server_process: subprocess.Popen[str] | None = None
    if start_server and not server_is_available(config.server_url):
        server_process = start_local_server(config.server_url)
        wait_for_server(config.server_url)
    elif not server_is_available(config.server_url):
        raise RuntimeError(f"server is not available: {config.server_url}")

    records: list[dict[str, Any]] = []
    try:
        cycle = 0
        while config.max_cycles is None or cycle < config.max_cycles:
            records.append(run_autorun_cycle(config))
            cycle += 1
            if config.max_cycles is not None and cycle >= config.max_cycles:
                break
            time.sleep(max(1, config.interval_seconds))
    finally:
        if server_process is not None:
            server_process.terminate()
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a self-updating local AGI symposium node loop.")
    parser.add_argument("--nickname", required=True)
    parser.add_argument("--ai-system", required=True)
    parser.add_argument("--server-url", default=DEFAULT_SERVER_URL)
    parser.add_argument("--provider", choices=["ollama", "openai-compatible", "dry-run"], default="ollama")
    parser.add_argument("--endpoint", default=DEFAULT_OLLAMA_ENDPOINT)
    parser.add_argument("--model", default=None)
    parser.add_argument("--mode", default="daily-topic-autopilot")
    parser.add_argument("--interval-seconds", type=int, default=3600)
    parser.add_argument("--max-cycles", type=int, default=None)
    parser.add_argument("--start-server", action="store_true")
    parser.add_argument("--no-export", action="store_true")
    args = parser.parse_args()

    config = AutoRunConfig(
        nickname=args.nickname,
        ai_system=args.ai_system,
        server_url=args.server_url,
        provider=args.provider,
        endpoint=args.endpoint,
        model=args.model or args.ai_system,
        mode=args.mode,
        interval_seconds=args.interval_seconds,
        max_cycles=args.max_cycles,
        export_result_packet=not args.no_export,
    )
    records = run_autorun_loop(config, start_server=args.start_server)
    print(json.dumps({"records": records}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
