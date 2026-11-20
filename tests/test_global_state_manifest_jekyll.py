import re
from pathlib import Path


def test_global_state_manifest_liquid_tokens_are_guarded_by_raw_blocks():
    manifest = Path(__file__).resolve().parents[1] / "GLOBAL_STATE_MANIFEST.md"
    lines = manifest.read_text(encoding="utf-8").splitlines()
    in_raw = False
    raw_blocks = 0

    for number, line in enumerate(lines, start=1):
        marker = line.strip()
        if marker == "{% raw %}":
            assert not in_raw, f"nested raw block at line {number}"
            in_raw = True
            raw_blocks += 1
            continue
        if marker == "{% endraw %}":
            assert in_raw, f"unmatched endraw at line {number}"
            in_raw = False
            continue
        if any(token in line for token in ("{{", "}}", "{%", "%}")):
            assert in_raw, f"unprotected Liquid token at line {number}"

    assert not in_raw, "unterminated Liquid raw block"
    assert raw_blocks == 2


def test_ci_validates_pages_build_on_pull_requests_without_deployment():
    workflow = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml"
    text = workflow.read_text(encoding="utf-8")
    assert "  pages-build:" in text
    assert "if: github.event_name == 'pull_request'" in text
    assert re.search(r"(?m)^\s+uses: actions/jekyll-build-pages@[0-9a-f]{40} # v1\s*$", text)
    config = Path(__file__).resolve().parents[1] / "_config.yml"
    config_text = config.read_text(encoding="utf-8")
    assert re.search(r"(?m)^\s*-\s*GLOBAL_STATE_MANIFEST\.md\s*$", config_text)
    assert "test -s ./GLOBAL_STATE_MANIFEST.md" in text
    assert "test ! -e ./_site/GLOBAL_STATE_MANIFEST.html" in text
    assert "test ! -e ./_site/GLOBAL_STATE_MANIFEST.md" in text
    assert "actions/deploy-pages" not in text
    assert "upload-pages-artifact" not in text
