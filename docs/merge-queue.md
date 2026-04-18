# Merge Queue Workflow

The **Merge Queue** workflow (`merge-queue.yml`) sequentially updates and merges open pull requests in this repository. It is triggered manually via `workflow_dispatch`.

## Inputs

| Input | Type | Default | Description |
|---|---|---|---|
| `mode` | `label` \| `all` | `label` | Processing mode (see below) |
| `label` | string | `merge-queue` | Label to filter PRs; only used when `mode=label` |
| `max_prs` | number | `0` | Maximum PRs to process per run (`0` = unlimited) |
| `dry_run` | `true` \| `false` | `false` | Report what would happen without making changes |
| `merge_method` | `squash` \| `merge` \| `rebase` | `squash` | Merge method used when merging a ready PR |

## Modes

### `mode=label` (default – recommended)

Only PRs that carry the label specified in the `label` input are processed.

```
label: merge-queue   ← default; change to any label you use
```

This is the **safe default**. You control exactly which PRs enter the queue by adding the label to them.

### `mode=all`

> ⚠️ **DANGER – read this before using `mode=all`**
>
> When `mode=all` is selected the workflow processes **every open pull request in the repository**, sorted by PR number ascending. The `label` input is ignored.
>
> Only use `mode=all` when:
>
> - You are certain that **all open PRs** are safe to merge (or safe to attempt)
> - Your branch protection rules, required checks, and review requirements are already enforced
> - You understand that PRs that are not yet ready (failing checks, conflicts, required reviews) will be **skipped with a comment** but the workflow will still attempt to update their branches
>
> **Do not use `mode=all` if:**
> - You have PRs from unknown contributors that have not been reviewed
> - You have experimental or work-in-progress PRs open
> - You are unsure which PRs are ready to be merged

## Authentication

The workflow uses the `GH_PAT` Actions secret for all GitHub API calls and merges.

**Classic personal access token** – requires the `repo` scope.

**Fine-grained personal access token** – requires repository permissions:
- `Contents: Read and write` (to push branch updates)
- `Pull requests: Read and write` (to merge PRs and post comments)

Configure the secret in **Settings → Secrets and variables → Actions → `GH_PAT`**.

## Behavior

For each PR selected by the chosen mode:

1. **Fetch PR status** (mergeable, merge state, branch info)
2. **Update branch** – if the PR branch is behind the base branch (`BEHIND` or `UNKNOWN` state), the workflow calls the GitHub "update branch" API to merge the base into the PR branch
3. **Skip if not ready** – if after updating the PR is still not in a `CLEAN`/`MERGEABLE` state (e.g., failing required checks, unresolved conflicts, pending reviews), it is skipped and a comment is posted on the PR
4. **Merge** – using the configured `merge_method`; the head branch is deleted after a successful merge
5. **Repeat** for the next PR (ascending PR number order)

## Examples

### Trigger via GitHub UI

Go to **Actions → Merge Queue → Run workflow** and fill in the inputs.

### Trigger via GitHub CLI

```bash
# Process only PRs labelled 'merge-queue' (default)
gh workflow run merge-queue.yml \
  -f mode=label \
  -f label=merge-queue \
  -f merge_method=squash

# Dry run – see what would be merged without changing anything
gh workflow run merge-queue.yml \
  -f mode=label \
  -f dry_run=true

# Process ALL open PRs (use with caution)
gh workflow run merge-queue.yml \
  -f mode=all \
  -f merge_method=squash
```

## Merge methods

| Method | Description |
|---|---|
| `squash` | All commits in the PR are squashed into a single commit on the base branch. Recommended for keeping a clean history. |
| `merge` | A merge commit is created. The full PR commit history is preserved. |
| `rebase` | PR commits are replayed on top of the base branch. No merge commit; linear history. |
The `merge-queue.yml` workflow provides a **sequential, label-gated merge queue** for this repository.  
It is manually triggered and processes open pull requests one at a time: updating the PR branch with `Main`, waiting for required checks, and then merging.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Required Secret – GH_PAT](#required-secret--gh_pat)
3. [Label Gating](#label-gating)
4. [Running the Workflow](#running-the-workflow)
5. [Workflow Inputs](#workflow-inputs)
6. [How It Works](#how-it-works)
7. [Skipped PRs and the `merge-queue:blocked` Label](#skipped-prs-and-the-merge-queueblocked-label)
8. [Unblocking a PR](#unblocking-a-pr)
9. [Security and Permissions](#security-and-permissions)

---

## Prerequisites

| Requirement | Details |
|---|---|
| GitHub Actions enabled | Must be enabled for the repository |
| `GH_PAT` Actions secret | A Personal Access Token with `repo` scope (see below) |
| Label `merge-queue` | Created automatically on first run; add it to PRs you want processed |

---

## Required Secret – GH_PAT

The workflow uses a **Personal Access Token (PAT)** stored as the Actions secret `GH_PAT`.

### Why a PAT instead of `GITHUB_TOKEN`?

`GITHUB_TOKEN` cannot trigger additional workflow runs, is restricted from merging into branch-protected branches in some configurations, and cannot push to PR branches owned by other users.  
A PAT with `repo` scope bypasses these limitations.

### Creating and adding the secret

1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens** (or Classic tokens).
2. Grant the token **`repo`** scope (full repository access) — or for fine-grained tokens: `Contents: Write`, `Pull requests: Write`, `Checks: Read`.
3. Copy the token value.
4. In the repository: **Settings → Secrets and variables → Actions → New repository secret**.
   - **Name:** `GH_PAT`
   - **Value:** paste the token

> **Fallback:** If `GH_PAT` is not set, the workflow silently falls back to `GITHUB_TOKEN` for read operations, but **write operations (push, merge) may fail**.

---

## Label Gating

Only PRs that carry the configured label (default: `merge-queue`) are processed.  
This prevents the workflow from accidentally merging PRs that are not ready.

### Adding the label to a PR

```bash
gh pr edit <PR_NUMBER> --add-label "merge-queue"
```

Or use the GitHub UI: open the PR → right panel → **Labels** → add `merge-queue`.

---

## Running the Workflow

1. Go to **Actions → Merge Queue** in the repository.
2. Click **Run workflow**.
3. Fill in the inputs (or keep defaults).
4. Click **Run workflow** to start.

> ℹ️ **Always do a dry run first** (`dry_run: true`, the default) to see which PRs would be processed and why some might be skipped — before committing to an actual merge run.

---

## Workflow Inputs

| Input | Default | Description |
|---|---|---|
| `label` | `merge-queue` | Only PRs with this label are processed |
| `max_prs` | `100` | Maximum number of PRs to process per run |
| `dry_run` | `true` | When `true`, no branches are pushed and no PRs are merged — only reports what *would* happen |
| `merge_method` | `squash` | Merge method: `squash`, `merge`, or `rebase` |

### Merge method comparison

| Method | Result on `Main` | Best for |
|---|---|---|
| `squash` | One commit per PR | Noisy/many commits in PR; clean history preferred |
| `merge` | Merge commit + all PR commits | Preserving full PR commit history |
| `rebase` | PR commits replayed linearly | Linear history with per-commit granularity |

---

## How It Works

For each PR (in ascending PR number order, up to `max_prs`):

1. **Fetch PR details** — title, head branch, mergeability, merge state, review decision.
2. **Skip fork PRs** — the workflow cannot push to fork branches.
3. **Check for conflicts** — if `CONFLICTING` or `DIRTY`, comment + label + skip.
4. **Check for pending review changes** — if reviewers requested changes, skip.
5. **Update branch** — merge `Main` into the PR branch:
   - First tries the GitHub API `PUT /repos/{repo}/pulls/{number}/update-branch` endpoint.
   - Falls back to `git fetch / checkout / merge / push` if the API call fails.
6. **Poll required checks** — waits up to **45 minutes** (polling every 30 seconds) for all CI checks on the new head SHA to complete.
7. **Re-check mergeability** — after checks pass, verifies the PR is still mergeable.
8. **Merge** — using the selected method with `--delete-branch` (retries without branch deletion if the branch is protected).
9. **Write summary** — a Markdown summary is written to the job's Summary page listing all merged and skipped PRs.

---

## Skipped PRs and the `merge-queue:blocked` Label

When a PR cannot be processed, the workflow:

1. Posts a comment on the PR explaining the reason (e.g., conflicts, failing checks, changes requested).
2. Applies the `merge-queue:blocked` label to the PR.

The label is created automatically (color: red/`#d93f0b`) on the first run if it does not exist.

### Reasons a PR may be skipped

| Reason | How to fix |
|---|---|
| **Fork branch** | Update the branch from your fork manually and re-add `merge-queue` |
| **Merge conflicts** | Resolve conflicts locally, push, then re-add `merge-queue` |
| **Changes requested** | Address reviewer feedback, get approval, then re-add `merge-queue` |
| **Branch update failed** | Resolve the conflict that prevented the automated update |
| **Checks failed / timed out** | Fix CI failures; the workflow will retry on next run once `merge-queue` label is re-added |
| **Not mergeable (BLOCKED)** | Usually means branch protection rules are unsatisfied — check required reviews / checks |
| **Merge command failed** | Check the comment body for the exact error; may be a transient API issue |

---

## Unblocking a PR

1. **Identify the reason** from the workflow comment on the PR.
2. **Fix the issue** (resolve conflicts, get reviews, fix CI, etc.).
3. **Remove the `merge-queue:blocked` label** (optional — the workflow will remove it automatically when it successfully processes the PR):
   ```bash
   gh pr edit <PR_NUMBER> --remove-label "merge-queue:blocked"
   ```
4. **Re-add the `merge-queue` label** so the PR is picked up on the next run:
   ```bash
   gh pr edit <PR_NUMBER> --add-label "merge-queue"
   ```
5. **Trigger the workflow** again (Actions → Merge Queue → Run workflow).

---

## Security and Permissions

The workflow requests only the minimum required permissions:

```yaml
permissions:
  contents: write        # push branch updates, delete merged branches
  pull-requests: write   # post comments, add/remove labels, merge PRs
  checks: read           # read check-run results
  statuses: read         # read commit statuses
```

The workflow is only triggerable via `workflow_dispatch` (manual), so it never runs automatically without explicit human intent.  
Use the `label` input together with label gating to further restrict which PRs are processed.
