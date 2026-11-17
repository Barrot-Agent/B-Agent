# Listing Barrot as a server: what WebMCP is, and what to actually publish

Date: 2026-11-17. Baseline: HEAD 83cead57b. Quote check:
`scripts/webmcp_check.py` -> `data/mcp/webmcp_check.json`, all four quotes matched.

## 1. WebMCP, quoted, and the category error it corrects

Fetched https://raw.githubusercontent.com/webmachinelearning/webmcp/main/README.md:

> WebMCP lets developers expose web application functionality as

> can be thought of as in-page

> WebMCP is designed to complement, not replace

> First published August 13, 2025

Read those together. WebMCP is a browser API for exposing page functionality to a
browser-integrated agent. It is not a directory, not a marketplace, and by its own
text it does not replace backend MCP. There is no such thing as "listing a server on
WebMCP". The listing targets are the MCP directories.

This is a correction to the request, not a refusal to package the server.

## 2. What gets published

The server is `scripts/barrot_mcp_server.py`, stdio, standard library only, seven
tools, no network listener. It is already registered in this repository's
`opencode.json` and answered live calls in-session.

| Tool | What it does | Proof |
|---|---|---|
| check_capability | looks up a capability in the audit file | returns evidence for a2a_server.py |
| run_foundry_cycle | refuses: no foundry exists | NOT_AVAILABLE, 0 files |
| flight_recorder_replay | refuses without two comparable runs | INSUFFICIENT_DATA with count |
| reverse_engineer | grade counts from a claims file | 6 records, 3 usable on p_vs_np |
| trace5_validate | quotes must exist in stored sources | valid true on the consciousness file |
| verdict_check | verdict needs falsifier and upgrade condition | passes the real doc, fails a fixture |
| repo_guard | Liquid-hostile markdown, unguarded optional imports | clean on this repo, flags fixtures |

Tests: `python3 -m pytest tests/test_mcp_server.py -q` -> 16 passed.

Install, exactly as tested here:

```json
"mcp": { "servers": { "barrot": {
  "type": "local",
  "command": ["python3", "scripts/barrot_mcp_server.py"],
  "timeout": { "startup": 30000 }
}}}
```

No key. No environment variable. No package manager.

## 3. Where to list it

Reachability checked 2026-11-17, not assumed:

| Target | HTTP | What to submit |
|---|---|---|
| glama.ai/mcp/servers | 200 | repository URL, tool list |
| mcp.so | 200 | server entry with install command |
| pulsemcp.com | 200 | server entry |
| github.com/punkpeye/awesome-mcp-servers | 200 | pull request adding one line |
| smithery.ai | 308 redirect | submit through the site, not a raw API |

Submission itself needs an account on each site. That is an approval item, named in
STATUS. Until then the listing is prepared, not published.

## 4. Free tier and paid tier

- Free: the whole server, local, no telemetry.
- Paid: hosted endpoint with the retraction list refreshed weekly, $29/month.
- One-off: $99 human-reviewed audit report.

Nothing paid exists yet. The hosted tier is a promise until there is an endpoint.

## 5. Demo script, 45 seconds

1. Open a claims file with one quote that does not exist in the source.
2. Run `trace5_validate`. It fails and names the record. Say: this is the check your
   agent skips.
3. Run `repo_guard` on the repository. Two failures we hit in real life, now caught.
4. Run `verdict_check` on a verdict with no upgrade condition. It fails. Say: a
   verdict you cannot revisit is a paragraph.
5. Show the retraction list: four DOIs, each with a Crossref notice.
6. Close: seven tools, no network, free to clone.

## 6. Not done

- No directory submission was made; each needs an account.
- No hosted endpoint exists; the $29 tier has no backend.
- WebMCP integration is not applicable for a stdio server, by the quotes above.
