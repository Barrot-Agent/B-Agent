import subprocess


def rollback_worktree(cwd="."):
    process = subprocess.run(
        "git restore .",
        cwd=cwd,
        shell=True,
        capture_output=True,
        text=True,
    )

    return {
        "success": process.returncode == 0,
        "stdout": process.stdout,
        "stderr": process.stderr,
    }
