# CHROME VRP — GAP FILL

**Mode: SANDBOX ONLY. No live site. No live Chrome. No Bug Hunters submission
until Sean says GO LIVE.**

Self-audit of what I can and cannot do for each Chrome bug class, measured in
this environment instead of assumed. Every "cannot" below has a command result
behind it.

## 0. What the machine actually supports

Probed on 2026-11-18.

| Tool | State | Evidence |
|---|---|---|
| gcc 14.2.0 | **usable** | compiled the UAF exercise and the fuzz target |
| UBSan (`-fsanitize=undefined`) | **usable** | built and ran a probe; does not catch UAF, by design |
| ASAN (`-fsanitize=address`) | **broken** | `CHECK failed: sanitizer_allocator_primary64.h:131`, exit on start |
| clang 21.1.8 | **unusable** | `proot error: unknown option '-cc1'`; cannot compile a hello world |
| libFuzzer | **impossible** | needs clang, and clang cannot compile |
| gdb | missing | `command -v gdb` → none |
| valgrind | missing | `command -v valgrind` → none |
| docker / podman | missing | no container runtime |
| chrome / chromium | missing | no browser binary |
| gn / ninja / autoninja | missing | no build system for Chromium |
| objdump / readelf | present | usable for binary inspection |
| RAM | 3 GB total, ~0 free | `free -g` |
| Disk | 96% used, 5.3 G free | `df -h /` |

The consequence is blunt: **a real Chromium build, a real ASAN run, and a real
fuzzing campaign are all impossible here.** Anything I claim has to come from
something that actually runs on this box, or it is marked UNRESOLVED.

## 1. Top 10 gaps

### Gap 1 — No Chromium source tree
- **Lack:** the vulnerable functions, the patch diffs, `git log` on `src/`.
  Without it, "what did Google change" is unanswerable, and guessing a patch
  would be fabrication.
- **Fills it:** `depot_tools` + `fetch chromium` (~100 GB) on a machine with
  disk headroom. `git log --oneline -- src/` then gives real fix commits.
- **Proof exercise:** pick one CVE, `git log -S` the fix, paste the diff, and
  rebuild the vulnerable version beside it.
- **Status:** BLOCKED (disk, and no checkout).

### Gap 2 — ASAN does not start
- **Lack:** Chrome's primary memory-corruption detector. The allocator fails its
  own init before `main`.
- **Fills it:** a working clang toolchain or a newer ASAN runtime; or a kernel
  with the expected address-space layout. Valgrind would be an alternative and
  is also missing.
- **Proof exercise:** the UAF exercise, reproduced under ASAN, showing the
  `heap-use-after-free` report with the alloc/free stacks.
- **Status:** SUBSTITUTED — a quarantine allocator with poison bytes stands in
  (`sandbox/chrome/exercises/uaf/uaf.c`). It proves the pattern and detects the
  write; it is not ASAN and does not claim to be.

### Gap 3 — clang cannot compile, so no libFuzzer
- **Lack:** coverage-guided fuzzing, MSan, and `-fsanitize=fuzzer`.
- **Fills it:** a native clang build for this architecture, or a container with
  one.
- **Proof exercise:** `-fsanitize=fuzzer` target that finds the planted overflow
  in under 20k runs.
- **Status:** SUBSTITUTED — a handwritten mutational fuzzer
  (`sandbox/chrome/fuzz/mutational_fuzzer.py`) found 2 unique crashes in 2000
  runs. No coverage feedback, so it is strictly weaker than libFuzzer.

### Gap 4 — No sandbox or VM
- **Lack:** a disposable boundary to run untrusted binaries and a second OS to
  model process separation.
- **Fills it:** any container runtime, or a VM with snapshots.
- **Proof exercise:** run the escape model as two real processes at different
  privilege levels instead of one Python process playing both.
- **Status:** BLOCKED, MODELLED — exercise 3 models the authorisation flaw
  in-process. It proves the logic, not the sandbox.

### Gap 5 — No debugger
- **Lack:** gdb. A crash cannot be walked back to a frame, a register, or a
  freed allocation.
- **Fills it:** `gdb` plus a binary built with `-g`, ideally with `pwndbg`.
- **Proof exercise:** attach to the UAF target, break on the write, print the
  allocation state.
- **Status:** BLOCKED, partially compensated by `objdump`/`readelf` and by
  writing detectors into the target itself.

### Gap 6 — No V8 shell (`d8`)
- **Lack:** a JS runtime that exposes V8's internals, `--allow-natives-syntax`,
  and the optimisation/deopt pipeline.
- **Fills it:** a V8 build (`tools/dev/gm.py x64.release`) or a `d8` from a
  Chromium build.
- **Proof exercise:** trigger a real deopt, print the feedback vector, show the
  map check being removed.
- **Status:** MODELLED — exercise 2 reproduces the feedback → specialise →
  confuse chain in Python.

### Gap 7 — No Blink/DOM harness
- **Lack:** a headless browser to test UXSS, SOP, CORS, and permission logic.
- **Fills it:** headless Chromium in a container, driven by CDP, never pointed
  at a live site.
- **Proof exercise:** two origins, one iframe, a documented SOP check, then a
  bypass in a page I control.
- **Status:** BLOCKED (no browser binary).

### Gap 8 — No Bug Hunters corpus or CVE database
- **Lack:** verified CVE identifiers, report text, and patch commits.
- **Fills it:** the Chromium issue tracker, the Chrome release blog, and
  `git log` in a real checkout.
- **Proof exercise:** for each bug class, cite CVE + fix commit + the diff.
- **Status:** **UNRESOLVED.** I will not write a CVE number I cannot verify. The
  bug *mechanisms* below are described from the code shape, and every CVE field
  is explicitly marked UNRESOLVED.

### Gap 9 — No Mojo IDL or generated bindings
- **Lack:** the real `.mojom` interfaces, the generated C++ bindings, and the
  broker's actual validation code.
- **Fills it:** a Chromium checkout plus `mojom` generation.
- **Proof exercise:** a real interface definition, a real serialisation, and a
  real ownership check.
- **Status:** MODELLED — exercise 3.

### Gap 10 — Not enough machine
- **Lack:** disk (5.3 G free against ~100 G for a Chromium build) and RAM
  (3 GB against the 16 GB a link step wants).
- **Fills it:** a build host or a cloud runner. Nothing local will fix this.
- **Proof exercise:** `gn gen out/asan && autoninja -C out/asan chrome`.
- **Status:** BLOCKED. Hard limit, not a preference.

## 2. What this means for the mastery claim

Mastery needs steps that cannot be faked: a real CVE, a real patch diff, a real
build, a real crash under a real detector, a variant hunt on real code. Six of
those are blocked here. What is left is mechanism: models and synthetic targets
that reproduce the *shape* of each bug and detect it.

That is worth something and it is not mastery. Scores in
`REVERSE_ENGINEERED_BUGS.md` reflect exactly that split: mechanism credit, no
credit for the steps that require the missing toolchain. **No category is at 85.
The highest is 40.**

## 3. Plan, in order

1. Get a machine that can hold a Chromium checkout and build it (gap 1, 10).
2. Build `out/asan` with a working toolchain (gap 2, 3).
3. Reproduce one real CVE per class from the checkout (gap 8).
4. Add coverage-guided fuzzing once clang works (gap 3).
5. Only then touch a submission path, and only after Sean says GO LIVE.

Until step 1 happens, every additional "exercise" raises mechanism knowledge and
does not raise mastery. I will keep saying that rather than inflating the scores.
