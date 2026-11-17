#!/usr/bin/env python3
"""Barrot HTTP server: boot, serve, and answer a health check with 200.

Three endpoints, no dependencies beyond the standard library:

  GET /health   200, {"status": "ok", ...}
  GET /status   200, environment summary and Millennium ledger counts
  anything else 404 JSON

Binds to loopback by default. --host 0.0.0.0 exposes it, and that is a deliberate
flag rather than a default.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STARTED = time.time()


def _ledger_counts() -> dict:
    path = ROOT / "data" / "millennium" / "ledger.json"
    if not path.exists():
        return {"available": False}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"available": False, "error": "ledger is not valid json"}
    evidence = {p["name"]: p["evidence"]["usable_claims"] for p in payload.get("problems", []) if "evidence" in p}
    return {
        "available": True,
        "problems": len(payload.get("problems", [])),
        "conflicts": len(payload.get("conflicts", [])),
        "usable_claims_by_problem": evidence,
    }


def status_payload() -> dict:
    try:
        from barrot_agent.environment import detect

        env = detect()
        environment = {
            "summary": env.summary,
            "device": env.device_model,
            "surface": env.surface,
            "lightweight": env.lightweight,
        }
    except Exception as exc:  # never fail the status endpoint on detection
        environment = {"error": str(exc)}
    return {
        "service": "barrot",
        "version": "1",
        "platform": platform.platform(),
        "uptime_seconds": round(time.time() - STARTED, 3),
        "environment": environment,
        "ledger": _ledger_counts(),
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "Barrot/1"

    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send(200, {"status": "ok", "time": datetime.now(timezone.utc).isoformat()})
        elif self.path == "/status":
            self._send(200, status_payload())
        else:
            self._send(404, {"error": "not found", "path": self.path})

    def log_message(self, fmt: str, *args) -> None:
        if "--quiet" not in sys.argv:
            print(f"{self.address_string()} {fmt % args}")


def make_server(host: str = "127.0.0.1", port: int = 8134) -> ThreadingHTTPServer:
    return ThreadingHTTPServer((host, port), Handler)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8134)
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()
    server = make_server(args.host, args.port)
    host, port = server.server_address[:2]
    print(f"BARROT SERVER listening on http://{host}:{port}")
    print("health: /health  status: /status")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("BARROT SERVER stopping")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
