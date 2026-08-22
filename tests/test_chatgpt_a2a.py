"""
Tests: ChatGPT ↔ Barrot A2A integration (mocked, no live API calls).

Covers:
  1. ChatGPT connector registration / instantiation
  2. Missing OPENAI_API_KEY raises RuntimeError
  3. Successful mocked ChatGPT response + NormalizedResponse mapping
  4. Timeout handling with retry
  5. Rate-limit (429) handling with retry
  6. A2A → ChatGPT routing (agent="chatgpt")
  7. A2A → Groq default routing (agent absent)
  8. A2A authentication failure
  9. Unauthorized privileged capability rejection
 10. GitHub capability (github-write) blocked over A2A
 11. Agent Card advertises correct skills including chatgpt-relay
"""
from __future__ import annotations

import importlib
import io
import json
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_openai_response(content: str = "Hello from ChatGPT", model: str = "gpt-4o"):
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {
        "choices": [{"message": {"role": "assistant", "content": content}}],
        "model": model,
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }
    resp.raise_for_status = MagicMock()
    return resp


# ---------------------------------------------------------------------------
# Imports under test
# ---------------------------------------------------------------------------

sys.path.insert(0, ".")

from barrot_agent.chatgpt_connector import ChatGPTClient, NormalizedResponse
from barrot_agent.config import OpenAIConfig


# ---------------------------------------------------------------------------
# 1. Connector instantiation
# ---------------------------------------------------------------------------


class TestChatGPTConnectorRegistration(unittest.TestCase):
    def test_instantiation_with_key(self):
        cfg = OpenAIConfig(api_key="sk-test", model="gpt-4o")
        client = ChatGPTClient(config=cfg)
        self.assertTrue(client.is_available)
        client.close()

    def test_instantiation_without_key(self):
        cfg = OpenAIConfig(api_key=None)
        client = ChatGPTClient(config=cfg)
        self.assertFalse(client.is_available)
        client.close()


# ---------------------------------------------------------------------------
# 2. Missing OPENAI_API_KEY
# ---------------------------------------------------------------------------


class TestMissingApiKey(unittest.TestCase):
    def test_raises_runtime_error_when_key_missing(self):
        cfg = OpenAIConfig(api_key=None)
        client = ChatGPTClient(config=cfg)
        with self.assertRaises(RuntimeError) as ctx:
            client.chat("Hello")
        self.assertIn("OPENAI_API_KEY", str(ctx.exception))
        client.close()


# ---------------------------------------------------------------------------
# 3. Successful mocked response + NormalizedResponse mapping
# ---------------------------------------------------------------------------


class TestSuccessfulMockedResponse(unittest.TestCase):
    def test_normalized_response_fields(self):
        cfg = OpenAIConfig(api_key="sk-test", model="gpt-4o", max_retries=1)
        with patch("requests.Session.post", return_value=_mock_openai_response("BTC is bullish")) as mock_post:
            with ChatGPTClient(config=cfg) as client:
                result = client.chat("What is BTC doing?")

        self.assertIsInstance(result, NormalizedResponse)
        self.assertTrue(result.success)
        self.assertEqual(result.content, "BTC is bullish")
        self.assertEqual(result.role, "chatgpt")
        self.assertEqual(result.source, "external-agent")
        self.assertEqual(result.model, "gpt-4o")
        self.assertEqual(result.usage["total_tokens"], 15)
        self.assertIsNone(result.error)

    def test_to_dict_shape(self):
        cfg = OpenAIConfig(api_key="sk-test", model="gpt-4o", max_retries=1)
        with patch("requests.Session.post", return_value=_mock_openai_response("ok")):
            with ChatGPTClient(config=cfg) as client:
                d = client.chat("ping").to_dict()
        self.assertIn("success", d)
        self.assertIn("role", d)
        self.assertIn("source", d)
        self.assertIn("model", d)
        self.assertIn("usage", d)


# ---------------------------------------------------------------------------
# 4. Timeout handling with retry
# ---------------------------------------------------------------------------


class TestTimeoutHandling(unittest.TestCase):
    def test_timeout_returns_failure_after_retries(self):
        import requests as req_lib

        cfg = OpenAIConfig(api_key="sk-test", model="gpt-4o", max_retries=2, timeout=1)
        with patch("requests.Session.post", side_effect=req_lib.Timeout("timed out")):
            with patch("time.sleep"):  # speed up
                with ChatGPTClient(config=cfg) as client:
                    result = client.chat("slow query")

        self.assertFalse(result.success)
        self.assertIn("timed out", result.error)

    def test_timeout_retries_correct_count(self):
        import requests as req_lib

        cfg = OpenAIConfig(api_key="sk-test", model="gpt-4o", max_retries=3, timeout=1)
        with patch("requests.Session.post", side_effect=req_lib.Timeout("timed out")) as mock_post:
            with patch("time.sleep"):
                with ChatGPTClient(config=cfg) as client:
                    client.chat("slow")
        self.assertEqual(mock_post.call_count, 3)


# ---------------------------------------------------------------------------
# 5. Rate-limit (429) handling
# ---------------------------------------------------------------------------


class TestRateLimitHandling(unittest.TestCase):
    def test_429_retries_and_fails(self):
        rate_resp = MagicMock()
        rate_resp.status_code = 429
        rate_resp.headers = {"Retry-After": "0"}
        rate_resp.raise_for_status = MagicMock()
        import requests as req_lib
        rate_resp.raise_for_status.side_effect = req_lib.HTTPError("429", response=rate_resp)

        cfg = OpenAIConfig(api_key="sk-test", model="gpt-4o", max_retries=2, timeout=1)
        with patch("requests.Session.post", return_value=rate_resp):
            with patch("time.sleep"):
                with ChatGPTClient(config=cfg) as client:
                    result = client.chat("rate-limited")
        self.assertFalse(result.success)


# ---------------------------------------------------------------------------
# 6. A2A → ChatGPT routing
# ---------------------------------------------------------------------------


class TestA2AChatGPTRouting(unittest.TestCase):
    def _make_a2a_request(self, params: dict, secret: str = "testsecret") -> dict:
        """Drive the A2A handler in-process."""
        import importlib.util, pathlib
        spec = importlib.util.spec_from_file_location(
            "a2a_server",
            str(pathlib.Path(__file__).parent.parent / "scripts" / "a2a_server.py"),
        )
        mod = importlib.util.load_from_spec = None  # guard
        # Load via exec to avoid module-level sys.exit check
        with open(pathlib.Path(__file__).parent.parent / "scripts" / "a2a_server.py") as f:
            src = f.read()
        ns: dict = {}
        # Patch sys.exit to prevent startup guard from killing us
        with patch("sys.exit"):
            exec(compile(src, "a2a_server.py", "exec"), ns)  # noqa: S102

        # Patch BRAIN_SECRET and GROQ_KEY
        ns["BRAIN_SECRET"] = secret
        ns["GROQ_KEY"] = "fake-groq"

        body = json.dumps({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "message/send",
            "params": params,
        }).encode()

        rfile = io.BytesIO(body)
        wfile = io.BytesIO()

        handler = ns["A2AHandler"].__new__(ns["A2AHandler"])
        handler.client_address = ("127.0.0.1", 9999)
        handler.headers = {
            "X-Barrot-Auth": secret,
            "Content-Length": str(len(body)),
            "Content-Type": "application/json",
        }
        handler.rfile = rfile
        handler.wfile = wfile
        handler.path = "/"

        # Stub HTTP primitives
        handler._headers_buffer = []
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()

        return handler, wfile, ns

    def test_chatgpt_agent_calls_call_chatgpt(self):
        params = {
            "agent": "chatgpt",
            "message": {"parts": [{"type": "text", "text": "Hello ChatGPT"}]},
        }
        handler, wfile, ns = self._make_a2a_request(params)

        mock_result = {
            "success": True,
            "content": "Hi from ChatGPT",
            "role": "chatgpt",
            "source": "external-agent",
            "model": "gpt-4o",
            "usage": {},
            "error": None,
        }
        ns["call_chatgpt"] = MagicMock(return_value=mock_result)
        ns["call_groq"] = MagicMock(side_effect=AssertionError("should not be called"))

        handler.do_POST()

        ns["call_chatgpt"].assert_called_once_with("Hello ChatGPT")
        wfile.seek(0)
        resp = json.loads(wfile.read())
        self.assertIn("result", resp)
        parts = resp["result"]["artifacts"][0]["parts"]
        text_parts = [p for p in parts if p.get("type") == "text"]
        self.assertEqual(text_parts[0]["text"], "Hi from ChatGPT")


# ---------------------------------------------------------------------------
# 7. A2A → Groq default routing
# ---------------------------------------------------------------------------


class TestA2AGroqDefaultRouting(unittest.TestCase):
    def test_no_agent_param_calls_call_groq(self):
        import importlib.util, pathlib

        with open(pathlib.Path(__file__).parent.parent / "scripts" / "a2a_server.py") as f:
            src = f.read()
        ns: dict = {}
        with patch("sys.exit"):
            exec(compile(src, "a2a_server.py", "exec"), ns)  # noqa: S102

        secret = "testsecret"
        ns["BRAIN_SECRET"] = secret
        ns["GROQ_KEY"] = "fake-groq"
        ns["call_groq"] = MagicMock(return_value="groq reply")
        ns["call_chatgpt"] = MagicMock(side_effect=AssertionError("should not be called"))

        body = json.dumps({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "message/send",
            "params": {"message": {"parts": [{"type": "text", "text": "hello"}]}},
        }).encode()

        handler = ns["A2AHandler"].__new__(ns["A2AHandler"])
        handler.client_address = ("127.0.0.1", 9999)
        handler.headers = {
            "X-Barrot-Auth": secret,
            "Content-Length": str(len(body)),
        }
        handler.rfile = io.BytesIO(body)
        wfile = io.BytesIO()
        handler.wfile = wfile
        handler.path = "/"
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()

        handler.do_POST()
        ns["call_groq"].assert_called_once_with("hello")


# ---------------------------------------------------------------------------
# 8. A2A authentication failure
# ---------------------------------------------------------------------------


class TestA2AAuthFailure(unittest.TestCase):
    def test_wrong_secret_returns_unauthorized(self):
        import importlib.util, pathlib

        with open(pathlib.Path(__file__).parent.parent / "scripts" / "a2a_server.py") as f:
            src = f.read()
        ns: dict = {}
        with patch("sys.exit"):
            exec(compile(src, "a2a_server.py", "exec"), ns)  # noqa: S102

        ns["BRAIN_SECRET"] = "correct-secret"
        ns["GROQ_KEY"] = "fake-groq"

        body = json.dumps({"jsonrpc": "2.0", "id": 3, "method": "message/send", "params": {}}).encode()
        handler = ns["A2AHandler"].__new__(ns["A2AHandler"])
        handler.client_address = ("127.0.0.1", 9999)
        handler.headers = {
            "X-Barrot-Auth": "wrong-secret",
            "Content-Length": str(len(body)),
        }
        handler.rfile = io.BytesIO(body)
        wfile = io.BytesIO()
        handler.wfile = wfile
        handler.path = "/"
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()

        handler.do_POST()
        wfile.seek(0)
        resp = json.loads(wfile.read())
        self.assertIn("error", resp)
        self.assertEqual(resp["error"]["code"], -32001)
        self.assertIn("Unauthorized", resp["error"]["message"])


# ---------------------------------------------------------------------------
# 9. Unauthorized privileged capability rejection
# ---------------------------------------------------------------------------


class TestPrivilegedCapabilityRejection(unittest.TestCase):
    def _run_with_capability(self, capability: str) -> dict:
        import pathlib

        with open(pathlib.Path(__file__).parent.parent / "scripts" / "a2a_server.py") as f:
            src = f.read()
        ns: dict = {}
        with patch("sys.exit"):
            exec(compile(src, "a2a_server.py", "exec"), ns)  # noqa: S102

        secret = "s"
        ns["BRAIN_SECRET"] = secret
        ns["GROQ_KEY"] = "fake"

        body = json.dumps({
            "jsonrpc": "2.0", "id": 4, "method": "message/send",
            "params": {
                "capability": capability,
                "message": {"parts": [{"type": "text", "text": "do it"}]},
            },
        }).encode()

        handler = ns["A2AHandler"].__new__(ns["A2AHandler"])
        handler.client_address = ("127.0.0.1", 9)
        handler.headers = {"X-Barrot-Auth": secret, "Content-Length": str(len(body))}
        handler.rfile = io.BytesIO(body)
        wfile = io.BytesIO()
        handler.wfile = wfile
        handler.path = "/"
        handler.send_response = MagicMock()
        handler.send_header = MagicMock()
        handler.end_headers = MagicMock()
        handler.do_POST()
        wfile.seek(0)
        return json.loads(wfile.read())

    def test_mcp_execute_rejected(self):
        resp = self._run_with_capability("mcp-execute")
        self.assertIn("error", resp)
        self.assertEqual(resp["error"]["code"], -32003)

    def test_production_deploy_rejected(self):
        resp = self._run_with_capability("production-deploy")
        self.assertIn("error", resp)

    def test_natural_language_permitted(self):
        import pathlib

        with open(pathlib.Path(__file__).parent.parent / "scripts" / "a2a_server.py") as f:
            src = f.read()
        ns: dict = {}
        with patch("sys.exit"):
            exec(compile(src, "a2a_server.py", "exec"), ns)  # noqa: S102
        # _check_capability is defined in ns
        self.assertTrue(ns["_check_capability"]("natural-language"))

    def test_privileged_capabilities_blocked(self):
        import pathlib

        with open(pathlib.Path(__file__).parent.parent / "scripts" / "a2a_server.py") as f:
            src = f.read()
        ns: dict = {}
        with patch("sys.exit"):
            exec(compile(src, "a2a_server.py", "exec"), ns)  # noqa: S102
        for cap in ("github-write", "mcp-execute", "production-deploy"):
            self.assertFalse(ns["_check_capability"](cap), cap)


# ---------------------------------------------------------------------------
# 10. GitHub capability authorization
# ---------------------------------------------------------------------------


class TestGitHubCapabilityAuthorization(unittest.TestCase):
    def test_github_read_permitted(self):
        import pathlib

        with open(pathlib.Path(__file__).parent.parent / "scripts" / "a2a_server.py") as f:
            src = f.read()
        ns: dict = {}
        with patch("sys.exit"):
            exec(compile(src, "a2a_server.py", "exec"), ns)  # noqa: S102
        self.assertTrue(ns["_check_capability"]("github-read"))

    def test_github_write_blocked(self):
        import pathlib

        with open(pathlib.Path(__file__).parent.parent / "scripts" / "a2a_server.py") as f:
            src = f.read()
        ns: dict = {}
        with patch("sys.exit"):
            exec(compile(src, "a2a_server.py", "exec"), ns)  # noqa: S102
        self.assertFalse(ns["_check_capability"]("github-write"))


# ---------------------------------------------------------------------------
# 11. Agent Card capability accuracy
# ---------------------------------------------------------------------------


class TestAgentCardCapabilityAccuracy(unittest.TestCase):
    def _load_agent_card(self) -> dict:
        import pathlib

        with open(pathlib.Path(__file__).parent.parent / "scripts" / "a2a_server.py") as f:
            src = f.read()
        ns: dict = {}
        with patch("sys.exit"):
            exec(compile(src, "a2a_server.py", "exec"), ns)  # noqa: S102
        return ns["AGENT_CARD"]

    def test_agent_card_has_chatgpt_relay_skill(self):
        card = self._load_agent_card()
        skill_ids = {s["id"] for s in card["skills"]}
        self.assertIn("chatgpt-relay", skill_ids)

    def test_agent_card_has_natural_language_skill(self):
        card = self._load_agent_card()
        skill_ids = {s["id"] for s in card["skills"]}
        self.assertIn("natural-language", skill_ids)

    def test_agent_card_has_github_read_skill(self):
        card = self._load_agent_card()
        skill_ids = {s["id"] for s in card["skills"]}
        self.assertIn("github-read", skill_ids)

    def test_agent_card_has_mcp_read_skill(self):
        card = self._load_agent_card()
        skill_ids = {s["id"] for s in card["skills"]}
        self.assertIn("mcp-read", skill_ids)

    def test_agent_card_does_not_advertise_privileged_skills(self):
        card = self._load_agent_card()
        skill_ids = {s["id"] for s in card["skills"]}
        for priv in ("github-write", "mcp-execute", "production-deploy"):
            self.assertNotIn(priv, skill_ids, f"Privileged skill '{priv}' should not be advertised")

    def test_agent_card_version_updated(self):
        card = self._load_agent_card()
        self.assertNotEqual(card["version"], "1.0.0", "Agent Card version should reflect the update")

    def test_agent_card_auth_references_env_var(self):
        card = self._load_agent_card()
        self.assertIn("BRAIN_SHARED_SECRET", card["authentication"]["credentials"])


if __name__ == "__main__":
    unittest.main()
