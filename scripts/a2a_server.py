#!/usr/bin/env python3
"""
Barrot-Ω A2A (Agent-to-Agent) Server
Real A2A v1.0.1 protocol implementation, no Cloudflare needed.
Runs on localhost:8000 — Agent Card at /.well-known/agent-card.json
JSON-RPC endpoint at / — accepts message/send calls.
"""
import json
import os
import sys
import urllib.request
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
BRAIN_SECRET = os.environ.get("BRAIN_SHARED_SECRET", "")
MODEL = "openai/gpt-oss-120b"

AGENT_CARD = {
    "name": "Barrot-Ω",
    "description": "Autonomous XRP/BTC signal research agent. Real Groq-backed inference, no owned compute.",
    "url": "http://localhost:8000/",
    "version": "1.0.0",
    "capabilities": {
        "streaming": False,
        "pushNotifications": False,
        "stateTransitionHistory": False
    },
    "defaultInputModes": ["text/plain"],
    "defaultOutputModes": ["text/plain"],
    "authentication": {
        "schemes": ["custom-header"],
        "credentials": "X-Barrot-Auth header, shared secret"
    },
    "skills": [{
        "id": "general-query",
        "name": "General grounded query",
        "description": "Ask Barrot a question; answered via Groq openai/gpt-oss-120b.",
        "tags": ["research", "qa"],
        "examples": ["What is Barrot's current signal accuracy?"]
    }]
}

def call_groq(text):
    body = json.dumps({
        "model": MODEL,
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

            try:
                reply = call_groq(text)
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
                    {"name": "response", "parts": [{"type": "text", "text": reply}]}
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
