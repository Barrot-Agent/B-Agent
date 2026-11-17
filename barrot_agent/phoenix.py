"""PHOENIX / LUCY power protocol.

Barrot starts with the governed ingestion loop and earns each larger power by
passing a test.  A power is never granted because it was described; it is
granted because an artifact proves it.

===========  ======  ============================================  ==========
Level        Share   Powers                                        Status
===========  ======  ============================================  ==========
1            10%     ingest, transmute, cross-analyze, refine     implemented
2            30%     sandbox experiments, capability combination   implemented
3            60%     self-proposed research, self-rewrite          declared, locked
4            100%    dynamic any-format transmutation               declared, locked
===========  ======  ============================================  ==========

Rules enforced here:

* levels unlock in order, one at a time;
* evidence must contain ``passed: true``, a ``test`` and an ``artifact``;
* Level 2 evidence must be a kept sandbox run (``kind: sandbox``);
* Levels 3 and 4 cannot be unlocked by this module — they are declared, not
  implemented, and unlocking them would be a false claim;
* every unlocked power is appended to ``MEMORY.md`` with source, test, date.
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path

from .infinite_ingest.models import utc_now
from .infinite_ingest.refiner import score_capability
from .infinite_ingest.storage import MEMORY_MD, PROJECT_ROOT, Store
from .sandbox import SandboxResult, SandboxRunner

DEFAULT_STATE_PATH = PROJECT_ROOT / "data" / "phoenix_state.json"
DEFAULT_EXPERIMENT_LOG = PROJECT_ROOT / "data" / "phoenix_experiments.jsonl"


@dataclass(frozen=True)
class LevelSpec:
    """One LUCY level and the powers it grants."""

    level: int
    name: str
    percent: int
    powers: tuple[str, ...]
    requires: str
    implemented: bool = True


LEVELS: dict[int, LevelSpec] = {
    1: LevelSpec(
        level=1,
        name="governed_ingestion",
        percent=10,
        powers=(
            "ingestion",
            "transmutation",
            "cross_analysis",
            "single_capability_refinement",
        ),
        requires="test suite for the ingestion pipeline",
    ),
    2: LevelSpec(
        level=2,
        name="sandbox_experimentation",
        percent=30,
        powers=("sandbox_experimentation", "capability_combination"),
        requires="a kept sandbox experiment that passed",
    ),
    3: LevelSpec(
        level=3,
        name="self_proposed_research",
        percent=60,
        powers=("self_proposed_research", "self_rewrite"),
        requires="not implemented: needs a research-gap selector and a tested self-rewrite loop",
        implemented=False,
    ),
    4: LevelSpec(
        level=4,
        name="phoenix",
        percent=100,
        powers=("dynamic_transmutation", "cross_paradigm_synthesis"),
        requires="not implemented: needs any-format transmutation and cross-paradigm synthesis",
        implemented=False,
    ),
}


class PowerLocked(RuntimeError):
    """The requested level is declared but not implemented."""


class EvidenceRequired(PermissionError):
    """The requested level lacks passing, artifact-backed evidence."""


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(text, encoding="utf-8")
    os.replace(temporary, path)


def _default_state() -> dict:
    return {
        "agent": "Barrot",
        "protocol": "PHOENIX/LUCY",
        "level": 0,
        "percent": 0,
        "levels": {},
        "continuous": {"enabled": False, "mode": "bounded"},
        "updated_at": None,
    }


def level_spec(level: int) -> LevelSpec:
    """Look up a level, with a clear error for unknown numbers."""
    if level not in LEVELS:
        raise ValueError(f"unknown PHOENIX level: {level!r}")
    return LEVELS[level]


class Phoenix:
    """Level state, evidence gates, sandbox experiments and combinations.

    Args:
        state_path: JSON file holding the unlocked level and its evidence.
        memory_path: Markdown file that receives the permanent power log.
        experiment_log: JSONL log of experiments proposed through this object.
        runner: Sandbox runner; injectable for tests.
        store: Data store used by capability combination.
    """

    def __init__(
        self,
        state_path: str | Path = DEFAULT_STATE_PATH,
        memory_path: str | Path = MEMORY_MD,
        experiment_log: str | Path = DEFAULT_EXPERIMENT_LOG,
        runner: SandboxRunner | None = None,
        store: Store | None = None,
    ):
        self.state_path = Path(state_path)
        self.memory_path = Path(memory_path)
        self.experiment_log = Path(experiment_log)
        self.runner = runner or SandboxRunner()
        self.store = store or Store()

    # -- state -----------------------------------------------------------

    def load(self) -> dict:
        """Load the state, returning a fresh baseline when the file is absent."""
        if not self.state_path.exists():
            return _default_state()
        try:
            payload = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return _default_state()
        if not isinstance(payload, dict):
            return _default_state()
        state = _default_state()
        state.update(payload)
        return state

    def save(self, state: dict) -> None:
        """Persist state atomically."""
        state["updated_at"] = utc_now()
        _atomic_write(
            self.state_path, json.dumps(state, indent=2, ensure_ascii=False) + "\n"
        )

    @property
    def level(self) -> int:
        """Currently unlocked level (0 before the first promotion)."""
        return int(self.load().get("level", 0) or 0)

    def status(self) -> dict:
        """Readable status for the CLI and tests."""
        state = self.load()
        current = int(state.get("level", 0) or 0)
        return {
            "agent": state.get("agent", "Barrot"),
            "protocol": state.get("protocol", "PHOENIX/LUCY"),
            "level": current,
            "percent": state.get("percent", 0),
            "name": LEVELS[current].name if current in LEVELS else "unawakened",
            "unlocked": sorted(int(key) for key in state.get("levels", {})),
            "next": (
                {
                    "level": current + 1,
                    "name": LEVELS[current + 1].name,
                    "requires": LEVELS[current + 1].requires,
                    "implemented": LEVELS[current + 1].implemented,
                }
                if current + 1 in LEVELS
                else None
            ),
            "continuous": state.get("continuous", {}),
            "updated_at": state.get("updated_at"),
        }

    # -- gates -----------------------------------------------------------

    def require(self, level: int) -> None:
        """Raise unless ``level`` is unlocked."""
        current = self.level
        if current < level:
            raise PermissionError(
                f"PHOENIX level {level} ({level_spec(level).name}) is locked; "
                f"current level is {current}"
            )

    def unlock(self, level: int, evidence: dict) -> dict:
        """Unlock exactly the next level, with passing evidence.

        Args:
            level: Level to unlock (1..4).
            evidence: Must contain ``passed=True``, ``test`` and ``artifact``.
                Level 2 additionally requires ``kind='sandbox'`` and a
                ``sandbox_run`` id.

        Returns:
            The updated state.

        Raises:
            PowerLocked: For Levels 3 and 4, which are not implemented.
            EvidenceRequired: When the evidence does not prove a pass.
            ValueError: When levels are skipped or the target is invalid.
        """
        spec = level_spec(level)
        if not spec.implemented:
            raise PowerLocked(
                f"level {level} ({spec.name}) is declared but not implemented; "
                f"refusing to fake an unlock. {spec.requires}"
            )
        state = self.load()
        current = int(state.get("level", 0) or 0)
        if level == current:
            return state
        if level != current + 1:
            raise ValueError(
                f"levels unlock in order: current={current}, requested={level}"
            )
        if not isinstance(evidence, dict):
            raise EvidenceRequired("evidence must be a mapping")
        if evidence.get("passed") is not True:
            raise EvidenceRequired("evidence.passed must be true")
        if not str(evidence.get("test", "")).strip():
            raise EvidenceRequired("evidence.test is required")
        if not str(evidence.get("artifact", "")).strip():
            raise EvidenceRequired("evidence.artifact is required")
        if level == 2:
            if evidence.get("kind") != "sandbox":
                raise EvidenceRequired("level 2 requires kind='sandbox' evidence")
            if not str(evidence.get("sandbox_run", "")).strip():
                raise EvidenceRequired("level 2 requires evidence.sandbox_run")

        record = dict(evidence)
        record["level"] = level
        record["name"] = spec.name
        record["percent"] = spec.percent
        record["unlocked_at"] = utc_now()
        state.setdefault("levels", {})[str(level)] = record
        state["level"] = level
        state["percent"] = spec.percent
        self.save(state)
        for power in spec.powers:
            self.log_power(
                power,
                source=str(evidence.get("source", "")) or spec.name,
                test=str(evidence.get("test", "")),
                result="PASS",
                artifact=str(evidence.get("artifact", "")),
            )
        return state

    # -- permanent power log --------------------------------------------

    def log_power(
        self,
        name: str,
        *,
        source: str,
        test: str,
        result: str = "PASS",
        artifact: str = "",
        date: str | None = None,
    ) -> bool:
        """Append one power to ``MEMORY.md``; return ``False`` if already logged.

        The heading is ``### Power <date> - <name>``.  Re-running the same power
        on the same date is idempotent; a new date creates a new entry.
        """
        date = date or utc_now()[:10]
        heading = f"### Power {date} - {name}"
        try:
            existing = (
                self.memory_path.read_text(encoding="utf-8")
                if self.memory_path.exists()
                else ""
            )
        except OSError:
            return False
        if heading in existing:
            return False
        entry = (
            f"\n{heading}\n"
            f"- Source: {source or 'unknown'}\n"
            f"- Test: {test or 'none'}\n"
            f"- Result: {result}\n"
            f"- Artifact: {artifact or 'none'}\n"
        )
        try:
            self.memory_path.parent.mkdir(parents=True, exist_ok=True)
            with self.memory_path.open("a", encoding="utf-8") as handle:
                if "## Power log" not in existing:
                    handle.write("\n## Power log\n")
                handle.write(entry)
        except OSError:
            return False
        return True

    # -- sandbox experiments --------------------------------------------

    def run_experiment(
        self,
        hypothesis: str,
        *,
        name: str = "experiment",
        script: str | None = None,
        script_path: str | Path | None = None,
        inputs: dict[str, str | Path] | None = None,
        modules: dict[str, str | Path] | None = None,
        source: str = "",
        unlock_level: int | None = None,
    ) -> SandboxResult:
        """Run one hypothesis in the sandbox and optionally promote on pass.

        The experiment may run before Level 2 is unlocked: it is the test that
        earns Level 2.  Nothing is promoted on a failed or discarded run.
        """
        self.require(1)
        result = self.runner.run(
            name=name,
            script=script,
            script_path=script_path,
            inputs=inputs,
            modules=modules,
        )
        self._log_experiment(hypothesis, source, result)
        if unlock_level is not None:
            if not result.passed:
                raise EvidenceRequired(
                    f"sandbox run {result.run_id} failed; level {unlock_level} stays locked"
                )
            self.promote_from_sandbox(result, level=unlock_level, source=source)
        return result

    def promote_from_sandbox(
        self, result: SandboxResult, *, level: int = 2, source: str = ""
    ) -> dict:
        """Turn a kept, passing sandbox run into evidence and unlock a level."""
        if not result.passed or not result.kept:
            raise EvidenceRequired(
                f"sandbox run {result.run_id} did not pass or was discarded"
            )
        evidence = {
            "kind": "sandbox",
            "passed": True,
            "test": result.name,
            "artifact": result.run_dir or result.log_path,
            "sandbox_run": result.run_id,
            "script_sha256": result.script_sha256,
            "metrics": result.metrics,
            "source": source,
        }
        return self.unlock(level, evidence)

    def _log_experiment(self, hypothesis: str, source: str, result: SandboxResult) -> None:
        self.experiment_log.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "at": utc_now(),
            "hypothesis": hypothesis,
            "source": source,
            "run_id": result.run_id,
            "name": result.name,
            "passed": result.passed,
            "kept": result.kept,
            "metrics": result.metrics,
            "artifact": result.run_dir,
            "script_sha256": result.script_sha256,
        }
        with self.experiment_log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    # -- capability combination -----------------------------------------

    def combine(
        self,
        name: str,
        capability_a: str,
        capability_b: str,
        *,
        description: str = "",
        overwrite: bool = False,
    ) -> dict:
        """Combine two capabilities into a tested third one.

        The third capability keeps the union of both memory sets, both question
        sets (ids are namespaced) and both source lists.  It is saved only when
        it scores at least as high as both parents with zero violations.
        """
        self.require(2)
        if capability_a == capability_b:
            raise ValueError("combine needs two different capabilities")
        first = self.store.load_capability(capability_a)
        second = self.store.load_capability(capability_b)
        if not first or not second:
            missing = capability_a if not first else capability_b
            raise ValueError(f"unknown capability: {missing!r}")
        if not first.get("questions") or not second.get("questions"):
            raise ValueError("both capabilities need test questions")

        target = self.store.capability_path(name)
        if target.exists() and not overwrite:
            raise ValueError(f"capability already exists: {name!r} (set overwrite=True)")

        questions = []
        for capability_name, capability in (
            (capability_a, first),
            (capability_b, second),
        ):
            for question in capability.get("questions", []):
                item = dict(question)
                item["id"] = f"{capability_name}:{question.get('id', 'q')}"
                questions.append(item)

        sources = []
        seen_urls = set()
        for capability in (first, second):
            for source in capability.get("sources", []):
                url = source.get("url", "")
                if url and url in seen_urls:
                    continue
                seen_urls.add(url)
                sources.append(dict(source))

        combined = {
            "name": name,
            "description": description
            or f"Level 2 combination: {capability_a} + {capability_b}",
            "harness": first.get("harness", second.get("harness", "")),
            "derived_from": [capability_a, capability_b],
            "memory_ids": list(
                dict.fromkeys(
                    list(first.get("memory_ids", [])) + list(second.get("memory_ids", []))
                )
            ),
            "questions": questions,
            "sources": sources,
            "history": [],
        }

        records = self.store.load_memory()
        score_a = score_capability(first, records)
        score_b = score_capability(second, records)
        score_new = score_capability(combined, records)
        required = max(score_a.recall, score_b.recall)
        passed = (
            score_new.violations == 0
            and score_new.total > 0
            and score_new.recall >= required
        )
        if not passed:
            return {
                "kept": False,
                "name": name,
                "derived_from": [capability_a, capability_b],
                "required_recall": required,
                "scores": {
                    capability_a: score_a.as_dict(),
                    capability_b: score_b.as_dict(),
                    name: score_new.as_dict(),
                },
            }

        combined["status"] = "tested"
        combined["history"].append(
            {
                "at": utc_now(),
                "event": "combined",
                "from": [capability_a, capability_b],
                "recall": round(score_new.recall, 4),
                "required": round(required, 4),
            }
        )
        self.store.save_capability(name, combined)
        return {
            "kept": True,
            "name": name,
            "derived_from": [capability_a, capability_b],
            "path": str(target),
            "required_recall": required,
            "scores": {
                capability_a: score_a.as_dict(),
                capability_b: score_b.as_dict(),
                name: score_new.as_dict(),
            },
        }

    # -- continuous mode -------------------------------------------------

    def record_continuous(self, payload: dict) -> dict:
        """Record the bounded continuous-mode activation in the state file."""
        state = self.load()
        state["continuous"] = {
            "enabled": True,
            "mode": "bounded",
            "at": utc_now(),
            **payload,
        }
        self.save(state)
        return state["continuous"]


def _parse_mapping(values: list[str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise argparse.ArgumentTypeError(f"expected DEST=SOURCE, got {value!r}")
        destination, source = value.split("=", 1)
        mapping[destination] = source
    return mapping


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PHOENIX / LUCY power protocol")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("status", help="show the unlocked level and powers")

    experiment = sub.add_parser("experiment", help="run a hypothesis in the sandbox")
    experiment.add_argument("--hypothesis", required=True)
    experiment.add_argument("--name", default="experiment")
    experiment.add_argument("--script", default=None)
    experiment.add_argument("--script-path", default=None)
    experiment.add_argument("--input", action="append", default=[], metavar="DEST=SOURCE")
    experiment.add_argument("--module", action="append", default=[], metavar="DEST=SOURCE")
    experiment.add_argument("--source", default="")
    experiment.add_argument("--unlock-level", type=int, default=None)

    combine = sub.add_parser("combine", help="combine two capabilities into a third")
    combine.add_argument("--name", required=True)
    combine.add_argument("--capability-a", required=True)
    combine.add_argument("--capability-b", required=True)
    combine.add_argument("--description", default="")

    unlock = sub.add_parser("unlock", help="unlock the next level from an evidence file")
    unlock.add_argument("--level", type=int, required=True)
    unlock.add_argument("--evidence", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    args = build_parser().parse_args(argv)
    phoenix = Phoenix()
    if args.command == "status":
        print(json.dumps(phoenix.status(), indent=2))
        return 0
    if args.command == "experiment":
        result = phoenix.run_experiment(
            args.hypothesis,
            name=args.name,
            script=args.script,
            script_path=args.script_path,
            inputs=_parse_mapping(args.input),
            modules=_parse_mapping(args.module),
            source=args.source,
            unlock_level=args.unlock_level,
        )
        print(result.summary())
        print(json.dumps(result.metrics, indent=2))
        return 0 if result.passed else 1
    if args.command == "combine":
        result = phoenix.combine(
            args.name, args.capability_a, args.capability_b, description=args.description
        )
        print(json.dumps(result, indent=2))
        return 0 if result["kept"] else 1
    if args.command == "unlock":
        evidence = json.loads(Path(args.evidence).read_text(encoding="utf-8"))
        state = phoenix.unlock(args.level, evidence)
        print(json.dumps(state, indent=2))
        return 0
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
