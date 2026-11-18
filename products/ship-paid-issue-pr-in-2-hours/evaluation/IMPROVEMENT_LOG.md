# Improvement log

Newest last. Every entry follows the same shape: **what changed**, **why it is
better**, **proof**. Measurements are real; where a timing varies between runs,
the run that produced the quoted number is named.

---

## 2026-11-18 — v0.1 → v0.1.1: `timebox start` did not start

**What changed.** `cmd_timebox` created a `Timebox`, saved it, and returned.
`started_at` stayed `null`; the next `checkpoint` failed with "start the timebox
before checkpointing". One line added: `box.start()` before `box.save()`.

**Why it is better.** The first command in the documented workflow was broken.
The test caught it before any doc was written around it.

**Proof.** Before: `FAIL: test_timebox_flow ... AssertionError: 1 != 0`
(72 tests, 1 failure). After: `Ran 72 tests ... OK`. The failing test remains in
the suite as `test_timebox_flow`.

---

## 2026-11-18 — v0.1.1 → v0.1.2: the effort gate contradicted the product name

**What changed.** `Policy.max_effort_hours` default 16 → 3. Examples, templates,
and rules updated. A 10-hour refactor was previously a `GO`.

**Why it is better.** The product sells "in 2 hours". A 10-hour task cannot
honestly be sold as that, even if the hourly rate is acceptable. The gate now
matches the promise instead of quietly widening it. The example run exposed the
contradiction: `ex-105` scored `GO, 24.0, 30.0/hour, 10h`.

**Proof.** Before: `GO,24.0,30.0,300.0,300.0,10.0,example/parser,ex-105,...`
After: `NO-GO,...,effort above 3 hour cap`. Test suite `Ran 73 tests ... OK`.
One line in `ledger.py`, plus fixture and doc updates.

---

## 2026-11-18 — v0.1.2 → v0.1.3: the summary reported a rejected row as "best"

**What changed.** `summarize()` used every row for `best_effective_hourly_usd`.
With zero GO rows it reported 133.33, taken from a stale repository that had just
been rejected. Renamed and narrowed to `best_go_hourly_usd`, computed from GO
rows only.

**Why it is better.** A summary that recommends a rejected candidate is worse
than no summary. The field name now states its scope.

**Proof.** Before: `"go": 0, "best_effective_hourly_usd": 133.33`. After:
`"go": 1, "best_go_hourly_usd": 250.0`. New assertion in
`test_summary_counts`; `Ran 73 tests ... OK`.

---

## 2026-11-18 — v0.1.3 → v0.1.4: section detection had a false positive

**What changed.** `validate_pr_body` checked `section in text`. A body that
mentioned `## Proof` inside prose or a code fence passed even with no Proof
section. Replaced with a set of stripped lines and exact heading membership.

**Why it is better.** The validator's job is to reject a PR that cannot be
reviewed. A substring check lets the most important section disappear while the
body still validates.

**Variants measured** on a 1.5 KB body, 20,000 calls each:

| Variant | Method | Time per call | Correct on the false-positive case |
|---|---|---|---|
| v1 | `section in text` | 1.11 µs | no |
| **v2** | **set of stripped lines** | **4.10 µs** | **yes** |
| v3 | anchored regex, MULTILINE | 27.01 µs | yes |

v2 is 3.7x slower than v1 in absolute terms, but 4 µs per validation is
irrelevant next to a test run measured in milliseconds. v3 is 6.6x slower than
v2 for the same result. v2 wins on correctness, then speed, then lines.

**Proof.** New test `test_section_name_inside_prose_does_not_count` fails on v1
and passes on v2. `Ran 74 tests ... OK`; flake8 clean. `pack.py` +1 line.

---

## 2026-11-18 — v0.1.4 → v1.0.0: release gate added

**What changed.** Added `evaluation/verify_release.py`: required files, 10
PROPOSED capabilities, 74 tests, flake8, banned marketing phrases, secret scan,
version/changelog match, fee arithmetic, stale test-count scan.

**Why it is better.** The checklist is now executable. A future edit that drops a
file, ships a token, or adds "guaranteed" to the sales page fails a command
instead of relying on a human to notice.

**Proof.** First run failed only on the three evaluation files that did not exist
yet (35/38). Full passing output is in `TEST_RESULTS.md` section 5.

---

## 2026-11-18 — final consistency pass (pre-verification)

**What changed.** Fixed six factual mismatches found by reading the buyer
surface against the files: template count (6, not 7), gate count (9, not 7),
"73 unittest cases" in the buyer README, the Field Kit shipping the Operator
README, the payback figure that assumed a 1-2 hour build, and the stale-count
gate that only matched "73 tests" and not "73 unittest".

**Why it is better.** A $9 buyer now gets a README whose file list and commands
match the files in the zip. The release gate catches the stale-count variant
that slipped through. The payback claim is a formula, not an unsupported number.

**Proof.** `verify_release.py`: 9 checks, 0 failed; secret scan 52 files, 0
findings. Field package dry-run in `/tmp`: README plus six templates, every
referenced path exists. Stale regex returns true for "73 tests", "73 unittest
cases", "73 unit-test" and false for "173 tests". Suite still `Ran 74 tests`,
`OK`.

---

## 2026-11-18 — independent verification round 1 repairs

**What changed.** Round 1 returned FAIL on claim integrity. Repaired: E-13
marketplace net ($5.80 -> $6.30); fee ranges now state 30% marketplace; removed
the unsupported "rest were noise, stale, or unpaid" sentence; replaced
"committed log" wording with "included"; added `README_FIELD.md` to the release
gate (39 files); corrected the support break-even to 41.5 minutes; clarified
manifest source paths; documented that link existence and general bracket text
are not checked; added two validator tests.

**Why it is better.** The evidence log no longer contains a false number, the
copy no longer claims more than the sample supports, and the gate now fails if
the Field Kit start page disappears.

**Proof.** `Ran 76 tests`, `OK`; flake8 clean; release gate 9 checks, 0 failed;
secret scan 54 files, 0 findings. The two new tests are
`test_non_url_issue_is_rejected` and `test_leftover_bracket_placeholder_is_caught`.

---

## Remaining known issues

1. **The effort estimate is the operator's.** The tool cannot detect optimism.
   The 3-hour gate is only as good as the number typed into it.
2. **Escrow is never verified.** `escrow_verified` is a human claim. A buyer can
   set it to true and raise the score; the tool cannot stop that.
3. **The validator is conservative.** A benign "guarantee" in a quoted policy
   will be blocked. Reword; do not weaken the check.
4. **No CSV input for the ledger.** Candidates must be JSON. A CSV reader is a
   candidate for 1.1, not a Phase 1 requirement.
5. **Examples are snapshots.** The timing inside `examples/PR_BODY.md` is from one
   run. The test count is the check; the time is not.
6. **No independent verification.** Builder-run tests only. Stage 7 is pending.
7. **Windows and macOS untested.** Path handling is `os.path`, but that is not
   evidence; it is an untested assumption.
8. **The licence has two intentional blanks.** Governing law and support email.
   Both are release blockers, listed in `DELIVERY_REQUIREMENTS.md` section 10.
