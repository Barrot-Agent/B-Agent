from scripts.barrot_agent import ScriptBrain


def test_tool_result_serialization_preserves_strings():
    assert ScriptBrain._serialize_tool_result("hello") == "hello"


def test_tool_result_serialization_converts_structured_values_to_json():
    result = {"success": True, "bundle_sha256": "abc123"}
    serialized = ScriptBrain._serialize_tool_result(result)

    assert isinstance(serialized, str)
    assert '"success": true' in serialized
    assert '"bundle_sha256": "abc123"' in serialized


def test_tool_result_serialization_handles_non_json_values():
    class Value:
        def __str__(self):
            return "non-json-value"

    serialized = ScriptBrain._serialize_tool_result({"value": Value()})

    assert isinstance(serialized, str)
    assert "non-json-value" in serialized
