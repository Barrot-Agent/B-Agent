#!/usr/bin/env python3
"""CLI for the live concurrent MCP synchronization engine.

Examples:
    python scripts/mcp_sync.py
    python scripts/mcp_sync.py --benchmark
    python scripts/mcp_sync.py --mode sequential --no-cache
    python scripts/mcp_sync.py --include-local-exec
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from barrot_agent.mcp_sync import (  # noqa: E402
    load_cache,
    load_configs,
    probe_all,
    build_snapshot,
    merge_cached,
    synchronize,
    write_outputs,
)


def _print_summary(snapshot: dict) -> None:
    summary = snapshot["summary"]
    print(
        f"MCP sync [{snapshot['mode']}] {snapshot['elapsed_ms']}ms: "
        f"{summary['servers_reachable']}/{summary['servers_total']} reachable "
        f"({summary['servers_live']} live), {summary['tools_total']} tools "
        f"({summary['tools_live']} live), {summary['gaps_total']} gaps "
        f"({summary['gaps_filled_static']} with static candidates)"
    )
    for name, server in snapshot["servers"].items():
        tool_count = len(server["tools"])
        detail = server["status"]
        if server["source"] != "live":
            detail += f"/{server['source']}"
        if server["error"]:
            detail += f" - {server['error'][:90]}"
        print(f"  - {name:<28} {detail:<22} {tool_count:>3} tools")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synchronize all configured MCP servers concurrently.")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--out-dir", type=Path, default=REPO_ROOT / "results" / "mcp_sync")
    parser.add_argument("--mode", choices=("async", "threads", "sequential"), default="threads")
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--retries", type=int, default=1)
    parser.add_argument("--include-local-exec", action="store_true")
    parser.add_argument("--no-cache", action="store_true", help="do not back-fill from last_good.json")
    parser.add_argument("--benchmark", action="store_true", help="time all three modes and keep the fastest")
    parser.add_argument("--json", action="store_true", help="print the full snapshot to stdout")
    args = parser.parse_args(argv)

    if args.benchmark:
        servers = load_configs(args.repo_root)
        cache_path = None if args.no_cache else args.out_dir / "last_good.json"
        results = []
        for mode in ("sequential", "threads", "async"):
            start = time.perf_counter()
            probes = probe_all(
                servers,
                mode=mode,
                timeout=args.timeout,
                retries=args.retries,
                include_local_exec=args.include_local_exec,
            )
            cached = load_cache(cache_path) if cache_path else {}
            probes = merge_cached(probes, cached)
            elapsed_ms = (time.perf_counter() - start) * 1000
            snapshot = build_snapshot(probes, elapsed_ms, mode)
            results.append(snapshot)
            _print_summary(snapshot)
        winner = min(results, key=lambda s: s["elapsed_ms"])
        print(f"\nWinner: {winner['mode']} ({winner['elapsed_ms']}ms)")
        paths = write_outputs(winner, args.out_dir)
        print(f"Snapshot: {paths['snapshot']}")
        if args.json:
            print(json.dumps(winner, indent=2, sort_keys=True))
        return 0

    cache_path = None if args.no_cache else args.out_dir / "last_good.json"
    snapshot = synchronize(
        args.repo_root,
        mode=args.mode,
        timeout=args.timeout,
        retries=args.retries,
        include_local_exec=args.include_local_exec,
        cache_path=cache_path,
    )
    _print_summary(snapshot)
    paths = write_outputs(snapshot, args.out_dir)
    print(f"Snapshot: {paths['snapshot']}")
    print(f"Cache:    {paths['cache']}")
    if args.json:
        print(json.dumps(snapshot, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
