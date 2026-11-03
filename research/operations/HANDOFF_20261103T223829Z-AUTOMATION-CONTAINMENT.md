# Fresh-main automation containment handoff

Captured: 2026-11-03T22:38:29Z  
Repository: Barrot-Agent/B-Agent  
Inspected main: `8007440e08a40608c119e48b7f8fa4e189175280`  
Branch: `security/automation-containment-8007440e-20261103T2238Z`

## Scope

Eight workflow quarantines and one inert exporter replacement:
- Scheduler Tick: disables arbitrary workflow dispatch and direct queue writes to main.
- Subscriber Sync: stops the hourly Gumroad email-hash export to the public repository.
- Daily Digest, Auto Resolve Issues, Autonomous Resolver and Self Schedule: stop unattended public issue creation, assignment, comments and closure.
- Merge Queue: disables broad automatic branch updates, merges and branch deletion.
- Dump Brain Corpus: disables the Databricks export workflow and makes its script inert.

## Data preservation

Existing `brain_corpus/dump.json` and `brain_corpus/dump.md` are deliberately retained unchanged. Their contents were not inspected, copied or deleted. The exporter is disabled pending classification and an approved non-public destination. This proposal does not erase Git history, forks, caches or external copies.

The subscriber export was previously observed as empty in the current tree; prior public history has not been fully audited.

## Verification

Four regression tests are appended to `tests/test_v3_scripts.py`, which is explicitly included in core CI. Exact-head CI and the fail-closed gate remain pending.

## Residual audit

Separate scheduled writers remain for a later fresh-main proposal: autonomous self-deployment, cognitive PingPong, transparency audit, Riemann harvest, WebMCP sandbox and monetization enrichment. External Kaggle, Hugging Face and Cloudflare actions also need protection. `hover_bike_updates.yml` and manual Databricks token rotation remain separate reviews.

## Safety

Draft branch only. No main modification, merge, force-push, workflow dispatch, credential access, external deployment, data export, paper trade or real-money transaction.
