"""Configuration management for B-Agent — stdlib implementation.

Transmuted from pydantic-settings to stdlib (dataclasses + os.environ) so the
configuration layer imports on dependency-light devices (Termux, slim CI).
Contract preserved from the pydantic version:
  * precedence: init kwargs > environment variables > .env file > defaults
  * env names: uppercased field names, "__" joins nested paths (MODEL__TEMPERATURE)
  * env_file: ".env" in the current working directory (utf-8, KEY=VALUE)
  * temperature fields bounded to 0.0..2.0, invalid values raise ValueError
  * extra init kwargs / unrelated env keys are ignored
"""

from __future__ import annotations

import os
from dataclasses import MISSING, dataclass, field as dc_field, fields as dc_fields
from enum import Enum
from pathlib import Path
from typing import Any, Optional, Union, get_args, get_origin, get_type_hints

_ENV_TRUE = {"1", "true", "yes", "on"}
_ENV_FALSE = {"0", "false", "no", "off"}


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


# ge/le bounds carried over from the pydantic Field() definitions.
_BOUNDS: dict[tuple[str, str], dict[str, float]] = {
    ("ModelConfig", "temperature"): {"ge": 0.0, "le": 2.0},
    ("KimiConfig", "temperature"): {"ge": 0.0, "le": 2.0},
}


def _parse_env_file(path: Path) -> dict[str, str]:
    """Parse a dotenv-style file: KEY=VALUE, '#' comments, stripped quotes."""
    if not path.is_file():
        return {}
    out: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        out[key.strip()] = value
    return out


def _coerce(raw: str, annotation: Any, bounds: dict[str, float]) -> Any:
    """Coerce an env-file/env-var string to the annotated type."""
    origin = get_origin(annotation)
    if origin is Union:
        args = tuple(a for a in get_args(annotation) if a is not type(None))
        if len(args) == 1:
            return _coerce(raw, args[0], bounds)
    if isinstance(annotation, type) and issubclass(annotation, Enum):
        return annotation(raw)
    if annotation is bool:
        low = raw.strip().lower()
        if low in _ENV_TRUE:
            return True
        if low in _ENV_FALSE:
            return False
        raise ValueError(f"invalid boolean value: {raw!r}")
    if annotation is int:
        return int(raw)
    if annotation is float:
        return float(raw)
    return raw


def _bounded(value: Any, annotation: Any, bounds: dict[str, float], label: str) -> Any:
    """Enforce ge/le bounds for numeric fields (was pydantic Field(ge=, le=))."""
    if bounds and annotation in (int, float) and isinstance(value, (int, float)):
        if "ge" in bounds and value < bounds["ge"]:
            raise ValueError(f"{label}: {value} < ge={bounds['ge']}")
        if "le" in bounds and value > bounds["le"]:
            raise ValueError(f"{label}: {value} > le={bounds['le']}")
    return value


class _SettingsBase:
    """Minimal pydantic-settings work-alike; see module docstring for contract."""

    model_config: dict[str, Any] = {}

    def __init__(self, **kwargs: Any) -> None:
        cls = type(self)
        hints = get_type_hints(cls)
        nested_prefix: str = kwargs.pop("_nested_prefix", "")
        file_vars: dict[str, str] = kwargs.pop("_file_vars", None) or {}
        if not file_vars:
            env_file = cls.model_config.get("env_file")
            if env_file:
                file_vars = _parse_env_file(Path(env_file))
        for f in dc_fields(cls):
            name = f.name
            annotation = hints[name]
            bounds = _BOUNDS.get((cls.__name__, name), {})
            label = f"{cls.__name__}.{name}"
            if name in kwargs:
                value = kwargs.pop(name)
                if isinstance(value, str):
                    value = _coerce(value, annotation, bounds)
                value = _bounded(value, annotation, bounds, label)
            else:
                env_key = f"{nested_prefix}{name}".upper()
                raw = os.environ.get(env_key)
                if raw is None:
                    raw = file_vars.get(env_key)
                if raw is None and nested_prefix:
                    flat = name.upper()
                    raw = os.environ.get(flat) or file_vars.get(flat)
                if raw is not None:
                    value = _bounded(_coerce(raw, annotation, bounds),
                                     annotation, bounds, label)
                else:
                    sub = annotation if isinstance(annotation, type) else None
                    if sub is not None and issubclass(sub, _SettingsBase):
                        value = sub(_nested_prefix=f"{env_key}__",
                                    _file_vars=file_vars)
                    elif f.default is not MISSING:
                        value = f.default
                    elif f.default_factory is not MISSING:
                        value = f.default_factory()
                    else:
                        raise ValueError(f"{label}: required but unset")
            setattr(self, name, value)
        # extra="ignore": silently drop unknown kwargs / env keys


@dataclass(init=False, repr=False)
class ModelConfig(_SettingsBase):
    """IBM Granite model configuration."""

    model_config = {"protected_namespaces": ()}

    model_id: str = "ibm-granite/granite-4.0-3b-vision"
    model_revision: str = "main"
    tensor_type: str = "bf16"
    max_new_tokens: int = 512
    temperature: float = 0.7
    device: str = "auto"
    load_in_8bit: bool = False
    load_in_4bit: bool = False
    trust_remote_code: bool = True


@dataclass(init=False, repr=False)
class KimiConfig(_SettingsBase):
    """Kimi 3 model configuration for recursive feedback loops."""

    model_config = {"protected_namespaces": ()}

    api_key: Optional[str] = None
    api_base: str = "https://api.moonshot.cn/v1"
    model_name: str = "moonshot-v1-128k"
    max_tokens: int = 4096
    temperature: float = 0.7
    enabled: bool = False


@dataclass(init=False, repr=False)
class FeedbackLoopConfig(_SettingsBase):
    """Recursive feedback loop configuration."""

    model_config = {"protected_namespaces": ()}

    max_iterations: int = 100
    convergence_threshold: float = 0.95
    improvement_window: int = 5
    enable_auto_refinement: bool = True
    refinement_interval: int = 10
    feedback_history_limit: int = 1000


@dataclass(init=False, repr=False)
class AppConfig(_SettingsBase):
    """Main application configuration."""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "env_nested_delimiter": "__",
        "extra": "ignore",
    }

    # Environment
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False

    # Application
    app_name: str = "B-Agent"
    app_version: str = "0.1.0"
    host: str = "0.0.0.0"
    port: int = 8501

    # Hugging Face
    hf_token: Optional[str] = None
    hf_cache_dir: Optional[str] = None

    # GitHub integration (GPT Actions & MCP server)
    github_token: Optional[str] = None
    github_default_owner: Optional[str] = None
    github_default_repo: Optional[str] = None
    gpt_api_host: str = "127.0.0.1"
    gpt_api_port: int = 8502

    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = None
    log_json: bool = False

    # Model
    model: ModelConfig = dc_field(default_factory=ModelConfig)

    # Kimi 3 Integration
    kimi: KimiConfig = dc_field(default_factory=KimiConfig)

    # Feedback Loop
    feedback_loop: FeedbackLoopConfig = dc_field(default_factory=FeedbackLoopConfig)


def get_config() -> AppConfig:
    """Get the application configuration singleton."""
    return AppConfig()


# Default config instance
config = get_config()
