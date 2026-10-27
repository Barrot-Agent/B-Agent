#!/usr/bin/env python3
"""
Adds getBarrotBenchmark and getBarrotAudit gated WebMCP tools to
web/landing.html. Inserted right before the closing IIFE. Fails closed
if the expected insertion point isn't found.

Usage:
  python3 scripts/patch_add_transparency_tools.py            # dry run
  python3 scripts/patch_add_transparency_tools.py --apply    # writes the file
"""
import sys
import difflib
from pathlib import Path

LANDING = Path("web/landing.html")
ANCHOR = "})();\n</script>"

NEW_TOOLS = """  mcp.registerTool({
    name: "getBarrotBenchmark",
    title: "Barrot Self-Benchmark History",
    description: "Get Barrot's real, machine-graded coding-task benchmark history (generated code executed against real assertions, not self-reported). Includes every run, including failures. Measures coding-benchmark performance, not trading signal accuracy - see getSignalAccuracy for that.",
    inputSchema: { type: "object", properties: {
        license_key: { type: "string", description: "Gumroad license key for XRP Signal Service" },} },
    annotations: { readOnlyHint: true },
    execute: async function(args) {
      const __lic = await window.__webmcpMonetization.verifyGumroadLicense(args.license_key);
      if (!__lic.valid) return window.__webmcpMonetization.paywallResponse('getBarrotBenchmark');
      var res = await fetch("benchmark_summary.json");
      if (!res.ok) return { error: "data_unavailable" };
      return await res.json();
    }
  });
  mcp.registerTool({
    name: "getBarrotAudit",
    title: "Barrot Self-Audit Summary",
    description: "Get the latest real static-analysis audit of Barrot's own codebase (apex_lattice), run weekly. Counts of real findings/recommendations only, not full detail. No PRs are opened by this process.",
    inputSchema: { type: "object", properties: {
        license_key: { type: "string", description: "Gumroad license key for XRP Signal Service" },} },
    annotations: { readOnlyHint: true },
    execute: async function(args) {
      const __lic = await window.__webmcpMonetization.verifyGumroadLicense(args.license_key);
      if (!__lic.valid) return window.__webmcpMonetization.paywallResponse('getBarrotAudit');
      var res = await fetch("apex_audit_summary.json");
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

    if "getBarrotBenchmark" in src:
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
