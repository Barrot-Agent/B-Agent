"""Deterministic repository-reference corroboration."""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


FAILURE_MISSING_FILE = "MISSING_REFERENCED_FILE"
FAILURE_WRONG_TYPE = "WRONG_REFERENCE_TYPE"
FAILURE_SYMBOL_MISSING = "SYMBOL_MISSING"
FAILURE_HASH_MISMATCH = "FILE_HASH_MISMATCH"
FAILURE_STALE_MANIFEST = "REPO_STATE_STALE"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _symbol_exists(path: Path, symbol: str) -> bool:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return False

    return any(
        isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
        )
        and node.name == symbol
        for node in ast.walk(tree)
    )


class RepoStateCorroborator:
    """Validate model repository references against an observed manifest."""

    def __init__(self, workspace: str | Path):
        self.workspace = Path(workspace).resolve()
        self.manifest_path = (
            self.workspace / ".barrot" / "repo_state_manifest.json"
        )

    def load_manifest(self) -> dict:
        return json.loads(
            self.manifest_path.read_text(encoding="utf-8")
        )

    def corroborate(
        self,
        *,
        manifest_id: str,
        references: list[dict],
    ) -> dict:
        manifest = self.load_manifest()

        if manifest_id != manifest.get("manifest_id"):
            return {
                "status": "BLOCKED",
                "failure": {
                    "class": FAILURE_STALE_MANIFEST,
                    "provided": manifest_id,
                    "current": manifest.get("manifest_id"),
                },
                "manifest_id": manifest.get("manifest_id"),
            }

        manifest_files = set(manifest["tree"]["files"])
        failures = []

        for reference in references:
            path = str(reference["path"]).replace("\\", "/").lstrip("./")
            target = self.workspace / path

            if path not in manifest_files or not target.is_file():
                failures.append({
                    "class": FAILURE_MISSING_FILE,
                    "path": path,
                })
                continue

            expected_hash = manifest["file_hashes"].get(path)
            if expected_hash:
                actual_hash = _sha256(target)
                if actual_hash != expected_hash:
                    failures.append({
                        "class": FAILURE_HASH_MISMATCH,
                        "path": path,
                        "expected": expected_hash,
                        "actual": actual_hash,
                    })

            for symbol in reference.get("symbols", []):
                if not _symbol_exists(target, symbol):
                    failures.append({
                        "class": FAILURE_SYMBOL_MISSING,
                        "path": path,
                        "symbol": symbol,
                    })

        return {
            "status": "BLOCKED" if failures else "PASS",
            "manifest_id": manifest["manifest_id"],
            "failures": failures,
        }


def extract_path_references(text: str) -> list[str]:
    """Extract plausible repository paths from generated text."""
    candidates = set()

    for token in text.replace("(", " ").replace(")", " ").split():
        token = token.strip("'\"` ,:;")
        if "/" in token and not token.startswith(("http://", "https://")):
            candidates.add(token)

    return sorted(candidates)
