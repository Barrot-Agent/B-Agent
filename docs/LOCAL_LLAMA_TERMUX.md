# Barrot Local Llama (Termux)

This is the phone-local Barrot chat route. It uses the existing llama.cpp server; it does not start a second server or expose the endpoint publicly.

## Start

Keep the existing llama-server session running on port 8081. From the Barrot repository root, run:

```bash
bash scripts/barrot-local "Reply exactly: BARROT LOCAL LLAMA ONLINE"
```

The launcher checks `/health`, selects `local_llama`, and starts Barrot's normal chat entry point. It writes the answer to `barrot_answer.md` and appends the conversation to the existing `ping-pongings/knowledge-base/barrot_memory.jsonl` memory file.

## Configuration

Defaults:
- `BARROT_INFERENCE_PROVIDER=local_llama`
- `LOCAL_LLAMA_BASE_URL=http://127.0.0.1:8081/v1`
- `LOCAL_LLAMA_MODEL=local`

Override these environment variables only when the server configuration changes.

## Capability boundary

The local Llama 3.2 1B model is intended for lightweight local chat, short summaries, classification, and transformations. It is not the default for complex XRP research or repository tool execution. The GitHub Actions runtime cannot access the phone's loopback endpoint. Existing cloud inference selection remains unchanged when `BARROT_INFERENCE_PROVIDER` is not explicitly set to `local_llama`.

Keep the llama.cpp context at 2048 and generation threads at 4 unless Sean explicitly authorizes a change. Do not expose the local server to the public internet.
