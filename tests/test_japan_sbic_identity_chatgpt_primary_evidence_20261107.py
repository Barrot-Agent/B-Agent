import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261107T212100Z-japan-sbic-identity-chatgpt-primary-evidence.json"
)


def _record():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_japanese_sbic_artifact_is_well_formed():
    record = _record()
    assert record["schema_version"] == "1.0"
    assert record["record_type"] == "japan_sbic_legal_identity_and_chatgpt_course_reconciliation"
    assert record["mission_id"] == "xrp_intelligence_prediction_engine"
    assert record["identity_resolution"]["sbic_legal_entity_count"] == 3


def test_short_primary_source_receipts_recompute():
    record = _record()
    assert record["source_capture_contract"]["maximum_direct_quote_words_per_source"] == 25
    for source in record["sources"]:
        excerpt = source.get("excerpt")
        digest = source.get("excerpt_sha256")
        assert source["url"].startswith("https://")
        if excerpt is None:
            assert digest is None
            continue
        assert len(excerpt.split()) <= 25
        assert hashlib.sha256(excerpt.encode("utf-8")).hexdigest() == digest


def test_government_sources_name_three_distinct_legal_companies():
    record = _record()
    names = record["identity_resolution"]["legal_names"]
    assert names == [
        "Tokyo Small and Medium Business Investment & Consultation Co., Ltd.",
        "Nagoya Small and Medium Business Investment & Consultation Co., Ltd.",
        "Osaka Small and Medium Business Investment & Consultation Co., Ltd.",
    ]
    assert record["identity_resolution"]["east_central_west_labels_are_legal_names"] is False
    sources = {s["source_id"] for s in record["sources"]}
    assert "METI_SPECIAL_LAW_PRIVATE_CORPORATIONS" in sources
    assert "SME_AGENCY_2025_GUIDEBOOK" in sources


def test_sme_investment_development_purpose_is_not_sbi_holding_company_control():
    record = _record()
    names = {x["entity_id"] for x in record["entities"]}
    assert {"TOKYO_SME_INVESTMENT_DEVELOPMENT", "NAGOYA_SME_INVESTMENT_DEVELOPMENT", "OSAKA_SME_INVESTMENT_DEVELOPMENT", "SBI_HOLDINGS_INC"} <= names
    assert record["identity_resolution"]["sbic_holdings_relationship"] == "NO_AFFILIATION_ESTABLISHED_IN_REVIEWED_PRIMARY_SOURCES"
    assert "no parent, subsidiary, equity or shared-control relationship" in " ".join(record["identity_resolution"]["evidence_for_separation"]).lower()


def test_sbi_holdings_is_a_separate_1999_holding_company():
    record = _record()
    sbi = next(x for x in record["entities"] if x["entity_id"] == "SBI_HOLDINGS_INC")
    assert sbi["established"] == "1999-07-08"
    assert sbi["ticker"] == "8473"
    assert sbi["role"].startswith("Financial-services holding company")


def test_tokyo_sbic_chatgpt_pages_document_education_not_partnership():
    record = _record()
    chatgpt = record["chatgpt_phrase_resolution"]
    assert chatgpt["verified_relationship"] == "TOKYO_SBIC_EDUCATIONAL_COURSES_AND_SEMINARS_ONLY"
    assert chatgpt["openai_partnership_evidence"] is False
    training = next(s for s in record["sources"] if s["source_id"] == "TOKYO_SBIC_2025_GENERATIVE_AI_TRAINING")
    seminar = next(s for s in record["sources"] if s["source_id"] == "TOKYO_SBIC_2026_CHATGPT_SEMINAR")
    assert "general companies were not eligible" in training["paraphrase"].lower()
    assert "microsoft japan executive evangelist" in seminar["paraphrase"].lower()


def test_chatgpt_mentions_do_not_imply_sbi_holdings_or_openai_affiliation():
    record = _record()
    interpretation = record["chatgpt_phrase_resolution"]["interpretation"].lower()
    assert "do not establish" in interpretation
    assert "sbi holdings" in interpretation
    assert "openai" in interpretation


def test_sbic_identity_record_is_not_a_price_feature_or_forecast():
    record = _record()
    assert record["model_admission"]["model_eligible"] is False
    assert record["forecast_status"] == "NOT_ISSUED"
    assert record["trade_status"] == "NO_TRADE"
