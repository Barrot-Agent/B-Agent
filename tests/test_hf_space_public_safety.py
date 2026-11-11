from pathlib import Path
import ast
import re

APP = Path(__file__).resolve().parents[1] / "hf_space" / "app.py"
SOURCE = APP.read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


def _function_source(name):
    node = next(
        item for item in TREE.body
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == name
    )
    lines = SOURCE.splitlines()
    return "\n".join(lines[node.lineno - 1:node.end_lineno])


def _class_method_source(class_name, method_name):
    cls = next(item for item in TREE.body if isinstance(item, ast.ClassDef) and item.name == class_name)
    node = next(item for item in cls.body if isinstance(item, ast.FunctionDef) and item.name == method_name)
    lines = SOURCE.splitlines()
    return "\n".join(lines[node.lineno - 1:node.end_lineno])


def _directional_action_labels(source):
    """Return BUY/SELL labels attached to actionable Streamlit controls or metrics.

    Negative safety disclaimers may mention BUY/SELL. Those words alone do not
    publish a signal and must not make this regression test fail.
    """
    labels = re.findall(
        r"""st\.(?:metric|button)\(\s*["']([^"']+)["']""",
        source,
        flags=re.IGNORECASE,
    )
    return [label for label in labels if re.search(r"\b(?:BUY|SELL)\b", label, re.IGNORECASE)]


def test_external_inference_requires_operator_opt_in_and_explicit_session_consent():
    assert "BARROT_ALLOW_EXTERNAL_INFERENCE" in SOURCE
    order = _function_source("_brain_order")
    assert "not _operator_allows_external_inference()" in order
    assert "not user_consented" in order
    assert "return [primary]" in order
    assert "order = [primary] +" not in order
    tool_loop = _function_source("barrot_tool_chat")
    assert "not _operator_allows_external_inference()" in tool_loop
    assert "not user_consented" in tool_loop
    assert tool_loop.index("raise RuntimeError") < tool_loop.index("requests.post")


def test_brain_never_sends_messages_without_both_permissions():
    think = _class_method_source("BarrotBrain", "think")
    assert "user_consented=False" in think
    assert "not _operator_allows_external_inference()" in think
    assert "not user_consented" in think
    assert "No message or chat history was sent" in think
    assert "automatic provider fallback" in think


def test_legacy_sentiment_classifier_makes_no_external_request():
    sentiment = _function_source("get_sentiment_signal")
    assert "NOT_ISSUED" in sentiment
    assert "requests.get" not in sentiment
    assert "requests.post" not in sentiment


def test_public_xrp_tab_does_not_compute_or_publish_directional_signals():
    start = SOURCE.index("# TAB 2 — XRP RESEARCH STATUS")
    end = SOURCE.index("# TAB 3 — BRAIN QUERY", start)
    tab = SOURCE[start:end]
    assert "NOT_ISSUED" in tab
    assert "get_orderbook_signal(" not in tab
    assert "get_sentiment_signal(" not in tab
    assert "Ternary.resolve" not in tab
    assert "not converted into BUY/SELL outputs" in tab
    assert _directional_action_labels(tab) == []
    assert "RUN SIGNAL CHECK" not in tab
    assert "BLENDED SIGNAL" not in tab


def test_legacy_signal_history_is_quarantined_from_public_analytics():
    start = SOURCE.index("# TAB 5 — QUARANTINED LEGACY HISTORY")
    end = SOURCE.index('if __name__ == "__main__":', start)
    tab = SOURCE[start:end]
    assert "Quarantined" in tab
    assert "fetch_signal_history(" not in tab
    assert "metric(\"🟢 BUY\"" not in tab
    assert "metric(\"🔴 SELL\"" not in tab


def test_api_tab_does_not_publish_legacy_signal_or_subscription_offer():
    start = SOURCE.index("# TAB 4 — API STATUS")
    end = SOURCE.index("# TAB 5 — QUARANTINED LEGACY HISTORY", start)
    tab = SOURCE[start:end].lower()
    assert "not_issued" in tab
    assert "xrp signal service" not in tab
    assert "gumroad" not in tab
    assert "signal_output" not in tab
    assert "no buy/sell forecast" in tab
    assert _directional_action_labels(tab) == []


def test_provider_consent_is_exposed_and_passed_to_chat_and_brain_query():
    assert "I authorize this session's messages and chat history" in SOURCE
    assert SOURCE.count("user_consented=external_inference_consent") == 3
    assert "External model inference is disabled by operator policy" in SOURCE


def test_orbitron_font_and_branding_are_preserved():
    assert "Orbitron:wght@700" in SOURCE
    assert "font-family: 'Orbitron'" in SOURCE
