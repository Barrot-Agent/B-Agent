# Product capability matrix

Date: 2026-11-18. Iteration 8. Revenue to date: $0.00. No number on this page is
revenue or a forecast.

Grade meaning: Q means the artifact can be built from what is in this repository and
verified by a test. E means the artifact is buildable but demand or price is unverified.
X means a required input is missing. Every grade states its basis.

## Market evidence, before any row

What was actually fetched on 2026-11-18:

| Source | Status | What it gives |
|---|---|---|
| gumroad.com/pricing | 200 | commission text: 10 percent plus 50 cents, 30 percent via Discover |
| one Gumroad product page | 200 | a price of 2.67 in the page markup |
| gumroad.com/discover search | 200 | client-rendered, no price in the HTML |
| a Gumroad creator profile | 200 | client-rendered, no price in the HTML |
| udemy.com course search | 403 | blocked to anonymous fetch |
| etsy.com search | 403 | blocked to anonymous fetch |
| api.lemonsqueezy.com/v1/products | 401 | token required |
| api.polar.sh/v1/products | 401 | token required |
| polar.sh/pricing and /docs/features/fees | 404 | no fee page at those paths |

Consequence: a top-10-per-category table across those five platforms cannot be built
from evidence gathered here. One product price is not a market. Rather than invent ten
rows per category, this matrix grades buildability and names the missing dataset.

## Categories

| # | Category | Time to build | Cost to build | Observed or proposed price | Best platform | Next product | Grade and basis |
|---|---|---|---|---|---|---|---|
| 1 | Digital downloads | 4-8 h | 0 | 9-49 proposed; one observed price 2.67 | Gumroad, fee quoted | CI Rescue Checklist, 42 checks | Q build, E demand |
| 2 | Ebooks | 20-40 h | 0 | 19-59 proposed | Gumroad or Polar | Citation Integrity Playbook, 40 pages | Q build, E demand |
| 3 | Courses | 40-80 h | 0-40 for hosting | 49-299 proposed | Self-hosted plus Gumroad | TRACE-5 Practitioner Course, 5 modules | E build, E demand |
| 4 | Services | 1-3 days per job | 0 | 199-1500 proposed | Direct invoice, Polar for card | Citation audit, 50 claims | Q build, E demand |
| 5 | Trading tools | 8-16 h | 0 | 9-149 proposed | Gumroad | Risk calculator plus journal, educational only | Q build, X on any signal product |
| 6 | Marketplace | 40-120 h | hosting plus payment fees | 10-20 percent commission | Custom, not one of the five | Niche audit marketplace, vendors vetted | E build, X until escrow and dispute policy exist |
| 7 | Advertising | 4-8 h | 0 | 49-499 per unit proposed | Direct, disclosed | Sponsored slot in a newsletter | X until measured traffic exists |
| 8 | SaaS and MCP | 2-5 days | 0-20 per month hosting | 9-99 per month proposed | Polar for subscriptions | Evidence Audit MCP hosted tier | Q build, E demand |

Time and cost are estimates made by the builder, not measurements. The only measured
numbers on this page are the HTTP statuses and the prices quoted above.

Build state (2026-11-18): row 1 is STAGED on branch
`phase1/digital-downloads-paid-issue-pr` at
`products/ship-paid-issue-pr-in-2-hours/`. Not published, not priced live, no
transaction. Rows 2-8 are not started.

## Why the grades are not all Q

A product is only Q when a test can prove it works. The Evidence Audit MCP already
has seven tools and tests, so the hosted tier is a packaging problem. Advertising
needs measured traffic, which this repository does not have. Marketplace needs escrow
and a dispute path, which are policies plus code that do not exist yet. Trading
products are Q only for journals and calculators, because anything that recommends a
trade is refused outright.

## Highest Q score among buildable products

Evidence Audit MCP hosted tier and the CI Rescue Checklist tie on buildability. The
MCP wins on differentiation: it is already tested here, and the audit claim can be
re-verified by a buyer running one command. Next queued product is therefore the MCP
packaging, not a new artifact.

## Files

- Templates: `products/templates/`, eight files, one per category
- Drafts: `products/drafts/`, one folder per category, all marked DRAFT
- Staged product: `products/ship-paid-issue-pr-in-2-hours/`, category 1 only
- Polar description: `docs/money/POLAR.md`, under 3000 characters, staged not published
- Tests: `tests/test_product_factory.py`
