# Digital download template

Status: reusable. Every field is original text, no copied product copy.

## Title formula

`[Outcome] [Artifact] for [Audience] ([Count] [units])`
Example shape: "CI Rescue Checklist for Solo Maintainers (42 checks)". The outcome
comes first, the artifact second, the audience last. No adjectives that cannot be
counted.

## Pricing table

| Tier | Price | What changes |
|---|---|---|
| Single | 9-19 | one file, no updates |
| Bundle | 29-49 | three related files, one year of updates |
| Team | 99-149 | same files, internal sharing allowed, invoice |

Price is set by the number of decisions the artifact removes, not by length. A 6-page
checklist that prevents one broken deploy is worth more than a 60-page book nobody
opens. All prices are proposals, not observed market prices.

## Outline

1. Cover and one-paragraph promise
2. When to use this, when not to
3. The checklist itself, grouped by phase
4. Three worked examples
5. Change log and version

## Deliverables checklist

- [ ] one portable file (PDF or MD) that opens without an account
- [ ] a printable variant
- [ ] a machine-readable variant only if the content is tabular
- [ ] version and date on the cover
- [ ] licence line: personal use, no resale of the file

## Sales page copy structure

1. Headline: the outcome, with the count
2. Who this is for, in one sentence
3. The specific failure it prevents
4. What is inside, as a list of sections
5. Price and what the buyer receives
6. Refund sentence, stated plainly
7. FAQ: format, updates, licence, support

## File structure

```
product-slug/
  README.md          buyer-facing start here
  artifact.md        the download itself
  artifact.pdf       generated, not hand-edited
  CHANGELOG.md
  LICENSE.txt
```
