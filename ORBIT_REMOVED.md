# Orbit Permanently Retired

**Status:** Discontinued. Confirmed by Sean on 2026-11-18.

GitLab Orbit was a seven-day trial integration. It is not part of Barrot's active architecture and must not block development, testing, deployment, or XRP intelligence work.

## Permanent operating rule

- Do not require a GitLab Orbit account, subscription, credits, token, CLI, MCP server, API, or skill.
- Do not install or restore `.agents/skills/orbit`.
- Do not invoke `glab orbit` or add Orbit to startup, orchestration, CI, workflows, or required environment variables.
- Do not wait for Orbit access or ask Sean to renew it.
- Treat any remaining Orbit-specific code as obsolete and remove it only after confirming its callers and tests; preserve unrelated GitLab functionality.
- Reintroduce Orbit only if Sean explicitly authorizes it and independently restores the required account access.

## Provider configuration

This file does not select or authorize a replacement LLM provider. The current runtime/provider source of truth is `BARROT_SYNC.md` and the active Barrot configuration. Do not infer that the historical LunaRoute settings below remain active.

## Historical record

Orbit was retired on 2026-11-10 after trial credits were exhausted. This record was updated on 2026-11-18 to make the no-account/no-dependency rule explicit.

No Orbit credentials are required for Barrot.
