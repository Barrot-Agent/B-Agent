import json
from pathlib import Path


ARTIFACT = (
    Path(__file__).resolve().parents[1]
    / "research"
    / "xrp_intelligence"
    / "20261107T130152Z-japan-sbic-east-central-west-primary-identity.json"
)


def load_artifact():
    return json.loads(ARTIFACT.read_text(encoding="utf-8"))


def test_statute_names_exactly_the_three_regional_entities():
    data = load_artifact()
    law = data["identity_resolution"]["statutory_basis"]
    assert law["law_id"] == "338AC0000000101"
    assert "Tokyo" in law["article_2"]
    assert "Nagoya" in law["article_2"]
    assert "Osaka" in law["article_2"]


def test_east_entity_is_tokyo_sme_investment_company():
    data = load_artifact()
    east = data["identity_resolution"]["regional_entities"][0]
    assert east["legal_name_ja"] == "東京中小企業投資育成株式会社"
    assert east["regional_identifier"] == "SBIC East Japan"
    assert east["corporate_number"] == "9011001030621"


def test_central_entity_is_nagoya_and_has_chubu_region():
    data = load_artifact()
    central = data["identity_resolution"]["regional_entities"][1]
    assert central["legal_name_ja"] == "名古屋中小企業投資育成株式会社"
    assert central["regional_identifier"] == "SBIC Central Japan"
    assert "Aichi" in central["operating_area"]


def test_west_entity_is_osaka_and_has_western_region():
    data = load_artifact()
    west = data["identity_resolution"]["regional_entities"][2]
    assert west["legal_name_ja"] == "大阪中小企業投資育成株式会社"
    assert west["regional_identifier"] == "SBIC West Japan"
    assert "Osaka" in west["headquarters"]


def test_three_regional_entities_identify_one_another_as_sister_companies():
    data = load_artifact()
    entities = data["identity_resolution"]["regional_entities"]
    ids = {x["entity_id"] for x in entities}
    assert ids == {"SBIC_EAST_JAPAN", "SBIC_CENTRAL_JAPAN", "SBIC_WEST_JAPAN"}
    for entity in entities:
        assert set(entity["sister_companies"]) == ids - {entity["entity_id"]}


def test_sbi_holdings_is_separately_identified():
    data = load_artifact()
    sbi = data["identity_resolution"]["separate_sbi_holdings_entity"]
    assert sbi["legal_name_en"] == "SBI Holdings, Inc."
    assert sbi["established"] == "1999-07-08"
    assert "Control and management of the SBI Group" in sbi["principal_business"]
    assert data["identity_resolution"]["relationship_to_sbi_holdings"]["status"].startswith("NO_PARENT")


def test_chatgpt_mentions_are_training_not_partnership_evidence():
    data = load_artifact()
    contexts = data["chatgpt_phrase_reconciliation"]["verified_contexts"]
    assert len(contexts) == 2
    assert all("not an OpenAI partnership" in x["interpretation"] for x in contexts)
    assert data["chatgpt_phrase_reconciliation"]["status"] == "ORIGINAL_REFERENT_NOT_CONFIRMED"


def test_no_direct_xrp_relationship_or_market_feature_is_inferred():
    data = load_artifact()
    assert data["xrp_relationship_assessment"]["status"].startswith("NO_DIRECT_XRP")
    assert data["model_admission"]["admitted_to_price_features"] is False
    assert data["model_admission"]["admitted_to_forecast_features"] is False
    assert data["forecast"]["status"] == "NOT_ISSUED"
