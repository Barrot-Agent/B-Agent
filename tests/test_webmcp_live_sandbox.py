import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "webmcp_live_sandbox.py"


def load_sandbox():
    spec = importlib.util.spec_from_file_location("barrot_webmcp_sandbox", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sandbox_import_does_not_require_playwright_installed():
    module = load_sandbox()
    assert module.EXPECTED_TOOL_NAMES


def test_sandbox_allows_only_its_local_http_origin():
    module = load_sandbox()
    assert module._is_local_sandbox_url("http://127.0.0.1:8791/landing.html")
    assert not module._is_local_sandbox_url("https://api.gumroad.com/v2/licenses/verify")
    assert not module._is_local_sandbox_url("https://prostarelite.gumroad.com/l/opvxi")
    assert not module._is_local_sandbox_url("http://localhost:8791/landing.html")
    assert not module._is_local_sandbox_url("file:///tmp/landing.html")


def test_sandbox_fails_closed_when_no_tools_register():
    module = load_sandbox()
    try:
        module._require_expected_tools([], [])
    except RuntimeError as exc:
        assert "registered zero tools" in str(exc)
    else:
        raise AssertionError("zero registered tools must fail the sandbox")


def test_sandbox_fails_closed_when_expected_tool_is_missing():
    module = load_sandbox()
    names = sorted(module.EXPECTED_TOOL_NAMES - {"getLatestXRPSignal"})
    try:
        module._require_expected_tools(names, [])
    except RuntimeError as exc:
        assert "getLatestXRPSignal" in str(exc)
    else:
        raise AssertionError("missing expected tool must fail the sandbox")


def test_sandbox_fails_closed_on_page_errors():
    module = load_sandbox()
    try:
        module._require_expected_tools(module.EXPECTED_TOOL_NAMES, ["ReferenceError: modelContext"])
    except RuntimeError as exc:
        assert "page errors" in str(exc)
    else:
        raise AssertionError("page errors must fail the sandbox")


def test_sandbox_records_unauthenticated_license_scope_and_blocks_external_network():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "unauthenticated_paywall_path_only" in source
    assert 'context.route("**/*", _route_local_only)' in source
    assert 'page.on("popup"' in source
    assert "external_network_blocked" in source
    assert "licensed_data_paths_exercised" in source


def test_sandbox_expected_tool_names_match_landing_page():
    import re

    module = load_sandbox()
    html = (ROOT / "web" / "landing.html").read_text(encoding="utf-8")
    names = set(re.findall(r'name: "([^"]+)"', html))
    assert module.EXPECTED_TOOL_NAMES == names


def test_route_handler_continues_local_requests_and_aborts_external_requests():
    module = load_sandbox()

    class Request:
        def __init__(self, url):
            self.url = url

    class Route:
        def __init__(self, url):
            self.request = Request(url)
            self.continued = False
            self.aborted = False

        def continue_(self):
            self.continued = True

        def abort(self):
            self.aborted = True

    local = Route("http://127.0.0.1:8791/landing.html")
    external = Route("https://api.gumroad.com/v2/licenses/verify")
    module._route_local_only(local)
    module._route_local_only(external)
    assert local.continued and not local.aborted
    assert external.aborted and not external.continued
