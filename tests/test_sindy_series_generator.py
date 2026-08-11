import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "scripts" / "sindy_series_generator.py"
SPEC = importlib.util.spec_from_file_location("sindy_series_generator", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_parse_script_response_accepts_markdown_json():
    assert MODULE.parse_script_response('```json\n{"title": "Pilot"}\n```') == {
        "title": "Pilot"
    }


def test_parse_script_response_accepts_plain_code_fence():
    assert MODULE.parse_script_response('```\n{"title": "Pilot"}\n```') == {
        "title": "Pilot"
    }


def test_parse_script_response_extracts_json_from_model_prose():
    assert MODULE.parse_script_response('Here is the script:\n{"title": "Pilot"}') == {
        "title": "Pilot"
    }


def test_manifest_marks_external_assets_for_review():
    manifest = MODULE.build_episode_manifest(
        1, "Pilot", {"title": "Pilot"}, ["https://example.test/asset.glb"]
    )

    assert manifest["render"]["quality"] == "cinematic"
    assert manifest["assets"][0]["status"] == "pending_review"
    assert manifest["provenance"]["requires_asset_license_review"] is True
