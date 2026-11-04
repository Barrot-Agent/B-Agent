"""Bounded autonomous experimentation primitives for Barrot V3."""
from __future__ import annotations
import hashlib, itertools, json, os, shutil, subprocess, tempfile, threading, uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence
try:
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None

_LEDGER = Path(".barrot") / "experiments" / "ledger.jsonl"
_SKIP = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", ".mypy_cache",
         ".ruff_cache", "node_modules", ".tox", ".nox", "dist", "build",
         ".barrot", ".apex_lattice", "coverage"}
_LOCK = threading.RLock()

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

def _hash(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()

@dataclass(frozen=True)
class ExperimentSpec:
    objective: str
    hypothesis: str
    command: tuple[str, ...]
    verification_command: tuple[str, ...]
    source_commit: str
    dimensions: Mapping[str, Sequence[str]] = field(default_factory=dict)
    image: str = "python:3.11-slim"
    timeout_seconds: int = 300
    memory_limit: str = "512m"
    cpu_limit: str = "1.0"
    max_variants: int = 24
    experiment_id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def __post_init__(self) -> None:
        if not self.objective.strip() or not self.hypothesis.strip() or not self.source_commit:
            raise ValueError("objective, hypothesis and source_commit are required")
        for command in (self.command, self.verification_command):
            if not command or not all(isinstance(x, str) and x for x in command):
                raise ValueError("commands must be non-empty argument vectors, not shell strings")
        if not 1 <= self.timeout_seconds <= 3600 or not 1 <= self.max_variants <= 256:
            raise ValueError("execution limits are outside permitted bounds")
        if not self.image or any(ch.isspace() for ch in self.image):
            raise ValueError("image must be a single pre-existing image reference")

@dataclass
class SandboxResult:
    passed: bool
    status: str
    stdout: str = ""
    stderr: str = ""
    returncode: int | None = None
    duration_seconds: float = 0.0
    sandbox_id: str = ""
    reason: str = ""

class ExperimentKnowledgeRepository:
    """Append-only hash-chained JSONL ledger; tampering blocks further writes."""
    def __init__(self, repo_root: Path | str = ".") -> None:
        self.repo_root = Path(repo_root).resolve()
        self.path = self.repo_root / _LEDGER
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def verify(self) -> dict[str, Any]:
        previous, count = "0" * 64, 0
        if not self.path.exists():
            return {"valid": True, "records": 0, "head": previous}
        with _LOCK, self.path.open("r", encoding="utf-8") as stream:
            for number, line in enumerate(stream, 1):
                try:
                    entry = json.loads(line)
                    if entry["sequence"] != count + 1 or entry["previous_hash"] != previous:
                        raise ValueError("sequence or previous-hash mismatch")
                    expected = _hash(_canonical({
                        "sequence": count + 1, "previous_hash": previous,
                        "payload": entry["payload"],
                    }))
                    if entry["record_hash"] != expected:
                        raise ValueError("record hash mismatch")
                    previous, count = expected, count + 1
                except Exception as exc:
                    return {"valid": False, "records": count, "head": previous,
                            "line": number, "error": str(exc)}
        return {"valid": True, "records": count, "head": previous}

    def append(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        with _LOCK, self.path.open("a+", encoding="utf-8") as stream:
            if fcntl is not None:
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX)
            try:
                state = self.verify()
                if not state["valid"]:
                    raise RuntimeError(f"experiment ledger integrity failure: {state}")
                entry = {"sequence": state["records"] + 1, "previous_hash": state["head"],
                         "payload": dict(payload)}
                entry["record_hash"] = _hash(_canonical(entry))
                stream.seek(0, os.SEEK_END)
                stream.write(_canonical(entry).decode() + "\n")
                stream.flush()
                os.fsync(stream.fileno())
                return entry
            finally:
                if fcntl is not None:
                    fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

class VariationGenerator:
    """Deterministic bounded pairwise-oriented variation generation."""
    @staticmethod
    def generate(dimensions: Mapping[str, Sequence[str]], max_variants: int = 24) -> list[dict[str, str]]:
        if not 1 <= max_variants <= 256:
            raise ValueError("max_variants must be between 1 and 256")
        normalized = {}
        for key, values in dimensions.items():
            vals = tuple(dict.fromkeys(str(v) for v in values))
            if not key.strip() or not vals or any(not v for v in vals):
                raise ValueError("dimension names and values must be non-empty")
            normalized[key] = vals
        if not normalized:
            return [{}]
        keys = sorted(normalized)
        baseline = {key: normalized[key][0] for key in keys}
        result, seen = [baseline], {_canonical(baseline)}
        for left_index, left in enumerate(keys):
            for right in keys[left_index + 1:]:
                for lv, rv in itertools.product(normalized[left], normalized[right]):
                    candidate = dict(baseline, **{left: lv, right: rv})
                    marker = _canonical(candidate)
                    if marker not in seen:
                        result.append(candidate); seen.add(marker)
                        if len(result) >= max_variants:
                            return result
        for key in keys:
            for value in normalized[key][1:]:
                candidate = dict(baseline); candidate[key] = value
                marker = _canonical(candidate)
                if marker not in seen:
                    result.append(candidate); seen.add(marker)
                    if len(result) >= max_variants:
                        return result
        return result

class SandboxDiscoveryEngine:
    """Static repository discovery; does not execute candidate code."""
    def __init__(self, repo_root: Path | str = ".") -> None:
        self.repo_root = Path(repo_root).resolve()

    def discover(self, max_candidates: int = 50) -> list[dict[str, Any]]:
        if not 1 <= max_candidates <= 500:
            raise ValueError("max_candidates must be between 1 and 500")
        sources, test_stems = [], set()
        for path in self.repo_root.rglob("*.py"):
            rel = path.relative_to(self.repo_root)
            if path.is_symlink() or any(part in _SKIP for part in rel.parts):
                continue
            if rel.parts[0] == "tests":
                test_stems.add(path.stem.removeprefix("test_"))
            elif "test" not in rel.parts and not rel.parts[0].startswith("."):
                sources.append(path)
        candidates = []
        for path in sorted(sources):
            rel = path.relative_to(self.repo_root).as_posix()
            if rel.startswith(("legacy/", "examples/")):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            signals = []
            if path.stem not in test_stems and not rel.startswith(("scripts/", "web/")):
                signals.append("no_matching_test_module")
            if "shell=True" in text:
                signals.append("shell_true_execution")
            if "TODO" in text or "FIXME" in text:
                signals.append("unfinished_marker")
            if signals:
                candidates.append({"objective": f"Investigate {', '.join(signals)} in {rel}",
                                   "source_path": rel, "signals": signals,
                                   "priority": 100 if "shell_true_execution" in signals else 50,
                                   "status": "DESIGNED"})
                if len(candidates) >= max_candidates:
                    break
        return sorted(candidates, key=lambda item: (-item["priority"], item["source_path"]))

class DockerSandboxRunner:
    """Docker-only runner: no automatic image pulls, no network, bounded resources."""
    def __init__(self, repo_root: Path | str = ".", docker_executable: str = "docker",
                 output_limit: int = 12000) -> None:
        self.repo_root = Path(repo_root).resolve()
        self.docker, self.output_limit = docker_executable, output_limit

    @staticmethod
    def _ignore(directory: str, names: list[str]) -> set[str]:
        ignored = set()
        for name in names:
            path = Path(directory) / name
            if name in _SKIP or name == ".env" or name.startswith(".env.") or path.is_symlink():
                ignored.add(name)
            elif path.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}:
                ignored.add(name)
        return ignored

    def _run_one(self, workspace: Path, spec: ExperimentSpec,
                 command: Sequence[str], variant: Mapping[str, str] | None = None) -> SandboxResult:
        check = subprocess.run([self.docker, "image", "inspect", spec.image],
                               capture_output=True, text=True, timeout=15, check=False)
        if check.returncode:
            return SandboxResult(False, "REQUIRES_IMAGE", stderr=check.stderr[-self.output_limit:],
                                 reason="Image is not present locally; automatic pulls are disabled.")
        args = [self.docker, "run", "--rm", "--network", "none", "--read-only",
                "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                "--pids-limit", "128", "--memory", spec.memory_limit, "--cpus", spec.cpu_limit,
                "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
                "--mount", f"type=bind,src={workspace},dst=/workspace,rw",
                "--workdir", "/workspace", "--env", "HOME=/tmp", "--env", "TMPDIR=/tmp",
                "--env", "PYTHONDONTWRITEBYTECODE=1",
                "--env", "BARROT_EXPERIMENT_VARIANT=" + json.dumps(dict(variant or {}), sort_keys=True),
                spec.image, *command]
        started = datetime.now(timezone.utc)
        try:
            result = subprocess.run(args, capture_output=True, text=True,
                                    timeout=spec.timeout_seconds, check=False, start_new_session=True)
            elapsed = (datetime.now(timezone.utc) - started).total_seconds()
            return SandboxResult(result.returncode == 0,
                                 "EXECUTED" if result.returncode == 0 else "FAILED",
                                 result.stdout[-self.output_limit:], result.stderr[-self.output_limit:],
                                 result.returncode, elapsed)
        except subprocess.TimeoutExpired as exc:
            return SandboxResult(False, "TIMEOUT", str(exc.stdout or "")[-self.output_limit:],
                                 str(exc.stderr or "")[-self.output_limit:],
                                 reason="Execution time limit exceeded.")
        except OSError as exc:
            return SandboxResult(False, "BLOCKED", reason=f"Container execution unavailable: {exc}")

    def run(self, spec: ExperimentSpec, variant: Mapping[str, str] | None = None) -> SandboxResult:
        sandbox_id = uuid.uuid4().hex
        try:
            if not self.repo_root.is_dir():
                raise FileNotFoundError(f"repository root does not exist: {self.repo_root}")
            with tempfile.TemporaryDirectory(prefix=f"barrot-exp-{sandbox_id[:8]}-") as tmp:
                workspace = Path(tmp) / "workspace"
                shutil.copytree(self.repo_root, workspace, ignore=self._ignore, symlinks=False)
                execution = self._run_one(workspace, spec, spec.command, variant)
                if not execution.passed:
                    execution.sandbox_id = sandbox_id
                    return execution
                verification = self._run_one(workspace, spec, spec.verification_command, variant)
                verification.stdout = (execution.stdout + "\n" + verification.stdout)[-self.output_limit:]
                verification.stderr = (execution.stderr + "\n" + verification.stderr)[-self.output_limit:]
                verification.duration_seconds += execution.duration_seconds
                verification.sandbox_id = sandbox_id
                if verification.passed:
                    verification.status = "VERIFIED"
                return verification
        except Exception as exc:
            return SandboxResult(False, "BLOCKED", sandbox_id=sandbox_id, reason=str(exc))

class ExperimentOrchestrator:
    def __init__(self, repo_root: Path | str = ".", runner: DockerSandboxRunner | None = None):
        self.repo_root = Path(repo_root).resolve()
        self.knowledge = ExperimentKnowledgeRepository(self.repo_root)
        self.discovery = SandboxDiscoveryEngine(self.repo_root)
        self.runner = runner or DockerSandboxRunner(self.repo_root)

    def discover(self, max_candidates: int = 50) -> list[dict[str, Any]]:
        candidates = self.discovery.discover(max_candidates)
        known = set()
        if self.knowledge.path.exists():
            with self.knowledge.path.open(encoding="utf-8") as stream:
                for line in stream:
                    payload = json.loads(line).get("payload", {})
                    if payload.get("kind") == "discovery_candidate":
                        known.add(payload.get("candidate_id"))
        fresh = []
        for candidate in candidates:
            candidate_id = _hash(_canonical(candidate))
            if candidate_id in known:
                continue
            candidate["candidate_id"] = candidate_id
            self.knowledge.append({"timestamp": _now(), "kind": "discovery_candidate", **candidate})
            fresh.append(candidate)
        return fresh

    def plan_variations(self, dimensions: Mapping[str, Sequence[str]],
                        max_variants: int = 24) -> list[dict[str, str]]:
        return VariationGenerator.generate(dimensions, max_variants)

    def execute(self, spec: ExperimentSpec,
                variant: Mapping[str, str] | None = None) -> dict[str, Any]:
        if not self.knowledge.verify()["valid"]:
            raise RuntimeError("experiment ledger integrity failure")
        self.knowledge.append({"timestamp": _now(), "status": "DESIGNED",
                               "experiment_id": spec.experiment_id, "objective": spec.objective,
                               "hypothesis": spec.hypothesis, "source_commit": spec.source_commit,
                               "variant": dict(variant or {}), "spec": asdict(spec)})
        result = self.runner.run(spec, variant)
        status = "VERIFIED" if result.passed and result.status == "VERIFIED" else result.status
        evidence = {"timestamp": _now(), "status": status, "experiment_id": spec.experiment_id,
                    "source_commit": spec.source_commit, "variant": dict(variant or {}),
                    "passed": result.passed, "runner_status": result.status,
                    "returncode": result.returncode, "duration_seconds": result.duration_seconds,
                    "stdout_sha256": _hash(result.stdout.encode()),
                    "stderr_sha256": _hash(result.stderr.encode()),
                    "sandbox_id": result.sandbox_id, "reason": result.reason}
        self.knowledge.append(evidence)
        return {"status": status, "result": asdict(result), "evidence": evidence}

    def integration_assessment(self, experiment_id: str,
                               explicit_approval: bool = False) -> dict[str, Any]:
        state = self.knowledge.verify()
        if not state["valid"]:
            return {"ready": False, "reason": "experiment ledger integrity failure"}
        with self.knowledge.path.open(encoding="utf-8") as stream:
            records = [json.loads(line)["payload"] for line in stream]
        if not any(r.get("experiment_id") == experiment_id and r.get("status") == "VERIFIED"
                   for r in records):
            return {"ready": False, "reason": "no verified experiment record"}
        if not explicit_approval:
            return {"ready": False, "reason": "explicit integration approval is required"}
        return {"ready": True, "reason": "verified evidence exists; prepare a reviewable change only",
                "automatic_merge": False, "automatic_deploy": False}

class ContinuousDiscoveryScheduler:
    """One bounded persistent tick; an external scheduler owns cadence and restart."""
    def __init__(self, orchestrator: ExperimentOrchestrator, max_candidates_per_tick: int = 10):
        if not 1 <= max_candidates_per_tick <= 100:
            raise ValueError("max_candidates_per_tick must be between 1 and 100")
        self.orchestrator, self.max_candidates_per_tick = orchestrator, max_candidates_per_tick

    def run_once(self) -> dict[str, Any]:
        state = self.orchestrator.knowledge.verify()
        if not state["valid"]:
            raise RuntimeError("experiment ledger integrity failure")
        candidates = self.orchestrator.discover(self.max_candidates_per_tick)
        self.orchestrator.knowledge.append({"timestamp": _now(), "status": "EXECUTED",
                                            "kind": "discovery_tick",
                                            "candidate_count": len(candidates),
                                            "ledger_head_before_tick": state["head"]})
        return {"status": "EXECUTED", "candidate_count": len(candidates),
                "candidates": candidates, "ledger": self.orchestrator.knowledge.verify()}
