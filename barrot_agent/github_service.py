"""
GitHub service layer for B-Agent.

Provides domain-level operations on GitHub resources.  Both the HTTP API
(GPT Actions) and the MCP server use this module as their single source of
truth so that business logic is not duplicated.
"""

from __future__ import annotations

from typing import Any

from barrot_agent.github_client import GitHubClient


class GitHubService:
    """High-level GitHub operations used by both the HTTP API and MCP server."""

    def __init__(self, client: GitHubClient) -> None:
        self._client = client

    # ------------------------------------------------------------------
    # Issues
    # ------------------------------------------------------------------

    def list_issues(
        self,
        owner: str,
        repo: str,
        state: str = "open",
        per_page: int = 30,
        page: int = 1,
    ) -> list[dict[str, Any]]:
        """Return a list of issues for a repository."""
        path = (
            f"/repos/{owner}/{repo}/issues"
            f"?state={state}&per_page={per_page}&page={page}"
        )
        return self._client.get(path)  # type: ignore[return-value]

    def get_issue(self, owner: str, repo: str, issue_number: int) -> dict[str, Any]:
        """Return a single issue by number."""
        return self._client.get(f"/repos/{owner}/{repo}/issues/{issue_number}")  # type: ignore[return-value]

    def create_issue(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str = "",
        labels: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create a new issue and return the created object."""
        payload: dict[str, Any] = {"title": title, "body": body}
        if labels:
            payload["labels"] = labels
        return self._client.post(f"/repos/{owner}/{repo}/issues", payload)  # type: ignore[return-value]

    def add_comment(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        body: str,
    ) -> dict[str, Any]:
        """Add a comment to an existing issue and return the created comment."""
        return self._client.post(  # type: ignore[return-value]
            f"/repos/{owner}/{repo}/issues/{issue_number}/comments",
            {"body": body},
        )


def make_service(token: str) -> GitHubService:
    """Convenience factory used by both the HTTP API and MCP layers."""
    return GitHubService(GitHubClient(token))
