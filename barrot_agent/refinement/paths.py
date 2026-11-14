"""Canonical JSON-pointer helpers shared by the refinement upgrade.

Path format: dot-joined components, bare integers for list indices
(e.g. ``strategy_success_rates.auto_merge``, ``items[3].note`` →
``items.3.note``). Keys containing dots are escaped as ``\\.`` — the
knowledge-base datasets use simple keys; the limitation is documented.
"""
from __future__ import annotations

from typing import Any

SEP = "."
ESC = "\\"          # the escape character (escapes itself and the separator)


def ptr_join(parts: list[Any]) -> str:
    """Join ATOMIC components (single keys / indices). Keys containing dots
    are escaped (dot -> backslash-dot), literal backslashes are escaped
    first. Never pass an already-joined canonical path here — use
    ptr_child or ptr_concat."""
    out = []
    for p in parts:
        s = str(p).replace(ESC, ESC + ESC).replace(SEP, ESC + SEP)
        out.append(s)
    return SEP.join(out)


def ptr_child(prefix: str, key: Any) -> str:
    """Canonical path of one child of the node at `prefix`. The prefix is a
    canonical path (its dots are structural), so it is split and re-joined;
    only the new key is escaped as an atomic component."""
    if prefix == "":
        return ptr_join([key])
    return ptr_join(ptr_split(prefix) + [key])


def ptr_concat(base: str, sub: str) -> str:
    """Concatenate two canonical pointers (base subtree + sub path)."""
    if base == "":
        return sub
    if sub == "":
        return base
    return ptr_join(ptr_split(base) + ptr_split(sub))


def ptr_split(pointer: str) -> list[str]:
    if not pointer:
        return []
    parts, buf, esc = [], [], False
    for ch in pointer:
        if esc:
            buf.append(ch)
            esc = False
        elif ch == "\\":
            esc = True
        elif ch == ".":
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(ch)
    parts.append("".join(buf))
    return parts


def ptr_parent(pointer: str) -> str:
    parts = ptr_split(pointer)
    return ptr_join(parts[:-1]) if len(parts) > 1 else ""


def ptr_is_ancestor(a: str, b: str) -> bool:
    """True if a is a strict ancestor path of b (a contains b)."""
    if not a:
        return bool(b)
    pa, pb = ptr_split(a), ptr_split(b)
    return len(pa) < len(pb) and pb[:len(pa)] == pa


def resolve(doc: Any, pointer: str) -> Any:
    """Resolve a pointer; raises KeyError/LookupError-style IndexError when
    the path does not exist."""
    if pointer == "":
        return doc
    node = doc
    for part in ptr_split(pointer):
        if isinstance(node, list):
            node = node[int(part)]
        elif isinstance(node, dict):
            if part not in node:
                raise KeyError(pointer)
            node = node[part]
        else:
            raise IndexError(f"path {pointer!r} does not resolve")
    return node


def set_at(doc: Any, pointer: str, value: Any) -> Any:
    """Set (mutating) the value at pointer. Root pointer replaces in place
    via clear+update to keep the caller's object identity."""
    if pointer == "":
        if isinstance(doc, dict) and isinstance(value, dict):
            doc.clear()
            doc.update(value)
            return doc
        raise ValueError("root replace requires dict-to-dict")
    parts = ptr_split(pointer)
    node = doc
    for part in parts[:-1]:
        node = node[int(part)] if isinstance(node, list) else node[part]
    last = parts[-1]
    if isinstance(node, list):
        node[int(last)] = value
    else:
        node[last] = value
    return doc


def delete_at(doc: Any, pointer: str) -> Any:
    parts = ptr_split(pointer)
    node = doc
    for part in parts[:-1]:
        node = node[int(part)] if isinstance(node, list) else node[part]
    last = parts[-1]
    if isinstance(node, list):
        del node[int(last)]
    else:
        del node[last]
    return doc


def canonical(value: Any) -> str:
    import json
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"))


def value_hash(value: Any) -> str:
    import hashlib
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def walk_leaves(node: Any, path: str = ""):
    """Yield (canonical_pointer, value) for every node — scalar leaves get
    the plain pointer, containers get the pointer with a trailing '/'
    marker so callers can distinguish them."""
    if isinstance(node, dict):
        yield path + "/", node
        for k, v in node.items():
            yield from walk_leaves(v, ptr_child(path, k))
    elif isinstance(node, (list, tuple)):
        yield path + "/", node
        for i, v in enumerate(node):
            yield from walk_leaves(v, ptr_child(path, i))
    else:
        yield path, node
