# CI Rescue Checklist - DRAFT

Status: DRAFT. Not published. Not priced in public. Awaiting approval.

## Problem

A solo maintainer breaks CI once a week and spends an hour reading a log to find a
failure they have seen before. The checklist names the 42 failures that account for
most red builds, in the order they should be checked.

## Outline

1. Before the run: lockfile, cache key, matrix drift
2. Environment: python and node version pins, missing env var
3. Permissions: read-only token, missing id-token, fork pull request
4. Tests: flaky order, timezone, network call in a unit test
5. Docs: Liquid-hostile markdown, stale index, broken relative link
6. Release: tag race, changelog path, artifact name collision
7. Three worked examples from this repository

## Pricing (proposal)

| Tier | Price | Contents |
|---|---|---|
| Single | 12 | PDF plus Markdown |
| Bundle | 39 | plus a small shell script that checks four of the 42 |
| Team | 120 | internal sharing, invoice |

## Sales copy

Headline: 42 CI failures, in the order that fixes them.

Body: This is the checklist used to keep a repository with 1,100 tests green. Each
item is a symptom, a cause, and the smallest change that fixes it. It does not include
a script that rewrites your CI for you, because that is where trust breaks.

What the buyer receives: one PDF, one Markdown file, one shell script, one year of
updates. Refund on request within 14 days, no questions.

Call to action: Buy the checklist.

## Evidence

Items are drawn from real repairs in this repository. Each item can be tested by
introducing the fault in a scratch branch. The bundle script is not written yet.

## Approval gate

Do not publish until the owner approves the price and the 42 items are checked against
a fresh repository, not only this one.
