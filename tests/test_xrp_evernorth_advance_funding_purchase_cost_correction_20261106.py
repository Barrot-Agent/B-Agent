from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
OVERLAY_PATH = (
    ROOT
    / "research"
    / "xrp_intelligence"
    / "20261106T080100Z-evernorth-advance-funding-purchase-cost-correction.json"
)


def _load_relative(path: str) -> tuple[dict, str]:
    file_path = ROOT / path
    content = file_path.read_text(encoding="utf-8")
    return json.loads(content), content


def _git_blob_sha(content: str) -> str:
    data = content.encode("utf-8")
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def _get_pointer(document: object, pointer: str) -> object:
    current = document
    for token in pointer.split("/")[1:]:
        token = token.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def _set_pointer(document: object, pointer: str, value: object) -> None:
    tokens = pointer.split("/")[1:]
    current = document
    for raw in tokens[:-1]:
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    final = tokens[-1].replace("~1", "/").replace("~0", "~")
    if isinstance(current, list):
        current[int(final)] = value
    else:
        current[final] = value


@pytest.fixture(scope="module")
def overlay() -> dict:
    return json.loads(OVERLAY_PATH.read_text(encoding="utf-8"))


def test_all_corrected_source_artifacts_are_bound_to_exact_git_blobs(overlay: dict) -> None:
    for source in overlay["source_artifacts"]:
        _, current_content = _load_relative(source["path"])
        current_sha = _git_blob_sha(current_content)
        if current_sha == source["git_blob_sha"]:
            continue

        # A later append-only research correction may legitimately supersede
        # the path's current blob. Preserve and verify the exact historical
        # preimage referenced by the older overlay instead of pretending the
        # current path still contains that historical version.
        preimage_path = (
            ROOT
            / "research"
            / "xrp_intelligence"
            / "source_preimages"
            / f"{source['git_blob_sha']}.json"
        )
        assert preimage_path.is_file(), (
            f"Historical source blob {source['git_blob_sha']} for "
            f"{source['path']} is no longer present at its path and has no "
            "archived preimage."
        )
        preimage_content = preimage_path.read_text(encoding="utf-8")
        assert _git_blob_sha(preimage_content) == source["git_blob_sha"]


def test_21405m_cash_receipt_is_not_used_as_the_214m_purchase_cost(overlay: dict) -> None:
    source = overlay["source_artifacts"][0]
    original, _ = _load_relative(source["path"])
    derived = copy.deepcopy(original)

    assert original["capital_reconciliation"]["cash_subscriptions"]["advance_funding"]["cash_usd"] == 214050000

    corrections = [
        item for item in overlay["field_corrections"]
        if item["artifact_path"] == source["path"]
    ]
    assert len(corrections) == 4
    for item in corrections:
        assert _get_pointer(original, item["json_pointer"]) == item["original_value"]
        _set_pointer(derived, item["json_pointer"], item["corrected_value"])
        assert _get_pointer(derived, item["json_pointer"]) == item["corrected_value"]

    cash = derived["capital_reconciliation"]["cash_subscriptions"]
    assert cash["advance_funding"]["cash_usd"] == 214050000
    assert cash["cash_from_advance_funding_used_to_purchase_xrp_usd_rounded"] == 214000000
    assert cash["implied_cash_deployed_per_xrp_usd"] == pytest.approx(2.53657058)
    assert cash["xrp_purchased_with_that_cash"] == pytest.approx(84365876.3625)

    # The original source remains unchanged; the correction is a derived view.
    assert original["capital_reconciliation"]["cash_subscriptions"]["cash_from_advance_funding_used_to_purchase_xrp_usd_rounded"] == 214100000
    assert original["capital_reconciliation"]["cash_subscriptions"]["implied_cash_deployed_per_xrp_usd"] == pytest.approx(2.537163248325662)


def test_older_close_artifact_separates_purchase_cost_from_subscription_cash(overlay: dict) -> None:
    source = next(x for x in overlay["source_artifacts"] if "20261104T134706Z" in x["path"])
    original, _ = _load_relative(source["path"])
    derived = copy.deepcopy(original)
    corrections = [
        item for item in overlay["field_corrections"]
        if item["artifact_path"] == source["path"]
    ]
    assert len(corrections) == 2
    for item in corrections:
        assert _get_pointer(original, item["json_pointer"]) == item["original_value"]
        _set_pointer(derived, item["json_pointer"], item["corrected_value"])
    assert derived["xrp_asset_reconciliation"]["cash_funded_market_purchase"]["funding_cash_usd"] == 214000000
    assert derived["xrp_asset_reconciliation"]["cash_funded_market_purchase"]["implied_average_cost_status"].startswith("$2.53657058")
    assert derived["capital_reconciliation"]["gross_cash_components"][0]["amount_usd"] == 214050000


def test_postclose_and_reference_price_addendum_use_214m_purchase_cost(overlay: dict) -> None:
    postclose = next(x for x in overlay["source_artifacts"] if "postclose-capital" in x["path"])
    addendum = next(x for x in overlay["source_artifacts"] if "source-and-reference-price" in x["path"])
    for source in (postclose, addendum):
        original, _ = _load_relative(source["path"])
        derived = copy.deepcopy(original)
        correction = next(x for x in overlay["field_corrections"] if x["artifact_path"] == source["path"])
        assert _get_pointer(original, correction["json_pointer"]) == 214050000
        _set_pointer(derived, correction["json_pointer"], correction["corrected_value"])
        assert _get_pointer(derived, correction["json_pointer"]) == 214000000

    post, _ = _load_relative(postclose["path"])
    assert post["closing_capital_reconciliation"]["components"]["advance_subscription_cash_usd"] == 214050000
    add, _ = _load_relative(addendum["path"])
    purchase = add["capital_taxonomy"]["historical_cash_xrp_purchase"]
    assert purchase["cash_received_exact_usd"] == 214049995
    assert purchase["cash_received_under_advance_funding_subscriptions_usd"] == 214050000
    assert purchase["restricted_cash_at_2025_12_31_usd"] == 49995
    corrected_addendum = copy.deepcopy(add)
    addendum_correction = next(
        x for x in overlay["field_corrections"]
        if x["artifact_path"] == addendum["path"]
    )
    _set_pointer(corrected_addendum, addendum_correction["json_pointer"], addendum_correction["corrected_value"])
    assert corrected_addendum["capital_taxonomy"]["historical_cash_xrp_purchase"]["cash_used_usd"] == 214000000


def test_eloc_prose_correction_does_not_reclassify_cash_received_as_purchase_cost(overlay: dict) -> None:
    source = next(x for x in overlay["source_artifacts"] if "eloc-dollar-cap-correction" in x["path"])
    original, _ = _load_relative(source["path"])
    superseding = next(x for x in overlay["prose_claims_to_supersede"] if x["artifact_path"] == source["path"])
    for pointer in superseding["json_pointers"]:
        value = _get_pointer(original, pointer)
        assert isinstance(value, str)
        assert "214.05" in value or "214.05M" in value
    assert "214,000,000" in superseding["superseding_statement"]
    assert original["capital_reconciliation"]["historical_cash_xrp_purchase"]["cash_received_under_advance_funding_subscriptions_usd"] == 214050000
    assert original["capital_reconciliation"]["historical_cash_xrp_purchase"]["average_purchase_price_usd"] == pytest.approx(2.53657058)


def test_cash_receipt_purchase_cost_and_restricted_cash_reconcile_exactly(overlay: dict) -> None:
    evidence = overlay["primary_source_evidence"]
    assert evidence["advance_funding_cash_received_exact_usd"] == 214049995
    assert evidence["advance_funding_cash_received_summary_rounded_usd"] == 214050000
    assert evidence["cash_used_to_purchase_digital_assets_usd"] == 214000000
    assert evidence["restricted_cash_at_2025_12_31_usd"] == 49995
    assert evidence["advance_funding_cash_received_exact_usd"] - evidence["cash_used_to_purchase_digital_assets_usd"] == evidence["restricted_cash_at_2025_12_31_usd"]
    assert evidence["recomputed_average_price_usd_per_xrp"] == pytest.approx(2.53657058, abs=1e-8)
    assert evidence["recomputed_purchase_cost_usd"] == pytest.approx(214000000, abs=0.10)
    assert evidence["incorrect_average_if_214050000_is_used_as_purchase_cost"] > evidence["recomputed_average_price_usd_per_xrp"]


def test_preserved_cash_received_fields_are_not_overcorrected(overlay: dict) -> None:
    for preserved in overlay["preserved_fields"]["examples"]:
        document, _ = _load_relative(preserved["artifact_path"])
        assert _get_pointer(document, preserved["json_pointer"]) == preserved["expected_value"]

    assert overlay["preserved_fields"]["examples"][5]["expected_value"] == 214050000
    assert overlay["preserved_fields"]["examples"][5]["meaning"].startswith("Cash received")


def test_originals_remain_immutable_and_corrected_view_is_not_model_eligible(overlay: dict) -> None:
    assert overlay["application_contract"]["original_artifacts_mutated"] is False
    assert overlay["application_contract"]["model_eligible"] is False
    assert overlay["application_contract"]["if_any_source_blob_sha_mismatches"].startswith("Fail closed")
    assert "not a current XRP flow" in overlay["corrected_interpretation"]
    assert "source_preimages/<git_blob_sha>.json" in overlay["application_contract"]["correction_mode"]
    assert "historical, not current" in overlay["application_contract"]["correction_mode"]
    assert "neither the current source blob nor the archived preimage matches" in overlay["application_contract"]["if_any_source_blob_sha_mismatches"]
