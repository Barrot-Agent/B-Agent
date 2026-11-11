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
- Last sync: 2026-11-11T04:18:03Z; main `84f28ee7755607236231545a14f3d093c1baaa85`; active successor #1661 on `integration/xrp-v3-unified-main-20261111`, pre-update head `92f074e8bd7941bfe40c40a13e5c9ce5444cb5eb`, 1,979 ahead and zero behind. Exact-head full repository suite passed 3,397 tests, zero failures, eight subtests, 59.89% coverage on both PR run 42957736027 and push run 42957728782; wheel build and installed primary-mission verification passed. Dependency audit: six manifests, zero known vulnerabilities; fail-closed gate passed. Main CI passed on exact SHA. Cache is read-only due budget; warning only. Run12G adds ASK Coin candidate separation, official Tokyo SBIC/ChatGPT training evidence, Kamilah YouTube identity gate, and Alpha Finance/CryptoKeyhole ETF coverage disagreement. ETF flows remain model-ineligible. CI push is now restricted to main; pull_request retains full-suite exact-head verification. OAuth revocation is repository-reported, not independently verified. Forecast remains NOT_ISSUED.
- Next task: Complete semantic review of 932 non-workflow paths; resolve branch-protection/approval and Pages-publication authorization; coordinate safe handling of the 17 source-branch credential-path copies without reading contents or rewriting history; restore safe V3 parity; keep XRP forecasts NOT_ISSUED.

## Conversation Log
- 2026-11-10: User + ChatGPT established LunaRoute as sole brain, Orbit ditched.
