from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "data/xrp_intelligence/research_ledger_addenda/20261102T003705Z-kamilah-stevenson-public-identity-and-inventory-scope.json"


def test_canonical_creator_identity_is_kamilah_stevenson():
    d = json.loads(FILE.read_text(encoding="utf-8"))
    identity = d["identity_resolution"]
    assert identity["canonical_name"] == "Dr. Kamilah Stevenson"
    assert identity["channel_handle"] == "@drkamilahstevenson"
    assert identity["channel_id_verification"].startswith("UNVERIFIED")
    assert "Camilla" in identity["transcript_name_variant"]


def test_public_video_inventory_includes_all_requested_formats_without_claiming_completeness():
    d = json.loads(FILE.read_text(encoding="utf-8"))
    inventory = d["public_video_inventory"]
    assert inventory["scope"] == ["videos", "shorts", "livestreams"]
    assert inventory["candidate_uploads"] == 11
    assert inventory["complete"] is False
    assert inventory["exhaustive_enumeration"] is False
    assert inventory["channel_reported_total"] == "1.3K"
