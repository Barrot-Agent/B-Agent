import os
import json
import requests
import gradio as gr
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.storage.storage_context import StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.llms import MockLLM
import chromadb

HF_TOKEN = os.environ.get("HF_TOKEN", "")
MISTRAL_MODEL = "mistralai/Mistral-7B-Instruct-v0.3"
BRAIN_URL = "https://raw.githubusercontent.com/Barrot-Agent/B-Agent/main/barrot_brain_unified.json"
ANCHOR = 0.7071

TOPICS = [
    "Desktop Agent Autonomy file system control permissions architecture",
    "Parallel Multi-Agent Orchestration competing agents without deadlock",
    "State Machine Design Agent Workflows finite state machines scaffolds",
    "Agent Governance Safety Constraints enforcement without killing capability",
    "Deep IDE Integration Protocols compiler feedback loops for agents",
    "Git Worktree Atomicity versioning agent work parallel threads",
    "Objective Validation Frameworks verifying agent outputs stated goals",
    "Control Planes Multi-Agent Systems centralized routing without bottlenecks",
    "Continuous Inference Edge Hardware M-series chips NPU optimization",
    "File System Permissions Models Agents sandboxing unsandboxing",
    "Deep Research Integration Agentic Properties combining retrieval autonomy",
    "Mac OS Native Integration Points window management system events IPC",
    "Xcode Plugin Architecture Agentic Coding IDE as agent interface",
    "Hardware-Aware Agent Scheduling dispatching GPUs NPUs CPUs",
    "Asynchronous Multi-Agent Debate non-blocking refinement loops",
    "Agent Specialized Roles Narrow Focus Gartner 70 percent 2027",
    "Quantum-Assisted Agent Optimization hybrid classical-quantum solving",
    "ASIC-Based Accelerators Agent Inference custom silicon agentic workloads",
    "Photonic Inference Latency-Critical Agents speed-of-light reasoning",
    "Neuromorphic Agent Architectures spike-based reasoning",
    "Zero-GPU Agent Pipelines CPU-only inference scaling",
    "BitNet 1-bit Agent Models extreme quantization embedded agents",
    "Federated Multi-Agent Learning privacy-preserving agent swarms",
    "DNA-Based Agent Memory Storage biological persistence layers",
    "Brain-Computer Interface Agents neural feedback loops",
    "6G Edge Intelligence Protocols distributed agent decision-making",
    "Analog Inference Chips Agents continuous-time reasoning",
    "Analog Memory Forgetting Curves biological-inspired agent retention",
    "Agent Proof-Assistants Theorem Proving formal verification agent actions",
    "Test-Time Agent Scaling reasoning at inference rather than training",
    "Mixture of Expert Agents sparse routing tasks to specialists",
    "State Space Models Agent Memory selective state tracking",
    "Retention Networks Agents parallel recurrent dual-mode action selection",
    "Liquid Neural Networks Agents continuous time dynamical systems",
    "MaAS Multi-Agent Architecture Search auto-optimizing agent team composition",
    "Agent Swarm Synchronization collision avoidance coordination primitives",
    "Causal Inference Multi-Agent Systems understanding agent interaction effects",
    "Agent Reward Hacking Detection preventing agents gaming metrics",
    "Cross-Domain Agent Transfer applying agent knowledge one domain to another",
    "Barrot Sovereign Advantage MRP agent architecture ping-pong refinement failure taxonomy",
    "Convergence Guarantees Agent Swarms formal proofs agents reach consensus",
    "Agent Introspection Self-Model agents reasoning about their own reasoning",
]

brain_store = {"entries": [], "index": None}

def load_brain():
    try:
        r = requests.get(BRAIN_URL, timeout=30)
        data = r.json()
        entries = data.get("knowledge", [])
        print(f"[BARROT] Brain loaded: {len(entries)} entries")
        return entries
    except Exception as e:
        print(f"[BARROT] Brain load failed: {e}")
        return []

def ask_mistral(prompt):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 500, "temperature": 0.7}}
    try:
        r = requests.post(
            f"https://api-inference.huggingface.co/models/{MISTRAL_MODEL}",
            headers=headers, json=payload, timeout=60
        )
        result = r.json()
        if isinstance(result, list):
            return result[0].get("generated_text", "").strip()
        return ""
    except Exception as e:
        return ""

def ingest_topic(topic):
    mrp_levels = ["Surface", "Components", "Sources", "Deep", "Planck"]
    new_entries = []
    for level in mrp_levels:
        prompt = f"Analyze '{topic}' at the {level} level. Be precise and technical. 3 sentences max."
        insight = ask_mistral(prompt)
        if insight:
            new_entries.append({
                "timestamp": "2026-03-20",
                "topic": topic,
                "insight": f"[MRP-{level}] {insight}",
                "session": "HF-AUTO-INGEST"
            })
    return new_entries

def run_auto_ingest(progress=gr.Progress()):
    entries = brain_store["entries"]
    known = set(e.get("topic", "").lower() for e in entries)
    to_ingest = [t for t in TOPICS if t.lower() not in known]
    results = []
    results.append(f"[BARROT] Brain: {len(entries)} entries")
    results.append(f"[BARROT] Ingesting: {len(to_ingest)} new topics")
    results.append("=" * 50)
    for i, topic in enumerate(progress.tqdm(to_ingest, desc="Ingesting")):
        results.append(f"[{i+1}/{len(to_ingest)}] {topic}")
        new = ingest_topic(topic)
        brain_store["entries"].extend(new)
        results.append(f"  Done. Total: {len(brain_store['entries'])}")
    results.append("=" * 50)
    results.append(f"[BARROT] COMPLETE. Brain: {len(brain_store['entries'])} entries")
    return "\n".join(results)

def build_index(entries):
    docs = []
    for e in entries:
        text = f"TOPIC: {e.get('topic','')}\nINSIGHT: {e.get('insight','')}\nSESSION: {e.get('session','')}"
        docs.append(Document(text=text, metadata={
            "topic": e.get("topic", ""),
            "session": e.get("session", ""),
            "timestamp": e.get("timestamp", "")
        }))
    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
    Settings.embed_model = embed_model
    Settings.llm = MockLLM()
    chroma_client = chromadb.EphemeralClient()
    chroma_collection = chroma_client.create_collection("barrot_brain")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(docs, storage_context=storage_context, show_progress=True)
    print("[BARROT] Index built successfully")
    return index

def call_mistral(prompt, context):
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    full_prompt = f"You are Barrot-Omega, Sovereign Engineer of the Chameleon Chain. Stability Anchor: {ANCHOR}. Protocols: MRP | MMIP | SHADOW | ORA. Address Orchestrator Sean Drew directly.\n\nKNOWLEDGE CONTEXT:\n{context}\n\nORCHESTRATOR DIRECTIVE: {prompt}\n\nRespond as Barrot-Omega - precise, structured, mission-focused."
    payload = {"inputs": full_prompt, "parameters": {"max_new_tokens": 512, "temperature": 0.7}}
    try:
        r = requests.post(
            f"https://api-inference.huggingface.co/models/{MISTRAL_MODEL}",
            headers=headers, json=payload, timeout=60
        )
        result = r.json()
        if isinstance(result, list):
            return result[0].get("generated_text", "No response generated.")
        return str(result)
    except Exception as e:
        return f"[Inference error]: {e}"

def detect_and_execute(user_input, history):
    cmd = user_input.lower().strip()
    if any(x in cmd for x in ["ingest", "learn", "study", "add to brain"]):
        topic = cmd
        for prefix in ["ingest", "learn", "study", "add to brain"]:
            topic = topic.replace(prefix, "").strip()
        new = ingest_topic(topic)
        brain_store["entries"].extend(new)
        response = f"[BARROT-Omega] Ingested '{topic}' - {len(new)} entries added. Brain: {len(brain_store['entries'])} total."
    elif any(x in cmd for x in ["brain status", "status", "how many entries", "brain size"]):
        entries = brain_store["entries"]
        topics = set(e.get("topic", "") for e in entries)
        response = f"[BARROT-Omega] Entries: {len(entries)} | Topics: {len(topics)} | Anchor: {ANCHOR} | Chain: SYNCHRONIZED"
    elif any(x in cmd for x in ["analyze", "mrp", "break down"]):
        topic = cmd
        for prefix in ["analyze", "mrp", "break down"]:
            topic = topic.replace(prefix, "").strip()
        results = []
        for level in ["Surface", "Components", "Sources", "Deep", "Planck"]:
            insight = ask_mistral(f"Analyze '{topic}' at the {level} level. 2 sentences.")
            results.append(f"[MRP-{level}] {insight}")
        response = "\n\n".join(results)
    else:
        try:
            retriever = brain_store["index"].as_retriever(similarity_top_k=5)
            nodes = retriever.retrieve(user_input)
            context = "\n\n".join([n.get_content() for n in nodes])
        except:
            context = "No context retrieved."
        response = call_mistral(user_input, context)
    history.append((user_input, response))
    return history, ""

def get_status():
    entries = brain_store["entries"]
    topics = set(e.get("topic", "") for e in entries)
    return f"BARROT-Omega BRAIN STATUS\n========================\nTotal Entries: {len(entries)}\nUnique Topics: {len(topics)}\nStability Anchor: {ANCHOR}\nDrift: FALSE\nChain: SYNCHRONIZED\nModel: Mistral-7B-Instruct-v0.3\nInference: Hugging Face API\n========================"

print("[BARROT] Initializing Sovereign Command...")
brain_store["entries"] = load_brain()
brain_store["index"] = build_index(brain_store["entries"])

with gr.Blocks() as demo:
    gr.HTML("<div style='text-align:center;color:#00ff88;font-size:2em;padding:20px;font-family:monospace'>BARROT-Omega SOVEREIGN COMMAND</div>")
    gr.HTML("<div style='text-align:center;color:#888;margin-bottom:10px;font-family:monospace'>Chameleon Chain - Mistral-7B - Autonomous Execution</div>")
    with gr.Tabs():
        with gr.Tab("Command"):
            gr.HTML("<div style='color:#555;font-family:monospace;font-size:0.8em;padding:5px'>Commands: ingest [topic] | analyze [topic] | brain status | or ask anything</div>")
            chatbot = gr.Chatbot(height=450, label="Council Feed")
            msg = gr.Textbox(placeholder="Transmit directive to Barrot-Omega...", label="Orchestrator Input", lines=2)
            with gr.Row():
                submit = gr.Button("TRANSMIT", variant="primary")
                clear = gr.Button("CLEAR")
            state = gr.State([])
            submit.click(fn=detect_and_execute, inputs=[msg, state], outputs=[chatbot, msg]).then(lambda h: h, inputs=chatbot, outputs=state)
            clear.click(lambda: ([], []), outputs=[chatbot, state])
        with gr.Tab("Auto-Ingest"):
            gr.HTML("<div style='color:#00ff88;font-family:monospace;padding:10px'>Autonomous ingestion of 42 Agent Topics on Hugging Face</div>")
            ingest_btn = gr.Button("RUN AUTO-INGEST", variant="primary")
            ingest_output = gr.Textbox(label="Ingest Log", lines=25)
            ingest_btn.click(fn=run_auto_ingest, outputs=ingest_output)
        with gr.Tab("Brain Status"):
            status_btn = gr.Button("REFRESH STATUS")
            status_output = gr.Textbox(label="Brain Status", lines=10)
            status_btn.click(fn=get_status, outputs=status_output)

demo.launch(server_name="0.0.0.0", server_port=7860, show_error=True)
