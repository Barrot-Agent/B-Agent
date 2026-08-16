#!/usr/bin/env python3
"""Export repository-visible GitHub activity into one provenance-aware document."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List

import requests


API_ROOT = "https://api.github.com"
DEFAULT_REPOSITORY = "Barrot-Agent/B-Agent"
TIMEOUT = 30


class GitHubActivityExporter:
    def __init__(self, repository: str, token: str | None = None) -> None:
        if "/" not in repository:
            raise ValueError("repository must be in OWNER/REPOSITORY form")
        self.repository = repository
        self.token = token
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )
        if token:
            self.session.headers["Authorization"] = "Bearer " + self.token

    def _get_page(
        self,
        endpoint: str,
        page: int,
        extra_params: Dict[str, Any] | None = None,
    ) -> List[Dict[str, Any]]:
        params = {"page": page, "per_page": 100}
        if extra_params:
            params.update(extra_params)
        response = self.session.get(
            f"{API_ROOT}/repos/{self.repository}/{endpoint}",
            params=params,
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            raise RuntimeError(f"GitHub returned an unexpected response for {endpoint}")
        return data

    def _all_pages(
        self,
        endpoint: str,
        extra_params: Dict[str, Any] | None = None,
    ) -> Iterable[Dict[str, Any]]:
        page = 1
        while True:
            records = self._get_page(endpoint, page, extra_params)
            yield from records
            if len(records) < 100:
                return
            page += 1

    @staticmethod
    def _record(
        record_type: str,
        source: str,
        item: Dict[str, Any],
        *,
        timestamp: str | None,
        title: str = "",
        body: str = "",
        url: str = "",
        number: int | None = None,
    ) -> Dict[str, Any]:
        user = item.get("user") or item.get("author") or {}
        return {
            "type": record_type,
            "source": source,
            "id": item.get("id") or item.get("sha"),
            "number": number,
            "timestamp": timestamp,
            "actor": user.get("login") if isinstance(user, dict) else None,
            "title": title,
            "body": body,
            "url": url,
            "provenance": {
                "repository": item.get("html_url", "").split("/issues/")[0]
                if item.get("html_url")
                else f"https://github.com/{source}",
                "source_endpoint": source,
            },
        }

    def export(self) -> Dict[str, Any]:
        records: List[Dict[str, Any]] = []

        for commit in self._all_pages("commits"):
            details = commit.get("commit") or {}
            records.append(
                self._record(
                    "commit",
                    self.repository,
                    commit,
                    timestamp=details.get("author", {}).get("date"),
                    title=(details.get("message") or "").splitlines()[0],
                    body=details.get("message") or "",
                    url=commit.get("html_url", ""),
                )
            )

        pulls: List[Dict[str, Any]] = []
        for pull in self._all_pages("pulls", {"state": "all"}):
            pulls.append(pull)
            records.append(
                self._record(
                    "pull_request",
                    self.repository,
                    pull,
                    timestamp=pull.get("created_at"),
                    title=pull.get("title", ""),
                    body=pull.get("body") or "",
                    url=pull.get("html_url", ""),
                    number=pull.get("number"),
                )
            )

        for issue in self._all_pages("issues", {"state": "all"}):
            if issue.get("pull_request"):
                continue
            records.append(
                self._record(
                    "issue",
                    self.repository,
                    issue,
                    timestamp=issue.get("created_at"),
                    title=issue.get("title", ""),
                    body=issue.get("body") or "",
                    url=issue.get("html_url", ""),
                    number=issue.get("number"),
                )
            )

        for comment in self._all_pages("issues/comments"):
            records.append(
                self._record(
                    "comment",
                    self.repository,
                    comment,
                    timestamp=comment.get("created_at"),
                    body=comment.get("body") or "",
                    url=comment.get("html_url", ""),
                )
            )

        for pull in pulls:
            number = pull["number"]
            for review in self._all_pages(f"pulls/{number}/reviews"):
                records.append(
                    self._record(
                        "pull_request_review",
                        self.repository,
                        review,
                        timestamp=review.get("submitted_at"),
                        body=review.get("body") or "",
                        url=review.get("html_url", ""),
                        number=number,
                    )
                )
            for comment in self._all_pages(f"pulls/{number}/comments"):
                records.append(
                    self._record(
                        "pull_request_review_comment",
                        self.repository,
                        comment,
                        timestamp=comment.get("created_at"),
                        body=comment.get("body") or "",
                        url=comment.get("html_url", ""),
                        number=number,
                    )
                )

        records.sort(key=lambda item: item.get("timestamp") or "")
        return {
            "schema_version": 1,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "repository": self.repository,
            "record_count": len(records),
            "records": records,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=os.getenv("GITHUB_REPOSITORY", DEFAULT_REPOSITORY))
    parser.add_argument("--token", default=os.getenv("GITHUB_TOKEN") or os.getenv("GH_PAT"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("brain_corpus/github_activity.json"),
    )
    args = parser.parse_args()

    document = GitHubActivityExporter(args.repository, args.token).export()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {document['record_count']} records to {args.output}")


if __name__ == "__main__":
    main()
