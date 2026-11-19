# Nine-platform capability, authentication, permissions and data flow

**Observation cutoff:** 2026-11-04T21:26:00Z

| Platform | Current evidence | Authentication / permission status |
|---|---|---|
| ChatGPT | Current session and GitHub connector used for repository reads and existing PR-branch writes | Authenticated GitHub connector; no main write, merge or deployment |
| Claude | Public documentation only | No authenticated session/API flow verified |
| Grok (xAI) | Public search only | No xAI authentication verified; Groq is a separate provider |
| Gemini | Public documentation only | No authenticated session/API flow verified |
| Copilot | GitHub PR review comments/events observed | Review event only; no persistent chat/API or write flow verified |
| Codex | No separate Codex execution observed | No API/CLI authentication verified |
| Hugging Face | Prior public Space probe reached endpoint and returned `BUILD_ERROR` | Public read only; no token, restart or upload |
| Kaggle | No authenticated API/notebook execution observed | No credentials, upload or submission |
| Databricks | Prior workspace/API probe returned HTTP 403 | No successful SQL or job flow; no PAT rotation |

## Verified data flow

**ChatGPT session → authenticated GitHub connector → existing Barrot PR branches → GitHub CI/review evidence → ChatGPT.**

The connector successfully read the main tree, open PR inventory and PR reviews, then updated existing integration/research PR branches. It did not write main, merge, deploy, rotate secrets, restart Spaces, submit Kaggle entries, or run Databricks jobs.

Copilot review comments are repository evidence, not proof of a persistent agent-to-agent connection. Barrot's Groq integration does not establish Grok/xAI access. Hugging Face public endpoint reachability does not establish authenticated Space management.

## Permission boundary

- Verified: ChatGPT session + GitHub connector read/write to existing PR branches.
- Review-only evidence: Copilot PR review events.
- Public read only: Hugging Face Space status.
- Blocked: Databricks, last probe HTTP 403.
- Unverified: Claude, Grok/xAI, Gemini, Codex and Kaggle.
- No credentials exposed, no new scopes requested, no external platform write or transfer performed.

**Status: PARTIAL.** Do not claim nine-platform coordination until each platform has tested authentication, explicit permission scope and a verified data path. Continue local deterministic work when a provider is blocked.
