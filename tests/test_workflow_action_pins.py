from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEWED_WORKFLOWS = (
    ".github/workflows/barrot-ops.yml",
    ".github/workflows/capability-10-design.yml",
    ".github/workflows/capability-discovery.yml",
    ".github/workflows/coinbase-paper-trader.yml",
    ".github/workflows/cross-analysis.yml",
    ".github/workflows/data-value-triage.yml",
    ".github/workflows/deploy-a2a-worker.yml",
    ".github/workflows/financial-data-refresh.yml",
    ".github/workflows/formal-verification-benchmarks.yml",
    ".github/workflows/frontier-digest.yml",
    ".github/workflows/hover_bike_updates.yml",
    ".github/workflows/money-audit.yml",
    ".github/workflows/money-bounty-scan.yml",
    ".github/workflows/money-mcp-listing.yml",
    ".github/workflows/paid-issue-hunter.yml",
    ".github/workflows/research-topics.yml",
    ".github/workflows/riemann-harvest.yml",
    ".github/workflows/signal-summary.yml",
    ".github/workflows/sync-self-hosted-brain.yml",
    ".github/workflows/webmcp-monetization-enrich.yml",
    ".github/workflows/webmcp-trend-digest.yml",
    ".github/workflows/ci.yml",
    ".github/workflows/dependency-audit.yml",
    ".github/workflows/xrp-public-ingestion.yml",
)
APPROVED_ACTION_SHAS = {
    "actions/checkout": "3d3c42e5aac5ba805825da76410c181273ba90b1",
    "actions/setup-python": "6d4fd22b20465ccc0f7354476588e8df7c9ca0e0",
    "actions/upload-artifact": "cf430e030ddbb5b0abf93d22962f4752f3646cd9",
    "actions/download-artifact": "9000827ccba6bdab643e8b6fd33ac0654aef8333",
    "actions/jekyll-build-pages": "44a6e6beabd48582f863aeeb6cb2151cc1716697",
    "actions/cache/restore": "0057852bfaa89a56745cba8c7296529d2fc39830",
    "actions/cache/save": "0057852bfaa89a56745cba8c7296529d2fc39830",
    "cloudflare/wrangler-action": "953926a2e2182532811c01a25e53647d93bf07c0",
    "databricks/setup-cli": "9625fdde9ba2607df0087e0d3ec7449198bf2180",
}
ACTION_LINE = re.compile(r"^\s*(?:-\s*)?uses:\s*(?P<reference>\S+)(?:\s+#\s*(?P<annotation>.*))?$")


def test_reviewed_workflows_use_only_approved_immutable_action_commits():
    for relative_path in REVIEWED_WORKFLOWS:
        workflow = (ROOT / relative_path).read_text(encoding="utf-8")
        references = [
            (number, match)
            for number, line in enumerate(workflow.splitlines(), start=1)
            if (match := ACTION_LINE.match(line))
        ]
        assert references, relative_path

        for number, match in references:
            reference = match.group("reference")
            if reference.startswith("./"):
                continue
            assert "@" in reference, (relative_path, number, reference)
            repository, revision = reference.rsplit("@", 1)
            assert repository in APPROVED_ACTION_SHAS, (relative_path, number, repository)
            assert re.fullmatch(r"[0-9a-f]{40}", revision), (relative_path, number, reference)
            assert revision == APPROVED_ACTION_SHAS[repository], (relative_path, number, reference)
            assert match.group("annotation"), (relative_path, number, "missing release annotation")
