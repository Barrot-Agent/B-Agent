from barrot_agent.evolution.source_independence import (
    SourceIndependenceEngine,
    canonical_independence_groups,
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


def test_regional_sbic_east_central_west_share_one_group_separate_from_sbi():
    regional_urls = [
        "https://www.sbic.co.jp/company/",
        "https://www.sbic-cj.co.jp/company/",
        "https://www.sbic-wj.co.jp/profiles/profile/",
    ]

    assert {
        canonical_publisher_group(url) for url in regional_urls
    } == {"sbic-regional"}

    sources = [
        {
            "source_id": f"sbic-region-{index}",
            "independence_group": f"sbic-region-{index}",
            "source_uri": url,
        }
        for index, url in enumerate(regional_urls)
    ]
    assert canonical_independence_groups(sources) == ["publisher:sbic-regional"]
    assert canonical_publisher_group("https://www.sbigroup.co.jp/news") == "sbi-group"


def test_same_publisher_cannot_be_split_into_multiple_declared_groups():
    groups = canonical_independence_groups(
        [
            {
                "source_id": "api-feed",
                "independence_group": "api-feed",
                "source_uri": "https://api.example.com/market",
            },
            {
                "source_id": "www-feed",
                "independence_group": "www-feed",
                "source_uri": "https://www.example.com/market",
            },
        ]
    )
    assert groups == ["publisher:example.com"]


def test_sbi_group_aliases_collapse_across_distinct_domains_and_labels():
    groups = canonical_independence_groups(
        [
            {
                "source_id": "sbi-holdings",
                "independence_group": "sbi-holdings",
                "source_uri": "https://www.sbigroup.co.jp/news",
            },
            {
                "source_id": "sbi-vc",
                "independence_group": "sbi-vc",
                "source_uri": "https://www.sbivc.co.jp/news",
            },
        ]
    )
    assert groups == ["publisher:sbi-group"]


def test_shared_lineage_collapses_different_publishers():
    groups = canonical_independence_groups(
        [
            {
                "source_id": "wire-a",
                "independence_group": "shared-wire",
                "source_uri": "https://news-a.example/story",
            },
            {
                "source_id": "wire-b",
                "independence_group": "shared-wire",
                "source_uri": "https://news-b.example/story",
            },
        ]
    )
    assert groups == ["shared-wire"]


def test_non_http_urls_cannot_establish_external_publisher_identity():
    assert canonical_publisher_group("fixture://publisher-a") == ""
    assert canonical_publisher_group("barrot://generated/source") == ""

def test_ip_literal_hosts_do_not_create_publisher_groups():
    assert canonical_publisher_group("https://10.0.0.5/report") == ""
    assert canonical_publisher_group("https://1.2.3.4/report") == ""
    assert canonical_publisher_group("https://[2001:db8::1]/report") == ""
