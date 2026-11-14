"""Audit + segmentation for large-document ping-pong refinement.

Resolves the 24K truncation limitation: instead of slicing the prompt
(refiners.py caps the DATA echo at 24000 chars), large documents are
segmented into logically coherent slots that each fit the refinement
budget, with per-slot sibling context.

Coverage contract: the slot plan covers every leaf of the source exactly
once. `segment_document` raises if its own plan is not exhaustive — the
pipeline can therefore never silently skip a portion of the source.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from . import paths

#: documents above this many chars are routed through the patch pipeline
SEGMENT_THRESHOLD = 24000
#: max serialized size of one refinement slot (leaves headroom for the
#: strict-JSON protocol + critique inside the model's output budget)
DEFAULT_MAX_SLOT_CHARS = 9000
#: hard cap on serialized context prepended to a slot
MAX_CONTEXT_CHARS = 1500


@dataclass
class DocumentAudit:
    total_chars: int
    node_count: int
    leaf_count: int
    max_depth: int
    largest_node_chars: int
    needs_segmentation: bool

    def to_dict(self) -> dict:
        return {**self.__dict__}


@dataclass
class Slot:
    """One refinement unit: a subtree slice (or string range) that a model
    can refine in a single bounded call."""
    id: str
    kind: str                     # "root" | "dict_keys" | "list_slice" | "string_range"
    parent_path: str              # canonical pointer of the parent container
    keys: list[str] = field(default_factory=list)      # dict_keys slots
    start: int = -1               # list_slice / string_range
    end: int = -1
    value: Any = None             # exact current value at this slot
    context: str = ""             # bounded sibling/root context
    chars: int = 0

    @property
    def path_label(self) -> str:
        if self.kind == "root":
            return "<root>"
        if self.kind == "string_range":
            return f"{self.parent_path}[{self.start}:{self.end}]"
        if self.kind == "list_slice":
            return f"{self.parent_path}[{self.start}:{self.end}]"
        return f"{self.parent_path}{{{','.join(self.keys)}}}"

    def absolute_leaf_path(self, local_path: str) -> str:
        """Map a leaf path INSIDE this slot's value to its absolute canonical
        path in the source document. list_slice slots offset their first
        index component by `start`; everything else concatenates."""
        if self.kind == "root" or not local_path:
            return local_path
        if self.kind == "string_range":
            return self.parent_path
        if self.kind == "list_slice":
            parts = paths.ptr_split(local_path)
            try:
                parts[0] = str(int(parts[0]) + self.start)
            except ValueError:
                pass
            sub = paths.ptr_join(parts)
            return paths.ptr_concat(self.parent_path, sub)
        return paths.ptr_concat(self.parent_path, local_path)


def audit_document(data: Any) -> DocumentAudit:
    text = paths.canonical(data)
    nodes = leaves = 0
    depth = 0

    def visit(node: Any, d: int) -> None:
        nonlocal nodes, leaves, depth
        nodes += 1
        depth = max(depth, d)
        if isinstance(node, dict):
            for v in node.values():
                visit(v, d + 1)
        elif isinstance(node, (list, tuple)):
            for v in node:
                visit(v, d + 1)
        else:
            leaves += 1

    visit(data, 0)
    return DocumentAudit(
        total_chars=len(text),
        node_count=nodes,
        leaf_count=leaves,
        max_depth=depth,
        largest_node_chars=len(text),
        needs_segmentation=len(text) > SEGMENT_THRESHOLD,
    )


def _slot_context(data: Any, slot_parent: str) -> str:
    """Bounded context: root scalars + the parent container's sibling keys.
    Enough for the model to refine a section coherently without seeing all
    of a huge document."""
    ctx: dict[str, Any] = {}
    if slot_parent:
        ctx["section_path"] = slot_parent
        try:
            parent = paths.resolve(data, slot_parent)
        except (KeyError, IndexError):
            parent = None
        if isinstance(parent, dict):
            ctx["sibling_keys"] = list(parent.keys())[:32]
        elif isinstance(parent, list):
            ctx["list_length"] = len(parent)
    else:
        ctx["section_path"] = "<root>"
    # root-level scalar metadata always helps coherence
    root_scalars = {k: v for k, v in (data.items() if isinstance(data, dict)
                                      else [])
                    if not isinstance(v, (dict, list, tuple))}
    if root_scalars:
        ctx["root_scalars"] = root_scalars
    text = json.dumps(ctx, ensure_ascii=False, default=str)
    if len(text) > MAX_CONTEXT_CHARS:
        text = text[:MAX_CONTEXT_CHARS - 3] + "..."
    return text


def _split_string(text: str, max_chars: int) -> list[tuple[int, int]]:
    """Split an oversized string leaf into (start, end) ranges covering it
    exactly, in order. Cuts prefer natural boundaries (sentence/paragraph
    ends) inside each window; hard-cuts only when none exist."""
    n = len(text)
    if n <= max_chars:
        return [(0, n)]
    natural = [i + 1 for i, ch in enumerate(text)
               if ch in "\n." and i + 1 < n]
    ranges: list[tuple[int, int]] = []
    cursor = 0
    while n - cursor > max_chars:
        window = [b for b in natural
                  if cursor + max_chars // 2 <= b <= cursor + max_chars]
        cut = max(window) if window else cursor + max_chars
        ranges.append((cursor, cut))
        cursor = cut
    ranges.append((cursor, n))
    return [(a, b) for a, b in ranges if b > a]


def segment_document(data: Any,
                     max_chars: int = DEFAULT_MAX_SLOT_CHARS) -> list[Slot]:
    """Split data into a coverage-exact, order-preserving slot plan."""
    if len(paths.canonical(data)) <= max_chars:
        return [Slot(id="s00", kind="root", parent_path="", value=data,
                     context="", chars=len(paths.canonical(data)))]

    slots: list[Slot] = []

    def parent_slot(pid: str, kind: str, parent_path: str,
                    keys: list[str], start: int, end: int,
                    value: Any) -> None:
        slots.append(Slot(
            id=f"s{len(slots):02d}", kind=kind, parent_path=parent_path,
            keys=keys, start=start, end=end, value=value,
            context=_slot_context(data, parent_path),
            chars=len(paths.canonical(value))))

    def plan_container(node: Any, parent_path: str) -> None:
        if isinstance(node, dict):
            keys = list(node.keys())
            i = 0
            while i < len(keys):
                group, size = [], 0
                while i < len(keys):
                    k = keys[i]
                    # value size + key-name overhead (quotes, colon, comma)
                    ksize = len(paths.canonical(node[k])) + len(str(k)) + 4
                    if group and size + ksize > max_chars:
                        break
                    group.append(k)
                    size += ksize
                    i += 1
                if len(group) == 1 and size > max_chars:
                    # single oversized child — recurse into it
                    child_path = paths.ptr_child(parent_path, group[0])
                    plan_container(node[group[0]], child_path)
                else:
                    value = {k: node[k] for k in group}
                    parent_slot("", "dict_keys", parent_path, group, -1, -1,
                                value)
        elif isinstance(node, (list, tuple)):
            n = len(node)
            i = 0
            while i < n:
                group, size = [], 0
                while i < n:
                    v = node[i]
                    vsize = len(paths.canonical(v)) + 1   # + comma overhead
                    if group and size + vsize > max_chars:
                        break
                    group.append(v)
                    size += vsize
                    i += 1
                if len(group) == 1 and size > max_chars:
                    child_path = paths.ptr_child(parent_path, i - 1)
                    plan_container(node[i - 1], child_path)
                else:
                    value = list(group)
                    parent_slot("", "list_slice", parent_path, [],
                                i - len(group), i, value)
        else:
            # oversized scalar string leaf -> string_range slots
            ranges = _split_string(str(node), max_chars)
            for a, b in ranges:
                slots.append(Slot(
                    id=f"s{len(slots):02d}", kind="string_range",
                    parent_path=parent_path, start=a, end=b,
                    value=str(node)[a:b],
                    context=_slot_context(data, parent_path), chars=b - a))

    plan_container(data, "")

    # --- coverage contract: every original leaf path covered exactly once ---
    original_leaves = {p for p, _ in paths.walk_leaves(data)
                       if not p.endswith("/")}
    covered: set[str] = set()
    for s in slots:
        if s.kind == "string_range":
            covered.add(s.parent_path)      # the whole leaf is this slot
        else:
            for p, _ in paths.walk_leaves(s.value):
                if p.endswith("/"):
                    continue
                covered.add(s.absolute_leaf_path(p))
    missing = original_leaves - covered
    if missing:
        raise RuntimeError(
            f"segmentation coverage contract violated: {len(missing)} leaf "
            f"paths uncovered, e.g. {sorted(missing)[:3]}")
    for idx, s in enumerate(slots):
        s.id = f"s{idx:02d}"
    return slots
