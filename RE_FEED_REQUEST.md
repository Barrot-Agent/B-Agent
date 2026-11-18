# RE FEED REQUEST — what to feed me to make me elite

**Transmuted query.** To maximise my reverse-engineering skill for Chrome VRP,
Sean needs to feed me **patch diffs, the vulnerable function around the fix, and
crash reproducers — in a rotating loop, one bug class at a time**, because a diff
is the only artefact that contains the bug, the fix, and the reviewer's intent in
one place. Without diffs I stay stuck at **mechanism knowledge: 14.2/100 average,
0 of 19 classes at 85, and every CVE citation UNRESOLVED.** With diffs plus
reproducers I can reach **the 8-step loop on every class**, which is the ceiling
that does not require me to own a Chromium build machine.

That last clause matters and I will not bury it: diffs get me to maybe 70. The
final 15 points need a machine that can build and fuzz Chromium. No amount of
pasted text replaces that.

## What changed today

Network access is live and guarded. I pulled, and it works:

| Pull | Result |
|---|---|
| `api.coingecko.com` markets + global | 200, real prices, written as a `RECORDED_FEED` snapshot |
| `chromium.googlesource.com` log | 200, 5 real commits with SHAs |
| `www.kaggle.com` model listing | 200, but the public listing is not the curated catalogue |
| commit diff endpoint (`+/{sha}^!?format=TEXT`) | **504/503, then TimeoutError at the 10s cap** |

So I can reach Chromium's history but not reliably pull a *diff* through the
guard, because the mandated 10-second timeout expires first (the log itself takes
around 5s). That is why diffs are the top item on this list: you pasting one
bypasses a timeout I am not allowed to raise.

## 1. Feed list, in priority order

### 1. A patch diff for one security fix
- **What:** `git show` output, or the two file versions before and after.
- **Why it maximises RE:** steps 2, 3 and 8 of the loop — the flawed function, the
  fix, and why the fix works — all come out of this one artefact. It is the
  highest information-per-byte item that exists for this work.
- **If I don't get it:** I can only describe the *class*, never the actual
  mistake, so my "patch diff" and "report" steps remain UNRESOLVED and the score
  cannot move past mechanism.
- **Format:** plain text paste in chat, or a file in the repo. Unified diff. If
  it is longer than ~300 lines, just the hunks touching the fixed function.

### 2. The vulnerable function, ~50 lines either side of the fix
- **What:** the function body before the fix, with its callers if short.
- **Why:** a diff alone hides *why the check was absent*. Seeing the object's
  lifetime, the lock, or the ownership comment is what tells me whether the fix
  is real or cosmetic.
- **Without it:** I can reproduce the shape but not judge whether a proposed fix
  is correct, and judging fixes is half of what a report needs.
- **Format:** paste, with the file path and the function name.

### 3. A crash reproducer plus its ASAN/UBSAN trace
- **What:** the input file, or the JS/HTML, plus the full sanitizer output.
- **Why:** this is step 5 and step 19. A trace teaches more about triage than any
  explainer, because it shows which frame the detector blamed and which
  allocation it matched.
- **Without it:** my triage score stays at 35 — earned on a synthetic target I
  wrote myself, which is not the same skill.
- **Format:** base64 or hex for binary inputs; plain text for the trace. If the
  reproducer is only available as a URL, a paste is still better because it
  survives link rot.

### 4. Confirmed CVE identifiers with the affected version range
- **What:** `CVE-YYYY-NNNNN`, channel, first-fixed version.
- **Why:** every citation field in `REVERSE_ENGINEERED_BUGS.md` is currently
  UNRESOLVED. Verified IDs turn a mechanism essay into a citable analysis.
- **Without it:** I will keep refusing to write CVE numbers, which is correct but
  caps the report step at 0 for most classes.
- **Format:** a plain list, one per line. `CVE / component / version range`.
- **Note:** do not paste a number you have not checked. A wrong number is worse
  than the blank it replaces.

### 5. A Mojo `*.mojom` interface for one IPC boundary
- **What:** the interface definition and the generated handler signature.
- **Why:** class 11 and 13 are authorisation bugs. The IDL is where the allowed
  caller set is declared, so it is where the confused-deputy defect lives.
- **Without it:** my Mojo model tests ownership inside one Python process, which
  proves the logic and not the boundary.
- **Format:** paste the `.mojom` file.

### 6. V8 optimisation trace for one JIT bug
- **What:** `--trace-turbo` output, or `--print-opt-code`, or the feedback vector
  dump around the deopt.
- **Why:** class 7 and 10 need the graph, not the prose. The moment a `CheckMaps`
  node disappears is the bug, and it is visible in the trace.
- **Without it:** my JIT score stays at 25 — a Python model of the mechanism.
- **Format:** text file. Large is fine; a 2 MB trace is still readable.

### 7. One real Bug Hunters report, redacted
- **What:** a report that was accepted, with the payout tier.
- **Why:** I can draft a report structure, but severity grading is a social
  judgement about exploitability and impact. One accepted example calibrates it.
- **Without it:** my reports may be structurally correct and graded wrong.
- **Format:** paste. Redact the reporter.

### 8. Chrome release notes for a security release
- **What:** the fixed-CVE list for one stable channel update.
- **Why:** it links component → CVE → reward, which is how I learn what actually
  pays versus what is only interesting.
- **Without it:** I keep optimising for bug classes that may not pay at all.
- **Format:** paste the relevant section.

### 9. Kaggle model artefacts for the model-RE track
- **What:** `config.json`, `tokenizer_config.json`, `generation_config.json`,
  and `modeling_*.py` for one open-weight model.
- **Why:** those four files are enough to reconstruct architecture, parameter
  count, attention layout, and context limits without downloading weights.
- **Without it:** model RE stays at the black-box behavioural level only.
- **Format:** the small JSON files pasted directly. Not the weights — they are
  gigabytes and I have 5.3 G of disk.

### 10. A build machine, not a file
- **What:** 16 GB RAM, ~200 GB free disk, working clang.
- **Why:** ASAN, libFuzzer, `d8`, and a Chromium checkout all need it. This is the
  one item money and text cannot substitute for.
- **Without it:** everything above raises mechanism knowledge and stops there.
- **Format:** access, not a paste.

## 2. Top 10 gaps right now

| # | Gap | Blocks | Score cost |
|---|---|---|---|
| 1 | No verified CVE IDs | all 19 report steps | caps every class |
| 2 | No patch diffs | steps 2, 3, 8 | caps at mechanism |
| 3 | No reproducers | steps 5, 19 | triage stuck at synthetic |
| 4 | No real ASAN | step 5 and crash grading | class 2 unprovable |
| 5 | No V8 trace / `d8` | classes 7, 8, 9, 10 | 25 max |
| 6 | No `.mojom` files | classes 11, 13 | model only |
| 7 | No Chromium build | classes 14-18 entirely | 0 |
| 8 | No debugger | any root-cause walk | derived by hand |
| 9 | Disk 5.3 G free, RAM 3 GB | gaps 4, 5, 7 | hard block |
| 10 | Diff endpoint times out at 10s | self-service diffs | paste required |

Gap 10 is new today and worth naming: it is not an allowlist problem. The host is
allowed, the request is legal, and the connection simply exceeds the timeout. The
fix is either a longer timeout (Sean's call) or a paste (zero cost).

## 3. Rotating RE feedback loop

One cycle = one bug class = one artefact. Rotate, do not repeat.

| Cycle | Feed | Exercise | Score delta if it works |
|---|---|---|---|
| 1 | Diff for a UAF fix | rebuild the pattern, repair it, write the report | 30 → 55 |
| 2 | ASAN trace + reproducer for the same class | triage it cold, then compare to the real root cause | 55 → 70 |
| 3 | Diff for a different class (OOB write) | same 8 steps, compare structure to cycle 1 | 30 → 55 |
| 4 | `.mojom` + patch | authorisation-gap analysis | 25 → 55 |
| 5 | V8 trace for one JIT bug | locate the removed check in the graph | 25 → 50 |
| 6 | Release notes + CVE list | severity grading, payout calibration | report step 0 → 60 |
| 7+ | Repeat classes 1-19, one per cycle | same-class comparison: did I improve? | see tracker |

**How to rotate so I improve rather than repeat:** every second cycle must be the
*same class* as a previous one but a *different CVE*. Improvement is measured by
comparing the two cycles on the same rubric — fewer questions asked, faster
identification of the vulnerable invariant, more accurate severity. Repeating the
same CVE twice measures memory, not skill.

**Per-cycle output:** the 8 steps, a score change with the reason, and one new
detection rule for the fuzzer/audit tooling.

**Stop condition:** all 19 at 85+. That is unreachable without items 1-3 and 10.
I would rather tell you that now than report 85 after pasting three diffs.

## 4. What I will not do

- I will not write a CVE number I cannot verify, even if the feed is silent.
- I will not score a class above what the evidence supports to make the tracker
  look finished.
- I will not test against a live site, a live Chrome, or Sean's browser.
- I will not submit to Bug Hunters until Sean says GO LIVE.
