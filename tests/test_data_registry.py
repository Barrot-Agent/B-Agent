"""
Smoke tests for the canonical data registry.
"""

from data import registry


class TestDataRegistry:
    def test_pingpong_request_example_is_available(self) -> None:
        payload = registry.load_pingpong_request(example=True, force_reload=True)
        assert payload["origin"] == "barrot"
        assert payload["directive"] == "offload_pingpong"

