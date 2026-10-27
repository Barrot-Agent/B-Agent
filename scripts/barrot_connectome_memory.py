#!/usr/bin/env python3

import ast
import hashlib
import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OUT = (
    ROOT
    / "ping-pongings"
    / "knowledge-base"
    / "barrot_connectome_memory.json"
)

IGNORE = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    "dist",
    "build",
    ".next",
    ".cache",
    ".apex_lattice",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
}

TEXT_EXT = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".yaml",
    ".yml",
    ".md",
    ".txt",
    ".sh",
    ".toml",
    ".html",
    ".css",
    ".sql",
}

MAX_SIZE = 1000000


def file_id(path):
    return hashlib.sha256(str(path).encode()).hexdigest()[:16]


def safe_read(path):
    try:
        raw = path.read_bytes()
        return raw.decode("utf-8", errors="replace")
    except Exception:
        return ""


def extract_python_symbols(text):
    symbols = []
    imports = []

    try:
        tree = ast.parse(text)
    except Exception:
        return symbols, imports

    for node in ast.walk(tree):

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef,
                ast.ClassDef,
            ),
        ):
            symbols.append(node.name)

        elif isinstance(node, ast.Import):

            for alias in node.names:
                imports.append(alias.name.split(".")[0])

        elif isinstance(node, ast.ImportFrom):

            if node.module:
                imports.append(node.module.split(".")[0])

    return sorted(set(symbols)), sorted(set(imports))


def extract_generic_dependencies(text):
    patterns = [
        r'from\s+[\'"]([^\'"]+)[\'"]',
        r'import\s+[\'"]([^\'"]+)[\'"]',
        r'require\([\'"]([^\'"]+)[\'"]\)',
    ]

    found = []

    for pattern in patterns:
        found.extend(re.findall(pattern, text))

    return sorted(set(found))


def classify_file(path, text):
    p = str(path)

    if "/workflows/" in p or ".github/workflows" in p:
        return "workflow"

    if "/scripts/" in p or p.startswith("scripts/"):
        return "control"

    if "test" in path.name.lower():
        return "validation"

    if "knowledge" in p or "memory" in p:
        return "memory"

    if "agent" in p.lower():
        return "agent"

    if "config" in path.name.lower():
        return "configuration"

    if path.suffix == ".py":
        return "python"

    if path.suffix in {".js", ".jsx", ".ts", ".tsx"}:
        return "application"

    return "resource"


def main():

    nodes = []
    edges = []
    symbol_index = defaultdict(list)

    all_files = []

    for path in ROOT.rglob("*"):

        if not path.is_file():
            continue

        rel = path.relative_to(ROOT)

        if any(part in IGNORE for part in rel.parts):
            continue

        if path.suffix.lower() not in TEXT_EXT:
            continue

        try:
            if path.stat().st_size > MAX_SIZE:
                continue
        except Exception:
            continue

        all_files.append(rel)

    for rel in all_files:

        path = ROOT / rel
        text = safe_read(path)

        node_id = file_id(rel)

        node = {
            "id": node_id,
            "path": str(rel),
            "type": classify_file(rel, text),
            "size": len(text.encode("utf-8")),
            "symbols": [],
            "dependencies": [],
        }

        if path.suffix == ".py":

            symbols, imports = extract_python_symbols(text)

            node["symbols"] = symbols
            node["dependencies"] = imports

        else:

            node["dependencies"] = extract_generic_dependencies(text)

        for symbol in node["symbols"]:
            symbol_index[symbol].append(node_id)

        nodes.append(node)

    path_lookup = {
        node["path"]: node["id"]
        for node in nodes
    }

    stem_lookup = defaultdict(list)

    for node in nodes:

        stem = Path(node["path"]).stem

        stem_lookup[stem].append(node["id"])

    for node in nodes:

        source = node["id"]

        for dependency in node["dependencies"]:

            dependency_name = dependency.split("/")[-1]
            dependency_name = dependency_name.split(".")[0]

            for target in stem_lookup.get(
                dependency_name,
                [],
            ):

                if target != source:

                    edges.append(
                        {
                            "source": source,
                            "target": target,
                            "type": "dependency",
                        }
                    )

    for node in nodes:

        path = ROOT / node["path"]
        text = safe_read(path)

        for symbol in node["symbols"]:

            references = len(
                re.findall(
                    rf"\b{re.escape(symbol)}\b",
                    text,
                )
            )

            if references > 1:

                edges.append(
                    {
                        "source": node["id"],
                        "target": node["id"],
                        "type": "internal_recurrence",
                        "symbol": symbol,
                        "weight": references,
                    }
                )

    incoming = defaultdict(int)
    outgoing = defaultdict(int)

    for edge in edges:

        outgoing[edge["source"]] += 1
        incoming[edge["target"]] += 1

    hubs = []

    for node in nodes:

        node_id = node["id"]

        connectivity = (
            incoming[node_id]
            + outgoing[node_id]
        )

        if connectivity > 0:

            hubs.append(
                {
                    "id": node_id,
                    "path": node["path"],
                    "connectivity": connectivity,
                    "incoming": incoming[node_id],
                    "outgoing": outgoing[node_id],
                }
            )

    hubs.sort(
        key=lambda item: item["connectivity"],
        reverse=True,
    )

    memory = {
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "architecture": {
            "model": "BARROT_CONNECTOME_MEMORY",
            "principles": [
                "sparse_connectivity",
                "modular_processing",
                "recurrent_feedback",
                "hub_routing",
                "local_specialization",
            ],
        },

        "statistics": {
            "neurons": len(nodes),
            "synaptic_connections": len(edges),
            "hubs": len(hubs),
        },

        "nodes": nodes,

        "edges": edges,

        "top_hubs": hubs[:100],
    }

    OUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUT.write_text(
        json.dumps(
            memory,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print("BARROT CONNECTOME MEMORY COMPLETE")
    print("NEURONS:", len(nodes))
    print("SYNAPSES:", len(edges))
    print("HUBS:", len(hubs))
    print("MEMORY:", OUT)


if __name__ == "__main__":
    main()
