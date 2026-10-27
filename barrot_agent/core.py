"""
Core application logic for B-Agent.
"""

from __future__ import annotations

from barrot_agent.config import AppConfig, get_config
from barrot_agent.logger import get_logger

logger = get_logger(__name__)


class BAgent:
    """Main B-Agent application class."""

    def __init__(self, config: AppConfig | None = None) -> None:
        self.config = config or get_config()
        logger.info(
            "B-Agent initialized | env=%s version=%s",
            self.config.environment,
            self.config.app_version,
        )

    def get_version(self) -> str:
        """Return the application version."""
        return self.config.app_version

    def get_model_id(self) -> str:
        """Return the configured model identifier."""
        return self.config.model.model_id

    def is_debug(self) -> bool:
        """Return whether debug mode is enabled."""
        return self.config.debug
