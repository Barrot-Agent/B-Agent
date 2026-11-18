# Service template

## Title formula

`[Fixed outcome] for [System], delivered in [days]`
A service title names the deliverable and the boundary. "Audit" alone is not a
service; "citation audit of 50 claims, 3 days, report plus fixed files" is.

## Pricing table

| Tier | Price | Scope | Turnaround |
|---|---|---|---|
| Audit | 199-499 | up to 50 items, written report, no code changes | 3 days |
| Fix | 799-1500 | report plus a pull request that passes your CI | 7 days |
| Retainer | 500-2000 per month | two audits, priority queue | monthly |

Refuse scope that cannot be verified by a test or a quote. A service that cannot fail
a test cannot be priced.

## Outline

1. Intake: what the client sends, in one form
2. Check: the exact checks run, each one named
3. Report: findings ranked by cost of being wrong
4. Fix: pull request, tests, and what is out of scope
5. Handover: one page on how to keep it clean

## Deliverables checklist

- [ ] intake form with a size limit
- [ ] named checks, each reproducible by the client
- [ ] report with severity, evidence, and the smallest fix
- [ ] pull request that passes CI or a written reason it cannot
- [ ] out-of-scope list, signed off before work starts
- [ ] payment terms: 50 percent up front for new clients

## Sales page copy structure

1. Headline: the outcome, with a number
2. The failure this prevents, in one concrete case
3. What the client gets, as a list of files
4. What is not included
5. Price, turnaround, and how to start
6. Refund: a re-run if the checks were run incorrectly, not a satisfaction refund

## File structure

```
service-slug/
  OFFER.md          scope, price, turnaround
  intake.md         what the client must send
  checks.md         every check, named
  report-template.md
  handover.md
```
