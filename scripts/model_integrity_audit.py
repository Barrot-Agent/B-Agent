#!/usr/bin/env python3
"""Read-only model/checkpoint integrity audit; never loads model tensors."""
from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import sys
from typing import Any

METADATA_NAMES = {
    "config.json", "generation_config.json", "tokenizer.json",
    "tokenizer_config.json", "special_tokens_map.json",
    "added_tokens.json", "vocab.json", "merges.txt", "vocab.txt",
    "spiece.model", "tokenizer.model", "model.safetensors.index.json",
    "pytorch_model.bin.index.json", "adapter_config.json",
    "quantization_config.json",
}
WEIGHT_SUFFIXES = {".safetensors", ".bin", ".pt", ".pth", ".gguf"}
SKIP_DIRS = {".git", "__pycache__", ".cache", "runs", "outputs"}


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_version(name: str) -> str | None:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return None


def discover(root: Path) -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    warnings: list[str] = []
    for current, dirs, names in os.walk(root, followlinks=False):
        current_path = Path(current)
        dirs[:] = sorted(
            name for name in dirs
            if name not in SKIP_DIRS
            and not (current_path / name).is_symlink()
        )
        for name in sorted(names):
            path = current_path / name
            if path.is_symlink():
                warnings.append(f"SYMLINK_SKIPPED:{path.relative_to(root)}")
                continue
            if name in METADATA_NAMES or path.suffix.lower() in WEIGHT_SUFFIXES:
                if path.is_file():
                    files.append(path)
    return sorted(files), warnings


def audit_model(root_arg: str, max_file_bytes: int) -> dict[str, Any]:
    supplied = Path(root_arg).expanduser()
    if supplied.is_symlink():
        raise ValueError("model root must not be a symlink")
    root = supplied.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("model root must be a directory")

    files, warnings = discover(root)
    records: list[dict[str, Any]] = []
    parsed: dict[str, Any] = {}
    for path in files:
        relative = path.relative_to(root).as_posix()
        size = path.stat().st_size
        record: dict[str, Any] = {
            "path": relative,
            "size_bytes": size,
            "kind": "weight" if path.suffix.lower() in WEIGHT_SUFFIXES else "metadata",
        }
        if size > max_file_bytes:
            record["sha256_status"] = "NOT_HASHED_SIZE_LIMIT"
            warnings.append(f"SIZE_LIMIT:{relative}:{size}")
        else:
            record["sha256"] = sha256_file(path)
            record["sha256_status"] = "HASHED"
        if path.name in METADATA_NAMES and path.suffix.lower() == ".json":
            try:
                value = json.loads(path.read_text(encoding="utf-8"))
                parsed[relative] = value
                record["json_status"] = "VALID"
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                record["json_status"] = "INVALID"
                record["json_error"] = type(exc).__name__
                warnings.append(f"INVALID_JSON:{relative}:{type(exc).__name__}")
        records.append(record)

    # Validate shard references without opening tensor payloads.
    for relative, value in parsed.items():
        if not relative.endswith((".safetensors.index.json", ".bin.index.json")):
            continue
        weight_map = value.get("weight_map", {}) if isinstance(value, dict) else {}
        shards = sorted(set(weight_map.values())) if isinstance(weight_map, dict) else []
        missing = [name for name in shards if not (root / name).is_file()]
        if missing:
            warnings.append(f"MISSING_SHARDS:{relative}:{','.join(missing)}")

    config = parsed.get("config.json", {})
    tokenizer = parsed.get("tokenizer_config.json", {})
    quant = config.get("quantization_config") if isinstance(config, dict) else None
    if quant is None and isinstance(parsed.get("quantization_config.json"), dict):
        quant = parsed["quantization_config.json"]
    adapter = parsed.get("adapter_config.json")
    return {
        "schema_version": "barrot.model_integrity_audit.v1",
        "audit_mode": "READ_ONLY_METADATA_AND_HASHES",
        "model_root": str(root),
        "model_identity": {
            "architectures": config.get("architectures") if isinstance(config, dict) else None,
            "model_type": config.get("model_type") if isinstance(config, dict) else None,
            "tokenizer_class": tokenizer.get("tokenizer_class") if isinstance(tokenizer, dict) else None,
            "model_max_length": tokenizer.get("model_max_length") if isinstance(tokenizer, dict) else None,
            "quantization": quant,
            "adapter_config_present": isinstance(adapter, dict),
        },
        "runtime": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "torch": package_version("torch"),
            "transformers": package_version("transformers"),
            "tokenizers": package_version("tokenizers"),
            "safetensors": package_version("safetensors"),
        },
        "files": records,
        "file_count": len(records),
        "weight_file_count": sum(item["kind"] == "weight" for item in records),
        "warnings": sorted(warnings),
        "limitations": [
            "This audit does not load model tensors or execute inference.",
            "A valid hash proves artifact identity, not correctness or trustworthiness.",
            "Tokenizer compatibility and model behavior require pinned runtime tests.",
            "No weights, configs, caches, or production files are modified.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model_dir", help="Local model/checkpoint directory")
    parser.add_argument("--max-file-bytes", type=int, default=10 * 1024**3,
                        help="Skip hashing files larger than this limit (default: 10 GiB)")
    parser.add_argument("--output", help="Write JSON report to this path; default is stdout")
    args = parser.parse_args()
    if args.max_file_bytes <= 0:
        parser.error("--max-file-bytes must be positive")
    try:
        report = audit_model(args.model_dir, args.max_file_bytes)
    except (OSError, ValueError) as exc:
        print(f"model-integrity-audit: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        destination = Path(args.output).expanduser()
        if destination.exists():
            print("model-integrity-audit: refusing to overwrite an existing report", file=sys.stderr)
            return 2
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
