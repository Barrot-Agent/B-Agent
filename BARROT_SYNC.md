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
- Last sync: 2026-11-11T03:24Z; main `84f28ee`; #1661 current branch head `d58a6fa` (code head `c12ae0b` passed exact-head PR and push suites: 3,388 passed, 8 subtests, 59.89%; six dependency manifests audited, zero known vulnerabilities; fail-closed gate passed). Current diff: 976 files / 44 workflows / 932 other paths; 1,972 ahead, zero behind. Rechecked 17 source-PR tips: all still contain `.config/gh/hosts.yml`; main and successor do not. Main says OAuth REVOKED, not independently verified. Coinbase/Circle equity and USDC revenue-sharing, Ripple issuer RLUSD reserves and chain activity have been reconciled in the canonical handoff. This docs correction will trigger fresh exact-head CI.
- Next task: Complete semantic review of 932 non-workflow paths; resolve branch-protection/approval and Pages-publication authorization; coordinate safe handling of the 17 source-branch credential-path copies without reading contents or rewriting history; restore safe V3 parity; keep XRP forecasts NOT_ISSUED.

## Conversation Log
- 2026-11-10: User + ChatGPT established LunaRoute as sole brain, Orbit ditched.
