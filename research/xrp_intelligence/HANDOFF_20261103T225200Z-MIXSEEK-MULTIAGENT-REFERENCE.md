# MixSeek reference architecture handoff

Captured: 2026-11-03T22:52:00Z

## Discovery
SBI Group's AlpacaTech subsidiary launched MixSeek in December 2025 as a multi-agent competition/orchestration platform. It explicitly supports ChatGPT/OpenAI, Gemini/Google, Claude/Anthropic and Grok/xAI. The platform runs parallel agents, round-based evaluation and an evaluator/leaderboard that selects a best output. It can run on Snowflake or cloud.

SBI's May 18, 2026 release describes MixSeek AI Data Lake, combining MixSeek with Anthropic financial-services agent skills and public Japanese disclosures (TDnet/EDINET). It supports enterprise PoCs using customer-owned ChatGPT/Codex, Claude or Gemini. This is an institutional reference for public-data research and multi-agent orchestration, not a Barrot connection.

## Open-source implementation review
Repository: https://github.com/mixseek/mixseek-core
- Default branch: develop
- Inspected commit: d62f638dd1a1a46759ff45544585f96158487a6e (2026-10-26)
- Version 0.1.0a22, Alpha, Apache-2.0, Python >=3.13.7
- Pydantic AI provider abstraction, Leader/Member hierarchy, round-based evaluation, parallel teams, DuckDB persistence, Streamlit UI and CLI.
- Provider API keys: OpenAI, Google/Vertex, Anthropic and xAI.
- Security: prompt-injection sanitization and path-traversal/error-handling tests; CI permissions contents:read.
- Anthropic CodeExecutionTool is an external execution/data-egress boundary requiring separate review.

## Fit to Barrot's nine platforms
Native model-provider support is verified for four: ChatGPT, Claude, Grok and Gemini. The related Data Lake release mentions customer-owned ChatGPT/Codex, Claude and Gemini, but that does not establish a standalone Codex adapter. No native Copilot, Hugging Face, Kaggle or Databricks adapter was verified. Snowflake/cloud is named; Databricks is not.

## Barrot design decision
Reuse the architectural ideas, not the winner-takes-all policy:
1. Parallel independent agents and explicit provider adapters.
2. Round-based challenge/rebuttal and durable submissions.
3. DuckDB-like run history and evaluation storage.
4. Add point-in-time evidence provenance, source independence, immutable feature snapshots and leakage controls.
5. Keep minority objections and counter-hypotheses; use independent fact-checking and red-team review.
6. Evaluate factual accuracy and out-of-sample model performance separately from LLM-judge scores.

Status: DESIGNED reference only. No MixSeek code imported, no external keys used, no code-execution tool invoked, and no B-Agent files changed.
