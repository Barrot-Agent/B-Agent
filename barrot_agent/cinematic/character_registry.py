from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Character:
    name: str
    attributes: dict[str, Any] = field(default_factory=dict)
    relationships: dict[str, str] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)


class CharacterRegistry:
    """Canonical registry for characters and their established attributes."""

    def __init__(self) -> None:
        self._characters: dict[str, Character] = {}

    def register(
        self,
        name: str,
        attributes: dict[str, Any] | None = None,
    ) -> Character:
        key = name.lower()
        if key not in self._characters:
            self._characters[key] = Character(
                name=name,
                attributes=attributes or {},
            )
        elif attributes:
            self._characters[key].attributes.update(attributes)
        return self._characters[key]

    def get(self, name: str) -> Character | None:
        return self._characters.get(name.lower())

    def update_attribute(
        self,
        name: str,
        attribute: str,
        value: Any,
        scene_id: str | None = None,
    ) -> None:
        character = self.register(name)
        old_value = character.attributes.get(attribute)
        character.attributes[attribute] = value
        character.history.append(
            {
                "scene_id": scene_id,
                "attribute": attribute,
                "from": old_value,
                "to": value,
            }
        )

    def validate(
        self,
        name: str,
        proposed_attributes: dict[str, Any],
    ) -> list[dict[str, Any]]:
        character = self.get(name)
        if not character:
            return []

        conflicts = []
        for key, value in proposed_attributes.items():
            established = character.attributes.get(key)
            if established is not None and established != value:
                conflicts.append(
                    {
                        "character": character.name,
                        "attribute": key,
                        "established": established,
                        "proposed": value,
                    }
                )
        return conflicts

    def all_characters(self) -> list[Character]:
        return list(self._characters.values())
