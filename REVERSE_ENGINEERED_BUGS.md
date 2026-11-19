# REVERSE ENGINEERED CHROME BUG TYPES

**Mode: REVERSE ENGINEER. SANDBOX ONLY. PRACTICE ONLY.**

19 bug types. 8 steps each. Mastery scored honestly, starting from 0 and capped
by what this machine can prove.

**Every CVE identifier in this document is UNRESOLVED.** I have no verified
source in this environment — no Chromium checkout, no issue tracker access, no
release notes to cite. A number that looks right but cannot be checked is worse
than a blank, so the blank stays. The bug *mechanisms* are described from code
shape and are reproducible in the sandbox; the citation fields are not.

Environment limits that cap every score: see `CHROME_GAP_FILL.md`. Short
version — no Chromium source, no working ASAN, clang cannot compile, no gdb, no
V8 shell, no browser binary, 5.3 G free disk.

Scores: 0 = nothing verifiable. 85 = mastery. Highest here is **40**.

---

## 1. Use-after-free (browser / renderer / GPU)

**Score 30 / 100** — mechanism proven, real target not reproduced.

1. **Find real CVE.** UNRESOLVED. No verified identifier available here.
2. **Tear down.** The shape: an object is destroyed, its owner drops the
   reference, and a second component keeps a raw pointer to it. The lifetime ends
   in one file and the use happens in another, which is why the bug survives
   review. Typical sites: IPC callbacks holding a raw `this`, observer lists not
   unregistered in the destructor, and a `WeakPtr` that was never used where a
   raw pointer was.
3. **Patch diff.** UNRESOLVED as a commit. The fix *class* is invariant: end the
   reference at destruction (`= nullptr`, deregister the observer, or switch to a
   `WeakPtr` that invalidates). A fix that only adds a null check at the use site
   treats the symptom.
4. **Rebuild vuln.** `sandbox/chrome/exercises/uaf/uaf.c` — quarantined allocator,
   poison byte, header state. Reproduces the stale-write shape.
5. **Trigger.** `./uaf` → `use-after-free WRITE ... 20 of 32 bytes clobbered`,
   rc=1. `./uaf --fixed` → clean, rc=0.
6. **Variant hunt.**
   - Destroy the owner while an in-flight IPC reply still holds the callback.
   - Free a buffer, then let a second thread read it via a cached pointer.
   - Resize a container while an iterator into it is still live.
7. **Detection rule.** Poison freed blocks and flag any write where
   `header.state == FREE`. In a real build: ASAN with quarantine, plus an
   allocator that does not reuse immediately, because reuse is what hides UAF.
8. **Report.** Structure drafted; CVE, version range, and patch commit UNRESOLVED.
   Severity depends on what the freed object contained — a token or a vtable
   pointer grades differently from a buffer of zeros, and I cannot grade that
   without the real target.

## 2. Heap buffer overflow / OOB write

**Score 30 / 100** — same proof as class 6, different entry point.

1. **Find real CVE.** UNRESOLVED.
2. **Tear down.** A size computed from input, a destination allocated from a
   different number, and a copy that trusts the first. Heap rather than stack
   means the overflow lands next to another allocation, which is what turns it
   into controlled corruption instead of a crash.
3. **Patch diff.** UNRESOLVED. Fix class: allocate from the same value used to
   copy, or clamp the copy to the destination (`base::span`, `CHECK_LE`).
4. **Rebuild vuln.** Covered by `fuzz/target_overflow.c` (stack variant). A heap
   variant needs `-fsanitize=address` to see the redzone, which is blocked; the
   quarantine allocator can model it.
5. **Trigger.** `len=4095` → `*** stack smashing detected ***`, rc=134.
6. **Variant hunt.**
   - Length in elements vs length in bytes (the classic ×4).
   - Signed length that goes negative and wraps in the size computation.
   - Grow-then-copy where the buffer is reallocated but the old pointer is used.
7. **Detection rule.** Every `memcpy`/`memmove` destination must be derived from
   the same length expression as the copy count. Flag any call where the
   destination capacity and the copy count trace to different variables.
8. **Report.** Structure drafted; identifiers UNRESOLVED.

## 3. OOB read / info leak

**Score 5 / 100** — mechanism only, no exercise built.

1. **Find real CVE.** UNRESOLVED.
2. **Tear down.** A read past the end of a buffer whose contents are then
   returned to a less privileged context: uninitialised memory, a stale object,
   or a length that is trusted on read. The impact is not corruption, it is
   disclosure — an ASLR break or a token.
3. **Patch diff.** UNRESOLVED. Fix class: bound the read, zero-initialise the
   struct, or return an explicit length instead of a sentinel.
4. **Rebuild vuln.** NOT BUILT. A useful exercise needs a real serialisation
   boundary (an IPC message that carries the leaked bytes), which needs a
   browser.
5. **Trigger.** UNRESOLVED.
6. **Variant hunt.**
   - Struct padding serialised whole and shipped to another process.
   - A length field trusted on deserialisation before the buffer is validated.
   - An error path that returns a partially filled buffer.
7. **Detection rule.** MSan for uninitialised reads; in serialisation, assert
   every byte of an outbound struct was written.
8. **Report.** UNRESOLVED.

## 4. Type confusion (V8 and Blink)

**Score 30 / 100** — feedback → specialise → confuse proven; real TurboFan not.

1. **Find real CVE.** UNRESOLVED.
2. **Tear down.** The optimiser specialises on observed types and removes the
   check that enforced them. The check was correct when it was removed and wrong
   one input later. In V8 the payoff is a tagged value used as a machine integer:
   a pointer treated as an index.
3. **Patch diff.** UNRESOLVED. Fix class: reinstate the map check, or narrow the
   specialisation so the removed check cannot be wrong (a dependency the
   optimiser can invalidate on map transition).
4. **Rebuild vuln.** `sandbox/chrome/exercises/v8_type_confusion/jit_type_confusion.py`.
   Feedback vector, monomorphic specialisation, elided check, string input.
5. **Trigger.** `CONFUSION fast=Value(smi, '12') correct=Value(string, '12')`,
   rc=1. `--fixed` deoptimises, rc=0.
6. **Variant hunt.**
   - Make the type stable for longer so the optimiser is more confident.
   - Change the type through a path the feedback vector does not record
     (prototype, `Proxy`, `valueOf`).
   - Invalidate a map the optimiser marked stable, after compilation.
7. **Detection rule.** Any removed check must be tied to a dependency the
   optimiser can invalidate. Fuzz the *type* dimension: run the same function
   with every combination of Smi / Double / String / Object / Hole.
8. **Report.** Structure drafted; identifiers UNRESOLVED.

## 5. Double-free / use-after-scope

**Score 10 / 100** — detector path exists, no dedicated exercise.

1. **Find real CVE.** UNRESOLVED.
2. **Tear down.** Two owners both free the same object, or a scope-exit
   destructor runs while the object is still reachable. The second free corrupts
   the allocator's freelist, which is a write primitive in the right hands.
3. **Patch diff.** UNRESOLVED. Fix class: one owner, or a null-after-free plus
   ownership moved into a smart pointer.
4. **Rebuild vuln.** PARTIAL — `q_free` in the UAF exercise detects a second free
   (`DOUBLE-FREE of %p`) but no exercise drives that path yet.
5. **Trigger.** Not driven. Honest score consequence: 10, not 30.
6. **Variant hunt.**
   - Error path frees, then the normal path frees again.
   - Two threads racing on a refcount decrement to zero.
   - A `unique_ptr` released while a raw pointer is still held.
7. **Detection rule.** Refuse to free a block already marked FREE, and never
   reuse quarantined blocks. ASAN's double-free report is the model.
8. **Report.** UNRESOLVED.

## 6. Integer overflow leading to buffer overflow

**Score 40 / 100** — the only class with a full measured cycle. Highest score here.

1. **Find real CVE.** UNRESOLVED. This is the class where a wrong citation is
   most tempting, because the shape is famous. The blank stays.
2. **Tear down.** `len` is a `uint16_t` from the input, `dest` is 16 bytes, and
   nothing compares them. The length is trusted because it arrived in a struct
   with a valid magic value — the magic check creates false confidence.
3. **Patch diff.** UNRESOLVED as a commit. The repair is visible in
   `fuzz/target_overflow_fixed.c` and it is **two** conditions, which is the
   lesson: `len <= dest_size` **and** `len <= bytes_available`. Checking only the
   first still allows an out-of-bounds *read* of the source, which is exactly the
   6-byte SIGSEGV case the fuzzer found.
4. **Rebuild vuln.** `fuzz/target_overflow.c`, gcc `-O0 -fstack-protector-strong`.
5. **Trigger.** Fuzzer, 2000 mutations: **2 unique crashes**.
   `len=4095` → SIGABRT `*** stack smashing detected ***`.
   `len=65535` with 0 payload bytes → SIGSEGV.
6. **Variant hunt.**
   - `len * sizeof(elem)` where the multiply wraps before the comparison.
   - A signed length that passes `> 0` and then wraps negative in the copy.
   - Header length validated, but a *second* length later in the payload is not.
7. **Detection rule.** For every copy: destination capacity, copy count, and
   source availability must all be checked, and all three must trace to
   validated values. Automated rule: flag any `memcpy(dst, src, n)` where `n`
   comes from input and is not preceded by two comparisons.
8. **Report.** Full structure possible for the synthetic target, including the
   two-condition fix and the re-fuzz evidence. CVE mapping UNRESOLVED.

## 7. JIT bug — TurboFan / Maglev

**Score 25 / 100** — model shares the mechanism, not the engine.

1. **Find real CVE.** UNRESOLVED.
2. **Tear down.** TurboFan reduces a node using a type the feedback promised;
   Maglev makes the same bet with a different pipeline. The bug is always the
   same bet: a check removed because it was true during profiling.
3. **Patch diff.** UNRESOLVED.
4. **Rebuild vuln.** Shared with class 4 — the model is a feedback-driven
   specialiser, not TurboFan. It does not model nodes, effects, or `CheckMaps`
   rewiring, so it cannot reproduce a real TurboFan bug.
5. **Trigger.** Class 4's trigger. No TurboFan-specific trigger without `d8`.
6. **Variant hunt.** Side-effect ordering after a deopt; a check hoisted above a
   call that invalidates it; feedback recorded for one map and applied to a
   sibling map.
7. **Detection rule.** Every reduction that removes a check must carry a
   dependency; fuzz with `--always-opt` style forced compilation so the optimised
   path runs on first input.
8. **Report.** UNRESOLVED.

## 8. WASM bug — Liftoff / Turbofan

**Score 0 / 100** — no runtime, no exercise.

1. **Find real CVE.** UNRESOLVED.
2. **Tear down.** Candidate shapes: a bounds check on linear memory removed or
   mis-scaled, a signature mismatch between JS and WASM, or a table index not
   validated before an indirect call.
3. **Patch diff.** UNRESOLVED.
4. **Rebuild vuln.** NOT BUILT. Needs a WASM runtime and a JIT.
5. **Trigger.** UNRESOLVED.
6. **Variant hunt.** `memory.grow` racing an outstanding view; a function table
   index past the table length; a JS value coerced to `i64` with the wrong
   signedness.
7. **Detection rule.** Every linear-memory access must show `offset + width <=
   mem_size` after scaling. Fuzz module bytes, not JS.
8. **Report.** UNRESOLVED.

## 9. V8 sandbox escape

**Score 0 / 100.** Requires a real V8 sandbox to escape.

1-8. UNRESOLVED. The prerequisite is a build where the V8 heap sandbox is
enabled and an in-sandbox corruption primitive exists. Neither exists here. Any
write-up would be a description of someone else's work with no verification.

## 10. V8 logic bug

**Score 20 / 100** — the specialisation logic is modelled; no real spec bug.

1. **Find real CVE.** UNRESOLVED.
2. **Tear down.** A spec corner where the fast path and the spec disagree:
   coercion order, `-0`, hole vs `undefined`, prototype lookup during
   iteration. No memory corruption required — the wrong value is the bug.
3. **Patch diff.** UNRESOLVED.
4. **Rebuild vuln.** Class 4's model demonstrates specialisation-vs-reality, but
   a *specification* bug needs a real engine to compare against the spec.
5. **Trigger.** UNRESOLVED.
6. **Variant hunt.** Coercion inside a builtin that the fast path skips;
   `Array.prototype` methods mutated during iteration; observable side effects
   reordered across an inlined call.
7. **Detection rule.** Differential testing: run the same program interpreted and
   optimised and compare results. That is exactly the model's detector.
8. **Report.** UNRESOLVED.

## 11. Mojo IPC abuse / privilege escalation

**Score 25 / 100** — authorisation flaw proven, real Mojo not.

1. **Find real CVE.** UNRESOLVED.
2. **Tear down.** The broker validates *kind* and not *ownership*. The renderer
   is sandboxed so it cannot touch the filesystem; it asks the broker for a
   handle, and the broker, holding more privilege, complies. Confused deputy.
3. **Patch diff.** UNRESOLVED. Fix class: authorise the principal, not just the
   object — `handle.owner_pid == sender_pid`, or a capability the caller must
   present.
4. **Rebuild vuln.** `sandbox/chrome/exercises/mojo_confused_deputy/mojo_confused_deputy.py`.
5. **Trigger.** `ESCAPE: pid 4242 now holds file '...' owned by pid 1`, rc=1.
   `--fixed` → `DENIED`, rc=0.
6. **Variant hunt.**
   - Validate ownership of the first handle in a message and trust the rest.
   - A handle duplicated to a process that then forwards it again.
   - A callback re-entered after the receiving object is gone.
7. **Detection rule.** Every IPC handler that takes a handle must check the
   sender against the handle owner. Automated: flag handlers with an object
   parameter and no principal check.
8. **Report.** Structure drafted; identifiers UNRESOLVED.

## 12. Sandbox escape — GPU process

**Score 0 / 100.** Needs a real GPU process and a real sandbox.

1-8. UNRESOLVED. Candidate shapes exist (a GPU command buffer index trusted
after validation, a shared-memory mapping with the wrong protection, a driver
callback outliving its context) but without a browser and a driver none can be
verified, and an unverified shape is a guess.

## 13. Sandbox escape — renderer to broker

**Score 20 / 100** — same mechanism as class 11, scored separately.

1. **Find real CVE.** UNRESOLVED.
2. **Tear down.** Same confused-deputy pattern, one boundary out: the renderer
   asks a more privileged process to act on its behalf, and the privileged
   process does not verify who asked.
3. **Patch diff.** UNRESOLVED.
4. **Rebuild vuln.** Class 11's model is the mechanism; the difference is which
   boundary is crossed, not how.
5. **Trigger.** Class 11's trigger.
6. **Variant hunt.** A broker that trusts a message because it came over a
   channel it believes is renderer-only; a service exposed to the wrong process
   type in the interface registry.
7. **Detection rule.** Enumerate every interface and the process types allowed to
   bind it; flag any interface reachable by a renderer that performs a
   privileged action.
8. **Report.** UNRESOLVED.

## 14. Site isolation bypass

**Score 0 / 100.** Needs a browser with two real origins.

1-8. UNRESOLVED. The mechanism requires an actual process model and actual
origins. A model would only restate the definition of site isolation.

## 15. UXSS / universal XSS

**Score 0 / 100.** Needs a browser and a page I control.

1-8. UNRESOLVED. Same reason: script execution across origins cannot be
demonstrated without an engine.

## 16. SOP bypass / CORS bypass

**Score 0 / 100.**

1-8. UNRESOLVED. Requires two origins and a real fetch stack. The model would be
a mock of the thing being tested.

## 17. Permission bypass (camera / mic / geolocation / file)

**Score 0 / 100.**

1-8. UNRESOLVED. Requires a browser with a permission system and a real
permission prompt. No binary, no test.

## 18. DOM / Blink logic bug

**Score 0 / 100.**

1-8. UNRESOLVED. Requires Blink and a DOM. The code shape (a mutation during
tree traversal, a stale node reference after adoption, an event fired in the
wrong order) is describable and untestable here.

## 19. Fuzzer-found crash triage (ASAN trace → root cause)

**Score 35 / 100** — real crash triage done, but on a synthetic target.

1. **Find real CVE.** Not applicable; this class is the triage skill.
2. **Tear down.** A triage method, not a bug. Read the signal, locate the faulting
   frame, identify the object and its state, then ask which invariant failed
   before the fault.
3. **Patch diff.** Applied: `target_overflow_fixed.c`, two bounds checks.
4. **Rebuild vuln.** `fuzz/target_overflow.c`.
5. **Trigger.** 2 unique crashes, both triaged:

   | Input | Signal | Declared len | Destination | Verdict |
   |---|---|---|---|---|
   | 391 bytes | SIGABRT, stack smashing | 4095 | 16 | write overflow, 4079 bytes past |
   | 6 bytes | SIGSEGV | 65535 | 16 | source read past end of buffer |

   The second one is the useful one: it is a *different* root cause wearing the
   same input format. A triage that stopped at "length too large" would have
   missed it.
6. **Variant hunt.** Feed the triage the same corpus with the length field
   excluded, to check the crash is the length and not the magic.
7. **Detection rule.** Deduplicate by signal plus faulting frame, not by exit
   code. Two inputs that both abort can be two bugs.
8. **Report.** Full cycle done for the synthetic target: crash, triage table,
   two-condition repair, re-fuzz clean (0 crashes in 2000 runs). Real-ASAN trace
   reading remains UNRESOLVED without ASAN.

---

## Mastery tracker

**Scoring authority is now `CHROME_MASTERY_85.md`.** Chrome mastery is scored as
seven sub-skills averaged, not as one number, because one number let a working
fuzzer hide an empty Blink column. The per-bug-type scores below are the detail
underneath that average.

Verified citations, each backed by a hashed record in `sandbox/chrome/cves/`:

| CVE | Class | Fixed in |
|---|---|---|
| CVE-2020-6418 | Type confusion in V8 | 80.0.3987.122 |
| CVE-2024-2887 | Type confusion in WebAssembly | 123.0.6312.86 |
| CVE-2023-7024 | Heap buffer overflow in WebRTC | 120.0.6099.129 |

A verified ID is a citation, not an analysis. None of the three has a patch diff,
a PoC, or a variant yet, and `tests/test_chrome_cves.py` fails if the records
ever imply otherwise.

| # | Bug type | Score | What is proven | What is missing |
|---|---|---|---|---|
| 1 | Use-after-free | 30 | detector + repair | real target, CVE, ASAN |
| 2 | Heap OOB write | 30 | crash + repair | heap redzone (ASAN) |
| 3 | OOB read / leak | 5 | mechanism | exercise, serialisation boundary |
| 4 | Type confusion | 30 | feedback/JIT model | real TurboFan, `d8` |
| 5 | Double-free / scope | 10 | detector path | exercise that drives it |
| 6 | Integer → overflow | **40** | full measured cycle | CVE, real code |
| 7 | JIT TurboFan/Maglev | 25 | shared model | engine internals |
| 8 | WASM | 0 | — | runtime |
| 9 | V8 sandbox escape | 0 | — | V8 build with sandbox |
| 10 | V8 logic | 20 | differential method | real engine |
| 11 | Mojo IPC | 25 | confused-deputy + fix | real `.mojom` |
| 12 | GPU escape | 0 | — | browser + driver |
| 13 | Renderer → broker | 20 | same mechanism | real boundary |
| 14 | Site isolation | 0 | — | two origins |
| 15 | UXSS | 0 | — | browser |
| 16 | SOP / CORS | 0 | — | browser |
| 17 | Permission bypass | 0 | — | browser |
| 18 | DOM / Blink logic | 0 | — | Blink |
| 19 | Crash triage | 35 | real triage of 2 crashes | ASAN traces |

**Average 14.2 / 100. Categories at 85 or above: 0 of 19.**

## Batch reviews

**Classes 1-5.** One pattern repeats: a check that was true when it was made and
false when it was used. UAF is a lifetime check made at allocation time. Type
confusion is a type check made at compile time. Class 4 and class 1 are the same
bug at different layers — one ends an object's life too early, the other ends a
check's validity too early. Detection rule added: any check that is not tied to
something that can invalidate it is a bug waiting for the wrong input.

**Classes 6-10.** The second pattern: a value trusted because of where it came
from. The magic bytes in the fuzz target create confidence that suppresses the
bounds check. WASM table indices and JIT feedback are the same shape — provenance
is not validation. Detection rule added: a value from outside the trust boundary
must satisfy every invariant the code relies on, not just the one the parser
happened to check.

**Classes 11-15 and 16-19.** Not yet reviewable at a score that would make a
pattern meaningful. Both boundary-crossing classes that were modelled (11, 13)
show the same thing: privilege is checked on the object and not on the
principal.

## Status

| Item | Value |
|---|---|
| Mode | REVERSE ENGINEER, sandbox only |
| Bug types with a runnable proof | 4 (1, 4, 6, 11) |
| Bug types with a full measured cycle | 1 (6) |
| Mastery at 85+ | 0 |
| Real CVEs verified | 0 — all marked UNRESOLVED |
| Live-site testing | none |
| Bug Hunters submissions | none, and none until GO LIVE |

I have not mastered this. I have four working mechanisms, one complete measured
cycle, and a documented list of what the machine cannot do. Reporting anything
higher would be inventing a score.
