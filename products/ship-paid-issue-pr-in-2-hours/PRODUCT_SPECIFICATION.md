# Product specification

**Name:** Ship a Paid-Issue PR in 2 Hours — GitHub Template Pack
**Slug:** `ship-paid-issue-pr-in-2-hours`
**Template:** 1 — Digital Downloads
**Status:** STAGED on a branch. Not published. Demand not proven.
**Version:** 1.0.0 (2026-11-18)
**Price tiers:** $9 / $19 / $39 (proposal, not a live price)

## 1. Problem

A developer sees a GitHub issue with a bounty and cannot answer four questions
quickly:

1. Is this actually paid, or is "bounty" just a word in the template?
2. What does "done" mean for this maintainer?
3. Can I finish it in one session, or am I starting a second job?
4. What do I send so the maintainer can review it without asking me three
   questions?

The measured sample supports the first question: of 100 open issues carrying the
`bounty` label, only 6 stated a dollar amount in the parsed text. That does not
prove the other 94 were unpaid; it proves the label alone is not enough. The pack
exists to make those four questions cheap to answer and to stop the work at a
fixed time.

## 2. Buyer

**Primary.** A developer who has shipped code but has not been paid for an open
source contribution. They can read a stack trace, run tests, and open a PR. They
do not have a repeatable way to pick an issue or prove the work.

**Secondary.** A developer who already does paid issues occasionally and loses
hours to scope creep and review rework.

**Not the buyer.** Someone looking for guaranteed income, a list of live
bounties, a bot that opens PRs for them, or financial advice. The pack is not
that and says so in the sales copy.

## 3. Promise and boundaries

**What the product promises.** A 120-minute timebox split into six phases, with
a decision ledger, a PR body builder, an evidence-pack validator, and templates
that make each phase concrete.

**What it does not promise.**

- That a maintainer merges the PR.
- That a stated bounty is paid. A stated bounty is not escrow.
- That the buyer earns any amount of money.
- That two hours is enough for every issue. The default effort gate rejects
  estimates over three hours.

Evidence for the timebox's plausibility: in 112 merged PRs sampled across three
public repositories, the pooled median open-to-merge time was 1.11 hours and
52.7% merged within two hours. That measures review latency, not contributor
effort, and it does not predict any single PR. Source:
`research/market_measurement.json`.

## 4. Artifact inventory

| Artifact | What it does | Tier |
|---|---|---|
| `README.md` | Internal product status page; not shipped | internal |
| `deliverables/README_FIELD.md` | Field Kit start page, packaged as `README.md` | $9 |
| `deliverables/README.md` | Operator/Team start page, packaged as `README.md` | $19 |
| `PRODUCT_SPECIFICATION.md` | This file; scope and acceptance criteria | internal |
| `SALES_COPY.md` | Approved sales page copy | internal |
| `PRICING.md` | Tier contents and unit economics | internal |
| `PRODUCTION_WORKFLOW.md` | Ten-stage pipeline and eight roles | internal |
| `QUALITY_CHECKLIST.md` | Release gates with evidence | internal |
| `DELIVERY_REQUIREMENTS.md` | Exact package per tier | internal |
| `LICENSE_AND_TERMS.md` | Licence by tier and liability limits | $9 |
| `templates/issue_intake.md` | Hard-gate intake form | $9 |
| `templates/decision_rules.md` | Gates and scoring formula | $9 |
| `templates/pr_body.md` | Fill-in PR body | $9 |
| `templates/evidence_pack.md` | Fill-in evidence pack | $9 |
| `templates/bounty_ledger.csv` | Ledger header for a spreadsheet | $9 |
| `templates/timebox_card.md` | Printable 120-minute card | $9 |
| `paid_issue_kit/` | Scoring, packaging, timebox, CLI | $19 |
| `tests/` | 76 tests for the kit | $19 |
| `examples/` | Synthetic inputs and generated outputs | $19 |
| `run_selftest.sh` | One-command test run | $19 |
| `marketing/` | Descriptions, promotions, FAQ | internal |
| `evaluation/` | Test log and improvement log | internal |
| `research/` | Sources, market research, evidence log, measurement | internal |

Internal files are kept out of the buyer package. The exact per-tier manifests
are in `DELIVERY_REQUIREMENTS.md`.

## 5. Functional requirements

| ID | Requirement | Acceptance | Evidence |
|---|---|---|---|
| FR-1 | The ledger rejects a candidate with no stated amount | `NO-GO` with reason | `test_missing_amount_is_no_go` |
| FR-2 | The ledger rejects archived, stale, low-star, and spam issues | each gate produces its reason | `test_archived_repository`, `test_stale_repository`, `test_low_stars`, `test_spam_title` |
| FR-3 | The ledger rejects effort over 3 hours and rate under $30/hour | reason added | `test_effort_above_cap`, `test_low_effective_rate_blocks` |
| FR-4 | The ledger computes effective payout after fees and expenses | exact arithmetic | `test_fee_and_expenses_reduce_payout` |
| FR-5 | The ledger sorts GO rows first, then by score | stable order | `test_go_rows_sort_first` |
| FR-6 | The timebox has six ordered phases totalling 120 minutes | order violation raises | `test_total_is_120`, `test_out_of_order_checkpoint_rejected` |
| FR-7 | The timebox reports `CLAIM HOLDS` only when all phases finish inside 120 minutes | verdict tested at 114 min and 150 min | `test_claim_holds_inside_budget`, `test_claim_broken_over_budget` |
| FR-8 | The timebox persists and reloads state | round-trip equal | `test_save_and_load_roundtrip` |
| FR-9 | The PR builder emits the five required sections | validator returns no problems | `test_builds_and_validates` |
| FR-10 | The validator rejects placeholders, banned claims, missing link, missing test command, missing result, missing rollback, and weak checklists | one test per failure | `test_pack.py` |
| FR-11 | The evidence pack requires claim + evidence + limit and exit code 0 | per-claim rejection | `test_pack.py` |
| FR-12 | The CLI implements `score`, `pr`, `timebox`, `phases` with exit codes 0/1/2 | end-to-end tests | `test_cli.py` |
| FR-13 | The kit runs offline on the standard library | no third-party import | `grep` + test run |
| FR-14 | Examples are generated by the code, not typed by hand | regeneration commands | `examples/README.md` |

## 6. Non-functional requirements

- **Portability:** Python 3.10+, UTF-8 files, LF newlines in code.
- **Offline:** no network call in the package. The research script is separate
  and read-only.
- **Speed:** the full suite completes in under a second on the build machine.
  The CLI starts in well under a second. No performance claim beyond that.
- **Privacy:** the kit stores only what the user types into the ledger. No
  telemetry, no analytics, no outbound call.
- **Determinism:** tests inject a fixed clock and a fixed `now`. Live data is
  never used as a test fixture.
- **Accessibility:** Markdown and CSV; no proprietary viewer required.

## 7. Data model

**Candidate** (ledger input): `issue_id`, `url`, `repo`, `title`, `amount_usd`,
`acceptance_criteria`, `repo_stars`, `repo_pushed_at`, `archived`,
`escrow_verified`, `platform`, `labels`, `comments`, `effort_hours`,
`payout_fee_fraction`, `expenses_usd`.

**Policy** (thresholds): `min_amount_usd=50`, `max_amount_usd=50000`,
`min_stars=20`, `max_idle_days=120`, `min_effective_hourly_usd=30`,
`max_effort_hours=3`, `min_criteria_chars=20`.

**PR plan**: `issue_url`, `summary`, `change_bullets`, `why`, `test_command`,
`test_result`, `risk`, `rollback`, `checklist`, optional `note`.

**Evidence plan**: the PR plan plus `issue_id`, `claims[]` (`text`, `evidence`,
`limit`), `command`, `exit_code`, `output`, optional `commit`, `environment`.

## 8. Failure modes

| Failure | Detection | Handling |
|---|---|---|
| A candidate's amount was guessed, not stated | `amount_usd` null is rejected | Leave it null; do not estimate |
| Escrow is assumed | `escrow_verified` false lowers confidence to 0.7-0.9 | Sales copy and intake both say a bounty is not escrow |
| Effort estimate is optimistic | 3-hour hard gate | Re-estimate after triage; if over, NO-GO |
| Operator lies to the timebox | Tool cannot detect it | The log is auditable; the claim is the operator's, not the tool's |
| Validator false positive on a benign word | e.g. "guarantee" in a quoted policy | Reword the PR body; the validator is intentionally conservative |
| Validator false negative | unknown phrasing | The evidence pack still forces claim + limit per statement |
| Windows path or encoding issue | not tested | Stated as untested in `evaluation/TEST_RESULTS.md` |
| Buyer expects live bounties | sales copy and FAQ | Explicit "no list of live bounties" |

## 9. Out of scope

- Templates 2-7. Locked. Not built.
- Automatic bounty discovery, claiming, commenting, or PR opening.
- Escrow verification or payment handling.
- A hosted service, account system, or dashboard.
- Financial, legal, or tax advice.
- Any claim of income, guarantee, or "production-ready" outcome.

## 10. Pipeline and role ownership

The ten-stage pipeline is in `PRODUCTION_WORKFLOW.md`. Role ownership in one
line: Market Intelligence and Product Strategy decide; Research gathers;
Technical Development builds; Content/Production writes; QA tests; Business
Operations packages; Independent Verification audits; Sean authorizes.

## 11. Capability status

The ten named components are all PROPOSED. See `CAPABILITY_LEDGER.md`. The
product does not import any of them.

## 12. Kill criteria

| Rule | Result | Basis |
|---|---|---|
| No evidence of demand | PARTIAL — proceed only as a test | Live inventory exists; demand for this pack is unmeasured |
| Cost > 3x price | PASS | Fees are 11.3%-15.6% direct (30% marketplace); no paid infrastructure |
| Capability not buildable in one iteration | PASS | Standard library only |
| Governance violation | PASS | Branch only; no publish, merge, price change, or transaction |

## 13. Definition of done (Phase 1)

- [x] Required files exist under this directory
- [x] Deliverables are functional, not placeholders
- [x] 76 tests pass with a captured log
- [x] Research is sourced and dated
- [x] All ten components remain PROPOSED
- [x] No merge, publish, price change, or transaction
- [ ] Independent Verification completed by someone other than the builder
- [ ] Human authorization to publish

The last two are deliberately unchecked. They are the gate, not a formality.

## 14. Change control

Version follows `MAJOR.MINOR.PATCH` in `paid_issue_kit/__init__.py`. Every change
to a gate, a claim, or a price gets an entry in
`evaluation/IMPROVEMENT_LOG.md` with the test that proves it. A change that
cannot be tested does not ship.
