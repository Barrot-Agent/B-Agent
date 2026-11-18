# Marketplace template

A marketplace earns from listings or transactions. It needs four policies before it
needs code: who may list, what is forbidden, how money moves, and who decides disputes.

## Title formula

`[Niche] marketplace for [artifact type], [commission] per sale, escrow on delivery`
Name the niche, the artifact, the commission and the escrow rule in the title. If one
of the four is missing, the listing page will be vague and so will the product.

## Pricing table

| Fee | Rate | When |
|---|---|---|
| Listing | 0 | free to list, so supply is not gated by price |
| Commission | 10-20 percent | on completed sale |
| Featured slot | 19-49 per week | optional placement, labelled as sponsored |
| Dispute fee | cost only | charged to the party that loses the dispute |

## Outline

1. Vendor onboarding: identity, payout method, tax form
2. Listing rules: what may be sold, what is refused, evidence required
3. Commission and payout schedule
4. Escrow: hold, release, refund, and the timeout path
5. Dispute process with a decision deadline
6. Removal policy and appeals
7. Fee change policy with notice period

## Deliverables checklist

- [ ] vendor agreement with the refusal list
- [ ] commission calculation with worked examples
- [ ] escrow state machine: held, released, refunded, expired
- [ ] dispute form and a named decision maker
- [ ] sponsored placement disclosure text
- [ ] payout ledger schema
- [ ] takedown and appeal path

## Sales page copy structure

For vendors:
1. Headline: who buys here
2. Commission and payout timing, stated as numbers
3. What is refused
4. How disputes end
5. Apply

For buyers:
1. Headline: what is curated
2. Escrow protection in one sentence
3. Refund path
4. Browse

## File structure

```
marketplace/
  POLICIES/vendor.md
  POLICIES/disputes.md
  POLICIES/escrow.md
  LEDGER/schema.json
  LISTINGS/example.md
  FEES.md
```
