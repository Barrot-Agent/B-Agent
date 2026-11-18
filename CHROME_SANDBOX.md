# CHROME SANDBOX

**Sandbox only. No live site. No live Chrome install. No Bug Hunters submission
without Sean's explicit GO LIVE.**

This directory holds everything that runs. It is deliberately small: what the
machine cannot support is documented as blocked rather than faked.

## Layout

```
sandbox/chrome/
├── exercises/
│   ├── uaf/                       bug class 1  — use-after-free (C, gcc)
│   │   ├── uaf.c                  quarantine allocator + poison-byte detector
│   │   └── uaf                  built binary, safe to delete
│   ├── v8_type_confusion/         bug class 4  — type confusion (Python model)
│   │   └── jit_type_confusion.py  feedback vector -> specialise -> confuse
│   ├── mojo_confused_deputy/      bug class 11 — Mojo IPC (Python model)
│   │   └── mojo_confused_deputy.py
│   └── run_all.py                 runs all three, prints PASS/FAIL
└── fuzz/
    ├── target_overflow.c          bug class 6  — length field -> overflow
    ├── target_overflow_fixed.c    the repair, two bounds checks
    ├── target_overflow           built, vulnerable
    ├── target_overflow_fixed     built, repaired
    ├── mutational_fuzzer.py       handwritten fuzzer (libFuzzer unavailable)
    └── crashes/                   2 deduplicated crash inputs, kept as evidence
```

## Run it

```bash
python3 sandbox/chrome/exercises/run_all.py

cd sandbox/chrome/fuzz
gcc -O0 -g -fstack-protector-strong -o target_overflow target_overflow.c
gcc -O0 -g -fstack-protector-strong -o target_overflow_fixed target_overflow_fixed.c
python3 mutational_fuzzer.py --target ./target_overflow --runs 2000
python3 mutational_fuzzer.py --target ./target_overflow_fixed --runs 2000
```

Tests: `python -m pytest tests/test_chrome_exercises.py tests/test_chrome_fuzz.py -q`

## Exercise 1 — use-after-free

`exercises/uaf/uaf.c`

The bug: `q_free(buf)` ends ownership, the stale reference keeps being written.
This is the same shape as every UAF that matters: two components disagree about
who owns the object and when its lifetime ended.

The detector: ASAN cannot start here, so the program carries its own model of
ASAN — a header per block recording LIVE or FREE, a poison byte on free, and no
block reuse. A write after free is visible as poison that changed. `q_check`
reports it.

```
$ ./uaf
  [detector] use-after-free WRITE of 0x30000232c8, 20 of 32 bytes clobbered
  RESULT: BUG DETECTED          rc=1

$ ./uaf --fixed
  RESULT: clean                 rc=0
```

The repair: `buf = NULL` immediately after the free, so the reference cannot
outlive the ownership. That is what a real fix looks like — not a check at use,
but an end to the lifetime of the reference.

## Exercise 2 — V8 type confusion

`exercises/v8_type_confusion/jit_type_confusion.py`

The bug, in five steps:

1. the interpreter records feedback: every `add` at this site saw two Smis
2. the optimiser trusts it, specialises for Smis, and **deletes the map check**
3. a string arrives, which JavaScript permits at any time
4. the specialised path treats the string payload as an integer
5. the wrong value comes back **without crashing**

```
$ python3 jit_type_confusion.py
  feedback: 4 samples, monomorphic_smi=True
  optimiser: specialised add() for Smi, map check elided
  CONFUSION fast=Value(smi, '12') correct=Value(string, '12')
  RESULT: TYPE CONFUSION        rc=1
```

`Value(smi, '12')` is the whole bug class in one line: a heap pointer wearing an
integer tag. In a real engine the next step is using it as an index.

The repair: the guard is reinstated and the site deoptimises when the type
changes. Real engines do this with a map check that the optimiser had proven
"redundant" from feedback that was only ever a sample.

## Exercise 3 — Mojo confused deputy

`exercises/mojo_confused_deputy/mojo_confused_deputy.py`

The bug is not a memory error. It is an authorisation error: the broker checks
that a handle is the right *kind* and never checks that it belongs to the
*caller*.

```
$ python3 mojo_confused_deputy.py
  broker: duplicated handle 64 (file, '/home/user/.ssh/id_ed25519') to pid 4242
  ESCAPE: pid 4242 now holds file ... owned by pid 1
  RESULT: SANDBOX ESCAPE        rc=1
```

The renderer never breaks the sandbox. It asks the broker to cross the boundary
on its behalf, and the broker does, because the deputy is confused about who it
is serving.

The repair: compare `handle.owner_pid` to `sender_pid` and refuse.

## Fuzz lab — integer length to buffer overflow

`fuzz/target_overflow.c`

Format `"FUZZ" + uint16 length + payload`. The length is used as the copy size
and compared to nothing. 16-byte destination.

Measured, not asserted:

| Run | Result |
|---|---|
| 2000 mutations, vulnerable target | **2 unique crashes** |
| `len=4095`, 391-byte input | SIGABRT, `*** stack smashing detected ***` |
| `len=65535`, 6-byte input | SIGSEGV |
| both crash inputs against the repair | rc=0 |
| 2000 mutations, repaired target | **0 crashes** |

Triage of the 6-byte case: the declared length is 65535 and only 0 payload bytes
exist, so the copy reads 64 KiB past the end of the file buffer. That is a second
bug hidden by the first: checking `len` against the destination is not enough if
`len` is not also checked against the bytes actually present. The repair has both
checks, and that is why it survives.

## Why there is no libFuzzer here

libFuzzer needs clang. clang 21.1.8 is installed but is an Android/Termux binary
inside proot and fails on every compile:

```
proot error: unknown option '-cc1'.
```

So the fuzzer is handwritten and honest about it: no coverage feedback, no
instrumentation, mutation by interesting values plus splice/grow/truncate. It is
weaker than libFuzzer. It still found the planted bug in 2000 runs, which is the
point of the exercise.

## Rules this sandbox obeys

- Never a live site. Never Sean's browser. Never a real profile.
- Never a submission to Bug Hunters until Sean says GO LIVE.
- Targets are synthetic, written here, and marked vulnerable on purpose.
- No network access in any exercise or fuzzer (AST-tested).
- A blocked step is reported as BLOCKED or UNRESOLVED, never as passed.
