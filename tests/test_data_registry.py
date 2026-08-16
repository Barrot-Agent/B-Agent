"""
Smoke tests for the canonical data registry.
"""

from data import registry


class TestDataRegistry:
    def test_pingpong_request_example_is_available(self) -> None:
        payload = registry.load_pingpong_request(example=True, force_reload=True)
        assert payload["origin"] == "barrot"
        assert payload["directive"] == "offload_pingpong"

    def test_longevity_assets_are_available(self) -> None:
        longevity = registry.load_longevity_unified(force_reload=True)
        biomarker = registry.load_biomarker_tracking(force_reload=True)
        protocols = registry.load_reprogramming_protocols(force_reload=True)

        assert longevity["research_domain"] == "longevity"
        assert biomarker["dataset_name"] == "longevity_biomarker_tracking"
        assert protocols["protocol_library"][0]["protocol_id"] == "transient-oskm-baseline"
