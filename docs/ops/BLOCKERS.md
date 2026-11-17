# Blocker re-audit

Date: 2026-11-17. Baseline: HEAD 83cead57b. Rule: a blocker is either unblocked with
evidence or stated with the exact thing it needs. Silence is not allowed.

| # | Blocker | State | Evidence or exact need |
|---|---|---|---|
| 1 | MCP server registration | CLOSED | live in-session call: trace5_validate valid true; 16 tests |
| 2 | Learning-loop KPI | CLOSED | 4/4 retracted detected, 2/2 controls clear; denylist enforced in validate() |
| 3 | GO GITHUB | UNBLOCKED | `gh api user` -> login Barrot-Agent, id 238745440; scopes gist, read:org, repo, workflow; 4,635 calls left |
| 4 | MCP directory listing | BLOCKED, needs user | glama.ai, mcp.so, pulsemcp.com, awesome-mcp-servers all reachable (200); each submission needs an account created by the user |
| 5 | Paid issue entry | BLOCKED, needs user | 137 issues scanned, Q 0. Needs a bounty-platform account with payout details, or an on-chain escrow address |
| 6 | Foundry | STILL BLOCKED | no module matches foundry; run_foundry_cycle refuses by design. Needs a scoped build cycle, not a token |
| 7 | Flight recorder replay | STILL BLOCKED | 17 records, no two runs of the same mission and skill version. Needs a second real run of one mission |
| 8 | Fields track 2 (resonance) | STILL BLOCKED | repository rule: each track needs an explicit GO FIELDS from the user |
| 9 | Thermal KPI | STILL BLOCKED | `/sys/class/thermal` exposes 0 zones on this device; no power_supply entries. Needs a device with sensors |
| 10 | Parallel-agent convergence KPI | STILL BLOCKED | two subagent runs cost minutes each; not allocatable inside the 15 minute cap without displacing the cycle |
| 11 | Governance coverage link | STILL BLOCKED, needs user | a threshold would be born red at 36 percent coverage; the user must set the threshold or accept red |
| 12 | GO KAGGLE | STILL BLOCKED | no credentials present; Kaggle is unscoped, and no dataset task was requested |

## The one approval that blocks money

Directory listing needs a user account on at least one MCP directory. Without it the
server stays local and nothing is distributed.

## Token handling

`GITHUB_MCP_TOKEN` is not set in this shell. GitHub calls were made through the `gh`
credential store, which holds an OAuth token with scopes gist, read:org, repo,
workflow. No token value was read, printed, or written to any file in this repository.
`gh auth status` output was filtered so the token line could not reach the log.

## DOI audit

`data/research/doi_audit.json`: 15 distinct DOIs cited across data/. Every DOI cited by
a claims file is clean. Three retracted DOIs appear only inside the denylist file
itself, which is where they belong. No claims file cites a retracted source.
