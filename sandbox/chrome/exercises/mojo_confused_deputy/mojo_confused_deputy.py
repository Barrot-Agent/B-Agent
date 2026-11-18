"""Exercise 3 - Mojo confused deputy, modelled as an IPC broker.

A real sandbox escape needs a Chromium build, a sandboxed renderer, and a real
Mojo interface. None of that exists here. The *authorisation* flaw that makes
the escape possible does, and it is small enough to model exactly:

    a broker holds privileges the caller does not
    the caller asks the broker to act on a handle
    the broker checks the handle is the right *kind*
    the broker never checks the handle belongs to the caller
    the broker performs the privileged action for the wrong principal

That is a confused deputy. The renderer does not break the sandbox; it asks the
broker to go through the sandbox on its behalf and the broker agrees.

    python3 mojo_confused_deputy.py           # vulnerable: escape proven, rc 1
    python3 mojo_confused_deputy.py --fixed   # repaired: rc 0
"""
from __future__ import annotations

import sys

FILE = "file"
SHARED_MEMORY = "shared_memory"


class Handle:
    """A kernel object the broker is holding on behalf of one process."""

    __slots__ = ("handle_id", "owner_pid", "kind", "resource")

    def __init__(self, handle_id: int, owner_pid: int, kind: str, resource: str):
        self.handle_id = handle_id
        self.owner_pid = owner_pid
        self.kind = kind
        self.resource = resource

    def __repr__(self) -> str:
        return f"Handle({self.handle_id}, owner={self.owner_pid}, {self.kind}, {self.resource!r})"


class Broker:
    """Runs at a higher privilege than the renderers that call it."""

    def __init__(self) -> None:
        self._handles: dict[int, Handle] = {}

    def register(self, handle: Handle) -> None:
        self._handles[handle.handle_id] = handle

    def duplicate(self, sender_pid: int, handle_id: int, fixed: bool) -> Handle | None:
        handle = self._handles.get(handle_id)
        if handle is None:
            print(f"    broker: no such handle {handle_id}")
            return None
        if handle.kind not in (FILE, SHARED_MEMORY):
            print(f"    broker: handle {handle_id} is not duplicable")
            return None

        # The missing check. Kind is validated; ownership is not.
        if fixed and handle.owner_pid != sender_pid:
            print(
                f"    broker: DENIED handle {handle_id} — owned by pid {handle.owner_pid}, "
                f"requested by pid {sender_pid}"
            )
            return None

        print(
            f"    broker: duplicated handle {handle_id} ({handle.kind}, {handle.resource!r}) "
            f"to pid {sender_pid}"
        )
        return handle


def attempt(sender_pid: int, handle: Handle, fixed: bool) -> bool:
    """A sandboxed renderer asks for a handle it should not be able to reach."""
    broker = Broker()
    broker.register(handle)
    print(f"  renderer pid {sender_pid} -> broker.DuplicateHandle({handle.handle_id})")
    got = broker.duplicate(sender_pid, handle.handle_id, fixed)
    if got is None:
        return False
    if got.owner_pid != sender_pid:
        print(
            f"  ESCAPE: pid {sender_pid} now holds {got.kind} {got.resource!r} "
            f"owned by pid {got.owner_pid}"
        )
        return True
    return False


def main(argv: list[str]) -> int:
    fixed = "--fixed" in argv
    print(f"exercise 3: mojo confused deputy ({'repaired' if fixed else 'vulnerable'})")

    # The browser process wrote a file and holds the handle. A renderer must
    # never be able to ask for it, because the renderer is sandboxed precisely
    # so that it cannot touch the filesystem.
    privileged = Handle(
        handle_id=0x40,
        owner_pid=1,
        kind=FILE,
        resource="/home/user/.ssh/id_ed25519",
    )
    attacker_pid = 4242

    escaped = attempt(attacker_pid, privileged, fixed)
    if escaped:
        print("  RESULT: SANDBOX ESCAPE — confused deputy granted a foreign handle")
        return 1
    print("  RESULT: contained")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
