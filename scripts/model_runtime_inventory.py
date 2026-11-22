#!/usr/bin/env python3
"""Read-only inventory of Barrot inference configuration; never prints secrets."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import platform
import sys
from typing import Mapping

SECRET_ENV_NAMES = {
    "GROQ_API_KEY", "FIREWORKS_API_KEY", "GH_MODELS_TOKEN", "GITHUB_TOKEN",
    "GITHUB_APP_PRIVATE_KEY", "GITHUB_APP_ID", "GITHUB_INSTALLATION_ID",
    "GEMINI_API_KEY", "BRAIN_SHARED_SECRET", "LUNAROUTE_API_KEY",
    "BARROT_LLM_API_KEY", "OPENROUTER_API_KEY", "CLOUDFLARE_API_TOKEN",
}
PROVIDER_SURFACES = (
    {
        "surface": "repository_repair_worker",
        "entrypoint": "scripts/barrot_agent.py",
        "selection": "BARROT_LLM_PROVIDER (groq or local; default groq)",
        "model": "BARROT_LLM_MODEL, then BRAIN_MODEL; Groq default openai/gpt-oss-120b",
        "credential_env": ("BARROT_LLM_API_KEY", "GROQ_API_KEY"),
        "capabilities": ("chat", "native tool loop"),
        "external_transfer_default": "Groq requires provider credential; local route is loopback-only",
    },
    {
        "surface": "shared_inference_helper",
        "entrypoint": "barrot_agent/orchestration/shared_inference.py",
        "selection": "first configured credential: Groq, then Fireworks",
        "model": "GROQ_MODEL or FIREWORKS_MODEL",
        "credential_env": ("GROQ_API_KEY", "FIREWORKS_API_KEY"),
        "capabilities": ("text chat only in this helper",),
        "external_transfer_default": "credential presence selects provider; no explicit consent gate in this helper",
    },
    {
        "surface": "barrot_brain",
        "entrypoint": "barrot_agent/barrot_brain.py",
        "selection": "GitHub App first, then Groq; Fireworks only with BARROT_ALLOW_FIREWORKS_FALLBACK",
        "model": "code-defined provider model constants",
        "credential_env": ("GITHUB_APP_ID", "GITHUB_APP_PRIVATE_KEY", "GITHUB_INSTALLATION_ID", "GROQ_API_KEY", "FIREWORKS_API_KEY"),
        "capabilities": ("chat",),
        "external_transfer_default": "external inference disabled unless caller opts in",
    },
    {
        "surface": "huggingface_space_chat",
        "entrypoint": "hf_space/app.py",
        "selection": "BRAIN_PRIMARY; operator opt-in and session consent both required",
        "model": "BRAIN_MODEL override or selected provider default",
        "credential_env": ("GROQ_API_KEY", "GH_MODELS_TOKEN", "GEMINI_API_KEY", "BRAIN_SHARED_SECRET"),
        "capabilities": ("chat", "native tool loop for providers marked tools=true"),
        "external_transfer_default": "disabled unless BARROT_ALLOW_EXTERNAL_INFERENCE and session consent",
    },
    {
        "surface": "opencode_repository_agent",
        "entrypoint": "opencode.json and AGENTS.md",
        "selection": "default_agent and model in opencode.json",
        "model": "configured model identifier; provider authentication is separate",
        "credential_env": ("GITHUB_MCP_TOKEN", "LUNAROUTE_API_KEY"),
        "capabilities": ("repository agent", "MCP tools only when separately authenticated and enabled"),
        "external_transfer_default": "OpenCode default model is config, not proof of provider authentication; LunaRoute MCP disabled in checked-in config",
    },
)


def _present(env: Mapping[str, str], names: tuple[str, ...]) -> dict[str, bool]:
    return {name: bool(str(env.get(name, "")).strip()) for name in names}


def inspect_runtime(root: str | Path, env: Mapping[str, str] | None = None) -> dict:
    """Describe checked-in routing surfaces and this process's env-key presence only."""
    root_path = Path(root).expanduser().resolve(strict=True)
    if not root_path.is_dir():
        raise ValueError("repository root must be a directory")
    current_env = os.environ if env is None else env

    surfaces = []
    for spec in PROVIDER_SURFACES:
        record = dict(spec)
        record["credential_presence"] = _present(current_env, tuple(spec["credential_env"]))
        record["credential_values_exposed"] = False
        surfaces.append(record)

    repair_provider = str(current_env.get("BARROT_LLM_PROVIDER", "groq")).strip().lower() or "groq"
    repair_model = (
        str(current_env.get("BARROT_LLM_MODEL", "")).strip()
        or str(current_env.get("BRAIN_MODEL", "")).strip()
        or ("openai/gpt-oss-120b" if repair_provider == "groq" else None)
    )
    repair_base = str(current_env.get("BARROT_LLM_BASE_URL", "")).strip()
    if repair_provider == "local":
        repair_base = repair_base or "http://127.0.0.1:8080/v1/chat/completions"
        local_endpoint_allowed = repair_base.startswith(("http://127.0.0.1:", "http://localhost:", "http://[::1]:"))
    else:
        repair_base = repair_base or "https://api.groq.com/openai/v1/chat/completions"
        local_endpoint_allowed = None

    opencode_config = {}
    opencode_path = root_path / "opencode.json"
    if opencode_path.is_file() and not opencode_path.is_symlink():
        try:
            parsed = json.loads(opencode_path.read_text(encoding="utf-8"))
            if isinstance(parsed, dict):
                opencode_config = parsed
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            pass

    mcp_servers = opencode_config.get("mcp", {}).get("servers", {})
    lunaroute_mcp = mcp_servers.get("lunaroute", {}) if isinstance(mcp_servers, dict) else {}
    return {
        "schema_version": "barrot.inference_runtime_inventory.v1",
        "inventory_mode": "READ_ONLY_CONFIGURATION_AND_ENVIRONMENT_PRESENCE",
        "execution_context": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "environment_scope": "This process only; does not inspect Termux, OpenCode, GitHub Actions, or remote Space environments unless run there.",
        },
        "active_worker_snapshot": {
            "surface": "repository_repair_worker",
            "provider": repair_provider,
            "model": repair_model,
            "endpoint": repair_base,
            "credential_presence": _present(current_env, ("BARROT_LLM_API_KEY", "GROQ_API_KEY")),
            "local_endpoint_loopback_allowed": local_endpoint_allowed,
            "configuration_only": True,
            "connectivity_tested": False,
            "inference_executed": False,
        },
        "opencode_snapshot": {
            "default_agent": opencode_config.get("default_agent"),
            "model": opencode_config.get("model"),
            "lunaroute_provider_declared": "lunaroute" in opencode_config.get("provider", {}),
            "lunaroute_mcp_declared": bool(lunaroute_mcp),
            "lunaroute_mcp_disabled": lunaroute_mcp.get("disabled") is True,
            "authentication_verified": False,
            "model_execution_verified": False,
        },
        "provider_surfaces": surfaces,
        "safety": {
            "secret_values_read_or_emitted": False,
            "network_requests_made": False,
            "model_weights_read_or_modified": False,
            "inference_executed": False,
            "production_configuration_modified": False,
        },
        "limitations": [
            "Environment-key presence is not proof that a credential is valid or authorized.",
            "A checked-in model identifier is not proof of provider authentication, connectivity, or successful inference.",
            "This process cannot see environment variables held only by Termux, OpenCode, GitHub Actions, or a remote Space.",
            "Provider surfaces are separate execution paths; this inventory does not imply a unified router.",
            "No model artifact or tensor was loaded, benchmarked, or modified.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository", nargs="?", default=".", help="Barrot repository root")
    parser.add_argument("--output", help="Write JSON report to a new file; default stdout")
    args = parser.parse_args()
    try:
        report = inspect_runtime(args.repository)
    except (OSError, ValueError) as exc:
        print(f"model-runtime-inventory: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        target = Path(args.output).expanduser()
        if target.exists():
            print("model-runtime-inventory: refusing to overwrite an existing report", file=sys.stderr)
            return 2
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
