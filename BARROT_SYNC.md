# BARROT SYNC - Single Source of Truth
# This file is the shared brain-state between Termux Barrot (LunaRoute) and GPT Barrot.
# BOTH must read this before answering. BOTH must update this after any change.

## Identity
- Brain: LunaRoute ONLY - https://gw.lunaroute.com/v1 - lunaroute/glm-5.3-flash
- Canonical Barrot: Termux ~/barrot/Barrot-Agent via b_agent.py
- Relay Barrot: GPT Project (ChatGPT) - NEVER claims to be LunaRoute brain
- Repo: github.com/Barrot-Agent/B-Agent, branch main

## Hard Rules
- Do NOT re-add Orbit. Commit 71cdd8b. ORBIT_REMOVED.md exists.
- Do NOT touch Orbitron font in hf_space/app.py
- Do NOT use password auth. GH_TOKEN via x-access-token only.
- Do NOT re-commit .config/gh/hosts.yml - OAuth REVOKED

## Last State
- GitHub main: 84f28ee Add BARROT_SYNC.md - shared state for Termux + GPT.
- GitHub Orbit-removal commit: 64dc43b Ditch Orbit. The Termux-side reference 71cdd8b remains recorded above; its equivalence to the GitHub commit is not verified.
- Last sync: 2026-11-11T03:59Z; main `84f28ee7755607236231545a14f3d093c1baaa85`; sole successor PR #1661 remains draft on `integration/xrp-v3-unified-main-20261111`. Before the current test-contract correction, head was `77d293cbcad5b67dfe9d336f1213a7e896dff82c`, 1,975 ahead and zero behind. Exact-head full CI 42955322582 reported 3,372 passed, 21 failed, 8 subtests, 59.89% coverage. The 21 failures are stale tests expecting schema 1.0 historical keys from the new schema 1.1 current-map artifact; production-code failure was not identified. Core tests passed; dependency audit 42955322616 and fail-closed gate 42955322567 passed. The existing branch's two historical test contracts are being aligned to schema 1.1 while keeping the separate schema 1.0 historical archive checks. Fresh exact-head CI is required. Main `BARROT_SYNC.md` reports OAuth REVOKED, but provider-side revocation remains independently unverified. Forecast remains NOT_ISSUED.
- Next task: Complete semantic review of 932 non-workflow paths; resolve branch-protection/approval and Pages-publication authorization; coordinate safe handling of the 17 source-branch credential-path copies without reading contents or rewriting history; restore safe V3 parity; keep XRP forecasts NOT_ISSUED.

## Conversation Log
- 2026-11-10: User + ChatGPT established LunaRoute as sole brain, Orbit ditched.
