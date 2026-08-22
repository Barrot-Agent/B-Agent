#!/usr/bin/env python3
"""
Barrot-Ω A2A (Agent-to-Agent) Server
Real A2A v1.0.1 protocol implementation, no Cloudflare needed.
Runs on localhost:8000 — Agent Card at /.well-known/agent-card.json
JSON-RPC endpoint at / — accepts message/send calls.

Routing:
  - params.agent == "chatgpt"  → ChatGPT connector (requires OPENAI_API_KEY)
  - default                    → Groq inference (requires GROQ_API_KEY)

ChatGPT ↔ Barrot-Ω identity boundaries:
  user_request → A2A auth → capability_check → connector → normalized_result
"""
import json
import os
import sys
import urllib.request
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
BRAIN_SECRET = os.environ.get("BRAIN_SHARED_SECRET", "")
GROQ_MODEL = "openai/gpt-oss-120b"

# Capabilities that ChatGPT (or any A2A caller) is permitted to invoke.
# Privileged operations (repo writes, workflow execution, production deploy)
# must go through the MCP approval/sandbox layer and are NOT exposed here.
_PERMITTED_CAPABILITIES = {"natural-language", "chatgpt-relay", "mcp-read", "github-read"}
_PRIVILEGED_CAPABILITIES = {"github-write", "mcp-execute", "production-deploy"}

AGENT_CARD = {
    "name": "Barrot-Ω",
    "description": (
        "Autonomous research and orchestration agent. "
        "Backed by Groq inference and ChatGPT relay. "
        "Exposes read-only GitHub/MCP capabilities over A2A; "
        "privileged operations require out-of-band MCP approval."
    ),
    "url": "http://localhost:8000/",
    "version": "1.1.0",
    "capabilities": {
        "streaming": False,
        "pushNotifications": False,
        "stateTransitionHistory": False,
    },
    "defaultInputModes": ["text/plain"],
    "defaultOutputModes": ["text/plain"],
    "authentication": {
        "schemes": ["custom-header"],
        "credentials": "X-Barrot-Auth header, shared secret (BRAIN_SHARED_SECRET)",
    },
    "skills": [
        {
            "id": "natural-language",
            "name": "Natural-language reasoning (Groq)",
            "description": "General Q&A and reasoning via Groq-backed inference.",
            "tags": ["research", "qa", "reasoning"],
            "examples": ["Summarise today's XRP signal context."],
        },
        {
            "id": "chatgpt-relay",
            "name": "ChatGPT peer relay",
            "description": (
                "Route a message to ChatGPT (OpenAI) and return the "
                "normalised response. Requires OPENAI_API_KEY on the server."
            ),
            "tags": ["chatgpt", "openai", "external-agent"],
            "examples": ["@chatgpt What is the current state of BTC sentiment?"],
            "inputModes": ["text/plain"],
            "outputModes": ["application/json"],
        },
        {
            "id": "github-read",
            "name": "GitHub read operations",
            "description": "Read repository metadata, issues, and workflow status via GitHub App.",
            "tags": ["github", "read-only"],
            "examples": ["List open issues in Barrot-Agent/B-Agent."],
        },
        {
            "id": "mcp-read",
            "name": "MCP capability discovery (read-only)",
            "description": "Enumerate registered MCP servers and their tool inventories.",
            "tags": ["mcp", "discovery", "read-only"],
            "examples": ["List active MCP servers."],
        },
    ],
}

def call_groq(text):
    body = json.dumps({
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are Barrot-Ω, answering a request from another agent via the A2A protocol. Be concise and factual."},
            {"role": "user", "content": text}
        ],
        "max_tokens": 1024,
        "temperature": 0.3,
    }).encode()
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {GROQ_KEY}", "Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp)["choices"][0]["message"]["content"]
    except Exception as e:
        raise RuntimeError(f"Groq error: {e}")


def call_chatgpt(text):
    """Route text to ChatGPT and return a NormalizedResponse dict."""
    import importlib.util, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))
    from barrot_agent.chatgpt_connector import ChatGPTClient
    with ChatGPTClient() as client:
        return client.chat(text).to_dict()


def _check_capability(capability: str) -> bool:
    """Return True if the requested capability is permitted over A2A."""
    return capability not in _PRIVILEGED_CAPABILITIES


class A2AHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[{self.client_address[0]}] {format % args}")

    def do_GET(self):
        if self.path == "/.well-known/agent-card.json":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(AGENT_CARD, indent=2).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "content-type, x-barrot-auth")
        self.end_headers()

    def do_POST(self):
        if self.path != "/":
            self.send_response(404)
            self.end_headers()
            return

        auth = self.headers.get("X-Barrot-Auth", "")
        if not BRAIN_SECRET or auth != BRAIN_SECRET:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32001, "message": "Unauthorized"}
            }).encode())
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length))
        except Exception:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": "Parse error"}
            }).encode())
            return

        req_id = payload.get("id")
        method = payload.get("method")
        params = payload.get("params", {})

        if method == "message/send":
            message = params.get("message", {})
            parts = message.get("parts", [])
            text = "\n".join(p.get("text", "") for p in parts if p.get("type") == "text")

            if not text:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32602, "message": "Invalid params"}
                }).encode())
                return

            # Check capability authorization
            requested_capability = params.get("capability", "natural-language")
            if not _check_capability(requested_capability):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {
                        "code": -32003,
                        "message": f"Capability '{requested_capability}' requires out-of-band MCP approval",
                    },
                }).encode())
                return

            # Route to ChatGPT connector or default Groq inference
            agent = params.get("agent", "barrot")
            try:
                if agent == "chatgpt":
                    result = call_chatgpt(text)
                    reply_text = result.get("content", "")
                    if not result.get("success"):
                        raise RuntimeError(result.get("error", "ChatGPT error"))
                    artifact_parts = [
                        {"type": "text", "text": reply_text},
                        {"type": "data", "data": {
                            "role": result.get("role"),
                            "source": result.get("source"),
                            "model": result.get("model"),
                            "usage": result.get("usage"),
                        }},
                    ]
                else:
                    reply_text = call_groq(text)
                    artifact_parts = [{"type": "text", "text": reply_text}]
            except Exception as e:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32000, "message": f"Upstream error: {str(e)[:100]}"}
                }).encode())
                return

            task = {
                "id": str(uuid.uuid4()),
                "status": {"state": "completed"},
                "artifacts": [
                    {"name": "response", "parts": artifact_parts}
                ]
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "jsonrpc": "2.0",
                "id": req_id,
                "result": task
            }).encode())
        else:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            }).encode())

if __name__ == "__main__":
    if not GROQ_KEY:
        print("GROQ_API_KEY not set")
        sys.exit(1)
    if not BRAIN_SECRET:
        print("BRAIN_SHARED_SECRET not set")
        sys.exit(1)

    server = HTTPServer(("0.0.0.0", 8000), A2AHandler)
    print("Barrot-Ω A2A Server listening on http://0.0.0.0:8000/")
    print(f"Agent Card: GET /.well-known/agent-card.json")
    print(f"JSON-RPC endpoint: POST / with X-Barrot-Auth header")
    server.serve_forever()
