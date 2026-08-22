"""
Configuration management for B-Agent using Pydantic.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class ModelConfig(BaseSettings):
    """IBM Granite model configuration."""

    model_config = SettingsConfigDict(protected_namespaces=())

    model_id: str = Field(
        default="ibm-granite/granite-4.0-3b-vision",
        description="Hugging Face model identifier",
    )
    model_revision: str = Field(default="main", description="Model revision/branch")
    tensor_type: str = Field(default="bf16", description="Tensor precision type")
    max_new_tokens: int = Field(default=512, description="Maximum new tokens to generate")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    device: str = Field(default="auto", description="Device for model inference")
    load_in_8bit: bool = Field(default=False, description="Load model in 8-bit quantization")
    load_in_4bit: bool = Field(default=False, description="Load model in 4-bit quantization")
    trust_remote_code: bool = Field(default=True, description="Trust remote code for custom models")


class OpenAIConfig(BaseSettings):
    """OpenAI / ChatGPT connector configuration."""

    model_config = SettingsConfigDict(
        protected_namespaces=(),
        env_prefix="OPENAI_",
    )

    api_key: Optional[str] = Field(default=None, description="OpenAI API key (OPENAI_API_KEY)")
    base_url: str = Field(
        default="https://api.openai.com/v1",
        description="OpenAI-compatible API base URL (OPENAI_BASE_URL)",
    )
    model: str = Field(default="gpt-4o", description="Model identifier (OPENAI_MODEL)")
    timeout: int = Field(default=60, description="Request timeout seconds (OPENAI_TIMEOUT)")
    max_retries: int = Field(default=3, description="Max retry attempts (OPENAI_MAX_RETRIES)")
    enabled: bool = Field(default=False, description="Enable ChatGPT connector")


class KimiConfig(BaseSettings):
    """Kimi 3 model configuration for recursive feedback loops."""

    model_config = SettingsConfigDict(protected_namespaces=())

    api_key: Optional[str] = Field(default=None, description="Kimi API key")
    api_base: str = Field(
        default="https://api.moonshot.cn/v1",
        description="Kimi API base URL",
    )
    model_name: str = Field(default="moonshot-v1-128k", description="Kimi model name")
    max_tokens: int = Field(default=4096, description="Maximum tokens to generate")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")
    enabled: bool = Field(default=False, description="Enable Kimi integration")


class FeedbackLoopConfig(BaseSettings):
    """Recursive feedback loop configuration."""

    model_config = SettingsConfigDict(protected_namespaces=())

    max_iterations: int = Field(
        default=100, description="Maximum feedback loop iterations"
    )
    convergence_threshold: float = Field(
        default=0.95, description="Convergence threshold for improvement metrics"
    )
    improvement_window: int = Field(
        default=5, description="Window for tracking improvement trends"
    )
    enable_auto_refinement: bool = Field(
        default=True, description="Enable automatic infrastructure refinement"
    )
    refinement_interval: int = Field(
        default=10, description="Run refinement every N iterations"
    )
    feedback_history_limit: int = Field(
        default=1000, description="Maximum feedback history entries to retain"
    )


class AppConfig(BaseSettings):
    """Main application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    # Environment
    environment: Environment = Field(
        default=Environment.DEVELOPMENT, description="Runtime environment"
    )
    debug: bool = Field(default=False, description="Enable debug mode")

    # Application
    app_name: str = Field(default="B-Agent", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8501, description="Server port")

    # Hugging Face
    hf_token: Optional[str] = Field(default=None, description="Hugging Face API token")
    hf_cache_dir: Optional[str] = Field(default=None, description="Hugging Face cache directory")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    log_json: bool = Field(default=False, description="Enable JSON structured logging")

    # Model
    model: ModelConfig = Field(default_factory=ModelConfig)

    # Kimi 3 Integration
    kimi: KimiConfig = Field(default_factory=KimiConfig)

    # OpenAI / ChatGPT Integration
    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)

    # Feedback Loop
    feedback_loop: FeedbackLoopConfig = Field(default_factory=FeedbackLoopConfig)


def get_config() -> AppConfig:
    """Get the application configuration singleton."""
    return AppConfig()


# Default config instance
config = get_config()
