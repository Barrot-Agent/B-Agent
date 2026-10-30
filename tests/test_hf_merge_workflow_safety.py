from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = (
    ROOT / ".github" / "workflows" / "barrot-merge.yml",
    ROOT / ".github" / "workflows" / "barrot-merge-manual.yml",
)


def _step_block(content: str, step_name: str) -> str:
    marker = f"      - name: {step_name}"
    start = content.index(marker)
    next_step = content.find("\n      - name:", start + len(marker))
    return content[start:] if next_step == -1 else content[start:next_step]


def test_remote_code_merge_step_has_no_huggingface_credentials():
    for path in WORKFLOWS:
        content = path.read_text(encoding="utf-8")
        merge_step = _step_block(content, "Merge")
        assert "--trust-remote-code" in merge_step
        assert "HF_TOKEN" not in merge_step
        assert "HUGGINGFACE_HUB_TOKEN" not in merge_step
        assert "git-credentials" not in content
        assert "credential.helper store" not in content


def test_huggingface_token_is_scoped_to_upload_only():
    for path in WORKFLOWS:
        content = path.read_text(encoding="utf-8")
        upload_start = content.index("      - name: Upload")
        upload_step = _step_block(content, "Upload")
        assert "persist-credentials: false" in content
        assert "contents: read" in content
        assert "contents: write" not in content
        assert "secrets.HF_TOKEN" not in content[:upload_start]
        assert "HF_TOKEN: ${{ secrets.HF_TOKEN }}" in upload_step
        assert "HUGGINGFACE_HUB_TOKEN: ${{ secrets.HF_TOKEN }}" in upload_step


def test_duplicate_merge_workflows_remain_equivalent():
    contents = [path.read_text(encoding="utf-8") for path in WORKFLOWS]
    assert contents[0] == contents[1]
