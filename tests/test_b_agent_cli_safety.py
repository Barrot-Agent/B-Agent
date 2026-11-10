"""Safety tests for the standalone B-Agent CLI entry point."""

import ast
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "b_agent.py"


def _tree():
    return ast.parse(SOURCE.read_text(encoding="utf-8"), filename=str(SOURCE))


def test_b_agent_requires_provider_and_github_credentials():
    tree = _tree()
    guards = [node for node in tree.body if isinstance(node, ast.If)]
    assert any(
        isinstance(node.test, ast.BoolOp)
        and isinstance(node.test.op, ast.Or)
        and {name.id for name in ast.walk(node.test) if isinstance(name, ast.Name)}
        >= {"LUNAROUTE_API_KEY", "GH_TOKEN"}
        for node in guards
    )


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


def test_b_agent_external_repository_transfer_requires_explicit_confirmation():
    source = SOURCE.read_text(encoding="utf-8")
    main = source[source.index("def main():"):]
    assert '"--allow-lunaroute-data-transfer"' in main
    assert "if not args.allow_lunaroute_data_transfer:" in main
    assert "SEND REPOSITORY CONTEXT TO LUNAROUTE" in main
    assert main.index("if not args.allow_lunaroute_data_transfer:") < main.index("llm = GroqLLM(")
    assert main.index("transfer_confirmation") < main.index("llm = GroqLLM(")


def test_b_agent_local_repair_checks_clean_feature_worktree_before_loop():
    source = SOURCE.read_text(encoding="utf-8")
    main = source[source.index("def main():"):]
    assert "assert_clean_feature_worktree" in source
    assert "default_branch=repo.default_branch" in main
    assert main.index("safe_workspace = assert_clean_feature_worktree(") < main.index("run_repository_repair_loop(")
