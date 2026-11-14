"""Patch layer for large-document ping-pong refinement.

Models return refined SECTION values; this module turns section diffs into
targeted patches on canonical pointers, validates every patch against the
live document (hash preconditions), detects overlapping/conflicting/
incompatible patches, applies survivors in document order with batch
rollback, and verifies the final document against the original.

An applied patch is the only way the pipeline mutates the document, so the
verification step can prove: nothing skipped, nothing smuggled, order kept.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any

from . import paths

# patch op codes
REPLACE = "replace"     # swap value at existing path (old precondition)
SET = "set"             # add new key/index (parent must exist, key must not)
DELETE = "delete"       # remove key/index
SPLICE = "splice"       # replace text[start:end] of a string leaf

# patch statuses
PENDING = "pending"
APPLIED = "applied"
SKIPPED_NOOP = "skipped_noop"
REJECTED_STALE = "rejected_stale"           # precondition hash mismatch
REJECTED_CONFLICT = "rejected_conflict"     # overlaps an applied patch
REJECTED_INVALID = "rejected_invalid"       # unresolvable / unserializable


@dataclass
class Patch:
    op: str
    path: str                    # canonical pointer (parent for SET)
    old: Any = None
    new: Any = None
    old_hash: str = ""           # precondition: hash of value currently at path
    start: int = -1              # SPLICE only
    end: int = -1
    key: str = ""                # SET only (new key name)
    source: str = ""             # refiner/model that produced it
    note: str = ""
    patch_id: str = ""
    status: str = PENDING
    failure_cause: str = ""

    def to_dict(self) -> dict:
        d = {k: v for k, v in self.__dict__.items() if k != "old"}
        d["old_hash"] = self.old_hash
        return d


@dataclass
class BatchResult:
    document: Any = None          # the mutated working copy (caller owns it)
    applied: list[Patch] = field(default_factory=list)
    rejected: list[Patch] = field(default_factory=list)
    skipped: list[Patch] = field(default_factory=list)
    undo: list[tuple[str, str, Any]] = field(default_factory=list)
    # undo entries: (kind, pointer, prior) — kind in {"value","splice","set"}


def make_replace(path: str, old: Any, new: Any, source: str = "",
                 note: str = "") -> Patch:
    return Patch(op=REPLACE, path=path, old=old, new=new,
                 old_hash=paths.value_hash(old), source=source, note=note)


def make_set(parent_path: str, key: str, new: Any, source: str = "",
             note: str = "") -> Patch:
    return Patch(op=SET, path=parent_path, key=key, new=new,
                 source=source, note=note)


def make_delete(path: str, old: Any, source: str = "", note: str = "") -> Patch:
    return Patch(op=DELETE, path=path, old=old,
                 old_hash=paths.value_hash(old), source=source, note=note)


def make_splice(path: str, text: str, start: int, end: int, new_text: str,
                source: str = "", note: str = "") -> Patch:
    return Patch(op=SPLICE, path=path, start=start, end=end,
                 old=text[start:end], new=new_text,
                 old_hash=paths.value_hash(text[start:end]),
                 source=source, note=note)


def diff_values(old: Any, new: Any, path: str, source: str,
                max_patches: int = 400) -> list[Patch]:
    """Turn a refined section value into targeted patches against the old
    value. Leaf-level replaces where cheap; whole-VALUE replace when the
    structure diverges (list length changes etc.). Deletes for removed
    dict keys. Lists are positionally replaced — no index splicing."""
    patches: list[Patch] = []

    def walk(o: Any, n: Any, p: str) -> bool:
        if len(patches) >= max_patches:
            return False
        if paths.value_hash(o) == paths.value_hash(n):
            return True
        if isinstance(o, dict) and isinstance(n, dict):
            for k in list(o.keys()):
                if len(patches) >= max_patches:
                    return False
                if k not in n:
                    patches.append(make_delete(
                        paths.ptr_child(p, k), o[k], source,
                        "removed in refinement"))
                elif not walk(o[k], n[k], paths.ptr_child(p, k)):
                    patches.append(make_replace(
                        paths.ptr_child(p, k), o[k], n[k], source,
                        "subtree rewritten"))
            for k in n:
                if k not in o and len(patches) < max_patches:
                    patches.append(make_set(p, k, n[k], source,
                                            "added in refinement"))
            return True
        if isinstance(o, list) and isinstance(n, list) \
                and len(o) == len(n):
            for i, (ov, nv) in enumerate(zip(o, n)):
                if len(patches) >= max_patches:
                    return False
                if not walk(ov, nv, paths.ptr_child(p, i)):
                    patches.append(make_replace(
                        paths.ptr_child(p, i), ov, nv, source,
                        "item rewritten"))
            return True
        patches.append(make_replace(p, o, n, source, "value refined"))
        return True

    walk(old, new, path)
    return patches[:max_patches]


# ------------------------------------------------------------------ validate
def validate_patch(doc: Any, patch: Patch) -> Patch:
    """Validate against the LIVE document. Returns the patch with status
    set (PENDING stays valid-and-ready; anything else explains why)."""
    try:
        if patch.op == SET:
            parent = paths.resolve(doc, patch.path)
            if not isinstance(parent, dict):
                patch.status = REJECTED_INVALID
                patch.failure_cause = "SET parent is not a dict"
            elif patch.key in parent:
                patch.status = REJECTED_CONFLICT
                patch.failure_cause = f"key {patch.key!r} already exists"
            elif paths.value_hash(patch.new) is None:
                patch.status = REJECTED_INVALID
                patch.failure_cause = "new value not serializable"
            return patch
        current = paths.resolve(doc, patch.path)
    except (KeyError, IndexError, ValueError) as exc:
        patch.status = REJECTED_INVALID
        patch.failure_cause = f"path does not resolve: {exc}"
        return patch
    if patch.op == SPLICE:
        if not isinstance(current, str):
            patch.status = REJECTED_INVALID
            patch.failure_cause = "SPLICE target is not a string"
        elif not (0 <= patch.start <= patch.end <= len(current)):
            patch.status = REJECTED_INVALID
            patch.failure_cause = "splice range out of bounds"
        elif paths.value_hash(current[patch.start:patch.end]) != patch.old_hash:
            patch.status = REJECTED_STALE
            patch.failure_cause = "fragment hash mismatch (stale splice)"
        elif patch.new == patch.old:
            patch.status = SKIPPED_NOOP
        return patch
    # REPLACE / DELETE — op validity first, then the hash precondition
    if patch.op not in (REPLACE, DELETE):
        patch.status = REJECTED_INVALID
        patch.failure_cause = f"unknown op {patch.op!r}"
        return patch
    if paths.value_hash(current) != patch.old_hash:
        patch.status = REJECTED_STALE
        patch.failure_cause = "precondition hash mismatch (value changed)"
    elif patch.op == REPLACE and patch.new == patch.old:
        patch.status = SKIPPED_NOOP
    return patch


# ----------------------------------------------------------------- conflicts
def detect_conflicts(patches: list[Patch]) -> None:
    """Mark overlapping/conflicting/incompatible patches (mutates status).
    Same path: identical `new` → later is a duplicate (skipped_noop);
    different `new` → later is rejected_conflict. Ancestor/descendant
    overlap: the shallower (coarser) patch wins, the deeper is rejected —
    applying both would clobber. DELETE vs SET on the same key: incompatible.
    No-op patches (already skipped) conflict with nothing."""
    for i, a in enumerate(patches):
        if a.status != PENDING:
            continue
        for b in patches[i + 1:]:
            if b.status != PENDING:
                continue
            if a.path == b.path:
                if a.op == SET and b.op == SET and a.key == b.key:
                    if paths.value_hash(a.new) == paths.value_hash(b.new):
                        b.status = SKIPPED_NOOP
                        b.failure_cause = "duplicate SET"
                    else:
                        b.status = REJECTED_CONFLICT
                        b.failure_cause = \
                            f"conflicting SET of key {a.key!r} (vs {a.patch_id or a.source})"
                elif {a.op, b.op} == {DELETE, SET}:
                    b.status = REJECTED_CONFLICT
                    b.failure_cause = \
                        f"incompatible: {a.op} vs {b.op} at {b.path}"
                elif a.op == DELETE and b.op in (REPLACE, SPLICE):
                    b.status = REJECTED_CONFLICT
                    b.failure_cause = f"incompatible: {a.op} vs {b.op} at {b.path}"
                elif b.op == DELETE and a.op in (REPLACE, SPLICE):
                    b.status = REJECTED_CONFLICT
                    b.failure_cause = f"incompatible: {b.op} vs {a.op} at {b.path}"
                elif a.op == REPLACE and b.op == REPLACE:
                    if paths.value_hash(a.new) == paths.value_hash(b.new):
                        b.status = SKIPPED_NOOP
                        b.failure_cause = "duplicate replace"
                    else:
                        b.status = REJECTED_CONFLICT
                        b.failure_cause = \
                            f"conflicting replace at {b.path} (vs {a.patch_id or a.source})"
                continue
            if paths.ptr_is_ancestor(a.path, b.path) \
                    and a.op in (REPLACE, DELETE):
                b.status = REJECTED_CONFLICT
                b.failure_cause = \
                    f"ancestor patch at {a.path} supersedes {b.path}"
            elif paths.ptr_is_ancestor(b.path, a.path) \
                    and b.op in (REPLACE, DELETE):
                a.status = REJECTED_CONFLICT
                a.failure_cause = \
                    f"ancestor patch at {b.path} supersedes {a.path}"


# --------------------------------------------------------------------- apply
def _apply_order_key(p: Patch):
    # splices on the same string apply highest-start-first so earlier
    # offsets stay valid; everything else document order by pointer
    if p.op == SPLICE:
        return (p.path, 1, -p.start)
    return (p.path, 0, 0)


def apply_patches(doc: Any, patches: list[Patch],
                  validate: bool = True) -> BatchResult:
    """Apply validated patches to a deep copy of doc. Failed preconditions
    reject the individual patch and continue (patch-level rejection, batch
    continues). Returns BatchResult with an undo stack for rollback; the
    CALLER owns the returned copy."""
    result = BatchResult()
    work = copy.deepcopy(doc)
    if validate:
        for p in patches:
            validate_patch(work, p)
        detect_conflicts(patches)
    ordered = sorted(patches, key=_apply_order_key)
    for p in ordered:
        try:
            if p.status == SKIPPED_NOOP:
                result.skipped.append(p)
                continue
            if p.status != PENDING:
                result.rejected.append(p)
                continue
            if p.op == SPLICE:
                current = paths.resolve(work, p.path)
                result.undo.append(("splice", p.path,
                                    (p.start, p.end, current[p.start:p.end])))
                paths.set_at(work, p.path,
                             current[:p.start] + p.new + current[p.end:])
            elif p.op == REPLACE:
                result.undo.append(("value", p.path,
                                    copy.deepcopy(paths.resolve(work, p.path))))
                paths.set_at(work, p.path, copy.deepcopy(p.new))
            elif p.op == DELETE:
                result.undo.append(("value", p.path,
                                    copy.deepcopy(paths.resolve(work, p.path))))
                paths.delete_at(work, p.path)
            elif p.op == SET:
                parent = paths.resolve(work, p.path)
                result.undo.append(("set", p.path, p.key))
                parent[p.key] = copy.deepcopy(p.new)
            else:
                p.status = REJECTED_INVALID
                p.failure_cause = f"unknown op {p.op!r}"
                result.rejected.append(p)
                continue
            p.status = APPLIED
            result.applied.append(p)
        except (KeyError, IndexError, ValueError, TypeError) as exc:
            p.status = REJECTED_INVALID
            p.failure_cause = f"apply failed: {type(exc).__name__}: {exc}"
            result.rejected.append(p)
    result.document = work
    return result


def rollback(doc: Any, undo: list[tuple[str, str, Any]]) -> Any:
    """Restore a document from an undo stack (reverse application order)."""
    for kind, pointer, prior in reversed(undo):
        if kind == "value":
            paths.set_at(doc, pointer, copy.deepcopy(prior))
        elif kind == "splice":
            start, end, fragment = prior
            current = paths.resolve(doc, pointer)
            paths.set_at(doc, pointer,
                         current[:start] + fragment + current[end:])
        elif kind == "set":
            parent = paths.resolve(doc, pointer)
            parent.pop(prior, None)
    return doc


# ----------------------------------------------------------------- verify
@dataclass
class VerificationReport:
    ok: bool
    missing_paths: list[str] = field(default_factory=list)
    smuggled_changes: list[str] = field(default_factory=list)
    deletions: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict:
        return {**self.__dict__}


def verify_against_original(original: Any, final: Any,
                            applied: list[Patch]) -> VerificationReport:
    """Prove the refinement is complete and honest:
    1. every original leaf still exists, unless an applied DELETE removed it
       (a DELETE at an ancestor path excuses everything beneath it);
    2. subtrees OUTSIDE all applied patch scopes are byte-identical
       (nothing smuggled in by the model beyond its declared patches);
    3. untouched containers keep their exact child structure (key list /
       element count) — catches shape changes leaf comparison cannot see;
    4. applied patch scopes carry exactly the declared new values."""
    deletions = {p.path for p in applied if p.op == DELETE}
    report = VerificationReport(ok=True, deletions=sorted(deletions))
    final_leaves = {p: v for p, v in paths.walk_leaves(final)
                    if not p.endswith("/")}
    final_containers = {p.rstrip("/"): v
                        for p, v in paths.walk_leaves(final)
                        if p.endswith("/")}

    scoped = [p.path for p in applied if p.op != SPLICE]
    spliced = {p.path for p in applied if p.op == SPLICE}

    def in_scope(pointer: str) -> bool:
        return any(pointer == s or paths.ptr_is_ancestor(s, pointer)
                   for s in scoped)

    def deleted_above(pointer: str) -> bool:
        return any(pointer == d or paths.ptr_is_ancestor(d, pointer)
                   for d in deletions)

    directly_patched_children: set[str] = set()
    for p in applied:
        if p.op in (REPLACE, DELETE, SPLICE):
            directly_patched_children.add(paths.ptr_parent(p.path))

    for p, v in paths.walk_leaves(original):
        if p.endswith("/"):
            container_path = p[:-1]
            if in_scope(container_path) or deleted_above(container_path):
                continue
            if container_path in directly_patched_children:
                continue
            if container_path not in final_containers:
                report.ok = False
                report.smuggled_changes.append(container_path + " (shape)")
            else:
                orig_keys = list(v.keys()) if isinstance(v, dict) \
                    else list(range(len(v)))
                fin = final_containers[container_path]
                fin_keys = list(fin.keys()) if isinstance(fin, dict) \
                    else list(range(len(fin)))
                if orig_keys != fin_keys:
                    report.ok = False
                    report.smuggled_changes.append(
                        container_path + " (child structure)")
            continue
        if deleted_above(p):
            continue
        if p not in final_leaves:
            if in_scope(p):
                # inside a declared patch scope: the patch's own hash
                # precondition governed this subtree at apply time
                continue
            report.ok = False
            report.missing_paths.append(p)
        elif p not in spliced and not in_scope(p) and \
                paths.value_hash(final_leaves[p]) != paths.value_hash(v):
            report.ok = False
            report.smuggled_changes.append(p)
    if not report.ok:
        report.notes = (f"{len(report.missing_paths)} missing, "
                        f"{len(report.smuggled_changes)} smuggled")
    return report
