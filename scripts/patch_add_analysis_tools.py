#!/usr/bin/env python3
"""
Adds 3 new gated WebMCP tools to web/landing.html: getEntityCooccurrence,
getSentimentShift, getEntitySentimentProfile. Inserted right before the
closing IIFE. Fails closed if the expected insertion point isn't found.

Usage:
  python3 scripts/patch_add_analysis_tools.py            # dry run
  python3 scripts/patch_add_analysis_tools.py --apply    # writes the file
"""
import sys
import difflib
from pathlib import Path

LANDING = Path("web/landing.html")
ANCHOR = "})();\n</script>"

NEW_TOOLS = """  mcp.registerTool({
    name: "getEntityCooccurrence",
    title: "Entity Co-occurrence",
    description: "Get pairs of named entities that frequently appear together in the same XRP/BTC news items, with example headlines.",
    inputSchema: { type: "object", properties: {
        license_key: { type: "string", description: "Gumroad license key for XRP Signal Service" },} },
    annotations: { readOnlyHint: true },
    execute: async function(args) {
      const __lic = await window.__webmcpMonetization.verifyGumroadLicense(args.license_key);
      if (!__lic.valid) return window.__webmcpMonetization.paywallResponse('getEntityCooccurrence');
      var res = await fetch("entity_cooccurrence.json");
      if (!res.ok) return { error: "data_unavailable" };
      return await res.json();
    }
  });
  mcp.registerTool({
    name: "getSentimentShift",
    title: "Sentiment Shift Detector",
    description: "Get the 24h vs prior-24h sentiment shift for XRP and BTC, flagged if the shift is significant.",
    inputSchema: { type: "object", properties: {
        license_key: { type: "string", description: "Gumroad license key for XRP Signal Service" },} },
    annotations: { readOnlyHint: true },
    execute: async function(args) {
      const __lic = await window.__webmcpMonetization.verifyGumroadLicense(args.license_key);
      if (!__lic.valid) return window.__webmcpMonetization.paywallResponse('getSentimentShift');
      var res = await fetch("sentiment_shift.json");
      if (!res.ok) return { error: "data_unavailable" };
      return await res.json();
    }
  });
  mcp.registerTool({
    name: "getEntitySentimentProfile",
    title: "Entity Sentiment Profile",
    description: "Get the aggregated sentiment profile (bullish/bearish/neutral counts, net score) for named entities seen across XRP/BTC news.",
    inputSchema: { type: "object", properties: {
        license_key: { type: "string", description: "Gumroad license key for XRP Signal Service" },} },
    annotations: { readOnlyHint: true },
    execute: async function(args) {
      const __lic = await window.__webmcpMonetization.verifyGumroadLicense(args.license_key);
      if (!__lic.valid) return window.__webmcpMonetization.paywallResponse('getEntitySentimentProfile');
      var res = await fetch("entity_sentiment_profile.json");
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

    if "getEntityCooccurrence" in src:
        print("Already patched - tools already present. No changes made.")
        return

    if ANCHOR not in src:
        print("FAIL CLOSED: closing IIFE anchor not found. No changes made.")
        sys.exit(1)

    new_src = src.replace(ANCHOR, NEW_TOOLS + ANCHOR, 1)

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
