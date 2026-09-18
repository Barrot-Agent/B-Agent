import subprocess
from pathlib import Path


def run_command(command, cwd="."):
    process = subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        capture_output=True,
        text=True,
    )

    return {
        "command": command,
        "success": process.returncode == 0,
        "stdout": process.stdout[-5000:],
        "stderr": process.stderr[-5000:],
        "returncode": process.returncode,
    }


def validate_python_files(paths, cwd="."):
    results = []

    for path in paths:
        if not path.endswith(".py"):
            continue

        if not Path(cwd, path).exists():
            continue

        results.append(
            run_command(
                f"python -m py_compile {path}",
                cwd=cwd,
            )
        )

    return results


def validation_passed(results):
    return all(
        result["success"]
        for result in results
    )
