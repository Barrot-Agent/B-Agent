"""
Tests for the GitHub service layer and the MCP/HTTP adapters.

All GitHub API calls are mocked so that no real network requests are made.
"""

from __future__ import annotations

import json
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from barrot_agent.github_client import GitHubAPIError, GitHubClient
from barrot_agent.github_service import GitHubService, make_service


# ---------------------------------------------------------------------------
# GitHubClient unit tests
# ---------------------------------------------------------------------------


class TestGitHubClient:
    def test_requires_token(self) -> None:
        with pytest.raises(ValueError):
            GitHubClient("")

    def test_accepts_valid_token(self) -> None:
        client = GitHubClient("ghp_token123")
        assert client._token == "ghp_token123"

    def test_get_calls_request(self) -> None:
        client = GitHubClient("tok")
        client._request = MagicMock(return_value=[{"id": 1}])  # type: ignore[method-assign]
        result = client.get("/repos/o/r/issues")
        client._request.assert_called_once_with("GET", "/repos/o/r/issues")
        assert result == [{"id": 1}]

    def test_post_passes_body(self) -> None:
        client = GitHubClient("tok")
        client._request = MagicMock(return_value={"id": 99})  # type: ignore[method-assign]
        client.post("/repos/o/r/issues", {"title": "Bug"})
        client._request.assert_called_once_with("POST", "/repos/o/r/issues", {"title": "Bug"})

    def test_http_error_raises_github_api_error(self) -> None:
        import urllib.error

        client = GitHubClient("tok")
        http_err = urllib.error.HTTPError(url="", code=404, msg="Not Found", hdrs=None, fp=None)  # type: ignore[arg-type]

        with patch("urllib.request.urlopen", side_effect=http_err):
            with pytest.raises(GitHubAPIError) as exc_info:
                client.get("/repos/o/r/issues/999")
        assert exc_info.value.status == 404


# ---------------------------------------------------------------------------
# GitHubService unit tests
# ---------------------------------------------------------------------------


class TestGitHubService:
    def _svc(self) -> tuple[GitHubService, MagicMock]:
        mock_client = MagicMock(spec=GitHubClient)
        svc = GitHubService(mock_client)
        return svc, mock_client

    def test_list_issues_calls_get(self) -> None:
        svc, cli = self._svc()
        cli.get.return_value = [{"number": 1}]
        result = svc.list_issues("owner", "repo")
        assert result == [{"number": 1}]
        cli.get.assert_called_once()
        assert "/repos/owner/repo/issues" in cli.get.call_args[0][0]

    def test_list_issues_passes_state(self) -> None:
        svc, cli = self._svc()
        cli.get.return_value = []
        svc.list_issues("owner", "repo", state="closed")
        path = cli.get.call_args[0][0]
        assert "state=closed" in path

    def test_get_issue(self) -> None:
        svc, cli = self._svc()
        cli.get.return_value = {"number": 42, "title": "Test"}
        result = svc.get_issue("owner", "repo", 42)
        assert result["number"] == 42
        cli.get.assert_called_once_with("/repos/owner/repo/issues/42")

    def test_create_issue(self) -> None:
        svc, cli = self._svc()
        cli.post.return_value = {"number": 10, "title": "New bug"}
        result = svc.create_issue("owner", "repo", "New bug", "desc")
        assert result["title"] == "New bug"
        cli.post.assert_called_once()
        path, payload = cli.post.call_args[0]
        assert path == "/repos/owner/repo/issues"
        assert payload["title"] == "New bug"
        assert payload["body"] == "desc"

    def test_create_issue_with_labels(self) -> None:
        svc, cli = self._svc()
        cli.post.return_value = {}
        svc.create_issue("owner", "repo", "Title", labels=["bug"])
        _, payload = cli.post.call_args[0]
        assert payload["labels"] == ["bug"]

    def test_create_issue_without_labels_omits_key(self) -> None:
        svc, cli = self._svc()
        cli.post.return_value = {}
        svc.create_issue("owner", "repo", "Title")
        _, payload = cli.post.call_args[0]
        assert "labels" not in payload

    def test_add_comment(self) -> None:
        svc, cli = self._svc()
        cli.post.return_value = {"id": 5}
        result = svc.add_comment("owner", "repo", 1, "hello")
        assert result == {"id": 5}
        path, payload = cli.post.call_args[0]
        assert path == "/repos/owner/repo/issues/1/comments"
        assert payload == {"body": "hello"}

    def test_make_service_factory(self) -> None:
        svc = make_service("tok")
        assert isinstance(svc, GitHubService)


# ---------------------------------------------------------------------------
# MCP server unit tests
# ---------------------------------------------------------------------------


class TestMCPServer:
    def _run(self, messages: list[dict]) -> list[dict]:
        from barrot_agent.config import AppConfig
        from barrot_agent.mcp_github import run_server

        cfg = AppConfig(github_token="tok")
        lines_in = StringIO("\n".join(json.dumps(m) for m in messages) + "\n")
        responses: list[dict] = []

        def capture(obj: dict) -> None:
            responses.append(obj)

        with patch("barrot_agent.mcp_github.make_service") as mock_factory:
            mock_svc = MagicMock()
            mock_factory.return_value = mock_svc
            mock_svc.list_issues.return_value = [{"number": 1}]
            mock_svc.get_issue.return_value = {"number": 1, "title": "X"}
            mock_svc.create_issue.return_value = {"number": 2}
            mock_svc.add_comment.return_value = {"id": 9}

            run_server(config=cfg, _input=lines_in, _output=capture)

        return responses

    def test_initialize(self) -> None:
        resp = self._run([{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}])
        assert resp[0]["result"]["protocolVersion"] == "2024-11-05"
        assert "tools" in resp[0]["result"]["capabilities"]

    def test_tools_list(self) -> None:
        resp = self._run([{"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}])
        tool_names = [t["name"] for t in resp[0]["result"]["tools"]]
        assert "github_list_issues" in tool_names
        assert "github_create_issue" in tool_names
        assert "github_add_comment" in tool_names

    def test_tools_call_list_issues(self) -> None:
        resp = self._run(
            [
                {
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "github_list_issues",
                        "arguments": {"owner": "o", "repo": "r"},
                    },
                }
            ]
        )
        result = resp[0]["result"]
        assert result["isError"] is False
        payload = json.loads(result["content"][0]["text"])
        assert payload == [{"number": 1}]

    def test_tools_call_unknown_tool(self) -> None:
        resp = self._run(
            [
                {
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {"name": "unknown_tool", "arguments": {}},
                }
            ]
        )
        result = resp[0]["result"]
        assert result["isError"] is True

    def test_unknown_method_returns_error(self) -> None:
        resp = self._run(
            [{"jsonrpc": "2.0", "id": 5, "method": "foo/bar", "params": {}}]
        )
        assert "error" in resp[0]
        assert resp[0]["error"]["code"] == -32601

    def test_invalid_json_returns_parse_error(self) -> None:
        from barrot_agent.config import AppConfig
        from barrot_agent.mcp_github import run_server

        cfg = AppConfig(github_token="tok")
        lines_in = StringIO("not-json\n")
        responses: list[dict] = []
        run_server(config=cfg, _input=lines_in, _output=responses.append)
        assert responses[0]["error"]["code"] == -32700
