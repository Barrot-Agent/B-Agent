#!/usr/bin/env python3
"""
BARROT-Omega WEBMCP LIVE EXECUTION SANDBOX.

Runs the tools registered by the real landing page in a local Chromium
sandbox. The run fails closed if the page registers no tools, omits an
expected tool, raises a page error, or any tool execution fails.

Network scope is intentionally local-only. External requests and popups
are blocked. License-gated tools are invoked without a key, so this run
tests their unauthenticated paywall path, not licensed data retrieval.
"""

import http.server
import json
import sys
import threading
import time
from pathlib import Path
from urllib.parse import urlparse

WEB_DIR = Path("web")
RESULT_LOG = Path("ping-pongings/knowledge-base/webmcp_sandbox_log.jsonl")
EXPECTED_TOOL_NAMES = frozenset({
    "getLatestXRPSignal",
    "getResearchBasis",
    "subscribeToXRPSignals",
    "getSignalAccuracy",
    "getLatestBTCSignal",
    "getEntityCooccurrence",
    "getSentimentShift",
    "getEntitySentimentProfile",
    "getWebMCPTrendDigest",
    "getBarrotBenchmark",
    "getBarrotAudit",
    "getWebMCPMonetizationSignals",
    "getFinancialLiteracyData",
})

_POLYFILL_JS = """
(() => {
  window.__registeredTools = [];
  const mcp = {
    registerTool: (tool) => { window.__registeredTools.push(tool); },
  };
  Object.defineProperty(document, 'modelContext', { value: mcp, configurable: true });
  Object.defineProperty(navigator, 'modelContext', { value: mcp, configurable: true });
})();
"""


def _is_local_sandbox_url(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme == "http" and parsed.hostname == "127.0.0.1"


def _route_local_only(route) -> None:
    if _is_local_sandbox_url(route.request.url):
        route.continue_()
    else:
        route.abort()


def _require_expected_tools(tool_names, page_errors):
    names = set(tool_names or [])
    missing = sorted(EXPECTED_TOOL_NAMES - names)
    if not names:
        raise RuntimeError("WebMCP sandbox registered zero tools; refusing a false-success run")
    if missing:
        raise RuntimeError("WebMCP sandbox is missing expected tools: " + ", ".join(missing))
    if page_errors:
        raise RuntimeError("WebMCP page errors: " + " | ".join(page_errors[:5]))
    return sorted(names - EXPECTED_TOOL_NAMES)


def _serve_dir(directory: Path, port: int):
    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(
        *a, directory=str(directory), **kw
    )
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def run_sandbox(html_path: Path, port: int = 8791) -> dict:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("playwright not installed - pip install playwright && playwright install chromium")

    server = _serve_dir(html_path.parent, port)
    time.sleep(0.3)
    results = []
    page_errors = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            context = browser.new_context()
            context.route("**/*", _route_local_only)
            page = context.new_page()
            page.on("pageerror", lambda exc: page_errors.append(str(exc)))
            page.on("popup", lambda popup: popup.close())
            page.add_init_script(_POLYFILL_JS)
            page.goto(f"http://127.0.0.1:{port}/{html_path.name}", wait_until="load")
            try:
                page.wait_for_function(
                    "Array.isArray(window.__registeredTools) && window.__registeredTools.length > 0",
                    timeout=5000,
                )
            except Exception as exc:
                raise RuntimeError(
                    "WebMCP registration timed out; page errors: " + " | ".join(page_errors[:5])
                ) from exc

            tool_count = page.evaluate("window.__registeredTools.length")
            tool_names = page.evaluate("window.__registeredTools.map(t => t.name)")
            unexpected = _require_expected_tools(tool_names, page_errors)

            for i in range(tool_count):
                meta = page.evaluate(
                    f"""() => {{
                        const t = window.__registeredTools[{i}];
                        return {{
                            name: t.name,
                            description: t.description,
                            requires_license: Boolean(t.inputSchema && t.inputSchema.properties && t.inputSchema.properties.license_key)
                        }};
                    }}"""
                )
                try:
                    output = page.evaluate(
                        f"""async () => {{
                            const t = window.__registeredTools[{i}];
                            const result = await t.execute({{}});
                            return JSON.parse(JSON.stringify(result));
                        }}"""
                    )
                    results.append({
                        "tool": meta["name"],
                        "invoked": True,
                        "auth_mode": "unauthenticated_paywall_path_only" if meta["requires_license"] else "public_tool_execution",
                        "output_preview": json.dumps(output)[:300],
                        "error": None,
                    })
                except Exception as exc:
                    results.append({
                        "tool": meta.get("name", f"unnamed_{i}"),
                        "invoked": False,
                        "auth_mode": "unauthenticated_paywall_path_only" if meta.get("requires_license") else "public_tool_execution",
                        "output_preview": None,
                        "error": str(exc)[:500],
                    })

            if page_errors:
                raise RuntimeError("WebMCP page errors during execution: " + " | ".join(page_errors[:5]))
            failures = [item for item in results if not item["invoked"]]
            if failures:
                details = "; ".join(f"{item['tool']}: {item['error']}" for item in failures)
                raise RuntimeError("WebMCP tool execution failures: " + details)

            browser.close()
            return {
                "registered_tool_count": tool_count,
                "expected_tool_count": len(EXPECTED_TOOL_NAMES),
                "unexpected_tool_names": unexpected,
                "external_network_blocked": True,
                "popups_closed": True,
                "license_gated_tools_scope": "unauthenticated paywall path only; licensed data paths not exercised",
                "tools": results,
            }
    finally:
        server.shutdown()
        server.server_close()


def main():
    html_files = list(WEB_DIR.glob("*.html"))
    all_results = {}
    for html_path in html_files:
        source = html_path.read_text(encoding="utf-8", errors="replace")
        if "registerTool" not in source:
            continue
        print(f"Running live sandbox against {html_path}...")
        result = run_sandbox(html_path)
        all_results[str(html_path)] = result
        for item in result["tools"]:
            print(f"  [OK] {item['tool']} ({item['auth_mode']})")

    if not all_results:
        sys.exit("No WebMCP-registered HTML files found; refusing a false-success run")

    RESULT_LOG.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "files": all_results,
        "network_scope": "localhost-only",
        "licensed_data_paths_exercised": False,
    }
    with open(RESULT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


if __name__ == "__main__":
    main()
