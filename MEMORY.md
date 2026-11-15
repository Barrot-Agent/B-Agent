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

## Offline memory (gist compression)
- Source: Memorilla (Stanford, arXiv 2610.21375) — encodes a collection once, then a ~200M-param module produces 16 query-conditioned memory tokens for a frozen Qwen3-8B. Numbers: FactKG 84.33% vs 80.43% full context at 108x fewer tokens; 0.74 s vs 19.9 s at 512 docs (paper); NarrativeQA >4,000x compression.
- Barrot implementation: `barrot_agent/gist_memory.py` — stdlib, CPU, deterministic, extractive. 16 gist slots x 6 words, two-pass IDF selection, MMR redundancy penalty, source span kept for lookup.
- Rules: fixed budget always; condition on the query; two passes; never generate text — extract verbatim; keep the raw source for names/numbers/dates.
- Verified failure modes of the real system: buried-clue test hallucinated a shellfish allergy and a wrong name/birthday; Hound of the Baskervilles plot QA 1/8 vs 5/8 full context. Gist = context/preferences; RAG = exact facts.
- Limits of our version: lexical only (no embeddings), so synonyms ("health issues" vs "diabetes") do not match.

## Agent leverage (from AGI video, verified part)
- Same model, different harness: GPT-6 Astra scored 62.7% (ARC standard) vs 99.9% (provider adapter with persistent reasoning state + compaction). Environment/tools/memory move the score more than the model name.
- Long-run prompt pattern: clear finish line, permission to self-check, `progress.md` memory file, room to run, stop only for truly undecidable items.
- ARC Prize explicitly says ARC-AGI-3 is not proof of AGI. "AGI is here" = hype; verify at arcprize.org before repeating claims.
