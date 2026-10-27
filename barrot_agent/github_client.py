"""
GitHub API client for B-Agent.

Authentication is read from environment variables via AppConfig.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any


class GitHubClient:
    """Thin wrapper around the GitHub REST API."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str) -> None:
        if not token:
            raise ValueError("GitHub token must be provided via GITHUB_TOKEN env var.")
        self._token = token

    def _request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
    ) -> Any:
        url = f"{self.BASE_URL}{path}"
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={
                "Authorization": "Bearer " + self._token,
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "Content-Type": "application/json",
                "User-Agent": "B-Agent/1.0",
            },
        )
        try:
            with urllib.request.urlopen(req) as resp:  # noqa: S310
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as exc:
            raise GitHubAPIError(exc.code, exc.reason) from exc

    def get(self, path: str) -> Any:
        return self._request("GET", path)

    def post(self, path: str, body: dict[str, Any]) -> Any:
        return self._request("POST", path, body)


class GitHubAPIError(Exception):
    """Raised when the GitHub API returns an error response."""

    def __init__(self, status: int, reason: str) -> None:
        super().__init__(f"GitHub API error {status}: {reason}")
        self.status = status
        self.reason = reason
