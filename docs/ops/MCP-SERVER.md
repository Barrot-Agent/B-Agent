# MCP server: spec fetched, five tools, three real

Date: 2026-11-17. Baseline: HEAD 4190841a4. Server: scripts/barrot_mcp_server.py.
Spec check: scripts/mcp_spec_check.py -> data/mcp/spec_check.json.

## 1. Spec retrieved by query, not recalled

Fetched https://modelcontextprotocol.io/specification/2025-06-18/server/tools on
2026-11-17, HTTP 200. Three literal substrings were checked against the fetched page
and all three matched:

- "To discover available tools, clients send a"
- "To invoke a tool, clients send a"
- "Servers that support tools"

The protocol version the server declares, 2025-06-18, is the version in the URL that
was fetched, not a remembered number.

The internal task spec was a different document, and it was truncated. The recorded
evidence, quoted from docs/barrot-status.md: "Spec arrived truncated: the message ends
inside this tool's return object at". Tool 5 never arrived at all.

## 2. What was rebuilt

| # | Tool | Grade | Basis |
|---|---|---|---|
| 1 | check_capability | Q | barrot_capability_audit.json: 122 capabilities with evidence; tested on a2a_server.py |
| 2 | run_foundry_cycle | X | no foundry module exists; the tool refuses with NOT_AVAILABLE and records the goal |
| 3 | flight_recorder_replay | X capability, Q refusal | 17 records across 14 files, but no two runs of the same mission and skill version; refuses with INSUFFICIENT_DATA and the count |
| 4 | reverse_engineer | Q, reconstructed | contract was truncated at "steps_used"; returns TRACE-5 steps and grade counts from a claims file, labelled as a reconstruction |
| 5 | trace5_validate | Q, invented | tool 5 was never specified; defined here as offline validation of a claims file |

Grade 2 is X on purpose. A tool that can only refuse is honest, not done. It stays in
the list so callers get a real protocol error instead of a silent failure.

## 3. Test evidence

Ten tests, tests/test_mcp_server.py, command
`python3 -m pytest tests/test_mcp_server.py -q`, output line:
`10 passed in 13.63s`.

Each tool has a reproducible call in that file: check_capability returns the evidence
block for a real file; run_foundry_cycle returns isError true; flight_recorder_replay
returns isError true with the count; reverse_engineer returns 5 records and 3 usable
claims for the Hodge file; trace5_validate returns valid true. The stdio transport is
tested by piping two JSON-RPC lines into the process.

## 4. Security

Path arguments are resolved and rejected if they escape the repository root; that is
tested with ../../etc/passwd. Stdio only, loopback-free, no network listener, no auth
layer. Inputs are validated by the handler before dispatch.

## 5. Not done

- Not registered in opencode.json. Wiring it into the runtime is a config change that
  affects every session, so it is left for an explicit go.
- run_foundry_cycle remains X until a foundry exists.
- flight_recorder_replay remains X until two comparable runs are recorded.

## Overrun

This cycle exceeded the 15 minute cap: spec fetch, server, five tools, ten tests. The
overrun is logged in the flight recorder.

The separate deep-research request on consciousness and the GR/QM gap was not started
in this cycle. It is queued, and no claim about it is made here.
