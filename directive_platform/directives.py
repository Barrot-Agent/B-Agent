"""
DirectiveManager — creates, persists, and tracks directives.

Each directive is stored as a JSON file under
``.directive_platform/directives/``.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from .models import Directive, DirectiveStatus, DirectiveType

_DEFAULT_DIRECTIVES_DIR = Path(".directive_platform") / "directives"


class DirectiveManager:
    """
    Create and manage directives.

    Parameters
    ----------
    directives_dir:
        Directory where directive JSON files are persisted.
    """

    def __init__(self, directives_dir: Path | str | None = None) -> None:
        self._dir = Path(directives_dir) if directives_dir else _DEFAULT_DIRECTIVES_DIR
        self._dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create(
        self,
        *,
        title: str,
        description: str,
        directive_type: str,
        assigned_agent_ids: list[str],
        human_author: str,
    ) -> Directive:
        """Create and persist a new directive in *pending* status."""
        if directive_type not in DirectiveType.ALL:
            raise ValueError(
                f"Unknown directive_type {directive_type!r}. " f"Valid values: {DirectiveType.ALL}"
            )
        directive = Directive(
            title=title,
            description=description,
            directive_type=directive_type,
            assigned_agent_ids=assigned_agent_ids,
            human_author=human_author,
            status=DirectiveStatus.PENDING,
        )
        self._persist(directive)
        return directive

    def get(self, directive_id: str) -> Directive | None:
        """Return the directive with the given ID, or ``None``."""
        path = self._dir / f"{directive_id}.json"
        if not path.exists():
            return None
        try:
            return Directive.from_dict(json.loads(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, KeyError):
            return None

    def list_all(self) -> list[Directive]:
        """Return all directives, newest first."""
        directives: list[Directive] = []
        for fp in self._dir.glob("*.json"):
            try:
                directives.append(Directive.from_dict(json.loads(fp.read_text(encoding="utf-8"))))
            except (json.JSONDecodeError, KeyError):
                pass
        return sorted(directives, key=lambda d: d.created_at, reverse=True)

    def list_by_status(self, status: str) -> list[Directive]:
        """Return all directives with a specific *status*."""
        return [d for d in self.list_all() if d.status == status]

    def update_status(self, directive_id: str, status: str) -> bool:
        """
        Change the status of a directive.
        Returns ``True`` if the directive was found and updated.
        """
        directive = self.get(directive_id)
        if directive is None:
            return False
        directive.status = status
        directive.updated_at = time.time()
        self._persist(directive)
        return True

    def add_result(self, directive_id: str, result: dict[str, Any]) -> bool:
        """
        Append a result record to a directive.
        Returns ``True`` if the directive was found and updated.
        """
        directive = self.get(directive_id)
        if directive is None:
            return False
        result.setdefault("recorded_at", time.time())
        directive.results.append(result)
        directive.updated_at = time.time()
        self._persist(directive)
        return True

    def delete(self, directive_id: str) -> bool:
        """Delete a directive. Returns ``True`` if it existed."""
        path = self._dir / f"{directive_id}.json"
        if path.exists():
            path.unlink()
            return True
        return False

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _persist(self, directive: Directive) -> None:
        dest = self._dir / f"{directive.directive_id}.json"
        dest.write_text(json.dumps(directive.to_dict(), indent=2), encoding="utf-8")
