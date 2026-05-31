from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from .engine import accept_contribution, run_round
from .manifest import room_manifest
from .simulation import ensure_simulation_state, run_global_collaboration_simulation
from .storage import VERIFICATION_LEDGER_PATH, append_events, load_state, reset_state, save_state
from .verification import append_verification, make_verification_record, read_ledger, verify_ledger


INDEX_HTML = """<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>AGI Autonomous Symposium</title>
  <style>
    :root {
      color-scheme: light;
      --ink: #141414;
      --muted: #65676d;
      --line: #d7dbe2;
      --panel: #f7f8fa;
      --accent: #0f766e;
      --warn: #a16207;
      --bg: #ffffff;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Arial, "Malgun Gothic", sans-serif;
      color: var(--ink);
      background: var(--bg);
    }
    header {
      border-bottom: 1px solid var(--line);
      padding: 18px 24px;
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: center;
    }
    h1 { font-size: 22px; margin: 0 0 4px; letter-spacing: 0; }
    .sub { color: var(--muted); font-size: 13px; }
    button {
      min-height: 38px;
      border: 1px solid var(--line);
      background: #fff;
      color: var(--ink);
      padding: 0 14px;
      cursor: pointer;
      font-weight: 600;
    }
    button.primary { background: var(--accent); color: #fff; border-color: var(--accent); }
    button:disabled { opacity: .55; cursor: wait; }
    main {
      display: grid;
      grid-template-columns: minmax(260px, 360px) 1fr;
      min-height: calc(100vh - 76px);
    }
    aside {
      border-right: 1px solid var(--line);
      padding: 18px;
      background: var(--panel);
    }
    section { padding: 18px; }
    .stat-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 10px;
      margin-bottom: 18px;
    }
    .stat, .block, .event {
      border: 1px solid var(--line);
      background: #fff;
      padding: 12px;
    }
    .label { color: var(--muted); font-size: 12px; margin-bottom: 5px; }
    .value { font-size: 18px; font-weight: 700; }
    h2 { font-size: 15px; margin: 18px 0 10px; }
    ul { padding-left: 18px; margin: 8px 0 0; }
    li { margin-bottom: 8px; }
    .toolbar { display: flex; gap: 8px; flex-wrap: wrap; }
    .events { display: grid; gap: 10px; }
    .event { border-left: 4px solid var(--accent); }
    .event.decision { border-left-color: var(--warn); }
    .event.verification_summary, .event.pr_draft { border-left-color: #1d4ed8; }
    .meta { color: var(--muted); font-size: 12px; margin-bottom: 6px; }
    .pill {
      display: inline-block;
      border: 1px solid var(--line);
      padding: 2px 6px;
      font-size: 12px;
      margin-left: 4px;
      background: var(--panel);
    }
    textarea {
      width: 100%;
      min-height: 110px;
      resize: vertical;
      border: 1px solid var(--line);
      padding: 10px;
      font: inherit;
    }
    input {
      width: 100%;
      border: 1px solid var(--line);
      padding: 9px 10px;
      font: inherit;
      margin-bottom: 8px;
    }
    @media (max-width: 820px) {
      header { align-items: flex-start; flex-direction: column; }
      main { grid-template-columns: 1fr; }
      aside { border-right: 0; border-bottom: 1px solid var(--line); }
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>AGI Autonomous Symposium</h1>
      <div class="sub">자율 토론을 결정, 실험, 백로그로 변환하는 로컬 심포지엄</div>
    </div>
    <div class="toolbar">
      <button class="primary" id="stepBtn">Run Round</button>
      <button class="primary" id="simulateBtn">Simulate Global Loop</button>
      <button id="resetBtn">Reset</button>
      <button id="manifestBtn">Manifest</button>
    </div>
  </header>
  <main>
    <aside>
      <div class="stat-grid">
        <div class="stat"><div class="label">Round</div><div class="value" id="round">0</div></div>
        <div class="stat"><div class="label">Status</div><div class="value" id="status">idle</div></div>
      </div>
      <div class="block">
        <h2>Open Questions</h2>
        <ul id="questions"></ul>
      </div>
      <div class="block">
        <h2>Backlog</h2>
        <ul id="backlog"></ul>
      </div>
      <div class="block">
        <h2>Work Packets</h2>
        <ul id="workPackets"></ul>
      </div>
      <div class="block">
        <h2>Scorecard</h2>
        <ul id="scorecard"></ul>
      </div>
      <div class="block">
        <h2>PR Drafts</h2>
        <ul id="prDrafts"></ul>
      </div>
      <div class="block">
        <h2>Verification Ledger</h2>
        <div class="sub" id="ledgerSummary">loading</div>
      </div>
      <div class="block">
        <h2>External Agent Contribution</h2>
        <input id="agentId" value="external-agent" />
        <textarea id="contribution" placeholder="외부 에이전트의 주장, 반박, 실험 제안을 입력"></textarea>
        <button id="contributeBtn">Submit</button>
      </div>
    </aside>
    <section>
      <h2>Transcript</h2>
      <div class="events" id="events"></div>
    </section>
  </main>
  <script>
    const $ = (id) => document.getElementById(id);
    async function api(path, options = {}) {
      const res = await fetch(path, options);
      if (!res.ok) throw new Error(await res.text());
      return res.json();
    }
    function list(items, render) {
      return items.map(render).join("");
    }
    function render(state) {
      $("round").textContent = state.round ?? 0;
      $("status").textContent = state.status ?? "idle";
      $("questions").innerHTML = list(state.open_questions || [], q => `<li>${escapeHtml(q)}</li>`);
      $("backlog").innerHTML = list(state.backlog || [], item => `<li><strong>${escapeHtml(item.id)}</strong> ${escapeHtml(item.title)} <span class="sub">${escapeHtml(item.status)}</span></li>`);
      $("workPackets").innerHTML = list(state.work_packets || [], item => `<li><strong>${escapeHtml(item.id)}</strong> ${escapeHtml(item.title)} <span class="pill">${escapeHtml(item.status)}</span></li>`);
      $("scorecard").innerHTML = Object.entries(state.scorecard || {}).map(([name, score]) => `<li><strong>${escapeHtml(name)}</strong> pass ${score.pass || 0}, fail ${score.fail || 0}, review ${score["needs-review"] || 0}</li>`).join("");
      $("prDrafts").innerHTML = list([...(state.pr_drafts || [])].slice(-5).reverse(), draft => `<li><strong>${escapeHtml(draft.id)}</strong> ${escapeHtml(draft.title)} <span class="sub">${escapeHtml(draft.branch)}</span></li>`);
      const events = [...(state.events || [])].reverse();
      $("events").innerHTML = events.map(event => `
        <article class="event ${event.type === "decision" ? "decision" : ""} ${escapeHtml(event.type || "")}">
          <div class="meta">${escapeHtml(event.type)} · ${escapeHtml(event.agent_name || event.agent_id || "")} · round ${escapeHtml(String(event.round ?? 0))}</div>
          <div>${escapeHtml(event.content || "")}</div>
        </article>
      `).join("");
    }
    function escapeHtml(value) {
      return String(value).replace(/[&<>"']/g, char => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
      }[char]));
    }
    async function refresh() { render(await api("/api/state")); }
    async function refreshLedger() {
      const ledger = await api("/api/verification");
      $("ledgerSummary").textContent = `${ledger.records.length} records · ${ledger.errors.length} integrity errors`;
    }
    async function busy(button, work) {
      button.disabled = true;
      try { await work(); await refresh(); await refreshLedger(); } finally { button.disabled = false; }
    }
    $("stepBtn").onclick = () => busy($("stepBtn"), () => api("/api/step", { method: "POST" }));
    $("simulateBtn").onclick = () => busy($("simulateBtn"), () => api("/api/simulate", { method: "POST" }));
    $("resetBtn").onclick = () => busy($("resetBtn"), () => api("/api/reset", { method: "POST" }));
    $("manifestBtn").onclick = () => window.open("/room_manifest", "_blank");
    $("contributeBtn").onclick = () => busy($("contributeBtn"), () => api("/api/contribute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ agent_id: $("agentId").value, content: $("contribution").value })
    }));
    refresh();
    refreshLedger();
  </script>
</body>
</html>
"""


class SymposiumHandler(BaseHTTPRequestHandler):
    server_version = "AGISymposium/0.1"

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/":
            self.send_text(INDEX_HTML, "text/html; charset=utf-8")
        elif path == "/api/state":
            state = ensure_simulation_state(load_state())
            save_state(state)
            self.send_json(state)
        elif path == "/room_manifest":
            self.send_json(room_manifest(load_state()))
        elif path == "/api/verification":
            self.send_json(
                {
                    "records": read_ledger(VERIFICATION_LEDGER_PATH),
                    "errors": verify_ledger(VERIFICATION_LEDGER_PATH),
                }
            )
        else:
            self.send_error(404, "Not found")

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            if path == "/api/step":
                state, events = run_round(load_state())
                save_state(state)
                append_events(events)
                self.send_json(state)
            elif path == "/api/reset":
                self.send_json(reset_state())
            elif path == "/api/simulate":
                state, events, verification_specs = run_global_collaboration_simulation(load_state())
                saved_records = []
                for spec in verification_specs:
                    record = make_verification_record(**spec)
                    saved_records.append(append_verification(VERIFICATION_LEDGER_PATH, record))
                save_state(state)
                append_events(events)
                self.send_json({"state": state, "events": events, "verification_records": saved_records})
            elif path == "/api/contribute":
                body = self.read_json()
                state, event = accept_contribution(load_state(), body)
                save_state(state)
                append_events([event])
                self.send_json({"accepted": True, "event": event, "state": state})
            elif path == "/api/verification":
                body = self.read_json()
                record = make_verification_record(
                    claim=str(body.get("claim") or ""),
                    artifact=str(body.get("artifact") or ""),
                    verifier=str(body.get("verifier") or ""),
                    result=str(body.get("result") or "needs-review"),
                    evidence=str(body.get("evidence") or ""),
                )
                saved = append_verification(VERIFICATION_LEDGER_PATH, record)
                self.send_json({"accepted": True, "record": saved})
            else:
                self.send_error(404, "Not found")
        except ValueError as exc:
            self.send_json({"error": str(exc)}, status=400)

    def read_json(self) -> dict[str, Any]:
        length = int(self.headers.get("Content-Length") or "0")
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def send_json(self, payload: Any, status: int = 200) -> None:
        data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_text(self, payload: str, content_type: str) -> None:
        data = payload.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format: str, *args: Any) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), SymposiumHandler)
    print(f"AGI symposium running at http://{args.host}:{args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
