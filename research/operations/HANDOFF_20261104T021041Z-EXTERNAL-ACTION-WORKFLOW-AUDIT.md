# Barrot external-action workflow audit

Captured: 2026-11-04T02:10:41Z
Current main base: 162f43d29970db9abebfec1b7872601a9d659037
Source containment proposal: PR #1620
Status: proposed controls; no main changes or external actions performed.

## Critical findings

1. force-deploy-space.yml used git push -f with an HF token and no per-run confirmation. The proposal disables this path; sync-huggingface.yml is the non-force, explicitly confirmed alternative.
2. barrot-hf-admin.yml performed a Hugging Face repository DELETE followed by POST creation with no confirmation. It is disabled.
3. rotate-databricks-token.yml accepted a PAT in workflow_dispatch input and passed it to gh secret set, then triggered deployment. Workflow inputs are not a secret channel. It is disabled.
4. gumroad-metrics.yml had a weekly schedule, repository write permission and a public-main commit. Its script uses the products endpoint and intends aggregate-only fields, but prints the full product response to logs. It is disabled pending allowlisted output and artifact-only storage.

## Gated operations

- Self-upgrade: requires explicit YES and a main-ref run; it may create a review-only candidate branch/PR but does not merge.
- Model upload: requires explicit YES, validates the model suffix through an environment variable, and removes --trust-remote-code. A model requiring remote custom code will fail closed.
- Factory restart: requires explicit YES before the HF token is exposed to the job.
- Duplicate model-upload workflow: disabled; one gated entry point remains.

## Controls preserved

- Databricks deployment and Hugging Face sync already require explicit per-run YES confirmation.
- Controlled PR approval validates the exact head SHA and records a reason; it applies an audit label/comment only and does not submit a GitHub review or merge.
- The integrated containment changes quarantine scheduled repository writers, unrestricted merge queue, public brain export and other autonomous writers; Cross Analysis remains read-only/artifact-only.

## Research and prediction boundary

This workflow audit is separate from the XRP forecast engine. It does not issue a market prediction. The XRP research PR records 60 sources, 43 observations, 33 relationship edges and 13 competing hypotheses; the unresolved phrase actual capital remains an explicitly unsupported unknown. No live collaboration is claimed for the eight external AI/data platforms.

## Verification

Exact-head CI and fail-closed gate are pending for this proposed successor. No merge, main write, force-push, secret access, deployment, token rotation, Space restart, model upload, paper trade or real-money transaction was performed.
