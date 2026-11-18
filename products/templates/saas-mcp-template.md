# SaaS micro-tool and MCP template

## Title formula

`[Tool] for [agent or team]: [one verb] [one object], no account required to try`
The try-path must work before the pay-path exists. For an MCP server the try-path is a
stdio call; for a web tool it is one request with no login.

## Pricing table

| Tier | Price | Limit |
|---|---|---|
| Free | 0 | 50 calls per month, no card |
| Solo | 9-19 per month | 5,000 calls, email support |
| Team | 49-99 per month | 50,000 calls, invoice, shared keys |
| One-off audit | 199-499 | fixed scope, no subscription |

## Outline

1. The one call the tool makes better than a general model
2. Input schema and refusal cases
3. Output schema, with a worked example
4. Limits, rate limits, and what happens at the limit
5. Error messages a caller can act on
6. Privacy: what is stored, for how long
7. Versioning and deprecation policy

## Deliverables checklist

- [ ] protocol handler that answers initialize and tools/list
- [ ] every tool has a test with a real input and a refused input
- [ ] no credential in logs
- [ ] rate limit enforced, not documented only
- [ ] one-page quickstart that works copy-pasted
- [ ] changelog with breaking-change markers
- [ ] pricing page that states the limit in numbers

## Sales page copy structure

1. Headline: the verb and the object
2. A terminal block showing the call and the response
3. What it refuses to do
4. Limits and price
5. Install in three lines
6. FAQ: data handling, self-hosting, support

## File structure

```
saas-tool-slug/
  server/
  tests/
  QUICKSTART.md
  SCHEMA.md
  PRICING.md
  CHANGELOG.md
```
