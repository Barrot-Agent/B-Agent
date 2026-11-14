"""Tests for the live MCP synchronization engine.

Runs with the stdlib test runner (``python -m unittest``) and also under pytest.
No network access: a local ThreadingHTTPServer acts as the MCP server.
"""

from __future__ import annotations

import json
import os
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from barrot_agent.mcp_sync import (
    MCPServerConfig,
    _parse_rpc,
    _resolve_value,
    build_snapshot,
    compute_gaps,
    fill_gaps,
    infer_categories,
    load_configs,
    merge_cached,
    probe_all,
    probe_remote,
    ServerProbe,
    ToolRecord,
)
from barrot_agent.mcp_targets import CAPABILITY_TARGETS, SUPPORTED_MCP_SERVERS


class _StubMCPHandler(BaseHTTPRequestHandler):
    latency = 0.12
    sse = False

    def log_message(self, *args):  # silence test output
        pass

    def _send(self, payload: dict, content_type: str = "application/json") -> None:
        body = json.dumps(payload).encode()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        message = json.loads(self.rfile.read(length) or b"{}")
        method = message.get("method")
        if method == "initialize":
            self._send(
                {
                    "jsonrpc": "2.0",
                    "id": message.get("id"),
                    "result": {
                        "protocolVersion": "2025-06-18",
                        "capabilities": {"tools": {}},
                        "serverInfo": {"name": "stub", "version": "0.0.1"},
                    },
                }
            )
        elif method == "tools/list":
            time.sleep(self.latency)
            payload = {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "result": {
                    "tools": [
                        {
                            "name": "web_search",
                            "description": "Search the web for news",
                            "inputSchema": {"type": "object", "properties": {"q": {"type": "string"}}},
                        },
                        {
                            "name": "store_memory",
                            "description": "Store a fact in the knowledge graph",
                            "inputSchema": {"type": "object"},
                        },
                    ]
                },
            }
            if self.sse:
                body = ("event: message\ndata: " + json.dumps(payload) + "\n\n").encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:
                self._send(payload)
        else:
            self._send({"jsonrpc": "2.0", "id": message.get("id"), "result": {}})


class StubServer:
    def __init__(self, sse: bool = False):
        handler = type("Handler", (_StubMCPHandler,), {"sse": sse})
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.httpd.server_address[1]}/mcp"

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.httpd.shutdown()
        self.httpd.server_close()


class ConfigTests(unittest.TestCase):
    def test_resolve_value(self):
        with patch.dict(os.environ, {"DEMO_TOKEN": "abc"}):
            text, missing = _resolve_value("Bearer {env:DEMO_TOKEN}")
        self.assertEqual(text, "Bearer abc")
        self.assertEqual(missing, [])

    def test_resolve_missing_env(self):
        with patch.dict(os.environ, {}, clear=True):
            text, missing = _resolve_value("Bearer {env:NOT_SET}")
        self.assertEqual(text, "Bearer ")
        self.assertEqual(missing, ["NOT_SET"])

    def test_load_configs_new_and_legacy_shapes(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "opencode.json").write_text(
                json.dumps(
                    {
                        "mcp": {
                            "servers": {
                                "live": {
                                    "type": "remote",
                                    "url": "https://example.invalid/mcp",
                                    "headers": {"Authorization": "Bearer {env:TOKEN}"},
                                }
                            },
                            "legacy": {"type": "remote", "url": "https://legacy.invalid/mcp"},
                            "off": {
                                "type": "remote",
                                "url": "https://off.invalid/mcp",
                                "enabled": False,
                            },
                        }
                    }
                )
            )
            (root / "mcp_config.json").write_text(
                json.dumps(
                    {
                        "mcpServers": {
                            "local": {"command": "python3", "args": ["-m", "something"]}
                        }
                    }
                )
            )
            with patch.dict(os.environ, {"TOKEN": "secret"}):
                configs = load_configs(root)
        by_name = {c.name: c for c in configs}
        # Disabled servers are retained so the snapshot can report them explicitly.
        self.assertEqual(set(by_name), {"live", "legacy", "local", "off"})
        self.assertTrue(by_name["off"].enabled is False)
        self.assertEqual(by_name["live"].headers["Authorization"], "Bearer secret")
        self.assertEqual(by_name["local"].command, ["python3", "-m", "something"])
        self.assertEqual(by_name["local"].transport, "stdio")


class CategoryTests(unittest.TestCase):
    def test_infer_categories(self):
        cats = infer_categories("Generate an image from a text prompt")
        self.assertIn("image_generation", cats)
        self.assertIn("generative_media", cats)

    def test_infer_categories_no_false_coverage(self):
        # Regression: a document converter that mentions "scanned" and "facts"
        # must not claim security_scanning / knowledge_graph coverage.
        description = (
            "Convert a document or a scanned raster image into Markdown. "
            "Give a url the server fetches, or the file's bytes. "
            "Returns artifact metadata and facts about the source document."
        )
        cats = infer_categories("convert_document " + description)
        self.assertIn("document_conversion", cats)
        self.assertNotIn("security_scanning", cats)
        self.assertNotIn("knowledge_graph", cats)
        self.assertNotIn("fact_checking", cats)

    def test_gaps_detect_uncovered_and_fill(self):
        covered = ToolRecord(
            server="x",
            name="git_commit",
            description="Commit to git",
            categories=["version_control"],
        )
        gaps = compute_gaps(CAPABILITY_TARGETS, [covered])
        # Security scanning has no live tool and no static catalogue candidate.
        security = [g for g in gaps if g["target_id"] == "cap-002"]
        self.assertEqual(len(security), 1)
        # Knowledge graph can be back-filled by the static memory server spec.
        knowledge = [g for g in gaps if g["target_id"] == "cap-005"]
        self.assertEqual(len(knowledge), 1)
        fill_gaps(gaps, SUPPORTED_MCP_SERVERS)
        self.assertTrue(all("candidates" in g for g in gaps))
        self.assertFalse(security[0]["filled"])
        self.assertTrue(knowledge[0]["filled"])
        self.assertTrue(knowledge[0]["candidates"][0]["full_match"])

    def test_partial_candidate_is_not_a_fill(self):
        # cap-006 needs vision AND media_processing; no static spec covers both.
        gaps = compute_gaps(CAPABILITY_TARGETS, [])
        video = [g for g in gaps if g["target_id"] == "cap-006"][0]
        self.assertEqual(
            video["required_tool_categories"], ["media_processing", "vision"]
        )
        fill_gaps([video], SUPPORTED_MCP_SERVERS)
        self.assertFalse(video["filled"])
        self.assertTrue(all(not c["full_match"] for c in video["candidates"]))


class CacheTests(unittest.TestCase):
    def test_merge_cached_backfills_failed_server(self):
        failed = ServerProbe(name="a", transport="remote", status="unreachable", error="boom")
        cache = {
            "a": {
                "tools": [
                    {
                        "name": "stored_tool",
                        "description": "from cache",
                        "categories": ["knowledge_graph"],
                        "input_schema": {},
                    }
                ]
            }
        }
        merged = merge_cached([failed], cache)
        self.assertEqual(merged[0].status, "cached")
        self.assertEqual(merged[0].source, "cache")
        self.assertEqual(len(merged[0].tools), 1)
        self.assertEqual(merged[0].tools[0].source, "cache")

    def test_connected_server_is_not_overwritten(self):
        live = ServerProbe(
            name="a",
            transport="remote",
            status="connected",
            tools=[ToolRecord(server="a", name="live_tool")],
        )
        cache = {"a": {"tools": [{"name": "stale_tool"}]}}
        merged = merge_cached([live], cache)
        self.assertEqual([t.name for t in merged[0].tools], ["live_tool"])
        self.assertEqual(merged[0].status, "connected")


class TransportTests(unittest.TestCase):
    def test_sse_parser(self):
        msg = _parse_rpc('event: message\ndata: {"jsonrpc":"2.0","id":1,"result":{}}\n\n', "text/event-stream")
        self.assertEqual(msg["id"], 1)

    def test_probe_remote_connected(self):
        with StubServer() as server:
            probe = probe_remote(MCPServerConfig(name="stub", transport="remote", url=server.url))
        self.assertEqual(probe.status, "connected")
        self.assertEqual(probe.protocol_version, "2025-06-18")
        self.assertEqual({t.name for t in probe.tools}, {"web_search", "store_memory"})
        self.assertEqual(probe.attempts, 1)

    def test_probe_remote_sse(self):
        with StubServer(sse=True) as server:
            probe = probe_remote(MCPServerConfig(name="stub", transport="remote", url=server.url))
        self.assertEqual(probe.status, "connected")
        self.assertEqual(len(probe.tools), 2)

    def test_probe_remote_auth_missing(self):
        cfg = MCPServerConfig(
            name="stub",
            transport="remote",
            url="https://example.invalid/mcp",
            missing_env=["TOKEN"],
        )
        probe = probe_remote(cfg)
        self.assertEqual(probe.status, "auth_missing")
        self.assertIn("TOKEN", probe.error)

    def test_probe_all_modes_agree(self):
        with StubServer() as server:
            cfgs = [
                MCPServerConfig(name=f"s{i}", transport="remote", url=server.url) for i in range(4)
            ]
            results = {}
            for mode in ("sequential", "threads", "async"):
                probes = probe_all(cfgs, mode=mode, retries=0)
                results[mode] = {p.name: p.status for p in probes}
        for mode in results:
            self.assertEqual(results[mode], {f"s{i}": "connected" for i in range(4)})
        self.assertEqual(results["sequential"], results["async"])

    def test_probe_all_async_is_concurrent(self):
        # The assertion is wall-clock based, so under CI load scheduler jitter
        # can violate the margin even when async is genuinely concurrent.
        # Retry measurement rounds and pass if any round demonstrates it.
        with StubServer() as server:
            cfgs = [
                MCPServerConfig(name=f"s{i}", transport="remote", url=server.url) for i in range(4)
            ]
            last_err = None
            for _ in range(3):
                start = time.perf_counter()
                probe_all(cfgs, mode="sequential", retries=0)
                sequential = time.perf_counter() - start
                start = time.perf_counter()
                probe_all(cfgs, mode="async", retries=0)
                concurrent = time.perf_counter() - start
                # Each tools/list sleeps 0.12s; 4 sequential = ~0.48s,
                # concurrent ~0.12s.
                try:
                    self.assertLess(concurrent, sequential * 0.75, (concurrent, sequential))
                    return
                except AssertionError as exc:
                    last_err = exc
            raise last_err

    def test_stdio_disabled_by_default(self):
        cfg = MCPServerConfig(name="local", transport="stdio", command=["python3", "-c", "pass"])
        probes = probe_all([cfg], mode="async", retries=0)
        self.assertEqual(probes[0].status, "unreachable")
        self.assertIn("disabled", probes[0].error)

    def test_snapshot_shape(self):
        probe = ServerProbe(
            name="stub",
            transport="remote",
            status="connected",
            tools=[ToolRecord(server="stub", name="web_search", categories=["web_search"])],
        )
        snap = build_snapshot([probe], elapsed_ms=1.0, mode="async")
        self.assertEqual(snap["summary"]["servers_reachable"], 1)
        self.assertEqual(snap["summary"]["tools_total"], 1)
        self.assertIn("gaps", snap)
        self.assertIn("generated_at", snap)


if __name__ == "__main__":
    unittest.main()
