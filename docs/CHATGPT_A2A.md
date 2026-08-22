# ChatGPT ↔ Barrot-Ω A2A Integration

## Architecture

```
ChatGPT
   ↕  (HTTPS, OpenAI API)
barrot_agent/chatgpt_connector.py  ←  NormalizedResponse
   ↕
scripts/a2a_server.py  (A2A v1.0.1 JSON-RPC)
   ↕  (X-Barrot-Auth header)
Barrot-Ω
   ├── Groq inference  (default)
   ├── ChatGPT relay   (params.agent = "chatgpt")
   ├── GitHub read     (capability = "github-read")
   └── MCP read        (capability = "mcp-read")
```

Privileged operations (`github-write`, `mcp-execute`, `production-deploy`)
are **not** reachable via A2A; they require the out-of-band MCP
approval/sandbox flow in `barrot_agent/mcp_approval.py`.

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | **Yes** (for ChatGPT relay) | — | OpenAI API key |
| `OPENAI_BASE_URL` | No | `https://api.openai.com/v1` | OpenAI-compatible base URL |
| `OPENAI_MODEL` | No | `gpt-4o` | Model identifier |
| `OPENAI_TIMEOUT` | No | `60` | Per-request timeout (seconds) |
| `OPENAI_MAX_RETRIES` | No | `3` | Retry attempts on timeout / 5xx |
| `GROQ_API_KEY` | Yes (for default Groq path) | — | Groq API key |
| `BRAIN_SHARED_SECRET` | Yes | — | A2A authentication secret |

GitHub App env vars (`GITHUB_APP_ID`, `GITHUB_APP_PRIVATE_KEY`,
`GITHUB_INSTALLATION_ID`) are consumed by the existing GitHub orchestration
layer; they are never exposed through the ChatGPT connector.

## Auth Flow

```
POST / HTTP/1.1
X-Barrot-Auth: <BRAIN_SHARED_SECRET>
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "message/send",
  "params": {
    "agent": "chatgpt",          // optional; omit for Groq default
    "capability": "natural-language",  // optional; privileged caps are rejected
    "message": {
      "parts": [{"type": "text", "text": "Your question here"}]
    }
  }
}
```

## Identity Boundaries

Every ChatGPT response is tagged with:
- `role: "chatgpt"` — always identifies the external peer
- `source: "external-agent"` — distinguishes from internal tool results
- `model: "<actual model>"` — for audit

## Capability Exposure

| Skill ID | Description | Permitted over A2A |
|---|---|---|
| `natural-language` | Groq-backed Q&A | ✅ |
| `chatgpt-relay` | Forward to ChatGPT | ✅ |
| `github-read` | Read repos/issues/workflows | ✅ |
| `mcp-read` | MCP server discovery | ✅ |
| `github-write` | Repo/PR writes | ❌ MCP approval required |
| `mcp-execute` | MCP workflow execution | ❌ MCP approval required |
| `production-deploy` | Production deployment | ❌ MCP approval required |

## Local Test Procedure

```bash
# 1. Start the server
export GROQ_API_KEY=gsk_...
export OPENAI_API_KEY=sk-...
export BRAIN_SHARED_SECRET=mysecret
python scripts/a2a_server.py

# 2. Verify Agent Card
curl http://localhost:8000/.well-known/agent-card.json | python3 -m json.tool

# 3. Default Groq request
curl -X POST http://localhost:8000/ \
  -H "X-Barrot-Auth: mysecret" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"message/send","params":{"message":{"parts":[{"type":"text","text":"Hello Barrot"}]}}}'

# 4. ChatGPT relay request
curl -X POST http://localhost:8000/ \
  -H "X-Barrot-Auth: mysecret" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"message/send","params":{"agent":"chatgpt","message":{"parts":[{"type":"text","text":"Hello ChatGPT"}]}}}'

# 5. Privileged capability (should return -32003)
curl -X POST http://localhost:8000/ \
  -H "X-Barrot-Auth: mysecret" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"message/send","params":{"capability":"github-write","message":{"parts":[{"type":"text","text":"push code"}]}}}'

# 6. Run mocked tests (no live API needed)
python -m pytest tests/test_chatgpt_a2a.py -v
```

## Files Changed

| File | Change |
|---|---|
| `barrot_agent/config.py` | Added `OpenAIConfig`, `openai` field on `AppConfig` |
| `barrot_agent/chatgpt_connector.py` | New — `ChatGPTClient` + `NormalizedResponse` |
| `scripts/a2a_server.py` | ChatGPT routing, capability guard, updated Agent Card |
| `tests/test_chatgpt_a2a.py` | New — 11 mocked tests |
| `docs/CHATGPT_A2A.md` | This file |
