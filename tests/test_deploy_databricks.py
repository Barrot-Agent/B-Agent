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
    names: list[str] = []
    for node in ast.walk(function):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                names.append(node.func.id)
            elif isinstance(node.func, ast.Attribute):
                names.append(node.func.attr)
    return names


def test_authentication_preflight_precedes_remote_mutations() -> None:
    functions = _functions()
    calls = _calls(functions["main"])

    assert calls.index("_validate_connection") < calls.index("_ensure_folder")
    assert calls.index("_validate_connection") < calls.index("_upload_files")
    assert calls.index("_validate_connection") < calls.index("_deploy_job")
    assert "current_user" in _calls(functions["_validate_connection"])
    assert "me" in _calls(functions["_validate_connection"])


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
