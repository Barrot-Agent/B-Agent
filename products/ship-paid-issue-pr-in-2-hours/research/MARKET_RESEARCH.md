# Market research

Status: research complete for Phase 1. Decision: **CONDITIONAL GO** to build a
staged product, confidence **LOW**. The product is not published and this file
does not claim demand that was not measured.

## 1. The question

Is there enough evidence of demand to build and stage a $9 / $19 / $39 digital
download that helps a developer find, scope, ship, and evidence a paid-issue
pull request inside a two-hour timebox?

What would change the verdict:

- If no live paid-issue inventory existed, the product would be killed.
- If a licensable dataset of verified, escrowed bounties existed cheaply, the
  scanning part of the product would be redundant.
- If the only differentiator were the PR template, the product would be killed:
  GitHub ships templates for free and several sites give them away.

## 2. What was measured (primary data)

Source: `research/market_measurement.json`, retrieved 2026-11-18T06:09:03Z.

| Measure | Value | How |
|---|---|---|
| Open GitHub issues labelled `bounty` | 5,319 | Search API `total_count` |
| Issues mentioning `algora` | 559 | Search API `total_count` |
| Issues mentioning "paid" and "pull request" | 7,570 | Search API `total_count`, upper bound |
| Sampled `bounty`-labelled issues | 100 | Two pages of 50 |
| Sampled issues that state a dollar amount | 6 of 100 (6.0%) | Regex for `$N` or `N USD` in title/body |
| Stated amounts in that sample | min $450, median $525, max $600 | Parsed from issue text |
| Sampled issues linking a bounty platform | 9 of 100 | `algora.io` 6, `opire.dev` 9, `issuehunt.io` 0 |
| Median comments on sampled issues | 1 | Search API field |
| Median age of sampled issues | 1.3 days | Created timestamp |
| Merged PRs sampled across three repos | 112 | REST pulls API |
| Pooled median open-to-merge time | 1.11 hours | `merged_at - created_at` |
| Pooled share merged within 2 hours | 52.7% | Same sample |

Platform counts overlap: 9 distinct issues linked at least one platform, with 15
matches in total (6 Algora, 9 Opire, 0 IssueHunt). The 15 is not 15 issues.

Repository detail for merge latency:

| Repository | Merged PRs sampled | Median hours | Share within 2h |
|---|---|---|---|
| pallets/flask | 5 | 0.13 | 60.0% |
| fastapi/fastapi | 74 | 0.57 | 56.8% |
| encode/httpx | 33 | 4.27 | 42.4% |

Interpretation limits: this measures review latency on recently updated merged
PRs, not the time a contributor spends writing one. Small PRs merge fast; large
PRs do not. The 2-hour promise in the title is a timebox the buyer controls, not
a prediction of merge time. The measured data supports "a small, well-scoped PR
can clear review inside one working session", not "your PR will merge in 2h".

## 3. Platform landscape

- **Opire** is live. Its home page describes the model as "Anyone can create
  bounties in open-source projects and attract contributors, while developers
  can earn money by solving issues" (S6). Its rewards board at retrieval listed
  individual bounties at $100.00, $42.00, and $20.00 (S7). The same board
  rendered "Bounties paid 0", "Bounties available 0", "Money paid in bounties
  $0.00" while listing those bounties. That contradiction is an unresolved
  loading or data issue, so the counters are recorded as ambiguous, not as proof
  of zero activity.
- **Algora** no longer presents itself as a bounty marketplace. The home page
  headline at retrieval was "Hire your competitors' best engineers" (S8), and
  `https://algora.io/bounties` returned HTTP 404 (S9). Any copy that calls Algora
  a bounty marketplace today is out of date.
- **IssueHunt** now presents as "#1 Bug Bounty platform in Japan" for security
  reports (S10), not as an open-source issue bounty board.

Consequence: the marketplace layer is thinner and less stable than it looked in
2023-2024. A product that depends on one platform's API would be fragile. This
pack therefore depends on GitHub issue data plus manual verification, not on a
platform partnership.

## 4. Supply side: what the buyer can already get for free

- GitHub's own pull request templates are built in: "When you add a pull request
  template to your repository, project contributors will automatically see the
  template's contents in the pull request body" (S12).
- Gitmore publishes a guide with downloadable templates and says the reader can
  get "free markdown files you can download and drop into your repository today"
  (S13).
- A DuckDuckGo query for a paid PR template pack returned free template
  galleries and official documentation on the first page, not a paid pack (S14).

Consequence: **PR templates are a commodity.** They cannot carry the price. The
paid artifact has to be the decision layer: which issues are worth attempting,
what "done" means, how to prove it, and how to stop at 120 minutes. That is what
this pack actually contains. The templates are included because the workflow
needs them, not because they are scarce.

## 5. Buyer and willingness to pay

Two buyer types:

1. A developer who wants a first or next paid contribution and does not know how
   to separate a real bounty from noise.
2. A developer who already does paid issues occasionally and loses time on
   scope, reproduction, and review rework.

Willingness-to-pay anchor: in the measured sample, stated bounties were $450 to
$600. One accepted bounty pays for the $39 tier more than ten times. That is an
anchor, not a conversion estimate. No sales data exists for this product.

Fee reality (S11): Gumroad charges "10% + $0.50" per transaction for sales
through the seller's profile or direct links, and 30% for sales discovered
through its marketplace. At $9 the fee is $1.40 (15.6%); at $19 it is $2.40
(12.6%); at $39 it is $4.40 (11.3%). Gumroad has been merchant of record for
sales tax since 2025-01-01, per the same page.

## 6. Risks

| Risk | Evidence | Effect | Mitigation in this pack |
|---|---|---|---|
| Bounty is not escrow | 6 of 100 sampled issues even state an amount; none verified | Buyer can do the work and not get paid | Intake template requires escrow evidence; ledger marks `escrow_verified`; sales copy says it plainly |
| Platform churn | Algora route 404; IssueHunt repositioned | A platform-specific workflow ages badly | No platform API dependency; GitHub-first |
| Free substitutes | GitHub native templates; free template packs | Price ceiling on the template portion | Price floor is $9; value is in scoring, timebox, evidence |
| Marketplace noise | 94 of 100 labelled issues had no stated amount | Buyer waste | Hard gates reject missing amount, stale repo, spam markers |
| Claim risk | "2 hours" can read as a guarantee | Refunds, reputational damage | Claim is defined as a 120-minute timebox; measured limits published |
| AI commoditisation | Generic LLMs can draft PR text | Low differentiation over time | Artifact is a tested workflow with logs, not generated prose |

## 7. Kill criteria check

| Kill rule | Verdict | Basis |
|---|---|---|
| No evidence of demand | **PARTIAL** | There is live paid-issue inventory (5,319 labelled issues; Opire live; 559 Algora mentions in older issues). There is **no** measured demand for this exact paid pack. Proceed only as a low-cost staged test. |
| Cost > 3x price | **PASS** | Marginal cost is $0 plus payment fees of 11.3%-15.6% on direct sales (30% via marketplace discovery); production used existing tooling and no paid APIs. |
| Requires a capability that cannot be built in one iteration | **PASS** | The kit is Python standard library plus markdown. No external service is required to deliver it. |
| Violates governance | **PASS** | No publish, no merge, no pricing change, no transaction. Staged on a branch only. |

## 8. Pre-registered test (not yet run)

If a human approves a paid test, the first test is:

- One product page, three tiers, no ads, one distribution post per channel.
- Window: 30 days from publication.
- Falsifier: fewer than 3 paid sales at any tier in 30 days with at least 300
  page views means the demand hypothesis is not supported; stop and do not build
  Templates 2-7 from this evidence.
- Upgrade condition: 3 or more sales and at least one refund-free delivery, with
  a verified buyer-reported time-to-PR inside 120 minutes, upgrades the product
  from PROPOSED to TESTED.
- Limit: the test measures this page and this audience, not the whole market.

These numbers are a decision rule chosen before seeing sales, not a forecast.
