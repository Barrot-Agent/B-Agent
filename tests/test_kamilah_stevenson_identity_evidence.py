from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / "data/xrp_intelligence/research_ledger_addenda/20261101T222234Z-kamilah-stevenson-identity-and-video-inventory.json"

def test_identity_match_preserves_spelling_uncertainty():
    d = json.loads(FILE.read_text(encoding="utf-8"))
    assert d["identity_update"]["new_status"] == "STRONG_MATCH_TO_CAMILLA_STEVENSON; EXACT_USER_SPELLING_STEPHENSON_NOT_VERIFIED"
    assert "channel_id" in d["public_video_inventory"]

def test_public_video_inventory_is_not_claimed_exhaustive():
    d = json.loads(FILE.read_text(encoding="utf-8"))
    assert d["public_video_inventory"]["candidate_videos"] == 11
    assert d["public_video_inventory"]["complete"] is False
    assert d["public_video_inventory"]["channel_reported_total"] == "1.3K"
