from barrot_agent.evolution.source_independence import SourceIndependenceEngine


def test_groups_same_domain_as_one_source():
    engine = SourceIndependenceEngine()

    groups = engine.independent_sources(
        [
            {
                "source": "article_one",
                "source_url": "https://example.com/a",
            },
            {
                "source": "article_two",
                "source_url": "https://example.com/b",
            },
            {
                "source": "other",
                "source_url": "https://independent.org/a",
            },
        ]
    )

    assert len(groups) == 2
    assert len(groups["example.com"]) == 2
    assert len(groups["independent.org"]) == 1
