"""Keep the staged Product Foundry pack's own unittest suite in repository CI."""

from pathlib import Path
import subprocess
import sys


def test_staged_product_pack_unittest_suite():
    repository_root = Path(__file__).resolve().parents[1]
    deliverables = (
        repository_root
        / "products"
        / "github-pr-template-pack-self-guided"
        / "deliverables"
    )

    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=deliverables,
        text=True,
        capture_output=True,
        check=False,
    )

    output = result.stdout + result.stderr
    assert result.returncode == 0, output
    assert "OK" in result.stderr, output
