#!/usr/bin/env python3
"""
Adds a gated getWebMCPTrendDigest WebMCP tool to web/landing.html - exposes
the ranked candidate-tool-idea digest surfaced from real public WebMCP
discourse. Inserted right before the closing IIFE. Fails closed if the
expected insertion point isn't found.

Usage:
  python3 scripts/patch_add_trend_digest_tool.py            # dry run
  python3 scripts/patch_add_trend_digest_tool.py --apply    # writes the file
"""
import sys
import difflib
from pathlib import Path

LANDING = Path("web/landing.html")
ANCHOR = "})();\n</script>"

NEW_TOOL = """  mcp.registerTool({
    name: "getWebMCPTrendDigest",
    title: "WebMCP Trend Digest",
    description: "Get a ranked digest of candidate future WebMCP tool ideas, surfaced from real public developer discourse (news, announcements) about WebMCP and agentic browsing - not invented predictions.",
    inputSchema: { type: "object", properties: {
        license_key: { type: "string", description: "Gumroad license key for XRP Signal Service" },} },
    annotations: { readOnlyHint: true },
    execute: async function(args) {
      const __lic = await window.__webmcpMonetization.verifyGumroadLicense(args.license_key);
      if (!__lic.valid) return window.__webmcpMonetization.paywallResponse('getWebMCPTrendDigest');
      var res = await fetch("webmcp_trend_summary.json");
      if (!res.ok) return { error: "data_unavailable" };
      return await res.json();
    }
  });
"""


def main():
    apply = "--apply" in sys.argv
    if not LANDING.exists():
        print(f"FAIL CLOSED: {LANDING} not found. No changes made.")
        sys.exit(1)
    src = LANDING.read_text(encoding="utf-8")

    if "getWebMCPTrendDigest" in src:
        print("Already patched - tool already present. No changes made.")
        return

    if ANCHOR not in src:
        print("FAIL CLOSED: closing IIFE anchor not found. No changes made.")
        sys.exit(1)

    new_src = src.replace(ANCHOR, NEW_TOOL + ANCHOR, 1)

    diff = difflib.unified_diff(
        src.splitlines(keepends=True),
        new_src.splitlines(keepends=True),
        fromfile="web/landing.html (before)",
        tofile="web/landing.html (after)",
    )
    print("".join(diff))

    if apply:
        LANDING.write_text(new_src, encoding="utf-8")
        print(f"\nApplied. {LANDING} updated.")
    else:
        print("\nDry run only. Re-run with --apply to write these changes.")


if __name__ == "__main__":
    main()
