# GitHub Activity Consolidation

`scripts/consolidate_github_activity.py` collects repository-visible activity into
one JSON document while preserving the source type, URL, actor, timestamp, and
issue or pull-request number for each record.

## Usage

From the repository root:

```bash
export GITHUB_TOKEN="your-read-only-token"
python scripts/consolidate_github_activity.py \
  --repository Barrot-Agent/B-Agent \
  --output brain_corpus/github_activity.json
```

The token is optional for public repositories, but authenticated requests have
higher GitHub API rate limits. A read-only token is sufficient.
Very large repositories may still require multiple runs because GitHub can
apply secondary rate limits to high-volume API access.

The export includes commits, issues, pull requests, issue comments, pull-request
reviews, and pull-request review comments. It is safe to regenerate because it
replaces only the specified output file.

GitHub's repository API exposes project activity, not private agent conversation
transcripts. Those transcripts can only be included if the agent platform
publishes them as repository-visible artifacts or provides a separate export.
