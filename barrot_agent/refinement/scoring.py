"""Deterministic data-quality scoring for ping-pong refinement.

The score makes "cannot be refined further" measurable: refinement stops when
the score stops improving (fixed point), not when a model merely claims done.
Shape-agnostic: works on any JSON-able value (dict / list / str / scalar).
All components are pure functions — same input, same score, offline.
"""
from __future__ import annotations

import re
from typing import Any

WEIGHTS = {
    "completeness": 0.35,
    "consistency": 0.30,
    "specificity": 0.20,
    "redundancy": 0.15,
}

_EMPTY = ("", None, [], {}, set())
_WS = re.compile(r"\s+")
_WORD = re.compile(r"[A-Za-z0-9_]")


def _is_empty(v: Any) -> bool:
    if v is None:
        return True
    if isinstance(v, str) and not v.strip():
        return True
    if isinstance(v, (list, dict, tuple, set)) and len(v) == 0:
        return True
    return False


def _walk(node: Any, key_path: str = ""):
    """Yield (key_path, value) for every scalar leaf plus container nodes."""
    yield key_path, node
    if isinstance(node, dict):
        for k, v in node.items():
            yield from _walk(v, f"{key_path}.{k}" if key_path else str(k))
    elif isinstance(node, (list, tuple)):
        for i, v in enumerate(node):
            yield from _walk(v, f"{key_path}[{i}]")


def completeness(data: Any) -> float:
    """Fraction of leaf values that are non-empty."""
    leaves = [(p, v) for p, v in _walk(data)
              if not isinstance(v, (dict, list, tuple))]
    if not leaves:
        return 0.0 if _is_empty(data) else 1.0
    filled = sum(1 for _, v in leaves if not _is_empty(v))
    return filled / len(leaves)


def consistency(data: Any) -> float:
    """1.0 minus conflict ratio. A conflict = within a SINGLE container, the
    same normalized key (case/underscore-insensitive) holds different values
    — only possible via case/underscore variants, and the classic corruption
    multi-pass refinement inflicts. Sibling list items are independent by
    design: their differing values never conflict."""
    conflicts = 0
    containers = 0

    def visit(node: Any) -> None:
        nonlocal conflicts, containers
        if isinstance(node, dict):
            containers += 1
            seen: dict[str, str] = {}
            for k, v in node.items():
                if isinstance(v, (dict, list, tuple)):
                    visit(v)
                    continue
                nk = str(k).lower().replace("_", "").replace("-", "")
                val = _WS.sub(" ", str(v)).strip().lower()
                if nk in seen and seen[nk] != val:
                    conflicts += 1
                else:
                    seen.setdefault(nk, val)
        elif isinstance(node, (list, tuple)):
            for v in node:
                visit(v)

    visit(data)
    if containers == 0:
        return 1.0
    return 1.0 - (conflicts / containers)


def specificity(data: Any) -> float:
    """Share of string leaves carrying real information (not vague fillers)."""
    vague = {"tbd", "todo", "n/a", "na", "none", "unknown", "lorem ipsum", "xxx", "?", "-"}
    strings = [v for _, v in _walk(data) if isinstance(v, str) and v.strip()]
    if not strings:
        return 1.0
    good = 0
    for s in strings:
        norm = _WS.sub(" ", s.strip().lower())
        if norm in vague:
            continue
        if len(norm) >= 3 and _WORD.search(norm):
            good += 1
    return good / len(strings)


def redundancy(data: Any) -> float:
    """1.0 minus duplicate-item ratio across lists (order-insensitive)."""
    lists = [v for _, v in _walk(data) if isinstance(v, list) and len(v) > 1]
    if not lists:
        return 1.0
    total = dupes = 0
    for lst in lists:
        items = [_WS.sub(" ", str(x).strip().lower()) for x in lst
                 if not isinstance(x, (dict, list))]
        if len(items) < 2:
            continue
        total += len(items)
        dupes += len(items) - len(set(items))
    if total == 0:
        return 1.0
    return 1.0 - (dupes / total)


def score(data: Any) -> float:
    """Composite quality score in [0, 1]. Deterministic."""
    s = (WEIGHTS["completeness"] * completeness(data)
         + WEIGHTS["consistency"] * consistency(data)
         + WEIGHTS["specificity"] * specificity(data)
         + WEIGHTS["redundancy"] * redundancy(data))
    return round(max(0.0, min(1.0, s)), 6)


def breakdown(data: Any) -> dict:
    return {
        "completeness": round(completeness(data), 6),
        "consistency": round(consistency(data), 6),
        "specificity": round(specificity(data), 6),
        "redundancy": round(redundancy(data), 6),
        "total": score(data),
    }
