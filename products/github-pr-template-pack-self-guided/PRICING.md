# Pricing

Status: proposal. No price has been charged, changed, or published. Any change
to a live price requires explicit human sign-off.

## Tiers

| | Field Kit | Operator Kit | Team Kit |
|---|---|---|---|
| Price | **$9** | **$19** | **$39** |
| Intake and stop rules | yes | yes | yes |
| Decision rules and formula | yes | yes | yes |
| PR body and evidence templates | yes | yes | yes |
| Printable timebox card | yes | yes | yes |
| Ledger CSV | yes | yes | yes |
| Python toolkit | no | yes | yes |
| 76 tests and self-test | no | yes | yes |
| Generated examples | no | yes | yes |
| Updates | 1 year | 1 year | 1 year |
| Licence | personal | personal | up to 10 seats, internal |
| Invoice | no | no | yes |
| Email support | no | no | 30 days, 2 business days |
| Refund | 14 days | 14 days | 14 days |

Names are internal labels. The store listing can show them as Basic / Pro /
Team; the contents must not change without a new version and a changelog entry.

## Why these numbers

**Anchor, not forecast.** In the measured sample, six issues stated an amount;
the median was $525, the range $450-$600. One accepted bounty at that level is
more than ten times the top tier. That does not mean a buyer will earn it. It
means the price is small relative to a single stated bounty, which is the only
value anchor used here.

**What the price is not based on.** No competitor price was observed. No sales
data exists. No ad spend is assumed. The numbers are a test, not an optimum.

**Why a $9 entry exists.** The template portion is a commodity: GitHub ships PR
templates for free and several sites give them away. A buyer who only wants a
template should pay $9 or use the free ones. The $19 tier is the actual product:
the timer and the validator. The $39 tier prices internal sharing, not more
content.

## Unit economics

Store fee: 10% + $0.50 per transaction on direct sales; 30% on marketplace
traffic (published rate, checked 2026-11-18).

| Price | Fee (direct) | Net (direct) | Fee (marketplace) | Net (marketplace) |
|---|---|---|---|---|
| $9 | $1.40 (15.6%) | $7.60 | $2.70 (30%) | $6.30 |
| $19 | $2.40 (12.6%) | $16.60 | $5.70 (30%) | $13.30 |
| $39 | $4.40 (11.3%) | $34.60 | $11.70 (30%) | $27.30 |

Marginal cost of delivery: $0. No paid API, no license fee, no per-seat cost.
The only variable costs are the payment fee, refunds, chargebacks, and support
time.

**Refund worst case.** A refunded direct sale loses the fee and the net. At $39
that is a $4.40 loss plus the refunded amount, before any support time. A refund
rate high enough to erase margin would be a kill signal, not a pricing problem.

**Support cost.** Team Kit includes 30 days of email support at two business
days response. At the $34.60 net on a direct $39 sale and an internal rate of
$50/hour, break-even support is 41.5 minutes per sale (`34.60 / 50 * 60`). Above
that the tier is underpriced. That is the trigger to raise the price or cut the
support window, and it must be measured, not assumed.

## Cost kill-rule check

The rule is: kill if cost is more than 3x price.

| Price | 3x price | Cash cost per sale | Verdict |
|---|---|---|---|
| $9 | $27.00 | $1.40 fee | PASS |
| $19 | $57.00 | $2.40 fee | PASS |
| $39 | $117.00 | $4.40 fee | PASS |

Production cost was paid in time, not cash: existing machine, standard library,
no paid research API. A time valuation is deliberately excluded from this table
because it is not a cash cost and would make the check meaningless. For payback
only: at $50/hour, each $39 direct sale nets $34.60, so covering `H` build hours
needs `H * 50 / 34.60` sales. That is a payback statement, not a cost claim, and
it is not a forecast.

## What is not offered

- No subscription, no upsell, no "pro" tier hidden behind the page.
- No countdown timer, no fake scarcity, no "only 10 copies".
- No pay-what-you-want. It complicates refunds and the ledger.
- No affiliate programme in Phase 1.

## Pre-registered price test

From `research/MARKET_RESEARCH.md` section 8:

- Window: 30 days after publication.
- Falsifier: fewer than 3 paid sales at any tier with at least 300 page views.
- Upgrade condition: 3+ sales, no refunds, one verified buyer report of a PR
  shipped inside the timebox.
- Limit: this tests one page and one audience, not the market.

No price change before the window ends. If the falsifier triggers, stop and do
not build Templates 2-6 from this evidence. If the upgrade condition triggers,
the next test is a $49 bundle with the ebook, not a price increase on this pack.

## Discounts

None at launch. A launch discount would make the first sales unrepresentative of
the listed price and weaken the test. If a discount is ever run, it needs a
start date, an end date, a code, and a line in the improvement log.

## Human sign-off

Publishing, changing a price, or running a promotion requires explicit approval
from Sean. This file is a proposal; the staged branch does not charge anything.
