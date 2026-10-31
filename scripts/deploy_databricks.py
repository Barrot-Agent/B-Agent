"""
deploy_databricks.py
====================
Uploads the B-Agent codebase to a Databricks workspace and creates (or
updates) a scheduled job that runs the main agent pipeline.

Authentication is resolved in the following order (highest priority first):
  1. DATABRICKS_HOST + DATABRICKS_TOKEN environment variables
  2. ~/.databrickscfg  [DEFAULT] profile (or profile set via DATABRICKS_CONFIG_PROFILE)
  3. .databrickscfg in the repository root

Required environment variables (or .databrickscfg entries):
    DATABRICKS_HOST   – e.g. https://adb-<workspace-id>.azuredatabricks.net
    DATABRICKS_TOKEN  – Personal Access Token

Optional:
    DATABRICKS_CLUSTER_ID – existing cluster to attach jobs to; a new
                            single-node cluster is created when omitted.
    DATABRICKS_JOB_NAME   – job name, defaults to "barrot-agent"
    DATABRICKS_WS_PATH    – workspace destination folder,
                            defaults to "/Barrot-Agent/B-Agent"
"""

import logging
import os
import sys
from pathlib import Path

from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs as sdk_jobs
from databricks.sdk.service.workspace import ImportFormat, Language
from databricks.sdk.service.compute import Environment

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DATABRICKS_HOST = os.environ.get("DATABRICKS_HOST", "")
DATABRICKS_TOKEN = os.environ.get("DATABRICKS_TOKEN", "")
JOB_NAME = os.environ.get("DATABRICKS_JOB_NAME", "barrot-agent")
WS_PATH = os.environ.get("DATABRICKS_WS_PATH", "/Barrot-Agent/B-Agent")
CLUSTER_ID = os.environ.get("DATABRICKS_CLUSTER_ID", "")
LOCAL_DIR = Path(__file__).resolve().parent.parent

UPLOAD_EXTENSIONS = {".py", ".ipynb", ".yml", ".yaml", ".txt", ".md", ".json"}
SKIP_DIRS = {
    ".git",
    ".github",
    ".config",
    ".npm",
    ".termux",
    "__pycache__",
    "venv",
    ".venv",
    "node_modules",
    "output",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_client() -> WorkspaceClient:
    """Return a WorkspaceClient, preferring env-var auth over cfg file."""
    if DATABRICKS_HOST and DATABRICKS_TOKEN:
        return WorkspaceClient(host=DATABRICKS_HOST, token=DATABRICKS_TOKEN)
    local_config = LOCAL_DIR / ".databrickscfg"
    if local_config.is_file():
        return WorkspaceClient(config_file=str(local_config))
    # Fall back to the standard ~/.databrickscfg profile.
    return WorkspaceClient()


def _validate_connection(client: WorkspaceClient) -> None:
    """Validate credentials before making any remote changes."""
    try:
        client.current_user.me()
    except Exception as exc:
        # Avoid echoing SDK error details, which can include workspace metadata.
        raise RuntimeError(
            "Databricks authentication preflight failed. Verify DATABRICKS_HOST "
            "and DATABRICKS_TOKEN in repository secrets, or refresh the configured "
            "Databricks profile. No workspace changes were made."
        ) from exc
    log.info("Databricks authentication preflight succeeded.")


def _ensure_folder(client: WorkspaceClient, path: str) -> None:
    """Create a destination folder or fail instead of hiding permission errors."""
    client.workspace.mkdirs(path=path)
    log.info("Workspace folder ready: %s", path)


def _upload_files(client: WorkspaceClient) -> int:
    """Upload Python (and other text) files preserving directory structure."""
    uploaded = 0
    failed_paths: list[str] = []
    for local_file in LOCAL_DIR.rglob("*"):
        if local_file.is_dir():
            continue
        rel = local_file.relative_to(LOCAL_DIR)
        # Skip hidden / ignored directories
        if any(part.startswith(".") or part in SKIP_DIRS for part in rel.parts):
            continue
        if local_file.suffix not in UPLOAD_EXTENSIONS:
            continue

        dest = f"{WS_PATH}/{rel.as_posix()}"
        dest_dir = dest.rsplit("/", 1)[0]
        _ensure_folder(client, dest_dir)

        content = local_file.read_bytes()
        import base64

        b64 = base64.b64encode(content).decode()

        try:
            client.workspace.import_(
                path=dest,
                overwrite=True,
                format=ImportFormat.AUTO,
                content=b64,
            )
            log.info("  uploaded: %s", dest)
            uploaded += 1
        except Exception as exc:
            # Keep logs free of raw SDK error bodies and never deploy a partial tree.
            log.error("  failed to upload %s (%s)", dest, type(exc).__name__)
            failed_paths.append(rel.as_posix())

    if failed_paths:
        preview = ", ".join(failed_paths[:5])
        raise RuntimeError(
            f"Databricks upload incomplete: {len(failed_paths)} file(s) failed; "
            f"first failures: {preview}. Job creation was skipped."
        )
    return uploaded


def _get_or_create_cluster_spec() -> dict:
    """Return a cluster spec dict.  Uses an existing cluster if configured."""
    if CLUSTER_ID:
        return {"existing_cluster_id": CLUSTER_ID}
    return {}


def _deploy_job(client: WorkspaceClient) -> int:
    """Create or update the Databricks job; return the job ID."""
    notebook_path = f"/Workspace{WS_PATH}/app.py"
    cluster_spec = _get_or_create_cluster_spec()
    environments = [
        sdk_jobs.JobEnvironment(
            environment_key="Default",
            spec=Environment(client="1"),
        )
    ]

    task = sdk_jobs.Task(
        task_key="barrot-main",
        description="Barrot Agent main pipeline",
        spark_python_task=sdk_jobs.SparkPythonTask(
            python_file=notebook_path,
        ),
        **cluster_spec,
        environment_key="Default",
    )

    # Check whether job already exists
    existing_id = None
    for job in client.jobs.list(name=JOB_NAME):
        existing_id = job.job_id
        break

    if existing_id:
        log.info("Updating existing job %d (%s)…", existing_id, JOB_NAME)
        client.jobs.reset(
            job_id=existing_id,
            new_settings=sdk_jobs.JobSettings(
                name=JOB_NAME,
                tasks=[task],
                schedule=sdk_jobs.CronSchedule(
                    quartz_cron_expression="0 0 * * * ?",
                    timezone_id="UTC",
                    pause_status=sdk_jobs.PauseStatus.UNPAUSED,
                ),
                max_concurrent_runs=1,
                environments=environments,
            ),
        )
        return existing_id
    else:
        log.info("Creating new job: %s", JOB_NAME)
        response = client.jobs.create(
            name=JOB_NAME,
            tasks=[task],
            schedule=sdk_jobs.CronSchedule(
                quartz_cron_expression="0 0 * * * ?",
                timezone_id="UTC",
                pause_status=sdk_jobs.PauseStatus.UNPAUSED,
            ),
            max_concurrent_runs=1,
            environments=environments,
        )
        return response.job_id


def _run_job(client: WorkspaceClient, job_id: int) -> None:
    """Trigger a single run and log the run URL."""
    run = client.jobs.run_now(job_id=job_id)
    log.info("Job run triggered – run_id=%d", run.run_id)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    has_host = bool(DATABRICKS_HOST)
    has_token = bool(DATABRICKS_TOKEN)
    if has_host != has_token:
        log.error(
            "DATABRICKS_HOST and DATABRICKS_TOKEN must be configured together, "
            "or use a valid Databricks profile."
        )
        sys.exit(2)

    config_candidates = (Path.home() / ".databrickscfg", LOCAL_DIR / ".databrickscfg")
    if not (has_host and has_token) and not any(path.is_file() for path in config_candidates):
        log.error(
            "No Databricks credentials found. Set DATABRICKS_HOST and "
            "DATABRICKS_TOKEN, or configure a Databricks profile."
        )
        sys.exit(2)

    client = _build_client()
    try:
        _validate_connection(client)
    except RuntimeError as exc:
        log.error("%s", exc)
        sys.exit(2)

    log.info("Connected to Databricks workspace: %s", client.config.host)
    _ensure_folder(client, WS_PATH)
    n = _upload_files(client)
    log.info("Uploaded %d file(s) to %s", n, WS_PATH)

    job_id = _deploy_job(client)
    log.info("Job '%s' deployed with id=%d", JOB_NAME, job_id)

    _run_job(client, job_id)
    log.info("✅ Databricks deployment complete.")


if __name__ == "__main__":
    main()
