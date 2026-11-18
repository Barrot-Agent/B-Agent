# Barrot Foundry

## What this is

Autonomous Capability Foundry & Product Pipeline.

A repository that researches a market, builds a product from what is actually on
disk, tests it, and stops at a human gate before anything is sold. Every claim in
the product surface is supposed to trace to a file, a command, or a source with a
retrieval date. Where evidence is missing, the artefact says so.

## Status

**Phase 1 — Template 1 Digital Downloads ONLY.**

- Build state: STAGED on branch `phase1/digital-downloads-paid-issue-pr`
- Published: no
- Live price: none
- Transactions: none
- Revenue to date: $0.00
- Templates 2-6: locked, not started

## Current Product

**GitHub PR Template Pack — Self-Guided Checklist & Templates for Clean Pull Requests**

| Tier | Price (proposed) | Contents |
|---|---|---|
| Field Kit | $9 | Intake rules, decision rules, PR body template, evidence template, timebox card, ledger CSV |
| Operator Kit | $19 | Field Kit + Python toolkit (stdlib only) + 76 tests + generated examples |
| Team Kit | $39 | Operator Kit + up to 10 internal seats + invoice + 30 days of email answers |

Location: `products/github-pr-template-pack-self-guided/`

Measured build facts:

- 6 templates (5 Markdown, 1 CSV)
- 4 Python modules, standard library only, no network calls
- 76 tests, all passing (`python -m pytest tests -q` inside `deliverables/`)
- 9/9 release gates, 55 files secret-scanned, 0 findings
- Independent verification: PASS WITH CAVEATS (separate agent, reports in `evaluation/`)

What the numbers do not say: demand is **unmeasured**. The pre-registered kill
test is fewer than 3 sales at 300 or more views over 30 days. Prices are a
proposal and have never been charged.

## Components

All ten are **PROPOSED**. None is PROVEN. None is ACTIVE. None is a runtime
dependency of the product above.

| # | Component | Role in the pipeline | Status | Proof present |
|---|---|---|---|---|
| 1 | PydanticAI | Typed agent outputs and tool schemas | PROPOSED | none |
| 2 | LiteLLM | Model routing and cost control | PROPOSED | none |
| 3 | Phoenix | Tracing and evaluation of runs | PROPOSED | none |
| 4 | Promptfoo | Prompt regression tests | PROPOSED | none |
| 5 | Guardrails AI | Output validation | PROPOSED | none |
| 6 | Mem0 / Qdrant | Long-term memory and retrieval | PROPOSED | none |
| 7 | OpenPipe | Fine-tuning and dataset export | PROPOSED | none |
| 8 | Argilla | Human annotation and review | PROPOSED | none |
| 9 | KitOps | Model and artefact packaging | PROPOSED | none |
| 10 | Composio | External tool actions | PROPOSED | none |

Proof bar for PROVEN: pinned commit, a committed run log showing the component
doing the claimed job, a named owner among the eight roles, and a documented
failure mode. A config stub or a passing import does not count. Ledger:
`products/github-pr-template-pack-self-guided/CAPABILITY_LEDGER.md`.

## 8 Roles

| Role | Owns | Must not do |
|---|---|---|
| Research | Sources, quotes, retrieval dates | Present a vendor claim as measured fact |
| Market Intelligence | Demand, competition, platform status | Inflate a sample into a market size |
| Product Strategy | Scope, tiers, kill criteria, pricing rationale | Add a feature outside the template |
| Content/Production | Buyer-facing docs, templates, sales copy | Add a claim not in the evidence log |
| Technical Development | Kit code, CLI, examples, tests | Mark a component Active without proof |
| QA | Test execution, negative controls, regression log | Accept "it works" without a command and output |
| Business Operations | Packaging, delivery, refunds, invoices | Publish or charge without sign-off |
| Independent Verification | Re-run tests, audit claims, check governance | Fix the thing it is verifying |

Separation rule: the builder cannot sign off verification. Ten stages, fail-closed,
are in `products/github-pr-template-pack-self-guided/PRODUCTION_WORKFLOW.md`.

## How to run

Sandbox, branch, pull request. Never merge without Sean.

```bash
git clone https://github.com/Barrot-Agent/B-Agent.git
cd B-Agent

# Phase 1 work lives on its own branch
git checkout phase1/digital-downloads-paid-issue-pr

# Product tests (76)
cd products/github-pr-template-pack-self-guided/deliverables
python -m pytest tests -q

# Release gate
cd ..
python evaluation/verify_release.py

# Repository suite
cd ../..
python -m pytest -q
```

Rules:

- No commit to `main` from an agent.
- No listing, price, or file published to a store.
- No live price change.
- No transaction.
- Anything that would merge, publish, price, or charge stops and waits for
  Sean's written approval.

## Compliance

- Digital downloads only.
- Self-guided: the buyer runs the checklist and keeps the result.
- DIY: the buyer does the work; this repository sells files, not labour.
- Nothing is priced per job, per hour, or per engagement.
- Secrets live in environment variables or GitHub Secrets. Never in a file, a
  log, or a chat message.
- Stored data is limited to what is readily accessible: specifications, sources,
  templates, logs, HEAD, STATUS.

## Blocked / Needs Sean

Publish is blocked until every item below is supplied or decided by Sean:

1. Written authorization to publish (Stage 10).
2. Support email address for buyer questions.
3. Seller legal name and address for the licence and invoice.
4. Governing law for the terms.
5. Lawyer review of `LICENSE_AND_TERMS.md`.
6. Live checkout and refund test on the chosen platform.
7. Final zip plus checksums.
8. Confirmation of the $9 / $19 / $39 proposal, or a different price.

Nothing above is inferred, defaulted, or filled in by the agent.

## Last Updated

- Date: 2026-11-18
- Branch: `phase1/digital-downloads-paid-issue-pr`
- HEAD at time of writing: `b6d0b5c25` (parent commit)
- STATUS: STAGED — not published, not priced live, no transaction
- Memory: `MEMORY.md` and `BARROT_SYNC.md`
