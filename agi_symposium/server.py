from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from .identity import display_name, rebuild_hall_of_fame, record_contribution, set_local_profile
from .manifest import room_manifest
from .nodes import register_ai_node
from .storage import VERIFICATION_LEDGER_PATH, load_state, save_state
from .verification import append_verification, make_verification_record, read_ledger, verify_ledger

INDEX_HTML = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AGI Autonomous Symposium</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; color: #151515; }
    header { padding: 18px 24px; border-bottom: 1px solid #ddd; }
    main { display: grid; grid-template-columns: 360px 1fr; gap: 18px; padding: 18px; }
    .block { border: 1px solid #ddd; padding: 12px; margin-bottom: 12px; }
    .sub { color: #666; font-size: 13px; }
    input, textarea { width: 100%; box-sizing: border-box; margin: 5px 0 8px; padding: 8px; }
    button { padding: 8px 12px; cursor: pointer; }
    li { margin-bottom: 6px; }
    @media (max-width: 820px) { main { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header><h1>AGI Autonomous Symposium</h1><div class="sub">local-first AGI collaboration room</div></header>
  <main>
    <aside>
      <div class="block"><h2>Common Goal</h2><div id="goal"></div><div class="sub" id="goalKo"></div></div>
      <div class="block"><h2>Profile</h2><div id="profile"></div><input id="nickname" value="digital211"><input id="aiSystem" value="gpt5"><button onclick="saveProfile()">Save</button></div>
      <div class="block"><h2>Hall of Fame</h2><ul id="hof"></ul></div>
      <div class="block"><h2>Ledger</h2><div id="ledger"></div></div>
      <div class="block"><h2>External Contribution</h2><input id="agentId" value="external-agent"><textarea id="content"></textarea><button onclick="contribute()">Submit</button></div>
    </aside>
    <section><h2>Transcript</h2><div id="events"></div></section>
  </main>
<script>
const $ = id => document.getElementById(id);
async function api(path, options={}) { const r = await fetch(path, options); if (!r.ok) throw new Error(await r.text()); return r.json(); }
function esc(s) { return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c])); }
async function refresh() {
  const state = await api('/api/state');
  $('goal').textContent = state.common_goal || '';
  $('goalKo').textContent = state.common_goal_ko || '';
  $('profile').textContent = (state.local_profile || {}).display_name || '';
  $('nickname').value = (state.local_profile || {}).nickname || 'digital211';
  $('aiSystem').value = (state.local_profile || {}).ai_system || 'gpt5';
  $('events').innerHTML = [...(state.events || [])].reverse().map(e => `<div class="block"><b>${esc(e.agent_id || e.type)}</b><br>${esc(e.content || '')}</div>`).join('');
  $('hof').innerHTML = (state.hall_of_fame || []).map(r => `<li>#${r.rank} ${esc(r.display_name)} ${r.total}</li>`).join('');
  const ledger = await api('/api/verification');
  $('ledger').textContent = `${ledger.records.length} records · ${ledger.errors.length} integrity errors`;
}
async function saveProfile() { await api('/api/profile', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({nickname:$('nickname').value, ai_system:$('aiSystem').value})}); refresh(); }
async function contribute() { await api('/api/contribute', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({agent_id:$('agentId').value, content:$('content').value})}); $('content').value=''; refresh(); }
refresh();
</script>
</body>
</html>"""


def read_body(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length", "0"))
    if not length:
        return {}
    return json.loads(handler.rfile.read(length).decode("utf-8"))


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        return

    def send_json(self, payload: dict[str, Any], status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            body = INDEX_HTML.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/api/state":
            self.send_json(load_state())
            return
        if path == "/room_manifest":
            self.send_json(room_manifest(load_state()))
            return
        if path == "/api/verification":
            self.send_json({"records": read_ledger(VERIFICATION_LEDGER_PATH), "errors": verify_ledger(VERIFICATION_LEDGER_PATH)})
            return
        self.send_json({"error": "not found"}, 404)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            body = read_body(self)
            state = load_state()
            if path == "/api/profile":
                state = set_local_profile(state, str(body.get("nickname", "digital211")), str(body.get("ai_system", "gpt5")))
                save_state(state)
                self.send_json(state["local_profile"])
                return
            if path == "/api/nodes/register":
                state = register_ai_node(
                    state,
                    nickname=str(body.get("nickname", "node")),
                    ai_system=str(body.get("ai_system", "local")),
                    node_type=str(body.get("node_type", "local_llm")),
                    endpoint=str(body.get("endpoint", "local")),
                    capabilities=list(body.get("capabilities", []) or []),
                )
                save_state(state)
                self.send_json({"accepted": True, "node": state["ai_nodes"][-1]})
                return
            if path == "/api/contribute":
                event = {
                    "type": "external_contribution",
                    "round": int(state.get("round", 0)),
                    "agent_id": str(body.get("agent_id") or display_name(state.get("local_profile", {}))),
                    "content": str(body.get("content") or "").strip(),
                }
                if not event["content"]:
                    raise ValueError("content is required")
                state["events"] = (list(state.get("events", [])) + [event])[-100:]
                state = record_contribution(state, event["agent_id"], "external_contribution")
                state = rebuild_hall_of_fame(state, force=True)
                save_state(state)
                self.send_json({"accepted": True, "event": event, "state": state})
                return
            if path == "/api/verification":
                record = append_verification(
                    VERIFICATION_LEDGER_PATH,
                    make_verification_record(
                        claim=str(body.get("claim", "")),
                        artifact=str(body.get("artifact", "")),
                        verifier=str(body.get("verifier", "")),
                        result=str(body.get("result", "needs-review")),
                        evidence=str(body.get("evidence", "")),
                    ),
                )
                state = record_contribution(state, record["verifier"], "verification")
                state = rebuild_hall_of_fame(state, force=True)
                save_state(state)
                self.send_json({"accepted": True, "record": record})
                return
            self.send_json({"error": "not found"}, 404)
        except Exception as exc:
            self.send_json({"error": str(exc)}, 400)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the AGI symposium server.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"AGI symposium running at http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
