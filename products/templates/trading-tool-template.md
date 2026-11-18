# Trading tool template

Educational only, not financial advice. Every file in this category carries that line
at the top, including this template.

## Allowed and forbidden

Allowed: journals, backtest templates, risk calculators, strategy playbooks,
psychology checklists, data-cleaning scripts.

Forbidden: signals, buy or sell calls, guaranteed returns, specific coin or stock
picks, performance claims that imply future results, any product that decides a trade
for the buyer.

A tool may compute position size from a risk percentage. It may not say what to buy.

## Title formula

`[Discipline] Journal for [Market type]: [Count] fields, no signals`
The title states what the artifact measures and disclaims what it does not do.

## Pricing table

| Tier | Price | Contents |
|---|---|---|
| Journal | 9-19 | one spreadsheet plus a one-page guide |
| Journal + calculator | 29-39 | plus a risk calculator with tests |
| Coaching pack | 79-149 | plus a review checklist and a sample week |

## Outline

1. What this measures and what it cannot
2. Before the session: plan fields
3. During the session: execution fields
4. After the session: review fields and a scoring rule
5. Four weeks of example entries, clearly labelled as synthetic
6. A worked risk calculation

## Deliverables checklist

- [ ] the disclaimer on the cover, in the sales copy, and in the first row of the file
- [ ] a calculator with at least one unit test on the arithmetic
- [ ] no target price, no direction, no recommendation field
- [ ] synthetic examples labelled as synthetic
- [ ] one page on what the tool does not predict
- [ ] a licence line: personal use, no redistribution

## Sales page copy structure

1. Headline: the discipline, not the profit
2. "Educational only, not financial advice" in the first screen
3. What the buyer records, field by field
4. What the buyer does not get: signals, picks, returns
5. Price and format
6. Who should not buy this
7. Refund sentence

## File structure

```
trading-tool-slug/
  README.md            starts with the disclaimer
  journal.csv          empty, header only
  calculator.py        arithmetic only, tested
  examples/            synthetic entries
  guide.md
  DISCLAIMER.txt
```
