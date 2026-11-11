from pathlib import Path

from barrot_agent.mcp_sandbox import MCPSandbox


def test_regression_check_rejects_parent_traversal(tmp_path):
    sandbox = MCPSandbox(repo_root=tmp_path)
    result = sandbox._check_regression(tmp_path, {"../escaped.py": "print('escaped')"})
    assert not result.passed
    assert any("Unsafe proposed path" in finding for finding in result.findings)
    assert not (tmp_path.parent / "escaped.py").exists()


def test_regression_check_rejects_absolute_and_windows_paths(tmp_path):
    sandbox = MCPSandbox(repo_root=tmp_path)
    result = sandbox._check_regression(
        tmp_path,
        {str(tmp_path / "outside.py"): "pass", r"C:\outside.py": "pass"},
    )
    assert not result.passed
    assert len(result.findings) == 2


def test_regression_check_rejects_symlink_escape(tmp_path):
    sandbox_root = tmp_path / "sandbox"
    sandbox_root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (sandbox_root / "link").symlink_to(outside, target_is_directory=True)
    sandbox = MCPSandbox(repo_root=tmp_path)
    result = sandbox._check_regression(sandbox_root, {"link/escaped.py": "pass"})
    assert not result.passed
    assert not (outside / "escaped.py").exists()


def test_sandbox_does_not_report_deleted_temporary_path(tmp_path):
    sandbox = MCPSandbox(repo_root=tmp_path)
    report = sandbox.run("test", {"module.py": "value = 1"})
    assert report.sandbox_path == ""
