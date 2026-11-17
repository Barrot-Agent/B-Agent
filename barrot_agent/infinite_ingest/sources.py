"""Source adapters: URL in, :class:`Document` out.

Adapters are intentionally small and read-only.  Optional dependencies (the
YouTube transcript client) are imported lazily so the rest of the pipeline runs
on plain stdlib.  Every adapter records the canonical URL; callers never invent
a source.
"""

from __future__ import annotations

import html as html_module
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from .models import (
    AdapterUnavailable,
    Document,
    FetchError,
    IngestItem,
    RateLimitStop,
    normalise,
    read_text,
)

USER_AGENT = "BarrotInfiniteIngest/1.0 (+https://github.com/Barrot-Agent)"
DEFAULT_TIMEOUT = 25
DEFAULT_MIN_INTERVAL = 1.5
DEFAULT_SEARXNG_URL = "http://127.0.0.1:8888"
MAX_HTML_CHARS = 2_000_000


class RateLimiter:
    """Per-host minimum interval between requests."""

    def __init__(self, min_interval: float = DEFAULT_MIN_INTERVAL, clock=None, sleep=None):
        self.min_interval = min_interval
        self._clock = clock or time.monotonic
        self._sleep = sleep or time.sleep
        self._last: dict[str, float] = {}

    def wait(self, url: str) -> None:
        """Sleep just enough to respect the host interval."""
        host = urllib.parse.urlsplit(url).netloc
        last = self._last.get(host)
        if last is not None:
            elapsed = self._clock() - last
            if elapsed < self.min_interval:
                self._sleep(self.min_interval - elapsed)
        self._last[host] = self._clock()


def _http_get(url: str, headers: dict | None = None, timeout: int = DEFAULT_TIMEOUT) -> str:
    """Fetch a URL as text; map HTTP errors to pipeline errors."""
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept-Language": "en-US,en;q=0.9",
            **(headers or {}),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read(MAX_HTML_CHARS)
            charset = response.headers.get_content_charset() or "utf-8"
    except urllib.error.HTTPError as exc:
        if exc.code in (429, 503):
            raise RateLimitStop(f"rate limited by {url} (HTTP {exc.code})") from exc
        raise FetchError(f"HTTP {exc.code} for {url}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise FetchError(f"network error for {url}: {exc}") from exc
    return payload.decode(charset, "replace")


def strip_html(markup: str) -> tuple[str, str]:
    """Return ``(text, title)`` from an HTML document."""
    title_match = re.search(r"(?is)<title[^>]*>(.*?)</title>", markup)
    title = normalise(html_module.unescape(title_match.group(1))) if title_match else ""
    body = re.sub(r"(?is)<(script|style|noscript|svg)[^>]*>.*?</\1>", " ", markup)
    body = re.sub(r"(?s)<[^>]+>", " ", body)
    return normalise(html_module.unescape(body)), title


def infer_kind(url: str) -> str:
    """Infer a source kind from a URL."""
    host = urllib.parse.urlsplit(url).netloc.lower()
    path = urllib.parse.urlsplit(url).path.lower()
    if "youtube.com" in host or "youtu.be" in host:
        return "video"
    if "arxiv.org" in host or "pubmed" in host or "openalex.org" in host:
        return "paper"
    if "wikipedia.org" in host:
        return "article"
    if "news.ycombinator.com" in host:
        return "discussion"
    if "github.com" in host or "raw.githubusercontent.com" in host:
        return "code"
    if path.endswith(".pdf"):
        return "paper"
    return "web"


class SourceFetcher:
    """Dispatch a queued item to the right adapter.

    Args:
        min_interval: Seconds between requests to one host.
        timeout: HTTP timeout.
        http_get: Injectable transport with signature ``(url, headers) -> str``.
        limiter: Injectable rate limiter.
    """

    def __init__(
        self,
        min_interval: float = DEFAULT_MIN_INTERVAL,
        timeout: int = DEFAULT_TIMEOUT,
        http_get=None,
        limiter: RateLimiter | None = None,
    ):
        self.timeout = timeout
        self.http_get = http_get or _http_get
        self.limiter = limiter or RateLimiter(min_interval)

    # -- transport --------------------------------------------------------

    def _get(self, url: str, headers: dict | None = None) -> str:
        self.limiter.wait(url)
        try:
            return self.http_get(url, headers)
        except TypeError:
            # Injected transports may accept only the URL.
            return self.http_get(url)

    def fetch(self, item: IngestItem) -> Document:
        """Fetch one item and return its text with provenance."""
        kind = item.kind if item.kind and item.kind != "auto" else infer_kind(item.url)
        if item.path:
            path = Path(item.path)
            if not path.exists():
                raise FetchError(f"local cache missing: {item.path}")
            text = read_text(path)
            return Document(
                url=item.url,
                kind=kind,
                title=item.title or path.stem,
                text=text,
                fetch_mode="local_cache",
                extra={"cache_path": str(path)},
            )
        if kind == "video":
            return self._youtube(item, kind)
        if kind == "paper":
            return self._paper(item, kind)
        if kind == "article":
            return self._wikipedia(item, kind)
        if kind == "discussion":
            return self._hackernews(item, kind)
        if kind == "code":
            return self._github(item, kind)
        return self._web(item, kind)

    # -- adapters ---------------------------------------------------------

    def _youtube(self, item: IngestItem, kind: str) -> Document:
        match = re.search(r"(?:v=|youtu\.be/|shorts/)([\w-]{11})", item.url)
        if not match:
            raise FetchError(f"cannot extract video id from {item.url}")
        video_id = match.group(1)
        try:
            from youtube_transcript_api import YouTubeTranscriptApi  # type: ignore
        except ImportError as exc:  # pragma: no cover - depends on environment
            raise AdapterUnavailable(
                "youtube-transcript-api is not installed for this interpreter; "
                "use the dedicated venv or a local transcript file"
            ) from exc
        try:
            transcript = YouTubeTranscriptApi().fetch(
                video_id, languages=["en", "en-US", "en-GB"]
            )
            text = " ".join(segment.text.strip() for segment in transcript)
        except Exception as exc:  # pragma: no cover - network dependent
            raise FetchError(f"transcript fetch failed for {video_id}: {exc}") from exc
        return Document(
            url=item.url,
            kind=kind,
            title=item.title or video_id,
            text=text,
            extra={"video_id": video_id},
        )

    def _paper(self, item: IngestItem, kind: str) -> Document:
        url = item.url
        if "arxiv.org" in url:
            return self._arxiv(item, kind)
        if "pubmed" in url:
            return self._pubmed(item, kind)
        if "openalex.org" in url:
            return self._openalex(item, kind)
        return self._web(item, kind)

    def _arxiv(self, item: IngestItem, kind: str) -> Document:
        match = re.search(r"(\d{4}\.\d{4,5})", item.url)
        if not match:
            raise FetchError(f"cannot extract arXiv id from {item.url}")
        arxiv_id = match.group(1)
        xml = self._get(f"https://export.arxiv.org/api/query?id_list={arxiv_id}")
        title = _tag(xml, "title") or item.title or arxiv_id
        summary = _tag(xml, "summary")
        published = _tag(xml, "published")
        if not summary:
            raise FetchError(f"empty arXiv abstract for {arxiv_id}")
        return Document(
            url=item.url,
            kind=kind,
            title=title,
            text=f"{title}\n\n{summary}",
            published=published,
            extra={"arxiv_id": arxiv_id},
        )

    def _wikipedia(self, item: IngestItem, kind: str) -> Document:
        title = urllib.parse.unquote(item.url.rsplit("/wiki/", 1)[-1]).replace("_", " ")
        title = urllib.parse.unquote(title.split("#", 1)[0])
        query = urllib.parse.urlencode(
            {
                "action": "query",
                "prop": "extracts",
                "explaintext": "1",
                "format": "json",
                "redirects": "1",
                "titles": title,
            }
        )
        payload = json.loads(self._get(f"https://en.wikipedia.org/w/api.php?{query}"))
        pages = payload.get("query", {}).get("pages", {})
        extract = next((page.get("extract", "") for page in pages.values()), "")
        if not extract:
            raise FetchError(f"no Wikipedia extract for {title!r}")
        return Document(url=item.url, kind=kind, title=item.title or title, text=extract)

    def _hackernews(self, item: IngestItem, kind: str) -> Document:
        match = re.search(r"(?:id=|item/)(\d+)", item.url)
        if not match:
            raise FetchError(f"cannot extract Hacker News item id from {item.url}")
        story = json.loads(self._get(f"https://hn.algolia.com/api/v1/items/{match.group(1)}"))
        lines = [story.get("title") or item.title or "Hacker News item"]
        if story.get("text"):
            lines.append(strip_html(story["text"])[0])
        for child in _hn_children(story.get("children", []), limit=40):
            lines.append(child)
        return Document(
            url=item.url,
            kind=kind,
            title=item.title or story.get("title", ""),
            text="\n".join(lines),
        )

    def _pubmed(self, item: IngestItem, kind: str) -> Document:
        match = re.search(r"/(\d{6,9})", item.url)
        if not match:
            raise FetchError(f"cannot extract PubMed id from {item.url}")
        pmid = match.group(1)
        xml = self._get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
            f"?db=pubmed&id={pmid}&retmode=xml"
        )
        title = _tag(xml, "ArticleTitle") or item.title or pmid
        abstract = " ".join(_all_tags(xml, "AbstractText"))
        if not abstract:
            raise FetchError(f"no PubMed abstract for {pmid}")
        return Document(url=item.url, kind=kind, title=title, text=f"{title}\n\n{abstract}")

    def _openalex(self, item: IngestItem, kind: str) -> Document:
        work_id = item.url.rsplit("/", 1)[-1]
        work = json.loads(self._get(f"https://api.openalex.org/works/{work_id}"))
        title = work.get("title") or item.title
        index = work.get("abstract_inverted_index") or {}
        positions: list[tuple[int, str]] = []
        for word, slots in index.items():
            positions.extend((position, word) for position in slots)
        abstract = normalise(" ".join(word for _, word in sorted(positions)))
        if not abstract:
            raise FetchError(f"no OpenAlex abstract for {item.url}")
        return Document(
            url=item.url,
            kind=kind,
            title=title,
            text=f"{title}\n\n{abstract}",
            published=str(work.get("publication_date") or ""),
        )

    def _github(self, item: IngestItem, kind: str) -> Document:
        match = re.match(
            r"https?://github\.com/([^/]+)/([^/]+)/(?:blob|raw)/([^/]+)/(.+)", item.url
        )
        if match:
            owner, repo, ref, path = match.groups()
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"
            text = self._get(raw_url)
            return Document(url=item.url, kind=kind, title=item.title or path, text=text)
        match = re.match(r"https?://github\.com/([^/]+)/([^/]+)/?$", item.url)
        if not match:
            raise FetchError(f"unsupported GitHub URL: {item.url}")
        owner, repo = match.groups()
        headers = {"Accept": "application/vnd.github.raw+json"}
        token = os.environ.get("GITHUB_MCP_TOKEN") or os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        text = self._get(f"https://api.github.com/repos/{owner}/{repo}/readme", headers)
        return Document(
            url=item.url,
            kind=kind,
            title=item.title or f"{owner}/{repo} README",
            text=text,
        )

    def _web(self, item: IngestItem, kind: str) -> Document:
        text, title = strip_html(self._get(item.url))
        if not text:
            raise FetchError(f"empty page at {item.url}")
        return Document(url=item.url, kind=kind, title=item.title or title, text=text)


# -- parsing helpers ------------------------------------------------------


def _tag(xml: str, name: str) -> str:
    match = re.search(rf"<{name}[^>]*>(.*?)</{name}>", xml, re.DOTALL)
    return normalise(html_module.unescape(match.group(1))) if match else ""


def _all_tags(xml: str, name: str) -> list[str]:
    return [
        normalise(html_module.unescape(match.group(1)))
        for match in re.finditer(rf"<{name}[^>]*>(.*?)</{name}>", xml, re.DOTALL)
    ]


def _hn_children(children: list[dict], limit: int = 40) -> list[str]:
    out: list[str] = []
    for child in children:
        if len(out) >= limit:
            break
        text = strip_html(child.get("text") or "")[0]
        if text:
            out.append(text)
        out.extend(_hn_children(child.get("children", []), limit - len(out)))
    return out


def searxng_search(
    query: str,
    *,
    base_url: str = DEFAULT_SEARXNG_URL,
    limit: int = 10,
    kind: str = "",
    http_get=None,
) -> list[IngestItem]:
    """Discover URLs through the local SearXNG instance.

    Discovery only; nothing is ingested here.  Results are queued, then fetched
    through the normal adapters and deduped by the ledger.
    """
    get = http_get or _http_get
    params = urllib.parse.urlencode({"q": query, "format": "json", "language": "en"})
    payload = json.loads(get(f"{base_url.rstrip('/')}/search?{params}"))
    items: list[IngestItem] = []
    for result in payload.get("results", []):
        url = result.get("url", "")
        if not url:
            continue
        inferred = infer_kind(url)
        if kind and inferred != kind:
            continue
        items.append(IngestItem(url=url, kind=inferred, title=result.get("title", "")))
        if len(items) >= limit:
            break
    return items


def seed_local(item: IngestItem, path: str) -> IngestItem:
    """Return a copy of ``item`` bound to a local transcript file."""
    return IngestItem(
        url=item.url,
        kind=item.kind,
        title=item.title,
        capability=item.capability,
        path=path,
        added_at=item.added_at,
    )
