# MEMORY

Barrot's long-term memory. Append durable facts here when the user says "remember this".

## User
- Sean — Orchestrator. Calls me Barrot.

## Repo
- Barrot-Agent (B-Agent) lives on GitHub.
- Offline build: Termux on phone, 0.5B model, llama-cli, no internet.

## Agent setup
- OpenCode agent: `.opencode/agent/barrot.md`
- Model: `opencode/deepseek-v4.1-flash-free`
- Default agent in this repo: `barrot`
- Runtime: OpenCode free models only. No external providers.

## MCP
- Live stack (opencode.json): `github` remote + `docling` local + `searxng` local. Verified 2026-11-15: github 49 tools, docling 21 tools, searxng 4 tools.
- `github` — remote `https://api.githubcopilot.com/mcp/`; PAT read from `GITHUB_MCP_TOKEN` via `{env:GITHUB_MCP_TOKEN}` header. Token lives in the OpenCode service env (`opencode service set env GITHUB_MCP_TOKEN "$(gh auth token)"`). A service restart is required before MCP connections see new config or env.
- OAuth for github MCP does not work: GitHub's authorization server has no dynamic client registration.
- `docling` — `uvx --from "docling-mcp[local]" docling-mcp-server --transport stdio`; cold start is slow (tens of seconds), startup timeout is 240s.
- `searxng` — `npx mcp-searxng` against `http://127.0.0.1:8888`; start with `bash scripts/start_searxng.sh --daemon` (idempotent, logs to `~/.local/share/searxng/searxng.log`).
- Legacy `mcp_config.json` + `data/mcp_config.json` mirror the live stack for the Python MCP layer (`barrot_agent.mcp_sync`); they are not read by OpenCode.
- Phone RAM is tight (~3.6 GB total, <0.5 GB available). MCP connections cycle/reconnect under that pressure — that is resource churn, not a config error. Docling (Python) is the heaviest.
