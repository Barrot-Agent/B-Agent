# Money cycle: products, bounties, listing

Date: 2026-11-17. Baseline: HEAD 83cead57b. Revenue to date: $0.00. No number on
this page is revenue.

## 1. Top five products, ranked by fetched numbers

Source: `scripts/market_scan.py` -> `data/money/market.json`. Competition is a GitHub
repository count; demand is npm weekly downloads of the closest package, or a GitHub
count proxy where no package exists. Score is
`log10(demand+1) * speed_factor / log10(competition+10)`.

| # | Product | Format | Competition | Demand | Score | Hours | Grade |
|---|---|---|---|---|---|---|---|
| 1 | Evidence Audit MCP | MCP server + hosted tier | 7,016 | 90,522,817 | 1.4479 | 6 | Q on the counts |
| 2 | Retracted DOI Watchlist | dataset + refresh script | 649 | 7,016 proxy | 1.3644 | 2 | Q |
| 3 | TRACE-5 Research Kit | templates + CLI | 7,016 | 20,253 proxy | 1.1195 | 3 | Q |
| 4 | MCP Server Audit Template | template repo | 192,462 | 90,522,817 | 1.0540 | 5 | Q |
| 5 | Workflow Doctor | CLI + Action | 1,896 | 402 | 0.7943 | 4 | Q |

The counts prove the fields are crowded or empty. They do not prove anyone pays.
That is the falsifier for all five: no payment signal was retrieved.

Unreachable, stated rather than guessed: Product Hunt (needs a token), Etsy (needs a
key), Gumroad search (client-rendered, no count), Kaggle (needs credentials).

## 2. Product 1 MVP: Evidence Audit MCP

Why this one: it already exists in this repository and is tested. The gap between
"exists" and "sells" is packaging, not code.

What it does, all offline:

- `trace5_validate` - every Q record must quote text present in its stored source
- `reverse_engineer` - grade counts and usable claims from a claims file
- `verdict_check` - a verdict needs a letter, a falsifier, an upgrade condition
- `repo_guard` - Liquid-hostile markdown, unguarded optional imports
- retraction denylist enforced inside validation

Who pays: teams shipping research features that must show citations are real, and
teams that must prove an agent did not invent a quote.

Pricing:

| Tier | Price | What |
|---|---|---|
| Local | free | clone, `python3 scripts/barrot_mcp_server.py`, MIT-style licence |
| Pro | $29/month | hosted endpoint, 10k audits/month, retraction list refreshed weekly |
| Audit | $99 one-off | a human-reviewed report over a client claims file |

Falsifier for the pricing: nobody will pay $29 for checks they can run locally for
free. The paid tier only earns if hosting, refresh and review are worth more than the
clone. That is untested.

Landing copy:

> Your agent cites sources. Can you prove the quotes exist?
> Evidence Audit MCP checks every claim against its stored source, flags retracted
> DOIs, and refuses a verdict that has no falsifier. Seven tools, no network required.
> Free locally. $29/month hosted.

Launch checklist:

1. README with the install block that is tested in this repo
2. Submit to MCP directories: Smithery, Glama, mcp.so, PulseMCP, awesome-mcp-servers
3. Publish the retraction watchlist as the free lead magnet
4. Demo: run `trace5_validate` on a file with one fabricated quote, show the failure
5. Price page live before any outreach
6. Track: installs, audits run, replies. No revenue claim until a payment clears

Money timeline, stated as an estimate: packaging 1 day, directory listings 1 day,
first reply 3-14 days if a listing is approved. First dollar is not scheduled,
because no distribution channel is verified yet.

## 3. Paid GitHub issues: zero verified

`scripts/bounty_scan.py` queried five searches, fetched 137 open issues that state a
bounty, and graded them: Q 0, E 59, X 78.

- Q 0: no issue both states an amount literally and sits in a repo old and large
  enough to be credible.
- The one $10,000 issue was a propaganda dump with a dollar sign in front of it. The
  grader now rejects off-topic bodies by CJK count and stuffed bodies by unique-word
  ratio. That fix was forced by the evidence, not guessed.
- The $600/$450 "escrowed USDC" issues live in repos created this month with zero
  stars and no code history.
- The $150 documentation issue at Clawland-AI/picclaw #36 is a question thread from
  another agent asking whether the bounty is still funded, not a task.
- Platform APIs: `api.polar.sh/v1/issues/` 404, `algora.io/bounties` 404,
  `api.opire.dev/v1/bounties` 404, `issuehunt.io/api/v1/issues` returns HTML.

Decision: no PR was opened against an unverified bounty. Opening public work on a
payout that may not exist costs reputation for a number that may never arrive. The
pick is deferred until one of these exists: (a) a platform account with payout
details, or (b) an issue whose escrow is visible on-chain or in a funded platform
account. That decision needs the user, and it is named in STATUS.

## 4. What this cycle does not claim

- No product was sold, no listing was published, no bounty was entered.
- The ranking proves relative crowding, not willingness to pay.
- Hours are estimates and are labelled as such.
