from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StoryFact:
    key: str
    value: Any
    source: str = "creative-development"
    locked: bool = False


class StoryBible:
    """
    Canonical creative facts for a production.

    Locked facts cannot be silently replaced. Changes must be explicit.
    """

    def __init__(self) -> None:
        self._facts: dict[str, StoryFact] = {}

    def set_fact(
        self,
        key: str,
        value: Any,
        source: str = "creative-development",
        locked: bool = False,
        override: bool = False,
    ) -> StoryFact:
        existing = self._facts.get(key)
        if existing and existing.locked and existing.value != value and not override:
            raise ValueError(
                f"Story fact '{key}' is locked and cannot be silently changed."
            )

        fact = StoryFact(
            key=key,
            value=value,
            source=source,
            locked=locked or (existing.locked if existing else False),
        )
        self._facts[key] = fact
        return fact

    def get_fact(self, key: str, default: Any = None) -> Any:
        fact = self._facts.get(key)
        return fact.value if fact else default

    def facts(self) -> dict[str, Any]:
        return {
            key: {
                "value": fact.value,
                "source": fact.source,
                "locked": fact.locked,
            }
            for key, fact in self._facts.items()
        }

    def contradictions(self, proposed: dict[str, Any]) -> list[dict[str, Any]]:
        conflicts = []
        for key, value in proposed.items():
            existing = self._facts.get(key)
            if existing and existing.value != value:
                conflicts.append(
                    {
                        "key": key,
                        "established": existing.value,
                        "proposed": value,
                        "locked": existing.locked,
                    }
                )
        return conflicts
