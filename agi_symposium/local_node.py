from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Any, Protocol
from urllib import request
from urllib.error import HTTPError

from .identity import display_name, make_profile


DEFAULT_SERVER_URL = "http://127.0.0.1:8787"
DEFAULT_OLLAMA_ENDPOINT = "http://127.0.0.1:11434"
DEFAULT_OPENAI_COMPATIBLE_ENDPOINT = "http://127.0.0.1:1234/v1"


class SymposiumApi(Protocol):
    def get_json(self, path: str) -> dict[str, Any]:
        ...

    def post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        ...


class LLMClient(Protocol):
    def complete(self, prompt: str) -> str:
        ...


@dataclass(frozen=True)
class LocalNodeConfig:
    nickname: str
    ai_system: str
    server_url: str = DEFAULT_SERVER_URL
    provider: str = "ollama"
    endpoint: str = DEFAULT_OLLAMA_ENDPOINT
    model: str = "llama3"
    mode: str = "debate"

    @property
    def display_name(self) -> str:
        return display_name(make_profile(self.nickname, self.ai_system))


class HttpSymposiumApi:
    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip("/")

    def get_json(self, path: str) -> dict[str, Any]:
        return self._request("GET", path, None)

    def post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", path, payload)

    def _request(self, method: str, path: str, payload: dict[str, Any] | None) -> dict[str, Any]:
        data = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = request.Request(f"{self.server_url}{path}", data=data, headers=headers, method=method)
        try:
            with request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"{method} {path} failed: {exc.code} {body}") from exc


class OllamaClient:
    def __init__(self, endpoint: str, model: str):
        self.endpoint = endpoint.rstrip("/")
        self.model = model

    def complete(self, prompt: str) -> str:
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        req = request.Request(
            f"{self.endpoint}/api/generate",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=120) as response:
            body = json.loads(response.read().decode("utf-8"))
        return str(body.get("response") or "").strip()


class OpenAICompatibleClient:
    def __init__(self, endpoint: str, model: str):
        self.endpoint = endpoint.rstrip("/")
        self.model = model

    def complete(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a contributor node in an AGI symposium."},
                {"role": "user", "content": prompt},
            ],
            "stream": False,
        }
        req = request.Request(
            f"{self.endpoint}/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        with request.urlopen(req, timeout=120) as response:
            body = json.loads(response.read().decode("utf-8"))
        choices = body.get("choices") or []
        if not choices:
            return ""
        message = choices[0].get("message") or {}
        return str(message.get("content") or "").strip()


class DryRunClient:
    def __init__(self, display_name_value: str):
        self.display_name_value = display_name_value

    def complete(self, prompt: str) -> str:
        return (
            f"{self.display_name_value} dry-run contribution: selected one work packet, "
            "requires a reproducible artifact, a verifier, and a pass/fail command before merge."
        )


def build_prompt(manifest: dict[str, Any], state: dict[str, Any], config: LocalNodeConfig) -> str:
    work_packets = state.get("work_packets") or manifest.get("work_packets") or []
    ready_packets = [packet for packet in work_packets if packet.get("status") in {"ready", "needs-review"}]
    selected_packet = ready_packets[0] if ready_packets else (work_packets[0] if work_packets else {})
    recent_events = list(state.get("events", []))[-8:]
    return "\n".join(
        [
            "You are participating as an equal node in AGI Autonomous Symposium.",
            f"Display name: {config.display_name}",
            f"Node type: local_llm",
            f"Mode: {config.mode}",
            "",
            "Rules:",
            "- Do not claim AGI progress without an artifact, test, or measurable evidence.",
            "- Prefer one concrete next step over broad philosophy.",
            "- Mention the work packet ID you are addressing.",
            "- Keep the response under 1200 characters.",
            "",
            "Selected work packet:",
            json.dumps(selected_packet, ensure_ascii=False, indent=2),
            "",
            "Recent events:",
            json.dumps(recent_events, ensure_ascii=False, indent=2),
            "",
            "Return a contribution message that can be posted to /api/contribute.",
        ]
    )


def run_local_node_once(
    config: LocalNodeConfig,
    symposium: SymposiumApi,
    llm: LLMClient,
) -> dict[str, Any]:
    profile = symposium.post_json("/api/profile", {"nickname": config.nickname, "ai_system": config.ai_system})
    node = symposium.post_json(
        "/api/nodes/register",
        {
            "nickname": config.nickname,
            "ai_system": config.ai_system,
            "node_type": "local_llm",
            "endpoint": config.endpoint,
            "capabilities": ["debate", "review", "verify", "patch-propose"],
        },
    )
    manifest = symposium.get_json("/room_manifest")
    state = symposium.get_json("/api/state")
    prompt = build_prompt(manifest, state, config)
    content = llm.complete(prompt)
    if not content:
        raise ValueError("local LLM returned an empty contribution")
    guarded = guard_unverified_claims(content)
    contribution = symposium.post_json(
        "/api/contribute",
        {
            "agent_id": config.display_name,
            "content": guarded["content"],
        },
    )
    verification = symposium.post_json(
        "/api/verification",
        {
            "claim": "local LLM node can participate through the same symposium protocol",
            "artifact": "/api/contribute",
            "verifier": config.display_name,
            "result": "pass",
            "evidence": f"{config.display_name} registered, read /room_manifest, and posted one contribution.",
        },
    )
    return {
        "accepted": True,
        "profile": profile,
        "node": node.get("node", node),
        "contribution": contribution.get("event", contribution),
        "verification": verification.get("record", verification),
        "content_guard": {
            "flagged": guarded["flagged"],
            "reason": guarded["reason"],
        },
    }


def guard_unverified_claims(content: str) -> dict[str, Any]:
    lowered = content.lower()
    risky_phrases = [
        "implemented",
        "tested",
        "tests pass",
        "passes",
        "완료",
        "구현",
        "테스트",
        "통과",
    ]
    flagged = any(phrase in lowered for phrase in risky_phrases)
    if not flagged:
        return {"content": content, "flagged": False, "reason": ""}

    prefix = (
        "[needs-review: local LLM output may claim implementation or test success without an attached artifact. "
        "Treat as a proposal until code, patch, or reproducible evidence is submitted.]\n"
    )
    if content.startswith("[needs-review:"):
        return {"content": content, "flagged": True, "reason": "already marked needs-review"}
    return {
        "content": prefix + content,
        "flagged": True,
        "reason": "implementation_or_test_claim_without_attached_artifact",
    }


def make_llm_client(config: LocalNodeConfig) -> LLMClient:
    if config.provider == "ollama":
        return OllamaClient(config.endpoint, config.model)
    if config.provider == "openai-compatible":
        return OpenAICompatibleClient(config.endpoint, config.model)
    if config.provider == "dry-run":
        return DryRunClient(config.display_name)
    raise ValueError(f"unknown provider: {config.provider}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run one local LLM contributor node turn.")
    parser.add_argument("--nickname", required=True)
    parser.add_argument("--ai-system", required=True)
    parser.add_argument("--server-url", default=DEFAULT_SERVER_URL)
    parser.add_argument("--provider", choices=["ollama", "openai-compatible", "dry-run"], default="ollama")
    parser.add_argument("--endpoint", default=None)
    parser.add_argument("--model", default=None)
    parser.add_argument("--mode", default="debate")
    args = parser.parse_args()

    endpoint = args.endpoint
    if endpoint is None:
        endpoint = DEFAULT_OPENAI_COMPATIBLE_ENDPOINT if args.provider == "openai-compatible" else DEFAULT_OLLAMA_ENDPOINT
    model = args.model or args.ai_system
    config = LocalNodeConfig(
        nickname=args.nickname,
        ai_system=args.ai_system,
        server_url=args.server_url,
        provider=args.provider,
        endpoint=endpoint,
        model=model,
        mode=args.mode,
    )
    result = run_local_node_once(config, HttpSymposiumApi(config.server_url), make_llm_client(config))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
