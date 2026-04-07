"""
OpenShell Usage Examples
========================

Complete, runnable examples demonstrating the B-Agent OpenShell secure runtime.
"""

from __future__ import annotations

import sys
import os

# Allow running from the repo root without installing the package.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import yaml

# ---------------------------------------------------------------------------
# Example 1: Initialising the OpenShell runtime
# ---------------------------------------------------------------------------

def example_runtime_initialization() -> None:
    """Show how to create and initialise the OpenShellRuntime."""
    from barrot_agent.runtime.openshell_runtime import OpenShellRuntime

    runtime = OpenShellRuntime(policy_path="openshell/policies")
    runtime.initialize()

    stats = runtime.get_runtime_stats()
    print("[Runtime] Initialised — stats:", stats)

    runtime.shutdown()


# ---------------------------------------------------------------------------
# Example 2: Wrapping an agent with policy enforcement
# ---------------------------------------------------------------------------

def example_wrap_agent() -> None:
    """Demonstrate wrapping a plain callable with OpenShell policy checks."""
    from barrot_agent.runtime.openshell_runtime import (
        OpenShellRuntime,
        PolicyViolationError,
    )

    runtime = OpenShellRuntime(policy_path="openshell/policies")
    runtime.initialize()

    # inference_agent is listed in api_restrictions.execute_code.allow_from
    def inference_agent(prompt: str) -> str:  # noqa: E306
        return f"Response to: {prompt}"

    inference_agent.__name__ = "inference_agent"
    wrapped = runtime.wrap_agent(inference_agent)

    try:
        result = wrapped("What is quantum computing?")
        print("[Wrap] Agent returned:", result)
    except PolicyViolationError as exc:
        print("[Wrap] Blocked:", exc)

    runtime.shutdown()


# ---------------------------------------------------------------------------
# Example 3: Direct policy enforcement check
# ---------------------------------------------------------------------------

def example_policy_enforcement() -> None:
    """Manually evaluate an action against the loaded policies."""
    from barrot_agent.runtime.openshell_runtime import OpenShellRuntime

    runtime = OpenShellRuntime(policy_path="openshell/policies")
    runtime.initialize()

    # Allowed: inference_agent requesting network_request
    decision = runtime.execute_with_policy(
        action="network_request",
        context={"domain": "huggingface.co"},
        agent_id="inference_agent",
    )
    print(f"[Policy] network_request for inference_agent → allowed={decision.allowed}")

    # Denied: audit_agent requesting access_credentials
    decision2 = runtime.execute_with_policy(
        action="access_credentials",
        context={},
        agent_id="audit_agent",
    )
    print(f"[Policy] access_credentials for audit_agent   → allowed={decision2.allowed}")

    runtime.shutdown()


# ---------------------------------------------------------------------------
# Example 4: Privacy-first inference routing
# ---------------------------------------------------------------------------

def example_inference_routing() -> None:
    """Show how PrivacyRouter selects endpoints and anonymises data."""
    from barrot_agent.inference.privacy_router import PrivacyRouter

    with open("openshell/policies/inference_routes.yaml") as fh:
        config = yaml.safe_load(fh)

    # Simulate local GPU healthy, remote available as fallback
    router = PrivacyRouter(
        config,
        endpoint_health={"local_nvidia_gpu": True, "huggingface_api": True},
    )

    # Request containing PII that should be stripped on remote calls
    payload = {
        "prompt": "Summarise the research for user john.doe@company.com",
        "max_tokens": 200,
    }

    result = router.route_inference("granite-vision", payload)
    print(f"[Router] Model=granite-vision → endpoint={result['endpoint']}")
    print(f"[Router] Privacy applied: {result['privacy_applied']}")

    # Force fallback
    router2 = PrivacyRouter(
        config,
        endpoint_health={"local_nvidia_gpu": False, "huggingface_api": True},
    )
    result2 = router2.route_inference("llama3", payload)
    print(f"[Router] Fallback → endpoint={result2['endpoint']}")
    print(f"[Router] Anonymised prompt: {result2['request_data']['prompt'][:60]}...")


# ---------------------------------------------------------------------------
# Example 5: Audit trail query
# ---------------------------------------------------------------------------

def example_audit_trail() -> None:
    """Demonstrate recording and querying the audit trail."""
    import tempfile
    from openshell.audit.audit_engine import AuditEngine
    from openshell.audit.compliance_reporter import ComplianceReporter

    with tempfile.TemporaryDirectory() as tmpdir:
        engine = AuditEngine(audit_directory=tmpdir)

        # Record some events
        engine.record_action("inference", {"model": "llama3"}, "inference_agent")
        engine.record_action("network_request", {"domain": "huggingface.co"}, "inference_agent")
        engine.record_violation(
            "unauthorized_domain", {"domain": "evil.com"}, "rogue_agent"
        )

        trail = engine.get_audit_trail()
        print(f"[Audit] Total events: {len(trail)}")

        inference_trail = engine.get_audit_trail(agent_id="inference_agent")
        print(f"[Audit] inference_agent events: {len(inference_trail)}")

        reporter = ComplianceReporter(engine)
        summary = reporter.get_violation_summary()
        print(f"[Audit] Violation summary: {summary}")


# ---------------------------------------------------------------------------
# Example 6: Sandboxed command execution
# ---------------------------------------------------------------------------

def example_sandboxed_execution() -> None:
    """Run a command inside the sandbox executor with resource limits."""
    from barrot_agent.security.sandbox_executor import SandboxExecutor

    executor = SandboxExecutor(
        limits={
            "max_cpu_seconds": 10,
            "max_memory_bytes": 128 * 1024 * 1024,
        }
    )

    result = executor.execute_command(["python3", "--version"], timeout=5)
    print(f"[Sandbox] returncode={result['returncode']} stdout={result['stdout'].strip()}")
    print(f"[Sandbox] Stats: {executor.get_execution_stats()}")


# ---------------------------------------------------------------------------
# Run all examples
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("OpenShell Usage Examples")
    print("=" * 60)

    examples = [
        ("Runtime Initialization", example_runtime_initialization),
        ("Agent Wrapping", example_wrap_agent),
        ("Policy Enforcement", example_policy_enforcement),
        ("Inference Routing", example_inference_routing),
        ("Audit Trail", example_audit_trail),
        ("Sandboxed Execution", example_sandboxed_execution),
    ]

    for name, fn in examples:
        print(f"\n--- {name} ---")
        try:
            fn()
        except Exception as exc:
            print(f"  [ERROR] {exc}")
