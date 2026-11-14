from __future__ import annotations

import hashlib
import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261106T211523Z-japan-sbic-east-central-west-identity-resolution.json"
)


def test_japanese_sbic_identity_excerpts_are_content_addressed():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    assert artifact["captured_at_utc"] == "2026-11-06T21:15:23Z"
    assert len(artifact["sources"]) == 7

    for source in artifact["sources"]:
        excerpt = source["excerpt_text"].encode("utf-8")
        assert len(excerpt) == source["excerpt_bytes"]
        assert hashlib.sha256(excerpt).hexdigest() == source["excerpt_sha256"]
        assert source["hash_scope"].startswith("SHA-256 of the stored")
        assert source["raw_source_bytes_retained"] is False


def test_statute_names_exactly_three_japanese_sbic_companies():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    findings = {item["id"]: item for item in artifact["findings"]}
    statute = next(source for source in artifact["sources"] if source["id"] == "law_article_2")

    assert "東京中小企業投資育成株式会社" in statute["excerpt_text"]
    assert "名古屋中小企業投資育成株式会社" in statute["excerpt_text"]
    assert "大阪中小企業投資育成株式会社" in statute["excerpt_text"]
    assert findings["statutory_three_company_definition"]["status"] == "primary_statute_confirmed"


def test_east_central_west_profiles_are_distinct_and_not_sbi_holdings():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    findings = {item["id"]: item for item in artifact["findings"]}

    east = findings["sbic_east"]
    central = findings["sbic_central"]
    west = findings["sbic_west"]
    assert east["regional_label"] == "SBIC East Japan"
    assert east["corporate_number"] == "9011001030621"
    assert east["capital_jpy"] == 6673400000
    assert central["regional_label"] == "SBIC Central Japan"
    assert central["capital_jpy"] == 4300800000
    assert west["regional_label"] == "SBIC West Japan"
    assert west["capital_jpy"] == 6822000000
    assert findings["sbi_holdings_distinction"]["status"] == "separate_legal_and_corporate_identity"
    assert "July 8, 1999" in next(
        source["excerpt_text"] for source in artifact["sources"] if source["id"] == "sbi_holdings_profile"
    )


def test_chatgpt_reference_is_an_investee_training_course_not_partnership_evidence():
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    finding = next(item for item in artifact["findings"] if item["id"] == "chatgpt_sbic_reference")
    training = next(source for source in artifact["sources"] if source["id"] == "tokyo_chatgpt_training")

    assert "ChatGPTの使い方" in training["excerpt_text"]
    assert "一般企業：ご受講いただけません" in training["excerpt_text"]
    assert finding["status"] == "primary_training_listing_confirmed"
    assert "not evidence of an OpenAI partnership" in finding["limits"][0]
