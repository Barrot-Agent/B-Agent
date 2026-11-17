"""Typed relational structure for discovered geometric structures.

Classification answers "what class is this?". This module answers "how is
this related to that?". Every edge carries a witness: an edge with no witness
is rejected, because an unverifiable relation is not a relation.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterator


class RelationType(str, Enum):
    ADJACENT_TO = "adjacent_to"
    INTERSECTS = "intersects"
    CONTAINS = "contains"
    CONTAINED_BY = "contained_by"
    BOUNDARY_OF = "boundary_of"
    CLOSURE_OF = "closure_of"
    SPECIALIZES = "specializes"
    DEGENERATES_TO = "degenerates_to"
    DERIVED_FROM = "derived_from"


SYMMETRIC = frozenset({RelationType.ADJACENT_TO, RelationType.INTERSECTS})
ANTISYMMETRIC = frozenset(
    {
        RelationType.BOUNDARY_OF,
        RelationType.CLOSURE_OF,
        RelationType.SPECIALIZES,
        RelationType.DEGENERATES_TO,
        RelationType.DERIVED_FROM,
    }
)
IRREFLEXIVE = frozenset(
    {
        RelationType.BOUNDARY_OF,
        RelationType.CLOSURE_OF,
        RelationType.SPECIALIZES,
        RelationType.DEGENERATES_TO,
    }
)
#: Relations whose chains are checked for cycles by :meth:`RelationGraph.validate`.
ACYCLIC = frozenset({RelationType.SPECIALIZES, RelationType.DERIVED_FROM})


@dataclass(frozen=True)
class Relation:
    type: RelationType
    source: str
    target: str
    witness: str

    def to_dict(self) -> dict[str, str]:
        return {
            "type": self.type.value,
            "source": self.source,
            "target": self.target,
            "witness": self.witness,
        }


class RelationGraph:
    """Directed, typed, witnessed relation graph with structural checks."""

    def __init__(self) -> None:
        self._relations: list[Relation] = []

    def add(
        self,
        relation: RelationType,
        source: str,
        target: str,
        *,
        witness: str,
    ) -> Relation:
        if not source or not target:
            raise ValueError("source and target must be non-empty")
        if not witness or not witness.strip():
            raise ValueError("a relation requires a witness")
        if relation in IRREFLEXIVE and source == target:
            raise ValueError(f"{relation.value} is irreflexive: {source!r} -> itself")

        record = Relation(relation, source, target, witness)
        self._relations.append(record)
        return record

    def relations(
        self,
        relation: RelationType | None = None,
        *,
        node: str | None = None,
    ) -> tuple[Relation, ...]:
        result = [
            record
            for record in self._relations
            if (relation is None or record.type is relation)
            and (node is None or node in (record.source, record.target))
        ]
        return tuple(result)

    def neighbours(
        self,
        node: str,
        relation: RelationType | None = None,
        *,
        direction: str = "out",
    ) -> tuple[str, ...]:
        if direction not in {"in", "out", "both"}:
            raise ValueError("direction must be 'in', 'out' or 'both'")
        found: list[str] = []
        for record in self._relations:
            if relation is not None and record.type is not relation:
                continue
            if record.source == node and direction in {"out", "both"}:
                found.append(record.target)
            if record.target == node and direction in {"in", "both"}:
                found.append(record.source)
        return tuple(found)

    def validate(self) -> list[str]:
        """Return objective violations. An empty list means no violation found."""
        errors: list[str] = []
        pairs = {(record.type, record.source, record.target) for record in self._relations}

        for record in self._relations:
            if record.type in ANTISYMMETRIC:
                reverse = (record.type, record.target, record.source)
                if reverse in pairs:
                    errors.append(
                        f"{record.type.value} is antisymmetric: "
                        f"{record.source!r} <-> {record.target!r}"
                    )
            if record.type in IRREFLEXIVE and record.source == record.target:
                errors.append(
                    f"{record.type.value} is irreflexive: {record.source!r} -> itself"
                )

        for relation in ACYCLIC:
            cycle = self._find_cycle(relation)
            if cycle:
                errors.append(
                    f"{relation.value} must be acyclic: {' -> '.join(cycle)}"
                )

        return sorted(set(errors))

    def _find_cycle(self, relation: RelationType) -> list[str]:
        edges: dict[str, list[str]] = {}
        for record in self._relations:
            if record.type is relation:
                edges.setdefault(record.source, []).append(record.target)

        visiting: set[str] = set()
        visited: set[str] = set()

        def walk(node: str, path: list[str]) -> list[str] | None:
            if node in visiting:
                return path[path.index(node):] + [node]
            if node in visited:
                return None
            visiting.add(node)
            for target in edges.get(node, ()):
                found = walk(target, path + [node])
                if found:
                    return found
            visiting.discard(node)
            visited.add(node)
            return None

        for start in edges:
            found = walk(start, [])
            if found:
                return found
        return []

    def __iter__(self) -> Iterator[Relation]:
        return iter(self._relations)

    def __len__(self) -> int:
        return len(self._relations)
