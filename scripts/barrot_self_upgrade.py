#!/usr/bin/env python3
"""Deterministic Barrot self-upgrade candidate generator."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from barrot_agent.orchestration.shared_runtime import (
    CompletionGate,
    DurableStateStore,
    ExecutionRecord,
    Failure,
    FailureCode,
    Fingerprint,
    ProviderClient,
    RetryPolicy,
    ValidationResult,
    bounded_subprocess,
)

GROQ_KEY = os.environ.get("GROQ_API_KEY", "")
SCRIPTS_DIR = REPO_ROOT / "scripts"
AUDIT_PATH = REPO_ROOT / "barrot_capability_audit.json"
STATE_STORE = DurableStateStore(REPO_ROOT, "barrot_self_upgrade")

MODEL_CANDIDATES = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]

BANNED_TERMS = [
    "rm -rf",
    ".git/",
    "git reset --hard",
    "git checkout main",
    "sed -i",
    "git push",
    'subprocess.run(["git"',
    "os.system",
    "quantum harmonization",
    "free energy",
    "Willowchip",
    "Aethel",
    "Planck-scale",
    "bio-computing",
    "144-agent council",
]


class SelfUpgradeError(RuntimeError):
    pass


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_audit() -> dict[str, Any] | None:
    if not AUDIT_PATH.exists():
        return None
    return json.loads(AUDIT_PATH.read_text(encoding="utf-8"))


def strip_fences(text: str) -> str:
    match = re.search(r"```(?:python)?\s*\n(.*?)```", text, re.S)
    return match.group(1) if match else text


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=False)


def _groq_headers() -> dict[str, str]:
    return {
        "Authorization": "Bearer " + GROQ_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Barrot-Agent/1.0",
    }


def _send_groq_request(payload: dict[str, Any]) -> dict[str, Any]:
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers=_groq_headers(),
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.load(resp)


def call_groq(prompt: str) -> tuple[str, list[dict[str, Any]], Failure | None]:
    execution_records: list[dict[str, Any]] = []
    if not GROQ_KEY:
        failure = Failure(
            code=FailureCode.PROVIDER_AUTH.value,
            message="GROQ_API_KEY not set",
            failed_operation="call_groq",
        )
        return "", execution_records, failure
    for model in MODEL_CANDIDATES:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 2000,
            "temperature": 0.4,
        }
        client = ProviderClient(
            name=f"groq:{model}",
            send=_send_groq_request,
            retry_policy=RetryPolicy(max_attempts=3, base_delay_seconds=1.0, max_delay_seconds=8.0),
        )
        response, records, failure = client.request(payload)
        execution_records.extend(record.to_dict() for record in records)
        if response is None:
            if failure and failure.code == FailureCode.PROVIDER_TOOL_CONFLICT.value:
                return "", execution_records, failure
            continue
        try:
            content = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            failure = Failure(
                code=FailureCode.PROVIDER_INVALID_JSON.value,
                message=str(exc),
                raw_error=json.dumps(response)[:1000],
                failed_operation=f"groq:{model}",
                request_payload=payload,
            )
            execution_records.append(
                ExecutionRecord(
                    record_id=Fingerprint.create(model, response).value,
                    operation="provider_response_parse",
                    state="FAILED",
                    input_fingerprint=Fingerprint.create(payload).value,
                    output_fingerprint=Fingerprint.create(response).value,
                    request=payload,
                    response=response,
                    provider=model,
                    failure=failure,
                ).to_dict()
            )
            continue
        if content:
            return str(content), execution_records, None
    failure = Failure(
        code=FailureCode.RETRY_EXHAUSTED.value,
        message="All configured models failed to return code.",
        failed_operation="call_groq",
    )
    return "", execution_records, failure


def generate_capability(gap_id: int, gap_name: str) -> tuple[str | None, list[dict[str, Any]], Failure | None]:
    prompt = f"""Implement this capability as a standalone Python script: {gap_name} (gap ID {gap_id})

HARD CONSTRAINTS:
- stdlib only (os, sys, json, urllib.request, pathlib, datetime, subprocess for read-only checks)
- Call Groq via urllib for any analysis
- Read GROQ_API_KEY from env; exit non-zero if unset
- Write results to a JSON file; never mutate existing repo files
- NO git commands, NO os.system, NO shell mutation, NO rm
- If real input data is unavailable, write an explicit null/unavailable field.
  NEVER generate placeholder, simulated, or randomized values as if they were results.
- Do not reference hardware, APIs, or database tables you cannot verify exist

Output ONLY the Python source, starting with the shebang."""
    raw, records, failure = call_groq(prompt)
    if not raw:
        return None, records, failure
    code = strip_fences(raw).strip()
    if not code.startswith("#!"):
        return None, records, Failure(
            code=FailureCode.VALIDATION_FAILED.value,
            message="Generated output does not start with a shebang.",
            failed_operation="generate_capability",
            raw_error=code[:500],
        )
    for term in BANNED_TERMS:
        if term in code:
            return None, records, Failure(
                code=FailureCode.VALIDATION_FAILED.value,
                message=f"Generated code contains banned term: {term}",
                failed_operation="generate_capability",
                raw_error=term,
            )
    for fake in ("random.uniform", "random.random", "random.randint", "fake_", "placeholder"):
        if fake in code:
            return None, records, Failure(
                code=FailureCode.VALIDATION_FAILED.value,
                message=f"Generated code contains fabricated-data pattern: {fake}",
                failed_operation="generate_capability",
                raw_error=fake,
            )
    return code, records, None


def verify_syntax(code: str) -> ValidationResult:
    tmp = REPO_ROOT / ".selfupgrade_candidate.py"
    tmp.write_text(code, encoding="utf-8")
    try:
        return bounded_subprocess([sys.executable, "-m", "py_compile", str(tmp)], cwd=REPO_ROOT, timeout=60)
    finally:
        tmp.unlink(missing_ok=True)


def open_capability_pr(gap_name: str, code: str) -> dict[str, Any]:
    slug = re.sub(r"[^a-z0-9]+", "_", gap_name.lower()).strip("_")[:40]
    target = SCRIPTS_DIR / f"{slug}.py"
    if target.exists():
        raise SelfUpgradeError(f"{target.name} already exists")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    branch = f"selfupgrade/{slug}-{stamp}"
    current_branch = git("branch", "--show-current")
    if current_branch.returncode != 0:
        raise SelfUpgradeError(current_branch.stderr[:500] or "Unable to determine current branch")
    restore_branch = current_branch.stdout.strip() or "main"
    checkout = git("checkout", "-b", branch)
    if checkout.returncode != 0:
        raise SelfUpgradeError(checkout.stderr[:500])
    target.write_text(code, encoding="utf-8")
    add = git("add", str(target.relative_to(REPO_ROOT)))
    if add.returncode != 0:
        raise SelfUpgradeError(add.stderr[:500])
    commit = git("commit", "-m", f"Self-upgrade candidate: {gap_name}")
    if commit.returncode != 0:
        raise SelfUpgradeError(commit.stderr[:500])
    push = git("push", "-u", "origin", branch)
    if push.returncode != 0:
        raise SelfUpgradeError(push.stderr[:500])
    head_sha = git("rev-parse", "HEAD")
    if head_sha.returncode != 0 or not head_sha.stdout.strip():
        raise SelfUpgradeError(head_sha.stderr[:500] or "Unable to determine HEAD commit")
    remote_check = git("ls-remote", "--heads", "origin", branch)
    remote_ref = remote_check.stdout.strip()
    remote_sha = remote_ref.split()[0].strip() if remote_ref else ""
    remote_verified = (
        remote_check.returncode == 0
        and bool(remote_sha)
        and head_sha.stdout.strip() == remote_sha
        and f"refs/heads/{branch}" in remote_ref
    )
    body = (
        f"Autonomous self-upgrade candidate for gap: **{gap_name}**\n\n"
        "Generated by scripts/barrot_self_upgrade.py. Completed deterministic generation, "
        "banned-term, fabricated-data, syntax, commit, push, and remote branch verification steps.\n\n"
        f"- commit: {head_sha.stdout.strip()}\n"
        f"- remote_branch_verification: {'passed' if remote_verified else 'failed'}\n\n"
        "Requires human review before merge."
    )
    body_file = REPO_ROOT / ".selfupgrade_pr_body.md"
    body_file.write_text(body, encoding="utf-8")
    try:
        pr = subprocess.run(
            ["gh", "pr", "create", "--title", f"Self-upgrade: {gap_name}", "--body-file", str(body_file), "--base", "main", "--head", branch],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        body_file.unlink(missing_ok=True)
        git("checkout", restore_branch)
    if pr.returncode != 0:
        raise SelfUpgradeError(pr.stderr[:500] or pr.stdout[:500])
    return {
        "branch": branch,
        "target": str(target),
        "commit": head_sha.stdout.strip(),
        "remote_verified": remote_verified,
        "remote_ref": remote_ref,
        "pr_output": pr.stdout.strip() or pr.stderr.strip(),
        "restored_branch": restore_branch,
    }


def self_upgrade() -> int:
    run_record: dict[str, Any] = {
        "run_id": Fingerprint.create(now_iso(), str(AUDIT_PATH)).value[:24],
        "timestamp": now_iso(),
        "status": "FAILED",
        "execution_records": [],
        "failure": None,
    }
    try:
        audit = load_audit()
    except json.JSONDecodeError as exc:
        failure = Failure(
            code=FailureCode.VALIDATION_FAILED.value,
            message=f"Capability audit is not valid JSON: {exc}",
            failed_operation="load_audit",
            raw_error=str(exc),
        )
        run_record["failure"] = failure.to_dict()
        run_record["completion_gate"] = CompletionGate(
            gate_id=Fingerprint.create("self_upgrade", "invalid_audit").value,
            requirements={"audit_loaded": False, "audit_valid": False},
            satisfied=False,
            unresolved=["Capability audit is not valid JSON."],
        ).to_dict()
        STATE_STORE.write_state(run_record["run_id"], run_record, fingerprint=Fingerprint.create("self_upgrade", "invalid_audit").value)
        print("Capability audit invalid")
        return 1
    if audit is None:
        failure = Failure(
            code=FailureCode.VALIDATION_FAILED.value,
            message="Capability audit missing; run scripts/barrot_capability_audit.py first.",
            failed_operation="load_audit",
        )
        run_record["failure"] = failure.to_dict()
        run_record["completion_gate"] = CompletionGate(
            gate_id=Fingerprint.create("self_upgrade", "missing_audit").value,
            requirements={"audit_loaded": False, "gaps_present": None},
            satisfied=False,
            unresolved=["Capability audit is missing."],
        ).to_dict()
        STATE_STORE.write_state(run_record["run_id"], run_record, fingerprint=Fingerprint.create("self_upgrade", "missing_audit").value)
        print("Capability audit missing")
        return 1
    if not audit.get("gaps"):
        run_record["status"] = "NO_REPAIR_REQUIRED"
        run_record["completion_gate"] = CompletionGate(
            gate_id=Fingerprint.create("self_upgrade", "no_gaps").value,
            requirements={"audit_loaded": True, "gaps_present": False},
            satisfied=True,
            unresolved=[],
        ).to_dict()
        STATE_STORE.write_state(run_record["run_id"], run_record, fingerprint=Fingerprint.create("self_upgrade", audit or {}).value)
        print("No capability gaps found")
        return 0
    gap = audit["gaps"][0]
    run_record["selected_gap"] = gap
    code, provider_records, provider_failure = generate_capability(gap["id"], gap["name"])
    run_record["execution_records"].extend(provider_records)
    if provider_failure is not None or code is None:
        run_record["failure"] = provider_failure.to_dict() if provider_failure else None
        STATE_STORE.write_state(run_record["run_id"], run_record, fingerprint=Fingerprint.create("self_upgrade", gap).value)
        print("Generation failed")
        return 1
    syntax = verify_syntax(code)
    run_record["syntax_validation"] = syntax.to_dict()
    if not syntax.passed:
        run_record["failure"] = syntax.failure.to_dict() if syntax.failure else None
        STATE_STORE.write_state(run_record["run_id"], run_record, fingerprint=Fingerprint.create("self_upgrade", gap).value)
        print("Syntax verification failed")
        return 1
    try:
        pr_data = open_capability_pr(gap["name"], code)
    except Exception as exc:  # noqa: BLE001
        failure = Failure(
            code=FailureCode.VALIDATION_FAILED.value,
            message=str(exc),
            failed_operation="open_capability_pr",
            raw_error=str(exc),
        )
        run_record["failure"] = failure.to_dict()
        STATE_STORE.write_state(run_record["run_id"], run_record, fingerprint=Fingerprint.create("self_upgrade", gap).value)
        print("Failed to open PR")
        return 1
    run_record["pr"] = pr_data
    gate = CompletionGate(
        gate_id=Fingerprint.create("self_upgrade_gate", gap, pr_data).value,
        requirements={
            "audit_loaded": True,
            "gap_selected": True,
            "code_generated": True,
            "syntax_valid": True,
            "commit_created": bool(pr_data.get("commit")),
            "remote_verified": bool(pr_data.get("remote_verified")),
            "pr_created": bool(pr_data.get("pr_output")),
        },
        satisfied=all(
            [
                True,
                True,
                True,
                True,
                bool(pr_data.get("commit")),
                bool(pr_data.get("remote_verified")),
                bool(pr_data.get("pr_output")),
            ]
        ),
        unresolved=[] if pr_data.get("remote_verified") else ["Remote branch verification failed."],
    )
    run_record["completion_gate"] = gate.to_dict()
    run_record["status"] = "COMPLETE" if gate.satisfied else "BLOCKED"
    STATE_STORE.write_state(run_record["run_id"], run_record, fingerprint=Fingerprint.create("self_upgrade", gap).value)
    print(f"Self-upgrade candidate processed: {gap['name']}")
    return 0 if gate.satisfied else 1


if __name__ == "__main__":
    sys.exit(self_upgrade())
