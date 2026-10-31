from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (ROOT / ".github" / "workflows" / "xrp-ledger-validation.yml").read_text(encoding="utf-8")


def test_xrp_ledger_validator_is_read_only_and_branch_scoped():
    assert "permissions:\n  contents: read" in WORKFLOW
    assert "contents: write" not in WORKFLOW
    assert "actions: write" not in WORKFLOW
    assert "secrets." not in WORKFLOW
    assert "GH_TOKEN" not in WORKFLOW
    assert "workflow_dispatch:" not in WORKFLOW
    assert "git push" not in WORKFLOW
    assert "gh workflow run" not in WORKFLOW
    assert "persist-credentials: false" in WORKFLOW
    assert "research/xrp-ledger-shard-migration-20261029T2210Z" in WORKFLOW
    assert "research/xrp-ledger-index-pointer-migration-20261028T1959Z" in WORKFLOW
    assert "research/xrp-ledger-index-pointer-migration\n" not in WORKFLOW


def test_xrp_ledger_validator_pins_test_runner_and_checks_actual_archive():
    assert "pytest==8.4.2" in WORKFLOW
    assert "scripts/validate_xrp_ledger_index.py --root ." in WORKFLOW
    assert "tests/test_xrp_ledger_index.py" in WORKFLOW
    assert "tests/test_xrp_exchange_balance_snapshot.py" in WORKFLOW
    assert "tests/test_sbic_identity.py" in WORKFLOW
    assert "actions/checkout@v7" in WORKFLOW
    assert "actions/setup-python@v7" in WORKFLOW
