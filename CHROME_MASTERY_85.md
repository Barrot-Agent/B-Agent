# CHROME MASTERY 85 — decomposed so it is either provable or zero

Sean's correction accepted: one score called "Chrome mastery" was hiding seven
different abilities with seven different blockers. A single number lets a strong
fuzzer hide an empty Blink column. This file is now the scoring authority; the
19-class tracker in `REVERSE_ENGINEERED_BUGS.md` stays as the per-bug-type
detail underneath it.

## 1. The rule

**85 means:** the average of the seven sub-skills is >= 85 **and** at least three
full reverse-engineered CVEs exist in `REVERSE_ENGINEERED_BUGS.md`, each with
all three of:

- a **PoC** that is runnable or reproducible here
- a **patch diff** showing the removed or added check
- a **variant** of the same defect that the fix also has to survive

If either condition fails, the score stays below 85. That is arithmetic, not a
block.

**A recommendation, not a change to the gate:** an average of 85 can hide one
sub-skill at 40. I would add a floor of 60 on every sub-skill, because a report
written by someone who cannot read a stack trace is not a VRP report. I am
flagging it rather than imposing it, because moving the definition of done after
Sean set it is exactly the behaviour this track is supposed to stop.

**One proof file per score. No proof, score 0.** Below, every number cites the
file that earns it, and where the number is derived from the 19-class tracker
the arithmetic is shown.

## 2. Current scores — seven sub-skills

| # | Sub-skill | Score | Proof file | What that proof actually shows |
|---|---|---|---|---|
| 1 | Static analysis / patch diffing | **20** | `sandbox/chrome/cves/*.json`, `NETWORK_LOG.md`, `sandbox/chrome/exercises/uaf/uaf.c` | Can fetch two revisions and diff them locally; can name a missing invariant in C++. Has never diffed a real security fix — the one attempt produced 0 changed lines |
| 2 | Dynamic analysis / debugger + ASAN triage | **15** | `sandbox/chrome/fuzz/crashes/`, `tests/test_chrome_fuzz.py` | Triage of 2 real crashes by signal and stderr, on a target I wrote. No debugger, no ASAN, no symbolised stack |
| 3 | V8 / JIT RE (TurboFan, Maglev, WASM) | **15** | `sandbox/chrome/exercises/v8_type_confusion/`, `tests/test_chrome_exercises.py` | Python model of feedback-driven type confusion. Today: real `v8/src/compiler/typer.cc` and `operation-typer.cc` fetched and read. No `d8`, no `--trace-turbo`, no engine executed |
| 4 | Blink / DOM RE | **0** | none | No Blink artifact exists. Source is now reachable (proved today), which removes the access excuse but not the zero |
| 5 | Mojo IPC + sandbox RE | **15** | `sandbox/chrome/exercises/mojo_confused_deputy/` | Ownership/authorisation model and the fix, in Python. Real `.mojom` fetched today (71 KB) but not yet analysed |
| 6 | Fuzzer building / crash triage | **38** | `sandbox/chrome/fuzz/mutational_fuzzer.py`, `tests/test_chrome_fuzz.py` | Full measured cycle: 2 unique crashes in 2000 runs, repair survives both plus 2000 fresh runs. Synthetic target only, no ASAN, no libFuzzer |
| 7 | Report writing (VRP quality) | **10** | `sandbox/chrome/cves/*.json`, `tests/test_chrome_cves.py` | Three CVE citations now verified and hashed, so a report can cite something real. Has never written a report end to end, and has no accepted-report calibration |

**Sum 113 / 700. Average 16.1 / 100. Sub-skills at 85 or above: 0 of 7.**

How each number is derived, so it can be checked rather than trusted:

| Sub-skill | Derivation |
|---|---|
| 1 Static | cross-cutting; no class covers it. Scored from the artifacts: fetch+diff pipeline works, real diff never obtained |
| 2 Dynamic | class 19 (35) discounted for the missing toolchain, since triage without symbols is half the skill |
| 3 V8/JIT | mean of classes 4, 7, 8, 9, 10 = (30+25+0+0+20)/5 = 15 |
| 4 Blink | classes 14-18 are all 0, so the mean is 0 |
| 5 Mojo | mean of classes 11, 12, 13 = (25+0+20)/3 = 15 |
| 6 Fuzzer | mean of classes 6 and 19 = (40+35)/2 = 37.5, rounded to 38 |
| 7 Report | cross-cutting; scored from verified citations, of which there are three and no reports |

This is why the average **fell** in places. The old 19-class table gave Mojo 25
for one exercise; averaged across the three Mojo/sandbox classes it is 15. The
regrouping is not a score increase for the same work, and where it moves a number
down I have taken the lower number.

## 3. What changed today, and what it is worth

Three capability changes, and only one of them moved a score:

1. **CVE verification is now possible and was done.** Three records fetched from
   the authoritative CVE Program list, hashed, and stored. This is the first time
   a CVE number in this repo is checkable by a third party. It moves report
   writing 0 → 10, because a citation is the input to a report, not a report.
2. **Real engine source is now reachable.** `v8/v8` at `main` and at release
   tags; `chromium/chromium` at `main` including `third_party/blink/...mojom`
   (71 KB) and `third_party/blink/renderer/core/dom/node.cc` (146 KB). This
   removes the access blocker for sub-skills 3, 4 and 5. It does not move the
   scores, because reading a file is not an artifact.
3. **A two-revision patch-diff pipeline exists.** Same file, two tags, diff
   locally. It ran and returned 0 lines for `8.0.426.15` vs `8.0.426.16` on both
   `operation-typer.cc` and `typer.cc`, so those tags do not bracket the fix.
   The pipeline works; the vulnerable/fixed pair is still missing. Static
   analysis 0 → 20 for the tooling, not for a diff.

## 4. The three verified CVEs

Fetched through `network_guard.guarded_get`, unauthenticated, from
`CVEProject/cvelistV5`. Each record stores the source URL, HTTP status, byte
count, and SHA-256 of the payload, so the claim can be re-checked.

| CVE | Class | Fixed in | Record | Payload SHA-256 (first 16) |
|---|---|---|---|---|
| CVE-2020-6418 | Type confusion in V8 | 80.0.3987.122 (from prose; structured field is "unspecified") | `CVE-2020-6418.json` | `2b74b87545f8b558` |
| CVE-2024-2887 | Type confusion in WebAssembly | 123.0.6312.86 | `CVE-2024-2887.json` | `08421da3eeba57a2` |
| CVE-2023-7024 | Heap buffer overflow in WebRTC | 120.0.6099.129 | `CVE-2023-7024.json` | `aa4323d524b413c6` |

**What this proves:** the IDs are real, the affected products and fixed versions
are published facts, and the repo can cite them without inventing anything.
**What it does not prove:** nothing about the bug. No patch diff, no PoC, no
variant. Each record says so in its own `artifacts` block, and
`tests/test_chrome_cves.py` fails if that ever changes without the artifact
actually existing.

One data-quality finding worth keeping: **CVE-2020-6418 has
`fixed_version: "unspecified"`**. The only usable version is in the description
prose. An analysis that trusts the structured field would cite nothing.

## 5. Path to 85, per sub-skill

Target is 595 total points; current 113; gap 482. Each row names one CVE, one
test that would prove the step, and whether the network can get it without Sean.

| Sub-skill | CVE | Test that proves it | What is needed | Self-serve? |
|---|---|---|---|---|
| 1 Static / patch diff | CVE-2020-6418 | `test_patch_diff_names_the_removed_check`: two versions of one file in, the deleted guard identified out | the fix commit SHA, or a tag pair that brackets it | **No.** Gitiles ignores `?q=` (same bytes returned twice), and the two nearest tags diff to 0 lines |
| 2 Dynamic / ASAN | any UAF with a trace | `test_triage_recovers_the_faulting_frame` from a real ASAN log | a working clang/ASAN, or a pasted trace | **No.** clang is broken here, ASAN aborts in the allocator |
| 3 V8 / JIT | CVE-2024-2887 | `test_wasm_type_check_is_the_missing_invariant`: locate the check in real source and show what its absence permits | the fix diff, or `--trace-turbo` / `d8` output | **Partial.** Source yes, execution no |
| 4 Blink / DOM | a Blink CVE, not yet selected | `test_blink_lifetime_rule_is_stated_and_violated` against a real Blink file | one verified Blink CVE ID, or a patch touching `third_party/blink` | **Partial.** Source yes (proved today), CVE selection no |
| 5 Mojo / sandbox | a `.mojom` authorisation fix | `test_mojom_allowed_caller_set_matches_the_check` against the real interface | one patch diff for an IPC authorisation fix | **Partial.** Real `.mojom` yes, the diff no |
| 6 Fuzzer / triage | any fuzzer-found crash | `test_fuzzer_finds_and_reruns_a_real_crash` on a non-synthetic target | libFuzzer or ASAN, and a target bigger than 60 lines | **No.** Toolchain |
| 7 Report writing | CVE-2024-2887 first | `test_report_has_all_eight_steps_and_no_fabricated_citation` | one accepted report, redacted, for severity calibration | **No.** Social artefact, cannot be fetched |

The shape of the blocker is now clear and it is not the allowlist:

- **Source: solved.** V8, Blink, Mojo IDL are all reachable.
- **Diffs: blocked by lookup, not by policy.** I can fetch any file at any ref;
  I cannot find *which* ref without a search endpoint or a SHA.
- **Execution: blocked by toolchain.** No working clang, no ASAN, no `d8`, no
  debugger, 3 GB RAM, 5.3 GB free.

That is why item 1 on the feed request is still a pasted diff: it is 30 seconds
for Sean and it unblocks the single largest sub-skill gap.

## 6. RE loop started — CVE-2024-2887

Chosen because it is the easiest of the three verified records and it lands on a
sub-skill where a model already exists: WASM type confusion is the same defect
shape as the JIT model in `v8_type_confusion/`, so the mechanism transfers.

The eight steps, with an honest status on each:

| Step | Status |
|---|---|
| 1. Verified record | **DONE** — `sandbox/chrome/cves/CVE-2024-2887.json`, hashed |
| 2. Locate the vulnerable component | **PARTIAL** — component is WebAssembly in V8; the specific function is not identified, because that requires the fix diff |
| 3. State the broken invariant | **DONE** — a value's static type and its runtime representation must agree across a call boundary; the JIT trusts the static type after the boundary |
| 4. Patch diff | **UNRESOLVED** — no SHA, no diff |
| 5. PoC | **UNRESOLVED** — needs the diff or a public PoC, and I will not write one against a live browser |
| 6. Variant | **UNRESOLVED** — depends on step 4 |
| 7. Detection rule | **PARTIAL** — the model already flags "type asserted before a call, used after"; generalising it to real WASM needs step 2 |
| 8. Report | **UNRESOLVED** — no PoC, no diff, so any report would be a summary of the advisory |

Score change for this loop: none yet. Steps 1 and 3 are worth nothing on their
own, and a loop that awarded points for reading an advisory would be the exact
inflation this file exists to prevent.

**Why not the weakest sub-skill:** Blink is at 0 and is the weakest. Starting
there would be the right move, but I have no verified Blink CVE, and selecting
one by guessing an ID is how a fake citation gets born. Blink stays at 0 until a
Blink CVE is fed or a Blink patch is pasted. The trade-off is stated rather than
hidden.

## 7. The four engine defects, and the XLM proof

All four were introduced and fixed in commit `35862c8a1`; the before/after below
is from that commit's diff, not from memory.

**Defect 1 — every candidate sized against the whole stack.**
Before: `max_by_risk = stack_xrp * (MAX_RISK_PCT / 100) / ...` and
`xrp_allocated = min(stack_xrp, max_by_risk)`. Five approved candidates could
each risk 1% of the full stack, so the portfolio risk was the sum, not the
per-trade figure.
After: `capacity = min(stack_xrp, available_xrp)`, sizing uses `capacity`, and
the cycle engine decrements `available` after each acceptance. Two more guards:
a non-finite or negative `available_xrp` is rejected, and a zero allocation is
rejected instead of being recorded as a trade.
Proof: `tests/test_xrp_batch.py::test_risk_is_a_share_of_available_capital_not_the_raw_stack`,
plus `test_zero_available_capital_is_refused`.

**Defect 2 — unknown news blocked only the offensive leg.**
Before: `if plan.news == "UNKNOWN"` sat inside the `else:` branch, so an
incomplete news scan blocked offensive rotations and let the defensive USDT leg
through. That inverts the intent: the defensive trigger is itself derived from
the news scan, so it cannot be trusted when the scan did not complete.
After: the check is hoisted above the branch and blocks both legs.
Proof: `tests/test_xrp_batch.py::test_unknown_news_blocks_even_the_defensive_leg`.

**Defect 3 — holding XRP was recorded as a rejection.**
Before: there was no `NO_TRADE` decision; a hold went through `evaluate`, failed
the "XRP is the base asset" check, and was counted as `REJECTED`. That polluted
the rejection statistics that the rotating loop now grades.
After: a hold is `NO_TRADE`, excluded from `rejected`, and counted separately.
Proof: `tests/test_xrp_batch.py::test_hold_is_no_trade_not_a_rejection`.

**Defect 4 — a simulated lesson could disable an asset on recorded data.**
Before: `load_config` applied every lesson in the file, whatever provenance it
was learned under. A lesson learned from a fixture could therefore disable an
asset in the real snapshot.
After: `if record.get("provenance") != provenance: continue`.

Why it mattered, measured end to end on Sean's snapshot rather than asserted:

```
XLM ratio signal on Sean's snapshot: FAVOURS | trend: MIXED
without provenance scoping : disabled = ('XLM',) | approved = False | asset XLM disabled by the learning loop
with provenance scoping    : disabled = ()       | lessons applied = 0 | approved = False
outcome: XLM preserved
```

XLM was the only candidate whose ratio signal was FAVOURS on that snapshot. The
bug would not have made a bad trade — it would have removed the one favourable
candidate from consideration before its own signals were read, silently. It is
still not approved (trend `MIXED`), so the honest claim is "preserved and
evaluated", not "would have traded".

Proof: `tests/test_xrp_batch.py::test_simulated_lesson_cannot_disable_an_asset_on_real_data`,
with `test_same_provenance_lesson_does_apply` as the positive control, so the
test cannot pass by disabling the feature entirely.

## 8. Status

- Sub-skills scored: 7 of 7, each with a proof file. Average **16.1 / 100**.
- Full REs to Sean's standard (PoC + diff + variant): **0 of 3**.
- Verified CVE citations: **3** (was 0).
- Network: 3 CVE records pulled and hashed; 6 source probes; all logged.
- Chrome mastery at 85: **not reached, and not close.** The difference from the
  previous report is that the gap is now itemised instead of summarised.
