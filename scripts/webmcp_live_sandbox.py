#!/usr/bin/env python3
"""
BARROT-Omega WEBMCP LIVE EXECUTION SANDBOX.

The schema validator (apex_lattice/analyzers/webmcp_analyzer.py) checks
tool contracts statically. This actually runs them: serves the real
repo's web/ directory, loads the real HTML in a headless Chromium via
Playwright, injects a minimal real polyfill for document.modelContext
(matching the actual WebMCP registerTool contract - the same approach
the MCP-B project's real polyfill uses, since no CI runner has a native
Chrome origin-trial build), captures every tool the page's own script
registers, then actually calls each tool's real execute() function in
the page and checks the real result.

Honest scope: this proves the tools don't crash and return
JSON-serializable data when actually invoked. It does not prove an
external agent would choose to call them correctly - that requires a
real agent client, which per current WebMCP coverage (July 2026) doesn't
exist yet for any mainstream product.
"""

import http.server
import json
import sys
import threading
import time
from pathlib import Path

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sys.exit("playwright not installed - pip install playwright && playwright install chromium")

WEB_DIR = Path("web")
RESULT_LOG = Path("ping-pongings/knowledge-base/webmcp_sandbox_log.jsonl")

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


def _serve_dir(directory: Path, port: int):
    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(
        *a, directory=str(directory), **kw
    )
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def run_sandbox(html_path: Path, port: int = 8791) -> list[dict]:
    server = _serve_dir(html_path.parent, port)
    time.sleep(0.3)
    results = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.on("dialog", lambda d: d.dismiss())
            page.add_init_script(_POLYFILL_JS)
            page.goto(f"http://127.0.0.1:{port}/{html_path.name}", wait_until="load")

            tool_count = page.evaluate("window.__registeredTools.length")
            for i in range(tool_count):
                meta = page.evaluate(
                    f"""() => {{
                        const t = window.__registeredTools[{i}];
                        return {{ name: t.name, description: t.description }};
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
                    json.dumps(output)
                    results.append(
                        {
                            "tool": meta["name"],
                            "invoked": True,
                            "output_preview": json.dumps(output)[:300],
                            "error": None,
                        }
                    )
                except Exception as exc:
                    results.append(
                        {
                            "tool": meta.get("name", f"unnamed_{i}"),
                            "invoked": False,
                            "output_preview": None,
                            "error": str(exc)[:300],
                        }
                    )
            browser.close()
    finally:
        server.shutdown()
    return results


def main():
    html_files = list(WEB_DIR.glob("*.html"))
    all_results = {}
    for html_path in html_files:
        source = html_path.read_text(encoding="utf-8", errors="replace")
        if "registerTool" not in source:
            continue
        print(f"Running live sandbox against {html_path}...")
        results = run_sandbox(html_path)
        all_results[str(html_path)] = results
        for r in results:
            status = "OK" if r["invoked"] else "FAIL"
            detail = r["output_preview"] if r["invoked"] else r["error"]
            print(f"  [{status}] {r['tool']}: {detail}")

    if not all_results:
        print("No WebMCP-registered tools found in web/*.html")
        return

    RESULT_LOG.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "run_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "files": all_results,
    }
    with open(RESULT_LOG, "a") as f:
        f.write(json.dumps(record) + "\n")


if __name__ == "__main__":
    main()
