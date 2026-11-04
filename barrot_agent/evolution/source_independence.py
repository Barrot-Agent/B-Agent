"""
Barrot Source Independence Engine.

Groups evidence by canonical publisher identity so repeated evidence from the
same publisher does not count as independent corroboration. Publisher aliases
are explicit because one organization may publish from multiple domains.
"""

from __future__ import annotations

import ipaddress
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
# Tokyo SBIC is a separate corporation and is intentionally not grouped with SBI.
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
