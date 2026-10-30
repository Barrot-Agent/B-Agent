from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = (
    ROOT / ".github" / "workflows" / "barrot-merge.yml",
    ROOT / ".github" / "workflows" / "barrot-merge-manual.yml",
)


def _job_block(content: str, job_name: str) -> str:
    marker = f"  {job_name}:"
    start = content.index(marker)
    if job_name == "merge":
        end = content.index("\n  upload:", start + len(marker))
        return content[start:end]
    return content[start:]


def _step_block(content: str, step_name: str) -> str:
    marker = f"      - name: {step_name}"
    start = content.index(marker)
    next_step = content.find("\n      - name:", start + len(marker))
    return content[start:] if next_step == -1 else content[start:next_step]


def test_remote_code_merge_isolated_from_huggingface_upload_credentials():
    for path in WORKFLOWS:
        content = path.read_text(encoding="utf-8")
        merge_job = _job_block(content, "merge")
        upload_job = _job_block(content, "upload")
        assert "--trust-remote-code" in merge_job
        assert "HF_TOKEN" not in merge_job
        assert "HUGGINGFACE_HUB_TOKEN" not in merge_job
        assert "secrets.HF_TOKEN" not in merge_job
        assert "actions/upload-artifact@" in merge_job
        assert "actions/download-artifact@" in upload_job
        assert "needs: merge" in upload_job
        assert "persist-credentials: false" in merge_job
        assert "git-credentials" not in content
        assert "credential.helper store" not in content


def test_upload_token_is_scoped_to_final_step_on_separate_runner():
    for path in WORKFLOWS:
        content = path.read_text(encoding="utf-8")
        upload_job = _job_block(content, "upload")
        upload_step = _step_block(upload_job, "Upload")
        upload_start = upload_job.index("      - name: Upload")
        assert "HF_TOKEN: ${{ secrets.HF_TOKEN }}" in upload_step
        assert "secrets.HF_TOKEN" not in upload_job[:upload_start]
        assert upload_job.count("secrets.HF_TOKEN") == 1


def test_model_name_is_passed_as_environment_and_validated():
    for path in WORKFLOWS:
        content = path.read_text(encoding="utf-8")
        assert content.count("MODEL_NAME: ${{ inputs.model_name }}") == 2
        assert "${{ github.event.inputs.model_name }}" not in content
        assert content.count('[[ ! "$MODEL_NAME" =~ ^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$ ]]') == 2
        assert 'output/$MODEL_NAME' in content
        assert 'hf upload "Barrot-Agent/$MODEL_NAME"' in content


def test_artifact_boundary_rejects_symlinks_before_and_after_transfer():
    for path in WORKFLOWS:
        content = path.read_text(encoding="utf-8")
        assert content.count('find "output/$MODEL_NAME" -type l') == 2
        assert "path: output/" in content
        assert "retention-days: 1" in content


def test_duplicate_merge_workflows_remain_equivalent():
    contents = [path.read_text(encoding="utf-8") for path in WORKFLOWS]
    assert contents[0] == contents[1]
