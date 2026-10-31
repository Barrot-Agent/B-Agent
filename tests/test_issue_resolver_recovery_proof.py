import importlib.util
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "barrot_issue_resolver_recovery_proof",
    ROOT / "scripts" / "resolve_issue.py",
)
assert SPEC is not None and SPEC.loader is not None
resolver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(resolver)
resolver.REPO = "Barrot-Agent/B-Agent"


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def issue_body(run_id=1001, repo="Barrot-Agent/B-Agent"):
    return (
        "## Failing workflow: CI\n\n"
        f"**Most recent failed run:** https://github.com/{repo}/actions/runs/{run_id}\n"
    )


def original_run(**overrides):
    value = {
        "id": 1001,
        "workflow_id": 77,
        "head_branch": "main",
        "status": "completed",
        "conclusion": "failure",
        "created_at": "2026-10-31T10:00:00Z",
    }
    value.update(overrides)
    return value


def later_run(**overrides):
    value = {
        "id": 1002,
        "workflow_id": 77,
        "head_branch": "main",
        "status": "completed",
        "conclusion": "success",
        "created_at": "2026-10-31T10:05:00Z",
        "html_url": "https://github.com/Barrot-Agent/B-Agent/actions/runs/1002",
    }
    value.update(overrides)
    return value


def test_original_run_link_must_belong_to_this_repository():
    assert resolver.extract_original_run_id(issue_body()) == 1001
    assert resolver.extract_original_run_id(
        issue_body(repo="another-owner/another-repo")
    ) is None
    assert resolver.extract_original_run_id("No run URL is present.") is None


def test_same_branch_success_after_linked_failure_proves_recovery():
    with patch.object(
        resolver.requests,
        "get",
        side_effect=[
            FakeResponse(original_run()),
            FakeResponse({"workflow_runs": [later_run()]}),
        ],
    ) as get:
        evidence = resolver.get_verified_recovery_runs(issue_body(), 77)

    assert evidence is not None
    assert evidence["original"]["id"] == 1001
    assert evidence["latest"]["id"] == 1002
    assert get.call_args_list[1].kwargs["params"] == {
        "branch": "main",
        "per_page": 1,
    }


def test_success_on_an_unrelated_branch_does_not_prove_recovery():
    with patch.object(
        resolver.requests,
        "get",
        side_effect=[
            FakeResponse(original_run()),
            FakeResponse({"workflow_runs": [later_run(head_branch="release")]}),
        ],
    ):
        assert resolver.get_verified_recovery_runs(issue_body(), 77) is None


def test_success_not_later_than_original_failure_does_not_prove_recovery():
    with patch.object(
        resolver.requests,
        "get",
        side_effect=[
            FakeResponse(original_run()),
            FakeResponse({
                "workflow_runs": [
                    later_run(created_at="2026-10-31T09:59:00Z")
                ]
            }),
        ],
    ):
        assert resolver.get_verified_recovery_runs(issue_body(), 77) is None


def test_linked_run_must_be_a_failure_of_the_matched_workflow():
    with patch.object(
        resolver.requests,
        "get",
        return_value=FakeResponse(original_run(workflow_id=78)),
    ) as get:
        assert resolver.get_verified_recovery_runs(issue_body(), 77) is None
    assert get.call_count == 1

    with patch.object(
        resolver.requests,
        "get",
        return_value=FakeResponse(original_run(conclusion="success")),
    ) as get:
        assert resolver.get_verified_recovery_runs(issue_body(), 77) is None
    assert get.call_count == 1


def test_in_progress_run_cannot_close_the_issue():
    with patch.object(
        resolver.requests,
        "get",
        side_effect=[
            FakeResponse(original_run()),
            FakeResponse({
                "workflow_runs": [
                    later_run(status="in_progress", conclusion=None)
                ]
            }),
        ],
    ):
        assert resolver.get_verified_recovery_runs(issue_body(), 77) is None


def test_missing_original_run_url_fails_closed_without_api_access():
    with patch.object(resolver.requests, "get") as get:
        assert resolver.get_verified_recovery_runs("No source run URL.", 77) is None
    get.assert_not_called()


def test_resolver_does_not_comment_or_close_without_verified_recovery():
    issue = {
        "title": "[Auto] Workflow failing: CI",
        "body": issue_body(),
        "state": "OPEN",
    }
    with (
        patch.object(resolver, "get_issue", return_value=issue),
        patch.object(resolver, "find_workflow_file", return_value={"id": 77, "path": ".github/workflows/ci.yml"}),
        patch.object(resolver, "get_verified_recovery_runs", return_value=None),
        patch.object(resolver, "gh") as gh,
    ):
        resolver.resolve(42)
    gh.assert_not_called()


def test_resolver_closes_only_after_verified_same_branch_success():
    issue = {
        "title": "[Auto] Workflow failing: CI",
        "body": issue_body(),
        "state": "OPEN",
    }
    evidence = {
        "original": original_run(),
        "latest": later_run(),
    }
    with (
        patch.object(resolver, "get_issue", return_value=issue),
        patch.object(resolver, "find_workflow_file", return_value={"id": 77, "path": ".github/workflows/ci.yml"}),
        patch.object(resolver, "get_verified_recovery_runs", return_value=evidence),
        patch.object(resolver, "gh") as gh,
    ):
        resolver.resolve(42)

    assert gh.call_count == 2
    assert gh.call_args_list[0].args[:3] == ("issue", "comment", "42")
    assert gh.call_args_list[1].args == ("issue", "close", "42")


def test_resolver_leaves_issue_open_after_later_same_branch_failure():
    issue = {
        "title": "[Auto] Workflow failing: CI",
        "body": issue_body(),
        "state": "OPEN",
    }
    evidence = {
        "original": original_run(),
        "latest": later_run(conclusion="failure"),
    }
    with (
        patch.object(resolver, "get_issue", return_value=issue),
        patch.object(resolver, "find_workflow_file", return_value={"id": 77, "path": ".github/workflows/ci.yml"}),
        patch.object(resolver, "get_verified_recovery_runs", return_value=evidence),
        patch.object(resolver, "get_run_log_tail", return_value="failure trace"),
        patch.object(resolver, "gh") as gh,
    ):
        resolver.resolve(42)

    assert gh.call_count == 1
    assert gh.call_args.args[:3] == ("issue", "comment", "42")
    assert "still failed" in gh.call_args.args[-1]
