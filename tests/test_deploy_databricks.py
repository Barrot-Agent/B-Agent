from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / "scripts" / "deploy_databricks.py"


def _functions() -> dict[str, ast.FunctionDef]:
    tree = ast.parse(SCRIPT_PATH.read_text(encoding="utf-8"))
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }


def _calls(function: ast.FunctionDef) -> list[str]:
    found: list[tuple[int, int, str]] = []
    for node in ast.walk(function):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                found.append((node.lineno, node.col_offset, node.func.id))
            elif isinstance(node.func, ast.Attribute):
                found.append((node.lineno, node.col_offset, node.func.attr))
    return [name for _, _, name in sorted(found)]


def test_authentication_preflight_precedes_remote_mutations() -> None:
    functions = _functions()
    calls = _calls(functions["main"])

    upload_calls = _calls(functions["_upload_files"])
    assert upload_calls.index("_preflight_workspace_target_absent") < upload_calls.index("_ensure_folder")
    assert calls.index("_validate_connection") < calls.index("_upload_files")
    assert calls.index("_validate_connection") < calls.index("_deploy_job")
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "client.current_user.me()" in source


def test_partial_uploads_abort_before_job_creation() -> None:
    functions = _functions()
    main_calls = _calls(functions["main"])
    upload_calls = _calls(functions["_upload_files"])

    assert main_calls.index("_upload_files") < main_calls.index("_deploy_job")
    assert "RuntimeError" in upload_calls
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "Job creation was skipped." in source
    assert "DATABRICKS_HOST and DATABRICKS_TOKEN" in source


def test_upload_errors_do_not_log_raw_sdk_error_bodies() -> None:
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    assert 'log.error("  failed to upload %s (%s)", dest, type(exc).__name__)' in source
    assert 'log.warning("mkdirs(%s): %s", path, exc)' not in source


ORCHESTRATION_PATH = REPO_ROOT / "barrot_agent" / "orchestration" / "deploy_databricks.py"
OPS_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "barrot-ops.yml"
DEPLOY_WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "deploy-databricks.yml"


def _functions_for(path: Path) -> dict[str, ast.FunctionDef]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
    }


def _assert_no_overwrite_true(path: Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "import_":
            continue
        assert not any(
            keyword.arg == "overwrite"
            and isinstance(keyword.value, ast.Constant)
            and keyword.value.value is True
            for keyword in node.keywords
        ), f"{path} must never overwrite an existing Databricks object"


def test_both_deployment_entrypoints_require_per_run_approval_before_client_creation() -> None:
    for path in (SCRIPT_PATH, ORCHESTRATION_PATH):
        functions = _functions_for(path)
        calls = _calls(functions["main"])
        assert calls.index("_require_external_approval") < calls.index("_build_client")
        assert calls.index("_validate_connection") < calls.index("_upload_files")
        assert calls.index("_upload_files") < calls.index("_deploy_job")
        source = path.read_text(encoding="utf-8")
        assert 'os.environ.get("BARROT_CONFIRM_EXTERNAL_CHANGE") != "YES"' in source
        assert "client.current_user.me()" in source


def test_workspace_root_is_checked_before_creation_and_existing_targets_are_refused() -> None:
    for path in (SCRIPT_PATH, ORCHESTRATION_PATH):
        functions = _functions_for(path)
        calls = _calls(functions["_upload_files"])
        assert calls.index("_preflight_workspace_target_absent") < calls.index("_ensure_folder")
        source = path.read_text(encoding="utf-8")
        assert "except ResourceDoesNotExist:" in source
        assert "workspace.get_status(path=path)" in source
        assert "refusing overwrite" in source
        _assert_no_overwrite_true(path)


def test_databricks_workflows_do_not_overwrite_and_pass_explicit_approval() -> None:
    ops = OPS_WORKFLOW_PATH.read_text(encoding="utf-8")
    deploy = DEPLOY_WORKFLOW_PATH.read_text(encoding="utf-8")
    assert "--overwrite" not in ops
    assert "Existing paths are never overwritten." in ops
    assert "Target already exists. Refusing to overwrite" in ops
    assert "BARROT_CONFIRM_EXTERNAL_CHANGE: ${{ inputs.confirm_external_change }}" in deploy


def test_orchestration_upload_failures_abort_before_job_creation() -> None:
    functions = _functions_for(ORCHESTRATION_PATH)
    calls = _calls(functions["_upload_files"])
    assert "RuntimeError" in calls
    assert "Job creation was skipped." in ORCHESTRATION_PATH.read_text(encoding="utf-8")



def test_existing_jobs_are_never_reset_and_deployment_never_starts_a_job() -> None:
    for path in (SCRIPT_PATH, ORCHESTRATION_PATH):
        functions = _functions_for(path)
        deploy_calls = _calls(functions["_deploy_job"])
        assert deploy_calls.index("list") < deploy_calls.index("create")
        assert "RuntimeError" in deploy_calls
        assert "reset" not in deploy_calls
        assert "run_now" not in deploy_calls
        source = path.read_text(encoding="utf-8")
        assert "PauseStatus.PAUSED" in source
        assert "PauseStatus.UNPAUSED" not in source
        assert "client.jobs.reset(" not in source
        assert "client.jobs.run_now(" not in source
        assert "def _run_job(" not in source
