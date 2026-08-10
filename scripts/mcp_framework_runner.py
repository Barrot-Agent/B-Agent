#!/usr/bin/env python3
"""
Run Barrot's MCP integration framework in dry-run or full-auto mode.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from barrot_agent.mcp_integration import IntegrationConfig, MCPIntegration


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run MCP integration pipeline and assemble framework registry entries."
    )
    parser.add_argument(
        "--full-auto",
        action="store_true",
        help=(
            "Enable full-auto assembly mode (dry_run=False, approval_mode=always_allow). "
            "Use only in trusted environments."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Force dry-run mode (default when --full-auto is not set).",
    )
    parser.add_argument(
        "--min-score",
        type=float,
        default=50.0,
        help="Minimum score threshold for component proposals (default: 50.0).",
    )
    parser.add_argument(
        "--pingpong-max-cycles",
        type=int,
        default=3,
        help="Maximum ping-pong refinement cycles per proposal (default: 3).",
    )
    parser.add_argument(
        "--repo-root",
        default=str(REPO_ROOT),
        help="Repository root used by sandbox checks (default: inferred repo root).",
    )
    parser.add_argument(
        "--registry-path",
        default=None,
        help="Optional registry JSON output path override.",
    )
    parser.add_argument(
        "--provenance-path",
        default=None,
        help="Optional provenance JSONL output path override.",
    )
    return parser


def main() -> int:
    args = _build_parser().parse_args()

    full_auto = bool(args.full_auto)
    dry_run = bool(args.dry_run) or not full_auto
    approval_mode = "always_allow" if full_auto else "always_deny"

    cfg = IntegrationConfig(
        dry_run=dry_run,
        approval_mode=approval_mode,
        interactive_approval=False,
        min_score=args.min_score,
        pingpong_max_cycles=args.pingpong_max_cycles,
        repo_root=Path(args.repo_root),
        registry_path=Path(args.registry_path) if args.registry_path else None,
        provenance_path=Path(args.provenance_path) if args.provenance_path else None,
    )
    integration = MCPIntegration(cfg)
    stats = integration.run_pipeline()

    payload = {
        "mode": "full-auto" if full_auto else "dry-run",
        "config": {
            "dry_run": cfg.dry_run,
            "approval_mode": cfg.approval_mode,
            "min_score": cfg.min_score,
            "pingpong_max_cycles": cfg.pingpong_max_cycles,
            "repo_root": str(cfg.repo_root),
            "registry_path": str(cfg.registry_path) if cfg.registry_path else None,
            "provenance_path": str(cfg.provenance_path) if cfg.provenance_path else None,
        },
        "stats": stats,
        "active_registry_entries": len(integration.registry.list_active()),
    }
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
