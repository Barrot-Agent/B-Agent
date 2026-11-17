"""The server must boot, serve, and answer health with 200."""

from __future__ import annotations

import json
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.barrot_server import make_server


def start():
    server = make_server("127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    host, port = server.server_address[:2]
    return server, f"http://{host}:{port}"


def test_health_returns_200_and_ok():
    server, base = start()
    try:
        with urllib.request.urlopen(base + "/health", timeout=5) as response:
            assert response.status == 200
            body = json.loads(response.read())
        assert body["status"] == "ok"
        assert body["time"]
    finally:
        server.shutdown()
        server.server_close()


def test_status_reports_environment_and_ledger():
    server, base = start()
    try:
        with urllib.request.urlopen(base + "/status", timeout=5) as response:
            assert response.status == 200
            body = json.loads(response.read())
        assert body["service"] == "barrot"
        assert "environment" in body
        assert "ledger" in body
        assert body["uptime_seconds"] >= 0
    finally:
        server.shutdown()
        server.server_close()


def test_unknown_path_is_404():
    server, base = start()
    try:
        with urllib.request.urlopen(base + "/nope", timeout=5) as response:
            assert response.status == 404
    except urllib.error.HTTPError as exc:
        assert exc.code == 404
        body = json.loads(exc.read())
        assert body["error"] == "not found"
    finally:
        server.shutdown()
        server.server_close()
