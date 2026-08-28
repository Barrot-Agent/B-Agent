"""
HTTP API server for GPT Actions / custom GPT integration.

Exposes GitHub operations as JSON REST endpoints that can be described via an
OpenAPI schema and wired up to a custom GPT or other HTTP-based integration.

Run with:
    python -m scripts.run_gpt_api
    # or
    python scripts/run_gpt_api.py
"""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from barrot_agent.config import AppConfig
from barrot_agent.github_service import make_service


def _build_app(config: AppConfig) -> type[BaseHTTPRequestHandler]:
    """Return a request handler class bound to the given configuration."""

    default_owner = config.github_default_owner or ""
    default_repo = config.github_default_repo or ""
    # Build the service once; reuse it for every request in this process.
    svc = make_service(config.github_token or "")

    class _Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args: Any) -> None:  # noqa: D102
            pass  # silence access log

        def _send_json(self, status: int, payload: Any) -> None:
            body = json.dumps(payload).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _read_body(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", 0))
            if length == 0:
                return {}
            return json.loads(self.rfile.read(length).decode())

        def _params(self) -> dict[str, str]:
            parsed = urlparse(self.path)
            qs = parse_qs(parsed.query)
            return {k: v[0] for k, v in qs.items()}

        def _path_prefix(self) -> str:
            return urlparse(self.path).path

        # ------------------------------------------------------------------
        # Routes
        # ------------------------------------------------------------------

        def do_GET(self) -> None:  # noqa: N802
            path = self._path_prefix()
            params = self._params()

            if path == "/health":
                self._send_json(200, {"status": "ok"})
                return

            if path == "/openapi.json":
                self._send_json(200, _OPENAPI_SCHEMA)
                return

            # GET /issues?owner=&repo=&state=&page=&per_page=
            if path == "/issues":
                owner = params.get("owner", default_owner)
                repo = params.get("repo", default_repo)
                if not owner or not repo:
                    self._send_json(400, {"error": "owner and repo are required"})
                    return
                try:
                    result = svc.list_issues(
                        owner=owner,
                        repo=repo,
                        state=params.get("state", "open"),
                        per_page=int(params.get("per_page", 30)),
                        page=int(params.get("page", 1)),
                    )
                    self._send_json(200, result)
                except Exception as exc:  # noqa: BLE001
                    self._send_json(502, {"error": str(exc)})
                return

            # GET /issues/{number}?owner=&repo=
            if path.startswith("/issues/"):
                parts = path.split("/")
                if len(parts) == 3 and parts[2].isdigit():
                    owner = params.get("owner", default_owner)
                    repo = params.get("repo", default_repo)
                    if not owner or not repo:
                        self._send_json(400, {"error": "owner and repo are required"})
                        return
                    try:
                        result = svc.get_issue(owner, repo, int(parts[2]))
                        self._send_json(200, result)
                    except Exception as exc:  # noqa: BLE001
                        self._send_json(502, {"error": str(exc)})
                    return

            self._send_json(404, {"error": "not found"})

        def do_POST(self) -> None:  # noqa: N802
            path = self._path_prefix()
            params = self._params()
            body = self._read_body()

            # POST /issues  — create issue
            if path == "/issues":
                owner = body.get("owner") or params.get("owner", default_owner)
                repo = body.get("repo") or params.get("repo", default_repo)
                title = body.get("title", "")
                issue_body = body.get("body", "")
                labels = body.get("labels")
                if not owner or not repo or not title:
                    self._send_json(400, {"error": "owner, repo and title are required"})
                    return
                try:
                    result = svc.create_issue(owner, repo, title, issue_body, labels)
                    self._send_json(201, result)
                except Exception as exc:  # noqa: BLE001
                    self._send_json(502, {"error": str(exc)})
                return

            # POST /issues/{number}/comments  — add comment
            if path.startswith("/issues/") and path.endswith("/comments"):
                parts = path.split("/")
                if len(parts) == 4 and parts[2].isdigit():
                    owner = body.get("owner") or params.get("owner", default_owner)
                    repo = body.get("repo") or params.get("repo", default_repo)
                    comment_body = body.get("body", "")
                    if not owner or not repo or not comment_body:
                        self._send_json(400, {"error": "owner, repo and body are required"})
                        return
                    try:
                        result = svc.add_comment(owner, repo, int(parts[2]), comment_body)
                        self._send_json(201, result)
                    except Exception as exc:  # noqa: BLE001
                        self._send_json(502, {"error": str(exc)})
                    return

            self._send_json(404, {"error": "not found"})

    return _Handler


# Minimal OpenAPI 3.1 schema for GPT Actions registration
_OPENAPI_SCHEMA: dict[str, Any] = {
    "openapi": "3.1.0",
    "info": {
        "title": "B-Agent GitHub API",
        "description": "GitHub issue operations exposed for custom GPT / GPT Actions integration.",
        "version": "1.0.0",
    },
    "paths": {
        "/issues": {
            "get": {
                "operationId": "listIssues",
                "summary": "List repository issues",
                "parameters": [
                    {"name": "owner", "in": "query", "schema": {"type": "string"}},
                    {"name": "repo", "in": "query", "schema": {"type": "string"}},
                    {
                        "name": "state",
                        "in": "query",
                        "schema": {"type": "string", "default": "open"},
                    },
                    {
                        "name": "per_page",
                        "in": "query",
                        "schema": {"type": "integer", "default": 30},
                    },
                    {"name": "page", "in": "query", "schema": {"type": "integer", "default": 1}},
                ],
                "responses": {"200": {"description": "List of issues"}},
            },
            "post": {
                "operationId": "createIssue",
                "summary": "Create a new issue",
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["owner", "repo", "title"],
                                "properties": {
                                    "owner": {"type": "string"},
                                    "repo": {"type": "string"},
                                    "title": {"type": "string"},
                                    "body": {"type": "string"},
                                    "labels": {"type": "array", "items": {"type": "string"}},
                                },
                            }
                        }
                    },
                },
                "responses": {"201": {"description": "Created issue"}},
            },
        },
        "/issues/{number}": {
            "get": {
                "operationId": "getIssue",
                "summary": "Get a single issue by number",
                "parameters": [
                    {
                        "name": "number",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                    },
                    {"name": "owner", "in": "query", "schema": {"type": "string"}},
                    {"name": "repo", "in": "query", "schema": {"type": "string"}},
                ],
                "responses": {"200": {"description": "Issue details"}},
            }
        },
        "/issues/{number}/comments": {
            "post": {
                "operationId": "addComment",
                "summary": "Add a comment to an issue",
                "parameters": [
                    {
                        "name": "number",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "integer"},
                    }
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "required": ["owner", "repo", "body"],
                                "properties": {
                                    "owner": {"type": "string"},
                                    "repo": {"type": "string"},
                                    "body": {"type": "string"},
                                },
                            }
                        }
                    },
                },
                "responses": {"201": {"description": "Created comment"}},
            }
        },
    },
}


def run_server(config: AppConfig | None = None) -> None:
    """Start the GPT Actions HTTP server."""
    cfg = config or AppConfig()
    host = cfg.gpt_api_host
    port = cfg.gpt_api_port
    handler = _build_app(cfg)
    server = HTTPServer((host, port), handler)
    print(f"B-Agent GPT Actions API listening on http://{host}:{port}")
    print(f"OpenAPI schema: http://{host}:{port}/openapi.json")
    server.serve_forever()


if __name__ == "__main__":
    run_server()
