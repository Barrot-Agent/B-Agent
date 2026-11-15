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
- Default runtime uses the OpenCode free model. LunaRoute remains optional/unverified; its MCP server is disabled.

## MCP
- `github` — remote GitHub MCP; requires `GITHUB_MCP_TOKEN` in the OpenCode service environment; authentication and data flow are not yet verified.
- `docling` — local document/OCR conversion via `uvx`.
- `searxng` — local web search via `npx mcp-searxng`; run `bash scripts/start_searxng.sh` first.
