#!/usr/bin/env python3
import subprocess
import time
import json
import os

BRAIN_PATH = "/data/data/com.termux/files/home/barrot/barrot_brain_unified.json"
BARROT_DIR = "/data/data/com.termux/files/home/barrot"

TOPICS = [
    "State Space Models Mamba architecture selective state spaces",
    "Mixture of Experts sparse activation routing mechanisms",
    "Hyena Monarch Mixer subquadratic attention alternatives",
    "Retention Networks parallel recurrent dual-mode inference",
    "Liquid Neural Networks continuous time dynamic systems",
    "Test Time Compute Scaling reasoning through inference",
    "Neuromorphic computing spike-based inference",
    "Quantum-classical hybrid algorithms",
    "Photonic computing neural inference",
    "DNA data storage biological computing",
    "Brain-computer interfaces neural decoding",
    "Federated learning privacy-preserving AI",
    "Autonomous agent swarms multi-agent coordination",
    "Generative world models simulation-based reasoning",
    "6G network intelligence edge AI deployment",
    "Formal theorem proving Lean 4 Isabelle proof assistants",
    "Symbolic regression equation discovery",
    "AlphaGeometry geometry reasoning pipelines",
    "Chain of thought process reward models",
    "Mathematical olympiad problem decomposition",
    "Automated conjecture generation",
    "Category theory unifying mathematical framework",
    "Quantization INT4 INT8 GPTQ AWQ compression",
    "Knowledge distillation model compression pipelines",
    "ONNX runtime cross-platform inference optimization",
    "Sparse computation structured pruning",
    "In-memory computing analog inference chips",
    "Apple Neural Engine mobile NPU architectures",
    "WebAssembly AI inference browser",
    "BitNet 1-bit large language models",
    "MRP recursive decomposition multi-domain reasoning",
    "Ping-pong ensemble refinement proof verification",
    "Knowledge graph traversal live growing corpus",
    "Sovereign Algorithm Design pattern breaking architecture discovery",
    "Convergence criteria agentic reasoning loops",
    "Failure mode taxonomy emerging AI architectures",
    "Embedding search multi-domain knowledge cross-domain transfer",
    "Desktop Agent Autonomy file system control permissions architecture",
    "Parallel Multi-Agent Orchestration managing competing agents without deadlock",
    "State Machine Design for Agent Workflows finite state machines agent scaffolds",
    "Agent Governance and Safety Constraints enforcement without killing capability",
    "Deep IDE Integration Protocols compiler feedback loops for agents",
    "Git Worktree Atomicity versioning agent work across parallel threads",
    "Objective Validation Frameworks verifying agent outputs against stated goals",
    "Control Planes for Multi-Agent Systems centralized routing without bottlenecks",
    "Continuous Inference on Edge Hardware M-series chips NPU optimization",
    "File System Permissions Models for Agents sandboxing vs unsandboxing",
    "Deep Research Integration with Agentic Properties combining retrieval autonomy",
    "Hardware-Aware Agent Scheduling dispatching GPUs NPUs CPUs intelligently",
    "Asynchronous Multi-Agent Debate non-blocking refinement loops",
    "Agent Specialized Roles and Narrow Focus",
    "Quantum-Assisted Agent Optimization hybrid classical-quantum solving",
    "ASIC-Based Accelerators for Agent Inference custom silicon agentic workloads",
    "Photonic Inference for Latency-Critical Agents speed-of-light reasoning",
    "Neuromorphic Agent Architectures spike-based reasoning",
    "Zero-GPU Agent Pipelines CPU-only inference scaling",
    "BitNet 1-bit Agent Models extreme quantization embedded agents",
    "Federated Multi-Agent Learning privacy-preserving agent swarms",
    "DNA-Based Agent Memory Storage biological persistence layers",
    "Brain-Computer Interface Agents neural feedback loops",
    "6G Edge Intelligence Protocols distributed agent decision-making",
    "Analog Inference Chips for Agents continuous-time reasoning",
    "Agent Proof-Assistants Theorem Proving formal verification agent actions",
    "Test-Time Agent Scaling reasoning at inference rather than training",
    "Mixture of Expert Agents sparse routing tasks to specialists",
    "Multi-Agent Architecture Search auto-optimizing agent team composition",
    "Agent Swarm Synchronization collision avoidance coordination primitives",
    "Causal Inference in Multi-Agent Systems understanding agent interaction effects",
    "Agent Reward Hacking Detection preventing agents gaming metrics",
    "Cross-Domain Agent Transfer applying agent knowledge one domain to another",
    "Convergence Guarantees for Agent Swarms formal proofs agents reach consensus",
    "Agent Introspection and Self-Model agents reasoning about their own reasoning",
]

def load_known_topics():
    try:
        with open(BRAIN_PATH, "r") as f:
            data = json.load(f)
        entries = data.get("knowledge", [])
        known = set(e.get("topic", "").lower().strip() for e in entries)
        print(f"[AUTO-INGEST] Existing entries: {len(entries)}")
        print(f"[AUTO-INGEST] Known topics: {len(known)}")
        return known
    except Exception as ex:
        print(f"[AUTO-INGEST] Could not load brain: {ex}")
        return set()

def is_known(topic, known_topics):
    topic_lower = topic.lower().strip()
    for known in known_topics:
        if topic_lower in known or known in topic_lower:
            return True
    return False

def sync_to_github():
    print("\n[AUTO-INGEST] Syncing to GitHub and GitLab...")
    result = subprocess.run(
        "bash /data/data/com.termux/files/home/barrot/brain_sync.sh && "
        "git add -A && "
        "git commit -m 'Auto-ingest complete — brain expanded' && "
        "git push origin main && "
        "git push gitlab main",
        shell=True, text=True, cwd=BARROT_DIR
    )
    print(result.stdout if result.stdout else "[AUTO-INGEST] Sync done.")

def main():
    print("=" * 60)
    print("BARROT-Ω AUTO INGEST v2.0 — Orchestrator: Sean Drew")
    print("=" * 60)

    known_topics = load_known_topics()
    to_ingest = [t for t in TOPICS if not is_known(t, known_topics)]
    skipped = len(TOPICS) - len(to_ingest)

    print(f"[AUTO-INGEST] Skipped already known: {skipped}")
    print(f"[AUTO-INGEST] Ingesting: {len(to_ingest)} new topics")
    print(f"[AUTO-INGEST] Estimated new entries: ~{len(to_ingest) * 5}")
    print("=" * 60)

    if not to_ingest:
        print("[AUTO-INGEST] Brain is up to date.")
        sync_to_github()
        return

    input_data = "\n".join(to_ingest) + "\nq\n"

    process = subprocess.Popen(
        ["python3", "barrot.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=BARROT_DIR
    )

    try:
        stdout, _ = process.communicate(input=input_data, timeout=7200)
        print(stdout)
    except subprocess.TimeoutExpired:
        process.kill()
        print("[AUTO-INGEST] Timeout after 2 hours.")

    sync_to_github()

    try:
        with open(BRAIN_PATH, "r") as f:
            data = json.load(f)
        print(f"[AUTO-INGEST] Final brain size: {len(data.get('knowledge', []))} entries")
    except:
        pass

    print("=" * 60)
    print("[AUTO-INGEST] Done. Go to sleep, Sean.")
    print("=" * 60)

if __name__ == "__main__":
    main()
