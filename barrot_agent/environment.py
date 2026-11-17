"""Environment detection and behavior flags.

Barrot runs in three places that look similar and behave differently: a Debian
userland, a Termux userland on Android, and a PRoot container inside Termux on a
phone. Guessing wrong costs a broken keybinding or a wall of output on a phone.

Detected values are cached at data/environment.json and printed on startup.
Every field has an "unknown" state instead of a guess.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

CACHE_PATH = Path("data") / "environment.json"
TERMUX_PREFIX = "/data/data/com.termux/files/usr"
LOW_MEMORY_DEVICES = ("moto g7", "moto g", "sm-g", "redmi")


@dataclass
class Environment:
    platform: str = "unknown"
    distro_family: str = "unknown"
    distro_name: str = "unknown"
    arch: str = "unknown"
    device_model: str = "unknown"
    proot: bool = False
    android: bool = False
    shell: str = "unknown"
    surface: str = "unknown"
    home: str = ""
    tools: dict[str, str] = field(default_factory=dict)

    @property
    def lightweight(self) -> bool:
        """True when output should stay short: phone-scale device or no full TTY."""
        model = self.device_model.lower()
        return any(token in model for token in LOW_MEMORY_DEVICES)

    @property
    def enter_safe(self) -> bool:
        """True when behaviour may assume an interactive Enter key exists."""
        return self.surface in {"opencode-tui", "interactive-shell"}

    @property
    def summary(self) -> str:
        return f"{self.platform}/{self.distro_family} {self.distro_name} {self.arch}"


def _read_os_release() -> tuple[str, str]:
    path = Path("/etc/os-release")
    if not path.exists():
        return "unknown", "unknown"
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if "=" in line:
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip('"')
    name = values.get("PRETTY_NAME", values.get("NAME", "unknown"))
    family = "debian" if "debian" in name.lower() or "ubuntu" in name.lower() else "linux"
    return family, name


def _device_model() -> str:
    getprop = shutil.which("getprop")
    if getprop:
        try:
            out = subprocess.run(
                [getprop, "ro.product.model"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            model = out.stdout.strip()
            if model:
                return model
        except (OSError, subprocess.SubprocessError):
            pass
    return "unknown"


def _detect_surface() -> str:
    """Best-effort. Returns 'unknown' rather than guessing."""
    if not sys.stdout.isatty():
        return "opencode-run" if os.environ.get("OPENCODE") else "non-interactive"
    if os.environ.get("OPENCODE"):
        return "opencode-tui"
    if os.environ.get("TERM"):
        return "interactive-shell"
    return "unknown"


def detect() -> Environment:
    kernel = platform.system().lower()
    arch = platform.machine()
    family, distro = _read_os_release() if kernel == "linux" else ("unknown", platform.platform())
    termux = os.path.isdir(TERMUX_PREFIX)
    proot = "proot" in platform.release().lower()
    tools = {
        name: shutil.which(name) or ""
        for name in ("python3", "git", "gh", "uv", "node", "npx", "opencode", "termux-info")
    }
    return Environment(
        platform=kernel,
        distro_family="termux" if termux and family == "unknown" else family,
        distro_name=distro,
        arch=arch,
        device_model=_device_model(),
        proot=proot,
        android=termux,
        shell=os.path.basename(os.environ.get("SHELL", "")) or "unknown",
        surface=_detect_surface(),
        home=os.environ.get("HOME", ""),
        tools=tools,
    )


def save(env: Environment, path: Path | None = None) -> Path:
    path = path or CACHE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(env), indent=2), encoding="utf-8")
    return path


def load(path: Path | None = None) -> Environment | None:
    path = path or CACHE_PATH
    if not path.exists():
        return None
    try:
        return Environment(**json.loads(path.read_text(encoding="utf-8")))
    except (json.JSONDecodeError, TypeError):
        return None


def describe(env: Environment | None = None) -> str:
    env = env or detect()
    found = [name for name, path in env.tools.items() if path]
    missing = [name for name, path in env.tools.items() if not path]
    lines = [
        "ENVIRONMENT",
        f"  system   {env.summary}",
        f"  device   {env.device_model}" + (" (proot)" if env.proot else ""),
        f"  shell    {env.shell}",
        f"  surface  {env.surface}",
        f"  behaviour lightweight_output={env.lightweight} enter_safe={env.enter_safe}",
        f"  tools    {', '.join(found) or 'none'}",
    ]
    if missing:
        lines.append(f"  missing  {', '.join(missing)}")
    return "\n".join(lines)


def startup_banner() -> str:
    """Detect, cache, and return the banner to print once at startup."""
    env = detect()
    save(env)
    return describe(env)


if __name__ == "__main__":
    print(startup_banner())
