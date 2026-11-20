"""Controlled create-only file delivery from Barrot into the Termux filesystem."""

from __future__ import annotations

import os
import stat
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TermuxDropResult:
    success: bool
    path: str
    reason: str


class TermuxBridge:
    """Create files inside explicitly allowed Termux roots without overwriting user data."""

    def __init__(
        self,
        allowed_roots: tuple[str, ...] | None = None,
    ):
        if allowed_roots is None:
            allowed_roots = (
                str(Path.home() / "barrot"),
            )
        self.allowed_roots = tuple(
            Path(root).expanduser().resolve()
            for root in allowed_roots
        )

    def _resolve_target(self, value: str) -> Path:
        if not isinstance(value, str) or not value.strip():
            raise ValueError("Target path must be a non-empty string.")
        supplied = Path(value).expanduser()
        if ".." in supplied.parts:
            raise ValueError("Target path traversal is not allowed.")
        if supplied.is_absolute():
            candidate = supplied
        else:
            if len(self.allowed_roots) != 1:
                raise ValueError("Relative targets require exactly one approved Termux root.")
            candidate = self.allowed_roots[0] / supplied
        candidate = Path(os.path.abspath(candidate))

        for root in self.allowed_roots:
            try:
                relative = candidate.relative_to(root)
            except ValueError:
                continue

            current = root
            if current.is_symlink():
                raise ValueError("Approved Termux root became a symlink; refusing delivery.")
            for part in relative.parts:
                current = current / part
                try:
                    mode = current.lstat().st_mode
                except FileNotFoundError:
                    continue
                if stat.S_ISLNK(mode):
                    raise ValueError("Symlink targets are not allowed for Termux delivery.")

            resolved = candidate.resolve(strict=False)
            try:
                resolved.relative_to(root)
            except ValueError as exc:
                raise ValueError("Target resolves outside the approved Termux workspace.") from exc
            return resolved

        raise ValueError("Target is outside approved Termux workspace roots.")

    @staticmethod
    def _sync_parent(path: Path) -> None:
        if os.name == "nt":
            return
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)

    def _create_only(self, *, path: str, content: bytes) -> TermuxDropResult:
        target: Path | None = None
        try:
            target = self._resolve_target(path)
            target.parent.mkdir(parents=True, exist_ok=True)
            # Re-check after directory creation to reject newly introduced symlinks.
            target = self._resolve_target(path)
            try:
                with target.open("xb") as handle:
                    handle.write(content)
                    handle.flush()
                    os.fsync(handle.fileno())
                self._sync_parent(target)
                return TermuxDropResult(
                    success=True,
                    path=str(target),
                    reason="File created in the approved Termux workspace.",
                )
            except FileExistsError:
                # Idempotent retries are safe only when the existing regular file
                # already contains exactly the requested bytes. Never replace it.
                if target.is_symlink() or not target.is_file():
                    return TermuxDropResult(
                        success=False,
                        path=str(target),
                        reason="Target already exists and is not a regular file; no change was made.",
                    )
                if target.read_bytes() == content:
                    return TermuxDropResult(
                        success=True,
                        path=str(target),
                        reason="Identical file already exists; no write or overwrite was performed.",
                    )
                return TermuxDropResult(
                    success=False,
                    path=str(target),
                    reason="Target already exists with different content; existing user data was preserved.",
                )
        except Exception as exc:
            return TermuxDropResult(
                success=False,
                path=str(target) if target is not None else str(path),
                reason=str(exc),
            )

    def drop_text(
        self,
        *,
        path: str,
        content: str,
    ) -> TermuxDropResult:
        """Create a UTF-8 file; identical retries are idempotent, differing files are preserved."""
        if not isinstance(content, str):
            return TermuxDropResult(False, str(path), "Text content must be a string.")
        return self._create_only(path=path, content=content.encode("utf-8"))

    def drop_bytes(
        self,
        *,
        path: str,
        content: bytes,
    ) -> TermuxDropResult:
        """Create a binary file; identical retries are idempotent, differing files are preserved."""
        if not isinstance(content, bytes):
            return TermuxDropResult(False, str(path), "Binary content must be bytes.")
        return self._create_only(path=path, content=content)
