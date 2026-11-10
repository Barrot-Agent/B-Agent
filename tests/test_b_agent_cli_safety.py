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
