#!/usr/bin/env python3
"""Receive a hash-verified, data-only Barrot bundle into a local Termux inbox.

Only immutable raw files from Barrot-Agent/B-Agent are accepted. Bundle contents
are never executed and existing destination files are never overwritten.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import hashlib
import hmac
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

MAX_MANIFEST_BYTES = 2_000_000
MAX_PAYLOAD_BYTES = 1_000_000
HOST = "raw.githubusercontent.com"
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
HASH_RE = re.compile(r"^[0-9a-fA-F]{64}$")
URL_RE = re.compile(r"^/Barrot-Agent/B-Agent/([0-9a-f]{40})/data/termux_bundles/([A-Za-z0-9][A-Za-z0-9._-]{0,127})\.json$")


class BundleReceiveError(ValueError):
    """Raised when a bundle fails source, schema, integrity, or path checks."""


def validate_url(url: str) -> tuple[str, str]:
    if not isinstance(url, str):
        raise BundleReceiveError("Manifest URL must be a string.")
    parsed = urlparse(url)
    if (parsed.scheme != "https" or parsed.hostname != HOST or
            parsed.username is not None or parsed.password is not None or
            parsed.port not in (None, 443) or parsed.query or parsed.fragment):
        raise BundleReceiveError("Only HTTPS raw.githubusercontent.com URLs are allowed.")
    match = URL_RE.fullmatch(parsed.path)
    if not match:
        raise BundleReceiveError("URL must pin a 40-character commit under Barrot-Agent/B-Agent/data/termux_bundles/<id>.json.")
    return match.group(1), match.group(2)


def _fetch(url: str) -> dict[str, object]:
    request = Request(url, headers={"User-Agent": "Barrot-Termux-Bundle-Receiver/1.0", "Accept": "application/json"})
    with urlopen(request, timeout=20) as response:
        validate_url(response.geturl())
        raw = response.read(MAX_MANIFEST_BYTES + 1)
    if len(raw) > MAX_MANIFEST_BYTES:
        raise BundleReceiveError("Manifest exceeds the 2 MB limit.")
    try:
        manifest = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise BundleReceiveError("Manifest is not valid UTF-8 JSON.") from exc
    if not isinstance(manifest, dict):
        raise BundleReceiveError("Manifest root must be an object.")
    return manifest


def receive_bundle(*, manifest_url: str, expected_sha256: str, destination: str | Path,
                   home_dir: str | Path | None = None) -> dict[str, object]:
    """Fetch and verify one bundle, then create it without overwriting files."""
    _, url_bundle_id = validate_url(manifest_url)
    if not isinstance(expected_sha256, str) or not HASH_RE.fullmatch(expected_sha256):
        raise BundleReceiveError("Expected SHA-256 must contain 64 hexadecimal characters.")
    home = Path(home_dir).expanduser().resolve() if home_dir is not None else Path.home().resolve()
    dest = Path(destination).expanduser().resolve()
    if dest == home or home not in dest.parents:
        raise BundleReceiveError("Destination must be a subdirectory of the home directory.")

    manifest = _fetch(manifest_url)
    if manifest.get("schema_version") != 1:
        raise BundleReceiveError("Unsupported manifest schema_version.")
    bundle_id = manifest.get("bundle_id")
    if not isinstance(bundle_id, str) or not ID_RE.fullmatch(bundle_id) or bundle_id != url_bundle_id:
        raise BundleReceiveError("Manifest bundle_id is invalid or does not match the URL.")
    filename = manifest.get("filename")
    if not isinstance(filename, str) or not ID_RE.fullmatch(filename) or filename in {".", ".."}:
        raise BundleReceiveError("Manifest filename must be a simple basename.")
    encoded = manifest.get("content_base64")
    if not isinstance(encoded, str):
        raise BundleReceiveError("Manifest content_base64 must be a string.")
    try:
        payload = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise BundleReceiveError("Manifest content_base64 is invalid.") from exc
    if len(payload) > MAX_PAYLOAD_BYTES:
        raise BundleReceiveError("Bundle exceeds the 1 MB payload limit.")
    actual = hashlib.sha256(payload).hexdigest()
    claimed = manifest.get("sha256")
    if not isinstance(claimed, str) or not HASH_RE.fullmatch(claimed):
        raise BundleReceiveError("Manifest SHA-256 is invalid.")
    if not hmac.compare_digest(actual, claimed.lower()):
        raise BundleReceiveError("Payload SHA-256 does not match the manifest.")
    if not hmac.compare_digest(actual, expected_sha256.lower()):
        raise BundleReceiveError("Payload SHA-256 does not match the expected hash.")

    dest.mkdir(parents=True, exist_ok=True)
    dest = dest.resolve()
    if dest == home or home not in dest.parents:
        raise BundleReceiveError("Resolved destination escapes the home directory.")
    target = dest / filename
    if target.exists() or target.is_symlink():
        raise FileExistsError(f"Refusing to overwrite existing path: {target}")

    temp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile("wb", prefix=".barrot-receive-", dir=dest, delete=False) as temp:
            temp_path = temp.name
            temp.write(payload)
            temp.flush()
            os.fsync(temp.fileno())
        # Atomic create-if-absent; link fails instead of overwriting a raced target.
        os.link(temp_path, target)
    except FileExistsError:
        raise FileExistsError(f"Refusing to overwrite existing path: {target}")
    finally:
        if temp_path is not None:
            try:
                os.unlink(temp_path)
            except FileNotFoundError:
                pass

    return {"verified": True, "bundle_id": bundle_id, "path": str(target),
            "bytes": len(payload), "sha256": actual, "source_url": manifest_url,
            "received_at": datetime.now(timezone.utc).isoformat(),
            "executed": False, "git_modified": False}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Receive a verified Barrot bundle; never execute it.")
    parser.add_argument("--manifest-url", required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--destination", default=str(Path.home() / "barrot" / "Barrot-Agent" / ".barrot" / "inbox"))
    args = parser.parse_args(argv)
    try:
        result = receive_bundle(manifest_url=args.manifest_url, expected_sha256=args.expected_sha256, destination=args.destination)
    except Exception as exc:
        print(json.dumps({"verified": False, "error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
