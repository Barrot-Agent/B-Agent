"""
Barrot Source Independence Engine.

Groups evidence by canonical publisher identity so repeated evidence from the
same publisher does not count as independent corroboration. Publisher aliases
are explicit because one organization may publish from multiple domains.
"""

from __future__ import annotations

import hashlib
import ipaddress
import json
from collections.abc import Mapping
from urllib.parse import urlsplit


MULTI_LABEL_PUBLIC_SUFFIXES = {
    "co.jp", "ne.jp", "or.jp", "go.jp", "ac.jp", "ed.jp", "lg.jp",
    "co.uk", "org.uk", "ac.uk", "gov.uk",
    "com.au", "net.au", "org.au", "edu.au", "gov.au",
    "com.br", "com.cn", "com.sg", "com.hk", "com.tw", "co.in",
    "co.kr", "or.kr", "co.nz", "com.mx", "com.tr", "com.ar",
    "com.my", "com.ph", "com.vn", "com.id", "co.za",
}

# Related SBI legal entities are one publisher group for corroboration.
# SBIC East (Tokyo), Central (Nagoya), and West (Osaka) are separate regional
# SME investment companies, not SBI Holdings. Their domains are deliberately
# not aliased to sbi-group; each retains its publisher identity unless a
# shared upstream lineage is explicitly declared.
PUBLISHER_DOMAIN_ALIASES = {
    "sbigroup.co.jp": "sbi-group",
    "sbishinseibank.co.jp": "sbi-group",
    "sbivc.co.jp": "sbi-group",
    "sbirippleasia.co.jp": "sbi-group",
}


def canonical_publisher_group(source_url: str) -> str:
    """Resolve an HTTP(S) URL to a canonical publisher group.

    The result is a publisher-identity heuristic, not proof of independent
    reporting lineage. Known corporate aliases are collapsed explicitly.
    """
    if not isinstance(source_url, str) or not source_url.strip():
        return ""

    try:
        parsed = urlsplit(source_url.strip())
        if parsed.scheme.lower() not in {"http", "https"}:
            return ""
        hostname = parsed.hostname
        if not hostname:
            return ""
        hostname = hostname.rstrip(".").encode("idna").decode("ascii").lower()
    except (ValueError, UnicodeError):
        return ""

    if not hostname or hostname.startswith(".") or ".." in hostname:
        return ""
    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        return ""

    for domain, publisher in PUBLISHER_DOMAIN_ALIASES.items():
        if hostname == domain or hostname.endswith("." + domain):
            return publisher

    labels = hostname.split(".")
    if len(labels) < 2:
        return ""

    suffix = ".".join(labels[-2:])
    suffix_length = 2 if suffix in MULTI_LABEL_PUBLIC_SUFFIXES else 1
    if len(labels) <= suffix_length:
        return ""

    return ".".join(labels[-(suffix_length + 1):])


def canonical_independence_groups(sources: list[Mapping]) -> list[str]:
    """Collapse declared shared lineages and publisher aliases into one group.

    A declared independence_group captures known syndication or shared upstream
    provenance. The URL-derived publisher group is an additional conservative
    constraint: two differently labeled feeds from the same publisher cannot
    count as independent corroboration. Distinct publisher domains sharing one
    declared lineage also collapse into one group.
    """
    if not isinstance(sources, (list, tuple)):
        raise ValueError("sources must be a list or tuple")
    if not sources:
        return []

    parents = list(range(len(sources)))

    def find(index: int) -> int:
        while parents[index] != index:
            parents[index] = parents[parents[index]]
            index = parents[index]
        return index

    def union(left: int, right: int) -> None:
        root_left = find(left)
        root_right = find(right)
        if root_left != root_right:
            parents[max(root_left, root_right)] = min(root_left, root_right)

    key_owner: dict[str, int] = {}
    details: list[tuple[str, str]] = []
    for index, source in enumerate(sources):
        if not isinstance(source, Mapping):
            raise ValueError(f"sources[{index}] must be a mapping")
        lineage = source.get("independence_group")
        if not isinstance(lineage, str) or not lineage.strip():
            raise ValueError(f"sources[{index}].independence_group is required")
        lineage = lineage.strip()
        uri = source.get("source_uri", source.get("source_url", ""))
        publisher = canonical_publisher_group(uri) if isinstance(uri, str) else ""
        keys = [f"lineage:{lineage.casefold()}"]
        if publisher:
            keys.append(f"publisher:{publisher}")
        for key in keys:
            owner = key_owner.get(key)
            if owner is None:
                key_owner[key] = index
            else:
                union(index, owner)
        details.append((lineage, publisher))

    components: dict[int, dict[str, set[str]]] = {}
    for index, (lineage, publisher) in enumerate(details):
        root = find(index)
        component = components.setdefault(root, {"lineages": set(), "publishers": set()})
        component["lineages"].add(lineage)
        if publisher:
            component["publishers"].add(publisher)

    labels: list[str] = []
    for component in components.values():
        lineages = sorted(component["lineages"], key=str.casefold)
        publishers = sorted(component["publishers"])
        if len(lineages) == 1:
            label = lineages[0]
        elif len(publishers) == 1:
            label = f"publisher:{publishers[0]}"
        else:
            fingerprint = json.dumps(
                {"lineages": lineages, "publishers": publishers},
                sort_keys=True,
                separators=(",", ":"),
            )
            label = "merged:" + hashlib.sha256(fingerprint.encode("utf-8")).hexdigest()
        labels.append(label)
    return sorted(labels)


class SourceIndependenceEngine:
    """Determine whether evidence sources have distinct publisher identities."""

    @staticmethod
    def source_identity(source: str, source_url: str = "") -> str:
        """Return a stable publisher identity, preferring a normalized URL."""
        if source_url:
            identity = canonical_publisher_group(source_url)
            if identity:
                return identity
            return ""
        return source.strip().lower()

    def independent_sources(
        self,
        evidence_records: list[dict],
    ) -> dict[str, list[dict]]:
        """Group evidence records by canonical publisher identity."""
        groups: dict[str, list[dict]] = {}

        for record in evidence_records:
            identity = self.source_identity(
                record.get("source", ""),
                record.get("source_url", ""),
            )
            if not identity:
                continue
            groups.setdefault(identity, []).append(record)

        return groups
