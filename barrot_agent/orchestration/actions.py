"""Structured actions available to the Barrot autonomous system."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


class ActionError(ValueError):
    """Raised when an autonomous action is invalid."""


@dataclass(frozen=True)
class Action:
    type: str
    args: dict[str, Any]


ALLOWED_ACTIONS = {
    "LIST_FILES",
    "READ_FILE",
    "SEARCH_TEXT",
    "RUN_TESTS",
    "WRITE_FILE",
    "GIT_STATUS",
}


def parse_actions(payload: dict[str, Any]) -> list[Action]:
    raw_actions = payload.get("actions")

    if not isinstance(raw_actions, list) or not raw_actions:
        raise ActionError("Plan must contain a non-empty actions list")

    actions: list[Action] = []

    for raw in raw_actions:
        if not isinstance(raw, dict):
            raise ActionError("Each action must be an object")

        action_type = raw.get("type")
        args = raw.get("args", {})

        if action_type not in ALLOWED_ACTIONS:
            raise ActionError(f"Unsupported action: {action_type}")

        if not isinstance(args, dict):
            raise ActionError(f"Action args must be an object: {action_type}")

        actions.append(Action(type=action_type, args=args))

    return actions
