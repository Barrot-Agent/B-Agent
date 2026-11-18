"""Exercise 2 - V8 type confusion, modelled as a feedback-driven JIT.

A real TurboFan bug is not reproducible here: there is no Chromium checkout, no
`d8`, and no V8 build toolchain in this environment. What *is* reproducible is
the logic that produces the bug, which is the part worth learning:

    1. the interpreter sees values of one type and records feedback
    2. the optimiser specialises on that feedback, deleting type checks
    3. an input arrives with a different type
    4. the specialised code applies the wrong operation and no check stops it
    5. the wrong answer is produced *without crashing*, which is why type
       confusion is more dangerous than a crash: it is silent

The model is deliberately small so the failure is inspectable. `--fixed`
re-installs the check the optimiser removed.

    python3 jit_type_confusion.py           # vulnerable: confusion detected, rc 1
    python3 jit_type_confusion.py --fixed   # repaired: rc 0
"""
from __future__ import annotations

import sys

# A tagged value, the way V8 tags Smi versus HeapObject.
SMI = "smi"
STRING = "string"


class Value:
    __slots__ = ("kind", "payload")

    def __init__(self, kind: str, payload):
        self.kind = kind
        self.payload = payload

    def __repr__(self) -> str:
        return f"Value({self.kind}, {self.payload!r})"


def interpreted_add(a: Value, b: Value) -> Value:
    """The slow path: every type is handled correctly."""
    if a.kind == SMI and b.kind == SMI:
        return Value(SMI, a.payload + b.payload)
    if a.kind == STRING or b.kind == STRING:
        return Value(STRING, f"{a.payload}{b.payload}")
    raise TypeError("unsupported operand")


class FeedbackVector:
    """What the interpreter observed. This is what the optimiser trusts."""

    def __init__(self) -> None:
        self.kinds: list[tuple[str, str]] = []

    def record(self, a: Value, b: Value) -> None:
        self.kinds.append((a.kind, b.kind))

    def is_monomorphic_smi(self) -> bool:
        return bool(self.kinds) and all(pair == (SMI, SMI) for pair in self.kinds)


def optimised_add(a: Value, b: Value) -> Value:
    """Specialised for Smi. The type check was removed as 'redundant'.

    A real JIT verified the types with a map check that costs a branch. The
    optimiser deleted it because the feedback said the types never change.
    """
    left = a.payload  # tagged value used as a machine integer
    right = b.payload
    return Value(SMI, left + right)


def conflict(fast: Value, slow: Value) -> bool:
    return fast.kind != slow.kind or fast.payload != slow.payload


def run(warmup, incoming, fixed: bool):
    """Collect feedback, decide on specialisation, then execute the real input."""
    feedback = FeedbackVector()
    for a, b in warmup:
        interpreted_add(a, b)
        feedback.record(a, b)

    mono = feedback.is_monomorphic_smi()
    print(f"  feedback: {len(feedback.kinds)} samples, monomorphic_smi={mono}")
    if not feedback.is_monomorphic_smi():
        print("  optimiser declined: feedback is not monomorphic")
        return None, None

    print("  optimiser: specialised add() for Smi, map check elided")

    for a, b in incoming:
        slow = interpreted_add(a, b)
        if fixed and not (a.kind == SMI and b.kind == SMI):
            print(f"    [guard] type changed to ({a.kind}, {b.kind}), deoptimised")
            fast = slow
        else:
            fast = optimised_add(a, b)
        if conflict(fast, slow):
            print(f"    CONFUSION in=({a!r}, {b!r}) fast={fast!r} correct={slow!r}")
            return fast, slow
    return None, None


def main(argv: list[str]) -> int:
    fixed = "--fixed" in argv
    print(f"exercise 2: jit type confusion ({'repaired' if fixed else 'vulnerable'})")

    # Phase 1: a monomorphic site. Both operands are integers for every call.
    warmup = [(Value(SMI, i), Value(SMI, i + 1)) for i in range(4)]

    # Phase 2: the same site receives strings. JavaScript is untyped, so the
    # engine may see this at any time, after any amount of integer-only history.
    incoming = [(Value(STRING, "1"), Value(STRING, "2"))]

    fast, slow = run(warmup, incoming, fixed)
    if fast is None:
        print("  RESULT: clean")
        return 0
    print(f"  RESULT: TYPE CONFUSION — optimised={fast!r} interpreted={slow!r}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
