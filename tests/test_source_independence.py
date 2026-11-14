from barrot_agent.evolution.source_independence import (
    SourceIndependenceEngine,
    canonical_publisher_group,
)


def test_groups_same_domain_as_one_source():
    engine = SourceIndependenceEngine()

    groups = engine.independent_sources(
        [
            {"source": "article_one", "source_url": "https://example.com/a"},
            {"source": "article_two", "source_url": "https://example.com/b"},
            {"source": "other", "source_url": "https://independent.org/a"},
        ]
    )

    assert len(groups) == 2
    assert len(groups["example.com"]) == 2
    assert len(groups["independent.org"]) == 1


def test_subdomains_ports_and_www_resolve_to_one_publisher():
    assert canonical_publisher_group("https://www.example.com/a") == "example.com"
    assert canonical_publisher_group("https://api.example.com:8443/b") == "example.com"
    assert canonical_publisher_group("https://example.com:443/c") == "example.com"


def test_country_code_public_suffix_is_normalized():
    assert canonical_publisher_group("https://news.example.co.uk/story") == "example.co.uk"
    assert canonical_publisher_group("https://api.example.co.jp/story") == "example.co.jp"


def test_related_sbi_domains_share_one_publisher_group():
    assert canonical_publisher_group("https://www.sbigroup.co.jp/news") == "sbi-group"
    assert canonical_publisher_group("https://corp.sbishinseibank.co.jp/news") == "sbi-group"
    assert canonical_publisher_group("https://www.sbivc.co.jp/") == "sbi-group"


def test_tokyo_sbic_is_not_misclassified_as_sbi_holdings():
    assert canonical_publisher_group("https://www.sbic.co.jp/company/") == "sbic.co.jp"
    assert canonical_publisher_group("https://www.sbic.co.jp/company/") != "sbi-group"


def test_non_http_urls_cannot_establish_external_publisher_identity():
    assert canonical_publisher_group("fixture://publisher-a") == ""
    assert canonical_publisher_group("barrot://generated/source") == ""
