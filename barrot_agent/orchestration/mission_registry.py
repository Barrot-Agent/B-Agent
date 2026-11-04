"""Fail-closed primary mission registry for Barrot's learning curriculum."""

from __future__ import annotations

import json
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

    def _load_manifest(self) -> dict[str, Any]:
        if not self.manifest_path.is_file():
            raise MissionRegistryError(
                f"Primary mission manifest is missing: {self.manifest_path}"
            )

        try:
            payload = json.loads(
                self.manifest_path.read_text(encoding="utf-8")
            )
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

    def next_goal(self, known_text: str = "") -> str | None:
        """Return the highest-priority uncompleted mission goal."""

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
