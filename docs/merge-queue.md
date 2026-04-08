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
