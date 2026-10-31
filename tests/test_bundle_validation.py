from barrot_agent.orchestration.bundle_validation import (
    BundleValidationError,
    validate_python_bundle,
)


def test_valid_python_bundle_is_accepted():
    result = validate_python_bundle(
        path="generated_bundle.py",
        content='def probe():\n    return "OK"\n',
    )

    assert result.valid is True
    assert result.sha256.startswith("sha256:")
    assert result.content_length > 0
    assert result.reason == ""


def test_invalid_python_bundle_is_rejected():
    result = validate_python_bundle(
        path="generated_bundle.py",
        content="def broken(:\n",
    )

    assert result.valid is False
    assert result.sha256 == ""
    assert "syntax error" in result.reason.lower()


def test_empty_bundle_path_is_rejected():
    try:
        validate_python_bundle(
            path="",
            content="x = 1\n",
        )
    except BundleValidationError as exc:
        assert "path" in str(exc).lower()
    else:
        raise AssertionError("Expected BundleValidationError")


def test_non_string_bundle_content_is_rejected():
    try:
        validate_python_bundle(
            path="generated_bundle.py",
            content=None,
        )
    except BundleValidationError as exc:
        assert "content" in str(exc).lower()
    else:
        raise AssertionError("Expected BundleValidationError")
