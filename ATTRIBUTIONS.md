# ATTRIBUTIONS

Every pulled component is listed here with its repository, commit, licence and local
path. Nothing is copied without a permitted licence; GPL, AGPL, unlicensed and
NOASSERTION repositories are refused by `scripts/pull_components.py` and recorded in
`data/harvest/components.json`.

## Vendored workflow patterns

| Local file | Source | Commit | Licence | What it contributed |
|---|---|---|---|---|
| vendor/workflow-patterns/pytest-matrix.yml | Panniantong/Agent-Reach (.github/workflows/pytest.yml) | c70ae6da | MIT | python-version matrix with a macos include and fail-fast false |
| vendor/workflow-patterns/concurrency-paths-ignore.yml | D4Vinci/Scrapling (.github/workflows/code-quality.yml) | 2998c9eb | BSD-3-Clause | workflow-level concurrency group and paths-ignore so doc edits skip CI |
| vendor/workflow-patterns/mcp-registry-publish.yml | upstash/context7 (.github/workflows/mcp-registry.yml) | c36522f3 | MIT | OIDC publish flow: server.json, mcp-publisher, version stamping |

Each file keeps its licence header and full commit URL. They are reference copies,
not executed by this repository.

## Ideas adapted without copying code

- The three money workflows in `.github/workflows/` were written for this repository.
  They reuse the patterns above (matrix shape, concurrency, registry prerequisites)
  rather than the source files.

## Refused due to licence

10 of 33 scanned repositories were refused. Recorded in
`data/harvest/workflows.json` under `license_status: BLOCKED-LICENSE`:

| Repository | Licence |
|---|---|
| n8n-io/n8n | NOASSERTION |
| langgenius/dify | NOASSERTION |
| donnemartin/system-design-primer | NOASSERTION |
| awesome-selfhosted/awesome-selfhosted | NOASSERTION |
| firecrawl/firecrawl | AGPL-3.0 |
| NaiboWang/EasySpider | AGPL-3.0 |
| koala73/worldmonitor | AGPL-3.0 |
| freqtrade/freqtrade | GPL-3.0 |
| wilsonfreitas/awesome-quant | NONE |
| paperswithbacktest/awesome-systematic-trading | NONE |

No content was read from those repositories beyond the licence field and the
workflow file list needed to classify them.
