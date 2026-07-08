"""
Smoke tests for the canonical data registry.
"""

from data import registry


class TestDataRegistry:
    def test_pingpong_request_is_available(self) -> None:
        payload = registry.load_pingpong_request(force_reload=True)
        assert payload["origin"] == "barrot"
        assert payload["directive"] == "offload_pingpong"

    def test_pingpong_request_example_is_available(self) -> None:
        payload = registry.load_pingpong_request(example=True, force_reload=True)
        assert payload["origin"] == "barrot"
        assert payload["directive"] == "offload_pingpong"

    def test_registered_assets_report_pingpong_request(self) -> None:
        assets = registry.list_assets()
        assert assets["pingpong_request"]["exists"] is True
