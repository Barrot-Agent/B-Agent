# Evidence log

Every entry states one claim, the exact text or measurement behind it, what the
evidence does **not** support, and the state. States: `VERIFIED` (source read,
quote present), `MEASURED` (produced by our script, artifact in `research/`),
`REFUTED` (source contradicts the claim), `AMBIGUOUS` (source conflicts with
itself), `UNVERIFIED` (no source found). Retrieval: 2026-11-18 UTC.

---

## E-01 - Paid-issue inventory exists on GitHub

**Claim.** There is a live pool of GitHub issues labelled as paid work.

**Evidence.** GitHub Search API `total_count`:

- `label:bounty is:issue is:open` -> **5,319**
- `algora in:body is:issue is:open` -> **559**
- `"paid" "pull request" in:body is:issue is:open` -> **7,570**

Artifact: `research/market_measurement.json` -> `query_counts`.

**Supports.** A buyer for a paid-issue workflow has inventory to work on.
**Does not support.** Demand for a paid template pack. An issue labelled
`bounty` is not an offer, not escrow, and often not about money at all.
**State.** MEASURED.
**Would be falsified by.** A repeat query returning zero, or manual review
showing the label is entirely unrelated to payment.

---

## E-02 - Most bounty-labelled issues do not state an amount

**Claim.** The label is a weak signal; scanning by label alone produces noise.

**Evidence.** Of 100 sampled open issues carrying the `bounty` label, **6**
contained a parseable dollar amount in title or body (6.0%). 3 contained a
spam-style marker from our deny list. Artifact:
`research/market_measurement.json` -> `bounties.issues_with_stated_amount`.

**Supports.** A hard gate that rejects issues without an amount is useful, and
the product should teach it.
**Does not support.** That 94% are worthless; some may state amounts in images,
comments, or platform pages we did not parse.
**State.** MEASURED, with a known parser limit.
**Would be falsified by.** A larger manually labelled sample showing most issues
state an amount outside the parsed fields.

---

## E-03 - Stated amounts in the sample were $450-$600

**Claim.** A single accepted bounty can cost more than the top product tier.

**Evidence.** Six parsed amounts: min $450, median $525, max $600
(`bounties.amount_usd`). This is a small, self-selected sample.

**Supports.** A $9-$39 price is small relative to one stated bounty.
**Does not support.** Typical bounty size, payout probability, or conversion.
Those six are not a random sample of the 5,319.
**State.** MEASURED, small sample.
**Would be falsified by.** A random sample with a median far below $50, which
would make the value anchor weak.

---

## E-04 - Opire is a live bounty marketplace

**Claim.** At least one platform still runs the "fund an issue, pay for the fix"
model.

**Evidence.** Opire home page: "Anyone can create bounties in open-source
projects and attract contributors, while developers can earn money by solving
issues". Source S6.

**Supports.** The paid-issue model is not dead.
**Does not support.** Volume, payout reliability, or growth. The same page
footer says "2024 - Rewarded with Opire", which is a copyright year, not an
activity date.
**State.** VERIFIED quote; activity level UNVERIFIED.
**Would be falsified by.** The site going offline or the bounty board being
read-only.

---

## E-05 - Opire's own counters conflict with its listings

**Claim.** Platform activity numbers are not reliable enough to cite as market
size.

**Evidence.** The rewards board at retrieval displayed "Bounties paid 0",
"Bounties available 0", "Money paid in bounties $0.00", "Money available in
bounties $0.00", and in the same view listed bounties at $100.00, $42.00, and
$20.00. Source S7.

**Supports.** Treat platform metrics as AMBIGUOUS. Do not use "$0 paid" as proof
of no market, and do not use listing counts as proof of a large market.
**Does not support.** Either conclusion on its own.
**State.** AMBIGUOUS, recorded as observed.
**Would be falsified by.** A documented API response that explains the zero
counters (for example, counters scoped to the logged-out session).

---

## E-06 - Algora no longer presents as a bounty marketplace

**Claim.** Copy that calls Algora a bounty marketplace is out of date.

**Evidence.** Algora home page headline: "Hire your competitors' best
engineers". The page describes talent placement, not issue bounties. Source S8.

**Supports.** Platform churn risk is real; do not build on one platform's
bounty API.
**Does not support.** That Algora never had bounties. It did; the site changed.
**State.** VERIFIED for the current page.
**Would be falsified by.** A live Algora bounty product page with current
listings.

---

## E-07 - `algora.io/bounties` returns 404

**Claim.** The old bounty entry point is gone at that path.

**Evidence.** HTTP GET `https://algora.io/bounties` returned a 404 on
2026-11-18. Source S9.

**Supports.** The old link in any sales copy or template must not be used.
**Does not support.** That the entire bounty product was deleted; it may have
moved to another host or been folded into the talent product.
**State.** VERIFIED (route status).
**Would be falsified by.** A working bounty route at a different URL.

---

## E-08 - IssueHunt now presents as a security bug bounty platform

**Claim.** IssueHunt is not a current open-source issue-fix marketplace on its
home page.

**Evidence.** IssueHunt home page title: "#1 Bug Bounty platform in Japan". The
page describes vulnerability reports and rewards, not GitHub issue fixes.
Source S10.

**Supports.** Do not list IssueHunt as an OSS issue bounty board in the pack.
**Does not support.** That no OSS bounty history exists at IssueHunt.
**State.** VERIFIED for the current home page.
**Would be falsified by.** A current OSS bounty board at issuehunt.io.

---

## E-09 - GitHub gives pull request templates away

**Claim.** The PR template is not a scarce artifact.

**Evidence.** GitHub Docs: "When you add a pull request template to your
repository, project contributors will automatically see the template's contents
in the pull request body." Source S12.

**Supports.** Price the workflow and tooling, not the template.
**Does not support.** That a template has no value; it means the value is in
selection, scoping, and proof, not in the file existing.
**State.** VERIFIED.
**Would be falsified by.** GitHub removing the feature (would not change the
pricing logic much).

---

## E-10 - Free downloadable PR template packs exist

**Claim.** A competing paid template pack must beat a free substitute.

**Evidence.** Gitmore guide: the reader can get "free markdown files you can
download and drop into your repository today", with four template downloads.
Source S13.

**Supports.** The $9 tier must include the decision layer, not only templates.
**Does not support.** That free templates include paid-issue scoring, timeboxing,
or evidence packaging. They do not, based on the page.
**State.** VERIFIED.
**Would be falsified by.** The free files being removed.

---

## E-11 - A paid PR-template pack was not visible in one search

**Claim.** Weak: there is no obvious paid competitor for this exact query.

**Evidence.** DuckDuckGo HTML results for `"pull request" template pack gumroad`
returned free template galleries, GitHub Docs, GitLab/Bitbucket guides, and
vendor blogs on the first page. No paid pack appeared. Source S14.

**Supports.** Nothing on its own. Absence of a result is not absence of a market.
**Does not support.** That no paid competitor exists, or that demand is high.
**State.** UNVERIFIED / weak negative.
**Would be falsified by.** A paid pack with sales history in the same niche.
This is the first thing a human should check before publishing.

---

## E-12 - Small PRs can merge inside two hours

**Claim.** The 120-minute timebox is compatible with real review latency for
small PRs.

**Evidence.** 112 merged PRs sampled from three repositories: pooled median
open-to-merge **1.11 hours**; **52.7%** merged within 2 hours. Per repo:
flask 0.13h median (n=5), fastapi 0.57h (n=74), httpx 4.27h (n=33). Artifact:
`research/market_measurement.json` -> `merge_latency`.

**Supports.** A scoped PR can clear review in one session.
**Does not support.** That a contributor can write the PR in 2 hours, that a
maintainer will review promptly, or that any specific PR will merge. This is
review latency, not effort, and the sample is three repos.
**State.** MEASURED, limited sample.
**Would be falsified by.** A larger sample where almost nothing merges within a
day.

---

## E-13 - Payment fees leave a positive margin at all three prices

**Claim.** Cost is not above 3x price.

**Evidence.** Gumroad pricing: "10% + $0.50" per transaction for sales through
the seller's profile or direct links; "30%" for sales discovered through the
Gumroad marketplace. Source S11. Computed: $9 -> $1.40 fee (net $7.60); $19 ->
$2.40 (net $16.60); $39 -> $4.40 (net $34.60). Marginal production cost is $0.

**Supports.** The 3x cost kill rule passes on fees alone.
**Does not support.** Profitability. Ad spend, refunds, chargebacks, and time
are excluded. The 30% marketplace rate on a $9 sale leaves $6.30 before refunds;
it is a marketplace-only rate, not 10% + $0.50.
**State.** VERIFIED quotes + arithmetic.
**Would be falsified by.** A fee change or a refund rate high enough to erase
the margin.

---

## E-14 - Gumroad is merchant of record for sales tax

**Claim.** Sales-tax handling is delegated to the platform, not done by this
repo.

**Evidence.** Gumroad pricing page: "Since January 1, 2025, Gumroad handles ALL
your tax obligations." Source S11.

**Supports.** Delivery requirements can point to the platform for tax.
**Does not support.** That the seller has no other tax or legal obligations.
**State.** VERIFIED (vendor claim).
**Would be falsified by.** A platform terms change.

---

## E-15 - This repository already had bounty-scanning rules

**Claim.** The scanning rules in the kit have prior art in this repo.

**Evidence.** `scripts/paid_issue_hunter.py` enforces: amount on the same line as
a bounty word, greater than $50 and at most $50,000, repo pushed within 120 days,
not archived, at least 20 stars, at least one skill keyword, issue-specific
platform links only. Source S15.

**Supports.** Reusing tested rules instead of inventing new ones.
**Does not support.** That those thresholds are optimal for a buyer. They are a
starting policy and are configurable in the kit.
**State.** VERIFIED (local code).
**Would be falsified by.** The script changing its rules.

---

## E-16 - REFUTED: "Algora is a bounty marketplace you can use today"

**Status.** REFUTED by E-06 and E-07. The home page sells talent placement and
the bounty route is 404. Do not publish this claim.

## E-17 - PARTIALLY REFUTED: "IssueHunt pays for open-source issue fixes"

**Status.** The current home page sells security bug bounties (E-08). Historic
OSS bounties may exist, but the claim is not true as a present-tense product
description. Do not publish it.

## E-18 - UNKNOWN: sales of comparable paid packs

**Status.** No sales figure, review count, or revenue estimate for a comparable
product was found. Every statement about demand for this pack is a hypothesis.
The pre-registered test in `MARKET_RESEARCH.md` section 8 is the only honest
path from hypothesis to evidence.
