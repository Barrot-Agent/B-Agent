from barrot_agent.ingestion.riemann_harvest import (
    classify_evidence,
    merge_records,
    parse_arxiv_atom,
)


def test_evidence_classes():
    assert classify_evidence("Numerical verification", "") == "computational_evidence"
    assert classify_evidence("A new conjecture", "") == "conjecture_or_hypothesis"
    assert classify_evidence("Proof of RH", "") == "published_claim"


def test_merge_is_append_safe():
    records = merge_records(
        [{"id": "x", "title": "old"}],
        [{"id": "x", "title": "new"}, {"id": "y", "title": "other"}],
    )
    assert len(records) == 2
    assert any(r["id"] == "x" and r["title"] == "new" for r in records)


def test_atom_parser():
    xml = """<entry>
      <id>http://arxiv.org/abs/1234</id>
      <published>2026-01-01T00:00:00Z</published>
      <title>Riemann Hypothesis Research</title>
      <summary>A conjecture concerning zeros.</summary>
      <author><name>Researcher</name></author>
    </entry>"""
    records = parse_arxiv_atom(xml)
    assert len(records) == 1
    assert records[0]["evidence_class"] == "conjecture_or_hypothesis"
