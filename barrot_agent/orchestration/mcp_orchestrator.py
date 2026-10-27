"""
MCP Orchestrator
================
Coordinates the three MCP clients (Hugging Face, Databricks, GitHub) into a
unified workflow for the Stupid Sindy video generation pipeline.

Workflow steps
--------------
1. Load / validate configuration.
2. HF MCP – ensure required models are cached.
3. Local pipeline – generate the episode script.
4. Databricks MCP – submit rendering job; poll for completion.
5. GitHub MCP – commit video + metadata; trigger CI/CD workflow.
6. Emit progress events throughout so the Streamlit UI can react.

Usage
-----
    from mcp_orchestrator import MCPOrchestrator, OrchestratorConfig

    cfg = OrchestratorConfig(
        hf_token="hf_…",
        databricks_host="https://adb-…",
        databricks_token="dapi…",
        github_token="ghp_…",
    )
    orch = MCPOrchestrator(cfg)
    for event in orch.run_episode(episode_number=3):
        print(event)
"""

from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class OrchestratorConfig:
    """Credentials and settings for all three MCP services."""

    # Hugging Face
    hf_token: Optional[str] = None

    # Databricks
    databricks_host: Optional[str] = None
    databricks_token: Optional[str] = None
    databricks_cluster_id: Optional[str] = None

    # GitHub
    github_token: Optional[str] = None
    github_owner: str = "Barrot-Agent"
    github_repo: str = "B-Agent"
    github_branch: str = "Main"

    # Pipeline behaviour
    download_models: bool = True
    use_databricks: bool = True
    commit_to_github: bool = True
    trigger_cicd: bool = True
    databricks_poll_interval: int = 15  # seconds
    databricks_timeout: int = 3600  # seconds

    @classmethod
    def from_env(cls) -> "OrchestratorConfig":
        """Build an :class:`OrchestratorConfig` from environment variables."""
        return cls(
            hf_token=os.environ.get("HF_TOKEN"),
            databricks_host=os.environ.get("DATABRICKS_HOST"),
            databricks_token=os.environ.get("DATABRICKS_TOKEN"),
            databricks_cluster_id=os.environ.get("DATABRICKS_CLUSTER_ID"),
            github_token=os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_PAT"),
            github_owner=os.environ.get("GITHUB_OWNER", "Barrot-Agent"),
            github_repo=os.environ.get("GITHUB_REPO", "B-Agent"),
            github_branch=os.environ.get("GITHUB_BRANCH", "Main"),
        )


# ---------------------------------------------------------------------------
# Progress events
# ---------------------------------------------------------------------------


class OrchestratorStep(str, Enum):
    INIT = "init"
    HF_MODELS = "hf_models"
    SCRIPT_GEN = "script_gen"
    DATABRICKS_SUBMIT = "databricks_submit"
    DATABRICKS_WAIT = "databricks_wait"
    LOCAL_RENDER = "local_render"
    GITHUB_COMMIT = "github_commit"
    CICD_TRIGGER = "cicd_trigger"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class OrchestratorEvent:
    step: OrchestratorStep
    message: str
    progress: float = 0.0  # 0.0 – 1.0 overall pipeline progress
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    @property
    def is_error(self) -> bool:
        return self.step == OrchestratorStep.ERROR

    @property
    def is_complete(self) -> bool:
        return self.step == OrchestratorStep.COMPLETE


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------


@dataclass
class EpisodeRunRecord:
    episode_number: int
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    databricks_run_id: Optional[int] = None
    video_path: Optional[str] = None
    github_commit_sha: Optional[str] = None
    success: bool = False
    error_message: Optional[str] = None

    @property
    def elapsed(self) -> float:
        end = self.completed_at or time.time()
        return end - self.started_at


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


class MCPOrchestrator:
    """Unified MCP workflow orchestrator for the Stupid Sindy pipeline."""

    def __init__(self, config: Optional[OrchestratorConfig] = None) -> None:
        self.config = config or OrchestratorConfig.from_env()
        self._run_history: List[EpisodeRunRecord] = []
        self._hf: Optional[Any] = None
        self._db: Optional[Any] = None
        self._gh: Optional[Any] = None

    # ------------------------------------------------------------------
    # Lazy client initialisation
    # ------------------------------------------------------------------

    def _get_hf(self):
        if self._hf is None:
            from mcp_huggingface import HuggingFaceMCP

            self._hf = HuggingFaceMCP(token=self.config.hf_token)
        return self._hf

    def _get_db(self):
        if self._db is None:
            from mcp_databricks import DatabricksMCP

            self._db = DatabricksMCP(
                host=self.config.databricks_host,
                token=self.config.databricks_token,
                cluster_id=self.config.databricks_cluster_id,
            )
        return self._db

    def _get_gh(self):
        if self._gh is None:
            from mcp_github import GitHubMCP

            self._gh = GitHubMCP(
                token=self.config.github_token,
                owner=self.config.github_owner,
                repo=self.config.github_repo,
                branch=self.config.github_branch,
            )
        return self._gh

    # ------------------------------------------------------------------
    # Config validation
    # ------------------------------------------------------------------

    def validate_config(self) -> Dict[str, bool]:
        """
        Return a dict of ``{service: is_configured}`` without making
        any network calls.
        """
        return {
            "huggingface": bool(self.config.hf_token),
            "databricks": bool(self.config.databricks_host and self.config.databricks_token),
            "github": bool(self.config.github_token),
        }

    # ------------------------------------------------------------------
    # Main workflow
    # ------------------------------------------------------------------

    def run_episode(
        self,
        episode_number: int,
    ) -> Generator[OrchestratorEvent, None, None]:
        """
        Run the full MCP workflow for *episode_number*.

        Yields :class:`OrchestratorEvent` instances so callers can track
        progress in real time (Streamlit, CLI, tests …).
        """
        record = EpisodeRunRecord(episode_number=episode_number)
        self._run_history.append(record)

        # ------------------------------------------------------------------
        # Step 0 – Init
        # ------------------------------------------------------------------
        yield OrchestratorEvent(
            step=OrchestratorStep.INIT,
            message=f"Starting MCP workflow for episode {episode_number}",
            progress=0.0,
            details=self.validate_config(),
        )

        # ------------------------------------------------------------------
        # Step 1 – HF model downloads
        # ------------------------------------------------------------------
        if self.config.download_models:
            yield OrchestratorEvent(
                step=OrchestratorStep.HF_MODELS,
                message="Checking / downloading AI models via Hugging Face MCP…",
                progress=0.05,
            )
            try:
                hf = self._get_hf()
                results = hf.ensure_sindy_models()
                failed = [m for m, p in results.items() if p is None]
                if failed:
                    logger.warning("Some models could not be downloaded: %s", failed)
                yield OrchestratorEvent(
                    step=OrchestratorStep.HF_MODELS,
                    message=f"Models ready ({len(results) - len(failed)}/{len(results)} cached)",
                    progress=0.15,
                    details={"cached": [m for m, p in results.items() if p], "failed": failed},
                )
            except Exception as exc:
                logger.error("HF model step failed: %s", exc)
                yield OrchestratorEvent(
                    step=OrchestratorStep.HF_MODELS,
                    message="HF model download skipped (non-fatal)",
                    progress=0.15,
                    details={"error": str(exc)},
                )
        else:
            yield OrchestratorEvent(
                step=OrchestratorStep.HF_MODELS,
                message="HF model downloads disabled by config",
                progress=0.15,
            )

        # ------------------------------------------------------------------
        # Step 2 – Local script generation
        # ------------------------------------------------------------------
        yield OrchestratorEvent(
            step=OrchestratorStep.SCRIPT_GEN,
            message=f"Generating script for episode {episode_number}…",
            progress=0.20,
        )
        try:
            from stupid_sindy_series_generator import get_episode

            ep = get_episode(episode_number)
            script_text = ep.full_script()
            yield OrchestratorEvent(
                step=OrchestratorStep.SCRIPT_GEN,
                message=f"Script generated ({len(script_text)} chars, {len(ep.scenes)} scenes)",
                progress=0.25,
                details={
                    "title": ep.title,
                    "scenes": len(ep.scenes),
                    "characters": ep.characters,
                },
            )
        except Exception as exc:
            record.error_message = str(exc)
            yield OrchestratorEvent(
                step=OrchestratorStep.ERROR,
                message=f"Script generation failed: {exc}",
                progress=0.25,
                error=str(exc),
            )
            return

        # ------------------------------------------------------------------
        # Step 3 – Rendering (Databricks or local fallback)
        # ------------------------------------------------------------------
        video_path: Optional[str] = None

        if self.config.use_databricks and self._get_db().is_configured():
            # --- Databricks path ---
            from mcp_databricks import JobRunState  # noqa: F811

            yield OrchestratorEvent(
                step=OrchestratorStep.DATABRICKS_SUBMIT,
                message="Submitting rendering job to Databricks cluster…",
                progress=0.30,
            )
            db = self._get_db()
            run_id = db.submit_render_job(episode_number)
            if run_id is None:
                yield OrchestratorEvent(
                    step=OrchestratorStep.DATABRICKS_SUBMIT,
                    message="Databricks job submission failed – falling back to local render",
                    progress=0.35,
                )
                video_path = self._local_render(episode_number)
            else:
                record.databricks_run_id = run_id
                yield OrchestratorEvent(
                    step=OrchestratorStep.DATABRICKS_WAIT,
                    message=f"Databricks run {run_id} submitted – waiting for completion…",
                    progress=0.35,
                    details={"run_id": run_id},
                )
                final_state = db.wait_for_run(
                    run_id,
                    poll_interval=self.config.databricks_poll_interval,
                    timeout=self.config.databricks_timeout,
                )
                if final_state.job_state == JobRunState.COMPLETE:
                    yield OrchestratorEvent(
                        step=OrchestratorStep.DATABRICKS_WAIT,
                        message=f"Databricks run {run_id} completed successfully",
                        progress=0.70,
                        details={"run_page_url": final_state.run_page_url},
                    )
                    video_path = self._locate_databricks_output(episode_number)
                else:
                    err = final_state.error_message or "Unknown error"
                    yield OrchestratorEvent(
                        step=OrchestratorStep.DATABRICKS_WAIT,
                        message=f"Databricks run failed ({err}) – falling back to local render",
                        progress=0.70,
                    )
                    video_path = self._local_render(episode_number)
        else:
            # --- Local render path ---
            yield OrchestratorEvent(
                step=OrchestratorStep.LOCAL_RENDER,
                message="Rendering episode locally (Databricks not configured)…",
                progress=0.30,
            )
            video_path = self._local_render(episode_number)
            yield OrchestratorEvent(
                step=OrchestratorStep.LOCAL_RENDER,
                message="Local render complete" if video_path else "Local render failed",
                progress=0.70,
                details={"video_path": video_path},
            )

        record.video_path = video_path

        # ------------------------------------------------------------------
        # Step 4 – GitHub commit
        # ------------------------------------------------------------------
        if self.config.commit_to_github and video_path and Path(video_path).exists():
            yield OrchestratorEvent(
                step=OrchestratorStep.GITHUB_COMMIT,
                message="Committing video and metadata to GitHub…",
                progress=0.75,
            )
            gh = self._get_gh()

            # Build metadata payload
            try:
                from stupid_sindy_series_generator import get_episode as _get_ep

                ep_meta = _get_ep(episode_number)
                metadata: Dict[str, Any] = {
                    "episode_number": episode_number,
                    "title": ep_meta.title,
                    "description": ep_meta.description,
                    "runtime_minutes": ep_meta.runtime_minutes,
                    "characters": ep_meta.characters,
                    "scene_count": len(ep_meta.scenes),
                    "video_path": f"sindy_videos/ep{episode_number:02d}.mp4",
                    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "orchestrator": "mcp",
                }
            except Exception:
                metadata = {
                    "episode_number": episode_number,
                    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }

            meta_result = gh.commit_episode_metadata(episode_number, metadata)
            vid_result = gh.commit_episode_video(episode_number, video_path)

            record.github_commit_sha = vid_result.sha or meta_result.sha

            yield OrchestratorEvent(
                step=OrchestratorStep.GITHUB_COMMIT,
                message=(
                    "Committed to GitHub successfully"
                    if vid_result.success
                    else f"GitHub commit failed: {vid_result.error_message}"
                ),
                progress=0.88,
                details={
                    "video_commit": vid_result.sha,
                    "metadata_commit": meta_result.sha,
                },
            )
        elif self.config.commit_to_github:
            yield OrchestratorEvent(
                step=OrchestratorStep.GITHUB_COMMIT,
                message="GitHub commit skipped – no video file available",
                progress=0.88,
            )

        # ------------------------------------------------------------------
        # Step 5 – CI/CD trigger
        # ------------------------------------------------------------------
        if self.config.trigger_cicd and self._get_gh().is_configured():
            yield OrchestratorEvent(
                step=OrchestratorStep.CICD_TRIGGER,
                message="Triggering CI/CD workflow…",
                progress=0.92,
            )
            gh = self._get_gh()
            dispatch = gh.trigger_cicd(
                workflow_id="sindy-mcp-cicd.yml",
                episode_number=episode_number,
            )
            yield OrchestratorEvent(
                step=OrchestratorStep.CICD_TRIGGER,
                message=(
                    "CI/CD workflow triggered"
                    if dispatch.success
                    else f"CI/CD trigger failed: {dispatch.error_message}"
                ),
                progress=0.96,
            )

        # ------------------------------------------------------------------
        # Done
        # ------------------------------------------------------------------
        record.completed_at = time.time()
        record.success = video_path is not None
        yield OrchestratorEvent(
            step=OrchestratorStep.COMPLETE,
            message=(
                f"Episode {episode_number} pipeline complete"
                if record.success
                else f"Episode {episode_number} pipeline finished with errors"
            ),
            progress=1.0,
            details={
                "elapsed": record.elapsed,
                "video_path": video_path,
                "databricks_run_id": record.databricks_run_id,
                "github_sha": record.github_commit_sha,
            },
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _local_render(self, episode_number: int) -> Optional[str]:
        """Run the local SindyVideoPipeline and return the video path, or None."""
        try:
            from sindy_video_pipeline import RenderStatus, SindyVideoPipeline

            pipeline = SindyVideoPipeline()
            if pipeline.get_state(episode_number) is None:
                pipeline.queue_episode(episode_number)
            for _ in pipeline.render_episode(episode_number):
                pass  # consume the generator
            state = pipeline.get_state(episode_number)
            if state and state.status == RenderStatus.COMPLETE:
                return pipeline.get_video_path(episode_number)
        except Exception as exc:
            logger.error("Local render failed: %s", exc)
        return None

    def _locate_databricks_output(self, episode_number: int) -> Optional[str]:
        """
        Look for a video file that Databricks may have written to the local
        sindy_videos/ directory (e.g. when DBFS is mounted or artefacts are
        downloaded after the run).  Falls back to local render if absent.
        """
        ep_str = f"{episode_number:02d}"
        candidate = Path("sindy_videos") / f"ep{ep_str}.mp4"
        if candidate.exists():
            return str(candidate)
        # Nothing found – run locally as fallback
        return self._local_render(episode_number)

    def run_history(self) -> List[EpisodeRunRecord]:
        """Return all episode run records from this session."""
        return list(self._run_history)

    def latest_run(self, episode_number: int) -> Optional[EpisodeRunRecord]:
        """Return the most recent run record for *episode_number*."""
        matches = [r for r in self._run_history if r.episode_number == episode_number]
        return matches[-1] if matches else None
