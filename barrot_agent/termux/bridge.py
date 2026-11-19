"""Controlled file delivery from Barrot into the Termux filesystem."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class TermuxDropResult:
    success: bool
    path: str
    reason: str


class TermuxBridge:
    """Write files into explicitly allowed Termux workspace roots."""

    def __init__(
        self,
        allowed_roots: tuple[str, ...] | None = None,
    ):
        if allowed_roots is None:
            allowed_roots = (
                str(
                    Path.home()
                    / "barrot"
                ),
            )

        self.allowed_roots = tuple(
            Path(root).expanduser().resolve()
            for root in allowed_roots
        )

    def _allowed(
        self,
        path: Path,
    ) -> bool:
        for root in self.allowed_roots:
            try:
                path.relative_to(root)
                return True
            except ValueError:
                continue

        return False

    def drop_text(
        self,
        *,
        path: str,
        content: str,
    ) -> TermuxDropResult:
        """Write text to an approved Termux filesystem path."""

        target = (
            Path(path)
            .expanduser()
            .resolve()
        )

        if not self._allowed(target):
            return TermuxDropResult(
                success=False,
                path=str(target),
                reason=(
                    "Target is outside approved "
                    "Termux workspace roots."
                ),
            )

        try:
            target.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            target.write_text(
                content,
                encoding="utf-8",
            )

            return TermuxDropResult(
                success=True,
                path=str(target),
                reason="File written to Termux.",
            )

        except Exception as exc:
            return TermuxDropResult(
                success=False,
                path=str(target),
                reason=str(exc),
            )

    def drop_bytes(
        self,
        *,
        path: str,
        content: bytes,
    ) -> TermuxDropResult:
        """Write bytes to an approved Termux filesystem path."""

        target = Path(path).expanduser().resolve()

        if not self._allowed(target):
            return TermuxDropResult(
                success=False,
                path=str(target),
                reason=(
                    "Target is outside approved "
                    "Termux workspace roots."
                ),
            )

        try:
            target.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            target.write_bytes(content)

            return TermuxDropResult(
                success=True,
                path=str(target),
                reason="File dropped into Termux workspace.",
            )

        except Exception as exc:
            return TermuxDropResult(
                success=False,
                path=str(target),
                reason=str(exc),
            )
