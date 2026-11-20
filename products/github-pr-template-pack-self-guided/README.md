# GitHub PR Template Pack — Self-Guided

**Status: STAGED. Not published. Not for sale. Demand not proven.**
Branch `phase1/digital-downloads-paid-issue-pr`. Independently verified
**PASS WITH CAVEATS**; awaiting human authorization.

A decision layer for paid open source work: which issues are worth attempting,
what done means, how to prove it, and how to stop at 120 minutes.

## The problem in one measurement

Of 100 open GitHub issues carrying the `bounty` label on 2026-11-18, only 6
stated a dollar amount. A label is not an offer. A stated amount is not escrow.
Most of the time is lost before the first line of code.

## What is inside

| Layer | Artifact | What it removes |
|---|---|---|
| Decide | `deliverables/templates/issue_intake.md`, `decision_rules.md` | Guessing whether an issue is real, scoped, and worth the hour |
| Score | `paid_issue_kit score` | A ranked CSV ledger with every rejection reason |
| Timebox | `paid_issue_kit timebox` | Six ordered phases, 120 minutes, an honest verdict |
| Prove | `paid_issue_kit pr` | A PR body and evidence pack that reject placeholders and unverifiable claims |

Six templates, four Python modules (ledger, pack, timebox, CLI), 76 tests,
and three generated examples. Standard library only. No account, no API key, no network call.

## Quickstart

```bash
cd deliverables
./run_selftest.sh
python3 -m paid_issue_kit score --input examples/candidates.json
python3 -m paid_issue_kit timebox start --state /tmp/run.json --mission "issue 42"
python3 -m paid_issue_kit pr --plan examples/pr_plan.json --out-dir /tmp/pr
```

## What the two hours mean

| Phase | Minutes |
|---|---|
| Triage | 15 |
| Reproduce | 20 |
| Patch | 40 |
| Test | 25 |
| Package | 15 |
| Submit | 5 |

The timer measures the six phases. It excludes maintainer review, CI you do not
control, and payment. The tool reports `CLAIM HOLDS` only when all six finish
inside 120 minutes, and `CLAIM BROKEN` when they do not.

## Evidence

- **76 tests pass**, standard library only:
  `python3 -m unittest discover -s tests` → `Ran 76 tests` → `OK`.
- **112 merged PRs sampled** across three public repositories: pooled median
  open-to-merge 1.11 hours; 52.7% within two hours. This is review latency, not
  contributor effort.
- **100 bounty-labelled issues sampled**: 6 stated an amount, median $525, range
  $450-$600.
- Two platform claims were **refuted** during research and removed from the
  copy: Algora no longer presents a bounty marketplace (its `/bounties` route is
  404), and IssueHunt now sells security bug bounties.

Full method and limits: `research/MARKET_RESEARCH.md`,
`research/EVIDENCE_LOG.md`, `research/measure_market.py`.

## What this does not do

- No list of live bounties.
- No escrow verification.
- No URL existence check. Link shape is validated offline; a well-formed but
  nonexistent issue URL is not detected.
- No promise that a maintainer merges a PR.
- No promise that a bounty pays.
- No income estimate.
- No financial, legal, or tax advice.

## Price (proposal, not live)

$9 Field Kit · $19 Operator Kit · $39 Team Kit. See `PRICING.md`. Nothing is
charged and no store listing exists.

## File map

```
README.md                    this page
PRODUCT_SPECIFICATION.md     scope, requirements, acceptance criteria
SALES_COPY.md                approved sales page copy
PRICING.md                   tiers, fees, kill-rule check
PRODUCTION_WORKFLOW.md       ten stages, eight roles, fail-closed rules
QUALITY_CHECKLIST.md         release gates with evidence
DELIVERY_REQUIREMENTS.md     exact package per tier
LICENSE_AND_TERMS.md         licence by tier (draft, not legal advice)
CAPABILITY_LEDGER.md         ten components, all PROPOSED
research/                    sources, market data, evidence log, measurement
deliverables/                the product itself (templates, kit, tests, examples)
marketing/                   descriptions, promotions, FAQ
evaluation/                  test results, improvement log, verifier
```

## Phase 1 status

Only Template 1 (Digital Downloads) is built. Templates 2-6 are locked and were
not started. The ten named components (PydanticAI, LiteLLM, Phoenix, Promptfoo,
Guardrails AI, Mem0/Qdrant, OpenPipe, Argilla, KitOps, Composio) are all
PROPOSED, none Active; see `CAPABILITY_LEDGER.md`.

No merge to `main`, no publish, no price change, no transaction. Independent
verification is complete: **PASS WITH CAVEATS**
(`evaluation/INDEPENDENT_VERIFICATION.md`). Its one blocking caveat, a stale
gate log, was regenerated after the report. The next action is human
authorization.
