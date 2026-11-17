# Transmuting harvested workflows into money

Date: 2026-11-17. Baseline: HEAD 83cead57b. Evidence: `data/harvest/workflows.json`
(33 repos, 58 workflows, Q 58, 10 refused on licence), `data/harvest/components.json`
(3 components pulled), `ATTRIBUTIONS.md`.

## What was harvested, by evidence

Queries were run through GitHub search, sorted by stars, and every workflow claim is a
quote from its own YAML. Three examples, verbatim:

- google-gemini/gemini-cli, `chained_e2e.yml`: trigger `{'push': {'branches': ['main']}`,
  10 jobs.
- upstash/context7, `mcp-registry.yml`: trigger `workflow_dispatch`, publishes with
  OIDC and `mcp-publisher`.
- Panniantong/Agent-Reach, `pytest.yml`: trigger `push` and `pull_request`, four jobs,
  python matrix 3.10 to 3.13 plus a macos include.

Licence gate: 3 pull-eligible components from MIT, MIT and BSD-3-Clause repositories.
Refused: 10 repositories (3 AGPL-3.0, 1 GPL-3.0, 4 NOASSERTION, 2 NONE). Nothing was
read from them beyond the licence field and workflow file names.

## Workflow classes, transmuted

58 workflows reduce to four classes. Each row states what changes, who pays, and what
would show the money version is worthless.

| Harvested class | Money version | Who pays | Speed | Falsifier |
|---|---|---|---|---|
| Test matrix (Agent-Reach pytest.yml) | Money audit workflow that gates every claims file and verdict in CI | teams that must prove citations are real | same day to build, 7-30 days to a reply | nobody pays for checks they can run locally |
| Registry publish (context7 mcp-registry.yml) | MCP listing preflight and publish path | developers who need distribution, not code | blocked until a packaged artifact exists | no artifact, no listing, no money |
| Code quality with concurrency (Scrapling) | Repo guard: Liquid-hostile markdown, unguarded optional imports | maintainers whose docs build keeps breaking | 1 day | the guard finds nothing they did not already know |
| Release and publish jobs | Packaging step for the paid audit report | buyers of the $99 one-off | 14 days | no buyer for a report when a free CLI exists |

Only three of these became workflows in this repository. The rest are mapped, not
built, and that is stated rather than counted as work.

## Money stack, as pushed

1. `.github/workflows/money-audit.yml` runs on push and pull request: validates every
   claims file, gates the verdict, guards docs and imports, then runs the product
   tests. This is the product auditing itself, so a buyer can read the log.
2. `.github/workflows/money-bounty-scan.yml` runs weekly and on demand: scans paid
   issues, grades them, warns when Q is zero, uploads the JSON artifact. This is the
   input stage of "find paid issue, fix, PR, payout".
3. `.github/workflows/money-mcp-listing.yml` runs on demand: proves the server still
   answers with seven tools, checks `server/server.json`, and prints the registry
   prerequisites. It publishes nothing and says so in an annotation.

Workflow 2 is the only one that can lead to money without a human creating an
account, and its current output is Q 0 of 137 issues.

## Timeline to first dollar

| Path | What must happen first | Honest estimate |
|---|---|---|
| Audit product | directory listing approved, one team tries the audit, pays $29 | 7-30 days, unscheduled |
| Bounty | a Q-graded issue appears or an escrow account exists | unknown, currently 0 Q |
| Registry listing | packaged artifact plus registry OIDC | unknown, artifact does not exist |

No revenue has occurred. No payout has been requested. Any number above is an
estimate and is labelled as one.

## Components pulled, with proof

| File | Source | Licence | Test |
|---|---|---|---|
| vendor/workflow-patterns/pytest-matrix.yml | Agent-Reach | MIT | parses, 4 jobs |
| vendor/workflow-patterns/concurrency-paths-ignore.yml | Scrapling | BSD-3-Clause | parses, concurrency block present |
| vendor/workflow-patterns/mcp-registry-publish.yml | context7 | MIT | parses, 1 job |

`tests/test_money_stack.py` asserts the licence, the attribution header, the pinned
commit and that each vendored YAML parses. 8 tests, all passing.
