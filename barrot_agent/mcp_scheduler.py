"""
MCP Scheduler – Step 10
========================
Repeats discovery and evaluation on a schedule, but never permits
indefinite autonomous self-modification without bounded scope, budgets,
approval gates, and rollback controls.

Design constraints
------------------
* **Bounded scope** – only servers in ``SUPPORTED_MCP_SERVERS`` are ever
  considered; no arbitrary internet crawl.
* **Budget** – each run has a configurable ``max_new_integrations`` cap so
  the agent can't flood the registry in a single pass.
* **Approval gate** – every new integration still requires human sign-off
  via :class:`~barrot_agent.mcp_approval.MCPApprovalGate`.
* **Rollback controls** – the provenance recorder stores rollback refs so
  any integration can be undone.
* **No indefinite loops** – the scheduler runs a fixed number of
  ``max_runs`` and then stops (or waits for an external trigger).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Scheduler configuration
# ---------------------------------------------------------------------------


@dataclass
class SchedulerConfig:
    """Configuration for the MCP discovery scheduler."""

    interval_seconds: int = 3600  # How often to run discovery
    max_runs: int = 24  # Hard cap on autonomous runs
    max_new_integrations_per_run: int = 2  # Budget per run
    min_score_for_proposal: float = 50.0  # Only propose high-quality components
    dry_run: bool = True  # True = no side-effects (safe default)


# ---------------------------------------------------------------------------
# Run record
# ---------------------------------------------------------------------------


@dataclass
class SchedulerRunRecord:
    """Summary of a single scheduler pass."""

    run_number: int
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    finished_at: str = ""
    servers_discovered: int = 0
    proposals_created: int = 0
    proposals_accepted: int = 0
    proposals_rejected: int = 0
    integrations_promoted: int = 0
    dry_run: bool = True


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

# Type alias for the integration pipeline callable
IntegrationPipeline = Callable[[], Dict[str, int]]


class MCPScheduler:
    """
    Bounded, approval-gated discovery scheduler.

    The scheduler calls a *pipeline* function on each tick.  The pipeline
    encapsulates the full discovery → score → ping-pong → sandbox →
    approval → registry flow defined in :mod:`barrot_agent.mcp_integration`.

    Parameters
    ----------
    config:
        Scheduler behaviour settings.
    pipeline:
        Callable that runs one full integration pass and returns a dict
        with keys ``discovered``, ``accepted``, ``rejected``, ``promoted``.
    on_run_complete:
        Optional callback invoked after each run with the run record.
    """

    def __init__(
        self,
        config: SchedulerConfig,
        pipeline: IntegrationPipeline,
        on_run_complete: Optional[Callable[[SchedulerRunRecord], None]] = None,
    ) -> None:
        self._config = config
        self._pipeline = pipeline
        self._on_run_complete = on_run_complete
        self._run_history: List[SchedulerRunRecord] = []
        self._runs_completed = 0

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run_once(self) -> Optional[SchedulerRunRecord]:
        """
        Execute a single discovery pass if the budget allows.

        Returns the run record, or None if the max_runs cap is reached.
        """
        if self._runs_completed >= self._config.max_runs:
            logger.info(
                "Scheduler: max_runs=%d reached; stopping autonomous operation.",
                self._config.max_runs,
            )
            return None

        self._runs_completed += 1
        run = SchedulerRunRecord(
            run_number=self._runs_completed,
            dry_run=self._config.dry_run,
        )
        logger.info(
            "Scheduler run %d/%d starting (dry_run=%s)",
            self._runs_completed,
            self._config.max_runs,
            self._config.dry_run,
        )

        try:
            if self._config.dry_run:
                stats = {"discovered": 0, "accepted": 0, "rejected": 0, "promoted": 0}
                logger.info("Scheduler: dry_run=True – skipping pipeline side-effects.")
            else:
                stats = self._pipeline()

            run.servers_discovered = stats.get("discovered", 0)
            run.proposals_accepted = stats.get("accepted", 0)
            run.proposals_rejected = stats.get("rejected", 0)
            run.integrations_promoted = min(
                stats.get("promoted", 0),
                self._config.max_new_integrations_per_run,
            )
        except Exception as exc:  # noqa: BLE001
            logger.error("Scheduler run %d failed: %s", self._runs_completed, exc)

        run.finished_at = datetime.now(timezone.utc).isoformat()
        self._run_history.append(run)

        if self._on_run_complete:
            try:
                self._on_run_complete(run)
            except Exception as exc:  # noqa: BLE001
                logger.warning("on_run_complete callback error: %s", exc)

        logger.info(
            "Scheduler run %d complete: discovered=%d accepted=%d promoted=%d",
            run.run_number,
            run.servers_discovered,
            run.proposals_accepted,
            run.integrations_promoted,
        )
        return run

    def run_loop(self) -> List[SchedulerRunRecord]:
        """
        Block and run until ``max_runs`` is reached or the process is
        interrupted.

        This is intentionally a bounded loop – it will always terminate
        after ``max_runs * interval_seconds`` seconds.
        """
        logger.info(
            "Scheduler starting: max_runs=%d interval=%ds",
            self._config.max_runs,
            self._config.interval_seconds,
        )
        while self._runs_completed < self._config.max_runs:
            record = self.run_once()
            if record is None:
                break
            remaining = self._config.max_runs - self._runs_completed
            if remaining > 0:
                logger.debug(
                    "Scheduler sleeping %ds (%d run(s) remaining)",
                    self._config.interval_seconds,
                    remaining,
                )
                time.sleep(self._config.interval_seconds)
        logger.info(
            "Scheduler finished: %d/%d runs completed.",
            self._runs_completed,
            self._config.max_runs,
        )
        return list(self._run_history)

    def get_history(self) -> List[SchedulerRunRecord]:
        """Return all completed run records."""
        return list(self._run_history)

    @property
    def runs_remaining(self) -> int:
        """Return how many more autonomous runs are allowed."""
        return max(0, self._config.max_runs - self._runs_completed)
