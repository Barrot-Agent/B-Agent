"""
MCP Scorer – Step 3
====================
Scores discovered MCP components for usefulness, maturity, maintenance,
interoperability, and risk.  Returns a numeric score in [0, 100] with a
breakdown per dimension.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from barrot_agent.mcp_discovery import ServerInventory
from barrot_agent.mcp_targets import CAPABILITY_TARGETS, CapabilityTarget

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Score result
# ---------------------------------------------------------------------------


@dataclass
class ComponentScore:
    """Scoring breakdown for a single MCP server inventory."""

    server_id: str
    # Sub-scores in [0, 10]
    usefulness: float = 0.0
    maturity: float = 0.0
    maintenance: float = 0.0
    interoperability: float = 0.0
    risk: float = 0.0  # Higher = *lower* risk

    @property
    def total(self) -> float:
        """
        Weighted composite score in [0, 100].

        Weights:  usefulness 30 %, maturity 20 %, maintenance 20 %,
                  interoperability 15 %, risk 15 %.
        """
        return (
            self.usefulness * 3.0
            + self.maturity * 2.0
            + self.maintenance * 2.0
            + self.interoperability * 1.5
            + self.risk * 1.5
        )

    @property
    def grade(self) -> str:
        """Letter grade derived from total score."""
        t = self.total
        if t >= 80:
            return "A"
        if t >= 65:
            return "B"
        if t >= 50:
            return "C"
        if t >= 35:
            return "D"
        return "F"

    def to_dict(self) -> Dict[str, object]:
        return {
            "server_id": self.server_id,
            "total": round(self.total, 2),
            "grade": self.grade,
            "breakdown": {
                "usefulness": round(self.usefulness, 2),
                "maturity": round(self.maturity, 2),
                "maintenance": round(self.maintenance, 2),
                "interoperability": round(self.interoperability, 2),
                "risk": round(self.risk, 2),
            },
        }


# ---------------------------------------------------------------------------
# Scorer
# ---------------------------------------------------------------------------


class MCPScorer:
    """
    Score a :class:`~barrot_agent.mcp_discovery.ServerInventory` against
    Barrot's capability targets and compatibility requirements.
    """

    # Known-good versions bump maturity (stub; extend as servers publish semver)
    _STABLE_VERSION_PREFIXES = ("1.", "2.", "3.")
    _ALLOWED_LICENSES = {"MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause"}

    def score(
        self,
        inventory: ServerInventory,
        targets: Optional[List[CapabilityTarget]] = None,
    ) -> ComponentScore:
        """Compute and return a :class:`ComponentScore` for *inventory*."""
        targets = targets or CAPABILITY_TARGETS
        cs = ComponentScore(server_id=inventory.server_id)
        cs.usefulness = self._score_usefulness(inventory, targets)
        cs.maturity = self._score_maturity(inventory)
        cs.maintenance = self._score_maintenance(inventory)
        cs.interoperability = self._score_interoperability(inventory)
        cs.risk = self._score_risk(inventory)
        logger.debug(
            "Scored %s: total=%.1f grade=%s",
            inventory.server_id,
            cs.total,
            cs.grade,
        )
        return cs

    def score_all(self, inventories: Dict[str, ServerInventory]) -> Dict[str, ComponentScore]:
        """Score every inventory in the mapping and return results keyed by server_id."""
        return {sid: self.score(inv) for sid, inv in inventories.items()}

    def rank(self, scores: Dict[str, ComponentScore]) -> List[ComponentScore]:
        """Return scores sorted descending by total (best first)."""
        return sorted(scores.values(), key=lambda s: s.total, reverse=True)

    # ------------------------------------------------------------------
    # Dimension scorers
    # ------------------------------------------------------------------

    def _score_usefulness(self, inv: ServerInventory, targets: List[CapabilityTarget]) -> float:
        """
        Measure overlap between the server's tool categories and the
        categories required by at least one capability target.
        """
        server_cats = set(inv.tool_categories)
        if not server_cats:
            return 0.0

        required_cats: set = set()
        for tgt in targets:
            required_cats.update(tgt.required_tool_categories)

        if not required_cats:
            return 5.0  # neutral when no targets defined

        overlap = len(server_cats & required_cats)
        # Scale: full overlap across all required cats → 10
        score = min(10.0, (overlap / max(len(required_cats), 1)) * 10)

        # Bonus for covering high/critical priority targets
        for tgt in targets:
            if tgt.priority in ("high", "critical"):
                if server_cats & set(tgt.required_tool_categories):
                    score = min(10.0, score + 1.0)
        return round(score, 2)

    def _score_maturity(self, inv: ServerInventory) -> float:
        """Estimate maturity from version string and tool count."""
        score = 5.0  # baseline
        v = inv.version
        if v != "unknown":
            if any(v.startswith(p) for p in self._STABLE_VERSION_PREFIXES):
                score += 3.0
            elif v.startswith("0."):
                score -= 1.0
        if len(inv.tools) >= 5:
            score += 1.0
        if len(inv.tools) >= 10:
            score += 1.0
        return round(min(max(score, 0.0), 10.0), 2)

    def _score_maintenance(self, inv: ServerInventory) -> float:
        """
        Proxy for maintenance health using homepage presence and license.
        In a real implementation this would call PyPI/GitHub APIs.
        """
        score = 5.0
        if inv.homepage:
            score += 2.0
        if inv.license in self._ALLOWED_LICENSES:
            score += 2.0
        # Penalise if too many or zero dependencies (extremes suggest poor packaging)
        n_deps = len(inv.dependencies)
        if 1 <= n_deps <= 10:
            score += 1.0
        elif n_deps == 0:
            score -= 0.5
        elif n_deps > 20:
            score -= 1.0
        return round(min(max(score, 0.0), 10.0), 2)

    def _score_interoperability(self, inv: ServerInventory) -> float:
        """
        Assess how well the server fits into Barrot's existing MCP config.
        """
        score = 5.0
        # Bonus: already listed in mcp_config.json (server_id == known id)
        known_ids = {"barrot-core-repository", "github", "filesystem", "fetch"}
        if inv.server_id in known_ids:
            score += 2.0
        # Bonus: broad category coverage
        if len(inv.tool_categories) >= 2:
            score += 1.5
        if len(inv.tools) >= 3:
            score += 1.5
        return round(min(score, 10.0), 2)

    def _score_risk(self, inv: ServerInventory) -> float:
        """
        Return a *safety* score (10 = very safe, 0 = very risky).
        High-risk security posture lowers the score.
        """
        base = 10.0
        rl = inv.security.risk_level
        if rl == "medium":
            base -= 2.0
        elif rl == "high":
            base -= 5.0
        elif rl == "critical":
            base -= 8.0

        n_cves = len(inv.security.known_cves)
        base -= min(n_cves * 1.5, 5.0)

        n_env = len(inv.security.exposed_env_vars)
        if n_env > 2:
            base -= 1.0

        return round(max(base, 0.0), 2)
