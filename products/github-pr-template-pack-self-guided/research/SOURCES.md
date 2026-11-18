# Sources

All URLs were fetched on 2026-11-18 (UTC) unless a different date is written in
the row. Quotes are copied from the fetched text. Numbers produced by our own
scripts are marked "measured", not "published".

| ID | Source | URL | Type | Used for |
|---|---|---|---|---|
| S1 | GitHub Search API, query `label:bounty is:issue is:open` | https://api.github.com/search/issues?q=label:bounty+is:issue+is:open | measured, primary | Count of open issues carrying the bounty label |
| S2 | GitHub Search API, query `algora in:body is:issue is:open` | https://api.github.com/search/issues?q=algora+in:body+is:issue+is:open | measured, primary | Count of issues that mention Algora |
| S3 | GitHub Search API, query `"paid" "pull request" in:body is:issue is:open` | https://api.github.com/search/issues?q=%22paid%22+%22pull+request%22+in:body+is:issue+is:open | measured, primary | Upper bound on issues that talk about paid PR work |
| S4 | GitHub Search API, 100-item sample of S1 | https://api.github.com/search/issues?q=label:bounty+is:issue+is:open&per_page=50 | measured, primary | Share of labelled issues that state an amount, platform links, comment count, age |
| S5 | GitHub REST pulls API, 100 most recently updated closed PRs per repository | https://api.github.com/repos/pallets/flask/pulls | measured, primary | Open-to-merge latency in three public repositories |
| S6 | Opire home page | https://opire.dev/home | vendor page | Live bounty marketplace positioning |
| S7 | Opire rewards board | https://app.opire.dev | vendor page | Listed bounty amounts at retrieval |
| S8 | Algora home page | https://algora.io/ | vendor page | Current positioning of the largest former bounty marketplace |
| S9 | Algora bounty route | https://algora.io/bounties | HTTP observation | Route returned 404 at retrieval |
| S10 | IssueHunt home page | https://issuehunt.io/ | vendor page | Current positioning of a former OSS bounty marketplace |
| S11 | Gumroad pricing | https://gumroad.com/pricing | vendor page | Fee per sale, merchant-of-record status |
| S12 | GitHub Docs, creating a pull request template | https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository | vendor documentation | PR templates are a built-in, free GitHub feature |
| S13 | Gitmore, pull request template guide | https://gitmore.io/blog/pull-request-template | competitor page | Free downloadable PR templates already exist |
| S14 | DuckDuckGo HTML results for `"pull request" template pack gumroad` | https://html.duckduckgo.com/html/?q=%22pull+request%22+template+pack+gumroad | search result page | What a buyer sees for this query; free templates dominate the first page |
| S15 | `scripts/paid_issue_hunter.py` in this repository | local file | internal prior art | Existing bounty rules: amount on same line as bounty word, \$50-\$50,000, active repo, skill keyword |

## Measurement artifact

`research/market_measurement.json` is the output of `research/measure_market.py`
at 2026-11-18T06:09:03Z. Re-run with:

```bash
cd research
python3 measure_market.py --out market_measurement.json
```

The script is read-only: it calls `gh api` GET endpoints, writes one local JSON
file, and never comments, claims, labels, or opens anything on GitHub.

## What these sources cannot tell us

- They do not measure sales of this product or of any comparable paid pack.
- GitHub search counts include spam, stale issues, and issues where the word
  "bounty" appears for other reasons.
- A stated bounty is not escrow. No payout in this research was verified.
- Search result pages are personalised and change; S14 is one query on one
  engine at one time, not a market size estimate.
- Vendor pages describe intent, not revenue or user counts.
