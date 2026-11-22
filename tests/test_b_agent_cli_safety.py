"""Safety tests for the standalone B-Agent CLI entry point."""

import ast
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "b_agent.py"


def _tree():
    return ast.parse(SOURCE.read_text(encoding="utf-8"), filename=str(SOURCE))


def test_b_agent_requires_github_credentials_without_provider_key():
    source = SOURCE.read_text(encoding="utf-8")
    assert 'GH_TOKEN = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")' in source
    assert "LUNAROUTE_API_KEY" not in source
    assert "class OpenCodeLLM:" in source
    assert "locally authenticated OpenCode CLI" in source


def test_b_agent_has_no_unverified_auto_merge_cli_or_call():
    tree = _tree()
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    auto_merge_flags = [
        node for node in calls
        if isinstance(node.func, ast.Attribute)
        and node.func.attr == "add_argument"
        and node.args
        and isinstance(node.args[0], ast.Constant)
        and node.args[0].value == "--auto-merge"
    ]
    direct_merge_calls = [
        node for node in calls
        if isinstance(node.func, ast.Attribute) and node.func.attr == "merge_pr"
    ]
    assert not auto_merge_flags
    assert not direct_merge_calls


def test_b_agent_keeps_cli_entrypoint():
    tree = _tree()
    main_guards = [
        node for node in tree.body
        if isinstance(node, ast.If)
        and isinstance(node.test, ast.Compare)
        and isinstance(node.test.left, ast.Name)
        and node.test.left.id == "__name__"
        and any(
            isinstance(value, ast.Constant) and value.value == "__main__"
            for value in node.test.comparators
        )
    ]

    def invokes_main_directly(statement):
        return (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Call)
            and isinstance(statement.value.func, ast.Name)
            and statement.value.func.id == "main"
        )

    assert any(
        invokes_main_directly(statement)
        for guard in main_guards
        for statement in guard.body
    )



def test_b_agent_cli_has_no_direct_remote_write_or_pr_creation():
    tree = _tree()
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    forbidden_methods = {"put", "ensure_branch", "commit_file", "open_pr"}
    assert not any(
        isinstance(node.func, ast.Attribute) and node.func.attr in forbidden_methods
        for node in calls
    )
    assert not any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "create_repository_repair_commit"
        for node in tree.body
    )


def test_b_agent_local_mutations_require_explicit_interactive_opt_in():
    source = SOURCE.read_text(encoding="utf-8")
    assert '"--write-local-audit"' in source
    assert "if args.write_local_audit:" in source
    assert '"--execute-local-repair"' in source
    assert "if args.execute_local_repair:" in source
    assert "sys.stdin.isatty()" in source
    assert "APPLY LOCAL REPAIRS" in source


def test_b_agent_has_no_lunaroute_transfer_cli_or_provider_path():
    source = SOURCE.read_text(encoding="utf-8")
    main = source[source.index("def main():"):]
    assert "lunaroute" not in source.lower()
    assert "LUNAROUTE_API_KEY" not in source
    assert "--allow-lunaroute-data-transfer" not in main
    assert "OpenCodeLLM(args.model)" in main


def test_b_agent_local_repair_checks_clean_feature_worktree_before_loop():
    source = SOURCE.read_text(encoding="utf-8")
    main = source[source.index("def main():"):]
    assert "assert_clean_feature_worktree" in source
    assert "default_branch=repo.default_branch" in main
    assert main.index("safe_workspace = assert_clean_feature_worktree(") < main.index("run_repository_repair_loop(")
