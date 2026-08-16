"""
data/registry.py — Central data registry for Barrot-Agent.

Provides typed loader functions for all canonical JSON data assets.
All modules should import from here rather than loading JSON files ad-hoc.

Usage:
    from data.registry import load_merge_conflict_data, load_millennium_problems

Features:
- Single source of truth for canonical data file locations.
- In-memory caching: each dataset is loaded once and reused.
- Graceful error handling with descriptive messages on missing files.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

# Registry resolves paths relative to this file so it works regardless of
# the current working directory when the module is imported.
_DATA_DIR = Path(__file__).parent.resolve()

# Canonical file map  {logical_name: relative_path_from_DATA_DIR}
_FILE_MAP: Dict[str, str] = {
    "merge_conflict": "merge_conflict_unified.json",
    "millennium_problems": "millennium_problems_unified.json",
    "mmi_monetization": "mmi_monetization_unified.json",
    "character_capabilities": "character_capabilities_unified.json",
    "longevity_unified": "longevity_unified.json",
    "biomarker_tracking": "biomarker_tracking.json",
    "reprogramming_protocols": "reprogramming_protocols.json",
    "integration_report": "integration_report.json",
    "pingpong_request_example": "pingpong_request_example.json",
    "millennium_reasoning_stack": "millennium_reasoning_stack.json",
}

# ---------------------------------------------------------------------------
# In-memory cache
# ---------------------------------------------------------------------------

_CACHE: Dict[str, Any] = {}


def _load(name: str, force_reload: bool = False) -> Any:
    """Internal loader with caching."""
    if name not in _FILE_MAP:
        raise KeyError(
            f"Unknown data asset '{name}'. " f"Available assets: {sorted(_FILE_MAP.keys())}"
        )
    if name in _CACHE and not force_reload:
        return _CACHE[name]

    path = _DATA_DIR / _FILE_MAP[name]
    if not path.exists():
        raise FileNotFoundError(
            f"Data file for '{name}' not found at expected path: {path}\n"
            "Run the relevant micro-ingestion script to regenerate it."
        )
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    _CACHE[name] = data
    return data


def clear_cache(name: Optional[str] = None) -> None:
    """Clear the in-memory cache for one asset or all assets."""
    if name is None:
        _CACHE.clear()
    elif name in _CACHE:
        del _CACHE[name]


# ---------------------------------------------------------------------------
# Typed loader functions
# ---------------------------------------------------------------------------


def load_merge_conflict_data(force_reload: bool = False) -> Dict[str, Any]:
    """Return the unified merge-conflict knowledge base.

    Keys: patterns, scenarios, tools, best_practices, learning_outcomes,
          resolution_techniques, knowledge_summary.
    """
    return _load("merge_conflict", force_reload)


def load_millennium_problems(force_reload: bool = False) -> Dict[str, Any]:
    """Return the unified Millennium Problems dataset.

    Keys: overview, problems, search_summaries, taxonomy, _meta.
    """
    return _load("millennium_problems", force_reload)


def load_mmi_monetization(force_reload: bool = False) -> Dict[str, Any]:
    """Return the unified MMI/Monetization dataset.

    Keys: mmi_recommendations, monetization_protocols, council_weights, _meta.
    """
    return _load("mmi_monetization", force_reload)


def load_character_capabilities(force_reload: bool = False) -> Dict[str, Any]:
    """Return the unified Character Capabilities dataset.

    Keys: character_database, discovered_capabilities, _meta.
    """
    return _load("character_capabilities", force_reload)


def load_longevity_unified(force_reload: bool = False) -> Dict[str, Any]:
    """Return the unified longevity research dataset."""
    return _load("longevity_unified", force_reload)


def load_biomarker_tracking(force_reload: bool = False) -> Dict[str, Any]:
    """Return biomarker tracking templates and trial datasets."""
    return _load("biomarker_tracking", force_reload)


def load_reprogramming_protocols(force_reload: bool = False) -> Dict[str, Any]:
    """Return epigenetic reprogramming protocol templates."""
    return _load("reprogramming_protocols", force_reload)


def load_integration_report(force_reload: bool = False) -> Dict[str, Any]:
    """Return the latest system integration report."""
    return _load("integration_report", force_reload)


def load_millennium_reasoning_stack(force_reload: bool = False) -> Dict[str, Any]:
    """Return trusted sources and templates for Millennium reasoning orchestration."""
    return _load("millennium_reasoning_stack", force_reload)


def load_pingpong_request(example: bool = False, force_reload: bool = False) -> Dict[str, Any]:
    """Return a pingpong request object.

    Args:
        example: If True, return the example/template request instead of the
                 live one.
    """
    return _load("pingpong_request_example", force_reload)


# ---------------------------------------------------------------------------
# Convenience: list / health-check
# ---------------------------------------------------------------------------


def list_assets() -> Dict[str, Dict[str, Any]]:
    """Return availability information for every registered data asset."""
    result: Dict[str, Dict[str, Any]] = {}
    for name, rel_path in _FILE_MAP.items():
        path = _DATA_DIR / rel_path
        result[name] = {
            "path": str(path),
            "exists": path.exists(),
            "cached": name in _CACHE,
            "size_bytes": path.stat().st_size if path.exists() else None,
        }
    return result


def health_check() -> bool:
    """Return True if all registered data files are present; print a report."""
    assets = list_assets()
    all_ok = True
    for name, info in assets.items():
        status = "✓" if info["exists"] else "✗ MISSING"
        print(f"  [{status}] {name}: {info['path']}")
        if not info["exists"]:
            all_ok = False
    return all_ok
