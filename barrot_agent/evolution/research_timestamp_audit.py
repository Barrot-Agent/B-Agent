"""Read-only scheduled audit of XRP research timestamp correction overlays."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .research_timestamp_corrections import apply_research_timestamp_correction_overlays


def build_audit_payload(repository_root: str | Path) -> dict[str, Any]:
    """Build a deterministic, research-only correction view without source writes."""
    result = apply_research_timestamp_correction_overlays(repository_root)
    return {
        "schema_version": "barrot.xrp.research-correction-audit.v1",
        "archive_root": result["archive_root"],
        "overlay_count": result["overlay_count"],
        "application_manifests": result["application_manifests"],
        "corrected_artifacts": result["corrected_artifacts"],
        "narrative_only_correction_artifacts": result["narrative_only_correction_artifacts"],
        "unbound_timestamp_correction_artifacts": result["unbound_timestamp_correction_artifacts"],
        "source_artifacts_modified": False,
        "model_eligible": False,
        "forecast_issued": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", required=True)
    parser.add_argument("--output", required=True, help="New output file outside the repository root")
    args = parser.parse_args(argv)

    root = Path(args.repository_root)
    if root.is_symlink():
        raise SystemExit("repository root must not be a symlink")
    try:
        root = root.resolve(strict=True)
    except OSError as exc:
        raise SystemExit("repository root must be an existing directory") from exc
    if not root.is_dir():
        raise SystemExit("repository root must be a directory")

    output = Path(args.output).expanduser()
    if output.is_symlink() or output.exists():
        raise SystemExit("audit output must be a new, non-symlink file")
    resolved_output = output.resolve(strict=False)
    if resolved_output == root or resolved_output.is_relative_to(root):
        raise SystemExit("audit output must be outside the repository root")

    payload = build_audit_payload(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with output.open("x", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False)
            handle.write("\n")
    except FileExistsError as exc:
        raise SystemExit("audit output already exists; refusing to overwrite") from exc
    print(json.dumps({
        "overlay_count": payload["overlay_count"],
        "source_artifacts_modified": False,
        "model_eligible": False,
        "forecast_issued": False,
        "output": str(resolved_output),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
