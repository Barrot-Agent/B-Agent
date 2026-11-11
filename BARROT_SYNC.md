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
- Last sync: 2026-11-11T04:40Z; main `84f28ee7755607236231545a14f3d093c1baaa85`; active successor #1661 on `integration/xrp-v3-unified-main-20261111`; code/test head `e97f14faf70d5db7426f281218e965d53e7eb765`; latest canonical handoff commit `713d6df03e96ef127908450c638fd86bfcc004d0`. Exact-head core tests passed; full repository suite still running in PR CI 42960200400. PR dependency audit 42960200717 and fail-closed gate 42960200349 passed. Main/successor trees verified; 17 other open PR tips still contain `.config/gh/hosts.yml` (tree metadata only); OAuth revocation is repository-reported, not independently verified. Fresh XRP market, options, derivatives, exchange-flow, ETF disagreement, Circle/SBI ownership and Coinbase/Ripple RLUSD evidence added to the canonical handoff. Forecast remains `NOT_ISSUED`.
- Next task: Complete exact-head full-suite CI on `e97f14f`; then finish semantic review of 934 non-workflow paths, resolve credential-branch remediation with the owner, obtain authoritative branch-protection/approval and Pages-publication authorization, restore safe Barrot V3 operational parity, and only then consider #1661 for merge. Keep #1660 and unique PRs open until verified successor merge; keep XRP forecasts disabled.

## Conversation Log
- 2026-11-10: User + ChatGPT established LunaRoute as sole brain, Orbit ditched.
