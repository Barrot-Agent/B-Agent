"""Contract tests for barrot_agent.config (transmute rule 6: test first).

Pins the observable contract that must survive any transmutation of the
config layer: field defaults, precedence (kwargs > env > .env > default),
type coercion, bounds validation, nested access, extra-ignore.

stdlib-only so it runs under unittest (transmute loop) and pytest alike.
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from barrot_agent.config import (
    AppConfig,
    Environment,
    KimiConfig,
    ModelConfig,
    config as module_config,
    get_config,
)

# Env keys the config layer legitimately reads — must be absent for
# default-value assertions regardless of what the host device exports.
_CONFIG_ENV_KEYS = [
    "APP_NAME", "APP_VERSION", "HOST", "PORT", "DEBUG", "ENVIRONMENT",
    "LOG_LEVEL", "LOG_FILE", "LOG_JSON", "HF_TOKEN", "HF_CACHE_DIR",
    "GITHUB_TOKEN", "GITHUB_DEFAULT_OWNER", "GITHUB_DEFAULT_REPO",
    "GPT_API_HOST", "GPT_API_PORT",
    "MODEL_ID", "MODEL_REVISION", "TENSOR_TYPE", "MAX_NEW_TOKENS",
    "TEMPERATURE", "DEVICE", "LOAD_IN_8BIT", "LOAD_IN_4BIT",
    "TRUST_REMOTE_CODE", "MODEL__TEMPERATURE",
]


class TestDefaults(unittest.TestCase):
    def test_model_defaults(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            for k in _CONFIG_ENV_KEYS:
                os.environ.pop(k, None)
            c = ModelConfig()
        self.assertEqual(c.model_id, "ibm-granite/granite-4.0-3b-vision")
        self.assertEqual(c.model_revision, "main")
        self.assertEqual(c.tensor_type, "bf16")
        self.assertEqual(c.max_new_tokens, 512)
        self.assertEqual(c.temperature, 0.7)
        self.assertEqual(c.device, "auto")
        self.assertIs(c.load_in_8bit, False)
        self.assertIs(c.trust_remote_code, True)

    def test_app_defaults(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            for k in _CONFIG_ENV_KEYS:
                os.environ.pop(k, None)
            c = AppConfig()
        self.assertIs(c.environment, Environment.DEVELOPMENT)
        self.assertIs(c.debug, False)
        self.assertEqual(c.app_name, "B-Agent")
        self.assertEqual(c.app_version, "0.1.0")
        self.assertEqual(c.host, "0.0.0.0")
        self.assertEqual(c.port, 8501)
        self.assertIsNone(c.hf_token)
        self.assertIsNone(c.github_token)
        self.assertEqual(c.gpt_api_host, "127.0.0.1")
        self.assertEqual(c.gpt_api_port, 8502)
        self.assertEqual(c.log_level, "INFO")
        self.assertIs(c.log_json, False)

    def test_nested_defaults(self):
        with mock.patch.dict(os.environ, {}, clear=False):
            for k in _CONFIG_ENV_KEYS:
                os.environ.pop(k, None)
            c = AppConfig()
        self.assertEqual(c.model.model_id, "ibm-granite/granite-4.0-3b-vision")
        self.assertIs(c.kimi.enabled, False)
        self.assertEqual(c.kimi.api_base, "https://api.moonshot.cn/v1")
        self.assertEqual(c.feedback_loop.max_iterations, 100)
        self.assertEqual(c.feedback_loop.convergence_threshold, 0.95)

    def test_environment_values(self):
        self.assertEqual(Environment.DEVELOPMENT, "development")
        self.assertEqual(Environment.STAGING, "staging")
        self.assertEqual(Environment.PRODUCTION, "production")


class TestConstruction(unittest.TestCase):
    def test_kwargs_override(self):
        c = AppConfig(environment=Environment.DEVELOPMENT, debug=True)
        self.assertIs(c.debug, True)
        self.assertEqual(ModelConfig(temperature=0.5).temperature, 0.5)

    def test_temperature_out_of_range_raises(self):
        with self.assertRaises(Exception):
            ModelConfig(temperature=3.0)
        with self.assertRaises(Exception):
            ModelConfig(temperature=-0.1)
        with self.assertRaises(Exception):
            KimiConfig(temperature=2.5)

    def test_unknown_kwarg_ignored(self):
        c = AppConfig(totally_unknown_key=123)
        self.assertEqual(c.app_name, "B-Agent")

    def test_string_kwargs_coerced(self):
        c = AppConfig(environment="production", port="9999")
        self.assertIs(c.environment, Environment.PRODUCTION)
        self.assertEqual(c.port, 9999)

    def test_get_config_and_module_instance(self):
        self.assertIsInstance(get_config(), AppConfig)
        self.assertIsInstance(module_config, AppConfig)


class TestEnvironmentSources(unittest.TestCase):
    def test_env_override_scalars(self):
        env = {"APP_NAME": "Custom", "PORT": "9999", "DEBUG": "true",
               "LOG_LEVEL": "DEBUG"}
        with mock.patch.dict(os.environ, env, clear=False):
            c = AppConfig()
        self.assertEqual(c.app_name, "Custom")
        self.assertEqual(c.port, 9999)
        self.assertIs(c.debug, True)
        self.assertEqual(c.log_level, "DEBUG")

    def test_env_override_nested(self):
        with mock.patch.dict(os.environ, {"MODEL__TEMPERATURE": "1.25"}):
            c = AppConfig()
        self.assertEqual(c.model.temperature, 1.25)

    def test_env_enum_coercion(self):
        with mock.patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            c = AppConfig()
        self.assertIs(c.environment, Environment.PRODUCTION)

    def test_invalid_bool_env_raises(self):
        with mock.patch.dict(os.environ, {"DEBUG": "banana"}):
            with self.assertRaises(Exception):
                AppConfig()

    def test_extra_env_keys_ignored(self):
        env = {"TOTALLY_UNRELATED": "x", "PATH": os.environ.get("PATH", "")}
        with mock.patch.dict(os.environ, env, clear=False):
            c = AppConfig()
        self.assertEqual(c.app_name, "B-Agent")

    def test_dotenv_used_when_env_absent(self):
        old_cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                os.chdir(tmp)
                Path(".env").write_text('APP_NAME="FromDotEnv"\nPORT=7777\n')
                c = AppConfig()
            self.assertEqual(c.app_name, "FromDotEnv")
            self.assertEqual(c.port, 7777)
        finally:
            os.chdir(old_cwd)

    def test_env_var_beats_dotenv(self):
        old_cwd = os.getcwd()
        try:
            with tempfile.TemporaryDirectory() as tmp:
                os.chdir(tmp)
                Path(".env").write_text("APP_NAME=FromDotEnv\n")
                with mock.patch.dict(os.environ, {"APP_NAME": "FromEnv"}):
                    c = AppConfig()
            self.assertEqual(c.app_name, "FromEnv")
        finally:
            os.chdir(old_cwd)


if __name__ == "__main__":
    unittest.main()
