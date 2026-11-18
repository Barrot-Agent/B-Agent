"""A mutational fuzzer, because libFuzzer cannot run here.

libFuzzer needs clang. clang is installed as an Android/Termux binary inside
proot and fails to compile anything:

    proot error: unknown option '-cc1'

So this is a from-scratch mutational fuzzer: no coverage feedback, no
instrumentation, just structured mutation plus signal detection and dedup. It is
weaker than libFuzzer and the docstring says so. It still finds the target bug,
which is the point of the exercise.

    python3 mutational_fuzzer.py --target ./target_overflow --runs 3000

Detection: the child exits with a negative return code (killed by a signal) or
with a stack-protector abort. Crashes are deduplicated by signature and written
to `crashes/`. No network. No browser.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import random
import signal
import subprocess
import sys
import tempfile
from pathlib import Path

MAGIC = b"FUZZ"
# Values that break length fields in practice: zero, boundary, wrapped, max.
INTERESTING = (0, 1, 15, 16, 17, 31, 32, 255, 256, 1023, 4095, 0xFFFF)


def seed_corpus() -> list[bytes]:
    return [
        MAGIC + (4).to_bytes(2, "little") + b"AAAA",
        MAGIC + (0).to_bytes(2, "little"),
        MAGIC + (16).to_bytes(2, "little") + b"A" * 16,
        b"NOPE" + (8).to_bytes(2, "little") + b"BBBBBBBB",
    ]


def mutate(data: bytes, rng: random.Random) -> bytes:
    choice = rng.randrange(7)
    if choice == 0:  # bit flip
        if not data:
            return bytes([rng.randrange(256)])
        buf = bytearray(data)
        index = rng.randrange(len(buf))
        buf[index] ^= 1 << rng.randrange(8)
        return bytes(buf)
    if choice == 1:  # byte overwrite
        buf = bytearray(data)
        if buf:
            buf[rng.randrange(len(buf))] = rng.randrange(256)
        return bytes(buf)
    if choice == 2:  # splice the length field with an interesting value
        buf = bytearray(data if len(data) >= 6 else MAGIC + b"\x00\x00")
        value = rng.choice(INTERESTING)
        buf[4:6] = value.to_bytes(2, "little", signed=False)
        return bytes(buf)
    if choice == 3:  # grow the payload so the length has bytes to copy
        buf = bytearray(data if len(data) >= 6 else MAGIC + b"\x00\x00")
        buf[4:6] = rng.choice(INTERESTING).to_bytes(2, "little", signed=False)
        buf += bytes(rng.randrange(256) for _ in range(rng.randrange(1, 600)))
        return bytes(buf)
    if choice == 4:  # truncate
        return data[: rng.randrange(len(data) + 1)] if data else b""
    if choice == 5:  # insert
        buf = bytearray(data)
        at = rng.randrange(len(buf) + 1) if buf else 0
        buf[at:at] = bytes(rng.randrange(256) for _ in range(rng.randrange(1, 9)))
        return bytes(buf)
    # delete a run
    if len(data) < 2:
        return data
    start = rng.randrange(len(data))
    end = min(len(data), start + rng.randrange(1, 9))
    return data[:start] + data[end:]


def classify(returncode: int, stderr: str) -> str | None:
    if returncode < 0:
        name = signal.Signals(-returncode).name
        return f"SIGNAL_{name}"
    if "stack smashing detected" in stderr or "*** stack smashing" in stderr:
        return "STACK_PROTECTOR"
    if "AddressSanitizer" in stderr:
        return "ASAN"
    if "Segmentation fault" in stderr:
        return "SEGV_TEXT"
    return None


def run_one(target: Path, data: bytes, timeout: float) -> tuple[int, str]:
    with tempfile.NamedTemporaryFile(delete=False) as handle:
        handle.write(data)
        path = handle.name
    try:
        proc = subprocess.run(
            [str(target), path], capture_output=True, text=True, timeout=timeout
        )
        return proc.returncode, proc.stderr
    except subprocess.TimeoutExpired:
        return -signal.SIGKILL, "timeout"
    finally:
        os.unlink(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Mutational fuzzer. Sandbox only.")
    parser.add_argument("--target", required=True)
    parser.add_argument("--runs", type=int, default=3000)
    parser.add_argument("--seed", type=int, default=1337)
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--crashes", default="crashes")
    args = parser.parse_args(argv)

    target = Path(args.target).resolve()
    if not target.exists():
        print(f"target not found: {target}")
        return 2
    if not os.access(target, os.X_OK):
        print(f"target not executable: {target}")
        return 2

    rng = random.Random(args.seed)
    corpus = seed_corpus()
    seen: dict[str, bytes] = {}
    crash_dir = Path(args.crashes)
    executions = 0

    print(f"target {target.name}  runs={args.runs}  seed={args.seed}")
    for _ in range(args.runs):
        if corpus and rng.random() < 0.75:
            base = rng.choice(corpus)
        else:
            base = b""
        data = mutate(base, rng)
        executions += 1
        returncode, stderr = run_one(target, data, args.timeout)
        label = classify(returncode, stderr)
        if label is None:
            if len(corpus) < 64 and data not in corpus:
                corpus.append(data)
            continue
        if label not in seen:
            seen[label] = data
            crash_dir.mkdir(parents=True, exist_ok=True)
            digest = hashlib.sha256(data).hexdigest()[:12]
            path = crash_dir / f"{label}-{digest}.bin"
            path.write_bytes(data)
            print(f"  NEW {label:<18} {len(data):>4} bytes  {path.name}")
    print(f"executions {executions}  unique crashes {len(seen)}")
    for label in seen:
        print(f"  {label}")
    return 0 if seen else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
