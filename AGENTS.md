# Barrot

Barrot is the main agent for this repo.

- Agent definition: `.opencode/agent/barrot.md`
- Default OpenCode agent: `barrot` (`opencode.json`)
- Model: `opencode/deepseek-v4.1-flash-free`
- Long-term memory: `MEMORY.md`

## PERMANENT MEMORY - DO NOT ASK AGAIN
- OpenCode is the agent runtime for this repo.
- Barrot uses opencode free models only.
- MCP servers in `opencode.json`: GitHub (remote, PAT from `GITHUB_MCP_TOKEN`), Docling (local OCR/document conversion), SearXNG (local web search).
- Start SearXNG with `bash scripts/start_searxng.sh` before using the `searxng` MCP server.
- Image generation/editing is not wired into this repo's OpenCode config.
