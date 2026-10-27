#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BUNDLE = ROOT / "data" / "research" / "anthropic_fermats_last_theorem_bundle.json"
ROOT_STR = str(ROOT)
if ROOT_STR not in sys.path:
    sys.path.insert(0, ROOT_STR)

from barrot_agent.research import (  # noqa: E402
    ANTHROPIC_FLT_IMPORT_CONFIG,
    DEFAULT_ANTHROPIC_FLT_ARCHIVE,
    ExternalLeanProjectImporter,
    ScientificDiscoveryController,
    StaticResearchProblemAdapter,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a formal verification benchmark import/build cycle.")
    parser.add_argument("--workspace", default=str(ROOT), help="Workspace used for Barrot research ledger output.")
    parser.add_argument("--bundle-out", default="", help="Where to write the generated research bundle.")
    parser.add_argument("--report-out", default="", help="Where to write the resulting research cycle JSON.")
    parser.add_argument("--project-root", default="", help="Existing local external Lean project root.")
    parser.add_argument("--archive-url", default=DEFAULT_ANTHROPIC_FLT_ARCHIVE, help="Archive URL used when project-root is not provided.")
    parser.add_argument("--attempt-build", action="store_true", help="Attempt the external Lean build/check commands.")
    parser.add_argument("--timeout", type=int, default=900, help="Timeout in seconds for each formal verification command.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    importer = ExternalLeanProjectImporter()
    with tempfile.TemporaryDirectory(prefix="barrot-formal-benchmark-") as tmp_dir:
        bundle_path = Path(args.bundle_out).resolve() if args.bundle_out else Path(tmp_dir) / "anthropic_flt_bundle.json"
        if args.project_root:
            project_root = Path(args.project_root).resolve()
            importer.materialize_bundle(project_root, ANTHROPIC_FLT_IMPORT_CONFIG, bundle_path)
        elif args.attempt_build:
            project_root = importer.download_archive(args.archive_url, tmp_dir)
            importer.materialize_bundle(project_root, ANTHROPIC_FLT_IMPORT_CONFIG, bundle_path)
        else:
            project_root = None
            shutil.copyfile(DEFAULT_BUNDLE, bundle_path)
        bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
        if bundle.get("formal_verification"):
            bundle["formal_verification"][0]["timeout"] = args.timeout
            if args.attempt_build and project_root is not None:
                bundle["formal_verification"][0]["repository_path"] = str(project_root)
        bundle_path.write_text(json.dumps(bundle, indent=2, sort_keys=True), encoding="utf-8")
        cycle = ScientificDiscoveryController(workspace=Path(args.workspace).resolve()).run(StaticResearchProblemAdapter(bundle_path))
        rendered = json.dumps(cycle.to_dict(), indent=2, sort_keys=True)
        print(rendered)
        if args.report_out:
            Path(args.report_out).resolve().write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
