# Integrated automation containment handoff

Captured: 2026-11-04 01:03 UTC  
Repository: \`Barrot-Agent/B-Agent\`  
Fresh-main base: \`0b6005dcb714f794d120b95d7412a0814d006221\`

## Mission

XRP intelligence and prediction-engine mastery remains the top Barrot mission. Barrot V3 remains the execution, safety and verification foundation.

## Live-main evidence

- Main was \`0b6005dcb714f794d120b95d7412a0814d006221\` at inspection.
- Scheduler Tick run [41749988225](https://github.com/Barrot-Agent/B-Agent/actions/runs/41749988225) completed. Its log reported zero queue entries fired and one total queued, but the workflow still has \`contents: write\`, \`actions: write\`, arbitrary workflow dispatch, and a direct main-branch commit path.
- Subscriber Sync run [41749182476](https://github.com/Barrot-Agent/B-Agent/actions/runs/41749182476) reported zero active subscribers hashed. The main workflow nevertheless reads Gumroad sale email fields and writes hashes to public \`web/subscribers.json\`.
- Cross Analysis run [41749976015](https://github.com/Barrot-Agent/B-Agent/actions/runs/41749976015) completed its commit path. Main's latest commit at inspection was a Cross-analysis refresh.
- Autonomous Resolver run [41751128042](https://github.com/Barrot-Agent/B-Agent/actions/runs/41751128042) completed. Existing issue records caused issue creation to be skipped; no \`COPILOT_ASSIGNEE\` variable was configured.
- Main's Merge Queue supports \`mode=all\` and can update branches and merge every open PR when manually dispatched with dry-run disabled.
- Main's brain-corpus workflow queries Databricks and commits full output into the public repository.

## Proposed containment

This branch is based on the exact current main SHA and combines reviewed source changes from #1613, #1615 and #1617:

- Quarantine Scheduler Tick, Subscriber Sync, Merge Queue, public brain export, Daily Digest, Self-Scheduling, Auto-Resolve Issues, Autonomous Resolver, legacy signal-accuracy scoring, Cognitive PingPong and Autonomous Self-Deployment.
- Keep Cross Analysis useful as a read-only workflow that uploads bounded artifacts instead of committing to main.
- Make \`scripts/dump_brain_corpus.py\` inert; do not delete historical dumps or rewrite Git history.
- Add dedicated regression tests and explicitly register them in core CI.
- Preserve all unrelated current-main generated telemetry and XRP research files.

## Additional risks not included in this patch

- \`force-deploy-space.yml\` force-pushes to the Hugging Face Space.
- \`barrot-hf-admin.yml\` performs repository DELETE/POST operations.
- \`rotate-databricks-token.yml\` accepts a Databricks PAT through a workflow input and then stores it as a secret.
- \`gumroad-metrics.yml\` is scheduled with repository write permission and a Gumroad token.
- \`barrot-self-upgrade.yml\` has repository and PR write permissions and a Groq credential.
- \`barrot-merge.yml\` uploads a merged model to Hugging Face.
- \`deploy-databricks.yml\` and \`sync-huggingface.yml\` contain explicit per-run confirmation inputs and are not modified here.

## Safety and verification

- Designed: yes.
- Executed: proposed files assembled on an isolated new branch.
- Exact-head CI: pending.
- Fail-closed gate: pending.
- Main modified: no.
- Merge: not performed.
- Force-push: not performed.
- External deployment or secret access: not performed.

## Next actions

1. Verify this exact branch head through CI and the fail-closed gate.
2. Audit and contain the additional external writers listed above.
3. Reconcile the stale source PRs only after the integrated successor passes.
4. Continue the point-in-time XRP feature store, exchange-native data reconciliation and leakage-safe walk-forward evaluation.
