#!/usr/bin/env python3
"""
BARROT ALGORITHM INNOVATION & CONVERGENCE CURRICULUM v3
=======================================================
Claude + Perplexity + Gemini + Sonar synthesized
25 nodes | 5 categories | MRP 5-level | MMIP | Shadow | ORA
Each node: title, paradigm, primary_dim, secondary_dim,
           prerequisites, barrot_mapping, example, music
"""

import json, os, time, requests, random
from datetime import datetime

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
API_URL = "https://models.inference.ai.azure.com/chat/completions"
MODEL = "gpt-4o"
MEMORY_PATH = os.path.expanduser("~/barrot/memory.json")
CONTEXT_PATH = os.path.expanduser("~/barrot/algorithm_context.json")
ANCHOR = 0.7071
MAX_RETRIES = 3
MRP_LEVELS = ["Surface", "Components", "Sources", "Deep", "Planck"]

CURRICULUM = [
    {
        "node": 1, "category": "Algorithm Foundations",
        "title": "Big O and Multi-Dimensional Complexity Time Space and AI Compute Scaling",
        "description": "Formal language for measuring algorithm cost across time, memory, and AI-specific compute dimensions.",
        "paradigm": "Complexity-Aware Design",
        "primary_dim": "Time-space-compute scaling",
        "secondary_dim": "Dimensionality dependence under AI-specific workloads",
        "prerequisites": [],
        "barrot_mapping": "Sets the cost budget for every search, retrieval, and refinement loop in the engine.",
        "example": "O(n log n) sort vs O(n2) sort; transformer attention as O(n2) in sequence length",
        "music": "Big O = headroom in a mix. Time complexity = CPU load per plugin. Space = RAM per sample.",
    },
    {
        "node": 2, "category": "Algorithm Foundations",
        "title": "Recursion Divide-and-Conquer and Problem Decomposition",
        "description": "Breaking problems into self-similar subproblems and recombining results.",
        "paradigm": "Search-Driven Decomposition",
        "primary_dim": "Recursive problem splitting",
        "secondary_dim": "Dependency structure and subproblem independence",
        "prerequisites": [1],
        "barrot_mapping": "MRP 5-level analysis loop is a direct instantiation of recursive decomposition with stopping conditions.",
        "example": "Merge sort; recursive tree traversal; MRP level decomposition",
        "music": "Recursion = loop inside a loop in Ableton. Divide and conquer = splitting full mix into stems.",
    },
    {
        "node": 3, "category": "Algorithm Foundations",
        "title": "Dynamic Programming as State Reuse Under Constraints",
        "description": "Caching and reusing subproblem solutions to avoid redundant computation.",
        "paradigm": "State-Driven Update Under Constraints",
        "primary_dim": "State reuse and memoization",
        "secondary_dim": "Constraint-propagation and subproblem ordering",
        "prerequisites": [2],
        "barrot_mapping": "Barrot knowledge graph caches prior traversal results to avoid re-ingesting the same concept chains.",
        "example": "Fibonacci memoization; Viterbi algorithm; sequence alignment",
        "music": "Dynamic programming = saving a plugin preset and reusing it across tracks. Memoization = recall.",
    },
    {
        "node": 4, "category": "Algorithm Foundations",
        "title": "Greedy Algorithms as Local Decision Policies",
        "description": "Making the locally optimal choice at each step — fast but blind to global structure.",
        "paradigm": "Search-Driven Policy",
        "primary_dim": "Locally optimal choices",
        "secondary_dim": "Myopia versus global optimality gap",
        "prerequisites": [1],
        "barrot_mapping": "Pruning heuristics in the innovation engine use greedy selection to compress search space.",
        "example": "Dijkstra algorithm; Huffman coding; greedy set cover",
        "music": "Greedy = picking the loudest kick sample without hearing the full mix.",
    },
    {
        "node": 5, "category": "Algorithm Foundations",
        "title": "Graph Algorithms for Traversal Reachability and Dependency Resolution",
        "description": "Navigating linked structures to resolve paths, cycles, and ordering.",
        "paradigm": "State-Driven Graph Traversal",
        "primary_dim": "Structural navigation BFS DFS reachability",
        "secondary_dim": "Dependency and causality resolution",
        "prerequisites": [2, 3],
        "barrot_mapping": "Knowledge graph traversal in Category 5 is direct application of BFS/DFS over 800+ linked concept nodes.",
        "example": "BFS for shortest path; topological sort; PageRank",
        "music": "Graph traversal = following a signal chain from source to master bus.",
    },
    {
        "node": 6, "category": "Innovation and Search Patterns",
        "title": "Approximation Algorithms as Controlled Trade-Off Search",
        "description": "Accepting bounded error to achieve tractable solutions.",
        "paradigm": "Search-Driven Policy",
        "primary_dim": "Accuracy-efficiency trade-offs",
        "secondary_dim": "Bounded-error guarantees and problem classes",
        "prerequisites": [4],
        "barrot_mapping": "Barrot uses approximation logic when exact convergence is too expensive.",
        "example": "2-approximation for vertex cover; FPTAS for knapsack",
        "music": "Approximation = lossy audio compression. MP3 is good enough.",
    },
    {
        "node": 7, "category": "Innovation and Search Patterns",
        "title": "Local Search and Hill Climbing as Incremental Improvement Loops",
        "description": "Iteratively moving to better neighbors — the simplest form of iterative refinement.",
        "paradigm": "Search-Driven Iterative Policy",
        "primary_dim": "Greedy neighborhood improvement",
        "secondary_dim": "Local optima trapping and restarts",
        "prerequisites": [4, 6],
        "barrot_mapping": "Ping-pong ensemble loop is a multi-agent generalization of hill climbing over solution quality.",
        "example": "2-opt for TSP; coordinate descent; k-means iteration",
        "music": "Hill climbing = slowly pushing fader up until the mix sounds right.",
    },
    {
        "node": 8, "category": "Innovation and Search Patterns",
        "title": "Simulated Annealing as Probabilistic Escape from Local Optima",
        "description": "Adding controlled randomness to local search so the system can escape suboptimal traps.",
        "paradigm": "Search-Driven Policy",
        "primary_dim": "Temperature-controlled stochastic search",
        "secondary_dim": "Probabilistic escape from neighborhoods",
        "prerequisites": [7],
        "barrot_mapping": "Sovereign Algorithm Design borrows this — deliberate divergence prevents locking into a single reasoning path.",
        "example": "Chip placement optimization; schedule optimization",
        "music": "Simulated annealing = randomizing EQ settings wildly then slowly tightening.",
    },
    {
        "node": 9, "category": "Innovation and Search Patterns",
        "title": "Genetic Algorithms as Population-Based Search and Recombination",
        "description": "Evolving a population of candidate solutions through selection, crossover, and mutation.",
        "paradigm": "Search-Driven Policy",
        "primary_dim": "Population-based evolutionary search",
        "secondary_dim": "Crossover and mutation as recombinative operators",
        "prerequisites": [8],
        "barrot_mapping": "Multi-agent ensemble refinement recombines partial solutions across agents — soft analogue to crossover.",
        "example": "Neural architecture search; parameter optimization",
        "music": "Genetic algorithm = running 100 variations of a beat keeping the best elements from each generation.",
    },
    {
        "node": 10, "category": "Innovation and Search Patterns",
        "title": "Neuro-Symbolic Pattern Recognition Bridging Continuous Vectors and Discrete Logic",
        "description": "Combining sub-symbolic pattern matching with verifiable symbolic rules for cross-domain transfer.",
        "paradigm": "Information-Geometry and Logic-Driven Recognition",
        "primary_dim": "Continuous vector spaces and symbolic rules",
        "secondary_dim": "Confidence-driven rule-activation and grounding",
        "prerequisites": [5, 9],
        "barrot_mapping": "Barrot detects invariant structures across physics, music, and code using this hybrid recognition pattern.",
        "example": "AlphaGeometry; logic-augmented LLMs; scene graph grounding",
        "music": "Neuro-symbolic = hearing a chord and knowing its name. Neural = the feeling. Symbolic = the theory.",
    },
    {
        "node": 11, "category": "AI and Multi-Agent Loops",
        "title": "Reinforcement Learning as Reward-Driven Policy Adaptation",
        "description": "Learning optimal behavior through environmental feedback.",
        "paradigm": "Temporally Extended Policy Learning",
        "primary_dim": "Reward-driven policy adaptation",
        "secondary_dim": "Exploration-exploitation online adaptation",
        "prerequisites": [7, 9],
        "barrot_mapping": "Barrot agents use reward signals to adapt their refinement strategies over time.",
        "example": "AlphaGo; robotic control; LLM RLHF fine-tuning",
        "music": "RL = DJ reading the crowd. Reward = people dancing. Policy = what to play next.",
    },
    {
        "node": 12, "category": "AI and Multi-Agent Loops",
        "title": "Monte Carlo Tree Search as Guided Exploration Under Uncertainty",
        "description": "Balancing exploration and exploitation in tree-structured decision spaces using random sampling.",
        "paradigm": "State-Driven Search Tree Policy",
        "primary_dim": "Tree-based exploration under uncertainty",
        "secondary_dim": "Value-backpropagation and selection-expansion",
        "prerequisites": [5, 11],
        "barrot_mapping": "Barrot multi-step innovation search uses MCTS-style lookahead to evaluate which knowledge paths to expand.",
        "example": "AlphaZero; planning in POMDPs; LLM reasoning trees",
        "music": "Monte Carlo = simulating 1000 possible arrangements before committing to one.",
    },
    {
        "node": 13, "category": "AI and Multi-Agent Loops",
        "title": "MRP as a 5-Level Analysis Loop with Inputs Outputs and Stopping Conditions",
        "description": "Structured recursive protocol for decomposing any problem across five analytical levels.",
        "paradigm": "Meta-Recurrent Analysis Loop",
        "primary_dim": "Multilevel recursive problem analysis",
        "secondary_dim": "Inputs outputs and formal stopping conditions",
        "prerequisites": [2, 12],
        "barrot_mapping": "MRP is Barrot native reasoning scaffold — every innovation analysis runs through this loop.",
        "example": "MRP applied to feature design, market analysis, system debugging",
        "music": "MRP = listening at surface then drilling into each instrument then the room then the physics then the quantum vibration.",
    },
    {
        "node": 14, "category": "AI and Multi-Agent Loops",
        "title": "Ping-Pong Ensemble Refinement as Multi-Agent Debate-Driven Convergence",
        "description": "Iterative critique and counter-critique between agents converging on a hardened solution.",
        "paradigm": "Multi-Agent Debate Loop",
        "primary_dim": "Competitive-collaborative refinement",
        "secondary_dim": "Iterative consensus via critique and counter-critique",
        "prerequisites": [11, 13],
        "barrot_mapping": "Core Barrot refinement protocol — agents debate candidate innovations until convergence criterion is met.",
        "example": "Constitutional AI critique loops; multi-model debate for factuality",
        "music": "Ping pong = producer and engineer going back and forth on the mix until both agree it is perfect.",
    },
    {
        "node": 15, "category": "AI and Multi-Agent Loops",
        "title": "Sovereign Algorithm Design Deliberate Pattern Breaking for Controlled Divergence",
        "description": "Intentionally violating learned patterns to generate novel outputs — engineered creativity.",
        "paradigm": "Sovereign Meta-Design",
        "primary_dim": "Intentional pattern breaking",
        "secondary_dim": "Controlled divergence and safety constraints",
        "prerequisites": [8, 14],
        "barrot_mapping": "Barrot uses sovereign design when ensemble loop converges too quickly — injecting divergence to explore new regions.",
        "example": "Adversarial prompting for robustness; novelty search in neuroevolution",
        "music": "Sovereign design = Perelman refusing the $1M prize. Doing it because it is true not because it is rewarded.",
    },
    {
        "node": 16, "category": "Convergence and Stability",
        "title": "Fixed-Point Iteration as Repeated State Update Toward Equilibrium",
        "description": "Applying a function repeatedly until output equals input.",
        "paradigm": "State-Driven Iterative Update",
        "primary_dim": "Contraction-map convergence",
        "secondary_dim": "Local equilibrium and perturbation sensitivity",
        "prerequisites": [3, 7],
        "barrot_mapping": "Every Barrot refinement loop terminates when the system reaches a fixed point.",
        "example": "PageRank power iteration; value iteration in RL; expectation-maximization",
        "music": "Fixed point = tuning a synth oscillator until it locks onto the exact frequency and stops drifting.",
    },
    {
        "node": 17, "category": "Convergence and Stability",
        "title": "Gradient Descent as Error-Minimizing Iterative Optimization",
        "description": "Following the steepest downhill direction in a loss landscape to minimize error.",
        "paradigm": "State-Driven Iterative Optimization",
        "primary_dim": "Error-minimizing gradient updates",
        "secondary_dim": "Lyapunov-style descent and learning-rate tuning",
        "prerequisites": [16],
        "barrot_mapping": "Barrot embedding search fine-tunes retrieval weights using gradient signals from relevance feedback.",
        "example": "Neural network training; logistic regression; Adam optimizer",
        "music": "Gradient descent = slowly turning mix bus compressor threshold until distortion disappears.",
    },
    {
        "node": 18, "category": "Convergence and Stability",
        "title": "Stochastic Convergence Mixing and Lyapunov Stability",
        "description": "Understanding when probabilistic systems forget their starting state and settle into stable behavior.",
        "paradigm": "Stability-Driven Convergence",
        "primary_dim": "Stochastic convergence and mixing",
        "secondary_dim": "Lyapunov functions and stability guarantees",
        "prerequisites": [16, 17],
        "barrot_mapping": "Barrot uses mixing-time analysis to determine when ensemble debate has converged to stable consensus.",
        "example": "MCMC mixing; Markov chain stationary distributions; Lyapunov energy functions",
        "music": "Lyapunov stability = 0.707 anchor. System always returns to center no matter how hard it is pushed.",
    },
    {
        "node": 19, "category": "Convergence and Stability",
        "title": "Pruning Heuristics and Dimensionality Reduction as Search-Space Compression",
        "description": "Eliminating irrelevant dimensions and branches before deep search.",
        "paradigm": "Search-Driven Compression",
        "primary_dim": "Search-space pruning",
        "secondary_dim": "Dimensionality reduction and geometric compactness",
        "prerequisites": [6, 18],
        "barrot_mapping": "Barrot prunes 800+ knowledge entry space before running ensemble refinement.",
        "example": "Alpha-beta pruning; PCA; feature selection in ML pipelines",
        "music": "Pruning = high-pass filtering. Cutting everything below 80Hz that is not bass or kick.",
    },
    {
        "node": 20, "category": "Convergence and Stability",
        "title": "Convergence Criteria for Agentic Search and Refinement Loops",
        "description": "Formal stopping rules combining statistical, semantic, and Lyapunov-style signals.",
        "paradigm": "Stability-Driven Stopping Criteria",
        "primary_dim": "Convergence-and-stopping analysis",
        "secondary_dim": "Combining Lyapunov-style statistical and semantic criteria",
        "prerequisites": [18, 19],
        "barrot_mapping": "Every Barrot agent loop requires an explicit stopping condition — this topic provides the formal toolkit.",
        "example": "Early stopping in training; debate termination rules; consensus thresholds",
        "music": "Convergence = knowing when the mix is done. Not perfect. Done.",
    },
    {
        "node": 21, "category": "Barrot-Native Systems",
        "title": "Knowledge Graph Traversal as Structured Retrieval Over Linked Concepts",
        "description": "Navigating a semantic graph of linked concepts to retrieve contextually relevant knowledge chains.",
        "paradigm": "Information-Geometry and Graph-Driven Retrieval",
        "primary_dim": "Linked-concept traversal",
        "secondary_dim": "Semantic context and path-based reasoning",
        "prerequisites": [5, 10],
        "barrot_mapping": "Direct implementation: Barrot 800+ knowledge entries stored and retrieved as a traversable concept graph.",
        "example": "Wikidata traversal; ontology reasoning; knowledge-augmented LLM retrieval",
        "music": "Knowledge graph = Barrot navigating from quantum physics to Bb minor in 3 hops.",
    },
    {
        "node": 22, "category": "Barrot-Native Systems",
        "title": "Embedding Search and Latent Space Geometry Navigating High-Dimensional Vectors",
        "description": "Finding semantically similar entries by navigating compressed vector representations of meaning.",
        "paradigm": "Information-Geometry Mechanism",
        "primary_dim": "Latent-space navigation",
        "secondary_dim": "High-dimensional vector search and similarity",
        "prerequisites": [10, 19, 21],
        "barrot_mapping": "Barrot uses embedding search as first-pass retrieval layer before graph traversal and ensemble refinement.",
        "example": "FAISS vector search; sentence transformers; RAG retrieval pipelines",
        "music": "Embedding space = the zone between notes where feeling lives.",
    },
    {
        "node": 23, "category": "Barrot-Native Systems",
        "title": "Failure Mode Taxonomy Transient Permanent and Poison Pill Classification",
        "description": "Systematically classifying how systems fail by temporal impact and self-amplification potential.",
        "paradigm": "Failure-Mode Taxonomy",
        "primary_dim": "Temporal and causal impact transient and permanent",
        "secondary_dim": "Self-amplifying catastrophic failure poison pills",
        "prerequisites": [15, 20],
        "barrot_mapping": "Barrot classifies agent failures before propagating results — poison pill failures trigger full loop reset.",
        "example": "Cascading failures in distributed systems; poisoned training data; prompt injection",
        "music": "Transient failure = a click in the audio. Permanent = blown speaker. Poison pill = crashes the DAW.",
    },
    {
        "node": 24, "category": "Barrot-Native Systems",
        "title": "Memory JSON Atomic Writes via Content-Addressed Storage and Merkle DAGs",
        "description": "Storing state immutably and verifiably using content-addressed hashing.",
        "paradigm": "Content-Addressed Storage Mechanism",
        "primary_dim": "Immutable content-addressed storage",
        "secondary_dim": "Atomic writes Merkle-DAG tamper-evidence",
        "prerequisites": [3, 21],
        "barrot_mapping": "Barrot writes all session state atomically to memory.json — no partial writes, no silent corruption.",
        "example": "Git object store; IPFS; blockchain transaction logs",
        "music": "Atomic write = either the whole stem renders or nothing saves.",
    },
    {
        "node": 25, "category": "Barrot-Native Systems",
        "title": "Barrot Innovation Engine Convergent Search over 800 Plus Knowledge Entries with Pruning Heuristics",
        "description": "The full Barrot pipeline: embed, prune, traverse, debate, converge, output.",
        "paradigm": "Convergent Search Engine",
        "primary_dim": "Convergent search over structured knowledge",
        "secondary_dim": "Pruning heuristics and multi-agent refinement loops",
        "prerequisites": list(range(1, 25)),
        "barrot_mapping": "This IS Barrot — the capstone node that instantiates all 24 prior topics as a running system.",
        "example": "Full Barrot innovation cycle on a new domain: music to algorithm to system design",
        "music": "Barrot Innovation Engine = the full system. 800+ entries. 5 paradigms. All roads lead back to music.",
    },
]

# ── Shadow Engine ─────────────────────────────────────────────────────────────
CAPABILITIES = ["Amplify", "Aptitude", "Enhance", "Compound"]

def shadow_pass(content):
    size = random.randint(1, 4)
    for i in range(size):
        action = random.choice(CAPABILITIES)
        content = f"[Shadow-{i}:{action}] {content[:100]}"
    return content

# ── API ───────────────────────────────────────────────────────────────────────
def ask(prompt):
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.post(API_URL,
                headers={"Authorization": "Bearer " + GITHUB_TOKEN, "Content-Type": "application/json"},
                json={"model": MODEL, "max_tokens": 500,
                      "messages": [{"role": "user", "content": prompt}]},
                timeout=60)
            if r.status_code == 429:
                print(f"  Rate limit. Waiting 30s...")
                time.sleep(30)
                continue
            data = r.json()
            if "choices" in data:
                return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"  Error: {e}")
            time.sleep(10)
    return None

# ── Memory ────────────────────────────────────────────────────────────────────
def load_memory():
    if os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH, "r") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data.get("knowledge", [])
        return data
    return []

def save_memory(memory):
    if os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH, "r") as f:
            existing = json.load(f)
        if isinstance(existing, dict):
            existing["knowledge"] = memory
            with open(MEMORY_PATH, "w") as f:
                json.dump(existing, f, indent=2)
            return
    with open(MEMORY_PATH, "w") as f:
        json.dump(memory, f, indent=2)

def topic_known(memory, topic):
    return any(isinstance(e, dict) and e.get("topic") == topic for e in memory)

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("BARROT ALGORITHM INNOVATION AND CONVERGENCE CURRICULUM v3")
    print("Claude + Perplexity + Gemini + Sonar | 25 nodes | MRP")
    print(f"Anchor: {ANCHOR} | Protocols: MRP MMIP SHADOW ORA")
    print("=" * 60)

    if not GITHUB_TOKEN:
        print("GITHUB_TOKEN not set. Run: source ~/.bashrc")
        return

    memory = load_memory()
    context = {}
    completed = 0
    skipped = 0

    for node in CURRICULUM:
        topic = node["title"]
        num = node["node"]
        print(f"\n[{num}/25] {topic[:55]}")
        print(f"  Paradigm : {node['paradigm']}")
        print(f"  Primary  : {node['primary_dim']}")
        print(f"  Barrot   : {node['barrot_mapping'][:60]}")

        if topic_known(memory, topic):
            print("  Already known - skipping")
            skipped += 1
            continue

        node_done = 0
        for level in MRP_LEVELS:
            print(f"  {level}...", end=" ", flush=True)
            prompt = (
                f"Analyze this topic at {level} level using Multisynchronous Relativistic Perception (MRP):\n"
                f"Topic: {topic}\n"
                f"Description: {node['description']}\n"
                f"Paradigm: {node['paradigm']}\n"
                f"Primary dimension: {node['primary_dim']}\n"
                f"Secondary dimension: {node['secondary_dim']}\n"
                f"Barrot application: {node['barrot_mapping']}\n"
                f"Music parallel: {node['music']}\n"
                f"Include all scales: macro, micro, molecular, atomic, nano, fractal, Planck."
            )
            result = ask(prompt)
            if result:
                amplified = shadow_pass(result)
                memory.append({
                    "topic": topic,
                    "node": num,
                    "category": node["category"],
                    "paradigm": node["paradigm"],
                    "primary_dim": node["primary_dim"],
                    "secondary_dim": node["secondary_dim"],
                    "barrot_mapping": node["barrot_mapping"],
                    "level": level,
                    "content": result,
                    "shadow_amplified": amplified,
                    "music_mapping": node["music"],
                    "anchor": ANCHOR,
                    "protocol": "MMIP+MRP+SHADOW+ORA",
                    "timestamp": datetime.utcnow().isoformat()
                })
                save_memory(memory)
                node_done += 1
                print("done")
            else:
                print("FAILED")
            time.sleep(5)

        context[str(num)] = {
            "topic": topic,
            "paradigm": node["paradigm"],
            "completed_at": datetime.utcnow().isoformat(),
            "levels_saved": node_done,
            "barrot_mapping": node["barrot_mapping"]
        }
        with open(CONTEXT_PATH, "w") as f:
            json.dump(context, f, indent=2)

        completed += 1
        print(f"  Node {num} complete. Total memory: {len(memory)} entries")
        time.sleep(3)

    print("\n" + "=" * 60)
    print(f"ALGORITHM CURRICULUM COMPLETE")
    print(f"Nodes completed : {completed}")
    print(f"Nodes skipped   : {skipped}")
    print(f"Total entries   : {len(memory)}")
    print(f"Anchor held     : {ANCHOR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
