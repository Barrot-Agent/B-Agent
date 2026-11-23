"""Fail-closed primary mission registry for Barrot's learning curriculum."""

from __future__ import annotations

import json
from importlib.resources import files as package_files
from pathlib import Path
from typing import Any


DEFAULT_MISSION_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "missions"
    / "primary_mission.json"
)


class MissionRegistryError(ValueError):
    """Raised when the primary mission manifest is missing or unsafe."""


class MissionRegistry:
    """Load and prioritize the repository's declared primary mission."""

    def __init__(self, manifest_path: str | Path | None = None) -> None:
        self.manifest_path = Path(manifest_path or DEFAULT_MISSION_PATH)
        self.manifest = self._load_manifest()

    def _read_manifest_text(self) -> str:
        if self.manifest_path.is_file():
            return self.manifest_path.read_text(encoding="utf-8")

        # Source checkouts keep the operator-facing manifest at the repository
        # root. Installed wheels do not include that root-level directory, so
        # fall back to the explicitly packaged resource without weakening the
        # fail-closed validation below.
        if self.manifest_path == DEFAULT_MISSION_PATH:
            try:
                resource = package_files("barrot_agent").joinpath(
                    "data", "missions", "primary_mission.json"
                )
                if resource.is_file():
                    return resource.read_text(encoding="utf-8")
            except (ModuleNotFoundError, OSError):
                pass

        raise MissionRegistryError(
            f"Primary mission manifest is missing: {self.manifest_path}"
        )

    def _load_manifest(self) -> dict[str, Any]:
        try:
            payload = json.loads(self._read_manifest_text())
        except MissionRegistryError:
            raise
        except (OSError, json.JSONDecodeError) as exc:
            raise MissionRegistryError(
                f"Primary mission manifest cannot be read: {exc}"
            ) from exc

        if not isinstance(payload, dict):
            raise MissionRegistryError("Primary mission manifest must be an object.")

        if payload.get("schema_version") != "barrot.primary-mission.v1":
            raise MissionRegistryError("Unsupported primary mission schema.")

        if not isinstance(payload.get("mission_id"), str) or not payload["mission_id"].strip():
            raise MissionRegistryError("Primary mission id is required.")

        if not isinstance(payload.get("title"), str) or not payload["title"].strip():
            raise MissionRegistryError("Primary mission title is required.")

        if type(payload.get("priority")) is not int or payload["priority"] != 1:
            raise MissionRegistryError("The primary mission must have priority 1.")

        if payload.get("status") not in {"active", "paused", "complete"}:
            raise MissionRegistryError("Primary mission status is invalid.")

        foundation = payload.get("foundation")
        if (
            not isinstance(foundation, dict)
            or foundation.get("id") != "barrot_v3"
            or foundation.get("preserve") is not True
        ):
            raise MissionRegistryError(
                "Barrot V3 must remain the preserved execution foundation."
            )

        invariants = foundation.get("invariants")
        if not isinstance(invariants, list) or not all(
            isinstance(item, str) and item.strip() for item in invariants
        ):
            raise MissionRegistryError("Barrot V3 foundation invariants are required.")

        guardrails = payload.get("guardrails")
        if not isinstance(guardrails, list) or not all(
            isinstance(item, str) and item.strip() for item in guardrails
        ):
            raise MissionRegistryError("Primary mission guardrails are required.")

        normalized_guardrails = " ".join(guardrails).lower()
        if "directional forecast" not in normalized_guardrails or "real-money" not in normalized_guardrails:
            raise MissionRegistryError(
                "Forecast and real-money safety guardrails are mandatory."
            )

        workstreams = payload.get("workstreams")
        if not isinstance(workstreams, list) or not workstreams:
            raise MissionRegistryError("At least one primary mission workstream is required.")

        seen_topics: set[str] = set()
        seen_priorities: set[int] = set()
        for workstream in workstreams:
            if not isinstance(workstream, dict):
                raise MissionRegistryError("Every workstream must be an object.")
            topic_id = workstream.get("topic_id")
            priority = workstream.get("priority")
            if not isinstance(topic_id, str) or not topic_id.strip():
                raise MissionRegistryError("Every workstream needs a topic id.")
            if type(priority) is not int or priority < 1:
                raise MissionRegistryError(f"Invalid workstream priority for {topic_id}.")
            if topic_id in seen_topics or priority in seen_priorities:
                raise MissionRegistryError("Workstream topic ids and priorities must be unique.")
            if not isinstance(workstream.get("goal"), str) or not workstream["goal"].strip():
                raise MissionRegistryError(f"Workstream goal is required for {topic_id}.")
            seen_topics.add(topic_id)
            seen_priorities.add(priority)

        acceptance = payload.get("acceptance_criteria")
        if not isinstance(acceptance, list) or not acceptance or not all(
            isinstance(item, str) and item.strip() for item in acceptance
        ):
            raise MissionRegistryError("Primary mission acceptance criteria are required.")

        continuation = payload.get("continuation_goal")
        if (
            not isinstance(continuation, dict)
            or not isinstance(continuation.get("topic_id"), str)
            or not continuation["topic_id"].strip()
            or not isinstance(continuation.get("goal"), str)
            or not continuation["goal"].strip()
        ):
            raise MissionRegistryError("A continuous primary-mission goal is required.")

        portfolio = payload.get("mission_portfolio")
        if (
            not isinstance(portfolio, dict)
            or portfolio.get("schema_version") != "barrot.mission-portfolio.v1"
            or portfolio.get("scheduling_policy") != "durable_round_robin_v1"
        ):
            raise MissionRegistryError(
                "A versioned co-equal mission portfolio with durable round-robin scheduling is required."
            )

        missions = portfolio.get("missions")
        expected_mission_ids = {
            payload["mission_id"],
            "professional_audio_production",
            "long_horizon_continuity_capability_development",
        }
        if not isinstance(missions, list) or len(missions) != 3:
            raise MissionRegistryError("Exactly three co-equal highest-priority missions are required.")

        seen_mission_ids: set[str] = set()
        for mission in missions:
            if not isinstance(mission, dict):
                raise MissionRegistryError("Every co-equal mission must be an object.")
            mission_id = mission.get("mission_id")
            if not isinstance(mission_id, str) or not mission_id.strip():
                raise MissionRegistryError("Every co-equal mission needs an id.")
            if mission_id in seen_mission_ids:
                raise MissionRegistryError("Co-equal mission ids must be unique.")
            if type(mission.get("priority")) is not int or mission["priority"] != 1:
                raise MissionRegistryError("Every co-equal mission must retain priority 1.")
            if mission.get("status") != "active":
                raise MissionRegistryError("Every co-equal mission must remain active.")
            if not isinstance(mission.get("title"), str) or not mission["title"].strip():
                raise MissionRegistryError(f"Co-equal mission title is required for {mission_id}.")
            if not isinstance(mission.get("objective"), str) or not mission["objective"].strip():
                raise MissionRegistryError(f"Co-equal mission objective is required for {mission_id}.")

            if mission_id == payload["mission_id"]:
                if mission.get("workstream_source") != "primary_mission":
                    raise MissionRegistryError("The XRP mission must reuse the primary mission workstreams.")
            else:
                mission_workstreams = mission.get("workstreams")
                if not isinstance(mission_workstreams, list) or not mission_workstreams:
                    raise MissionRegistryError(f"Co-equal mission workstreams are required for {mission_id}.")
                topic_ids: set[str] = set()
                priorities: set[int] = set()
                for item in mission_workstreams:
                    if not isinstance(item, dict):
                        raise MissionRegistryError(f"Every workstream must be an object for {mission_id}.")
                    topic_id = item.get("topic_id")
                    priority = item.get("priority")
                    if not isinstance(topic_id, str) or not topic_id.strip():
                        raise MissionRegistryError(f"Every workstream needs a topic id for {mission_id}.")
                    if type(priority) is not int or priority < 1:
                        raise MissionRegistryError(f"Invalid workstream priority for {topic_id}.")
                    if topic_id in topic_ids or priority in priorities:
                        raise MissionRegistryError(f"Workstream ids and priorities must be unique for {mission_id}.")
                    if not isinstance(item.get("goal"), str) or not item["goal"].strip():
                        raise MissionRegistryError(f"Workstream goal is required for {topic_id}.")
                    topic_ids.add(topic_id)
                    priorities.add(priority)

                continuation = mission.get("continuation_goal")
                if (
                    not isinstance(continuation, dict)
                    or not isinstance(continuation.get("topic_id"), str)
                    or not continuation["topic_id"].strip()
                    or not isinstance(continuation.get("goal"), str)
                    or not continuation["goal"].strip()
                ):
                    raise MissionRegistryError(f"A continuation goal is required for {mission_id}.")
                criteria = mission.get("acceptance_criteria")
                if not isinstance(criteria, list) or not criteria or not all(
                    isinstance(item, str) and item.strip() for item in criteria
                ):
                    raise MissionRegistryError(f"Acceptance criteria are required for {mission_id}.")
            seen_mission_ids.add(mission_id)

        if seen_mission_ids != expected_mission_ids:
            raise MissionRegistryError("The co-equal portfolio must contain XRP, audio and long-horizon continuity.")

        cross_objectives = portfolio.get("cross_mission_objectives")
        if not isinstance(cross_objectives, list) or not any(
            isinstance(item, dict)
            and item.get("id") == "barrot_only_revenue_customer_acquisition"
            and item.get("not_a_fourth_mission") is True
            and isinstance(item.get("scope"), str)
            and "Barrot technology only" in item["scope"]
            and isinstance(item.get("state"), str)
            for item in cross_objectives
        ):
            raise MissionRegistryError(
                "Barrot-only customer acquisition must remain a cross-mission objective, not a fourth mission."
            )

        return payload

    @property
    def mission_id(self) -> str:
        return self.manifest["mission_id"]

    @property
    def workstreams(self) -> list[dict[str, Any]]:
        return sorted(
            self.manifest["workstreams"],
            key=lambda item: item["priority"],
        )

    @property
    def portfolio_missions(self) -> list[dict[str, Any]]:
        """The three active priority-1 missions in their round-robin order."""
        return list(self.manifest["mission_portfolio"]["missions"])

    def goal_for_mission(self, mission_id: str, known_text: str = "") -> str | None:
        """Return the next verified-topic-aware goal for one co-equal mission."""
        if self.manifest["status"] != "active":
            return None
        if mission_id == self.mission_id:
            return self.next_goal(known_text)

        mission = next(
            (item for item in self.portfolio_missions if item["mission_id"] == mission_id),
            None,
        )
        if mission is None:
            raise MissionRegistryError(f"Unknown mission in portfolio: {mission_id}")
        if mission["status"] != "active":
            return None

        known = known_text.lower()
        for workstream in sorted(mission["workstreams"], key=lambda item: item["priority"]):
            marker = f"mission_topic_id: {workstream['topic_id']}".lower()
            if marker not in known:
                return self._render_portfolio_goal(
                    mission=mission,
                    topic_id=workstream["topic_id"],
                    goal=workstream["goal"],
                )

        continuation = mission["continuation_goal"]
        return self._render_portfolio_goal(
            mission=mission,
            topic_id=continuation["topic_id"],
            goal=continuation["goal"],
        )

    def next_goal(self, known_text: str = "") -> str | None:
        """Return the highest-priority uncompleted XRP workstream."""

        if self.manifest["status"] != "active":
            return None

        known = known_text.lower()
        for workstream in self.workstreams:
            marker = f"mission_topic_id: {workstream['topic_id']}".lower()
            if marker not in known:
                return self._render_goal(
                    topic_id=workstream["topic_id"],
                    goal=workstream["goal"],
                )

        continuation = self.manifest["continuation_goal"]
        return self._render_goal(
            topic_id=continuation["topic_id"],
            goal=continuation["goal"],
        )

    def _render_portfolio_goal(
        self,
        *,
        mission: dict[str, Any],
        topic_id: str,
        goal: str,
    ) -> str:
        foundation = self.manifest["foundation"]
        guardrails = "\n".join(f"- {item}" for item in self.manifest["guardrails"])
        invariants = "\n".join(f"- {item}" for item in foundation["invariants"])
        acceptance = "\n".join(f"- {item}" for item in mission["acceptance_criteria"])
        commercial = "\n".join(
            f"- {item['id']}: {item['scope']} State: {item['state']}"
            for item in self.manifest["mission_portfolio"]["cross_mission_objectives"]
        )
        responsibilities = ", ".join(foundation["responsibilities"])

        return f"""CO-EQUAL MISSION — HIGHEST PRIORITY
{mission["title"]}
MISSION_ID: {mission["mission_id"]}
MISSION_PRIORITY: 1 (co-equal; durable round-robin)
MISSION_TOPIC_ID: {topic_id}

OBJECTIVE
{mission["objective"]}

CURRENT WORKSTREAM
{goal}

SHARED BARROT V3 FOUNDATION
{foundation["name"]}: {responsibilities}.
{invariants}

CROSS-MISSION COMMERCIAL OBJECTIVE — NOT A FOURTH MISSION
{commercial}

GLOBAL GUARDRAILS
{guardrails}

MISSION ACCEPTANCE CRITERIA
{acceptance}

Work one bounded objective at a time. The next curriculum selection advances the durable round-robin cursor even if this task is blocked or incomplete. Do not starve another co-equal mission. Inspect current main, the complete repository tree, open PRs, branch ancestry, overlapping diffs, CI, dependencies and security settings before changing files. Record evidence and test results. A plan or draft is not completion. This mission does not authorize trading, deployment, secret operations, external publication, outbound outreach or bypassing repository controls.
"""

    def _render_goal(self, *, topic_id: str, goal: str) -> str:
        foundation = self.manifest["foundation"]
        guardrails = "\n".join(
            f"- {item}" for item in self.manifest["guardrails"]
        )
        invariants = "\n".join(
            f"- {item}" for item in foundation["invariants"]
        )
        acceptance = "\n".join(
            f"- {item}" for item in self.manifest["acceptance_criteria"]
        )

        return f"""PRIMARY MISSION — HIGHEST PRIORITY
{self.manifest["title"]}
MISSION_ID: {self.mission_id}
MISSION_PRIORITY: 1 (1 is highest)
MISSION_TOPIC_ID: {topic_id}

OBJECTIVE
{self.manifest["objective"]}

CURRENT WORKSTREAM
{goal}

PRESERVED FOUNDATION
{foundation["name"]}: execution, orchestration, safety and verification.
{invariants}

GLOBAL GUARDRAILS
{guardrails}

MISSION ACCEPTANCE CRITERIA
{acceptance}

Work one bounded objective at a time. Inspect existing repository state and overlapping work before changing files. Record evidence and test results. A plan or draft is not completion. This mission does not authorize trading, deployment, secret operations, external publication or bypassing repository controls.
"""
