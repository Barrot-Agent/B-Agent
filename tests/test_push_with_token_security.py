from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PUSH_SCRIPT = REPO_ROOT / "scripts" / "push_with_token.sh"
TOKEN = "sentinel-gh-token-must-not-appear-in-argv"


def _fake_program(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)


def test_curl_validation_receives_token_on_stdin_not_argv(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    args_path = tmp_path / "curl-args.json"
    stdin_path = tmp_path / "curl-stdin.txt"
    fake_curl = bin_dir / "curl"
    _fake_program(
        fake_curl,
        f"""#!{shutil.which("python3")}
import json
import os
import sys
Path = __import__("pathlib").Path
Path(os.environ["CAPTURE_ARGS_PATH"]).write_text(json.dumps(sys.argv[1:]), encoding="utf-8")
Path(os.environ["CAPTURE_STDIN_PATH"]).write_text(sys.stdin.read(), encoding="utf-8")
Path(os.environ["CAPTURE_ENV_PATH"]).write_text(os.environ.get("GH_TOKEN", "<missing>"), encoding="utf-8")
print("200")
""",
    )

    env = os.environ.copy()
    env.update(
        {
            "GH_TOKEN": TOKEN,
            "REPO_SLUG": "Barrot-Agent/B-Agent",
            "BRANCH": "integration/test",
            "PATH": str(bin_dir) + os.pathsep + env.get("PATH", ""),
            "CAPTURE_ARGS_PATH": str(args_path),
            "CAPTURE_STDIN_PATH": str(stdin_path),
            "CAPTURE_ENV_PATH": str(tmp_path / "curl-env.txt"),
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_PAGER": "cat",
        }
    )
    result = subprocess.run(
        ["bash", str(PUSH_SCRIPT), "--verify-only"],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    child_args = json.loads(args_path.read_text(encoding="utf-8"))
    child_stdin = stdin_path.read_text(encoding="utf-8")
    assert TOKEN not in " ".join(child_args)
    assert child_args[:2] == ["--config", "-"]
    assert f"Authorization: Bearer {TOKEN}" in child_stdin
    assert (tmp_path / "curl-env.txt").read_text(encoding="utf-8") == "<missing>"
    assert TOKEN not in result.stdout
    assert TOKEN not in result.stderr


def test_python_fallback_receives_token_on_stdin_not_argv(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for command in ("git", "dirname"):
        source = shutil.which(command)
        assert source is not None
        (bin_dir / command).symlink_to(source)
    args_path = tmp_path / "python-args.json"
    stdin_path = tmp_path / "python-stdin.txt"
    fake_python = bin_dir / "python3"
    _fake_program(
        fake_python,
        f"""#!{shutil.which("python3")}
import json
import os
import sys
from pathlib import Path
Path(os.environ["CAPTURE_ARGS_PATH"]).write_text(json.dumps(sys.argv[1:]), encoding="utf-8")
Path(os.environ["CAPTURE_STDIN_PATH"]).write_text(sys.stdin.read(), encoding="utf-8")
Path(os.environ["CAPTURE_ENV_PATH"]).write_text(os.environ.get("GH_TOKEN", "<missing>"), encoding="utf-8")
print("200")
""",
    )

    env = os.environ.copy()
    env.update(
        {
            "GH_TOKEN": TOKEN,
            "REPO_SLUG": "Barrot-Agent/B-Agent",
            "BRANCH": "integration/test",
            "PATH": str(bin_dir),
            "CAPTURE_ARGS_PATH": str(args_path),
            "CAPTURE_STDIN_PATH": str(stdin_path),
            "CAPTURE_ENV_PATH": str(tmp_path / "python-env.txt"),
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_PAGER": "cat",
        }
    )
    result = subprocess.run(
        [shutil.which("bash"), str(PUSH_SCRIPT), "--verify-only"],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    child_args = json.loads(args_path.read_text(encoding="utf-8"))
    child_stdin = stdin_path.read_text(encoding="utf-8")
    assert TOKEN not in " ".join(child_args)
    assert child_args[0] == "-c"
    assert TOKEN in child_stdin.splitlines()
    assert (tmp_path / "python-env.txt").read_text(encoding="utf-8") == "<missing>"
    assert TOKEN not in result.stdout
    assert TOKEN not in result.stderr


def test_git_credential_helper_keeps_token_as_literal_environment_expansion() -> None:
    content = PUSH_SCRIPT.read_text(encoding="utf-8")
    assert "git -c credential.helper='!f()" in content
    assert 'password=${GH_TOKEN}' in content
    assert 'python3 - "${GH_TOKEN}"' not in content
    assert 'Authorization: Bearer %s' in content

def test_direct_main_push_is_refused_before_token_validation() -> None:
    env = os.environ.copy()
    env.pop("GH_TOKEN", None)
    env["BRANCH"] = "main"
    result = subprocess.run(
        ["bash", str(PUSH_SCRIPT), "--verify-only"],
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
        check=False,
    )
    assert result.returncode == 6
    assert "direct pushes to main are disabled" in result.stderr.lower()
    assert "gh_token is not set" not in result.stderr.lower()
