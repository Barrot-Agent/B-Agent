import subprocess
import sys

subprocess.run(
    [
        sys.executable,
        "-m",
        "barrot_agent.ingestion.corroborate_riemann_research",
    ],
    check=True,
)
