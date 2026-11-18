# Quality checklist

Status at 2026-11-18: automated checks **PASS**; release blockers **OPEN**.
A checked box needs evidence, not confidence.

Legend: `[x]` verified, `[ ]` not verified, **PENDING** means not done.

## A. Scope and governance

- [x] Only Template 1 (Digital Downloads) built — no files for Templates 2-6
- [x] Product stays on branch `phase1/digital-downloads-paid-issue-pr`
- [x] No merge to `main`
- [x] No store listing, publish, price change, or transaction
- [x] No financial, legal, or tax advice in the product
- [x] No secrets or buyer data in the product tree — `verify_release.py` secret scan, 55 files, 0 findings

## B. Content

- [x] All eight required product files, plus `CAPABILITY_LEDGER.md`, exist
- [x] `research/SOURCES.md` lists every source with a URL and retrieval date; S15 is a local file
- [x] `research/EVIDENCE_LOG.md` has 18 entries, including 2 refutations (E-16, E-17)
- [x] Every market number in `SALES_COPY.md` traces to the evidence log or the measurement JSON; prices and policy terms are product decisions
- [x] "Not a financial advice" style disclaimers are not needed here; the product is not a trading tool, and it makes no financial claims
- [x] The 2-hour claim is defined as a timebox, with its limits stated in the README, sales copy, spec, and FAQ
- [x] The product says a stated bounty is not escrow, in four places

## C. Code

- [x] Standard library only — no third-party import in `paid_issue_kit/`
- [x] No network call in `paid_issue_kit/`
- [x] `flake8` clean at max line length 100
- [x] CLI has explicit exit codes 0 (ok), 1 (blocked/invalid state), 2 (bad input)
- [x] No `eval`, `exec`, `pickle`, or shell interpolation in the kit
- [x] File writes are explicit paths chosen by the user; no writes outside the target
- [x] Version is `1.0.0` in the package and the changelog

## D. Tests

- [x] 76 tests pass — `Ran 76 tests in 0.095s`, `OK`
- [x] Per-module counts: ledger 24, pack 26, timebox 16, cli 10
- [x] Negative controls exist for every hard gate claimed (see `TEST_RESULTS.md` section 2)
- [x] Timebox tested at 114 minutes (holds) and 150 minutes (broken)
- [x] State save/load round-trip tested
- [x] CLI end-to-end tested, including blocked and bad-input paths
- [x] Test log included at `evaluation/logs/tests-verbose.log`
- [ ] Windows and macOS executed — **PENDING**, untested
- [ ] Python 3.10/3.11/3.12 executed — **PENDING**, only 3.13.5 ran

## E. Claims and evidence

- [x] Every remote source in `SOURCES.md` was fetched, not remembered; S15 is a local file
- [x] Two claims were refuted and removed from copy: Algora bounty marketplace, IssueHunt OSS issue bounties
- [x] Marketing claim scan: 4 buyer-facing files, 0 banned phrases
- [x] No testimonial, revenue figure, or buyer count is claimed
- [x] No "Active" status for any of the ten components
- [x] Vendor claims are labeled as vendor claims (Gumroad tax/fees)
- [x] The PR validator rejects unverifiable claims by test

## F. Capability ledger

- [x] All ten components are PROPOSED
- [x] Zero components are PROVEN or ACTIVE
- [x] Each component has a written proof bar and a named next step
- [x] The product imports none of them (runtime dependency column: none)

## G. Packaging

- [x] Per-tier file manifest exists in `DELIVERY_REQUIREMENTS.md`
- [x] Internal-only directories are listed as exclusions
- [x] Package names include the version
- [ ] Actual zip built and inspected — **PENDING**, nothing is for sale
- [ ] SHA256 checksums generated — **PENDING**
- [ ] Zip contents diffed against the manifest — **PENDING**

## H. Delivery and commercial

- [x] Price tiers and contents are consistent across `PRICING.md`, `SALES_COPY.md`, `DELIVERY_REQUIREMENTS.md`
- [x] Fee arithmetic checked: $9 → net $7.60, $19 → net $16.60, $39 → net $34.60
- [x] Cost < 3x price at every tier
- [x] Refund policy stated (14 days, no questions)
- [x] Update window stated (1 year)
- [x] Support scope stated (Team only, 30 days, two business days)
- [ ] Support email created and tested — **PENDING**
- [ ] Seller legal name and address set — **PENDING**
- [ ] Governing law and venue set — **PENDING**
- [ ] Licence reviewed by a lawyer — **PENDING**
- [ ] Live checkout and refund path tested — **PENDING**

## I. Verification and authorization

- [x] Builder-run automated verification complete
- [x] Independent verification by a separate agent — **PASS WITH CAVEATS**
- [x] Verification report signed with the verifier's identity — `evaluation/INDEPENDENT_VERIFICATION.md`
- [ ] Explicit written authorization from Sean to publish — **PENDING**

## J. Deliberately not done

- [x] Templates 2-6 not started
- [x] No live bounty claimed, commented on, or submitted
- [x] No PR opened by the product
- [x] No subscription or upsell built
- [x] No ad spend
- [x] No email list

## Release gate

```bash
python3 evaluation/verify_release.py
```

Result: **see `evaluation/TEST_RESULTS.md` section 5** for the captured output.
The gate must exit 0 before a human is asked to authorize publication.

## Sign-off

| Role | Name | Result | Date |
|---|---|---|---|
| Technical Development (builder) | Barrot | automated checks pass | 2026-11-18 |
| QA | Barrot | 76 tests, negative controls pass | 2026-11-18 |
| Independent Verification | OpenCode subagent | **PASS WITH CAVEATS** | 2026-11-18 |
| Human authorization | Sean | **PENDING** | — |

One signature is missing. The product is not ready to publish until Sean signs,
regardless of how many boxes above are checked.
